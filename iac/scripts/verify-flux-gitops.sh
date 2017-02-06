#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
NAMESPACE="${NAMESPACE:-flux-system}"

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

echo "== flux namespace and controllers =="
${KUBECTL} get namespace "${NAMESPACE}"
${KUBECTL} -n "${NAMESPACE}" get deploy,pdb,pod -o wide

check_deployment() {
  local deploy="$1"
  local min_ready="$2"
  local expected_pdb_min="$3"
  if [[ "${deploy}" != "source-controller" ]]; then
    ${KUBECTL} -n "${NAMESPACE}" rollout status "deploy/${deploy}" --timeout=180s
  fi
  available="$(${KUBECTL} -n "${NAMESPACE}" get "deploy/${deploy}" -o jsonpath='{.status.availableReplicas}')"
  [[ "${available:-0}" -ge "${min_ready}" ]] || { echo "expected ${deploy} >=${min_ready} available replicas, got ${available:-0}" >&2; exit 1; }
  desired="$(${KUBECTL} -n "${NAMESPACE}" get "deploy/${deploy}" -o jsonpath='{.spec.replicas}')"
  [[ "${desired}" == "3" ]] || { echo "expected ${deploy} replicas=3, got ${desired}" >&2; exit 1; }
  pdb_min="$(${KUBECTL} -n "${NAMESPACE}" get "pdb/${deploy}" -o jsonpath='{.spec.minAvailable}')"
  [[ "${pdb_min}" == "${expected_pdb_min}" ]] || { echo "expected ${deploy} PDB minAvailable=${expected_pdb_min}, got ${pdb_min}" >&2; exit 1; }
  spread="$(${KUBECTL} -n "${NAMESPACE}" get "deploy/${deploy}" -o jsonpath='{.spec.template.spec.topologySpreadConstraints[0].whenUnsatisfiable}' 2>/dev/null || true)"
  [[ "${spread}" == "DoNotSchedule" ]] || { echo "expected ${deploy} strict topology spread DoNotSchedule, got ${spread:-missing}" >&2; exit 1; }
  min_domains="$(${KUBECTL} -n "${NAMESPACE}" get "deploy/${deploy}" -o jsonpath='{.spec.template.spec.topologySpreadConstraints[0].minDomains}' 2>/dev/null || true)"
  [[ "${min_domains}" == "3" ]] || { echo "expected ${deploy} topology spread minDomains=3, got ${min_domains:-missing}" >&2; exit 1; }
  match_label_key="$(${KUBECTL} -n "${NAMESPACE}" get "deploy/${deploy}" -o jsonpath='{.spec.template.spec.topologySpreadConstraints[0].matchLabelKeys[0]}' 2>/dev/null || true)"
  [[ "${match_label_key}" == "pod-template-hash" ]] || { echo "expected ${deploy} topology spread matchLabelKeys[0]=pod-template-hash, got ${match_label_key:-missing}" >&2; exit 1; }
  if [[ "${deploy}" == "source-controller" ]]; then
    max_unavailable="$(${KUBECTL} -n "${NAMESPACE}" get "deploy/${deploy}" -o jsonpath='{.spec.strategy.rollingUpdate.maxUnavailable}' 2>/dev/null || true)"
    [[ "${max_unavailable}" == "2" ]] || {
      echo "expected source-controller rollingUpdate.maxUnavailable=2, got ${max_unavailable:-missing}" >&2
      exit 1
    }
    probe="$(${KUBECTL} -n "${NAMESPACE}" get "deploy/${deploy}" -o jsonpath='{.spec.template.spec.containers[?(@.name=="manager")].readinessProbe.httpGet.path}:{.spec.template.spec.containers[?(@.name=="manager")].readinessProbe.httpGet.port}' 2>/dev/null || true)"
    [[ "${probe}" == "/:http" ]] || {
      echo "expected source-controller readinessProbe / on http, got ${probe:-missing}" >&2
      exit 1
    }
  fi
}

check_pod_node_spread() {
  local app="$1"
  local label="$2"
  local ready_only="$3"
  local expected_nodes="$4"
  local distinct_nodes
  distinct_nodes="$(
    ${KUBECTL} -n "${NAMESPACE}" get pods -l "app=${app}" -o json | python3 -c '
import json
import sys

ready_only = sys.argv[1] == "true"
payload = json.load(sys.stdin)
nodes = set()
for pod in payload.get("items", []):
    if pod.get("status", {}).get("phase") != "Running":
        continue
    conditions = {
        item.get("type"): item.get("status")
        for item in pod.get("status", {}).get("conditions", [])
    }
    if ready_only and conditions.get("Ready") != "True":
        continue
    node = pod.get("spec", {}).get("nodeName")
    if node:
        nodes.add(node)
print(len(nodes), ",".join(sorted(nodes)))
' "${ready_only}"
  )"
  node_count="${distinct_nodes%% *}"
  node_list="${distinct_nodes#* }"
  [[ "${node_count}" -ge "${expected_nodes}" ]] || {
    echo "expected ${label} on at least ${expected_nodes} distinct nodes, got ${node_count}: ${node_list}" >&2
    exit 1
  }
  echo "${label} distinctNodes=${node_count} nodes=${node_list}"
}

check_deployment source-controller 1 1
check_deployment kustomize-controller 2 2
check_deployment helm-controller 2 2
check_deployment notification-controller 2 2
check_deployment platform-gitops-source 2 2
check_pod_node_spread source-controller source-controller-running false 3
check_pod_node_spread kustomize-controller kustomize-controller-ready true 3
check_pod_node_spread helm-controller helm-controller-ready true 3
check_pod_node_spread notification-controller notification-controller-ready true 3
check_pod_node_spread platform-gitops-source platform-gitops-source-ready true 3

echo "== flux source-controller leader election =="
read -r source_running source_ready source_ready_pods < <(
  ${KUBECTL} -n "${NAMESPACE}" get pods -l app=source-controller -o json | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
running = ready = 0
ready_names = []
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
        ready_names.append(pod.get("metadata", {}).get("name", ""))
print(running, ready, ",".join(sorted(ready_names)))
'
)
[[ "${source_running}" -eq 3 ]] || { echo "expected source-controller 3 Running pods, got ${source_running}" >&2; exit 1; }
[[ "${source_ready}" -eq 1 ]] || { echo "expected source-controller exactly 1 Ready artifact-serving pod, got ready=${source_ready} pods=${source_ready_pods:-missing}" >&2; exit 1; }
source_holder="$(${KUBECTL} -n "${NAMESPACE}" get lease source-controller-leader-election -o jsonpath='{.spec.holderIdentity}')"
source_leader="${source_holder%_*}"
[[ -n "${source_leader}" && ",${source_ready_pods}," == *",${source_leader},"* ]] || { echo "expected source-controller lease holder ${source_holder} to match a Ready pod in ${source_ready_pods:-missing}" >&2; exit 1; }
source_endpoint_pods="$(
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
)"
[[ "${source_endpoint_pods}" == "${source_leader}" ]] || { echo "expected source-controller Service endpoint to be only leader ${source_leader}, got ${source_endpoint_pods:-missing}" >&2; exit 1; }
echo "source-controller elected leader=${source_leader} holder=${source_holder} endpoints=${source_endpoint_pods}"

echo "== flux source and kustomization conditions =="
wait_condition gitrepository platform-gitops Ready "GitRepository/platform-gitops"
wait_condition kustomization platform-base Ready "Kustomization/platform-base"

revision="$(${KUBECTL} -n "${NAMESPACE}" get gitrepository platform-gitops -o jsonpath='{.status.artifact.revision}')"
[[ "${revision}" == main/* || "${revision}" == main@sha1:* ]] || { echo "expected platform-gitops artifact revision on main, got ${revision}" >&2; exit 1; }
echo "platform-gitops revision=${revision}"

last_applied="$(${KUBECTL} -n "${NAMESPACE}" get kustomization platform-base -o jsonpath='{.status.lastAppliedRevision}')"
[[ -n "${last_applied}" ]] || { echo "expected platform-base lastAppliedRevision" >&2; exit 1; }
echo "platform-base lastAppliedRevision=${last_applied}"

echo "== platform objects still healthy =="
${KUBECTL} get projects.platform.privatecloud.local
${KUBECTL} get capacitycells.platform.privatecloud.local
${KUBECTL} -n platform-system get hpa provider-portal
portal_hpa_min="$(${KUBECTL} -n platform-system get hpa provider-portal -o jsonpath='{.spec.minReplicas}')"
portal_hpa_max="$(${KUBECTL} -n platform-system get hpa provider-portal -o jsonpath='{.spec.maxReplicas}')"
[[ "${portal_hpa_min}" == "6" && "${portal_hpa_max}" == "9" ]] || {
  echo "expected provider-portal HPA bounds 6-9, got ${portal_hpa_min}-${portal_hpa_max}" >&2
  exit 1
}
portal_pdb_min="$(${KUBECTL} -n platform-system get pdb provider-portal -o jsonpath='{.spec.minAvailable}')"
[[ "${portal_pdb_min}" == "4" ]] || {
  echo "expected provider-portal PDB minAvailable=4, got ${portal_pdb_min:-missing}" >&2
  exit 1
}
${KUBECTL} get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

echo "flux gitops verification passed"
