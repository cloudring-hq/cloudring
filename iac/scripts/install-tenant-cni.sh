#!/usr/bin/env bash
set -euo pipefail

TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-a}"
CLUSTER_NAME="${CLUSTER_NAME:-claim-routable-cluster}"
CILIUM_VERSION="${CILIUM_VERSION:-1.19.5}"
HELM_IMAGE="${HELM_IMAGE:-alpine/helm:3.21.1}"
PROVIDER_NAMESPACE="${PROVIDER_NAMESPACE:-capk-system}"
CILIUM_K8S_SERVICE_HOST="${CILIUM_K8S_SERVICE_HOST:-}"
CILIUM_K8S_SERVICE_PORT="${CILIUM_K8S_SERVICE_PORT:-6443}"

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
KUBECONFIG_SECRET="${KUBECONFIG_SECRET:-${CLUSTER_NAME}-kubeconfig}"
DIRECT_SECRET="${CLUSTER_NAME}-direct-kubeconfig"
INSTALL_JOB="install-cilium-${CLUSTER_NAME}"
SERVICE_NAME="${SERVICE_NAME:-${CLUSTER_NAME}-lb}"
ROUTED_SERVICE_NAMESPACE="${ROUTED_SERVICE_NAMESPACE:-capk-system}"
ROUTED_SERVICE_NAME="${ROUTED_SERVICE_NAME:-${TENANT_NAMESPACE}-${CLUSTER_NAME}-api}"

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
  echo "missing API host for ${SERVICE_NAME} after waiting" >&2
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster "${CLUSTER_NAME}" -o wide || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get svc,endpoints "${SERVICE_NAME}" -o wide || true
  exit 1
}
tenant_vmi_node="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get vmi -l "cluster.x-k8s.io/cluster-name=${CLUSTER_NAME}" -o jsonpath='{.items[0].status.nodeName}' 2>/dev/null || true)"
[[ -n "${tenant_vmi_node}" ]] || { echo "missing VMI node for ${CLUSTER_NAME}" >&2; exit 1; }

select_install_node() {
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

install_node="${INSTALL_NODE:-$(select_install_node "${tenant_vmi_node}")}"
[[ -n "${install_node}" ]] || { echo "missing Ready management node for installer" >&2; exit 1; }
echo "installing tenant CNI for ${CLUSTER_NAME} via API host ${api_host} from management node ${install_node} (VMI on ${tenant_vmi_node})"

tmp="$(mktemp)"
cleanup() { rm -f "${tmp}"; }
trap cleanup EXIT

cilium_k8s_service_flags=""
if [[ -n "${CILIUM_K8S_SERVICE_HOST}" ]]; then
  cilium_k8s_service_flags="--set k8sServiceHost=${CILIUM_K8S_SERVICE_HOST} --set k8sServicePort=${CILIUM_K8S_SERVICE_PORT}"
fi

${KUBECTL} -n "${TENANT_NAMESPACE}" get secret "${KUBECONFIG_SECRET}" -o jsonpath='{.data.value}' | base64 -d > "${tmp}"
sed -i '/certificate-authority-data:/d' "${tmp}"
sed -i "s#server: .*#server: https://${api_host}:6443\\n    insecure-skip-tls-verify: true#" "${tmp}"

${KUBECTL} -n "${PROVIDER_NAMESPACE}" create secret generic "${DIRECT_SECRET}" \
  --from-file=value="${tmp}" \
  --dry-run=client -o yaml | ${KUBECTL} apply -f -

${KUBECTL} -n "${PROVIDER_NAMESPACE}" delete job "${INSTALL_JOB}" --ignore-not-found --wait=true

cat <<YAML | ${KUBECTL} apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: ${INSTALL_JOB}
  namespace: ${PROVIDER_NAMESPACE}
  labels:
    app.kubernetes.io/name: tenant-cni-installer
    platform.privatecloud.local/cluster: ${CLUSTER_NAME}
spec:
  backoffLimit: 1
  ttlSecondsAfterFinished: 3600
  template:
    metadata:
      labels:
        app.kubernetes.io/name: tenant-cni-installer
        platform.privatecloud.local/cluster: ${CLUSTER_NAME}
    spec:
      nodeSelector:
        kubernetes.io/hostname: ${install_node}
      restartPolicy: Never
      containers:
        - name: helm
          image: ${HELM_IMAGE}
          command:
            - sh
            - -lc
            - |
              set -eux
              helm repo add cilium https://helm.cilium.io
              helm repo update
              helm upgrade --install cilium cilium/cilium \
                --version ${CILIUM_VERSION} \
                --namespace kube-system \
                --kubeconfig /kubeconfig/value \
                --set operator.replicas=1 \
                --set ipam.mode=kubernetes \
                --set kubeProxyReplacement=false \
                ${cilium_k8s_service_flags} \
                --wait \
                --timeout 10m
          volumeMounts:
            - name: kubeconfig
              mountPath: /kubeconfig
              readOnly: true
      volumes:
        - name: kubeconfig
          secret:
            secretName: ${DIRECT_SECRET}
YAML

if ! ${KUBECTL} -n "${PROVIDER_NAMESPACE}" wait --for=condition=Complete "job/${INSTALL_JOB}" --timeout=12m; then
  ${KUBECTL} -n "${PROVIDER_NAMESPACE}" describe "job/${INSTALL_JOB}" || true
  ${KUBECTL} -n "${PROVIDER_NAMESPACE}" logs "job/${INSTALL_JOB}" --all-containers=true --tail=-1 || true
  exit 1
fi
${KUBECTL} -n "${PROVIDER_NAMESPACE}" logs "job/${INSTALL_JOB}"
