# Live Larger-Cell CAPK/OIDC Evidence

G018 is the live evidence gate after the offline CAPK/OIDC readiness contract.
It either produces a real live evidence file accepted by
`verify-production-capk-oidc-runtime-cutover-readiness.ps1 -EvidenceFile`, or
it produces a preflight/resource diagnosis that explains why this computer
cannot honestly produce that evidence yet.

The preflight command is read-only:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\invoke-live-larger-cell-capk-oidc-preflight.ps1
```

The command checks:

- Windows Hyper-V capacity and the running management cell.
- SSH access to the management node and `sudo -n k3s kubectl`.
- Cluster API and CAPK provider installation.
- Tenant `KubernetesClusterClaim` kubeconfig handoff.
- Tenant CAPI cluster shape for three ready control-plane replicas and at least
  one ready worker.
- KubeVirt tenant control-plane VMI placement.
- Provider portal runtime identity mode, requiring external `oidc-jwks` and no
  lab HS256 runtime secret. Kubernetes `secretKeyRef` and `configMapKeyRef`
  environment values are resolved before this check is evaluated.
- Provider portal token/JWKS runtime evidence. Deployment environment is only a
  precondition; final OIDC readiness requires accepted live runtime evidence.
- WSL/bash kubectl behavior, so a hanging local execution path is recorded as
  a tool blocker rather than hidden behind a manual timeout.

The blocked marker is:

```text
live_larger_cell_capk_oidc_preflight_blocked
```

A blocked report also emits:

```text
live_larger_cell_capk_oidc_no_aggregate_completion_claim
```

That marker is intentional. A preflight/resource diagnosis does not claim
aggregate completion. Final aggregate completion still requires real live
larger-cell CAPK lifecycle/HA evidence and external OIDC/JWKS runtime evidence.

In other words, the blocked preflight does not claim aggregate completion.
