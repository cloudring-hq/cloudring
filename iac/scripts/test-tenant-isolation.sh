#!/usr/bin/env bash
set -euo pipefail

sudo k3s kubectl -n tenant-a delete pod isolate-a --ignore-not-found
sudo k3s kubectl -n tenant-b delete pod isolate-b --ignore-not-found
sudo k3s kubectl apply -f /tmp/tenant-isolation.yaml
sudo k3s kubectl -n tenant-a wait pod/isolate-a --for=condition=Ready --timeout=120s
sudo k3s kubectl -n tenant-b wait pod/isolate-b --for=condition=Ready --timeout=120s

BIP="$(sudo k3s kubectl -n tenant-b get pod isolate-b -o jsonpath='{.status.podIP}')"
echo "tenant-b-pod=${BIP}"

set +e
sudo k3s kubectl -n tenant-a exec isolate-a -- sh -c "timeout 4 nc -vz ${BIP} 8080"
code="$?"
set -e

echo "cross_tenant_exit=${code}"
if [[ "${code}" -eq 0 ]]; then
  echo "cross-tenant traffic unexpectedly succeeded" >&2
  exit 1
fi

echo "cross-tenant traffic blocked as expected"
