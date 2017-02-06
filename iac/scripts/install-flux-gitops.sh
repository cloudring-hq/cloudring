#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
FLUX_VERSION="${FLUX_VERSION:-2.8.8}"
FLUX_ARCHIVE="flux_${FLUX_VERSION}_linux_amd64.tar.gz"
FLUX_URL="${FLUX_URL:-https://github.com/fluxcd/flux2/releases/download/v${FLUX_VERSION}/${FLUX_ARCHIVE}}"
FLUX_COMPONENTS="${FLUX_COMPONENTS:-source-controller,kustomize-controller,helm-controller,notification-controller}"
MANIFEST="${PROJECT_ROOT}/iac/kubernetes/gitops/flux-platform.yaml"

work="$(mktemp -d)"
cleanup() {
  rm -rf "${work}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "== download flux ${FLUX_VERSION} =="
curl -L --fail -o "${work}/${FLUX_ARCHIVE}" "${FLUX_URL}"
tar -xzf "${work}/${FLUX_ARCHIVE}" -C "${work}" flux
"${work}/flux" --version

echo "== install flux controllers =="
"${work}/flux" install \
  --export \
  --namespace=flux-system \
  --components="${FLUX_COMPONENTS}" \
  >"${work}/flux-install.yaml"
${KUBECTL} apply -f "${work}/flux-install.yaml"

for deploy in source-controller kustomize-controller helm-controller notification-controller; do
  ${KUBECTL} -n flux-system rollout status "deploy/${deploy}" --timeout=180s
done

echo "== harden flux controllers for lab HA =="
for deploy in kustomize-controller helm-controller notification-controller; do
  ${KUBECTL} -n flux-system scale "deploy/${deploy}" --replicas=3
  ${KUBECTL} -n flux-system patch "deploy/${deploy}" --type=merge -p "$(
    cat <<PATCH
{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxSurge":1,"maxUnavailable":1}},"template":{"spec":{"topologySpreadConstraints":[{"maxSkew":1,"minDomains":3,"topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule","matchLabelKeys":["pod-template-hash"],"labelSelector":{"matchLabels":{"app":"${deploy}"}}}],"affinity":{"podAntiAffinity":{"preferredDuringSchedulingIgnoredDuringExecution":[{"weight":100,"podAffinityTerm":{"labelSelector":{"matchLabels":{"app":"${deploy}"}},"topologyKey":"kubernetes.io/hostname"}}]}}}}}}
PATCH
  )"
  ${KUBECTL} -n flux-system rollout status "deploy/${deploy}" --timeout=180s
done

${KUBECTL} -n flux-system scale deploy/source-controller --replicas=3
${KUBECTL} -n flux-system patch deploy/source-controller --type=strategic -p "$(
  cat <<'PATCH'
{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxSurge":1,"maxUnavailable":2}},"template":{"spec":{"containers":[{"name":"manager","readinessProbe":{"httpGet":{"path":"/","port":"http"}}}],"topologySpreadConstraints":[{"maxSkew":1,"minDomains":3,"topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule","matchLabelKeys":["pod-template-hash"],"labelSelector":{"matchLabels":{"app":"source-controller"}}}],"affinity":{"podAntiAffinity":{"preferredDuringSchedulingIgnoredDuringExecution":[{"weight":100,"podAffinityTerm":{"labelSelector":{"matchLabels":{"app":"source-controller"}},"topologyKey":"kubernetes.io/hostname"}}]}}}}}}
PATCH
)"
source_ready=false
for _ in $(seq 1 90); do
  ready="$(${KUBECTL} -n flux-system get deploy/source-controller -o jsonpath='{.status.readyReplicas}' 2>/dev/null || true)"
  desired="$(${KUBECTL} -n flux-system get deploy/source-controller -o jsonpath='{.spec.replicas}' 2>/dev/null || true)"
  updated="$(${KUBECTL} -n flux-system get deploy/source-controller -o jsonpath='{.status.updatedReplicas}' 2>/dev/null || true)"
  available="$(${KUBECTL} -n flux-system get deploy/source-controller -o jsonpath='{.status.availableReplicas}' 2>/dev/null || true)"
  if [[ "${ready:-0}" -ge 1 && "${available:-0}" -ge 1 && "${updated:-0}" -eq 3 && "${desired}" == "3" ]]; then
    echo "source-controller artifactReady=${ready} available=${available} updated=${updated} desired=${desired}"
    source_ready=true
    break
  fi
  sleep 2
done
[[ "${source_ready}" == "true" ]] || { echo "source-controller did not publish a Ready artifact-serving leader" >&2; exit 1; }

echo "== apply platform gitops source and reconciler =="
${KUBECTL} apply --server-side --dry-run=server -f "${MANIFEST}"
${KUBECTL} apply -f "${MANIFEST}"
${KUBECTL} -n flux-system rollout status deploy/platform-gitops-source --timeout=180s

echo "Flux GitOps installation requested. Run verify-flux-gitops.sh for readiness gates."
