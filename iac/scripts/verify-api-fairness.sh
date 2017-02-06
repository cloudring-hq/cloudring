#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-c}"
TENANT_USER="${TENANT_USER:-noisy-tenant}"
TENANT_GROUP="${TENANT_GROUP:-platform:tenant-c:admins}"
CATALOG_GROUP="${CATALOG_GROUP:-platform:tenants}"
BURST_REQUESTS="${BURST_REQUESTS:-5}"
PLATFORM_PROBES="${PLATFORM_PROBES:-10}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-10s}"

tenant_kubectl() {
  ${KUBECTL} \
    --request-timeout="${REQUEST_TIMEOUT}" \
    --as="${TENANT_USER}" \
    --as-group="${TENANT_GROUP}" \
    --as-group="${CATALOG_GROUP}" \
    "$@"
}

tenant_can_i() {
  tenant_kubectl auth can-i "$@" 2>/dev/null || true
}

json_get() {
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" get "$1" "$2" -o json
}

expect_priority_level() {
  local name="$1"
  local shares="$2"
  local queue_limit="$3"
  json_get prioritylevelconfiguration "${name}" | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
name, shares, queue_limit = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
limited = payload.get("spec", {}).get("limited", {})
queuing = limited.get("limitResponse", {}).get("queuing", {})
actual_shares = limited.get("nominalConcurrencyShares")
actual_queue_limit = queuing.get("queueLengthLimit")
assert payload.get("spec", {}).get("type") == "Limited", f"{name} must be Limited"
assert actual_shares == shares, f"{name} shares expected {shares}, got {actual_shares}"
assert actual_queue_limit == queue_limit, (
    f"{name} queueLengthLimit expected {queue_limit}, got {actual_queue_limit}"
)
print(f"{name} shares={shares} queueLengthLimit={queue_limit}")
' "$name" "$shares" "$queue_limit"
}

expect_flow_schema() {
  local name="$1"
  local priority="$2"
  local distinguisher="$3"
  json_get flowschema "${name}" | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
name, priority, distinguisher = sys.argv[1], sys.argv[2], sys.argv[3]
spec = payload.get("spec", {})
actual_priority = spec.get("priorityLevelConfiguration", {}).get("name")
actual_distinguisher = spec.get("distinguisherMethod", {}).get("type")
assert actual_priority == priority, f"{name} priority expected {priority}, got {actual_priority}"
assert actual_distinguisher == distinguisher, (
    f"{name} distinguisher expected {distinguisher}, got {actual_distinguisher}"
)
conditions = payload.get("status", {}).get("conditions", [])
dangling = [
    condition for condition in conditions
    if condition.get("type") == "Dangling" and condition.get("status") == "True"
]
assert not dangling, f"{name} has dangling reference condition"
print(f"{name} priority={priority} distinguisher={distinguisher}")
' "$name" "$priority" "$distinguisher"
}

expect_flow_schema_contains() {
  local name="$1"
  shift
  json_get flowschema "${name}" | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
name = sys.argv[1]
expected = set(sys.argv[2:])
actual = set()
for rule in payload.get("spec", {}).get("rules", []):
    for subject in rule.get("subjects", []):
        kind = subject.get("kind")
        if kind == "Group":
            group = subject.get("group", {}).get("name")
            actual.add(f"group:{group}")
        elif kind == "ServiceAccount":
            sa = subject.get("serviceAccount", {})
            namespace = sa.get("namespace")
            sa_name = sa.get("name")
            actual.add(f"sa:{namespace}/{sa_name}")
missing = sorted(expected - actual)
assert not missing, f"{name} missing subjects: {missing}"
print(f"{name} subjects include {'"'"', '"'"'.join(sorted(expected))}")
' "$name" "$@"
}

echo "== API Priority and Fairness lanes =="
expect_priority_level platform-control 80 100
expect_priority_level tenant-limited 30 50
expect_priority_level tenant-bulk-low 10 25

expect_flow_schema platform-service-accounts platform-control ByUser
expect_flow_schema platform-admins platform-control ByUser
expect_flow_schema tenant-bulk-list-watch tenant-bulk-low ByNamespace
expect_flow_schema tenant-groups tenant-limited ByNamespace

expect_flow_schema_contains platform-service-accounts \
  sa:platform-system/provider-controller \
  sa:platform-system/provider-portal \
  sa:flux-system/source-controller \
  sa:flux-system/kustomize-controller \
  sa:capk-system/capk-controller-manager
expect_flow_schema_contains tenant-bulk-list-watch \
  group:platform:tenants \
  group:platform:tenant-a:admins \
  group:platform:tenant-b:admins \
  group:platform:tenant-c:admins
expect_flow_schema_contains tenant-groups \
  group:platform:tenants \
  group:platform:tenant-a:admins \
  group:platform:tenant-b:admins \
  group:platform:tenant-c:admins

echo "== tenant RBAC still scoped while APF catches noisy users =="
tenant_can_i list virtualmachineclaims.platform.privatecloud.local -n "${TENANT_NAMESPACE}" | grep -qx yes
tenant_can_i list capacityreservations.platform.privatecloud.local --all-namespaces | grep -qx no
tenant_can_i create volumes.platform.privatecloud.local -n tenant-a | grep -qx no

echo "== noisy tenant burst while platform paths remain responsive =="
tenant_resources=(
  virtualmachineclaims.platform.privatecloud.local
  kubernetesclusterclaims.platform.privatecloud.local
  volumes.platform.privatecloud.local
  networks.platform.privatecloud.local
  firewallrules.platform.privatecloud.local
  backupplans.platform.privatecloud.local
  restorerequests.platform.privatecloud.local
  accessgrants.platform.privatecloud.local
)

tenant_burst() {
  for _ in $(seq 1 "${BURST_REQUESTS}"); do
    for resource in "${tenant_resources[@]}"; do
      if ! tenant_kubectl -n "${TENANT_NAMESPACE}" get "${resource}" >/dev/null 2>&1; then
        echo "tenant burst request failed: ${resource}" >&2
        return 1
      fi
    done
  done
}

tenant_burst &
burst_pid="$!"
for _ in $(seq 1 "${PLATFORM_PROBES}"); do
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" get --raw=/readyz >/dev/null
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" -n platform-system get deploy -l app=provider-controller >/dev/null
  ${KUBECTL} --request-timeout="${REQUEST_TIMEOUT}" -n flux-system get kustomization platform-base >/dev/null
done
wait "${burst_pid}"

echo "api fairness verification passed"
