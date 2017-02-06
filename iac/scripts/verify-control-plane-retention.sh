#!/usr/bin/env bash
set -euo pipefail

KUBECTL_BASE="${KUBECTL:-sudo k3s kubectl}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-15s}"
KUBECTL="${KUBECTL_BASE} --request-timeout=${REQUEST_TIMEOUT}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-a}"
OLD_TS="${OLD_TS:-2000-01-01T00:00:00Z}"
NOW_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

OLD_JOURNAL="retention-old-admission-journal"
FRESH_JOURNAL="retention-fresh-admission-journal"
OLD_AUDIT="retention-old-audit-event"
FRESH_AUDIT="retention-fresh-audit-event"

cleanup() {
  ${KUBECTL} delete admissionjournal "${OLD_JOURNAL}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete admissionjournal "${FRESH_JOURNAL}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete selfserviceauditevent "${OLD_AUDIT}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete selfserviceauditevent "${FRESH_AUDIT}" --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

echo "== create synthetic old/fresh retention records =="
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: AdmissionJournal
metadata:
  name: ${OLD_JOURNAL}
  labels:
    platform.privatecloud.local/retention-probe: "true"
spec:
  claimRef:
    apiGroup: platform.privatecloud.local
    kind: VirtualMachineClaim
    namespace: ${TENANT_NAMESPACE}
    name: retention-old
    uid: retention-old
    generation: 1
  projectRef: ${TENANT_NAMESPACE}
  decision: Rejected
  reason: RetentionProbe
  message: synthetic old admission journal retention probe
  capacityCell: lab-hyperv
  serviceClass: tiny-vm
  resources:
    cpu: "1"
    memory: 256Mi
  quotaSnapshot:
    cpu: 0m
    memory: 0Mi
    vms: 0
    tenantClusters: 0
  locks: {}
  controller:
    identity: retention-probe
    shardIndex: 0
    shardTotal: 1
    ownsGlobal: true
  observedAt: ${OLD_TS}
---
apiVersion: platform.privatecloud.local/v1alpha1
kind: AdmissionJournal
metadata:
  name: ${FRESH_JOURNAL}
  labels:
    platform.privatecloud.local/retention-probe: "true"
spec:
  claimRef:
    apiGroup: platform.privatecloud.local
    kind: VirtualMachineClaim
    namespace: ${TENANT_NAMESPACE}
    name: retention-fresh
    uid: retention-fresh
    generation: 1
  projectRef: ${TENANT_NAMESPACE}
  decision: Rejected
  reason: RetentionProbe
  message: synthetic fresh admission journal retention probe
  capacityCell: lab-hyperv
  serviceClass: tiny-vm
  resources:
    cpu: "1"
    memory: 256Mi
  quotaSnapshot:
    cpu: 0m
    memory: 0Mi
    vms: 0
    tenantClusters: 0
  locks: {}
  controller:
    identity: retention-probe
    shardIndex: 0
    shardTotal: 1
    ownsGlobal: true
  observedAt: ${NOW_TS}
---
apiVersion: platform.privatecloud.local/v1alpha1
kind: SelfServiceAuditEvent
metadata:
  name: ${OLD_AUDIT}
  namespace: ${TENANT_NAMESPACE}
  labels:
    platform.privatecloud.local/retention-probe: "true"
spec:
  projectRef: ${TENANT_NAMESPACE}
  subject: retention-probe
  subjectHash: retention-probe
  groups:
    - platform:${TENANT_NAMESPACE}:admins
  action: create
  resource: virtualmachineclaims
  resourceName: retention-old
  outcome: Allowed
  statusCode: 201
  message: synthetic old audit retention probe
  source: retention-probe
  requestPath: /retention-probe
  timestamp: ${OLD_TS}
---
apiVersion: platform.privatecloud.local/v1alpha1
kind: SelfServiceAuditEvent
metadata:
  name: ${FRESH_AUDIT}
  namespace: ${TENANT_NAMESPACE}
  labels:
    platform.privatecloud.local/retention-probe: "true"
spec:
  projectRef: ${TENANT_NAMESPACE}
  subject: retention-probe
  subjectHash: retention-probe
  groups:
    - platform:${TENANT_NAMESPACE}:admins
  action: create
  resource: virtualmachineclaims
  resourceName: retention-fresh
  outcome: Allowed
  statusCode: 201
  message: synthetic fresh audit retention probe
  source: retention-probe
  requestPath: /retention-probe
  timestamp: ${NOW_TS}
YAML

echo "== wait for global-shard retention reaper =="
for _ in $(seq 1 18); do
  old_journal="$(${KUBECTL} get admissionjournal "${OLD_JOURNAL}" -o name 2>/dev/null || true)"
  old_audit="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get selfserviceauditevent "${OLD_AUDIT}" -o name 2>/dev/null || true)"
  fresh_journal="$(${KUBECTL} get admissionjournal "${FRESH_JOURNAL}" -o name 2>/dev/null || true)"
  fresh_audit="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get selfserviceauditevent "${FRESH_AUDIT}" -o name 2>/dev/null || true)"
  if [[ -z "${old_journal}" && -z "${old_audit}" && -n "${fresh_journal}" && -n "${fresh_audit}" ]]; then
    echo "retention reaper deleted old records and preserved fresh records"
    break
  fi
  sleep 10
done

[[ -z "$(${KUBECTL} get admissionjournal "${OLD_JOURNAL}" -o name 2>/dev/null || true)" ]] || {
  echo "expected old AdmissionJournal ${OLD_JOURNAL} to be deleted" >&2
  exit 1
}
[[ -z "$(${KUBECTL} -n "${TENANT_NAMESPACE}" get selfserviceauditevent "${OLD_AUDIT}" -o name 2>/dev/null || true)" ]] || {
  echo "expected old SelfServiceAuditEvent ${OLD_AUDIT} to be deleted" >&2
  exit 1
}
${KUBECTL} get admissionjournal "${FRESH_JOURNAL}" >/dev/null
${KUBECTL} -n "${TENANT_NAMESPACE}" get selfserviceauditevent "${FRESH_AUDIT}" >/dev/null

echo "== retention metrics =="
metrics_found=0
for metrics_pod in $(${KUBECTL} -n platform-system get pod -l 'app.kubernetes.io/name=provider-controller,platform.privatecloud.local/controller-shard=0' -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'); do
  metrics="$(${KUBECTL} -n platform-system exec "${metrics_pod}" -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/metrics", timeout=5).read().decode())' 2>/dev/null || true)"
  if grep -q 'provider_controller_retention_deleted_total{resource="admissionjournals"}' <<<"${metrics}" \
    && grep -q 'provider_controller_retention_deleted_total{resource="selfserviceauditevents"}' <<<"${metrics}"; then
    metrics_found=1
    break
  fi
done
[[ "${metrics_found}" == "1" ]] || {
  echo "expected retention deletion metrics on one shard-0 controller pod" >&2
  exit 1
}
echo "retention metrics present"

cleanup
echo "control-plane retention verification passed"
