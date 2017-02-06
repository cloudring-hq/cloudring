#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
NAMESPACE="${NAMESPACE:-flux-system}"
CONFIRM="${CONFIRM_FLUX_SOURCE_FAILOVER:-false}"
FAILOVER_SCOPE="${FLUX_SOURCE_FAILOVER_SCOPE:-pod}"
CORDONED_NODE=""

cleanup() {
  if [[ -n "${CORDONED_NODE}" ]]; then
    ${KUBECTL} uncordon "${CORDONED_NODE}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

if [[ "${CONFIRM}" != "true" ]]; then
  echo "Set CONFIRM_FLUX_SOURCE_FAILOVER=true to delete the current Flux source-controller leader pod." >&2
  exit 1
fi

case "${FAILOVER_SCOPE}" in
  pod|leader-node-cordon) ;;
  *)
    echo "FLUX_SOURCE_FAILOVER_SCOPE must be pod or leader-node-cordon, got ${FAILOVER_SCOPE}" >&2
    exit 1
    ;;
esac

source_state() {
  ${KUBECTL} -n "${NAMESPACE}" get pods -l app=source-controller -o json | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
running = ready = 0
ready_name = ready_node = ""
for pod in payload.get("items", []):
    if pod.get("status", {}).get("phase") != "Running":
        continue
    running += 1
    conditions = {
        item.get("type"): item.get("status")
        for item in pod.get("status", {}).get("conditions", [])
    }
    if conditions.get("Ready") == "True":
        ready += 1
        ready_name = pod.get("metadata", {}).get("name", "")
        ready_node = pod.get("spec", {}).get("nodeName", "")
print(running, ready, ready_name, ready_node)
'
}

source_endpoint_pod() {
  ${KUBECTL} -n "${NAMESPACE}" get endpoints source-controller -o json | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
names = []
for subset in payload.get("subsets", []):
    for address in subset.get("addresses", []) or []:
        target = address.get("targetRef", {})
        if target.get("kind") == "Pod":
            names.append(target.get("name", ""))
print(" ".join(sorted(name for name in names if name)))
'
}

source_leader() {
  local holder
  local leader
  local node
  holder="$(${KUBECTL} -n "${NAMESPACE}" get lease source-controller-leader-election -o jsonpath='{.spec.holderIdentity}' 2>/dev/null || true)"
  leader="${holder%_*}"
  node="$(${KUBECTL} -n "${NAMESPACE}" get pod "${leader}" -o jsonpath='{.spec.nodeName}' 2>/dev/null || true)"
  echo "${leader} ${node} ${holder}"
}

wait_condition() {
  local kind="$1"
  local name="$2"
  local condition="$3"
  local label="$4"
  for _ in $(seq 1 90); do
    status="$(${KUBECTL} -n "${NAMESPACE}" get "${kind}" "${name}" -o "jsonpath={.status.conditions[?(@.type=='${condition}')].status}" 2>/dev/null || true)"
    if [[ "${status}" == "True" ]]; then
      echo "${label} ${condition}=True"
      return 0
    fi
    sleep 2
  done
  echo "timed out waiting for ${label} ${condition}=True" >&2
  ${KUBECTL} -n "${NAMESPACE}" get "${kind}" "${name}" -o yaml >&2 || true
  return 1
}

wait_source_ready() {
  local forbidden_pod="${1:-}"
  local forbidden_node="${2:-}"
  local min_running="${3:-3}"
  for _ in $(seq 1 90); do
    read -r running ready _ _ < <(source_state)
    read -r leader leader_node holder < <(source_leader)
    endpoint_pod="$(source_endpoint_pod)"
    if [[ "${running:-0}" -ge "${min_running}" && "${ready:-0}" -eq 1 && -n "${leader}" && -n "${leader_node}" ]]; then
      if [[ -n "${forbidden_pod}" && "${leader}" == "${forbidden_pod}" ]]; then
        sleep 2
        continue
      fi
      if [[ -n "${forbidden_node}" && "${leader_node}" == "${forbidden_node}" ]]; then
        sleep 2
        continue
      fi
      if [[ "${holder}" == "${leader}"_* && "${endpoint_pod}" == "${leader}" ]]; then
        echo "source-controller leader=${leader} node=${leader_node} running=${running} ready=${ready} endpoints=${endpoint_pod}"
        return 0
      fi
    fi
    sleep 2
  done
  echo "timed out waiting for source-controller leader election state" >&2
  ${KUBECTL} -n "${NAMESPACE}" get deploy,pod,endpoints source-controller -o wide >&2 || true
  ${KUBECTL} -n "${NAMESPACE}" get lease source-controller-leader-election -o yaml >&2 || true
  return 1
}

wait_source_spread() {
  for _ in $(seq 1 90); do
    read -r running ready _ _ node_count node_list < <(
      ${KUBECTL} -n "${NAMESPACE}" get pods -l app=source-controller -o json | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
nodes = set()
running = ready = 0
ready_name = ready_node = ""
for pod in payload.get("items", []):
    if pod.get("status", {}).get("phase") != "Running":
        continue
    running += 1
    node = pod.get("spec", {}).get("nodeName", "")
    if node:
        nodes.add(node)
    conditions = {
        item.get("type"): item.get("status")
        for item in pod.get("status", {}).get("conditions", [])
    }
    if conditions.get("Ready") == "True":
        ready += 1
        ready_name = pod.get("metadata", {}).get("name", "")
        ready_node = node
print(running, ready, ready_name, ready_node, len(nodes), ",".join(sorted(nodes)))
'
    )
    read -r leader leader_node holder < <(source_leader)
    endpoint_pod="$(source_endpoint_pod)"
    if [[ "${running:-0}" -eq 3 && "${ready:-0}" -eq 1 && "${node_count:-0}" -eq 3 && "${holder}" == "${leader}"_* && "${endpoint_pod}" == "${leader}" ]]; then
      echo "source-controller restored spread leader=${leader} node=${leader_node} nodes=${node_list}"
      return 0
    fi
    sleep 2
  done
  echo "timed out waiting for source-controller strict spread restore" >&2
  ${KUBECTL} -n "${NAMESPACE}" get deploy,pod,endpoints source-controller -o wide >&2 || true
  ${KUBECTL} -n "${NAMESPACE}" get lease source-controller-leader-election -o yaml >&2 || true
  return 1
}

echo "== source-controller pre-failover state =="
wait_source_ready
read -r old_leader old_node old_holder < <(source_leader)
old_transitions="$(${KUBECTL} -n "${NAMESPACE}" get lease source-controller-leader-election -o jsonpath='{.spec.leaseTransitions}')"
old_revision="$(${KUBECTL} -n "${NAMESPACE}" get gitrepository platform-gitops -o jsonpath='{.status.artifact.revision}')"
old_applied="$(${KUBECTL} -n "${NAMESPACE}" get kustomization platform-base -o jsonpath='{.status.lastAppliedRevision}')"
[[ -n "${old_revision}" && -n "${old_applied}" ]] || {
  echo "expected existing GitRepository artifact and Kustomization applied revision" >&2
  exit 1
}
echo "old leader=${old_leader} node=${old_node} holder=${old_holder} transitions=${old_transitions} revision=${old_revision} applied=${old_applied}"

if [[ "${FAILOVER_SCOPE}" == "leader-node-cordon" ]]; then
  echo "== cordon source-controller leader node =="
  ${KUBECTL} cordon "${old_node}"
  CORDONED_NODE="${old_node}"
fi

echo "== delete source-controller leader =="
${KUBECTL} -n "${NAMESPACE}" delete pod "${old_leader}" --wait=false
${KUBECTL} -n "${NAMESPACE}" wait --for=delete "pod/${old_leader}" --timeout=120s

echo "== source-controller post-failover state =="
if [[ "${FAILOVER_SCOPE}" == "leader-node-cordon" ]]; then
  wait_source_ready "${old_leader}" "${old_node}" 2
else
  wait_source_ready "${old_leader}"
fi
read -r new_leader new_node new_holder < <(source_leader)
new_transitions="$(${KUBECTL} -n "${NAMESPACE}" get lease source-controller-leader-election -o jsonpath='{.spec.leaseTransitions}')"
[[ "${new_leader}" != "${old_leader}" ]] || {
  echo "expected source-controller leader to move away from deleted pod ${old_leader}" >&2
  exit 1
}
[[ "${new_transitions:-0}" -gt "${old_transitions:-0}" ]] || {
  echo "expected source-controller leaseTransitions to increase from ${old_transitions}, got ${new_transitions}" >&2
  exit 1
}
if [[ "${FAILOVER_SCOPE}" == "leader-node-cordon" ]]; then
  [[ "${new_node}" != "${old_node}" ]] || {
    echo "expected source-controller leader to move away from cordoned node ${old_node}" >&2
    exit 1
  }
fi
echo "new leader=${new_leader} node=${new_node} holder=${new_holder} transitions=${new_transitions}"

echo "== force source and kustomization reconcile after failover =="
stamp="$(date +%s)"
${KUBECTL} -n "${NAMESPACE}" annotate gitrepository/platform-gitops reconcile.fluxcd.io/requestedAt="${stamp}" --overwrite >/dev/null
${KUBECTL} -n "${NAMESPACE}" annotate kustomization/platform-base reconcile.fluxcd.io/requestedAt="${stamp}" --overwrite >/dev/null
wait_condition gitrepository platform-gitops Ready "GitRepository/platform-gitops"
wait_condition kustomization platform-base Ready "Kustomization/platform-base"

new_revision="$(${KUBECTL} -n "${NAMESPACE}" get gitrepository platform-gitops -o jsonpath='{.status.artifact.revision}')"
new_applied="$(${KUBECTL} -n "${NAMESPACE}" get kustomization platform-base -o jsonpath='{.status.lastAppliedRevision}')"
[[ "${new_revision}" == "${old_revision}" ]] || {
  echo "expected GitRepository revision to remain ${old_revision}, got ${new_revision}" >&2
  exit 1
}
[[ "${new_applied}" == "${old_applied}" ]] || {
  echo "expected platform-base applied revision to remain ${old_applied}, got ${new_applied}" >&2
  exit 1
}

if [[ "${FAILOVER_SCOPE}" == "leader-node-cordon" ]]; then
  echo "== uncordon source-controller leader node and restore spread =="
  ${KUBECTL} uncordon "${CORDONED_NODE}"
  CORDONED_NODE=""
  wait_source_spread
fi

echo "source-controller failover verification passed scope=${FAILOVER_SCOPE} leader=${old_leader}->${new_leader} revision=${new_revision}"
