#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
NAMESPACE="${NAMESPACE:-platform-system}"
SERVICE="${SERVICE:-provider-portal}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-a}"
TENANT_CLUSTER_CLAIM="${TENANT_CLUSTER_CLAIM:-routable-cluster}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-10s}"
PORTAL_LOAD_ITERATIONS="${PORTAL_LOAD_ITERATIONS:-30}"
PORTAL_LOAD_WORKERS="${PORTAL_LOAD_WORKERS:-12}"
MIN_304_RATIO_PERCENT="${MIN_304_RATIO_PERCENT:-90}"
MIN_BYTES_SAVED_PERCENT="${MIN_BYTES_SAVED_PERCENT:-80}"
MAX_P95_LATENCY_MS="${MAX_P95_LATENCY_MS:-2500}"

echo "== discover provider portal endpoints =="
${KUBECTL} -n "${NAMESPACE}" rollout status deploy/provider-portal --timeout=180s
portal_urls="$(
  ${KUBECTL} -n "${NAMESPACE}" get pods -l app=provider-portal -o json | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
for item in payload.get("items", []):
    metadata = item.get("metadata", {})
    status = item.get("status", {})
    if metadata.get("deletionTimestamp") or status.get("phase") != "Running":
        continue
    ready = any(
        condition.get("type") == "Ready" and condition.get("status") == "True"
        for condition in status.get("conditions", [])
    )
    ip = status.get("podIP")
    if ready and ip:
        print(f"http://{ip}:8080")
'
)"
[[ -n "${portal_urls}" ]] || { echo "expected at least one Ready provider-portal pod" >&2; exit 1; }
portal_count="$(printf "%s\n" "${portal_urls}" | sed '/^$/d' | wc -l)"
[[ "${portal_count}" -ge 2 ]] || { echo "expected at least two Ready provider-portal pods, got ${portal_count}" >&2; exit 1; }
portal_url_csv="$(printf "%s\n" "${portal_urls}" | sed '/^$/d' | paste -sd, -)"
echo "ready provider portal pods=${portal_count}"

service_ip="$(${KUBECTL} -n "${NAMESPACE}" get svc "${SERVICE}" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
[[ -n "${service_ip}" ]] || { echo "expected provider-portal LoadBalancer IP" >&2; exit 1; }
echo "provider portal service=http://${service_ip}/"

tenant_endpoint="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${TENANT_CLUSTER_CLAIM}" \
    -o jsonpath='{.status.apiEndpoint}' 2>/dev/null || true
)"
[[ -n "${tenant_endpoint}" ]] || { echo "expected ${TENANT_NAMESPACE}/${TENANT_CLUSTER_CLAIM} status.apiEndpoint" >&2; exit 1; }
echo "tenant api endpoint=https://${tenant_endpoint}/readyz"

echo "== wait for steady provider summary =="
summary_ready=""
for _ in $(seq 1 90); do
  non_running="$(${KUBECTL} get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null || true)"
  if [[ -n "${non_running}" ]]; then
    sleep 2
    continue
  fi
  summary_ready="$(
    python3 - "http://${service_ip}/api/summary?fresh=1" <<'PY' 2>/dev/null || true
import json
import sys
import urllib.request

url = sys.argv[1]
payload = json.loads(urllib.request.urlopen(url, timeout=8).read().decode())
print(str(payload.get("health", {}).get("ready")).lower())
PY
  )"
  if [[ "${summary_ready}" == "true" ]]; then
    echo "provider summary ready"
    break
  fi
  sleep 2
done
[[ "${summary_ready}" == "true" ]] || {
  echo "provider summary did not become ready before load gate" >&2
  ${KUBECTL} get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded >&2 || true
  exit 1
}

load_log="$(mktemp)"
cleanup() {
  if [[ -n "${load_pid:-}" ]] && kill -0 "${load_pid}" >/dev/null 2>&1; then
    kill "${load_pid}" >/dev/null 2>&1 || true
  fi
  rm -f "${load_log}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "== provider portal conditional read load =="
python3 - \
  "${portal_url_csv}" \
  "${PORTAL_LOAD_ITERATIONS}" \
  "${PORTAL_LOAD_WORKERS}" \
  "${MIN_304_RATIO_PERCENT}" \
  "${MIN_BYTES_SAVED_PERCENT}" \
  "${MAX_P95_LATENCY_MS}" >"${load_log}" <<'PY' &
import concurrent.futures
import json
import statistics
import sys
import time
import urllib.error
import urllib.request

urls_csv, iterations, workers, min_304, min_saved, max_p95 = sys.argv[1:7]
urls = [url for url in urls_csv.split(",") if url]
iterations = int(iterations)
workers = int(workers)
min_304 = float(min_304)
min_saved = float(min_saved)
max_p95 = float(max_p95)

if not urls:
    raise SystemExit("no portal URLs")

warm = {}
for url in urls:
    deadline = time.monotonic() + 90
    last_error = None
    while True:
        start = time.monotonic()
        try:
            response = urllib.request.urlopen(f"{url}/api/summary?fresh=1", timeout=12)
            body = response.read()
            elapsed = (time.monotonic() - start) * 1000
            payload = json.loads(body.decode())
            if payload.get("health", {}).get("ready"):
                break
            last_error = f"summary health not ready: {payload.get('health', {})}"
            if time.monotonic() >= deadline:
                raise AssertionError(f"{url} summary warmup failed: {last_error}")
        except urllib.error.HTTPError as exc:
            body = exc.read()
            elapsed = (time.monotonic() - start) * 1000
            last_error = f"HTTP {exc.code} after {elapsed:.1f}ms body={body[:120]!r}"
            if exc.code not in (429, 503) or time.monotonic() >= deadline:
                raise AssertionError(f"{url} summary warmup failed: {last_error}")
        except Exception as exc:
            last_error = repr(exc)
            if time.monotonic() >= deadline:
                raise AssertionError(f"{url} summary warmup failed: {last_error}")
        time.sleep(2)
    etag = response.headers.get("ETag", "")
    if not etag.startswith('W/"sha256:'):
        raise AssertionError(f"{url} did not return weak semantic ETag: {etag!r}")
    warm[url] = {"etag": etag, "bytes": len(body), "latency_ms": elapsed}

def conditional_get(url):
    etag = warm[url]["etag"]
    request = urllib.request.Request(f"{url}/api/summary", headers={"If-None-Match": etag})
    start = time.monotonic()
    try:
        response = urllib.request.urlopen(request, timeout=8)
        body = response.read()
        status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status = exc.code
    elapsed = (time.monotonic() - start) * 1000
    if status not in (200, 304):
        raise AssertionError(f"{url} conditional summary returned HTTP {status}")
    return {"url": url, "status": status, "bytes": len(body), "latency_ms": elapsed}

tasks = []
for _ in range(iterations):
    tasks.extend(urls)

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
    for result in pool.map(conditional_get, tasks):
        results.append(result)

total = len(results)
not_modified = sum(1 for item in results if item["status"] == 304)
ratio_304 = 100.0 * not_modified / total if total else 0.0
actual_bytes = sum(item["bytes"] for item in results)
full_bytes = sum(warm[item["url"]]["bytes"] for item in results)
saved_ratio = 100.0 * (1.0 - (actual_bytes / full_bytes)) if full_bytes else 0.0
latencies = sorted(item["latency_ms"] for item in results)
index = max(0, min(len(latencies) - 1, int(len(latencies) * 0.95) - 1))
p95 = latencies[index] if latencies else 0.0

if ratio_304 < min_304:
    raise AssertionError(f"conditional 304 ratio {ratio_304:.1f}% below {min_304:.1f}%")
if saved_ratio < min_saved:
    raise AssertionError(f"conditional body-byte savings {saved_ratio:.1f}% below {min_saved:.1f}%")
if p95 > max_p95:
    raise AssertionError(f"conditional p95 latency {p95:.1f}ms above {max_p95:.1f}ms")

metrics = "\n".join(
    urllib.request.urlopen(f"{url}/metrics", timeout=8).read().decode()
    for url in urls
)
if "provider_portal_summary_response_bytes_total" not in metrics:
    raise AssertionError("expected provider_portal_summary_response_bytes_total metric")
if 'provider_portal_summary_requests_total{status="304"' not in metrics:
    raise AssertionError("expected provider_portal_summary_requests_total status=304 metric")

print(
    "portal conditional reads total=%d pods=%d 304_ratio=%.1f%% bytes_saved=%.1f%% p95=%.1fms warm_bytes=%d"
    % (total, len(urls), ratio_304, saved_ratio, p95, int(statistics.mean(x["bytes"] for x in warm.values())))
)
PY
load_pid="$!"

while kill -0 "${load_pid}" >/dev/null 2>&1; do
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" get --raw=/readyz >/dev/null
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" -n "${NAMESPACE}" get deploy/provider-portal >/dev/null
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" -n platform-system get deploy -l app.kubernetes.io/name=provider-controller >/dev/null
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" -n flux-system get kustomization platform-base >/dev/null
  curl -k --max-time 8 -fsS "https://${tenant_endpoint}/readyz" >/dev/null
  sleep 1
done

wait "${load_pid}"
cat "${load_log}"

echo "provider API load verification passed"
