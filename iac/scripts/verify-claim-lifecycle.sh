#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-a}"
ADMITTED_TENANT_NAMESPACE="${ADMITTED_TENANT_NAMESPACE:-tenant-c}"
VM_CLAIM="${VM_CLAIM:-lifecycle-vm}"
KCC_CLAIM="${KCC_CLAIM:-lifecycle-ha-rejected}"
ADMITTED_KCC_CLAIM="${ADMITTED_KCC_CLAIM:-lifecycle-admitted-cluster}"
FINALIZER="platform.privatecloud.local/finalizer"
original_admitted_project_quotas=""

cleanup() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim "${VM_CLAIM}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm "claim-${VM_CLAIM}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation "vmc-${TENANT_NAMESPACE}-${VM_CLAIM}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubernetesclusterclaim "${KCC_CLAIM}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation "kcc-${TENANT_NAMESPACE}-${KCC_CLAIM}" --ignore-not-found >/dev/null 2>&1 || true
  cleanup_admitted_kcc >/dev/null 2>&1 || true
  restore_admitted_project_quota >/dev/null 2>&1 || true
}
trap cleanup EXIT

restore_admitted_project_quota() {
  if [[ -n "${original_admitted_project_quotas}" ]]; then
    ${KUBECTL} patch project "${ADMITTED_TENANT_NAMESPACE}" --type merge \
      -p "{\"spec\":{\"quotas\":${original_admitted_project_quotas}}}" >/dev/null
  fi
}

cleanup_admitted_kcc() {
  local cluster_name="claim-${ADMITTED_KCC_CLAIM}"
  local proxy_name="${ADMITTED_TENANT_NAMESPACE}-${cluster_name}-api"
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete kubernetesclusterclaim "${ADMITTED_KCC_CLAIM}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete machinedeployment "${cluster_name}-default" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete kubeadmconfigtemplate "${cluster_name}-default" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete kubevirtmachinetemplate "${cluster_name}-default" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete kubeadmcontrolplane "${cluster_name}-control-plane" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete kubevirtmachinetemplate "${cluster_name}-control-plane" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete kubevirtcluster "${cluster_name}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete cluster "${cluster_name}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete svc "${cluster_name}-lb" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete networkpolicy "allow-capi-${cluster_name}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n capk-system delete deploy "${proxy_name}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n capk-system delete pdb "${proxy_name}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n capk-system delete svc "${proxy_name}" --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation "kcc-${ADMITTED_TENANT_NAMESPACE}-${ADMITTED_KCC_CLAIM}" --ignore-not-found >/dev/null 2>&1 || true
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

wait_exists() {
  local description="$1"
  shift
  for _ in $(seq 1 60); do
    if "$@" >/dev/null 2>&1; then
      echo "${description} exists"
      return
    fi
    sleep 2
  done
  echo "expected ${description} to exist" >&2
  "$@" || true
  exit 1
}

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

cleanup

original_admitted_project_quotas="$(
  ${KUBECTL} get project "${ADMITTED_TENANT_NAMESPACE}" -o json | python3 -c '
import json
import sys
print(json.dumps(json.load(sys.stdin)["spec"]["quotas"], separators=(",", ":")))
'
)"

echo "== VM claim finalizer and cleanup =="
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: ${VM_CLAIM}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-a
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
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${VM_CLAIM}"
wait_jsonpath "${FINALIZER}" '{.metadata.finalizers[0]}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${VM_CLAIM}"
${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "claim-${VM_CLAIM}" >/dev/null
${KUBECTL} get capacityreservation "vmc-${TENANT_NAMESPACE}-${VM_CLAIM}" >/dev/null

${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim "${VM_CLAIM}" --wait=false
wait_absent "VirtualMachineClaim ${TENANT_NAMESPACE}/${VM_CLAIM}" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim "${VM_CLAIM}"
wait_absent "VM ${TENANT_NAMESPACE}/claim-${VM_CLAIM}" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "claim-${VM_CLAIM}"
wait_absent "CapacityReservation vmc-${TENANT_NAMESPACE}-${VM_CLAIM}" \
  ${KUBECTL} get capacityreservation "vmc-${TENANT_NAMESPACE}-${VM_CLAIM}"

echo "== rejected KubernetesClusterClaim finalizer and cleanup =="
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: KubernetesClusterClaim
metadata:
  name: ${KCC_CLAIM}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-a
  version: v1.32.1
  distribution: kubeadm
  controlPlane:
    replicas: 3
    class: tiny
  workers:
    - name: default
      replicas: 0
      class: tiny
  placement:
    capacityCell: lab-hyperv
    serviceClass: ha-tenant-kubernetes
  network:
    podCIDR: 10.249.0.0/16
    serviceCIDR: 10.97.0.0/16
    cni: cilium
YAML

wait_jsonpath "Rejected" '{.status.admission.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${KCC_CLAIM}"
wait_jsonpath "${FINALIZER}" '{.metadata.finalizers[0]}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${KCC_CLAIM}"
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster "claim-${KCC_CLAIM}" >/dev/null 2>&1; then
  echo "rejected KCC unexpectedly created backing Cluster API object" >&2
  exit 1
fi
if ${KUBECTL} get capacityreservation "kcc-${TENANT_NAMESPACE}-${KCC_CLAIM}" >/dev/null 2>&1; then
  echo "rejected KCC unexpectedly created a capacity reservation" >&2
  exit 1
fi

${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubernetesclusterclaim "${KCC_CLAIM}" --wait=false
wait_absent "KubernetesClusterClaim ${TENANT_NAMESPACE}/${KCC_CLAIM}" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${KCC_CLAIM}"
wait_absent "CapacityReservation kcc-${TENANT_NAMESPACE}-${KCC_CLAIM}" \
  ${KUBECTL} get capacityreservation "kcc-${TENANT_NAMESPACE}-${KCC_CLAIM}"

echo "== admitted KubernetesClusterClaim finalizer and cleanup =="
cleanup_admitted_kcc
${KUBECTL} patch project "${ADMITTED_TENANT_NAMESPACE}" --type merge -p '{"spec":{"quotas":{"cpu":"4","memory":"5Gi","tenantClusters":1,"vms":5,"volumes":4}}}' >/dev/null
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: KubernetesClusterClaim
metadata:
  name: ${ADMITTED_KCC_CLAIM}
  namespace: ${ADMITTED_TENANT_NAMESPACE}
spec:
  projectRef: ${ADMITTED_TENANT_NAMESPACE}
  version: v1.32.1
  distribution: kubeadm
  controlPlane:
    replicas: 1
    class: tiny
  workers:
    - name: default
      replicas: 0
      class: tiny
  placement:
    capacityCell: lab-hyperv
    serviceClass: tiny-tenant-kubernetes
  network:
    podCIDR: 10.250.0.0/16
    serviceCIDR: 10.100.0.0/16
    cni: cilium
YAML

wait_jsonpath "Admitted" '{.status.admission.phase}' \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get kubernetesclusterclaim "${ADMITTED_KCC_CLAIM}"
wait_jsonpath "${FINALIZER}" '{.metadata.finalizers[0]}' \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get kubernetesclusterclaim "${ADMITTED_KCC_CLAIM}"
wait_exists "CapacityReservation kcc-${ADMITTED_TENANT_NAMESPACE}-${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} get capacityreservation "kcc-${ADMITTED_TENANT_NAMESPACE}-${ADMITTED_KCC_CLAIM}"
wait_exists "CAPI Cluster ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get cluster "claim-${ADMITTED_KCC_CLAIM}"
wait_exists "KubeVirtCluster ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get kubevirtcluster "claim-${ADMITTED_KCC_CLAIM}"
wait_exists "KubeadmControlPlane ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}-control-plane" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get kubeadmcontrolplane "claim-${ADMITTED_KCC_CLAIM}-control-plane"
wait_exists "internal Service ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}-lb" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get svc "claim-${ADMITTED_KCC_CLAIM}-lb"
wait_exists "gateway Deployment capk-system/${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api" \
  ${KUBECTL} -n capk-system get deploy "${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api"
wait_exists "gateway PDB capk-system/${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api" \
  ${KUBECTL} -n capk-system get pdb "${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api"
wait_exists "gateway Service capk-system/${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api" \
  ${KUBECTL} -n capk-system get svc "${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api"

${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" delete kubernetesclusterclaim "${ADMITTED_KCC_CLAIM}" --wait=false
wait_absent "KubernetesClusterClaim ${ADMITTED_TENANT_NAMESPACE}/${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get kubernetesclusterclaim "${ADMITTED_KCC_CLAIM}"
wait_absent "CAPI Cluster ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get cluster "claim-${ADMITTED_KCC_CLAIM}"
wait_absent "KubeVirtCluster ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get kubevirtcluster "claim-${ADMITTED_KCC_CLAIM}"
wait_absent "KubeadmControlPlane ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}-control-plane" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get kubeadmcontrolplane "claim-${ADMITTED_KCC_CLAIM}-control-plane"
wait_absent "internal Service ${ADMITTED_TENANT_NAMESPACE}/claim-${ADMITTED_KCC_CLAIM}-lb" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get svc "claim-${ADMITTED_KCC_CLAIM}-lb"
wait_absent "gateway Deployment capk-system/${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api" \
  ${KUBECTL} -n capk-system get deploy "${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api"
wait_absent "gateway PDB capk-system/${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api" \
  ${KUBECTL} -n capk-system get pdb "${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api"
wait_absent "gateway Service capk-system/${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api" \
  ${KUBECTL} -n capk-system get svc "${ADMITTED_TENANT_NAMESPACE}-claim-${ADMITTED_KCC_CLAIM}-api"
wait_absent "NetworkPolicy ${ADMITTED_TENANT_NAMESPACE}/allow-capi-claim-${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} -n "${ADMITTED_TENANT_NAMESPACE}" get networkpolicy "allow-capi-claim-${ADMITTED_KCC_CLAIM}"
wait_absent "CapacityReservation kcc-${ADMITTED_TENANT_NAMESPACE}-${ADMITTED_KCC_CLAIM}" \
  ${KUBECTL} get capacityreservation "kcc-${ADMITTED_TENANT_NAMESPACE}-${ADMITTED_KCC_CLAIM}"
restore_admitted_project_quota

echo "claim lifecycle finalizer cleanup passed"
