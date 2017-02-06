#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
NAMESPACE="${NAMESPACE:-platform-system}"
MANIFEST="${MANIFEST:-${PROJECT_ROOT}/iac/kubernetes/provider-controller/sharded-controller.yaml}"
BASE_DEPLOYMENT="${BASE_DEPLOYMENT:-provider-controller}"
RESTORE_REPLICAS="${RESTORE_REPLICAS:-3}"
FLUX_NAMESPACE="${FLUX_NAMESPACE:-flux-system}"
FLUX_KUSTOMIZATION="${FLUX_KUSTOMIZATION:-platform-base}"
SUSPEND_FLUX="${SUSPEND_FLUX:-true}"
ACTION="${1:-status}"

flux_exists() {
  ${KUBECTL} -n "${FLUX_NAMESPACE}" get kustomization "${FLUX_KUSTOMIZATION}" >/dev/null 2>&1
}

patch_flux_suspend() {
  local suspend="$1"
  if [[ "${SUSPEND_FLUX}" != "true" ]] || ! flux_exists; then
    return
  fi
  ${KUBECTL} -n "${FLUX_NAMESPACE}" patch kustomization "${FLUX_KUSTOMIZATION}" \
    --type=merge -p "{\"spec\":{\"suspend\":${suspend}}}" >/dev/null
  echo "flux kustomization ${FLUX_NAMESPACE}/${FLUX_KUSTOMIZATION} suspend=${suspend}"
}

base_replicas() {
  ${KUBECTL} -n "${NAMESPACE}" get deploy "${BASE_DEPLOYMENT}" \
    -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0"
}

annotate_restore_replicas() {
  local replicas="$1"
  ${KUBECTL} -n "${NAMESPACE}" annotate deploy "${BASE_DEPLOYMENT}" \
    platform.privatecloud.local/pre-shard-replicas="${replicas}" --overwrite >/dev/null
}

stored_restore_replicas() {
  local replicas
  replicas="$(
    ${KUBECTL} -n "${NAMESPACE}" get deploy "${BASE_DEPLOYMENT}" \
      -o jsonpath='{.metadata.annotations.platform\.privatecloud\.local/pre-shard-replicas}' 2>/dev/null || true
  )"
  echo "${replicas:-${RESTORE_REPLICAS}}"
}

wait_no_base_pods() {
  for _ in $(seq 1 90); do
    running="$(
      ${KUBECTL} -n "${NAMESPACE}" get pods -l app="${BASE_DEPLOYMENT}" \
        --field-selector=status.phase=Running \
        -o jsonpath='{range .items[*]}{.metadata.ownerReferences[0].name}{"\n"}{end}' 2>/dev/null |
        grep -cx "${BASE_DEPLOYMENT}" || true
    )"
    [[ "${running}" == "0" ]] && return
    sleep 2
  done
  echo "timed out waiting for base provider-controller pods to stop" >&2
  exit 1
}

wait_shards() {
  local deployments
  deployments="$(
    ${KUBECTL} -n "${NAMESPACE}" get deploy \
      -l app.kubernetes.io/name=provider-controller,app.kubernetes.io/component=controller \
      -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null || true
  )"
  [[ -n "${deployments}" ]] || { echo "expected shard deployments" >&2; exit 1; }
  for deployment in ${deployments}; do
    ${KUBECTL} -n "${NAMESPACE}" rollout status "deploy/${deployment}" --timeout=180s
  done
}

status() {
  echo "== flux =="
  if flux_exists; then
    ${KUBECTL} -n "${FLUX_NAMESPACE}" get kustomization "${FLUX_KUSTOMIZATION}" \
      -o custom-columns=NAME:.metadata.name,READY:.status.conditions[0].status,SUSPEND:.spec.suspend,REVISION:.status.lastAppliedRevision --no-headers
  else
    echo "flux kustomization ${FLUX_NAMESPACE}/${FLUX_KUSTOMIZATION} not found"
  fi
  echo "== provider-controller deployments =="
  ${KUBECTL} -n "${NAMESPACE}" get deploy,pdb,svc -l app=provider-controller -o wide
  echo "== provider-controller leases =="
  ${KUBECTL} -n "${NAMESPACE}" get lease provider-controller provider-controller-shard-0 provider-controller-shard-1 \
    -o custom-columns=NAME:.metadata.name,HOLDER:.spec.holderIdentity,TRANSITIONS:.spec.leaseTransitions --ignore-not-found
}

dry_run() {
  "${SCRIPT_DIR}/verify-controller-shard-topology.sh"
  ${KUBECTL} apply --dry-run=server -f "${MANIFEST}" >/dev/null
  echo "provider-controller shard cutover dry-run passed"
}

cutover() {
  dry_run
  local replicas
  replicas="$(base_replicas)"
  annotate_restore_replicas "${replicas}"
  patch_flux_suspend true
  echo "scaling ${NAMESPACE}/${BASE_DEPLOYMENT} from ${replicas} to 0"
  ${KUBECTL} -n "${NAMESPACE}" scale "deploy/${BASE_DEPLOYMENT}" --replicas=0
  wait_no_base_pods
  ${KUBECTL} -n "${NAMESPACE}" delete lease "${BASE_DEPLOYMENT}" --ignore-not-found=true
  ${KUBECTL} apply -f "${MANIFEST}"
  wait_shards
  "${SCRIPT_DIR}/verify-provider-layer.sh"
  echo "provider-controller shard cutover passed"
}

rollback() {
  echo "deleting shard topology from ${MANIFEST}"
  ${KUBECTL} delete -f "${MANIFEST}" --ignore-not-found=true
  ${KUBECTL} -n "${NAMESPACE}" delete lease provider-controller-shard-0 provider-controller-shard-1 --ignore-not-found=true
  local replicas
  replicas="$(stored_restore_replicas)"
  echo "restoring ${NAMESPACE}/${BASE_DEPLOYMENT} replicas=${replicas}"
  ${KUBECTL} -n "${NAMESPACE}" scale "deploy/${BASE_DEPLOYMENT}" --replicas="${replicas}"
  ${KUBECTL} -n "${NAMESPACE}" rollout status "deploy/${BASE_DEPLOYMENT}" --timeout=180s
  patch_flux_suspend false
  "${SCRIPT_DIR}/verify-provider-layer.sh"
  echo "provider-controller shard rollback passed"
}

case "${ACTION}" in
  status)
    status
    ;;
  dry-run)
    dry_run
    ;;
  cutover)
    cutover
    ;;
  rollback)
    rollback
    ;;
  *)
    echo "usage: $0 [status|dry-run|cutover|rollback]" >&2
    exit 2
    ;;
esac
