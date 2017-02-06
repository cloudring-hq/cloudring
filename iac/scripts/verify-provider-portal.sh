#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
KUBE_REQUEST_TIMEOUT="${KUBE_REQUEST_TIMEOUT:-10s}"
KUBE_PROCESS_TIMEOUT="${KUBE_PROCESS_TIMEOUT:-20s}"
KUBE_ATTEMPTS="${KUBE_ATTEMPTS:-3}"
KUBE_WAIT_REQUEST_TIMEOUT="${KUBE_WAIT_REQUEST_TIMEOUT:-5s}"
KUBE_WAIT_PROCESS_TIMEOUT="${KUBE_WAIT_PROCESS_TIMEOUT:-8s}"
KUBE_WAIT_ATTEMPTS="${KUBE_WAIT_ATTEMPTS:-3}"
KUBE_SERVER_ENDPOINTS="${KUBE_SERVER_ENDPOINTS:-}"
KUBE_INSECURE_SKIP_TLS_VERIFY="${KUBE_INSECURE_SKIP_TLS_VERIFY:-true}"
PORTAL_STRICT_PRE_CLEANUP="${PORTAL_STRICT_PRE_CLEANUP:-false}"
PORTAL_SMOKE_ID="${PORTAL_SMOKE_ID:-$(date +%H%M%S)-$$}"
NAMESPACE="${NAMESPACE:-platform-system}"
SERVICE="${SERVICE:-provider-portal}"
WRITE_NAMESPACE="${WRITE_NAMESPACE:-tenant-c}"
WRITE_PROJECT="${WRITE_PROJECT:-ps-proj-${PORTAL_SMOKE_ID}}"
WRITE_PLAN="${WRITE_PLAN:-ps-plan-${PORTAL_SMOKE_ID}}"
WRITE_SUBSCRIPTION="${WRITE_SUBSCRIPTION:-ps-sub-${PORTAL_SMOKE_ID}}"
WRITE_ORDER="${WRITE_ORDER:-ps-order-${PORTAL_SMOKE_ID}}"
WRITE_SCHEDULED_ORDER="${WRITE_SCHEDULED_ORDER:-ps-sched-${PORTAL_SMOKE_ID}}"
WRITE_SUSPEND_ORDER="${WRITE_SUSPEND_ORDER:-ps-suspend-${PORTAL_SMOKE_ID}}"
WRITE_RESUME_ORDER="${WRITE_RESUME_ORDER:-ps-resume-${PORTAL_SMOKE_ID}}"
WRITE_RENEW_ORDER="${WRITE_RENEW_ORDER:-ps-renew-${PORTAL_SMOKE_ID}}"
WRITE_CANCEL_ORDER="${WRITE_CANCEL_ORDER:-ps-cancel-${PORTAL_SMOKE_ID}}"
WRITE_ORDER_SUBSCRIPTION="${WRITE_ORDER_SUBSCRIPTION:-ps-order-sub-${PORTAL_SMOKE_ID}}"
WRITE_VM_CLAIM="${WRITE_VM_CLAIM:-ps-vm-${PORTAL_SMOKE_ID}}"
WRITE_KCC_CLAIM="${WRITE_KCC_CLAIM:-ps-kcc-${PORTAL_SMOKE_ID}}"
WRITE_VOLUME="${WRITE_VOLUME:-ps-vol-${PORTAL_SMOKE_ID}}"
WRITE_NETWORK="${WRITE_NETWORK:-ps-net-${PORTAL_SMOKE_ID}}"
WRITE_FIREWALL_RULE="${WRITE_FIREWALL_RULE:-ps-fw-${PORTAL_SMOKE_ID}}"
WRITE_ACCESS_GRANT="${WRITE_ACCESS_GRANT:-ps-access-${PORTAL_SMOKE_ID}}"
RATE_LIMIT_SELECTOR='app=provider-portal,platform.privatecloud.local/write-rate-limit=true'

kube() {
  local attempt rc server
  local -a kube_servers kubectl_cmd server_args
  # KUBECTL intentionally accepts a command string such as "sudo k3s kubectl".
  kubectl_cmd=(${KUBECTL})
  kube_servers=()
  if [[ -n "${KUBE_SERVER_ENDPOINTS}" ]]; then
    IFS=',' read -r -a kube_servers <<<"${KUBE_SERVER_ENDPOINTS}"
  fi
  for attempt in $(seq 1 "${KUBE_ATTEMPTS}"); do
    server_args=()
    if [[ "${#kube_servers[@]}" -gt 0 ]]; then
      server="${kube_servers[$(((attempt - 1) % ${#kube_servers[@]}))]}"
      server_args=(--server="${server}")
      if [[ "${KUBE_INSECURE_SKIP_TLS_VERIFY}" == "true" ]]; then
        server_args+=(--insecure-skip-tls-verify=true)
      fi
    fi
    set +e
    if command -v timeout >/dev/null 2>&1; then
      timeout --foreground "${KUBE_PROCESS_TIMEOUT}" "${kubectl_cmd[@]}" "${server_args[@]}" --request-timeout="${KUBE_REQUEST_TIMEOUT}" "$@"
    else
      "${kubectl_cmd[@]}" "${server_args[@]}" --request-timeout="${KUBE_REQUEST_TIMEOUT}" "$@"
    fi
    rc=$?
    set -e
    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi
    if [[ "${attempt}" -eq "${KUBE_ATTEMPTS}" ]]; then
      return "${rc}"
    fi
    echo "kubectl ${*} failed, retrying (${attempt}/${KUBE_ATTEMPTS})" >&2
    sleep "${attempt}"
  done
}

wait_absent() {
  local resource="$1"
  local namespace="$2"
  local name="$3"
  local label="$4"
  for _ in $(seq 1 60); do
    if ! KUBE_ATTEMPTS="${KUBE_WAIT_ATTEMPTS}" KUBE_REQUEST_TIMEOUT="${KUBE_WAIT_REQUEST_TIMEOUT}" KUBE_PROCESS_TIMEOUT="${KUBE_WAIT_PROCESS_TIMEOUT}" kube -n "${namespace}" get "${resource}" "${name}" >/dev/null 2>&1; then
      echo "${label} absent"
      return 0
    fi
    sleep 2
  done
  echo "timed out waiting for ${label} to be absent" >&2
  return 1
}

wait_cluster_absent() {
  local resource="$1"
  local name="$2"
  local label="$3"
  for _ in $(seq 1 60); do
    if ! KUBE_ATTEMPTS="${KUBE_WAIT_ATTEMPTS}" KUBE_REQUEST_TIMEOUT="${KUBE_WAIT_REQUEST_TIMEOUT}" KUBE_PROCESS_TIMEOUT="${KUBE_WAIT_PROCESS_TIMEOUT}" kube get "${resource}" "${name}" >/dev/null 2>&1; then
      echo "${label} absent"
      return 0
    fi
    sleep 2
  done
  echo "timed out waiting for ${label} to be absent" >&2
  return 1
}

delete_write_smoke() {
  kube delete projects.platform.privatecloud.local "${WRITE_PROJECT}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube delete productplans.platform.privatecloud.local "${WRITE_PLAN}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  if [[ "${WRITE_PROJECT}" == portal-smoke-* || "${WRITE_PROJECT}" == ps-proj-* ]]; then
    kube delete namespace "${WRITE_PROJECT}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  fi
  kube -n "${WRITE_NAMESPACE}" delete subscriptions.platform.privatecloud.local "${WRITE_SUBSCRIPTION}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete orders.platform.privatecloud.local "${WRITE_CANCEL_ORDER}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete orders.platform.privatecloud.local "${WRITE_RENEW_ORDER}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete orders.platform.privatecloud.local "${WRITE_RESUME_ORDER}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete orders.platform.privatecloud.local "${WRITE_SUSPEND_ORDER}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete orders.platform.privatecloud.local "${WRITE_SCHEDULED_ORDER}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete orders.platform.privatecloud.local "${WRITE_ORDER}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete subscriptions.platform.privatecloud.local "${WRITE_ORDER_SUBSCRIPTION}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete virtualmachineclaim "${WRITE_VM_CLAIM}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete kubernetesclusterclaim "${WRITE_KCC_CLAIM}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete volumes.platform.privatecloud.local "${WRITE_VOLUME}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete networks.platform.privatecloud.local "${WRITE_NETWORK}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete firewallrules.platform.privatecloud.local "${WRITE_FIREWALL_RULE}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kube -n "${WRITE_NAMESPACE}" delete accessgrants.platform.privatecloud.local "${WRITE_ACCESS_GRANT}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
}

cleanup_write_smoke() {
  delete_write_smoke
  wait_absent subscriptions.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_SUBSCRIPTION}" "portal smoke subscription" >/dev/null || true
  wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_CANCEL_ORDER}" "portal smoke cancel order" >/dev/null || true
  wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_RENEW_ORDER}" "portal smoke renew order" >/dev/null || true
  wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_RESUME_ORDER}" "portal smoke resume order" >/dev/null || true
  wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_SUSPEND_ORDER}" "portal smoke suspend order" >/dev/null || true
  wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_SCHEDULED_ORDER}" "portal smoke scheduled order" >/dev/null || true
  wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_ORDER}" "portal smoke order" >/dev/null || true
  wait_absent subscriptions.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_ORDER_SUBSCRIPTION}" "portal smoke order subscription" >/dev/null || true
  wait_absent virtualmachineclaim "${WRITE_NAMESPACE}" "${WRITE_VM_CLAIM}" "portal smoke VM claim" >/dev/null || true
  wait_absent kubernetesclusterclaim "${WRITE_NAMESPACE}" "${WRITE_KCC_CLAIM}" "portal smoke Kubernetes claim" >/dev/null || true
  wait_absent volumes.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_VOLUME}" "portal smoke volume" >/dev/null || true
  wait_absent networks.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_NETWORK}" "portal smoke network" >/dev/null || true
  wait_absent firewallrules.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_FIREWALL_RULE}" "portal smoke firewall rule" >/dev/null || true
  wait_absent accessgrants.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_ACCESS_GRANT}" "portal smoke access grant" >/dev/null || true
  wait_cluster_absent productplans.platform.privatecloud.local "${WRITE_PLAN}" "portal smoke product plan" >/dev/null || true
  wait_cluster_absent projects.platform.privatecloud.local "${WRITE_PROJECT}" "portal smoke project" >/dev/null || true
}

cleanup_rate_limit_leases() {
  kube -n "${NAMESPACE}" delete lease -l "${RATE_LIMIT_SELECTOR}" --ignore-not-found >/dev/null 2>&1 || true
}

cleanup() {
  cleanup_write_smoke
  cleanup_rate_limit_leases
}

trap cleanup EXIT
cleanup_rate_limit_leases

echo "== provider portal rollout =="
kube -n "${NAMESPACE}" rollout status deploy/provider-portal --timeout=180s
kube -n "${NAMESPACE}" get deploy,hpa,pdb,svc,pod -l app=provider-portal -o wide

available="$(kube -n "${NAMESPACE}" get deploy provider-portal -o jsonpath='{.status.availableReplicas}')"
[[ "${available:-0}" -ge 2 ]] || { echo "expected provider-portal >=2 available replicas, got ${available:-0}" >&2; exit 1; }
min_available="$(kube -n "${NAMESPACE}" get pdb provider-portal -o jsonpath='{.spec.minAvailable}')"
[[ "${min_available}" == "4" ]] || { echo "expected provider-portal PDB minAvailable=4, got ${min_available}" >&2; exit 1; }
image="$(kube -n "${NAMESPACE}" get deploy provider-portal -o jsonpath='{.spec.template.spec.containers[0].image}')"
[[ "${image}" == "localhost/platform-provider-portal:dev" ]] || { echo "unexpected provider-portal image ${image}" >&2; exit 1; }
topology_policy="$(kube -n "${NAMESPACE}" get deploy provider-portal -o jsonpath='{.spec.template.spec.topologySpreadConstraints[0].whenUnsatisfiable}')"
[[ "${topology_policy}" == "DoNotSchedule" ]] || { echo "expected strict provider-portal topology spread DoNotSchedule, got ${topology_policy}" >&2; exit 1; }
topology_min_domains="$(kube -n "${NAMESPACE}" get deploy provider-portal -o jsonpath='{.spec.template.spec.topologySpreadConstraints[0].minDomains}')"
[[ "${topology_min_domains}" == "3" ]] || { echo "expected provider-portal topology spread minDomains=3, got ${topology_min_domains:-missing}" >&2; exit 1; }
topology_match_label_key="$(kube -n "${NAMESPACE}" get deploy provider-portal -o jsonpath='{.spec.template.spec.topologySpreadConstraints[0].matchLabelKeys[0]}')"
[[ "${topology_match_label_key}" == "pod-template-hash" ]] || { echo "expected provider-portal topology spread matchLabelKeys[0]=pod-template-hash, got ${topology_match_label_key:-missing}" >&2; exit 1; }
ready_portal_nodes="$(
  kube -n "${NAMESPACE}" get pods -l app=provider-portal -o json | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
nodes = set()
for item in payload.get("items", []):
    metadata = item.get("metadata", {})
    status = item.get("status", {})
    if metadata.get("deletionTimestamp") or status.get("phase") != "Running":
        continue
    if not any(c.get("type") == "Ready" and c.get("status") == "True" for c in status.get("conditions", [])):
        continue
    node = item.get("spec", {}).get("nodeName")
    if node:
        nodes.add(node)
print(len(nodes))
'
)"
[[ "${ready_portal_nodes}" -ge 3 ]] || { echo "expected Ready provider-portal pods on 3 distinct nodes, got ${ready_portal_nodes}" >&2; exit 1; }
hpa_min="$(kube -n "${NAMESPACE}" get hpa provider-portal -o jsonpath='{.spec.minReplicas}')"
hpa_max="$(kube -n "${NAMESPACE}" get hpa provider-portal -o jsonpath='{.spec.maxReplicas}')"
[[ "${hpa_min}" == "6" ]] || { echo "expected provider-portal HPA minReplicas=6, got ${hpa_min}" >&2; exit 1; }
[[ "${hpa_max}" == "9" ]] || { echo "expected provider-portal HPA maxReplicas=9, got ${hpa_max}" >&2; exit 1; }
desired="$(kube -n "${NAMESPACE}" get deploy provider-portal -o jsonpath='{.spec.replicas}')"
[[ "${desired:-0}" -ge "${hpa_min}" && "${desired:-0}" -le "${hpa_max}" ]] || {
  echo "expected provider-portal desired replicas between HPA bounds ${hpa_min}-${hpa_max}, got ${desired:-0}" >&2
  exit 1
}
kube -n "${NAMESPACE}" get hpa provider-portal -o json | python3 -c '
import json
import sys

hpa = json.load(sys.stdin)
ref = hpa["spec"]["scaleTargetRef"]
assert ref["apiVersion"] == "apps/v1", ref
assert ref["kind"] == "Deployment", ref
assert ref["name"] == "provider-portal", ref
targets = {
    item["resource"]["name"]: item["resource"]["target"]["averageUtilization"]
    for item in hpa["spec"].get("metrics", [])
    if item.get("type") == "Resource"
}
assert targets.get("cpu") == 60, targets
assert targets.get("memory") == 75, targets
behavior = hpa["spec"].get("behavior", {})
assert behavior.get("scaleDown", {}).get("stabilizationWindowSeconds") == 300, behavior
print("provider-portal HPA target=Deployment/provider-portal min=%s max=%s metrics=%s" % (
    hpa["spec"].get("minReplicas"),
    hpa["spec"].get("maxReplicas"),
    ",".join(sorted(targets)),
))
'
for _ in $(seq 1 90); do
  scaling_active="$(kube -n "${NAMESPACE}" get hpa provider-portal -o jsonpath='{.status.conditions[?(@.type=="ScalingActive")].status}' 2>/dev/null || true)"
  able_to_scale="$(kube -n "${NAMESPACE}" get hpa provider-portal -o jsonpath='{.status.conditions[?(@.type=="AbleToScale")].status}' 2>/dev/null || true)"
  if [[ "${scaling_active}" == "True" && "${able_to_scale}" == "True" ]]; then
    echo "provider-portal HPA ScalingActive=True AbleToScale=True"
    break
  fi
  sleep 2
done
[[ "${scaling_active:-}" == "True" && "${able_to_scale:-}" == "True" ]] || {
  echo "provider-portal HPA did not become ScalingActive/AbleToScale" >&2
  kube -n "${NAMESPACE}" describe hpa provider-portal >&2 || true
  exit 1
}

endpoint="$(kube -n "${NAMESPACE}" get svc "${SERVICE}" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
[[ -n "${endpoint}" ]] || { echo "expected provider-portal LoadBalancer IP" >&2; exit 1; }

echo "== provider portal API from cluster =="
portal_targets="$(
  kube -n "${NAMESPACE}" get pods -l app=provider-portal -o json | python3 -c '
import json
import sys

data = json.load(sys.stdin)
for item in data.get("items", []):
    meta = item.get("metadata", {})
    status = item.get("status", {})
    if meta.get("deletionTimestamp") or status.get("phase") != "Running":
        continue
    ready = any(
        condition.get("type") == "Ready" and condition.get("status") == "True"
        for condition in status.get("conditions", [])
    )
    ip = status.get("podIP")
    if ready and ip:
        print("%s %s" % (meta.get("name"), ip))
'
)"
[[ -n "${portal_targets}" ]] || { echo "expected a Ready provider-portal pod" >&2; exit 1; }
portal_target_count="$(printf "%s\n" "${portal_targets}" | sed '/^$/d' | wc -l)"
[[ "${portal_target_count}" -ge 2 ]] || { echo "expected at least two Ready provider-portal pods for shared rate-limit verification, got ${portal_target_count}" >&2; exit 1; }
portal_target="$(printf "%s\n" "${portal_targets}" | sed '/^$/d' | head -1)"
portal_urls="$(
  printf "%s\n" "${portal_targets}" | sed '/^$/d' | awk '{print "http://"$2":8080"}' | paste -sd, -
)"
read -r pod pod_ip <<<"${portal_target}"
portal_base_url="http://${pod_ip}:8080"
echo "selected provider-portal pod=${pod} url=${portal_base_url} readyPods=${portal_target_count}"
python3 - "${portal_base_url}" <<'PY'
import json
import sys
import time
import urllib.error
import urllib.request

base_url = sys.argv[1]

def open_retry(target, timeout=5, attempts=12):
    last_error = None
    for attempt in range(attempts):
        try:
            return urllib.request.urlopen(target, timeout=timeout)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code != 429 or attempt == attempts - 1:
                raise
            exc.read()
            time.sleep(min(2.0, 0.25 * (attempt + 1)))
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
            time.sleep(min(2.0, 0.25 * (attempt + 1)))
    raise last_error

raw = open_retry(f"{base_url}/api/summary", timeout=5).read()
assert len(raw) < 250000, "summary payload should stay compact for portal read path"
summary = json.loads(raw.decode())
cached_response = open_retry(f"{base_url}/api/summary", timeout=5)
cached = json.loads(cached_response.read().decode())
etag = cached_response.headers.get("ETag", "")
metrics = urllib.request.urlopen(f"{base_url}/metrics", timeout=5).read().decode()
assert summary["projects"], "expected projects"
assert summary["capacityCells"], "expected capacity cells"
assert "productPlans" in summary, "expected product plan catalog inventory"
assert "subscriptions" in summary, "expected subscription inventory"
assert "orders" in summary, "expected order inventory"
assert summary["vmClaims"], "expected VM claims"
assert summary["kubernetesClusterClaims"], "expected Kubernetes cluster claims"
assert "volumes" in summary, "expected volume inventory"
assert "networks" in summary, "expected network inventory"
assert "firewallRules" in summary, "expected firewall rule inventory"
assert "accessGrants" in summary, "expected access grant inventory"
assert "auditEvents" in summary, "expected self-service audit events collection"
assert "admissionJournals" in summary, "expected admission journal collection"
assert "health" in summary, "expected health block"
assert "cache" in summary, "expected cache metadata"
assert summary["health"].get("writeAuthMode") == "oidc-jwks", "expected OIDC/JWKS write auth mode"
assert summary["health"].get("writeAuthRequired") is True, "expected write auth to be required"
assert summary["health"].get("writeAuthIssuer") == "https://issuer.platform.local", "expected lab JWT issuer"
assert summary["health"].get("writeAuthAudience") == "platform-portal", "expected lab JWT audience"
assert summary["health"].get("writeAuthJwksUri") == "http://provider-portal.platform-system.svc.cluster.local/oidc/jwks.json", "expected lab JWKS URI"
assert summary["health"].get("writeAuthAllowedAlgorithms") == ["RS256"], "expected only RS256"
assert summary["health"].get("writeAuthHs256Configured") is False, "expected no HS256 secret"
assert summary["health"].get("writeAuthGroupsClaim") == "groups", "expected groups claim"
assert summary["health"].get("writeAuthNamespacesClaim") == "platform_namespaces", "expected namespaces claim"
jwks = json.loads(urllib.request.urlopen(f"{base_url}/oidc/jwks.json", timeout=5).read().decode())
assert len(jwks.get("keys", [])) == 1, "expected one lab JWKS key"
assert jwks["keys"][0].get("alg") == "RS256", "expected RS256 lab JWKS key"
configuration = json.loads(urllib.request.urlopen(f"{base_url}/.well-known/openid-configuration", timeout=5).read().decode())
assert configuration.get("issuer") == "https://issuer.platform.local", "expected lab OIDC issuer"
assert configuration.get("jwks_uri") == "http://provider-portal.platform-system.svc.cluster.local/oidc/jwks.json", "expected configured JWKS URI"
assert configuration.get("id_token_signing_alg_values_supported") == ["RS256"], "expected RS256 discovery algs"
rate_limit = summary["health"].get("writeRateLimit") or {}
assert rate_limit.get("enabled") is True, "expected write rate limiting to be enabled"
assert int(rate_limit.get("maxRequests", 0)) == 8, "expected write rate limit maxRequests=8"
assert int(float(rate_limit.get("windowSeconds", 0))) == 10, "expected write rate limit windowSeconds=10"
assert rate_limit.get("scope") == "shared", "expected shared write rate limit scope"
assert rate_limit.get("backend") == "kubernetes-lease", "expected Kubernetes Lease rate-limit backend"
assert cached["cache"]["mode"] in ("hit", "miss", "stale"), "expected cache mode"
assert etag.startswith('W/"sha256:'), f"expected weak semantic summary ETag, got {etag!r}"
assert "private" in cached_response.headers.get("Cache-Control", ""), "expected private summary cache-control"
conditional = urllib.request.Request(f"{base_url}/api/summary", headers={"If-None-Match": etag})
try:
    open_retry(conditional, timeout=5)
    raise AssertionError("expected summary conditional GET to return 304")
except urllib.error.HTTPError as exc:
    assert exc.code == 304, f"expected 304, got {exc.code}"
    assert exc.headers.get("ETag") == etag, "expected 304 to preserve ETag"
metrics = urllib.request.urlopen(f"{base_url}/metrics", timeout=5).read().decode()
assert "provider_portal_summary_cache_total" in metrics, "expected portal cache metrics"
assert "provider_portal_summary_requests_total" in metrics, "expected portal summary request metrics"
assert "provider_portal_summary_response_bytes_total" in metrics, "expected portal summary byte metrics"
assert 'provider_portal_summary_requests_total{status="304"' in metrics, "expected 304 summary metric"
print(
    "summary projects=%d vms=%d kcc=%d cells=%d cache=%s"
    % (
        len(summary["projects"]),
        len(summary["vmClaims"]),
        len(summary["kubernetesClusterClaims"]),
        len(summary["capacityCells"]),
        cached["cache"]["mode"],
    )
)
PY

echo "== provider portal write API from cluster =="
if [[ "${PORTAL_STRICT_PRE_CLEANUP}" == "true" ]]; then
  cleanup_write_smoke
else
  delete_write_smoke
fi
cleanup_rate_limit_leases
echo "provider portal write pre-cleanup complete"
private_jwk="$(
  kube -n "${NAMESPACE}" get secret provider-portal-auth -o json | python3 -c '
import base64
import json
import sys

secret = json.load(sys.stdin)
print(base64.b64decode(secret["data"]["jwt-rs256-private-jwk"]).decode())
'
)"
echo "provider portal write auth secret loaded"
PORTAL_PRIVATE_JWK="${private_jwk}" python3 - \
  "${portal_base_url}" \
  "${portal_urls}" \
  "${WRITE_NAMESPACE}" \
  "${WRITE_PROJECT}" \
  "${WRITE_PLAN}" \
  "${WRITE_SUBSCRIPTION}" \
  "${WRITE_ORDER}" \
  "${WRITE_SCHEDULED_ORDER}" \
  "${WRITE_SUSPEND_ORDER}" \
  "${WRITE_RESUME_ORDER}" \
  "${WRITE_RENEW_ORDER}" \
  "${WRITE_CANCEL_ORDER}" \
  "${WRITE_ORDER_SUBSCRIPTION}" \
  "${WRITE_VM_CLAIM}" \
  "${WRITE_KCC_CLAIM}" \
  "${WRITE_VOLUME}" \
  "${WRITE_NETWORK}" \
  "${WRITE_FIREWALL_RULE}" \
  "${WRITE_ACCESS_GRANT}" \
  "https://issuer.platform.local" \
  "platform-portal" <<'PY'
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

base_url, portal_urls_csv, namespace, project_name, plan_name, subscription_name, order_name, scheduled_order_name, suspend_order_name, resume_order_name, renew_order_name, cancel_order_name, order_subscription_name, vm_name, kcc_name, volume_name, network_name, firewall_name, access_name, jwt_issuer, jwt_audience = sys.argv[1:22]
portal_urls = [item for item in portal_urls_csv.split(",") if item]
if not portal_urls:
    portal_urls = [base_url]
invalid_token = "not-a-real-portal-token"
private_jwk_json = os.environ["PORTAL_PRIVATE_JWK"]
private_jwk = json.loads(private_jwk_json)
rsa_n = int.from_bytes(base64.urlsafe_b64decode(private_jwk["n"] + "=" * (-len(private_jwk["n"]) % 4)), "big")
rsa_d = int.from_bytes(base64.urlsafe_b64decode(private_jwk["d"] + "=" * (-len(private_jwk["d"]) % 4)), "big")
rsa_key_bytes = (rsa_n.bit_length() + 7) // 8
sha256_digestinfo_prefix = bytes.fromhex("3031300d060960864801650304020105000420")

def b64url(payload):
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")

def issue_token(subject, groups, namespaces, exp_offset=600, audience=None, issuer=None, nbf_offset=-10, iat_offset=0):
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT", "kid": private_jwk["kid"]}
    claims = {
        "iss": issuer or jwt_issuer,
        "aud": audience or jwt_audience,
        "sub": subject,
        "groups": groups,
        "platform_namespaces": namespaces,
        "iat": now + iat_offset,
        "nbf": now + nbf_offset,
        "exp": now + exp_offset,
    }
    signing_input = ".".join(
        [
            b64url(json.dumps(header, sort_keys=True, separators=(",", ":")).encode()),
            b64url(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()),
        ]
    )
    digest = hashlib.sha256(signing_input.encode()).digest()
    padding_len = rsa_key_bytes - len(sha256_digestinfo_prefix) - len(digest) - 3
    if padding_len < 8:
        raise AssertionError("lab RSA key is too small")
    encoded = b"\x00\x01" + (b"\xff" * padding_len) + b"\x00" + sha256_digestinfo_prefix + digest
    signature = pow(int.from_bytes(encoded, "big"), rsa_d, rsa_n).to_bytes(rsa_key_bytes, "big")
    return f"{signing_input}.{b64url(signature)}"

tenant_token = issue_token("lab:tenant-c-admin", ["platform:tenant-c:admins", "platform:tenants"], [namespace])
wrong_tenant_token = issue_token("lab:tenant-a-admin", ["platform:tenant-a:admins", "platform:tenants"], ["tenant-a"])
platform_admin_token = issue_token("lab:platform-admin", ["platform:admins"], ["*"])
expired_token = issue_token("lab:tenant-c-admin", ["platform:tenant-c:admins", "platform:tenants"], [namespace], exp_offset=-120)
wrong_audience_token = issue_token("lab:tenant-c-admin", ["platform:tenant-c:admins", "platform:tenants"], [namespace], audience="other-platform")
hs256_token = ".".join(
    [
        b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, sort_keys=True, separators=(",", ":")).encode()),
        tenant_token.split(".")[1],
        b64url(hashlib.sha256(b"not-a-real-shared-secret").digest()),
    ]
)
token_header, token_payload, token_signature = tenant_token.split(".")
tampered_signature = ("A" if token_signature[0] != "A" else "B") + token_signature[1:]
invalid_signature_token = ".".join([token_header, token_payload, tampered_signature])

def request(method, path, payload=None, expected=(200, 201), token=None, target_base_url=None, attempts=12, timeout=8):
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    targets = [target_base_url] if target_base_url else (portal_urls or [base_url])
    last_error = None
    for attempt in range(attempts):
        target = targets[attempt % len(targets)]
        req = urllib.request.Request(f"{target}{path}", data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode()
                if response.status not in expected:
                    raise AssertionError(f"{method} {path} returned {response.status}: {raw}")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode()
            if exc.code in expected:
                return json.loads(raw) if raw else {}
            last_error = AssertionError(f"{method} {path} returned {exc.code}: {raw}")
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise last_error from exc
            time.sleep(min(2.0, 0.25 * (attempt + 1)))
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
            time.sleep(min(2.0, 0.25 * (attempt + 1)))
    raise last_error

def summary(require_fresh=False):
    targets = portal_urls or [base_url]
    last_error = None
    max_attempts = 36 if require_fresh else 24
    for attempt in range(max_attempts):
        target = targets[attempt % len(targets)]
        path = "/api/summary?fresh=1" if require_fresh or attempt < 18 else "/api/summary"
        try:
            data = request("GET", path, target_base_url=target, attempts=1, timeout=12 if require_fresh else 6)
            if require_fresh and data.get("cache", {}).get("stale"):
                last_error = AssertionError("summary refresh returned stale cache")
                time.sleep(min(2.0, 0.25 * (attempt + 1)))
                continue
            return data
        except (AssertionError, TimeoutError, urllib.error.URLError, OSError) as exc:
            last_error = exc
            message = str(exc)
            transient = isinstance(exc, (TimeoutError, urllib.error.URLError, OSError)) or any(
                f"returned {code}" in message for code in (429, 500, 502, 503, 504)
            )
            if not transient:
                raise
            time.sleep(min(2.0, 0.25 * (attempt + 1)))
    raise last_error

project_payload = {
    "name": project_name,
    "tenantId": project_name,
    "displayName": "Portal Smoke Project",
    "tier": "shared",
    "adminsGroup": f"platform:{project_name}:admins",
    "quotas": {
        "cpu": "1000m",
        "memory": "1Gi",
        "vms": 2,
        "tenantClusters": 1,
        "volumes": 4,
    },
    "network": {
        "defaultDeny": True,
        "allowInternetEgress": False,
        "allowedLoadBalancers": 0,
    },
}
plan_payload = {
    "name": plan_name,
    "displayName": "Portal Smoke Basic VM Plan",
    "category": "compute",
    "visibility": "public",
    "lifecycle": {"state": "Published"},
    "service": {
        "kind": "VirtualMachineClaim",
        "serviceClass": "tiny-vm",
        "defaultImage": "cirros",
        "capacityCellSelector": {"zone": "single-host", "storage": "longhorn-lab"},
    },
    "quotaProfile": {"cpu": "1000m", "memory": "1Gi", "vms": 1, "volumes": 1},
    "commercial": {"billingMode": "free", "currency": "USD"},
}
subscription_payload = {
    "namespace": namespace,
    "name": subscription_name,
    "projectRef": namespace,
    "planRef": plan_name,
    "state": "Active",
    "autoRenew": True,
    "requestedBy": "lab:tenant-c-admin",
}
order_payload = {
    "namespace": namespace,
    "name": order_name,
    "projectRef": namespace,
    "action": "CreateSubscription",
    "state": "Submitted",
    "planRef": plan_name,
    "subscriptionRef": order_subscription_name,
    "idempotencyKey": f"{namespace}:{order_name}:create-subscription:v1",
    "requestedBy": "lab:tenant-c-admin",
    "policy": {"decision": "Allowed"},
    "approval": {"required": False},
    "budget": {"currency": "USD", "estimatedMonthly": "0"},
}
suspend_order_payload = dict(
    order_payload,
    name=suspend_order_name,
    action="SuspendSubscription",
    idempotencyKey=f"{namespace}:{suspend_order_name}:suspend-subscription:v1",
)
scheduled_order_payload = dict(
    order_payload,
    name=scheduled_order_name,
    action="SuspendSubscription",
    idempotencyKey=f"{namespace}:{scheduled_order_name}:scheduled-suspend-subscription:v1",
    schedule={
        "notBefore": (datetime.now(timezone.utc) + timedelta(minutes=10)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "reason": "portal smoke delayed execution window",
    },
)
resume_order_payload = dict(
    order_payload,
    name=resume_order_name,
    action="ResumeSubscription",
    idempotencyKey=f"{namespace}:{resume_order_name}:resume-subscription:v1",
)
renew_order_payload = dict(
    order_payload,
    name=renew_order_name,
    action="RenewSubscription",
    idempotencyKey=f"{namespace}:{renew_order_name}:renew-subscription:v1",
)
cancel_order_payload = dict(
    order_payload,
    name=cancel_order_name,
    action="CancelSubscription",
    idempotencyKey=f"{namespace}:{cancel_order_name}:cancel-subscription:v1",
)
vm_payload = {
    "namespace": namespace,
    "name": vm_name,
    "projectRef": namespace,
    "class": "tiny",
    "image": "cirros",
    "cpu": 1,
    "memory": "256Mi",
    "rootDisk": "1Gi",
    "serviceClass": "tiny-vm",
    "failureDomains": {"zone": "single-host", "storage": "longhorn-lab"},
}
kcc_payload = {
    "namespace": namespace,
    "name": kcc_name,
    "projectRef": namespace,
    "version": "v1.32.1",
    "controlPlaneReplicas": 1,
    "workerReplicas": 0,
    "serviceClass": "tiny-tenant-kubernetes",
    "failureDomains": {"zone": "single-host", "storage": "longhorn-lab"},
    "podCIDR": "10.246.0.0/16",
    "serviceCIDR": "10.98.0.0/12",
}
volume_payload = {
    "namespace": namespace,
    "name": volume_name,
    "projectRef": namespace,
    "size": "1Gi",
    "class": "replicated",
    "accessMode": "ReadWriteOnce",
    "sourceType": "empty",
    "encryptionEnabled": False,
    "reclaimPolicy": "Snapshot",
}
network_payload = {
    "namespace": namespace,
    "name": network_name,
    "projectRef": namespace,
    "type": "isolated",
    "cidr": "10.248.0.0/24",
    "gateway": "10.248.0.1",
    "dns": ["10.96.0.10"],
    "egress": {"allowInternet": False, "nat": False},
    "loadBalancer": {"allowed": False},
}
firewall_payload = {
    "namespace": namespace,
    "name": firewall_name,
    "projectRef": namespace,
    "networkRef": network_name,
    "direction": "Ingress",
    "action": "Allow",
    "priority": 100,
    "rules": [
        {
            "protocol": "TCP",
            "ports": [443, 6443],
            "cidrs": ["172.28.10.0/24"],
        }
    ],
}
access_payload = {
    "namespace": namespace,
    "name": access_name,
    "projectRef": namespace,
    "subject": {"kind": "Group", "name": "platform:tenant-c:admins", "provider": "oidc"},
    "role": "viewer",
    "target": {"kind": "Project", "name": namespace},
    "duration": "8h",
    "approval": {"required": False},
}
cross_tenant_payload = dict(vm_payload, namespace="tenant-a", projectRef="tenant-a", name="portal-cross-tenant-vm")
project_mismatch_payload = dict(vm_payload, projectRef="tenant-a", name="portal-project-mismatch-vm")

assert "manage projects" in request("POST", "/api/claims/projects", project_payload, expected=(403,), token=tenant_token).get("error", "").lower()
request("POST", "/api/claims/projects", project_payload, expected=(201,), token=platform_admin_token)
for _ in range(30):
    data = summary(require_fresh=True)
    project_seen = any(x["metadata"]["name"] == project_name for x in data["projects"])
    if project_seen:
        break
    time.sleep(2)
else:
    raise AssertionError("created portal smoke Project did not appear in /api/summary")
request("DELETE", f"/api/claims/projects/{project_name}/{project_name}", expected=(403,), token=tenant_token)
request("DELETE", f"/api/claims/projects/{project_name}/{project_name}", token=platform_admin_token)
assert "manage projects" in request("POST", "/api/claims/productplans", plan_payload, expected=(403,), token=tenant_token).get("error", "").lower()
request("POST", "/api/claims/productplans", plan_payload, expected=(201,), token=platform_admin_token)
for _ in range(30):
    data = summary(require_fresh=True)
    plan_seen = any(x["metadata"]["name"] == plan_name for x in data.get("productPlans", []))
    if plan_seen:
        break
    time.sleep(2)
else:
    raise AssertionError("created portal smoke product plan did not appear in /api/summary")
print("portal write admin project and product plan checks passed", flush=True)

assert "bearer" in request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(401,)).get("error", "").lower()
assert "bearer" in request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(401,), token=invalid_token).get("error", "").lower()
assert "bearer" in request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(401,), token=invalid_signature_token).get("error", "").lower()
assert "algorithm" in request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(401,), token=hs256_token).get("error", "").lower()
assert "expired" in request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(401,), token=expired_token).get("error", "").lower()
assert "audience" in request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(401,), token=wrong_audience_token).get("error", "").lower()
assert "not allowed" in request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(403,), token=wrong_tenant_token).get("error", "").lower()
assert "not allowed" in request("POST", "/api/claims/virtualmachineclaims", cross_tenant_payload, expected=(403,), token=tenant_token).get("error", "").lower()
assert "projectref" in request("POST", "/api/claims/virtualmachineclaims", project_mismatch_payload, expected=(400,), token=tenant_token).get("error", "").lower()
request("DELETE", f"/api/claims/virtualmachineclaims/{namespace}/{vm_name}", expected=(401,))
request("DELETE", f"/api/claims/virtualmachineclaims/{namespace}/{vm_name}", expected=(403,), token=wrong_tenant_token)
print("portal write auth and validation negative checks passed", flush=True)

request("POST", "/api/claims/virtualmachineclaims", vm_payload, expected=(201,), token=tenant_token)
request("POST", "/api/claims/kubernetesclusterclaims", kcc_payload, expected=(201,), token=tenant_token)

for _ in range(30):
    data = summary(require_fresh=True)
    vm_seen = any(x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == vm_name for x in data["vmClaims"])
    kcc_seen = any(x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == kcc_name for x in data["kubernetesClusterClaims"])
    if vm_seen and kcc_seen:
        break
    time.sleep(2)
else:
    raise AssertionError("created portal smoke claims did not appear in /api/summary")

request("DELETE", f"/api/claims/virtualmachineclaims/{namespace}/{vm_name}", token=tenant_token)
request("DELETE", f"/api/claims/kubernetesclusterclaims/{namespace}/{kcc_name}", token=tenant_token)
print("portal write VM and Kubernetes claim lifecycle passed", flush=True)

time.sleep(11)
request("POST", "/api/claims/subscriptions", subscription_payload, expected=(201,), token=tenant_token)
for _ in range(30):
    data = summary(require_fresh=True)
    subscription = next((x for x in data.get("subscriptions", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == subscription_name), None)
    if subscription and subscription.get("status", {}).get("phase") == "Active":
        break
    time.sleep(2)
else:
    raise AssertionError("created portal smoke subscription did not become Active in /api/summary")
request("DELETE", f"/api/claims/subscriptions/{namespace}/{subscription_name}", token=tenant_token)
print("portal write direct subscription lifecycle passed", flush=True)

request("POST", "/api/claims/orders", order_payload, expected=(201,), token=tenant_token)
for _ in range(45):
    data = summary(require_fresh=True)
    order = next((x for x in data.get("orders", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == order_name), None)
    order_subscription = next((x for x in data.get("subscriptions", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == order_subscription_name), None)
    if (
        order
        and order.get("status", {}).get("phase") == "Succeeded"
        and order_subscription
        and order_subscription.get("status", {}).get("phase") == "Active"
    ):
        break
    time.sleep(2)
else:
    raise AssertionError("created portal smoke order did not provision an Active subscription in /api/summary")
print("portal write create-subscription order lifecycle passed", flush=True)

request("POST", "/api/claims/orders", scheduled_order_payload, expected=(201,), token=tenant_token)
for _ in range(45):
    data = summary(require_fresh=True)
    scheduled_order = next((x for x in data.get("orders", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == scheduled_order_name), None)
    order_subscription = next((x for x in data.get("subscriptions", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == order_subscription_name), None)
    if (
        scheduled_order
        and scheduled_order.get("status", {}).get("phase") == "Scheduled"
        and scheduled_order.get("status", {}).get("reason") == "OrderWindowPending"
        and order_subscription
        and order_subscription.get("status", {}).get("phase") == "Active"
        and order_subscription.get("spec", {}).get("state") == "Active"
    ):
        break
    time.sleep(2)
else:
    raise AssertionError("portal smoke scheduled order did not stay Scheduled without mutating the target subscription")
request("DELETE", f"/api/claims/orders/{namespace}/{scheduled_order_name}", token=tenant_token)
print("portal write scheduled order guard passed", flush=True)

time.sleep(11)
request("POST", "/api/claims/orders", suspend_order_payload, expected=(201,), token=tenant_token)
for _ in range(45):
    data = summary(require_fresh=True)
    suspend_order = next((x for x in data.get("orders", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == suspend_order_name), None)
    order_subscription = next((x for x in data.get("subscriptions", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == order_subscription_name), None)
    if (
        suspend_order
        and suspend_order.get("status", {}).get("phase") == "Succeeded"
        and order_subscription
        and order_subscription.get("status", {}).get("phase") == "Suspended"
    ):
        break
    time.sleep(2)
else:
    raise AssertionError("portal smoke suspend order did not suspend the target subscription in /api/summary")
print("portal write suspend order lifecycle passed", flush=True)

request("POST", "/api/claims/orders", resume_order_payload, expected=(201,), token=tenant_token)
for _ in range(45):
    data = summary(require_fresh=True)
    resume_order = next((x for x in data.get("orders", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == resume_order_name), None)
    order_subscription = next((x for x in data.get("subscriptions", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == order_subscription_name), None)
    if (
        resume_order
        and resume_order.get("status", {}).get("phase") == "Succeeded"
        and order_subscription
        and order_subscription.get("status", {}).get("phase") == "Active"
    ):
        break
    time.sleep(2)
else:
    raise AssertionError("portal smoke resume order did not resume the target subscription in /api/summary")
print("portal write resume order lifecycle passed", flush=True)

request("POST", "/api/claims/orders", renew_order_payload, expected=(201,), token=tenant_token)
for _ in range(45):
    data = summary(require_fresh=True)
    renew_order = next((x for x in data.get("orders", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == renew_order_name), None)
    if renew_order and renew_order.get("status", {}).get("phase") == "Succeeded":
        break
    time.sleep(2)
else:
    raise AssertionError("portal smoke renew order did not reach Succeeded in /api/summary")
print("portal write renew order lifecycle passed", flush=True)

request("POST", "/api/claims/orders", cancel_order_payload, expected=(201,), token=tenant_token)
for _ in range(45):
    data = summary(require_fresh=True)
    cancel_order = next((x for x in data.get("orders", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == cancel_order_name), None)
    order_subscription = next((x for x in data.get("subscriptions", []) if x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == order_subscription_name), None)
    if (
        cancel_order
        and cancel_order.get("status", {}).get("phase") == "Succeeded"
        and order_subscription
        and order_subscription.get("status", {}).get("phase") == "Cancelled"
    ):
        break
    time.sleep(2)
else:
    raise AssertionError("portal smoke cancel order did not cancel the target subscription in /api/summary")
print("portal write cancel order lifecycle passed", flush=True)

time.sleep(11)
request("DELETE", f"/api/claims/subscriptions/{namespace}/{order_subscription_name}", token=tenant_token)
request("DELETE", f"/api/claims/orders/{namespace}/{cancel_order_name}", token=tenant_token)
request("DELETE", f"/api/claims/orders/{namespace}/{renew_order_name}", token=tenant_token)
request("DELETE", f"/api/claims/orders/{namespace}/{resume_order_name}", token=tenant_token)
request("DELETE", f"/api/claims/orders/{namespace}/{suspend_order_name}", token=tenant_token)
request("DELETE", f"/api/claims/orders/{namespace}/{scheduled_order_name}", expected=(200, 404), token=tenant_token)
request("DELETE", f"/api/claims/orders/{namespace}/{order_name}", token=tenant_token)

time.sleep(11)
request("POST", "/api/claims/volumes", volume_payload, expected=(201,), token=tenant_token)
request("POST", "/api/claims/networks", network_payload, expected=(201,), token=tenant_token)
request("POST", "/api/claims/firewallrules", firewall_payload, expected=(201,), token=tenant_token)
request("POST", "/api/claims/accessgrants", access_payload, expected=(201,), token=tenant_token)

for _ in range(30):
    data = summary(require_fresh=True)
    volume_seen = any(x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == volume_name for x in data.get("volumes", []))
    network_seen = any(x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == network_name for x in data.get("networks", []))
    firewall_seen = any(x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == firewall_name for x in data.get("firewallRules", []))
    access_seen = any(x["metadata"]["namespace"] == namespace and x["metadata"]["name"] == access_name for x in data.get("accessGrants", []))
    if volume_seen and network_seen and firewall_seen and access_seen:
        break
    time.sleep(2)
else:
    raise AssertionError("created portal smoke extended resources did not appear in /api/summary")

request("DELETE", f"/api/claims/accessgrants/{namespace}/{access_name}", token=tenant_token)
request("DELETE", f"/api/claims/firewallrules/{namespace}/{firewall_name}", token=tenant_token)
request("DELETE", f"/api/claims/networks/{namespace}/{network_name}", token=tenant_token)
request("DELETE", f"/api/claims/volumes/{namespace}/{volume_name}", token=tenant_token)
request("DELETE", f"/api/claims/productplans/{plan_name}/{plan_name}", token=platform_admin_token)
print("portal write extended resource lifecycle passed", flush=True)

rate_limited = False
time.sleep(11)
for attempt in range(10):
    target = portal_urls[attempt % len(portal_urls)]
    result = request(
        "POST",
        "/api/claims/virtualmachineclaims",
        project_mismatch_payload,
        expected=(400, 429),
        token=tenant_token,
        target_base_url=target,
    )
    if "rate limit" in result.get("error", "").lower():
        assert result.get("retryAfterSeconds", 0) >= 1, result
        rate_limited = True
        break
if not rate_limited:
    raise AssertionError("tenant write burst across portal pods did not hit shared portal rate limit")
print("portal write shared rate limit check passed", flush=True)

metrics = "\n".join(
    urllib.request.urlopen(f"{url}/metrics", timeout=5).read().decode()
    for url in portal_urls
)
def load_audit_sets():
    loaded = summary(require_fresh=True).get("auditEvents", [])
    loaded_project_matching = [
        item for item in loaded
        if item.get("namespace") == "platform-system"
        and item.get("subject") == "lab:platform-admin"
        and item.get("resource") == "projects"
        and item.get("resourceName") == project_name
    ]
    loaded_plan_matching = [
        item for item in loaded
        if item.get("namespace") == "platform-system"
        and item.get("subject") == "lab:platform-admin"
        and item.get("resource") == "productplans"
        and item.get("resourceName") == plan_name
    ]
    loaded_matching = [
        item for item in loaded
        if item.get("namespace") == namespace
        and item.get("subject") == "lab:tenant-c-admin"
        and item.get("resource") in (
            "virtualmachineclaims",
            "kubernetesclusterclaims",
            "volumes",
            "networks",
            "firewallrules",
            "accessgrants",
            "subscriptions",
            "orders",
        )
    ]
    return loaded, loaded_project_matching, loaded_plan_matching, loaded_matching

def has_rate_limited_vm_mismatch(items):
    return any(
        item.get("resource") == "virtualmachineclaims"
        and item.get("resourceName") == "portal-project-mismatch-vm"
        and item.get("outcome") == "RateLimited"
        and int(item.get("statusCode", 0)) == 429
        for item in items
    )

audits, project_matching, plan_matching, matching = load_audit_sets()
for _ in range(30):
    if has_rate_limited_vm_mismatch(matching):
        break
    time.sleep(2)
    audits, project_matching, plan_matching, matching = load_audit_sets()
def has_audit(resource, resource_name, action, outcome, status):
    return any(
        item.get("action") == action
        and item.get("resource") == resource
        and item.get("resourceName") == resource_name
        and item.get("outcome") == outcome
        and int(item.get("statusCode", 0)) == status
        for item in matching
    )

assert any(
    item.get("action") == "create"
    and item.get("outcome") == "Allowed"
    and int(item.get("statusCode", 0)) == 201
    for item in project_matching
), audits
assert any(
    item.get("action") == "create"
    and item.get("outcome") == "Allowed"
    and int(item.get("statusCode", 0)) == 201
    for item in plan_matching
), audits
assert any(
    item.get("action") == "delete"
    and item.get("outcome") == "Allowed"
    and int(item.get("statusCode", 0)) == 200
    for item in plan_matching
), audits
assert any(
    item.get("action") == "delete"
    and item.get("outcome") == "Allowed"
    and int(item.get("statusCode", 0)) == 200
    for item in project_matching
), audits
assert any(
    item.get("action") == "create"
    and item.get("resource") == "virtualmachineclaims"
    and item.get("resourceName") == vm_name
    and item.get("outcome") == "Allowed"
    and int(item.get("statusCode", 0)) == 201
    for item in matching
), audits
assert any(
    item.get("action") == "delete"
    and item.get("resource") == "virtualmachineclaims"
    and item.get("resourceName") == vm_name
    and item.get("outcome") == "Allowed"
    and int(item.get("statusCode", 0)) == 200
    for item in matching
), audits
assert any(
    item.get("resource") == "virtualmachineclaims"
    and item.get("resourceName") == "portal-project-mismatch-vm"
    and item.get("outcome") == "RateLimited"
    and int(item.get("statusCode", 0)) == 429
    for item in matching
), audits
assert has_audit("volumes", volume_name, "create", "Allowed", 201), audits
assert has_audit("volumes", volume_name, "delete", "Allowed", 200), audits
assert has_audit("networks", network_name, "create", "Allowed", 201), audits
assert has_audit("networks", network_name, "delete", "Allowed", 200), audits
assert has_audit("firewallrules", firewall_name, "create", "Allowed", 201), audits
assert has_audit("firewallrules", firewall_name, "delete", "Allowed", 200), audits
assert has_audit("accessgrants", access_name, "create", "Allowed", 201), audits
assert has_audit("accessgrants", access_name, "delete", "Allowed", 200), audits
assert has_audit("subscriptions", subscription_name, "create", "Allowed", 201), audits
assert has_audit("subscriptions", subscription_name, "delete", "Allowed", 200), audits
assert has_audit("orders", order_name, "create", "Allowed", 201), audits
assert has_audit("orders", order_name, "delete", "Allowed", 200), audits
assert has_audit("orders", scheduled_order_name, "create", "Allowed", 201), audits
assert has_audit("orders", scheduled_order_name, "delete", "Allowed", 200), audits
assert has_audit("orders", suspend_order_name, "create", "Allowed", 201), audits
assert has_audit("orders", suspend_order_name, "delete", "Allowed", 200), audits
assert has_audit("orders", resume_order_name, "create", "Allowed", 201), audits
assert has_audit("orders", resume_order_name, "delete", "Allowed", 200), audits
assert has_audit("orders", renew_order_name, "create", "Allowed", 201), audits
assert has_audit("orders", renew_order_name, "delete", "Allowed", 200), audits
assert has_audit("orders", cancel_order_name, "create", "Allowed", 201), audits
assert has_audit("orders", cancel_order_name, "delete", "Allowed", 200), audits
assert has_audit("subscriptions", order_subscription_name, "delete", "Allowed", 200), audits
assert 'method="POST",resource="virtualmachineclaims",status="401"' in metrics
assert 'method="POST",resource="virtualmachineclaims",status="403"' in metrics
assert 'method="POST",resource="virtualmachineclaims",status="201"' in metrics
assert 'method="POST",resource="virtualmachineclaims",status="429"' in metrics
assert 'method="DELETE",resource="virtualmachineclaims",status="200"' in metrics
assert 'method="POST",resource="projects",status="403"' in metrics
assert 'method="POST",resource="projects",status="201"' in metrics
assert 'method="DELETE",resource="projects",status="200"' in metrics
assert 'method="POST",resource="productplans",status="403"' in metrics
assert 'method="POST",resource="productplans",status="201"' in metrics
assert 'method="DELETE",resource="productplans",status="200"' in metrics
assert 'method="POST",resource="subscriptions",status="201"' in metrics
assert 'method="DELETE",resource="subscriptions",status="200"' in metrics
assert 'method="POST",resource="orders",status="201"' in metrics
assert 'method="DELETE",resource="orders",status="200"' in metrics
assert 'method="POST",resource="volumes",status="201"' in metrics
assert 'method="DELETE",resource="volumes",status="200"' in metrics
assert 'method="POST",resource="networks",status="201"' in metrics
assert 'method="DELETE",resource="networks",status="200"' in metrics
assert 'method="POST",resource="firewallrules",status="201"' in metrics
assert 'method="DELETE",resource="firewallrules",status="200"' in metrics
assert 'method="POST",resource="accessgrants",status="201"' in metrics
assert 'method="DELETE",resource="accessgrants",status="200"' in metrics
time.sleep(11)
print(f"oidc-jwks RS256/shared-rate-limit/audit smoke rejected unauth/HS256/tampered/cross-tenant/noisy calls, created/deleted admin Project {project_name}, ProductPlan {plan_name}, tenant Subscription {subscription_name}, tenant Orders {order_name}/{scheduled_order_name}/{suspend_order_name}/{resume_order_name}/{renew_order_name}/{cancel_order_name}, and VM, KCC, volume, network, firewall, and access resources in {namespace} across {len(portal_urls)} portal pods", flush=True)
PY
wait_cluster_absent projects.platform.privatecloud.local "${WRITE_PROJECT}" "portal smoke project"
wait_cluster_absent productplans.platform.privatecloud.local "${WRITE_PLAN}" "portal smoke product plan"
wait_absent subscriptions.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_SUBSCRIPTION}" "portal smoke subscription"
wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_CANCEL_ORDER}" "portal smoke cancel order"
wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_RENEW_ORDER}" "portal smoke renew order"
wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_RESUME_ORDER}" "portal smoke resume order"
wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_SUSPEND_ORDER}" "portal smoke suspend order"
wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_SCHEDULED_ORDER}" "portal smoke scheduled order"
wait_absent orders.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_ORDER}" "portal smoke order"
wait_absent subscriptions.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_ORDER_SUBSCRIPTION}" "portal smoke order subscription"
wait_absent virtualmachineclaim "${WRITE_NAMESPACE}" "${WRITE_VM_CLAIM}" "portal smoke VM claim"
wait_absent kubernetesclusterclaim "${WRITE_NAMESPACE}" "${WRITE_KCC_CLAIM}" "portal smoke Kubernetes claim"
wait_absent volumes.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_VOLUME}" "portal smoke volume"
wait_absent networks.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_NETWORK}" "portal smoke network"
wait_absent firewallrules.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_FIREWALL_RULE}" "portal smoke firewall rule"
wait_absent accessgrants.platform.privatecloud.local "${WRITE_NAMESPACE}" "${WRITE_ACCESS_GRANT}" "portal smoke access grant"

echo "provider-portal endpoint=http://${endpoint}/"
