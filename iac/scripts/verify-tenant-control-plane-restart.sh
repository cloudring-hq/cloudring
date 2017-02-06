#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-a}"
CLUSTER_CLAIM_NAME="${CLUSTER_CLAIM_NAME:-routable-cluster}"
CLUSTER_NAME="${CLUSTER_NAME:-claim-${CLUSTER_CLAIM_NAME}}"
ROUTED_SERVICE_NAMESPACE="${ROUTED_SERVICE_NAMESPACE:-capk-system}"
ROUTED_SERVICE_NAME="${ROUTED_SERVICE_NAME:-${TENANT_NAMESPACE}-${CLUSTER_NAME}-api}"
KUBECONFIG_SECRET="${KUBECONFIG_SECRET:-${CLUSTER_NAME}-kubeconfig}"
CONFIRM_TENANT_CP_RESTART="${CONFIRM_TENANT_CP_RESTART:-false}"
WAIT_SECONDS="${WAIT_SECONDS:-900}"
POLL_SECONDS="${POLL_SECONDS:-5}"
RUN_LAYER_VERIFY="${RUN_LAYER_VERIFY:-true}"
RUN_REACHABILITY_PROBE="${RUN_REACHABILITY_PROBE:-true}"
STALE_POD_NAMESPACES="${STALE_POD_NAMESPACES:-kube-system}"

tenant_kubeconfig=""
cleanup() {
  if [[ -n "${tenant_kubeconfig}" && -f "${tenant_kubeconfig}" ]]; then
    rm -f "${tenant_kubeconfig}"
  fi
}
trap cleanup EXIT

if [[ "${CONFIRM_TENANT_CP_RESTART}" != "true" ]]; then
  cat >&2 <<EOF
Refusing to run destructive tenant control-plane restart drill.
Set CONFIRM_TENANT_CP_RESTART=true to delete and recreate the CAPK control-plane VMI.
EOF
  exit 2
fi

deadline=0
start_deadline() {
  deadline=$(( $(date +%s) + WAIT_SECONDS ))
}

wait_for() {
  local description="$1"
  shift
  start_deadline
  while (( $(date +%s) < deadline )); do
    if "$@" >/dev/null 2>&1; then
      echo "${description}"
      return
    fi
    sleep "${POLL_SECONDS}"
  done
  echo "timed out waiting for ${description}" >&2
  "$@" || true
  exit 1
}

wait_jsonpath() {
  local description="$1"
  local expected="$2"
  local jsonpath="$3"
  shift 3
  local value=""
  start_deadline
  while (( $(date +%s) < deadline )); do
    value="$("$@" -o "jsonpath=${jsonpath}" 2>/dev/null || true)"
    if [[ "${value}" == "${expected}" ]]; then
      echo "${description}: ${value}"
      return
    fi
    sleep "${POLL_SECONDS}"
  done
  echo "timed out waiting for ${description}; expected ${expected}, got ${value:-<empty>}" >&2
  "$@" -o yaml || true
  exit 1
}

wait_readyz() {
  local endpoint="$1"
  start_deadline
  while (( $(date +%s) < deadline )); do
    if curl -k --fail --connect-timeout 5 --max-time 15 -sS "https://${endpoint}/readyz" | grep -qx "ok"; then
      echo "routed /readyz ${endpoint} OK"
      return
    fi
    sleep "${POLL_SECONDS}"
  done
  echo "timed out waiting for routed /readyz ${endpoint}" >&2
  curl -k --connect-timeout 5 --max-time 15 -sS "https://${endpoint}/readyz" || true
  exit 1
}

write_tenant_kubeconfig() {
  local endpoint="$1"
  tenant_kubeconfig="$(mktemp)"
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get secret "${KUBECONFIG_SECRET}" \
    -o jsonpath='{.data.value}' | base64 -d > "${tenant_kubeconfig}"
  sed -i '/certificate-authority-data:/d' "${tenant_kubeconfig}"
  sed -i "s#server: .*#server: https://${endpoint}\\n    insecure-skip-tls-verify: true#" "${tenant_kubeconfig}"
}

tenant_kubectl() {
  ${KUBECTL} --kubeconfig="${tenant_kubeconfig}" "$@"
}

list_stale_tenant_pods() {
  local namespace
  for namespace in ${STALE_POD_NAMESPACES}; do
    tenant_kubectl get pods -n "${namespace}" --no-headers 2>/dev/null \
      | awk '$3 == "Unknown" || $3 == "Failed" || $3 == "Terminating" {print ns " " $1 " " $3}' ns="${namespace}" || true
  done
}

cleanup_stale_tenant_pods() {
  echo "== clean stale tenant pods after hard VMI restart =="
  local stale=""
  for _ in $(seq 1 3); do
    stale="$(list_stale_tenant_pods)"
    if [[ -z "${stale}" ]]; then
      echo "no stale tenant pods in namespaces: ${STALE_POD_NAMESPACES}"
      return
    fi
    echo "${stale}" | while read -r namespace pod status; do
      [[ -n "${namespace}" && -n "${pod}" ]] || continue
      echo "deleting stale ${namespace}/${pod} status=${status}"
      tenant_kubectl -n "${namespace}" delete pod "${pod}" --force --grace-period=0 --wait=false >/dev/null
    done
    sleep 20
  done
  stale="$(list_stale_tenant_pods)"
  if [[ -n "${stale}" ]]; then
    echo "stale tenant pods remained after cleanup:" >&2
    echo "${stale}" >&2
    tenant_kubectl get pods -A -o wide >&2 || true
    exit 1
  fi
  echo "stale tenant pods cleaned"
}

wait_tenant_pods_steady() {
  echo "== wait for tenant pods to settle =="
  local non_steady=""
  start_deadline
  while (( $(date +%s) < deadline )); do
    non_steady=""
    local namespace
    for namespace in ${STALE_POD_NAMESPACES}; do
      namespace_non_steady="$(
        tenant_kubectl get pods -n "${namespace}" --no-headers 2>/dev/null \
          | awk '$3 != "Running" && $3 != "Succeeded" {print ns " " $1 " " $3}' ns="${namespace}" || true
      )"
      if [[ -n "${namespace_non_steady}" ]]; then
        non_steady="${non_steady}${namespace_non_steady}"$'\n'
      fi
    done
    if [[ -z "${non_steady}" ]]; then
      echo "tenant pods steady in namespaces: ${STALE_POD_NAMESPACES}"
      return
    fi
    sleep "${POLL_SECONDS}"
  done
  echo "tenant pods did not settle:" >&2
  echo "${non_steady}" >&2
  tenant_kubectl get pods -A -o wide >&2 || true
  exit 1
}

echo "== tenant control-plane restart drill target =="
${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}"
wait_jsonpath "KCC phase" "Ready" '{.status.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}"
wait_jsonpath "KCC endpointProbeReachable" "true" '{.status.endpointProbeReachable}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}"

api_endpoint="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}" \
    -o jsonpath='{.status.apiEndpoint}'
)"
[[ -n "${api_endpoint}" ]] || { echo "expected ${TENANT_NAMESPACE}/${CLUSTER_CLAIM_NAME} status.apiEndpoint" >&2; exit 1; }
wait_readyz "${api_endpoint}"

tenant_vm="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm \
    -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME},cluster.x-k8s.io/role=control-plane" \
    -o jsonpath='{.items[0].metadata.name}'
)"
[[ -n "${tenant_vm}" ]] || { echo "expected CAPK control-plane VM for ${CLUSTER_NAME}" >&2; exit 1; }
machine_name="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get machine \
    -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME},cluster.x-k8s.io/control-plane=" \
    -o jsonpath='{.items[0].metadata.name}'
)"
[[ -n "${machine_name}" ]] || { echo "expected CAPI control-plane Machine for ${CLUSTER_NAME}" >&2; exit 1; }

root_pvc="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "${tenant_vm}" \
    -o jsonpath='{.spec.dataVolumeTemplates[0].metadata.name}' 2>/dev/null || true
)"
[[ -n "${root_pvc}" ]] || { echo "expected ${TENANT_NAMESPACE}/${tenant_vm} to use a DataVolume root disk" >&2; exit 1; }
root_storage_class="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get pvc "${root_pvc}" \
    -o jsonpath='{.spec.storageClassName}'
)"
root_pvc_uid_before="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get pvc "${root_pvc}" \
    -o jsonpath='{.metadata.uid}'
)"
dv_phase_before="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get datavolume "${root_pvc}" \
    -o jsonpath='{.status.phase}'
)"
[[ "${root_storage_class}" == "longhorn" ]] || { echo "expected root PVC storageClass longhorn, got ${root_storage_class}" >&2; exit 1; }
[[ "${dv_phase_before}" == "Succeeded" ]] || { echo "expected root DataVolume Succeeded before restart, got ${dv_phase_before}" >&2; exit 1; }

vmi_uid_before="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}" \
    -o jsonpath='{.metadata.uid}'
)"
vmi_node_before="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}" \
    -o jsonpath='{.status.nodeName}'
)"
vmi_ip_before="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}" \
    -o jsonpath='{.status.interfaces[0].ipAddress}'
)"
echo "target vm=${tenant_vm} machine=${machine_name} rootPVC=${root_pvc} rootPVCUID=${root_pvc_uid_before} vmiUID=${vmi_uid_before} node=${vmi_node_before} ip=${vmi_ip_before}"

echo "== delete CAPK control-plane VMI =="
${KUBECTL} -n "${TENANT_NAMESPACE}" delete vmi "${tenant_vm}" --wait=true
wait_for "VMI ${TENANT_NAMESPACE}/${tenant_vm} recreated" \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}"

echo "== wait for recreated VMI and preserved root disk =="
start_deadline
vmi_uid_after=""
while (( $(date +%s) < deadline )); do
  vmi_uid_after="$(
    ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}" \
      -o jsonpath='{.metadata.uid}' 2>/dev/null || true
  )"
  [[ -n "${vmi_uid_after}" && "${vmi_uid_after}" != "${vmi_uid_before}" ]] && break
  sleep "${POLL_SECONDS}"
done
[[ -n "${vmi_uid_after}" && "${vmi_uid_after}" != "${vmi_uid_before}" ]] || {
  echo "expected recreated VMI UID to differ from ${vmi_uid_before}, got ${vmi_uid_after:-<empty>}" >&2
  exit 1
}

wait_jsonpath "VMI phase" "Running" '{.status.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}"
wait_jsonpath "VM ready" "true" '{.status.ready}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "${tenant_vm}"

root_pvc_uid_after="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get pvc "${root_pvc}" \
    -o jsonpath='{.metadata.uid}'
)"
dv_phase_after="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get datavolume "${root_pvc}" \
    -o jsonpath='{.status.phase}'
)"
[[ "${root_pvc_uid_after}" == "${root_pvc_uid_before}" ]] || {
  echo "root PVC UID changed: before=${root_pvc_uid_before} after=${root_pvc_uid_after}" >&2
  exit 1
}
[[ "${dv_phase_after}" == "Succeeded" ]] || { echo "expected root DataVolume Succeeded after restart, got ${dv_phase_after}" >&2; exit 1; }

vmi_node_after="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}" \
    -o jsonpath='{.status.nodeName}'
)"
vmi_ip_after="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}" \
    -o jsonpath='{.status.interfaces[0].ipAddress}'
)"
echo "recreated vmiUID=${vmi_uid_after} node=${vmi_node_after} ip=${vmi_ip_after}; rootPVCUID preserved=${root_pvc_uid_after}"

echo "== wait for CAPI and provider status recovery =="
${KUBECTL} -n "${TENANT_NAMESPACE}" wait --for=condition=Available=true "cluster/${CLUSTER_NAME}" --timeout="${WAIT_SECONDS}s"
${KUBECTL} -n "${TENANT_NAMESPACE}" wait --for=condition=Available=true "kubeadmcontrolplane/${CLUSTER_NAME}-control-plane" --timeout="${WAIT_SECONDS}s"
${KUBECTL} -n "${TENANT_NAMESPACE}" wait --for=condition=Ready=true "machine/${machine_name}" --timeout="${WAIT_SECONDS}s"
wait_jsonpath "KCC phase" "Ready" '{.status.phase}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}"
wait_jsonpath "KCC endpointProbeReachable" "true" '{.status.endpointProbeReachable}' \
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}"

api_endpoint_after="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}" \
    -o jsonpath='{.status.apiEndpoint}'
)"
[[ -n "${api_endpoint_after}" ]] || { echo "expected recovered status.apiEndpoint" >&2; exit 1; }
wait_readyz "${api_endpoint_after}"
write_tenant_kubeconfig "${api_endpoint_after}"
cleanup_stale_tenant_pods
wait_tenant_pods_steady

${KUBECTL} -n "${ROUTED_SERVICE_NAMESPACE}" get deploy,svc,pdb "${ROUTED_SERVICE_NAME}" -o wide
${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster,kubeadmcontrolplane,machine,vm,vmi -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME}" -o wide

if [[ "${RUN_LAYER_VERIFY}" == "true" ]]; then
  echo "== run tenant layer verifier after restart =="
  TENANT_NAMESPACE="${TENANT_NAMESPACE}" CLUSTER_CLAIM_NAME="${CLUSTER_CLAIM_NAME}" \
    timeout "$(( WAIT_SECONDS + 120 ))" "${SCRIPT_DIR}/verify-tenant-cluster-layer.sh"
fi

if [[ "${RUN_REACHABILITY_PROBE}" == "true" ]]; then
  echo "== run routed reachability probe after restart =="
  timeout 300 "${SCRIPT_DIR}/probe-tenant-api-reachability.sh" "${TENANT_NAMESPACE}" "${CLUSTER_CLAIM_NAME}"
fi

echo "tenant control-plane restart drill passed"
