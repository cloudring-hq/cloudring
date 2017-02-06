#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"

check_deployment() {
  local namespace="$1"
  local deployment="$2"
  local selector="$3"
  local expected_replicas="${4:-3}"

  ${KUBECTL} -n "${namespace}" rollout status "deployment/${deployment}" --timeout=5m

  local desired available ready updated
  for _ in $(seq 1 60); do
    desired="$(${KUBECTL} -n "${namespace}" get deployment "${deployment}" -o jsonpath='{.spec.replicas}')"
    available="$(${KUBECTL} -n "${namespace}" get deployment "${deployment}" -o jsonpath='{.status.availableReplicas}')"
    ready="$(${KUBECTL} -n "${namespace}" get deployment "${deployment}" -o jsonpath='{.status.readyReplicas}')"
    updated="$(${KUBECTL} -n "${namespace}" get deployment "${deployment}" -o jsonpath='{.status.updatedReplicas}')"
    if [[ "${desired}" == "${expected_replicas}" && "${available}" == "${expected_replicas}" && "${ready}" == "${expected_replicas}" && "${updated}" == "${expected_replicas}" ]]; then
      break
    fi
    sleep 5
  done
  if [[ "${desired}" != "${expected_replicas}" || "${available}" != "${expected_replicas}" || "${ready}" != "${expected_replicas}" || "${updated}" != "${expected_replicas}" ]]; then
    echo "${namespace}/${deployment} expected ${expected_replicas}/${expected_replicas}, got desired=${desired:-0} available=${available:-0} ready=${ready:-0} updated=${updated:-0}" >&2
    exit 1
  fi

  ${KUBECTL} -n "${namespace}" get pdb "${deployment}" >/dev/null
  local min_available
  min_available="$(${KUBECTL} -n "${namespace}" get pdb "${deployment}" -o jsonpath='{.spec.minAvailable}')"
  if [[ "${min_available}" != "2" ]]; then
    echo "${namespace}/${deployment} expected PDB minAvailable=2, got ${min_available}" >&2
    exit 1
  fi

  local spread_count
  spread_count="$(${KUBECTL} -n "${namespace}" get pods -l "${selector}" --field-selector=status.phase=Running -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | sort -u | wc -l)"
  if (( spread_count < 2 )); then
    echo "${namespace}/${deployment} expected pods across at least 2 nodes, got ${spread_count}" >&2
    exit 1
  fi

  echo "${namespace}/${deployment} desired=${desired} available=${available} ready=${ready} updated=${updated}, PDB minAvailable=${min_available}, nodes=${spread_count}"
}

echo "== management control-plane HA =="
check_deployment capi-system capi-controller-manager "cluster.x-k8s.io/provider=cluster-api,control-plane=controller-manager"
check_deployment capi-kubeadm-bootstrap-system capi-kubeadm-bootstrap-controller-manager "cluster.x-k8s.io/provider=bootstrap-kubeadm,control-plane=controller-manager"
check_deployment capi-kubeadm-control-plane-system capi-kubeadm-control-plane-controller-manager "cluster.x-k8s.io/provider=control-plane-kubeadm,control-plane=controller-manager"
check_deployment capk-system capk-controller-manager "cluster.x-k8s.io/provider=kubevirt,control-plane=controller-manager"
check_deployment cert-manager cert-manager "app.kubernetes.io/component=controller,app.kubernetes.io/instance=cert-manager,app.kubernetes.io/name=cert-manager"
check_deployment cert-manager cert-manager-cainjector "app.kubernetes.io/component=cainjector,app.kubernetes.io/instance=cert-manager,app.kubernetes.io/name=cainjector"
check_deployment cert-manager cert-manager-webhook "app.kubernetes.io/component=webhook,app.kubernetes.io/instance=cert-manager,app.kubernetes.io/name=webhook"
if ${KUBECTL} -n cdi get deployment cdi-operator >/dev/null 2>&1; then
  check_deployment cdi cdi-operator "name=cdi-operator,operator.cdi.kubevirt.io="
  check_deployment cdi cdi-apiserver "cdi.kubevirt.io=cdi-apiserver"
  check_deployment cdi cdi-deployment "cdi.kubevirt.io=cdi-deployment"
  check_deployment cdi cdi-uploadproxy "cdi.kubevirt.io=cdi-uploadproxy"
fi
