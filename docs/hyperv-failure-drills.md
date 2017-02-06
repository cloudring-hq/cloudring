# Hyper-V failure drills

Use `iac/scripts/hyperv-failure-drill.ps1` from an elevated PowerShell session for VM stop/start drills. The script is dry-run by default and writes both text and newline-delimited JSON logs under `artifacts/hyperv-failure-drills` when `artifacts/` exists, otherwise under `docs/logs/hyperv-failure-drills`.

Dry-run plan from a normal shell:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\iac\scripts\hyperv-failure-drill.ps1 -Action RestartVm -VMName platform-n1
```

Run an actual single-VM restart from an Administrator PowerShell:

```powershell
Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "C:\Users\yuri\Personal\Sources\Platform\iac\scripts\hyperv-failure-drill.ps1" -Action RestartVm -VMName platform-n1 -Execute -ConfirmDestructive'
```

The default allowed VM pattern is `^platform-n[1-3]$`, mapped to `172.28.10.11-13`. The script maps those Hyper-V VM names to Kubernetes node names `n1`, `n2`, and `n3`, connects as SSH user `platform`, and uses the workspace key `.ssh/platform_lab_ed25519`. Override `-VMNamePattern`, `-NodeIps`, `-SshUser`, `-SshKeyPath`, or `-KubeReadyNodeName` only when the lab inventory intentionally differs.

The script does not perform disk operations. `-AllowDiskOperations` is reserved as an explicit guard and currently fails closed.

## Post-Restart Convergence

On the current three-node nested Hyper-V lab, a real `RestartVm` can make the
local k3s API servers and KubeVirt management pods spend several minutes
catching up. Treat the drill as complete only after all of these are true:

```bash
sudo k3s kubectl get --raw=/readyz
sudo k3s kubectl get nodes --no-headers
sudo k3s kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers
iac/scripts/verify-kubevirt-ha.sh
sudo k3s kubectl -n flux-system get gitrepository,kustomization -o wide
```

The drill script retries native `ssh.exe` failures inside its polling loops.
This is intentional: immediately after a VM power cycle, Windows OpenSSH can
return a connection-timeout error before the guest network stack is ready.

KubeVirt `virt-operator` probes are also tuned by
`iac/scripts/apply-kubevirt-ha.sh` for the nested lab. Without a startup probe,
the operator can be killed by liveness checks before its metrics endpoint comes
up during heavy post-fault API/etcd catch-up.
