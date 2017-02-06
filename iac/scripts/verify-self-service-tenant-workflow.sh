#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-c}"
TENANT_GROUP="${TENANT_GROUP:-platform:tenant-c:admins}"
TENANT_USER="${TENANT_USER:-alice}"
CLAIM_NAME="${CLAIM_NAME:-self-service-vm}"
FINALIZER="platform.privatecloud.local/finalizer"

tenant_kubectl() {
  ${KUBECTL} --as="${TENANT_USER}" --as-group="${TENANT_GROUP}" --as-group=platform:tenants "$@"
}

cleanup() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim "${CLAIM_NAME}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm "claim-${CLAIM_NAME}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation "vmc-${TENANT_NAMESPACE}-${CLAIM_NAME}" --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup EXIT

wait_jsonpath() {
  local expected="$1"
  local jsonpath="$2"
  shift 2
  local value=""
  for _ in $(seq 1 60); do
    value="$("$@" -o "jsonpath=${jsonpath}" 2>/dev/null || true)"
    [[ "${value}" == "${expected}" ]] && return
    sleep 2
  done
  echo "expected jsonpath ${jsonpath} to become ${expected}, got ${value:-<empty>}" >&2
  "$@" -o yaml || true
  exit 1
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

echo "== ensure tenant-c project exists =="
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: Project
metadata:
  name: tenant-c
spec:
  tenantId: tenant-c
  displayName: Tenant C
  tier: shared
  adminsGroup: platform:tenant-c:admins
  quotas:
    cpu: "2"
    memory: 2Gi
    tenantClusters: 1
    vms: 5
    volumes: 4
  network:
    defaultDeny: true
    allowInternetEgress: false
    allowedLoadBalancers: 0
YAML

for _ in $(seq 1 60); do
  ${KUBECTL} get ns "${TENANT_NAMESPACE}" >/dev/null 2>&1 && break
  sleep 2
done
${KUBECTL} get ns "${TENANT_NAMESPACE}" >/dev/null
wait_jsonpath "Ready" '{.status.phase}' ${KUBECTL} get project tenant-c
${KUBECTL} -n "${TENANT_NAMESPACE}" get rolebinding tenant-self-service >/dev/null

echo "== tenant RBAC =="
[[ "$(tenant_kubectl auth can-i create virtualmachineclaims -n "${TENANT_NAMESPACE}")" == "yes" ]] || {
  echo "expected tenant admin to create VirtualMachineClaim in ${TENANT_NAMESPACE}" >&2
  exit 1
}
[[ "$(tenant_kubectl auth can-i delete virtualmachineclaims -n "${TENANT_NAMESPACE}")" == "yes" ]] || {
  echo "expected tenant admin to delete VirtualMachineClaim in ${TENANT_NAMESPACE}" >&2
  exit 1
}
[[ "$(tenant_kubectl auth can-i create virtualmachineclaims -n tenant-a)" == "no" ]] || {
  echo "expected tenant-c admin to be denied in tenant-a" >&2
  exit 1
}
[[ "$(tenant_kubectl auth can-i get capacityreservations)" == "no" ]] || {
  echo "expected tenant admin to be denied provider-internal CapacityReservations" >&2
  exit 1
}

cleanup

echo "== tenant self-service VM claim create/delete =="
cat <<YAML | tenant_kubectl apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: ${CLAIM_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-c
  class: tiny
  image:
    name: cirros
    source: catalog
  resources:
    cpu: 1
    memory: 256Mi
    rootDisk: 1Gi
  placement:
    capacityCell: lab-hyperv
    serviceClass: tiny-vm
  availability:
    runStrategy: Halted
YAML

wait_jsonpath "Admitted" '{.status.admission.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
wait_jsonpath "${FINALIZER}" '{.metadata.finalizers[0]}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
wait_jsonpath "claim-${CLAIM_NAME}" '{.status.vmName}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "claim-${CLAIM_NAME}" >/dev/null
${KUBECTL} get capacityreservation "vmc-${TENANT_NAMESPACE}-${CLAIM_NAME}" >/dev/null

tenant_kubectl -n "${TENANT_NAMESPACE}" delete virtualmachineclaim "${CLAIM_NAME}" --wait=false
wait_absent "VirtualMachineClaim ${TENANT_NAMESPACE}/${CLAIM_NAME}" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${CLAIM_NAME}"
wait_absent "VM ${TENANT_NAMESPACE}/claim-${CLAIM_NAME}" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "claim-${CLAIM_NAME}"
wait_absent "CapacityReservation vmc-${TENANT_NAMESPACE}-${CLAIM_NAME}" \
  ${KUBECTL} get capacityreservation "vmc-${TENANT_NAMESPACE}-${CLAIM_NAME}"

echo "self-service tenant workflow passed"
