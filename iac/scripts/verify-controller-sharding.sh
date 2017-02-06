#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
NAMESPACE="${NAMESPACE:-platform-system}"
DEPLOYMENT="${DEPLOYMENT:-provider-controller}"

env_value() {
  local name="$1"
  ${KUBECTL} -n "${NAMESPACE}" get deploy "${DEPLOYMENT}" \
    -o jsonpath="{.spec.template.spec.containers[?(@.name==\"controller\")].env[?(@.name==\"${name}\")].value}"
}

deployment_env_value() {
  local deployment="$1"
  local name="$2"
  ${KUBECTL} -n "${NAMESPACE}" get deploy "${deployment}" \
    -o jsonpath="{.spec.template.spec.containers[?(@.name==\"controller\")].env[?(@.name==\"${name}\")].value}"
}

shard_deployments="$(
  ${KUBECTL} -n "${NAMESPACE}" get deploy \
    -l app.kubernetes.io/name=provider-controller,app.kubernetes.io/component=controller \
    -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null || true
)"

if [[ -n "${shard_deployments}" ]]; then
  echo "== provider-controller active shard configuration =="
  base_replicas="$(${KUBECTL} -n "${NAMESPACE}" get deploy "${DEPLOYMENT}" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo 0)"
  [[ "${base_replicas:-0}" == "0" ]] || {
    echo "base ${DEPLOYMENT} replicas=${base_replicas}; active sharded mode must not run both topologies" >&2
    exit 1
  }

  deployments=()
  while IFS= read -r deployment; do
    [[ -n "${deployment}" ]] && deployments+=("${deployment}")
  done <<< "${shard_deployments}"
  expected_total="${#deployments[@]}"
  first_deployment="${deployments[0]}"
  shard_total="$(deployment_env_value "${first_deployment}" CONTROLLER_SHARD_TOTAL)"
  global_shard_index="$(deployment_env_value "${first_deployment}" CONTROLLER_GLOBAL_SHARD_INDEX)"
  [[ "${shard_total}" == "${expected_total}" ]] || {
    echo "expected shard_total=${expected_total}, got ${shard_total}" >&2
    exit 1
  }

  seen_indexes=()
  global_owners=0
  leader=""
  for deployment in "${deployments[@]}"; do
    shard_index="$(deployment_env_value "${deployment}" CONTROLLER_SHARD_INDEX)"
    deployment_total="$(deployment_env_value "${deployment}" CONTROLLER_SHARD_TOTAL)"
    deployment_global="$(deployment_env_value "${deployment}" CONTROLLER_GLOBAL_SHARD_INDEX)"
    allowlist="$(deployment_env_value "${deployment}" CONTROLLER_NAMESPACE_ALLOWLIST)"
    lease_name="$(deployment_env_value "${deployment}" LEADER_ELECTION_LEASE_NAME)"
    [[ "${deployment_total}" == "${shard_total}" ]] || { echo "${deployment} shard total mismatch" >&2; exit 1; }
    [[ "${deployment_global}" == "${global_shard_index}" ]] || { echo "${deployment} global shard mismatch" >&2; exit 1; }
    [[ -z "${allowlist}" ]] || { echo "expected empty namespace allowlist for ${deployment}, got ${allowlist}" >&2; exit 1; }
    [[ "${lease_name}" == "${deployment}" ]] || { echo "expected ${deployment} lease ${deployment}, got ${lease_name}" >&2; exit 1; }
    seen_indexes+=("${shard_index}")
    owns_global=0
    if [[ "${shard_index}" == "${global_shard_index}" ]]; then
      owns_global=1
      global_owners=$((global_owners + 1))
    fi

    pods="$(
      ${KUBECTL} -n "${NAMESPACE}" get pods \
        -l "app.kubernetes.io/name=provider-controller,app.kubernetes.io/component=controller,platform.privatecloud.local/controller-shard=${shard_index}" \
        --field-selector=status.phase=Running \
        -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
    )"
    [[ -n "${pods}" ]] || { echo "expected running pods for ${deployment}" >&2; exit 1; }
    for pod in ${pods}; do
      metrics="$(
        ${KUBECTL} -n "${NAMESPACE}" exec "${pod}" -- \
          python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/metrics", timeout=2).read().decode())'
      )"
      grep -q 'provider_controller_shard_info' <<< "${metrics}" || {
        echo "expected shard info metric from ${pod}" >&2
        exit 1
      }
      grep -q "shard_index=\"${shard_index}\",shard_total=\"${shard_total}\",owns_global=\"${owns_global}\"" <<< "${metrics}" || {
        echo "expected shard labels ${shard_index}/${shard_total} owns_global=${owns_global} on ${pod}" >&2
        exit 1
      }
    done

    holder=""
    for _ in $(seq 1 45); do
      candidate="$(${KUBECTL} -n "${NAMESPACE}" get lease "${lease_name}" -o jsonpath='{.spec.holderIdentity}' 2>/dev/null || true)"
      if [[ -n "${candidate}" ]] && ${KUBECTL} -n "${NAMESPACE}" get pod "${candidate}" >/dev/null 2>&1; then
        holder="${candidate}"
        break
      fi
      sleep 2
    done
    [[ -n "${holder}" ]] || { echo "expected ${lease_name} leader pod" >&2; exit 1; }
    [[ -n "${leader}" ]] || leader="${holder}"
    echo "${deployment} shard=${shard_index}/${shard_total} global=${owns_global} leader=${holder}"
  done

  [[ "${global_owners}" -eq 1 ]] || { echo "expected exactly one global shard owner, got ${global_owners}" >&2; exit 1; }
  unique_indexes="$(printf '%s\n' "${seen_indexes[@]}" | sort -n | uniq | wc -l | tr -d ' ')"
  [[ "${unique_indexes}" == "${shard_total}" ]] || {
    echo "expected unique shard indexes 0..$((shard_total - 1))" >&2
    exit 1
  }

  echo "== deterministic namespace ownership helper =="
  ${KUBECTL} -n "${NAMESPACE}" exec -i "${leader}" -- python - <<'PY'
import os
from controller import ProviderController, stable_shard

original = dict(os.environ)
try:
    os.environ["CONTROLLER_SHARD_TOTAL"] = "2"
    os.environ["CONTROLLER_GLOBAL_SHARD_INDEX"] = "0"
    os.environ.pop("CONTROLLER_NAMESPACE_ALLOWLIST", None)
    covered = {}
    for index in (0, 1):
        os.environ["CONTROLLER_SHARD_INDEX"] = str(index)
        controller = ProviderController()
        for namespace in ("tenant-a", "tenant-b", "tenant-c", "tenant-z"):
            if controller.owns_namespace(namespace):
                covered.setdefault(namespace, []).append(index)
            assert controller.owns_namespace(namespace) == (stable_shard(namespace, 2) == index)
    assert all(len(owners) == 1 for owners in covered.values())
finally:
    os.environ.clear()
    os.environ.update(original)

print("active shard namespace ownership helper passed")
PY

  echo "controller sharding verification passed"
  exit 0
fi

echo "== provider-controller shard configuration =="
shard_total="$(env_value CONTROLLER_SHARD_TOTAL)"
shard_index="$(env_value CONTROLLER_SHARD_INDEX)"
global_shard_index="$(env_value CONTROLLER_GLOBAL_SHARD_INDEX)"
allowlist="$(env_value CONTROLLER_NAMESPACE_ALLOWLIST)"
lease_name="$(env_value LEADER_ELECTION_LEASE_NAME)"

[[ "${shard_total}" == "1" ]] || { echo "expected lab shard_total=1, got ${shard_total}" >&2; exit 1; }
[[ "${shard_index}" == "0" ]] || { echo "expected lab shard_index=0, got ${shard_index}" >&2; exit 1; }
[[ "${global_shard_index}" == "0" ]] || { echo "expected global shard index 0, got ${global_shard_index}" >&2; exit 1; }
[[ -z "${allowlist}" ]] || { echo "expected empty namespace allowlist in lab, got ${allowlist}" >&2; exit 1; }
[[ "${lease_name}" == "provider-controller" ]] || { echo "expected lab lease provider-controller, got ${lease_name}" >&2; exit 1; }
echo "lab shard index=${shard_index}/${shard_total} global=${global_shard_index} lease=${lease_name}"

echo "== provider-controller shard metrics =="
pods="$(
  ${KUBECTL} -n "${NAMESPACE}" get pods -l app="${DEPLOYMENT}" \
    --field-selector=status.phase=Running \
    -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
)"
[[ -n "${pods}" ]] || { echo "expected running provider-controller pods" >&2; exit 1; }
for pod in ${pods}; do
  metrics="$(
    ${KUBECTL} -n "${NAMESPACE}" exec "${pod}" -- \
      python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/metrics", timeout=2).read().decode())'
  )"
  grep -q 'provider_controller_shard_info' <<< "${metrics}" || {
    echo "expected shard info metric from ${pod}" >&2
    exit 1
  }
  grep -q 'shard_index="0",shard_total="1",owns_global="1"' <<< "${metrics}" || {
    echo "expected lab shard labels on ${pod}" >&2
    exit 1
  }
done

echo "== deterministic namespace ownership helper =="
leader=""
for _ in $(seq 1 45); do
  candidate="$(${KUBECTL} -n "${NAMESPACE}" get lease "${lease_name}" -o jsonpath='{.spec.holderIdentity}' 2>/dev/null || true)"
  if [[ -n "${candidate}" ]] && ${KUBECTL} -n "${NAMESPACE}" get pod "${candidate}" >/dev/null 2>&1; then
    leader="${candidate}"
    break
  fi
  sleep 2
done
[[ -n "${leader}" ]] || { echo "expected provider-controller leader pod" >&2; exit 1; }
${KUBECTL} -n "${NAMESPACE}" exec -i "${leader}" -- python - <<'PY'
import os
from controller import ProviderController, stable_shard

assert stable_shard("tenant-a", 1) == 0
assert stable_shard("tenant-c", 1) == 0

original = dict(os.environ)
try:
    os.environ["CONTROLLER_SHARD_TOTAL"] = "1"
    os.environ["CONTROLLER_SHARD_INDEX"] = "0"
    os.environ["CONTROLLER_GLOBAL_SHARD_INDEX"] = "0"
    os.environ.pop("CONTROLLER_NAMESPACE_ALLOWLIST", None)
    lab = ProviderController()
    assert lab.owns_global_resources()
    assert lab.owns_namespace("tenant-a")
    assert lab.owns_namespace("tenant-c")

    os.environ["CONTROLLER_SHARD_TOTAL"] = "2"
    os.environ["CONTROLLER_GLOBAL_SHARD_INDEX"] = "0"
    os.environ.pop("CONTROLLER_NAMESPACE_ALLOWLIST", None)
    for index in (0, 1):
        os.environ["CONTROLLER_SHARD_INDEX"] = str(index)
        controller = ProviderController()
        for namespace in ("tenant-a", "tenant-b", "tenant-c", "tenant-z"):
            expected = stable_shard(namespace, 2) == index
            assert controller.owns_namespace(namespace) == expected

    os.environ["CONTROLLER_SHARD_TOTAL"] = "4"
    os.environ["CONTROLLER_SHARD_INDEX"] = "3"
    os.environ["CONTROLLER_GLOBAL_SHARD_INDEX"] = "0"
    os.environ["CONTROLLER_NAMESPACE_ALLOWLIST"] = "tenant-c,tenant-d"
    allowlisted = ProviderController()
    assert not allowlisted.owns_global_resources()
    assert allowlisted.owns_namespace("tenant-c")
    assert allowlisted.owns_namespace("tenant-d")
    assert not allowlisted.owns_namespace("tenant-a")
finally:
    os.environ.clear()
    os.environ.update(original)

print("namespace ownership helper passed")
PY

echo "controller sharding verification passed"
