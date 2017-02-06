#!/usr/bin/env bash
set -euo pipefail

sudo k3s kubectl apply -f /tmp/provider-self-service-00

for _ in $(seq 1 40); do
  if sudo k3s kubectl get ns tenant-c >/dev/null 2>&1; then
    break
  fi
  sleep 3
done

sudo k3s kubectl get ns tenant-c >/dev/null
sudo k3s kubectl apply -f /tmp/provider-self-service-01

for _ in $(seq 1 60); do
  if sudo k3s kubectl -n tenant-c get vmi claim-smoke-vm >/dev/null 2>&1; then
    break
  fi
  sleep 3
done

sudo k3s kubectl -n tenant-c get vmi claim-smoke-vm >/dev/null
sudo k3s kubectl -n tenant-c wait vmi/claim-smoke-vm --for=condition=Ready --timeout=180s

project_phase="$(sudo k3s kubectl get project tenant-c -o jsonpath='{.status.phase}')"
project_namespace="$(sudo k3s kubectl get project tenant-c -o jsonpath='{.status.namespaces[0]}')"
claim_phase="$(sudo k3s kubectl -n tenant-c get virtualmachineclaim smoke-vm -o jsonpath='{.status.phase}')"
claim_vm="$(sudo k3s kubectl -n tenant-c get virtualmachineclaim smoke-vm -o jsonpath='{.status.vmName}')"
claim_ip="$(sudo k3s kubectl -n tenant-c get virtualmachineclaim smoke-vm -o jsonpath='{.status.ip}')"

[[ "${project_phase}" == "Ready" ]] || { echo "unexpected project phase: ${project_phase}" >&2; exit 1; }
[[ "${project_namespace}" == "tenant-c" ]] || { echo "unexpected project namespace: ${project_namespace}" >&2; exit 1; }
[[ "${claim_phase}" == "Ready" ]] || { echo "unexpected claim phase: ${claim_phase}" >&2; exit 1; }
[[ "${claim_vm}" == "claim-smoke-vm" ]] || { echo "unexpected claim vm: ${claim_vm}" >&2; exit 1; }
[[ -n "${claim_ip}" ]] || { echo "claim IP is empty" >&2; exit 1; }

sudo k3s kubectl -n tenant-c get resourcequota tenant-quota tenant-object-quota >/dev/null
sudo k3s kubectl -n tenant-c get networkpolicy default-deny allow-dns >/dev/null
if sudo k3s kubectl -n tenant-c get networkpolicy allow-internet-egress >/dev/null 2>&1; then
  echo "internet egress policy exists despite allowInternetEgress=false" >&2
  exit 1
fi
sudo k3s kubectl -n tenant-c get role tenant-admin >/dev/null
rb_subject="$(sudo k3s kubectl -n tenant-c get rolebinding tenant-admins -o jsonpath='{.subjects[0].name}')"
[[ "${rb_subject}" == "platform:tenant-c:admins" ]] || { echo "unexpected tenant admin group: ${rb_subject}" >&2; exit 1; }

if [[ -f /tmp/tenant-c-deny-loadbalancer.yaml ]]; then
  set +e
  deny_output="$(sudo k3s kubectl apply --dry-run=server -f /tmp/tenant-c-deny-loadbalancer.yaml 2>&1)"
  deny_code="$?"
  set -e
  if [[ "${deny_code}" -eq 0 ]] || ! grep -q "tenant-guardrails" <<< "${deny_output}"; then
    echo "expected tenant-c LoadBalancer to be rejected by tenant-guardrails, got:" >&2
    echo "${deny_output}" >&2
    exit 1
  fi
fi

echo "project_phase=${project_phase}"
echo "claim_status=${claim_phase} ${claim_vm} ${claim_ip}"
sudo k3s kubectl -n tenant-c get resourcequota,networkpolicy,role,rolebinding
sudo k3s kubectl -n tenant-c get vm,vmi,pod -o wide
