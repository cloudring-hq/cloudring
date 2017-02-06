#!/usr/bin/env bash
set -euo pipefail

CDI_VERSION="${CDI_VERSION:-}"
KUBECTL="${KUBECTL:-sudo k3s kubectl}"

if [[ -z "${CDI_VERSION}" ]]; then
  CDI_VERSION="$(basename "$(curl -fsSL -o /dev/null -w '%{url_effective}' https://github.com/kubevirt/containerized-data-importer/releases/latest)")"
fi

echo "Installing CDI ${CDI_VERSION}"
${KUBECTL} apply -f "https://github.com/kubevirt/containerized-data-importer/releases/download/${CDI_VERSION}/cdi-operator.yaml"
${KUBECTL} apply -f "https://github.com/kubevirt/containerized-data-importer/releases/download/${CDI_VERSION}/cdi-cr.yaml"

${KUBECTL} wait -n cdi --for=condition=Available=true deployment/cdi-operator --timeout=10m
${KUBECTL} wait -n cdi --for=condition=Available=true deployment/cdi-deployment --timeout=10m
${KUBECTL} wait -n cdi --for=condition=Available=true deployment/cdi-apiserver --timeout=10m
${KUBECTL} wait -n cdi --for=condition=Available=true deployment/cdi-uploadproxy --timeout=10m

for _ in $(seq 1 120); do
  phase="$(${KUBECTL} -n cdi get cdi cdi -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  echo "CDI phase=${phase:-missing}"
  [[ "${phase}" == "Deployed" ]] && break
  sleep 5
done

phase="$(${KUBECTL} -n cdi get cdi cdi -o jsonpath='{.status.phase}')"
[[ "${phase}" == "Deployed" ]] || {
  echo "expected CDI phase Deployed, got ${phase}" >&2
  exit 1
}

${KUBECTL} get cdi -n cdi
${KUBECTL} get crd datavolumes.cdi.kubevirt.io storageprofiles.cdi.kubevirt.io
