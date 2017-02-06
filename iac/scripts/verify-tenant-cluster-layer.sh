#!/usr/bin/env bash
set -euo pipefail

TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-a}"
CLUSTER_CLAIM_NAME="${CLUSTER_CLAIM_NAME:-routable-cluster}"
CLUSTER_NAME="${CLUSTER_NAME:-claim-${CLUSTER_CLAIM_NAME}}"
PROVIDER_NAMESPACE="${PROVIDER_NAMESPACE:-capk-system}"
KUBECTL="${KUBECTL:-sudo k3s kubectl}"
KUBECONFIG_SECRET="${KUBECONFIG_SECRET:-${CLUSTER_NAME}-kubeconfig}"
DIRECT_SECRET="${CLUSTER_NAME}-direct-kubeconfig"
SERVICE_NAME="${SERVICE_NAME:-${CLUSTER_NAME}-lb}"
ROUTED_SERVICE_NAMESPACE="${ROUTED_SERVICE_NAMESPACE:-capk-system}"
ROUTED_SERVICE_NAME="${ROUTED_SERVICE_NAME:-${TENANT_NAMESPACE}-${CLUSTER_NAME}-api}"
VERIFY_PREFIX="verify-${CLUSTER_NAME}"

echo "== cluster api providers =="
${KUBECTL} get providers -A

echo "== cluster api controllers =="
${KUBECTL} wait -n capi-system --for=condition=Available=true deployment/capi-controller-manager --timeout=120s
${KUBECTL} wait -n capi-kubeadm-bootstrap-system --for=condition=Available=true deployment/capi-kubeadm-bootstrap-controller-manager --timeout=120s
${KUBECTL} wait -n capi-kubeadm-control-plane-system --for=condition=Available=true deployment/capi-kubeadm-control-plane-controller-manager --timeout=120s
${KUBECTL} wait -n capk-system --for=condition=Available=true deployment/capk-controller-manager --timeout=120s

echo "== tenant cluster claim =="
phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}" -o jsonpath='{.status.phase}')"
secret="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}" -o jsonpath='{.status.kubeconfigSecret}')"
if [[ "${phase}" == "PendingClusterAPI" || -z "${phase}" ]]; then
  echo "expected KubernetesClusterClaim to be reconciled into Cluster API, got phase=${phase}" >&2
  exit 1
fi
[[ "${secret}" == "${KUBECONFIG_SECRET}" ]] || {
  echo "unexpected kubeconfig secret name: ${secret}" >&2
  exit 1
}
echo "${CLUSTER_CLAIM_NAME} phase=${phase} kubeconfigSecret=${secret}"

echo "== tenant cluster api objects =="
${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster "${CLUSTER_NAME}"
${KUBECTL} -n "${TENANT_NAMESPACE}" get kubevirtcluster "${CLUSTER_NAME}"
${KUBECTL} -n "${TENANT_NAMESPACE}" get kubeadmcontrolplane "${CLUSTER_NAME}-control-plane"
${KUBECTL} -n "${TENANT_NAMESPACE}" get machinedeployment "${CLUSTER_NAME}-default" || true
${KUBECTL} -n "${TENANT_NAMESPACE}" get networkpolicy "allow-capi-${CLUSTER_NAME}"

infra_template="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubeadmcontrolplane "${CLUSTER_NAME}-control-plane" -o jsonpath='{.spec.machineTemplate.spec.infrastructureRef.name}')"
root_storage_class="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubevirtmachinetemplate "${infra_template}" -o jsonpath='{.spec.template.spec.virtualMachineTemplate.spec.dataVolumeTemplates[0].spec.storage.storageClassName}' 2>/dev/null || true)"
root_volume_name="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubevirtmachinetemplate "${infra_template}" -o jsonpath='{.spec.template.spec.virtualMachineTemplate.spec.dataVolumeTemplates[0].metadata.name}' 2>/dev/null || true)"
interface_ports="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubevirtmachinetemplate "${infra_template}" -o jsonpath='{.spec.template.spec.virtualMachineTemplate.spec.template.spec.domain.devices.interfaces[0].ports[*].port}' 2>/dev/null || true)"
interface_binding="$(
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get kubevirtmachinetemplate "${infra_template}" -o json | python3 -c '
import json
import sys

template = json.load(sys.stdin)
interfaces = (
    template.get("spec", {})
    .get("template", {})
    .get("spec", {})
    .get("virtualMachineTemplate", {})
    .get("spec", {})
    .get("template", {})
    .get("spec", {})
    .get("domain", {})
    .get("devices", {})
    .get("interfaces", [])
)
print("masquerade" if interfaces and "masquerade" in interfaces[0] else "")
'
)"
if [[ -n "${root_volume_name}" ]]; then
  [[ "${root_storage_class}" == "longhorn" ]] || { echo "expected CAPK root DataVolume storageClass longhorn, got ${root_storage_class}" >&2; exit 1; }
  [[ "${interface_binding}" == "masquerade" ]] || { echo "expected CAPK tenant node interface to use masquerade binding" >&2; exit 1; }
  [[ " ${interface_ports} " == *" 22 "* && " ${interface_ports} " == *" 6443 "* ]] || {
    echo "expected CAPK masquerade ports 22 and 6443, got ${interface_ports}" >&2
    exit 1
  }
  echo "CAPK template ${infra_template} uses root DataVolume ${root_volume_name}, storageClass=${root_storage_class}, masquerade ports=${interface_ports}"
else
  echo "CAPK template ${infra_template} does not use DataVolume root; this is legacy containerDisk mode"
fi

admission_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}" -o jsonpath='{.status.admission.phase}')"
admission_cell="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}" -o jsonpath='{.status.admission.capacityCell}')"
effective_workers="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${CLUSTER_CLAIM_NAME}" -o jsonpath='{.status.admission.effectiveWorkerReplicas[0].admitted}')"
md_replicas="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get machinedeployment "${CLUSTER_NAME}-default" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo 0)"
[[ "${admission_phase}" == "Admitted" && "${admission_cell}" == "lab-hyperv" ]] || {
  echo "expected ${CLUSTER_CLAIM_NAME} admitted to lab-hyperv, got phase=${admission_phase} cell=${admission_cell}" >&2
  exit 1
}
[[ "${effective_workers}" == "0" && "${md_replicas}" == "0" ]] || {
  echo "expected tenant worker guardrail to keep admitted workers and MachineDeployment at 0, got admitted=${effective_workers} md=${md_replicas}" >&2
  exit 1
}

echo "== tenant cluster vm =="
tenant_vm="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get vm -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME}" -o jsonpath='{.items[0].metadata.name}')"
[[ -n "${tenant_vm}" ]] || { echo "expected a CAPK-created KubeVirt VM" >&2; exit 1; }
${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "${tenant_vm}"
${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}"

vmi_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi "${tenant_vm}" -o jsonpath='{.status.phase}')"
if [[ "${vmi_phase}" != "Running" ]]; then
  echo "expected CAPK-created VMI to be Running, got ${vmi_phase}" >&2
  exit 1
fi

echo "== tenant cluster readiness =="
${KUBECTL} -n "${TENANT_NAMESPACE}" wait --for=condition=Available=true "cluster/${CLUSTER_NAME}" --timeout=120s
${KUBECTL} -n "${TENANT_NAMESPACE}" wait --for=condition=Available=true "kubeadmcontrolplane/${CLUSTER_NAME}-control-plane" --timeout=120s

api_host="${TENANT_API_HOST:-}"
for _ in $(seq 1 120); do
  if [[ -z "${api_host}" ]]; then
    api_host="$(${KUBECTL} -n "${ROUTED_SERVICE_NAMESPACE}" get svc "${ROUTED_SERVICE_NAME}" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
  fi
  if [[ -z "${api_host}" ]]; then
    api_host="$(${KUBECTL} -n "${ROUTED_SERVICE_NAMESPACE}" get svc "${ROUTED_SERVICE_NAME}" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)"
  fi
  if [[ -z "${api_host}" ]]; then
    api_host="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster "${CLUSTER_NAME}" -o jsonpath='{.spec.controlPlaneEndpoint.host}' 2>/dev/null || true)"
  fi
  if [[ -z "${api_host}" ]]; then
    api_host="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster "${CLUSTER_NAME}" -o jsonpath='{.status.controlPlaneEndpoint.host}' 2>/dev/null || true)"
  fi
  if [[ -z "${api_host}" ]]; then
    api_host="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get svc "${SERVICE_NAME}" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || true)"
  fi
  if [[ -z "${api_host}" ]]; then
    api_host="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get endpoints "${SERVICE_NAME}" -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null || true)"
  fi
  [[ -n "${api_host}" ]] && break
  sleep 5
done
[[ -n "${api_host}" ]] || {
  echo "expected tenant cluster API host" >&2
  ${KUBECTL} -n "${ROUTED_SERVICE_NAMESPACE}" get svc,endpoints "${ROUTED_SERVICE_NAME}" -o wide || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get svc,endpoints "${SERVICE_NAME}" -o wide || true
  exit 1
}
service_type="$(${KUBECTL} -n "${ROUTED_SERVICE_NAMESPACE}" get svc "${ROUTED_SERVICE_NAME}" -o jsonpath='{.spec.type}' 2>/dev/null || true)"
external_ip="$(${KUBECTL} -n "${ROUTED_SERVICE_NAMESPACE}" get svc "${ROUTED_SERVICE_NAME}" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
proxy_available="$(${KUBECTL} -n "${ROUTED_SERVICE_NAMESPACE}" get deploy "${ROUTED_SERVICE_NAME}" -o jsonpath='{.status.availableReplicas}' 2>/dev/null || true)"
[[ "${service_type}" == "LoadBalancer" ]] || { echo "expected ${ROUTED_SERVICE_NAMESPACE}/${ROUTED_SERVICE_NAME} to be LoadBalancer, got ${service_type:-missing}" >&2; exit 1; }
[[ -n "${external_ip}" ]] || { echo "expected ${ROUTED_SERVICE_NAMESPACE}/${ROUTED_SERVICE_NAME} to have a routed external IP" >&2; exit 1; }
[[ "${proxy_available:-0}" -ge 1 ]] || { echo "expected routed API proxy deployment ${ROUTED_SERVICE_NAMESPACE}/${ROUTED_SERVICE_NAME} to be available" >&2; exit 1; }
tenant_vmi_node="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME}" -o jsonpath='{.items[0].status.nodeName}' 2>/dev/null || true)"
[[ -n "${tenant_vmi_node}" ]] || { echo "expected tenant VMI node" >&2; exit 1; }
select_verify_node() {
  local vmi_node="$1"
  local fallback=""
  while read -r node status _; do
    [[ "${status}" == "Ready" ]] || continue
    [[ -z "${fallback}" ]] && fallback="${node}"
    if [[ "${node}" != "${vmi_node}" ]]; then
      echo "${node}"
      return
    fi
  done < <(${KUBECTL} get nodes --no-headers)
  [[ -n "${fallback}" ]] && echo "${fallback}"
}
verify_node="${VERIFY_NODE:-$(select_verify_node "${tenant_vmi_node}")}"
[[ -n "${verify_node}" ]] || { echo "expected Ready management node for verification" >&2; exit 1; }
echo "tenant cluster API ${api_host} is hosted on VMI node ${tenant_vmi_node}; verifying provider routed service ${ROUTED_SERVICE_NAMESPACE}/${ROUTED_SERVICE_NAME} from management node ${verify_node}"

tmp="$(mktemp)"
cleanup() { rm -f "${tmp}"; }
trap cleanup EXIT

${KUBECTL} -n "${TENANT_NAMESPACE}" get secret "${KUBECONFIG_SECRET}" -o jsonpath='{.data.value}' | base64 -d > "${tmp}"
sed -i '/certificate-authority-data:/d' "${tmp}"
sed -i "s#server: .*#server: https://${api_host}:6443\\n    insecure-skip-tls-verify: true#" "${tmp}"

${KUBECTL} -n "${PROVIDER_NAMESPACE}" create secret generic "${DIRECT_SECRET}" \
  --from-file=value="${tmp}" \
  --dry-run=client -o yaml | ${KUBECTL} apply -f -

for job in "${VERIFY_PREFIX}-nodes" "${VERIFY_PREFIX}-pods" "${VERIFY_PREFIX}-ready"; do
  ${KUBECTL} -n "${PROVIDER_NAMESPACE}" delete job "${job}" --ignore-not-found --wait=true
done

cat <<YAML | ${KUBECTL} apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: ${VERIFY_PREFIX}-nodes
  namespace: ${PROVIDER_NAMESPACE}
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: ${verify_node}
      restartPolicy: Never
      containers:
        - name: kubectl
          image: registry.k8s.io/kubectl:v1.32.1
          command: ["kubectl"]
          args: ["--kubeconfig", "/kubeconfig/value", "get", "nodes", "-o", "wide"]
          volumeMounts:
            - name: kubeconfig
              mountPath: /kubeconfig
              readOnly: true
      volumes:
        - name: kubeconfig
          secret:
            secretName: ${DIRECT_SECRET}
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ${VERIFY_PREFIX}-pods
  namespace: ${PROVIDER_NAMESPACE}
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: ${verify_node}
      restartPolicy: Never
      containers:
        - name: kubectl
          image: registry.k8s.io/kubectl:v1.32.1
          command: ["kubectl"]
          args: ["--kubeconfig", "/kubeconfig/value", "get", "pods", "-A", "-o", "wide"]
          volumeMounts:
            - name: kubeconfig
              mountPath: /kubeconfig
              readOnly: true
      volumes:
        - name: kubeconfig
          secret:
            secretName: ${DIRECT_SECRET}
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ${VERIFY_PREFIX}-ready
  namespace: ${PROVIDER_NAMESPACE}
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: ${verify_node}
      restartPolicy: Never
      containers:
        - name: kubectl
          image: registry.k8s.io/kubectl:v1.32.1
          command: ["kubectl"]
          args: ["--kubeconfig", "/kubeconfig/value", "wait", "--for=condition=Ready", "node", "--all", "--timeout=5m"]
          volumeMounts:
            - name: kubeconfig
              mountPath: /kubeconfig
              readOnly: true
      volumes:
        - name: kubeconfig
          secret:
            secretName: ${DIRECT_SECRET}
YAML

wait_job() {
  local job="$1"
  if ! ${KUBECTL} -n "${PROVIDER_NAMESPACE}" wait --for=condition=Complete "job/${job}" --timeout=7m; then
    ${KUBECTL} -n "${PROVIDER_NAMESPACE}" describe "job/${job}" || true
    ${KUBECTL} -n "${PROVIDER_NAMESPACE}" logs "job/${job}" --all-containers=true --tail=-1 || true
    exit 1
  fi
}

wait_job "${VERIFY_PREFIX}-nodes"
wait_job "${VERIFY_PREFIX}-pods"
wait_job "${VERIFY_PREFIX}-ready"

${KUBECTL} -n "${PROVIDER_NAMESPACE}" logs "job/${VERIFY_PREFIX}-nodes"
${KUBECTL} -n "${PROVIDER_NAMESPACE}" logs "job/${VERIFY_PREFIX}-pods"
${KUBECTL} -n "${PROVIDER_NAMESPACE}" logs "job/${VERIFY_PREFIX}-ready"

if ! ${KUBECTL} -n "${TENANT_NAMESPACE}" wait --for=condition=Ready=true machine -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME}" --timeout=120s; then
  echo "tenant workload API is reachable, but Cluster API Machine readiness is degraded:" >&2
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster,kubeadmcontrolplane,machine,kubevirtmachine,vm,vmi -o wide >&2 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" describe machine -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME}" >&2 || true
  exit 1
fi
