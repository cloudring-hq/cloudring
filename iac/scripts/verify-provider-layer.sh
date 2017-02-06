#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DENY_MANIFEST="${DENY_MANIFEST:-${SCRIPT_DIR}/../kubernetes/tests/tenant-deny-loadbalancer.yaml}"
GROUP="${GROUP:-platform.privatecloud.local}"

echo "== nodes =="
sudo k3s kubectl get nodes

echo "== non-running pods =="
sudo k3s kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

echo "== provider api =="
sudo k3s kubectl get "projects.${GROUP}"
sudo k3s kubectl get "virtualmachineclaims.${GROUP}" -A
sudo k3s kubectl get "kubernetesclusterclaims.${GROUP}" -A
sudo k3s kubectl get "capacitycells.${GROUP}"
sudo k3s kubectl get "productplans.${GROUP}" --ignore-not-found
sudo k3s kubectl get "images.${GROUP}"
sudo k3s kubectl -n tenant-a get "subscriptions.${GROUP}","orders.${GROUP}","volumes.${GROUP}","networks.${GROUP}","firewallrules.${GROUP}","backupplans.${GROUP}","restorerequests.${GROUP}","accessgrants.${GROUP}"
if sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" demo-cluster >/dev/null 2>&1; then
  demo_endpoint_reachable="$(
    sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" demo-cluster \
      -o jsonpath='{.status.endpointReachable}'
  )"
  demo_condition="$(
    sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" demo-cluster \
      -o jsonpath='{.status.conditions[?(@.type=="EndpointReachable")].status}'
  )"
  if [[ "${demo_endpoint_reachable}" != "true" || "${demo_condition}" != "True" ]]; then
    echo "expected demo-cluster endpointReachable=true and EndpointReachable=True, got ${demo_endpoint_reachable}/${demo_condition}" >&2
    exit 1
  fi
fi
if sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" routable-cluster >/dev/null 2>&1; then
  routable_phase="$(
    sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" routable-cluster \
      -o jsonpath='{.status.phase}'
  )"
  routable_endpoint="$(
    sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" routable-cluster \
      -o jsonpath='{.status.apiEndpoint}'
  )"
  routable_endpoint_reachable="$(
    sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" routable-cluster \
      -o jsonpath='{.status.endpointReachable}'
  )"
  if [[ "${routable_phase}" == "Degraded" && ( -n "${routable_endpoint}" || "${routable_endpoint_reachable}" != "false" ) ]]; then
    echo "expected degraded routable-cluster to suppress apiEndpoint and report endpointReachable=false, got endpoint=${routable_endpoint:-<none>} reachable=${routable_endpoint_reachable}" >&2
    exit 1
  fi
fi

check_tenant_api_gateway() {
  local tenant_namespace="$1"
  local claim_name="$2"
  local cluster_name="claim-${claim_name}"
  local proxy_namespace="${TENANT_API_PROXY_NAMESPACE:-capk-system}"
  local proxy_name="${tenant_namespace}-${cluster_name}-api"

  if ! sudo k3s kubectl -n "${proxy_namespace}" get svc "${proxy_name}" >/dev/null 2>&1; then
    echo "expected tenant API gateway service ${proxy_namespace}/${proxy_name}" >&2
    exit 1
  fi

  local external_traffic_policy
  external_traffic_policy="$(
    sudo k3s kubectl -n "${proxy_namespace}" get svc "${proxy_name}" \
      -o jsonpath='{.spec.externalTrafficPolicy}'
  )"
  if [[ "${external_traffic_policy}" != "Cluster" ]]; then
    echo "expected ${proxy_namespace}/${proxy_name} externalTrafficPolicy=Cluster, got ${external_traffic_policy:-<empty>}" >&2
    exit 1
  fi

  local pdb_min_available pdb_app_label pdb_current_healthy pdb_desired_healthy
  if ! sudo k3s kubectl -n "${proxy_namespace}" get pdb "${proxy_name}" >/dev/null 2>&1; then
    echo "expected tenant API gateway PDB ${proxy_namespace}/${proxy_name}" >&2
    exit 1
  fi
  pdb_min_available="$(
    sudo k3s kubectl -n "${proxy_namespace}" get pdb "${proxy_name}" \
      -o jsonpath='{.spec.minAvailable}'
  )"
  pdb_app_label="$(
    sudo k3s kubectl -n "${proxy_namespace}" get pdb "${proxy_name}" \
      -o jsonpath='{.spec.selector.matchLabels.app}'
  )"
  pdb_current_healthy="$(
    sudo k3s kubectl -n "${proxy_namespace}" get pdb "${proxy_name}" \
      -o jsonpath='{.status.currentHealthy}'
  )"
  pdb_desired_healthy="$(
    sudo k3s kubectl -n "${proxy_namespace}" get pdb "${proxy_name}" \
      -o jsonpath='{.status.desiredHealthy}'
  )"
  if [[ "${pdb_min_available}" != "1" || "${pdb_app_label}" != "tenant-api-proxy" ]]; then
    echo "expected ${proxy_namespace}/${proxy_name} PDB minAvailable=1 selecting tenant-api-proxy, got minAvailable=${pdb_min_available:-<empty>} app=${pdb_app_label:-<empty>}" >&2
    exit 1
  fi
  if [[ "${pdb_desired_healthy:-0}" -lt 1 || "${pdb_current_healthy:-0}" -lt 1 ]]; then
    echo "expected ${proxy_namespace}/${proxy_name} PDB to cover at least one healthy proxy, got currentHealthy=${pdb_current_healthy:-0} desiredHealthy=${pdb_desired_healthy:-0}" >&2
    exit 1
  fi

  local vmi_nodes
  vmi_nodes="$(
    sudo k3s kubectl -n "${tenant_namespace}" get vmi \
      -l "cluster.x-k8s.io/cluster-name=${cluster_name},cluster.x-k8s.io/role=control-plane" \
      -o jsonpath='{range .items[*]}{.status.nodeName}{"\n"}{end}' | sort -u
  )"
  [[ -n "${vmi_nodes}" ]] || return 0

  local proxy_nodes
  proxy_nodes="$(
    sudo k3s kubectl -n "${proxy_namespace}" get pods \
      -l "app=tenant-api-proxy,platform.privatecloud.local/cluster=${cluster_name},platform.privatecloud.local/tenant-namespace=${tenant_namespace}" \
      -o jsonpath='{range .items[?(@.status.phase=="Running")]}{.spec.nodeName}{"\n"}{end}' | sort -u
  )"
  [[ -n "${proxy_nodes}" ]] || {
    echo "expected tenant API gateway ${proxy_namespace}/${proxy_name} to have running proxy pods" >&2
    exit 1
  }
  while IFS= read -r proxy_node; do
    [[ -n "${proxy_node}" ]] || continue
    if grep -qx "${proxy_node}" <<< "${vmi_nodes}"; then
      echo "expected tenant API gateway ${proxy_namespace}/${proxy_name} to avoid VMI node ${proxy_node}; VMI nodes: ${vmi_nodes:-<none>} proxy nodes: ${proxy_nodes:-<none>}" >&2
      exit 1
    fi
  done <<< "${proxy_nodes}"
}

if sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" demo-cluster >/dev/null 2>&1; then
  check_tenant_api_gateway tenant-a demo-cluster
fi
if sudo k3s kubectl -n tenant-a get "kubernetesclusterclaims.${GROUP}" routable-cluster >/dev/null 2>&1; then
  check_tenant_api_gateway tenant-a routable-cluster
fi

echo "== provider-controller runtime =="
base_replicas="$(
  sudo k3s kubectl -n platform-system get deploy provider-controller \
    -o jsonpath='{.spec.replicas}' 2>/dev/null || true
)"
shard_deployments="$(
  sudo k3s kubectl -n platform-system get deploy \
    -l app.kubernetes.io/name=provider-controller,app.kubernetes.io/component=controller \
    -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null || true
)"

if [[ -n "${shard_deployments}" ]]; then
  controller_mode="sharded"
  if [[ "${base_replicas:-0}" -gt 0 ]]; then
    echo "base provider-controller replicas=${base_replicas} while shard deployments exist; cutover must not run both topologies" >&2
    exit 1
  fi
else
  controller_mode="single"
fi
echo "provider-controller mode=${controller_mode}"

controller_deployments=()
expected_leaders=1
expected_shard_total=1
global_shard_index=0
if [[ "${controller_mode}" == "single" ]]; then
  controller_deployments=(provider-controller)
else
  while IFS= read -r deployment; do
    [[ -n "${deployment}" ]] && controller_deployments+=("${deployment}")
  done <<< "${shard_deployments}"
  expected_leaders="${#controller_deployments[@]}"
  first_deployment="${controller_deployments[0]}"
  expected_shard_total="$(
    sudo k3s kubectl -n platform-system get deploy "${first_deployment}" \
      -o jsonpath='{.spec.template.spec.containers[?(@.name=="controller")].env[?(@.name=="CONTROLLER_SHARD_TOTAL")].value}'
  )"
  global_shard_index="$(
    sudo k3s kubectl -n platform-system get deploy "${first_deployment}" \
      -o jsonpath='{.spec.template.spec.containers[?(@.name=="controller")].env[?(@.name=="CONTROLLER_GLOBAL_SHARD_INDEX")].value}'
  )"
  [[ "${expected_leaders}" -eq "${expected_shard_total}" ]] || {
    echo "expected one active deployment per shard, got deployments=${expected_leaders} shardTotal=${expected_shard_total}" >&2
    exit 1
  }
fi

controller_nodes=0
lease_names=()
for deployment in "${controller_deployments[@]}"; do
  sudo k3s kubectl -n platform-system rollout status "deploy/${deployment}" --timeout=120s
  available_replicas="$(
    sudo k3s kubectl -n platform-system get deploy "${deployment}" \
      -o jsonpath='{.status.availableReplicas}'
  )"
  if [[ "${available_replicas:-0}" -lt 2 ]]; then
    echo "expected at least 2 available replicas for ${deployment}, got ${available_replicas:-0}" >&2
    exit 1
  fi
  min_available="$(
    sudo k3s kubectl -n platform-system get pdb "${deployment}" \
      -o jsonpath='{.spec.minAvailable}'
  )"
  if [[ "${min_available}" != "2" ]]; then
    echo "expected ${deployment} PDB minAvailable=2, got ${min_available}" >&2
    exit 1
  fi
  controller_image="$(
    sudo k3s kubectl -n platform-system get deploy "${deployment}" \
      -o jsonpath='{.spec.template.spec.containers[?(@.name=="controller")].image}'
  )"
  controller_command="$(
    sudo k3s kubectl -n platform-system get deploy "${deployment}" \
      -o jsonpath='{.spec.template.spec.containers[?(@.name=="controller")].command}' 2>/dev/null || true
  )"
  [[ "${controller_image}" == "localhost/platform-provider-controller:dev" ]] || {
    echo "expected ${deployment} to use local immutable runtime image, got ${controller_image}" >&2
    exit 1
  }
  if grep -q "pip install" <<< "${controller_command}"; then
    echo "${deployment} still installs Python dependencies at pod startup" >&2
    exit 1
  fi
  lease_name="$(
    sudo k3s kubectl -n platform-system get deploy "${deployment}" \
      -o jsonpath='{.spec.template.spec.containers[?(@.name=="controller")].env[?(@.name=="LEADER_ELECTION_LEASE_NAME")].value}'
  )"
  lease_names+=("${lease_name:-${deployment}}")
done

controller_nodes="$(
  sudo k3s kubectl -n platform-system get pods -l app=provider-controller \
    --field-selector=status.phase=Running \
    -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | sort -u | wc -l
)"
if [[ "${controller_nodes}" -lt 2 ]]; then
  echo "expected provider-controller pods on at least 2 nodes, got ${controller_nodes}" >&2
  exit 1
fi

for lease_name in "${lease_names[@]}"; do
  leader_holder=""
  for _ in $(seq 1 45); do
    candidate="$(sudo k3s kubectl -n platform-system get lease "${lease_name}" -o jsonpath='{.spec.holderIdentity}' 2>/dev/null || true)"
    if [[ -n "${candidate}" ]] && sudo k3s kubectl -n platform-system get pod "${candidate}" >/dev/null 2>&1; then
      leader_holder="${candidate}"
      break
    fi
    sleep 2
  done
  lease_transitions="$(sudo k3s kubectl -n platform-system get lease "${lease_name}" -o jsonpath='{.spec.leaseTransitions}')"
  [[ -n "${leader_holder}" ]] || { echo "expected ${lease_name} leader lease holder" >&2; exit 1; }
  [[ -n "${lease_transitions}" ]] || { echo "expected ${lease_name} lease transition count" >&2; exit 1; }
  echo "${lease_name} leader=${leader_holder} leaseTransitions=${lease_transitions}"
done

echo "== provider-controller metrics =="
if [[ "${controller_mode}" == "single" ]]; then
  sudo k3s kubectl -n platform-system get svc provider-controller-metrics
else
  for deployment in "${controller_deployments[@]}"; do
    sudo k3s kubectl -n platform-system get svc "${deployment}-metrics"
  done
fi
echo "provider-controller runtime image=localhost/platform-provider-controller:dev"
metrics_pods="$(
  sudo k3s kubectl -n platform-system get pods -l app=provider-controller \
    --field-selector=status.phase=Running \
    -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
)"
metrics_leaders=0
metrics_success=0
for pod in ${metrics_pods}; do
  metrics=""
  for _ in $(seq 1 20); do
    metrics="$(
      sudo k3s kubectl -n platform-system exec "${pod}" -- \
        python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/metrics", timeout=2).read().decode())' 2>/dev/null || true
    )"
    grep -q "provider_controller_reconcile_total" <<< "${metrics}" && break
    sleep 3
  done
  grep -q "provider_controller_reconcile_total" <<< "${metrics}" || {
    echo "expected provider-controller metrics from pod ${pod}" >&2
    exit 1
  }
  grep -q "provider_controller_shard_info" <<< "${metrics}" || {
    echo "expected provider-controller shard metric from pod ${pod}" >&2
    exit 1
  }
  if [[ "${controller_mode}" == "single" ]]; then
    grep -q 'shard_index="0",shard_total="1",owns_global="1"' <<< "${metrics}" || {
      echo "expected lab shard labels on provider-controller pod ${pod}" >&2
      exit 1
    }
  else
    grep -q "shard_total=\"${expected_shard_total}\"" <<< "${metrics}" || {
      echo "expected sharded labels with shard_total=${expected_shard_total} on ${pod}" >&2
      exit 1
    }
  fi
  if grep -Eq 'provider_controller_leader\{identity="[^"]+"\} 1' <<< "${metrics}"; then
    metrics_leaders=$((metrics_leaders + 1))
  fi
  success_count="$(
    awk -F'[ }]' '/provider_controller_reconcile_total\{result="success"\}/ {print int($NF)}' <<< "${metrics}" | tail -n1
  )"
  if [[ "${success_count:-0}" -gt 0 ]]; then
    metrics_success=$((metrics_success + success_count))
  fi
done
[[ "${metrics_leaders}" -ge "${expected_leaders}" ]] || { echo "expected metrics to expose ${expected_leaders} active provider-controller leaders, got ${metrics_leaders}" >&2; exit 1; }
[[ "${metrics_success}" -gt 0 ]] || { echo "expected metrics to expose successful reconcile samples" >&2; exit 1; }
echo "provider-controller metrics leaders=${metrics_leaders} successfulReconciles=${metrics_success}"

if sudo k3s kubectl get "projects.${GROUP}" tenant-c >/dev/null 2>&1; then
  sudo k3s kubectl get "projects.${GROUP}" tenant-c -o jsonpath='tenant-c project phase={.status.phase} namespaces={.status.namespaces}{"\n"}'
fi

if sudo k3s kubectl -n tenant-c get "virtualmachineclaims.${GROUP}" smoke-vm >/dev/null 2>&1; then
  sudo k3s kubectl -n tenant-c get "virtualmachineclaims.${GROUP}" smoke-vm -o jsonpath='tenant-c smoke-vm phase={.status.phase} vm={.status.vmName} ip={.status.ip}{"\n"}'
  sudo k3s kubectl -n tenant-c get vm claim-smoke-vm
fi

echo "== policy =="
sudo k3s kubectl get clusterpolicy tenant-guardrails
sudo k3s kubectl get flowschema platform-service-accounts platform-admins tenant-bulk-list-watch tenant-groups
sudo k3s kubectl get prioritylevelconfiguration platform-control tenant-limited tenant-bulk-low
sudo k3s kubectl -n tenant-a get networkpolicy default-deny
sudo k3s kubectl -n tenant-c get networkpolicy default-deny
sudo k3s kubectl -n tenant-a get networkpolicy allow-cdi-importer-egress
default_deny_types="$(
  sudo k3s kubectl -n tenant-a get networkpolicy default-deny \
    -o jsonpath='{.spec.policyTypes[*]}'
)"
if [[ "${default_deny_types}" != *"Ingress"* || "${default_deny_types}" != *"Egress"* ]]; then
  echo "expected tenant-a default-deny to cover Ingress and Egress, got ${default_deny_types}" >&2
  exit 1
fi
cdi_importer_selector="$(
  sudo k3s kubectl -n tenant-a get networkpolicy allow-cdi-importer-egress \
    -o jsonpath='{.spec.podSelector.matchLabels.cdi\.kubevirt\.io}'
)"
if [[ "${cdi_importer_selector}" != "importer" ]]; then
  echo "expected allow-cdi-importer-egress to select cdi.kubevirt.io=importer, got ${cdi_importer_selector}" >&2
  exit 1
fi
tenant_bulk_priority="$(
  sudo k3s kubectl get flowschema tenant-bulk-list-watch \
    -o jsonpath='{.spec.priorityLevelConfiguration.name}'
)"
tenant_interactive_distinguisher="$(
  sudo k3s kubectl get flowschema tenant-groups \
    -o jsonpath='{.spec.distinguisherMethod.type}'
)"
platform_priority_shares="$(
  sudo k3s kubectl get prioritylevelconfiguration platform-control \
    -o jsonpath='{.spec.limited.nominalConcurrencyShares}'
)"
tenant_bulk_shares="$(
  sudo k3s kubectl get prioritylevelconfiguration tenant-bulk-low \
    -o jsonpath='{.spec.limited.nominalConcurrencyShares}'
)"
[[ "${tenant_bulk_priority}" == "tenant-bulk-low" ]] || {
  echo "expected tenant-bulk-list-watch to use tenant-bulk-low, got ${tenant_bulk_priority}" >&2
  exit 1
}
[[ "${tenant_interactive_distinguisher}" == "ByNamespace" ]] || {
  echo "expected tenant-groups APF distinguisher ByNamespace, got ${tenant_interactive_distinguisher}" >&2
  exit 1
}
[[ "${platform_priority_shares}" -gt "${tenant_bulk_shares}" ]] || {
  echo "expected platform-control APF shares > tenant-bulk-low, got ${platform_priority_shares}/${tenant_bulk_shares}" >&2
  exit 1
}

echo "== kyverno deny tenant load balancer =="
sudo k3s kubectl get ns tenant-a >/dev/null
[[ -f "${DENY_MANIFEST}" ]] || { echo "missing deny manifest: ${DENY_MANIFEST}" >&2; exit 1; }
set +e
deny_output="$(sudo k3s kubectl apply --dry-run=server -f "${DENY_MANIFEST}" 2>&1)"
code="$?"
set -e
if [[ "${code}" -eq 0 ]]; then
  echo "expected tenant LoadBalancer admission denial, got success" >&2
  exit 1
fi
if ! grep -q "tenant-guardrails" <<< "${deny_output}"; then
  echo "expected Kyverno tenant-guardrails denial, got:" >&2
  echo "${deny_output}" >&2
  exit 1
fi
echo "tenant LoadBalancer rejected as expected"
