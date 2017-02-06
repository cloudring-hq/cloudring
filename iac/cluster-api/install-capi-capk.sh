#!/usr/bin/env bash
set -euo pipefail

CLUSTERCTL_VERSION="${CLUSTERCTL_VERSION:-v1.13.2}"
CAPK_VERSION="${CAPK_VERSION:-v0.11.2}"
if [[ -z "${KUBECTL:-}" ]]; then
  if command -v kubectl >/dev/null 2>&1; then
    KUBECTL="kubectl"
  else
    KUBECTL="sudo k3s kubectl"
  fi
fi

kubectl_cmd() {
  ${KUBECTL} "$@"
}

if ! command -v clusterctl >/dev/null 2>&1; then
  arch="$(uname -m)"
  case "${arch}" in
    x86_64 | amd64) clusterctl_arch="amd64" ;;
    aarch64 | arm64) clusterctl_arch="arm64" ;;
    *)
      echo "unsupported architecture for clusterctl: ${arch}" >&2
      exit 1
      ;;
  esac

  tmpdir="$(mktemp -d)"
  trap 'rm -rf "${tmpdir}"' EXIT
  curl -fsSL \
    "https://github.com/kubernetes-sigs/cluster-api/releases/download/${CLUSTERCTL_VERSION}/clusterctl-linux-${clusterctl_arch}" \
    -o "${tmpdir}/clusterctl"
  chmod +x "${tmpdir}/clusterctl"
  sudo install -m 0755 "${tmpdir}/clusterctl" /usr/local/bin/clusterctl
fi

export CLUSTER_TOPOLOGY="${CLUSTER_TOPOLOGY:-true}"

clusterctl init --infrastructure "kubevirt:${CAPK_VERSION}"

kubectl_cmd wait -n cert-manager --for=condition=Available=true deployment/cert-manager --timeout=10m
kubectl_cmd wait -n cert-manager --for=condition=Available=true deployment/cert-manager-webhook --timeout=10m
kubectl_cmd wait -n capi-system --for=condition=Available=true deployment/capi-controller-manager --timeout=10m
kubectl_cmd wait -n capi-kubeadm-bootstrap-system --for=condition=Available=true deployment/capi-kubeadm-bootstrap-controller-manager --timeout=10m
kubectl_cmd wait -n capi-kubeadm-control-plane-system --for=condition=Available=true deployment/capi-kubeadm-control-plane-controller-manager --timeout=10m
kubectl_cmd wait -n capk-system --for=condition=Available=true deployment/capk-controller-manager --timeout=10m

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ha_script="${script_dir}/../scripts/apply-management-control-plane-ha.sh"
if [[ -f "${ha_script}" ]]; then
  KUBECTL="${KUBECTL}" bash "${ha_script}"
else
  echo "HA hardening script not found or not executable at ${ha_script}; skipping" >&2
fi

clusterctl describe cluster --all-namespaces || true
kubectl_cmd get providers -A
