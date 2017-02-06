#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
PROBE_NAMESPACE="${PROBE_NAMESPACE:-platform-system}"
PROBE_SELECTOR="${PROBE_SELECTOR:-app=provider-controller}"
REQUIRE_DIAGNOSTIC_ENDPOINTS="${REQUIRE_DIAGNOSTIC_ENDPOINTS:-false}"
DEFAULT_TENANT_CLUSTER_CLAIMS="${DEFAULT_TENANT_CLUSTER_CLAIMS:-tenant-a/routable-cluster}"

if [[ "$#" -ge 2 ]]; then
  tenant_namespace="$1"
  claim_name="$2"
  claim_endpoint="$(
    ${KUBECTL} -n "${tenant_namespace}" get kubernetesclusterclaim "${claim_name}" \
      -o jsonpath='{.status.apiEndpoint}' 2>/dev/null || true
  )"
  [[ -n "${claim_endpoint}" ]] || {
    echo "KubernetesClusterClaim ${tenant_namespace}/${claim_name} has no status.apiEndpoint" >&2
    exit 1
  }
  ROUTED_ENDPOINTS="${ROUTED_ENDPOINTS:-${claim_endpoint}}"
  DIAGNOSTIC_ENDPOINTS="${DIAGNOSTIC_ENDPOINTS:-claim-${claim_name}-lb.${tenant_namespace}.svc.cluster.local:6443}"
else
  routed_endpoints=()
  diagnostic_endpoints=()
  for claim_ref in ${DEFAULT_TENANT_CLUSTER_CLAIMS}; do
    tenant_namespace="${claim_ref%%/*}"
    claim_name="${claim_ref##*/}"
    if [[ -z "${tenant_namespace}" || "${tenant_namespace}" == "${claim_ref}" || -z "${claim_name}" ]]; then
      echo "invalid tenant cluster claim reference ${claim_ref}; expected namespace/name" >&2
      exit 1
    fi
    claim_endpoint="$(
      ${KUBECTL} -n "${tenant_namespace}" get kubernetesclusterclaim "${claim_name}" \
        -o jsonpath='{.status.apiEndpoint}' 2>/dev/null || true
    )"
    [[ -n "${claim_endpoint}" ]] || {
      echo "KubernetesClusterClaim ${tenant_namespace}/${claim_name} has no status.apiEndpoint" >&2
      exit 1
    }
    routed_endpoints+=("${claim_endpoint}")
    diagnostic_endpoints+=("claim-${claim_name}-lb.${tenant_namespace}.svc.cluster.local:6443")
  done
  ROUTED_ENDPOINTS="${ROUTED_ENDPOINTS:-${routed_endpoints[*]}}"
  DIAGNOSTIC_ENDPOINTS="${DIAGNOSTIC_ENDPOINTS:-${diagnostic_endpoints[*]}}"
fi

pods="$(
  ${KUBECTL} -n "${PROBE_NAMESPACE}" get pods -l "${PROBE_SELECTOR}" \
    --field-selector=status.phase=Running \
    -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
)"

[[ -n "${pods}" ]] || {
  echo "no running probe pods found in ${PROBE_NAMESPACE} with selector ${PROBE_SELECTOR}" >&2
  exit 1
}

probe_endpoint() {
  local pod="$1"
  local endpoint="$2"
  local output
  set +e
  output="$(${KUBECTL} -n "${PROBE_NAMESPACE}" exec -i "${pod}" -- python - "${endpoint}" 2>&1 <<'PY'
import socket
import ssl
import sys

endpoint = sys.argv[1]
host, _, port_text = endpoint.partition(":")
port = int(port_text or "6443")
try:
    raw_sock = socket.create_connection((host, port), timeout=4)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with context.wrap_socket(raw_sock, server_hostname=host) as tls_sock:
        tls_sock.settimeout(4)
        request = f"GET /readyz HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        tls_sock.sendall(request.encode("ascii"))
        chunks = []
        while True:
            chunk = tls_sock.recv(1024)
            if not chunk:
                break
            chunks.append(chunk)
            if sum(len(item) for item in chunks) >= 4096:
                break
    response = b"".join(chunks)
    headers, _, body = response.partition(b"\r\n\r\n")
    status_line = headers.splitlines()[0].decode("latin1") if headers else ""
    ok = status_line.startswith(("HTTP/1.0 200", "HTTP/1.1 200")) and b"ok" in body.lower()
    print(f"{'OK' if ok else 'FAIL'} {status_line}")
    sys.exit(0 if ok else 2)
except Exception as exc:
    print(f"FAIL {type(exc).__name__}: {exc}")
    sys.exit(2)
PY
)"
  local rc="$?"
  set -e
  sed '/^command terminated with exit code /d' <<< "${output}"
  [[ "${rc}" -eq 0 ]]
}

failures=0
for pod in ${pods}; do
  node="$(${KUBECTL} -n "${PROBE_NAMESPACE}" get pod "${pod}" -o jsonpath='{.spec.nodeName}')"
  echo "== ${PROBE_NAMESPACE}/${pod} on ${node} =="
  for endpoint in ${ROUTED_ENDPOINTS}; do
    printf 'routed %s ' "${endpoint}"
    if ! probe_endpoint "${pod}" "${endpoint}"; then
      failures=$((failures + 1))
    fi
  done
  for endpoint in ${DIAGNOSTIC_ENDPOINTS}; do
    printf 'diagnostic%s %s ' "$([[ "${REQUIRE_DIAGNOSTIC_ENDPOINTS}" == "true" ]] || printf '(optional)')" "${endpoint}"
    if ! probe_endpoint "${pod}" "${endpoint}"; then
      if [[ "${REQUIRE_DIAGNOSTIC_ENDPOINTS}" == "true" ]]; then
        failures=$((failures + 1))
      fi
    fi
  done
done

exit "${failures}"
