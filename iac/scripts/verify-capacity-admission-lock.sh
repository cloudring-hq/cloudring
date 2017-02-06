#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
LOCK_NAMESPACE="${LOCK_NAMESPACE:-platform-system}"
CAPACITY_CELL="${CAPACITY_CELL:-lab-hyperv}"
LOCK_NAME="${LOCK_NAME:-capacity-admission-${CAPACITY_CELL}}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-c}"
CLAIM_NAME="${CLAIM_NAME:-admission-lock-vm}"
VM_NAME="claim-${CLAIM_NAME}"
RESERVATION_NAME="vmc-${TENANT_NAMESPACE}-${CLAIM_NAME}"
LOCK_HOLDER="verify-capacity-admission-lock"
original_project_quotas=""
original_resource_quota_hard=""

cleanup() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim "${CLAIM_NAME}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm "${VM_NAME}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation "${RESERVATION_NAME}" --ignore-not-found >/dev/null 2>&1 || true
  holder="$(${KUBECTL} -n "${LOCK_NAMESPACE}" get lease "${LOCK_NAME}" -o jsonpath='{.spec.holderIdentity}' 2>/dev/null || true)"
  if [[ "${holder}" == "${LOCK_HOLDER}" ]]; then
    ${KUBECTL} -n "${LOCK_NAMESPACE}" delete lease "${LOCK_NAME}" --ignore-not-found >/dev/null 2>&1 || true
  fi
  restore_quota >/dev/null 2>&1 || true
}
trap cleanup EXIT

restore_quota() {
  if [[ -n "${original_project_quotas}" ]]; then
    ${KUBECTL} patch project "${TENANT_NAMESPACE}" --type merge \
      -p "{\"spec\":{\"quotas\":${original_project_quotas}}}" >/dev/null
  fi
  if [[ -n "${original_resource_quota_hard}" ]]; then
    ${KUBECTL} -n "${TENANT_NAMESPACE}" patch resourcequota tenant-quota --type merge \
      -p "{\"spec\":{\"hard\":${original_resource_quota_hard}}}" >/dev/null
  fi
}

wait_absent() {
  local description="$1"
  shift
  for _ in $(seq 1 60); do
    if ! "$@" >/dev/null 2>&1; then
      echo "${description} absent"
      return
    fi
    sleep 2
  done
  echo "expected ${description} to be absent" >&2
  "$@" || true
  exit 1
}

wait_jsonpath() {
  local expected="$1"
  local jsonpath="$2"
  shift 2
  local value=""
  for _ in $(seq 1 90); do
    value="$("$@" -o "jsonpath=${jsonpath}" 2>/dev/null || true)"
    [[ "${value}" == "${expected}" ]] && return
    sleep 2
  done
  echo "expected jsonpath ${jsonpath} to become ${expected}, got ${value:-<empty>}" >&2
  "$@" -o yaml || true
  exit 1
}

wait_lock_free() {
  for _ in $(seq 1 60); do
    holder="$(${KUBECTL} -n "${LOCK_NAMESPACE}" get lease "${LOCK_NAME}" -o jsonpath='{.spec.holderIdentity}' 2>/dev/null || true)"
    if [[ -z "${holder}" ]]; then
      return
    fi
    if [[ "${holder}" == "${LOCK_HOLDER}" ]]; then
      ${KUBECTL} -n "${LOCK_NAMESPACE}" delete lease "${LOCK_NAME}" --ignore-not-found >/dev/null 2>&1 || true
      return
    fi
    sleep 2
  done
  echo "capacity admission lock ${LOCK_NAMESPACE}/${LOCK_NAME} remained held by ${holder}" >&2
  ${KUBECTL} -n "${LOCK_NAMESPACE}" get lease "${LOCK_NAME}" -o yaml >&2 || true
  exit 1
}

cleanup
wait_lock_free

original_project_quotas="$(
  ${KUBECTL} get project "${TENANT_NAMESPACE}" -o json | python3 -c '
import json
import sys
print(json.dumps(json.load(sys.stdin)["spec"]["quotas"], separators=(",", ":")))
'
)"
original_resource_quota_hard="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get resourcequota tenant-quota -o json | python3 -c '
import json
import sys
print(json.dumps(json.load(sys.stdin)["spec"]["hard"], separators=(",", ":")))
'
)"

${KUBECTL} patch project "${TENANT_NAMESPACE}" --type merge \
  -p '{"spec":{"quotas":{"cpu":"4","memory":"5Gi","tenantClusters":1,"vms":5,"volumes":4}}}' >/dev/null
${KUBECTL} -n "${TENANT_NAMESPACE}" patch resourcequota tenant-quota --type merge \
  -p '{"spec":{"hard":{"requests.cpu":"4","requests.memory":"5Gi","limits.cpu":"4","limits.memory":"5Gi","persistentvolumeclaims":"4","pods":"20"}}}' >/dev/null

now="$(date -u +"%Y-%m-%dT%H:%M:%S.000000Z")"
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: coordination.k8s.io/v1
kind: Lease
metadata:
  name: ${LOCK_NAME}
  namespace: ${LOCK_NAMESPACE}
  labels:
    app: provider-controller
    platform.privatecloud.local/capacity-admission-lock: "true"
    platform.privatecloud.local/capacity-cell: ${CAPACITY_CELL}
spec:
  holderIdentity: ${LOCK_HOLDER}
  leaseDurationSeconds: 120
  acquireTime: "${now}"
  renewTime: "${now}"
  leaseTransitions: 0
YAML

cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: ${CLAIM_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  class: tiny
  image:
    source: catalog
    name: cirros
  resources:
    cpu: 1
    memory: 256Mi
    rootDisk: 1Gi
  placement:
    capacityCell: ${CAPACITY_CELL}
    serviceClass: tiny-vm
YAML

echo "== admission is blocked while synthetic capacity lock is held =="
wait_jsonpath "PendingAdmission" '{.status.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
wait_jsonpath "CapacityAdmissionLocked" '{.status.admission.reason}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "${VM_NAME}" >/dev/null 2>&1; then
  echo "backing VM ${TENANT_NAMESPACE}/${VM_NAME} was created while capacity admission lock was held" >&2
  exit 1
fi
if ${KUBECTL} get capacityreservation "${RESERVATION_NAME}" >/dev/null 2>&1; then
  echo "capacity reservation ${RESERVATION_NAME} was created while capacity admission lock was held" >&2
  exit 1
fi

echo "== admission proceeds after lock release =="
${KUBECTL} -n "${LOCK_NAMESPACE}" delete lease "${LOCK_NAME}"
wait_jsonpath "Admitted" '{.status.admission.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
wait_jsonpath "Ready" '{.status.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "${VM_NAME}"
${KUBECTL} get capacityreservation "${RESERVATION_NAME}"

echo "== cleanup =="
${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim "${CLAIM_NAME}" --wait=false
wait_absent "VirtualMachineClaim ${TENANT_NAMESPACE}/${CLAIM_NAME}" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
wait_absent "VirtualMachine ${TENANT_NAMESPACE}/${VM_NAME}" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "${VM_NAME}"
wait_absent "CapacityReservation ${RESERVATION_NAME}" \
  ${KUBECTL} get capacityreservation "${RESERVATION_NAME}"
restore_quota

echo "capacity admission lock verification passed"
