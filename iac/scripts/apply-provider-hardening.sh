#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/tmp/platform-iac}"

sudo k3s kubectl apply -f "${ROOT}/kubernetes/platform/tenant-security.yaml"
sudo k3s kubectl apply -f "${ROOT}/kubernetes/platform/tenant-rbac.yaml"
sudo k3s kubectl apply -f "${ROOT}/kubernetes/platform/apf-tenant-fairness.yaml"

if sudo k3s kubectl api-resources | grep -q '^clusterpolicies[[:space:]]'; then
  sudo k3s kubectl apply -f "${ROOT}/kubernetes/platform/kyverno-policies.yaml"
else
  echo "Kyverno CRDs are not installed; skipped kyverno-policies.yaml"
fi
