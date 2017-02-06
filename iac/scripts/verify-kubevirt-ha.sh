#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
NAMESPACE="${NAMESPACE:-kubevirt}"

check_deployment() {
  local deployment="$1"
  local pdb="$2"
  local label="$3"

  ${KUBECTL} -n "${NAMESPACE}" rollout status "deployment/${deployment}" --timeout=10m

  local desired available ready updated
  desired="$(${KUBECTL} -n "${NAMESPACE}" get deployment "${deployment}" -o jsonpath='{.spec.replicas}')"
  available="$(${KUBECTL} -n "${NAMESPACE}" get deployment "${deployment}" -o jsonpath='{.status.availableReplicas}')"
  ready="$(${KUBECTL} -n "${NAMESPACE}" get deployment "${deployment}" -o jsonpath='{.status.readyReplicas}')"
  updated="$(${KUBECTL} -n "${NAMESPACE}" get deployment "${deployment}" -o jsonpath='{.status.updatedReplicas}')"
  [[ "${desired}" == "3" && "${available}" == "3" && "${ready}" == "3" && "${updated}" == "3" ]] || {
    echo "${deployment} expected 3/3, got desired=${desired:-0} available=${available:-0} ready=${ready:-0} updated=${updated:-0}" >&2
    exit 1
  }

  local policy
  policy="$(${KUBECTL} -n "${NAMESPACE}" get deployment "${deployment}" -o jsonpath='{.spec.template.spec.topologySpreadConstraints[0].whenUnsatisfiable}' 2>/dev/null || true)"
  [[ "${policy}" == "DoNotSchedule" ]] || {
    echo "${deployment} expected strict topology spread DoNotSchedule, got ${policy:-missing}" >&2
    exit 1
  }

  local nodes
  nodes="$(
    ${KUBECTL} -n "${NAMESPACE}" get pods -l "${label}" -o json | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
nodes = set()
for pod in payload.get("items", []):
    if pod.get("status", {}).get("phase") != "Running":
        continue
    conditions = {
        item.get("type"): item.get("status")
        for item in pod.get("status", {}).get("conditions", [])
    }
    if conditions.get("Ready") != "True":
        continue
    node = pod.get("spec", {}).get("nodeName")
    if node:
        nodes.add(node)
print(len(nodes), ",".join(sorted(nodes)))
'
  )"
  node_count="${nodes%% *}"
  node_list="${nodes#* }"
  [[ "${node_count}" == "3" ]] || {
    echo "${deployment} expected Ready pods on 3 distinct nodes, got ${node_count}: ${node_list}" >&2
    exit 1
  }

  ${KUBECTL} -n "${NAMESPACE}" get pdb "${pdb}" >/dev/null
  local min_available
  min_available="$(${KUBECTL} -n "${NAMESPACE}" get pdb "${pdb}" -o jsonpath='{.spec.minAvailable}')"
  [[ "${min_available}" == "2" ]] || {
    echo "${pdb} expected minAvailable=2, got ${min_available:-missing}" >&2
    exit 1
  }

  echo "${deployment} desired=${desired} ready=${ready} nodes=${node_list} pdb=${pdb}:minAvailable=${min_available}"
}

echo "== KubeVirt CR =="
${KUBECTL} -n "${NAMESPACE}" wait kubevirt/kubevirt --for=condition=Available --timeout=10m
phase="$(${KUBECTL} -n "${NAMESPACE}" get kubevirt kubevirt -o jsonpath='{.status.phase}')"
[[ "${phase}" == "Deployed" ]] || {
  echo "expected KubeVirt phase Deployed, got ${phase:-missing}" >&2
  exit 1
}

infra_replicas="$(${KUBECTL} -n "${NAMESPACE}" get kubevirt kubevirt -o jsonpath='{.spec.infra.replicas}')"
workload_replicas="$(${KUBECTL} -n "${NAMESPACE}" get kubevirt kubevirt -o jsonpath='{.spec.workloads.replicas}')"
[[ "${infra_replicas}" == "3" && "${workload_replicas}" == "3" ]] || {
  echo "expected KubeVirt infra/workloads replicas=3/3, got ${infra_replicas:-missing}/${workload_replicas:-missing}" >&2
  exit 1
}

echo "== KubeVirt deployments =="
check_deployment virt-api virt-api-pdb "kubevirt.io=virt-api"
check_deployment virt-controller virt-controller-pdb "kubevirt.io=virt-controller"
check_deployment virt-operator virt-operator "kubevirt.io=virt-operator"

echo "== virt-handler daemonset =="
desired="$(${KUBECTL} -n "${NAMESPACE}" get daemonset virt-handler -o jsonpath='{.status.desiredNumberScheduled}')"
ready="$(${KUBECTL} -n "${NAMESPACE}" get daemonset virt-handler -o jsonpath='{.status.numberReady}')"
available="$(${KUBECTL} -n "${NAMESPACE}" get daemonset virt-handler -o jsonpath='{.status.numberAvailable}')"
[[ "${desired}" == "3" && "${ready}" == "3" && "${available}" == "3" ]] || {
  echo "expected virt-handler 3/3, got desired=${desired:-0} ready=${ready:-0} available=${available:-0}" >&2
  exit 1
}

if ${KUBECTL} -n "${NAMESPACE}" logs daemonset/virt-handler --since=30m 2>/dev/null | grep -qi '/dev/kvm.*missing\|no such file.*dev/kvm'; then
  echo "virt-handler logs contain recent /dev/kvm missing errors" >&2
  exit 1
fi

${KUBECTL} -n "${NAMESPACE}" get pods -o wide
echo "KubeVirt HA verification passed"
