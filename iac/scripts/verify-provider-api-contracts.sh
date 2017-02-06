#!/usr/bin/env bash
set -euo pipefail

KUBECTL_BASE="${KUBECTL:-sudo k3s kubectl}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-15s}"
KUBECTL="${KUBECTL_BASE} --request-timeout=${REQUEST_TIMEOUT}"
TENANT_USER="${TENANT_USER:-alice}"
TENANT_GROUP="${TENANT_GROUP:-platform:tenant-a:admins}"
CATALOG_GROUP="${CATALOG_GROUP:-platform:tenants}"
TENANT_NAMESPACE="${TENANT_NAMESPACE:-tenant-a}"
OTHER_NAMESPACE="${OTHER_NAMESPACE:-tenant-b}"
TENANT_CLUSTER_CLAIM="${TENANT_CLUSTER_CLAIM:-routable-cluster}"
ORDER_PROBE_NAME="${ORDER_PROBE_NAME:-contract-missing-plan-order}"
ORDER_LIFECYCLE_PLAN="${ORDER_LIFECYCLE_PLAN:-contract-lifecycle-plan}"
ORDER_LIFECYCLE_SUBSCRIPTION="${ORDER_LIFECYCLE_SUBSCRIPTION:-contract-lifecycle-subscription}"
ORDER_CHANGE_NAME="${ORDER_CHANGE_NAME:-contract-change-subscription-order}"
ORDER_SUSPEND_NAME="${ORDER_SUSPEND_NAME:-contract-suspend-subscription-order}"
ORDER_RESUME_NAME="${ORDER_RESUME_NAME:-contract-resume-subscription-order}"
ORDER_RENEW_NAME="${ORDER_RENEW_NAME:-contract-renew-subscription-order}"
ORDER_CANCEL_NAME="${ORDER_CANCEL_NAME:-contract-cancel-subscription-order}"
original_project_quotas=""

expect_can_i() {
  local expected="$1"
  shift
  local output
  output="$(${KUBECTL} auth can-i "$@" --as="${TENANT_USER}" --as-group="${TENANT_GROUP}" --as-group="${CATALOG_GROUP}" 2>/dev/null || true)"
  if [[ "${output}" != "${expected}" ]]; then
    echo "expected auth can-i $* => ${expected}, got ${output}" >&2
    exit 1
  fi
  echo "auth can-i $* => ${output}"
}

wait_admission_journal() {
  local kind="$1"
  local namespace="$2"
  local name="$3"
  local decision="$4"
  local reason="$5"
  local uid="${6:-}"
  local found=""
  for _ in $(seq 1 40); do
    found="$(
      ${KUBECTL} get admissionjournals -o json 2>/dev/null | python3 -c '
import json
import sys

kind, namespace, name, decision, reason, uid = sys.argv[1:7]
try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError:
    payload = {"items": []}
for item in payload.get("items", []):
    spec = item.get("spec", {})
    claim = spec.get("claimRef", {})
    if claim.get("kind") != kind:
        continue
    if claim.get("namespace") != namespace or claim.get("name") != name:
        continue
    if uid and claim.get("uid") != uid:
        continue
    if spec.get("decision") != decision:
        continue
    if reason and spec.get("reason") != reason:
        continue
    print(item.get("metadata", {}).get("name", "found"))
    break
' "${kind}" "${namespace}" "${name}" "${decision}" "${reason}" "${uid}" || true
    )"
    if [[ -n "${found}" ]]; then
      echo "admission journal ${found} ${kind} ${namespace}/${name} decision=${decision} reason=${reason}"
      return 0
    fi
    sleep 3
  done
  echo "expected AdmissionJournal for ${kind} ${namespace}/${name} decision=${decision} reason=${reason}" >&2
  ${KUBECTL} get admissionjournals -o wide >&2 || true
  return 1
}

wait_absent() {
  local namespace="$1"
  local resource="$2"
  local name="$3"
  local label="$4"
  for _ in $(seq 1 30); do
    if [[ "${namespace}" == "-" ]]; then
      if ! ${KUBECTL} get "${resource}" "${name}" >/dev/null 2>&1; then
        echo "${label} absent"
        return 0
      fi
    else
      if ! ${KUBECTL} -n "${namespace}" get "${resource}" "${name}" >/dev/null 2>&1; then
        echo "${label} absent"
        return 0
      fi
    fi
    sleep 2
  done
  echo "expected ${label} to be absent after cleanup" >&2
  return 1
}

wait_project_quota_usage() {
  local project="$1"
  local usage=""
  for _ in $(seq 1 30); do
    usage="$(${KUBECTL} get project "${project}" -o jsonpath='{.status.quotaUsage.cpu} {.status.quotaUsage.memory} {.status.quotaUsage.vms} {.status.quotaUsage.tenantClusters}' 2>/dev/null || true)"
    if [[ "${usage}" =~ [^[:space:]] ]]; then
      echo "${usage}"
      return 0
    fi
    sleep 2
  done
  echo "expected ${project} project quotaUsage status" >&2
  return 1
}

cleanup_capacity_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim capacity-too-large --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm claim-capacity-too-large --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation vmc-${TENANT_NAMESPACE}-capacity-too-large --ignore-not-found >/dev/null 2>&1 || true
}

cleanup_image_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim image-not-in-catalog --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm claim-image-not-in-catalog --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation vmc-${TENANT_NAMESPACE}-image-not-in-catalog --ignore-not-found >/dev/null 2>&1 || true
}

cleanup_placement_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim placement-auto-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim placement-zone-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachineclaim placement-impossible-zone-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubernetesclusterclaim placement-impossible-zone-cluster --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm claim-placement-auto-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm claim-placement-zone-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm claim-placement-impossible-zone-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete cluster claim-placement-impossible-zone-cluster --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubevirtcluster claim-placement-impossible-zone-cluster --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubeadmcontrolplane claim-placement-impossible-zone-cluster-control-plane --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubevirtmachinetemplate claim-placement-impossible-zone-cluster-control-plane --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete machinedeployment claim-placement-impossible-zone-cluster-default --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation vmc-${TENANT_NAMESPACE}-placement-auto-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation vmc-${TENANT_NAMESPACE}-placement-zone-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation vmc-${TENANT_NAMESPACE}-placement-impossible-zone-vm --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation kcc-${TENANT_NAMESPACE}-placement-impossible-zone-cluster --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacitycell aaa-empty-cell --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacitycell zzz-zone-b-cell --ignore-not-found >/dev/null 2>&1 || true
}

wait_placement_probe_absent() {
  wait_absent "${TENANT_NAMESPACE}" virtualmachineclaim placement-auto-vm "placement-auto-vm claim"
  wait_absent "${TENANT_NAMESPACE}" virtualmachineclaim placement-zone-vm "placement-zone-vm claim"
  wait_absent "${TENANT_NAMESPACE}" virtualmachineclaim placement-impossible-zone-vm "placement-impossible-zone-vm claim"
  wait_absent "${TENANT_NAMESPACE}" kubernetesclusterclaim placement-impossible-zone-cluster "placement-impossible-zone-cluster claim"
  wait_absent "${TENANT_NAMESPACE}" vm claim-placement-auto-vm "placement-auto-vm backing VM"
  wait_absent "${TENANT_NAMESPACE}" vm claim-placement-zone-vm "placement-zone-vm backing VM"
  wait_absent "${TENANT_NAMESPACE}" vm claim-placement-impossible-zone-vm "placement-impossible-zone-vm backing VM"
  wait_absent "${TENANT_NAMESPACE}" cluster claim-placement-impossible-zone-cluster "placement-impossible-zone-cluster CAPI Cluster"
  wait_absent "-" capacityreservation vmc-${TENANT_NAMESPACE}-placement-auto-vm "placement-auto-vm reservation"
  wait_absent "-" capacityreservation vmc-${TENANT_NAMESPACE}-placement-zone-vm "placement-zone-vm reservation"
  wait_absent "-" capacityreservation vmc-${TENANT_NAMESPACE}-placement-impossible-zone-vm "placement-impossible-zone-vm reservation"
  wait_absent "-" capacityreservation kcc-${TENANT_NAMESPACE}-placement-impossible-zone-cluster "placement-impossible-zone-cluster reservation"
  wait_absent "-" capacitycell aaa-empty-cell "aaa-empty-cell capacity cell"
  wait_absent "-" capacitycell zzz-zone-b-cell "legacy zzz-zone-b-cell capacity cell"
}

cleanup_ha_cluster_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubernetesclusterclaim ha-control-plane-too-large --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete cluster claim-ha-control-plane-too-large --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubevirtcluster claim-ha-control-plane-too-large --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubeadmcontrolplane claim-ha-control-plane-too-large-control-plane --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubevirtmachinetemplate claim-ha-control-plane-too-large-control-plane --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete machinedeployment claim-ha-control-plane-too-large-default --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation kcc-${TENANT_NAMESPACE}-ha-control-plane-too-large --ignore-not-found >/dev/null 2>&1 || true
}

cleanup_restore_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete restorerequest contract-restore --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete virtualmachinerestore restore-contract-restore --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete vm contract-restored-vm --ignore-not-found >/dev/null 2>&1 || true
}

cleanup_order_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete orders.platform.privatecloud.local "${ORDER_PROBE_NAME}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
}

cleanup_order_lifecycle_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete orders.platform.privatecloud.local "${ORDER_CANCEL_NAME}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete orders.platform.privatecloud.local "${ORDER_RENEW_NAME}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete orders.platform.privatecloud.local "${ORDER_RESUME_NAME}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete orders.platform.privatecloud.local "${ORDER_SUSPEND_NAME}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete orders.platform.privatecloud.local "${ORDER_CHANGE_NAME}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  ${KUBECTL} delete productplans.platform.privatecloud.local "${ORDER_LIFECYCLE_PLAN}" --ignore-not-found --wait=false >/dev/null 2>&1 || true
}

vm_restore_request_label() {
  local vm_name="$1"
  local payload
  payload="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get vm "${vm_name}" -o json 2>/dev/null || true)"
  if [[ -z "${payload}" ]]; then
    echo "missing"
    return
  fi
  printf '%s' "${payload}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("metadata", {}).get("labels", {}).get("platform.privatecloud.local/restore-request", "missing"))'
}

cleanup_kcc_quota_probe() {
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubernetesclusterclaim project-quota-too-many-clusters --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete cluster claim-project-quota-too-many-clusters --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubevirtcluster claim-project-quota-too-many-clusters --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubeadmcontrolplane claim-project-quota-too-many-clusters-control-plane --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete kubevirtmachinetemplate claim-project-quota-too-many-clusters-control-plane --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" delete machinedeployment claim-project-quota-too-many-clusters-default --ignore-not-found >/dev/null 2>&1 || true
  ${KUBECTL} delete capacityreservation kcc-${TENANT_NAMESPACE}-project-quota-too-many-clusters --ignore-not-found >/dev/null 2>&1 || true
}

restore_project_quota() {
  if [[ -n "${original_project_quotas}" ]]; then
    ${KUBECTL} patch project "${TENANT_NAMESPACE}" --type merge \
      -p "{\"spec\":{\"quotas\":${original_project_quotas}}}" >/dev/null
  fi
}

cleanup_all() {
  cleanup_capacity_probe >/dev/null 2>&1 || true
  cleanup_image_probe >/dev/null 2>&1 || true
  cleanup_placement_probe >/dev/null 2>&1 || true
  cleanup_ha_cluster_probe >/dev/null 2>&1 || true
  cleanup_restore_probe >/dev/null 2>&1 || true
  cleanup_order_probe >/dev/null 2>&1 || true
  cleanup_order_lifecycle_probe >/dev/null 2>&1 || true
  cleanup_kcc_quota_probe >/dev/null 2>&1 || true
  restore_project_quota >/dev/null 2>&1 || true
}
trap cleanup_all EXIT

echo "== provider API CRDs =="
${KUBECTL} get crd \
  projects.platform.privatecloud.local \
  capacitycells.platform.privatecloud.local \
  capacityreservations.platform.privatecloud.local \
  admissionjournals.platform.privatecloud.local \
  productplans.platform.privatecloud.local \
  subscriptions.platform.privatecloud.local \
  orders.platform.privatecloud.local \
  virtualmachineclaims.platform.privatecloud.local \
  kubernetesclusterclaims.platform.privatecloud.local \
  images.platform.privatecloud.local \
  volumes.platform.privatecloud.local \
  networks.platform.privatecloud.local \
  firewallrules.platform.privatecloud.local \
  backupplans.platform.privatecloud.local \
  restorerequests.platform.privatecloud.local \
  accessgrants.platform.privatecloud.local \
  selfserviceauditevents.platform.privatecloud.local

echo "== provider API example objects =="
${KUBECTL} get projects
${KUBECTL} get capacitycells
${KUBECTL} get capacityreservations
${KUBECTL} get admissionjournals --ignore-not-found
${KUBECTL} get productplans --ignore-not-found
${KUBECTL} get images
${KUBECTL} -n "${TENANT_NAMESPACE}" get \
  subscriptions.platform.privatecloud.local,orders.platform.privatecloud.local,virtualmachineclaims,kubernetesclusterclaims,volumes.platform.privatecloud.local,networks,firewallrules,backupplans,restorerequests,accessgrants
${KUBECTL} -n "${TENANT_NAMESPACE}" get selfserviceauditevents --ignore-not-found

for _ in $(seq 1 30); do
  cell_reserved_cpu="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.reserved.cpu}' 2>/dev/null || true)"
  cell_available_cpu="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.available.cpu}' 2>/dev/null || true)"
  [[ -n "${cell_reserved_cpu}" && -n "${cell_available_cpu}" ]] && break
  sleep 5
done

ubuntu_image_phase="$(${KUBECTL} get image ubuntu-2404-kubevirt -o jsonpath='{.status.phase}')"
cirros_image_phase="$(${KUBECTL} get image cirros -o jsonpath='{.status.phase}')"
cell_phase="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.phase}')"
cell_ready_nodes="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.readyNodeCount}')"
cell_allocatable_cpu="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.allocatable.cpu}')"
cell_allocatable_memory="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.allocatable.memory}')"
cell_reserved_cpu="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.reserved.cpu}')"
cell_reserved_memory="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.reserved.memory}')"
cell_reserved_claims="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.reserved.claims}')"
cell_available_cpu="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.available.cpu}')"
cell_available_memory="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.available.memory}')"
volume_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get volumes.platform.privatecloud.local demo-data -o jsonpath='{.status.phase}')"
network_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get networks.platform.privatecloud.local demo-private -o jsonpath='{.status.phase}')"
firewall_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get firewallrules.platform.privatecloud.local allow-tenant-api -o jsonpath='{.status.phase}')"
for _ in $(seq 1 60); do
  backup_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get backupplans.platform.privatecloud.local demo-daily -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  backup_recovery_points="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get backupplans.platform.privatecloud.local demo-daily -o jsonpath='{.status.recoveryPoints}' 2>/dev/null || true)"
  backup_snapshot_ready="$(
    ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachinesnapshots.snapshot.kubevirt.io \
      -l platform.privatecloud.local/backupplan=demo-daily -o json 2>/dev/null \
      | python3 -c 'import json,sys; data=json.load(sys.stdin); print(sum(1 for x in data.get("items", []) if x.get("status", {}).get("readyToUse") is True))' \
      || true
  )"
  if [[ "${backup_phase}" == "Protected" && "${backup_recovery_points:-0}" -ge 1 && "${backup_snapshot_ready:-0}" -ge 1 ]]; then
    break
  fi
  sleep 5
done
access_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get accessgrants.platform.privatecloud.local tenant-a-admins-kubeconfig -o jsonpath='{.status.phase}')"
for _ in $(seq 1 60); do
  product_plan_phase="$(${KUBECTL} get productplan vm-basic -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  subscription_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscription tenant-a-vm-basic -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  order_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local tenant-a-vm-basic-order -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  ordered_subscription_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local tenant-a-vm-basic-ordered -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  [[ "${product_plan_phase}" == "Published" && "${subscription_phase}" == "Active" && "${order_phase}" == "Succeeded" && "${ordered_subscription_phase}" == "Active" ]] && break
  sleep 5
done
vm_admission="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim demo-vm -o jsonpath='{.status.admission.phase}')"
vm_capacity_cell="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim demo-vm -o jsonpath='{.status.admission.capacityCell}')"
kcc_admission="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${TENANT_CLUSTER_CLAIM}" -o jsonpath='{.status.admission.phase}')"
kcc_capacity_cell="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${TENANT_CLUSTER_CLAIM}" -o jsonpath='{.status.admission.capacityCell}')"
kcc_effective_workers="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${TENANT_CLUSTER_CLAIM}" -o jsonpath='{.status.admission.effectiveWorkerReplicas[0].admitted}')"
[[ "${ubuntu_image_phase}" == "Ready" ]] || { echo "expected ubuntu image Ready, got ${ubuntu_image_phase}" >&2; exit 1; }
[[ "${cirros_image_phase}" == "Ready" ]] || { echo "expected cirros image Ready, got ${cirros_image_phase}" >&2; exit 1; }
[[ "${cell_phase}" == "Ready" ]] || { echo "expected capacity cell Ready, got ${cell_phase}" >&2; exit 1; }
[[ "${cell_ready_nodes}" -ge 3 ]] || { echo "expected at least 3 ready nodes in capacity cell, got ${cell_ready_nodes}" >&2; exit 1; }
read -r expected_reserved_cpu expected_reserved_memory expected_reserved_claims < <(
  ${KUBECTL} get virtualmachineclaims,kubernetesclusterclaims -A -o json | python3 -c '
import json
import sys

def cpu_to_m(value):
    text = str(value or "0")
    return int(text[:-1]) if text.endswith("m") else int(float(text) * 1000)

def memory_to_mi(value):
    text = str(value or "0")
    units = {
        "Ki": 1 / 1024,
        "Mi": 1,
        "Gi": 1024,
        "Ti": 1024 * 1024,
        "K": 1 / 1000,
        "M": 1000 / 1024,
        "G": 1000 * 1000 / 1024,
        "T": 1000 * 1000 * 1000 / 1024,
    }
    for suffix, multiplier in units.items():
        if text.endswith(suffix):
            return int(float(text[:-len(suffix)]) * multiplier)
    return int(float(text) / (1024 * 1024))

payload = json.load(sys.stdin)
cpu = memory = claims = 0
for item in payload.get("items", []):
    admission = item.get("status", {}).get("admission", {})
    if admission.get("phase") != "Admitted" or admission.get("capacityCell") != "lab-hyperv":
        continue
    resources = admission.get("estimatedResources", {})
    cpu += cpu_to_m(resources.get("cpu", "0"))
    memory += memory_to_mi(resources.get("memory", "0"))
    claims += 1
print(cpu, memory, claims)
'
)
for _ in $(seq 1 30); do
  read -r reservation_cpu reservation_memory reservation_claims reservation_lifecycle_errors < <(
    ${KUBECTL} get capacityreservations -o json | python3 -c '
import json
import sys
from datetime import datetime, timezone

def cpu_to_m(value):
    text = str(value or "0")
    return int(text[:-1]) if text.endswith("m") else int(float(text) * 1000)

def memory_to_mi(value):
    text = str(value or "0")
    units = {
        "Ki": 1 / 1024,
        "Mi": 1,
        "Gi": 1024,
        "Ti": 1024 * 1024,
        "K": 1 / 1000,
        "M": 1000 / 1024,
        "G": 1000 * 1000 / 1024,
        "T": 1000 * 1000 * 1000 / 1024,
    }
    for suffix, multiplier in units.items():
        if text.endswith(suffix):
            return int(float(text[:-len(suffix)]) * multiplier)
    return int(float(text) / (1024 * 1024))

def parse_time(value):
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

payload = json.load(sys.stdin)
cpu = memory = claims = lifecycle_errors = 0
now = datetime.now(timezone.utc)
for item in payload.get("items", []):
    spec = item.get("spec", {})
    status = item.get("status", {})
    if status.get("phase") != "Active" or spec.get("capacityCell") != "lab-hyperv":
        continue
    resources = spec.get("resources", {})
    cpu += cpu_to_m(resources.get("cpu", "0"))
    memory += memory_to_mi(resources.get("memory", "0"))
    claims += 1
    heartbeat = parse_time(status.get("lastHeartbeatTime"))
    expires_at = parse_time(status.get("expiresAt"))
    ttl = int(status.get("reservationTTLSeconds") or 0)
    if not heartbeat or not expires_at or ttl <= 0 or expires_at <= now:
        lifecycle_errors += 1
print(cpu, memory, claims, lifecycle_errors)
'
  )
  if [[ "${reservation_cpu:-0}" -eq "${expected_reserved_cpu}" && "${reservation_memory:-0}" -eq "${expected_reserved_memory}" && "${reservation_claims:-0}" -eq "${expected_reserved_claims}" && "${reservation_lifecycle_errors:-1}" -eq 0 ]]; then
    break
  fi
  sleep 5
done
cell_reserved_cpu="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.reserved.cpu}')"
cell_reserved_memory="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.reserved.memory}')"
cell_reserved_claims="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.reserved.claims}')"
cell_available_cpu="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.available.cpu}')"
cell_available_memory="$(${KUBECTL} get capacitycell lab-hyperv -o jsonpath='{.status.available.memory}')"
expected_available_cpu="$(( ${cell_allocatable_cpu%m} - expected_reserved_cpu ))"
expected_available_memory="$(( ${cell_allocatable_memory%Mi} - expected_reserved_memory ))"
[[ "${reservation_cpu:-0}" -eq "${expected_reserved_cpu}" ]] || { echo "expected active reservation CPU ${expected_reserved_cpu}m, got ${reservation_cpu:-missing}m" >&2; exit 1; }
[[ "${reservation_memory:-0}" -eq "${expected_reserved_memory}" ]] || { echo "expected active reservation memory ${expected_reserved_memory}Mi, got ${reservation_memory:-missing}Mi" >&2; exit 1; }
[[ "${reservation_claims:-0}" -eq "${expected_reserved_claims}" ]] || { echo "expected active reservation claims ${expected_reserved_claims}, got ${reservation_claims:-missing}" >&2; exit 1; }
[[ "${reservation_lifecycle_errors:-1}" -eq 0 ]] || { echo "expected active reservations to have heartbeat, TTL, and future expiresAt; lifecycle_errors=${reservation_lifecycle_errors:-missing}" >&2; exit 1; }
[[ "${cell_reserved_cpu%m}" -eq "${expected_reserved_cpu}" ]] || { echo "expected capacity cell reserved CPU ${expected_reserved_cpu}m, got ${cell_reserved_cpu}" >&2; exit 1; }
[[ "${cell_reserved_memory%Mi}" -eq "${expected_reserved_memory}" ]] || { echo "expected capacity cell reserved memory ${expected_reserved_memory}Mi, got ${cell_reserved_memory}" >&2; exit 1; }
[[ "${cell_reserved_claims}" -eq "${expected_reserved_claims}" ]] || { echo "expected capacity cell reserved claims ${expected_reserved_claims}, got ${cell_reserved_claims}" >&2; exit 1; }
[[ "${cell_available_cpu%m}" -eq "${expected_available_cpu}" ]] || { echo "expected capacity cell available CPU ${expected_available_cpu}m, got ${cell_available_cpu}" >&2; exit 1; }
[[ "${cell_available_memory%Mi}" -eq "${expected_available_memory}" ]] || { echo "expected capacity cell available memory ${expected_available_memory}Mi, got ${cell_available_memory}" >&2; exit 1; }
[[ "${cell_available_cpu%m}" -gt 0 ]] || { echo "expected capacity cell available CPU >0, got ${cell_available_cpu}" >&2; exit 1; }
[[ "${volume_phase}" == "Bound" ]] || { echo "expected volume Bound, got ${volume_phase}" >&2; exit 1; }
[[ "${network_phase}" == "Ready" ]] || { echo "expected network Ready, got ${network_phase}" >&2; exit 1; }
[[ "${firewall_phase}" == "Ready" ]] || { echo "expected firewall Ready, got ${firewall_phase}" >&2; exit 1; }
[[ "${backup_phase}" == "Protected" ]] || { echo "expected backup Protected, got ${backup_phase}" >&2; exit 1; }
[[ "${backup_recovery_points:-0}" -ge 1 ]] || { echo "expected backup recovery points >=1, got ${backup_recovery_points:-missing}" >&2; exit 1; }
[[ "${backup_snapshot_ready:-0}" -ge 1 ]] || { echo "expected at least one ready KubeVirt VM snapshot for backup plan, got ${backup_snapshot_ready:-missing}" >&2; exit 1; }

echo "== VM restore request from recovery point =="
cleanup_restore_probe
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: RestoreRequest
metadata:
  name: contract-restore
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-a
  source:
    backupPlanRef: demo-daily
  target:
    kind: VirtualMachineClaim
    name: contract-restored-vm
    mode: Copy
  approval:
    required: false
YAML
for _ in $(seq 1 60); do
  restore_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get restorerequest contract-restore -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  restore_name="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get restorerequest contract-restore -o jsonpath='{.status.restoreName}' 2>/dev/null || true)"
  restored_vm="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get restorerequest contract-restore -o jsonpath='{.status.restoredVMName}' 2>/dev/null || true)"
  kubevirt_restore_complete="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachinerestore restore-contract-restore -o jsonpath='{.status.complete}' 2>/dev/null || true)"
  restored_vm_label="$(vm_restore_request_label contract-restored-vm)"
  if [[ "${restore_phase}" == "Succeeded" && "${restore_name}" == "restore-contract-restore" && "${restored_vm}" == "contract-restored-vm" && "${kubevirt_restore_complete}" == "true" && "${restored_vm_label}" == "contract-restore" ]]; then
    break
  fi
  sleep 5
done
[[ "${restore_phase}" == "Succeeded" ]] || {
  echo "expected RestoreRequest Succeeded, got phase=${restore_phase:-missing}" >&2
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get restorerequest contract-restore -o yaml >&2 || true
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachinerestore restore-contract-restore -o yaml >&2 || true
  cleanup_restore_probe
  exit 1
}
[[ "${kubevirt_restore_complete}" == "true" ]] || {
  echo "expected KubeVirt restore complete=true, got ${kubevirt_restore_complete:-missing}" >&2
  cleanup_restore_probe
  exit 1
}
[[ "${restored_vm_label}" == "contract-restore" ]] || {
  echo "expected restored VM label restore-request=contract-restore, got ${restored_vm_label:-missing}" >&2
  cleanup_restore_probe
  exit 1
}
echo "RestoreRequest contract-restore completed as KubeVirt restore ${restore_name}"
cleanup_restore_probe

[[ "${access_phase}" == "Ready" ]] || { echo "expected access grant Ready, got ${access_phase}" >&2; exit 1; }
[[ "${product_plan_phase}" == "Published" ]] || { echo "expected ProductPlan vm-basic Published, got ${product_plan_phase:-missing}" >&2; exit 1; }
[[ "${subscription_phase}" == "Active" ]] || { echo "expected Subscription tenant-a-vm-basic Active, got ${subscription_phase:-missing}" >&2; exit 1; }
[[ "${order_phase}" == "Succeeded" ]] || { echo "expected Order tenant-a-vm-basic-order Succeeded, got ${order_phase:-missing}" >&2; exit 1; }
[[ "${ordered_subscription_phase}" == "Active" ]] || { echo "expected ordered Subscription tenant-a-vm-basic-ordered Active, got ${ordered_subscription_phase:-missing}" >&2; exit 1; }
cleanup_order_probe
cleanup_order_lifecycle_probe
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: Order
metadata:
  name: ${ORDER_PROBE_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  action: CreateSubscription
  state: Submitted
  planRef: missing-contract-plan
  subscriptionRef: missing-contract-plan-subscription
  idempotencyKey: ${ORDER_PROBE_NAME}-v1
  requestedBy: contract-verifier
  policy:
    decision: Allowed
  approval:
    required: false
YAML
for _ in $(seq 1 30); do
  order_probe_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_PROBE_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  order_probe_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_PROBE_NAME}" -o jsonpath='{.status.reason}' 2>/dev/null || true)"
  [[ "${order_probe_phase}" == "Rejected" && "${order_probe_reason}" == "ProductPlanNotFound" ]] && break
  sleep 5
done
[[ "${order_probe_phase}" == "Rejected" && "${order_probe_reason}" == "ProductPlanNotFound" ]] || {
  echo "expected missing-plan order to be rejected, got phase=${order_probe_phase:-missing} reason=${order_probe_reason:-missing}" >&2
  ${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_PROBE_NAME}" -o yaml >&2 || true
  cleanup_order_probe
  exit 1
}
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local missing-contract-plan-subscription >/dev/null 2>&1; then
  echo "missing-plan order unexpectedly created a subscription" >&2
  cleanup_order_probe
  exit 1
fi
cleanup_order_probe

echo "== order lifecycle actions =="
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: ProductPlan
metadata:
  name: ${ORDER_LIFECYCLE_PLAN}
spec:
  displayName: Contract Lifecycle Plan
  category: compute
  visibility: public
  lifecycle:
    state: Published
  service:
    kind: VirtualMachineClaim
    serviceClass: tiny-vm
    defaultImage: cirros
    capacityCellSelector:
      region: lab
      site: ws0
      zone: single-host
      storage: longhorn-lab
  quotaProfile:
    cpu: 1000m
    memory: 1Gi
    vms: 1
    volumes: 1
  commercial:
    billingMode: free
    currency: USD
---
apiVersion: platform.privatecloud.local/v1alpha1
kind: Subscription
metadata:
  name: ${ORDER_LIFECYCLE_SUBSCRIPTION}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  planRef: vm-basic
  displayName: Contract lifecycle subscription
  state: Active
  autoRenew: false
  requestedBy: contract-verifier
YAML
for _ in $(seq 1 40); do
  lifecycle_plan_phase="$(${KUBECTL} get productplans.platform.privatecloud.local "${ORDER_LIFECYCLE_PLAN}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  [[ "${lifecycle_plan_phase}" == "Published" && "${lifecycle_subscription_phase}" == "Active" ]] && break
  sleep 3
done
[[ "${lifecycle_plan_phase}" == "Published" ]] || { echo "expected lifecycle ProductPlan Published, got ${lifecycle_plan_phase:-missing}" >&2; cleanup_order_lifecycle_probe; exit 1; }
[[ "${lifecycle_subscription_phase}" == "Active" ]] || { echo "expected lifecycle Subscription Active, got ${lifecycle_subscription_phase:-missing}" >&2; cleanup_order_lifecycle_probe; exit 1; }
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: Order
metadata:
  name: ${ORDER_CHANGE_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  action: ChangeSubscription
  state: Submitted
  planRef: ${ORDER_LIFECYCLE_PLAN}
  subscriptionRef: ${ORDER_LIFECYCLE_SUBSCRIPTION}
  idempotencyKey: ${ORDER_CHANGE_NAME}-v1
  requestedBy: contract-verifier
  policy:
    decision: Allowed
  approval:
    required: false
YAML
for _ in $(seq 1 60); do
  change_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_CHANGE_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_plan_ref="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.spec.planRef}' 2>/dev/null || true)"
  [[ "${change_phase}" == "Succeeded" && "${lifecycle_plan_ref}" == "${ORDER_LIFECYCLE_PLAN}" ]] && break
  sleep 3
done
[[ "${change_phase}" == "Succeeded" && "${lifecycle_plan_ref}" == "${ORDER_LIFECYCLE_PLAN}" ]] || {
  echo "expected change order Succeeded and subscription plan ${ORDER_LIFECYCLE_PLAN}, got phase=${change_phase:-missing} plan=${lifecycle_plan_ref:-missing}" >&2
  cleanup_order_lifecycle_probe
  exit 1
}
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: Order
metadata:
  name: ${ORDER_SUSPEND_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  action: SuspendSubscription
  state: Submitted
  planRef: ${ORDER_LIFECYCLE_PLAN}
  subscriptionRef: ${ORDER_LIFECYCLE_SUBSCRIPTION}
  idempotencyKey: ${ORDER_SUSPEND_NAME}-v1
  requestedBy: contract-verifier
  schedule:
    notBefore: $(date -u -d '+10 minutes' +%Y-%m-%dT%H:%M:%SZ)
  policy:
    decision: Allowed
  approval:
    required: false
YAML
for _ in $(seq 1 60); do
  suspend_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_SUSPEND_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_state="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.spec.state}' 2>/dev/null || true)"
  [[ "${suspend_phase}" == "Scheduled" && "${lifecycle_subscription_phase}" == "Active" && "${lifecycle_subscription_state}" == "Active" ]] && break
  sleep 3
done
[[ "${suspend_phase}" == "Scheduled" && "${lifecycle_subscription_phase}" == "Active" && "${lifecycle_subscription_state}" == "Active" ]] || {
  echo "expected scheduled suspend order to stay Scheduled and subscription Active, got order=${suspend_phase:-missing} phase=${lifecycle_subscription_phase:-missing} state=${lifecycle_subscription_state:-missing}" >&2
  cleanup_order_lifecycle_probe
  exit 1
}
past_not_before="$(date -u -d '-1 minute' +%Y-%m-%dT%H:%M:%SZ)"
${KUBECTL} -n "${TENANT_NAMESPACE}" patch orders.platform.privatecloud.local "${ORDER_SUSPEND_NAME}" --type merge \
  -p "{\"spec\":{\"schedule\":{\"notBefore\":\"${past_not_before}\"}}}" >/dev/null
for _ in $(seq 1 60); do
  suspend_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_SUSPEND_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  suspend_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_SUSPEND_NAME}" -o jsonpath='{.status.reason}' 2>/dev/null || true)"
  lifecycle_subscription_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_state="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.spec.state}' 2>/dev/null || true)"
  [[ "${suspend_phase}" == "Succeeded" && "${suspend_reason}" == "SubscriptionSuspended" && "${lifecycle_subscription_phase}" == "Suspended" && "${lifecycle_subscription_state}" == "Suspended" ]] && break
  sleep 3
done
[[ "${suspend_phase}" == "Succeeded" && "${suspend_reason}" == "SubscriptionSuspended" && "${lifecycle_subscription_phase}" == "Suspended" && "${lifecycle_subscription_state}" == "Suspended" ]] || {
  echo "expected delayed suspend order Succeeded and subscription Suspended after opening window, got order=${suspend_phase:-missing} reason=${suspend_reason:-missing} phase=${lifecycle_subscription_phase:-missing} state=${lifecycle_subscription_state:-missing}" >&2
  cleanup_order_lifecycle_probe
  exit 1
}
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: Order
metadata:
  name: ${ORDER_RESUME_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  action: ResumeSubscription
  state: Submitted
  planRef: ${ORDER_LIFECYCLE_PLAN}
  subscriptionRef: ${ORDER_LIFECYCLE_SUBSCRIPTION}
  idempotencyKey: ${ORDER_RESUME_NAME}-v1
  requestedBy: contract-verifier
  policy:
    decision: Allowed
  approval:
    required: false
YAML
for _ in $(seq 1 60); do
  resume_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_RESUME_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_state="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.spec.state}' 2>/dev/null || true)"
  [[ "${resume_phase}" == "Succeeded" && "${lifecycle_subscription_phase}" == "Active" && "${lifecycle_subscription_state}" == "Active" ]] && break
  sleep 3
done
[[ "${resume_phase}" == "Succeeded" && "${lifecycle_subscription_phase}" == "Active" && "${lifecycle_subscription_state}" == "Active" ]] || {
  echo "expected resume order Succeeded and subscription Active, got order=${resume_phase:-missing} phase=${lifecycle_subscription_phase:-missing} state=${lifecycle_subscription_state:-missing}" >&2
  cleanup_order_lifecycle_probe
  exit 1
}
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: Order
metadata:
  name: ${ORDER_RENEW_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  action: RenewSubscription
  state: Submitted
  planRef: ${ORDER_LIFECYCLE_PLAN}
  subscriptionRef: ${ORDER_LIFECYCLE_SUBSCRIPTION}
  idempotencyKey: ${ORDER_RENEW_NAME}-v1
  requestedBy: contract-verifier
  policy:
    decision: Allowed
  approval:
    required: false
YAML
for _ in $(seq 1 60); do
  renew_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_RENEW_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_auto_renew="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.spec.autoRenew}' 2>/dev/null || true)"
  [[ "${renew_phase}" == "Succeeded" && "${lifecycle_auto_renew}" == "true" ]] && break
  sleep 3
done
[[ "${renew_phase}" == "Succeeded" && "${lifecycle_auto_renew}" == "true" ]] || {
  echo "expected renew order Succeeded and autoRenew=true, got phase=${renew_phase:-missing} autoRenew=${lifecycle_auto_renew:-missing}" >&2
  cleanup_order_lifecycle_probe
  exit 1
}
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: Order
metadata:
  name: ${ORDER_CANCEL_NAME}
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: ${TENANT_NAMESPACE}
  action: CancelSubscription
  state: Submitted
  planRef: ${ORDER_LIFECYCLE_PLAN}
  subscriptionRef: ${ORDER_LIFECYCLE_SUBSCRIPTION}
  idempotencyKey: ${ORDER_CANCEL_NAME}-v1
  requestedBy: contract-verifier
  policy:
    decision: Allowed
  approval:
    required: false
YAML
for _ in $(seq 1 60); do
  cancel_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get orders.platform.privatecloud.local "${ORDER_CANCEL_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  lifecycle_subscription_state="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get subscriptions.platform.privatecloud.local "${ORDER_LIFECYCLE_SUBSCRIPTION}" -o jsonpath='{.spec.state}' 2>/dev/null || true)"
  [[ "${cancel_phase}" == "Succeeded" && "${lifecycle_subscription_phase}" == "Cancelled" && "${lifecycle_subscription_state}" == "Cancelled" ]] && break
  sleep 3
done
[[ "${cancel_phase}" == "Succeeded" && "${lifecycle_subscription_phase}" == "Cancelled" && "${lifecycle_subscription_state}" == "Cancelled" ]] || {
  echo "expected cancel order Succeeded and subscription Cancelled, got order=${cancel_phase:-missing} phase=${lifecycle_subscription_phase:-missing} state=${lifecycle_subscription_state:-missing}" >&2
  cleanup_order_lifecycle_probe
  exit 1
}
cleanup_order_lifecycle_probe
[[ "${vm_admission}" == "Admitted" && "${vm_capacity_cell}" == "lab-hyperv" ]] || { echo "expected demo-vm admitted to lab-hyperv, got phase=${vm_admission} cell=${vm_capacity_cell}" >&2; exit 1; }
[[ "${kcc_admission}" == "Admitted" && "${kcc_capacity_cell}" == "lab-hyperv" ]] || { echo "expected ${TENANT_CLUSTER_CLAIM} admitted to lab-hyperv, got phase=${kcc_admission} cell=${kcc_capacity_cell}" >&2; exit 1; }
[[ "${kcc_effective_workers}" == "0" ]] || { echo "expected ${TENANT_CLUSTER_CLAIM} effective workers 0, got ${kcc_effective_workers}" >&2; exit 1; }
vm_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim demo-vm -o jsonpath='{.metadata.uid}')"
vm_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim demo-vm -o jsonpath='{.status.admission.reason}')"
kcc_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${TENANT_CLUSTER_CLAIM}" -o jsonpath='{.metadata.uid}')"
kcc_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim "${TENANT_CLUSTER_CLAIM}" -o jsonpath='{.status.admission.reason}')"
wait_admission_journal VirtualMachineClaim "${TENANT_NAMESPACE}" demo-vm Admitted "${vm_reason}" "${vm_uid}"
wait_admission_journal KubernetesClusterClaim "${TENANT_NAMESPACE}" "${TENANT_CLUSTER_CLAIM}" Admitted "${kcc_reason}" "${kcc_uid}"
project_quota_usage="$(wait_project_quota_usage tenant-a)"

echo "== tenant cluster project quota rejection =="
cleanup_kcc_quota_probe
original_project_quotas="$(
  ${KUBECTL} get project "${TENANT_NAMESPACE}" -o json | python3 -c '
import json
import sys
print(json.dumps(json.load(sys.stdin)["spec"]["quotas"], separators=(",", ":")))
'
)"
tenant_cluster_quota_patch="$(
  ${KUBECTL} get project "${TENANT_NAMESPACE}" -o json | python3 -c '
import json
import sys
data = json.load(sys.stdin)
quotas = data["spec"]["quotas"]
usage = data.get("status", {}).get("quotaUsage", {})
quotas["tenantClusters"] = int(usage.get("tenantClusters", 0) or 0)
print(json.dumps({"spec": {"quotas": quotas}}, separators=(",", ":")))
'
)"
${KUBECTL} patch project "${TENANT_NAMESPACE}" --type merge -p "${tenant_cluster_quota_patch}" >/dev/null
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: KubernetesClusterClaim
metadata:
  name: project-quota-too-many-clusters
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-a
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
    podCIDR: 10.249.0.0/16
    serviceCIDR: 10.99.0.0/16
    cni: cilium
YAML
kcc_quota_probe_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim project-quota-too-many-clusters -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  kcc_quota_probe_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim project-quota-too-many-clusters -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  kcc_quota_probe_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim project-quota-too-many-clusters -o jsonpath='{.status.admission.reason}' 2>/dev/null || true)"
  [[ "${kcc_quota_probe_phase}" == "Rejected" && "${kcc_quota_probe_reason}" == "ProjectQuotaExceeded" ]] && break
  sleep 5
done
[[ "${kcc_quota_probe_phase}" == "Rejected" && "${kcc_quota_probe_reason}" == "ProjectQuotaExceeded" ]] || {
  echo "expected extra tenant cluster claim to be rejected by project quota, got phase=${kcc_quota_probe_phase:-missing} reason=${kcc_quota_probe_reason:-missing}" >&2
  cleanup_kcc_quota_probe
  exit 1
}
wait_admission_journal KubernetesClusterClaim "${TENANT_NAMESPACE}" project-quota-too-many-clusters Rejected ProjectQuotaExceeded "${kcc_quota_probe_uid}"
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster claim-project-quota-too-many-clusters >/dev/null 2>&1; then
  echo "project-quota tenant cluster probe unexpectedly created backing CAPI Cluster" >&2
  cleanup_kcc_quota_probe
  exit 1
fi
if ${KUBECTL} get capacityreservation kcc-${TENANT_NAMESPACE}-project-quota-too-many-clusters >/dev/null 2>&1; then
  echo "project-quota tenant cluster probe unexpectedly created capacity reservation" >&2
  cleanup_kcc_quota_probe
  exit 1
fi
echo "extra tenant cluster claim rejected by project quota as expected"
cleanup_kcc_quota_probe
restore_project_quota

echo "== capacity admission rejection =="
cleanup_capacity_probe
capacity_probe_cpu="$(( ${cell_available_cpu%m} / 1000 + 1 ))"
cell_allocatable_cpu_cores="$(( ${cell_allocatable_cpu%m} / 1000 ))"
if [[ "${capacity_probe_cpu}" -gt "${cell_allocatable_cpu_cores}" ]]; then
  capacity_probe_cpu="${cell_allocatable_cpu_cores}"
fi
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: capacity-too-large
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-a
  class: custom
  image:
    name: cirros
    source: catalog
  resources:
    cpu: ${capacity_probe_cpu}
    memory: 256Mi
    rootDisk: 1Gi
  placement:
    capacityCell: lab-hyperv
    serviceClass: tiny-vm
  availability:
    runStrategy: Halted
YAML
capacity_probe_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim capacity-too-large -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  capacity_probe_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim capacity-too-large -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  capacity_probe_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim capacity-too-large -o jsonpath='{.status.admission.reason}' 2>/dev/null || true)"
  [[ "${capacity_probe_phase}" == "Rejected" && "${capacity_probe_reason}" == "InsufficientCapacity" ]] && break
  sleep 5
done
[[ "${capacity_probe_phase}" == "Rejected" && "${capacity_probe_reason}" == "InsufficientCapacity" ]] || {
  echo "expected oversized VM claim to be rejected by capacity admission, got phase=${capacity_probe_phase:-missing} reason=${capacity_probe_reason:-missing}" >&2
  cleanup_capacity_probe
  exit 1
}
wait_admission_journal VirtualMachineClaim "${TENANT_NAMESPACE}" capacity-too-large Rejected InsufficientCapacity "${capacity_probe_uid}"
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm claim-capacity-too-large >/dev/null 2>&1; then
  echo "oversized VM claim unexpectedly created backing VM" >&2
  cleanup_capacity_probe
  exit 1
fi
if ${KUBECTL} get capacityreservation vmc-${TENANT_NAMESPACE}-capacity-too-large >/dev/null 2>&1; then
  echo "oversized VM claim unexpectedly created capacity reservation" >&2
  cleanup_capacity_probe
  exit 1
fi
echo "oversized VM claim rejected as expected"
cleanup_capacity_probe

echo "== image catalog admission rejection =="
cleanup_image_probe
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: image-not-in-catalog
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-a
  class: tiny
  image:
    name: definitely-not-in-catalog
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
image_probe_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim image-not-in-catalog -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  image_probe_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim image-not-in-catalog -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  image_probe_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim image-not-in-catalog -o jsonpath='{.status.admission.reason}' 2>/dev/null || true)"
  [[ "${image_probe_phase}" == "Rejected" && "${image_probe_reason}" == "ImageNotFound" ]] && break
  sleep 5
done
[[ "${image_probe_phase}" == "Rejected" && "${image_probe_reason}" == "ImageNotFound" ]] || {
  echo "expected missing catalog image VM claim to be rejected, got phase=${image_probe_phase:-missing} reason=${image_probe_reason:-missing}" >&2
  cleanup_image_probe
  exit 1
}
wait_admission_journal VirtualMachineClaim "${TENANT_NAMESPACE}" image-not-in-catalog Rejected ImageNotFound "${image_probe_uid}"
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm claim-image-not-in-catalog >/dev/null 2>&1; then
  echo "missing-image VM claim unexpectedly created backing VM" >&2
  cleanup_image_probe
  exit 1
fi
if ${KUBECTL} get capacityreservation vmc-${TENANT_NAMESPACE}-image-not-in-catalog >/dev/null 2>&1; then
  echo "missing-image VM claim unexpectedly created capacity reservation" >&2
  cleanup_image_probe
  exit 1
fi
echo "missing catalog image VM claim rejected as expected"
cleanup_image_probe

echo "== multi-cell placement skips NotReady candidates =="
cleanup_placement_probe
wait_placement_probe_absent
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: CapacityCell
metadata:
  name: aaa-empty-cell
spec:
  provider: hyperv
  region: lab
  site: empty
  nodeSelector:
    platform.privatecloud.local/cell: does-not-exist
  failureDomains:
    region: lab
    site: empty
    zone: empty-zone
  serviceClasses:
    - name: tiny-vm
      kind: vm
      default: true
  limits:
    overcommitCPU: "1.0"
YAML
for _ in $(seq 1 30); do
  empty_cell_phase="$(${KUBECTL} get capacitycell aaa-empty-cell -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  [[ -n "${empty_cell_phase}" ]] && break
  sleep 5
done
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: placement-auto-vm
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
    serviceClass: tiny-vm
  availability:
    runStrategy: Halted
YAML
placement_probe_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-auto-vm -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  placement_probe_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-auto-vm -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  placement_probe_cell="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-auto-vm -o jsonpath='{.status.admission.capacityCell}' 2>/dev/null || true)"
  [[ "${placement_probe_phase}" == "Admitted" && "${placement_probe_cell}" == "lab-hyperv" ]] && break
  sleep 5
done
[[ "${placement_probe_phase}" == "Admitted" && "${placement_probe_cell}" == "lab-hyperv" ]] || {
  echo "expected auto placement to skip NotReady aaa-empty-cell and select lab-hyperv, got phase=${placement_probe_phase:-missing} cell=${placement_probe_cell:-missing}" >&2
  cleanup_placement_probe
  exit 1
}
placement_probe_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-auto-vm -o jsonpath='{.status.admission.reason}')"
wait_admission_journal VirtualMachineClaim "${TENANT_NAMESPACE}" placement-auto-vm Admitted "${placement_probe_reason}" "${placement_probe_uid}"
echo "auto placement selected Ready cell ${placement_probe_cell} while aaa-empty-cell phase=${empty_cell_phase:-missing}"
cleanup_placement_probe
wait_placement_probe_absent

echo "== placement failure-domain constraints select matching Ready cells =="
cleanup_placement_probe
wait_placement_probe_absent
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: placement-zone-vm
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
    serviceClass: tiny-vm
    failureDomains:
      zone: single-host
      storage: longhorn-lab
  availability:
    runStrategy: Halted
YAML
placement_zone_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-zone-vm -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  placement_zone_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-zone-vm -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  placement_zone_cell="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-zone-vm -o jsonpath='{.status.admission.capacityCell}' 2>/dev/null || true)"
  [[ "${placement_zone_phase}" == "Admitted" && "${placement_zone_cell}" == "lab-hyperv" ]] && break
  sleep 5
done
[[ "${placement_zone_phase}" == "Admitted" && "${placement_zone_cell}" == "lab-hyperv" ]] || {
  echo "expected failure-domain placement to select lab-hyperv, got phase=${placement_zone_phase:-missing} cell=${placement_zone_cell:-missing}" >&2
  cleanup_placement_probe
  exit 1
}
placement_zone_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-zone-vm -o jsonpath='{.status.admission.reason}')"
wait_admission_journal VirtualMachineClaim "${TENANT_NAMESPACE}" placement-zone-vm Admitted "${placement_zone_reason}" "${placement_zone_uid}"
echo "failure-domain placement selected ${placement_zone_cell}"
cleanup_placement_probe
wait_placement_probe_absent

echo "== placement failure-domain constraints reject impossible zones =="
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: placement-impossible-zone-vm
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
    serviceClass: tiny-vm
    failureDomains:
      zone: impossible-zone
  availability:
    runStrategy: Halted
YAML
placement_impossible_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-impossible-zone-vm -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  placement_impossible_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-impossible-zone-vm -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  placement_impossible_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get virtualmachineclaim placement-impossible-zone-vm -o jsonpath='{.status.admission.reason}' 2>/dev/null || true)"
  [[ "${placement_impossible_phase}" == "Rejected" && "${placement_impossible_reason}" == "FailureDomainNotFound" ]] && break
  sleep 5
done
[[ "${placement_impossible_phase}" == "Rejected" && "${placement_impossible_reason}" == "FailureDomainNotFound" ]] || {
  echo "expected impossible failure-domain placement to be rejected with FailureDomainNotFound, got phase=${placement_impossible_phase:-missing} reason=${placement_impossible_reason:-missing}" >&2
  cleanup_placement_probe
  exit 1
}
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get vm claim-placement-impossible-zone-vm >/dev/null 2>&1; then
  echo "impossible failure-domain placement unexpectedly created VM" >&2
  cleanup_placement_probe
  exit 1
fi
if ${KUBECTL} get capacityreservation vmc-${TENANT_NAMESPACE}-placement-impossible-zone-vm >/dev/null 2>&1; then
  echo "impossible failure-domain placement unexpectedly created capacity reservation" >&2
  cleanup_placement_probe
  exit 1
fi
wait_admission_journal VirtualMachineClaim "${TENANT_NAMESPACE}" placement-impossible-zone-vm Rejected FailureDomainNotFound "${placement_impossible_uid}"
echo "impossible failure-domain placement rejected as expected"
cleanup_placement_probe
wait_placement_probe_absent

echo "== tenant cluster placement failure-domain constraints reject impossible zones =="
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: KubernetesClusterClaim
metadata:
  name: placement-impossible-zone-cluster
  namespace: ${TENANT_NAMESPACE}
spec:
  projectRef: tenant-a
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
    serviceClass: tiny-tenant-kubernetes
    failureDomains:
      zone: impossible-zone
  network:
    podCIDR: 10.247.0.0/16
    serviceCIDR: 10.100.0.0/16
    cni: cilium
YAML
placement_kcc_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim placement-impossible-zone-cluster -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  placement_kcc_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim placement-impossible-zone-cluster -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  placement_kcc_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim placement-impossible-zone-cluster -o jsonpath='{.status.admission.reason}' 2>/dev/null || true)"
  [[ "${placement_kcc_phase}" == "Rejected" && "${placement_kcc_reason}" == "FailureDomainNotFound" ]] && break
  sleep 5
done
[[ "${placement_kcc_phase}" == "Rejected" && "${placement_kcc_reason}" == "FailureDomainNotFound" ]] || {
  echo "expected impossible tenant-cluster failure-domain placement to be rejected with FailureDomainNotFound, got phase=${placement_kcc_phase:-missing} reason=${placement_kcc_reason:-missing}" >&2
  cleanup_placement_probe
  exit 1
}
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster claim-placement-impossible-zone-cluster >/dev/null 2>&1; then
  echo "impossible tenant-cluster failure-domain placement unexpectedly created backing CAPI Cluster" >&2
  cleanup_placement_probe
  exit 1
fi
if ${KUBECTL} get capacityreservation kcc-${TENANT_NAMESPACE}-placement-impossible-zone-cluster >/dev/null 2>&1; then
  echo "impossible tenant-cluster failure-domain placement unexpectedly created capacity reservation" >&2
  cleanup_placement_probe
  exit 1
fi
wait_admission_journal KubernetesClusterClaim "${TENANT_NAMESPACE}" placement-impossible-zone-cluster Rejected FailureDomainNotFound "${placement_kcc_uid}"
echo "impossible tenant-cluster failure-domain placement rejected as expected"
cleanup_placement_probe
wait_placement_probe_absent

echo "== HA tenant cluster admission guardrail =="
cleanup_ha_cluster_probe
cat <<YAML | ${KUBECTL} apply -f -
apiVersion: platform.privatecloud.local/v1alpha1
kind: KubernetesClusterClaim
metadata:
  name: ha-control-plane-too-large
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
    podCIDR: 10.248.0.0/16
    serviceCIDR: 10.98.0.0/16
    cni: cilium
YAML
ha_probe_uid="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim ha-control-plane-too-large -o jsonpath='{.metadata.uid}')"
for _ in $(seq 1 30); do
  ha_probe_phase="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim ha-control-plane-too-large -o jsonpath='{.status.admission.phase}' 2>/dev/null || true)"
  ha_probe_reason="$(${KUBECTL} -n "${TENANT_NAMESPACE}" get kubernetesclusterclaim ha-control-plane-too-large -o jsonpath='{.status.admission.reason}' 2>/dev/null || true)"
  [[ "${ha_probe_phase}" == "Rejected" && "${ha_probe_reason}" == "ControlPlaneReplicaLimitExceeded" ]] && break
  sleep 5
done
[[ "${ha_probe_phase}" == "Rejected" && "${ha_probe_reason}" == "ControlPlaneReplicaLimitExceeded" ]] || {
  echo "expected HA tenant cluster claim to be rejected by current cell CP replica limit, got phase=${ha_probe_phase:-missing} reason=${ha_probe_reason:-missing}" >&2
  cleanup_ha_cluster_probe
  exit 1
}
wait_admission_journal KubernetesClusterClaim "${TENANT_NAMESPACE}" ha-control-plane-too-large Rejected ControlPlaneReplicaLimitExceeded "${ha_probe_uid}"
if ${KUBECTL} -n "${TENANT_NAMESPACE}" get cluster claim-ha-control-plane-too-large >/dev/null 2>&1; then
  echo "HA tenant cluster probe unexpectedly created backing CAPI Cluster" >&2
  cleanup_ha_cluster_probe
  exit 1
fi
if ${KUBECTL} get capacityreservation kcc-${TENANT_NAMESPACE}-ha-control-plane-too-large >/dev/null 2>&1; then
  echo "HA tenant cluster probe unexpectedly created capacity reservation" >&2
  cleanup_ha_cluster_probe
  exit 1
fi
echo "HA tenant cluster claim rejected by lab control-plane replica limit as expected"
cleanup_ha_cluster_probe

echo "== provider API backing objects =="
${KUBECTL} -n "${TENANT_NAMESPACE}" wait --for=jsonpath='{.status.phase}'=Bound pvc/claim-demo-data --timeout=180s
${KUBECTL} -n "${TENANT_NAMESPACE}" get networkpolicy network-demo-private-isolation
${KUBECTL} -n "${TENANT_NAMESPACE}" get networkpolicy firewall-allow-tenant-api
${KUBECTL} -n "${TENANT_NAMESPACE}" get rolebinding accessgrant-tenant-a-admins-kubeconfig

echo "== tenant RBAC =="
expect_can_i yes get images
expect_can_i yes get productplans
expect_can_i yes create subscriptions.platform.privatecloud.local -n "${TENANT_NAMESPACE}"
expect_can_i yes create orders.platform.privatecloud.local -n "${TENANT_NAMESPACE}"
expect_can_i yes create virtualmachineclaims -n "${TENANT_NAMESPACE}"
expect_can_i yes create kubernetesclusterclaims -n "${TENANT_NAMESPACE}"
expect_can_i yes create volumes.platform.privatecloud.local -n "${TENANT_NAMESPACE}"
expect_can_i yes create networks -n "${TENANT_NAMESPACE}"
expect_can_i yes create firewallrules -n "${TENANT_NAMESPACE}"
expect_can_i yes create backupplans -n "${TENANT_NAMESPACE}"
expect_can_i yes create restorerequests -n "${TENANT_NAMESPACE}"
expect_can_i yes create accessgrants -n "${TENANT_NAMESPACE}"
expect_can_i yes get selfserviceauditevents.platform.privatecloud.local -n "${TENANT_NAMESPACE}"
expect_can_i yes list selfserviceauditevents.platform.privatecloud.local -n "${TENANT_NAMESPACE}"
expect_can_i no create selfserviceauditevents.platform.privatecloud.local -n "${TENANT_NAMESPACE}"
expect_can_i no delete selfserviceauditevents.platform.privatecloud.local -n "${TENANT_NAMESPACE}"
expect_can_i no create projects
expect_can_i no create productplans
expect_can_i no create capacitycells
expect_can_i no get capacityreservations
expect_can_i no get admissionjournals
expect_can_i no create orders.platform.privatecloud.local -n "${OTHER_NAMESPACE}"
expect_can_i no create volumes.platform.privatecloud.local -n "${OTHER_NAMESPACE}"
expect_can_i no get selfserviceauditevents.platform.privatecloud.local -n "${OTHER_NAMESPACE}"
