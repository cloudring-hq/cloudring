# GitOps Layout

This directory is the desired-state entry point for the lab Flux installation
and for future multi-cell promotion.

The current Hyper-V lab runs Flux in `flux-system`. `GitRepository/platform-gitops`
reads an immutable in-cluster bare Git snapshot served by
`platform-gitops-source`, and `Kustomization/platform-base` applies
`./gitops/platform` with `prune=false`. Rebuild the source image with
`iac/scripts/build-gitops-source-image.sh`, install/update Flux with
`iac/scripts/install-flux-gitops.sh`, and verify it with
`iac/scripts/verify-flux-gitops.sh`.

## Layout

| Path | Purpose |
| --- | --- |
| `platform/` | Platform add-ons shared by all cells |
| `platform-production-backup/` | Opt-in production backup and disaster-recovery overlay |
| `platform-production-backup-runtime/` | Opt-in production backup runtime cutover overlay |
| `platform-production-identity/` | Opt-in production OIDC/JWKS identity overlay for the provider portal |
| `platform-production-observability/` | Opt-in production observability, SLO, and alerting overlay |
| `platform-production-scheduler/` | Opt-in production scheduler and transactional admission overlay |
| `platform-production-scheduler-runtime/` | Opt-in production scheduler runtime cutover overlay |
| `cells/` | Per-capacity-cell configuration; `production-cell-template/` is an opt-in copy point for real cells |
| `tenants/` | Tenant projects and claims |
| `policies/` | Admission, APF, and security policy |

Tenant overlays should contain provider API objects, not raw substrate objects.
For the current v1alpha1 contract this means `Project`, `VirtualMachineClaim`,
`KubernetesClusterClaim`, `Network`, `FirewallRule`, `Volume`, `BackupPlan`,
and `AccessGrant`. Platform overlays own cluster-scoped `CapacityCell`
inventory contracts, `Image` catalog entries, and CRD/RBAC installation.
VM and tenant Kubernetes overlays can set `spec.placement.capacityCell` and
`spec.placement.serviceClass`; otherwise the provider controller selects the
matching default service class for the current cell.

## Promotion Model

1. Commit desired change.
2. Validate manifests and policies.
3. Sync dev/lab cell.
4. Run conformance, tenant isolation, storage, KubeVirt, and API smoke tests.
5. Promote to production cells by wave.
6. Monitor SLOs and rollback through Git if needed.

Production-cell substrate manifests live under
`iac/kubernetes/production-cell` and are intentionally not included in the lab
or shared platform overlays. Copy `gitops/cells/production-cell-template` to a
real cell overlay, replace the placeholders, and run
`iac/scripts/verify-production-cell-blueprint.ps1` before promotion.

Production identity manifests live under `iac/kubernetes/production-identity`
and are layered by `gitops/platform-production-identity`. They are intentionally
not included in `gitops/platform` or the Hyper-V lab cell; replace the OIDC
placeholders and complete the provider-portal JWKS runtime cutover before
promotion.

Production observability manifests live under
`iac/kubernetes/production-observability` and are layered by
`gitops/platform-production-observability`. They are intentionally not included
in the lab overlay; install the required CRDs/operators, replace placeholders,
and run `iac/scripts/verify-production-observability-blueprint.ps1` before
promotion.

Production backup and DR manifests live under `iac/kubernetes/production-backup`
and are layered by `gitops/platform-production-backup` together with the
production-cell Velero locations. They are intentionally not included in the
lab overlay; install Velero with CSI support, replace placeholders, verify
remote immutability, run `iac/scripts/verify-production-backup-blueprint.ps1`
and `iac/scripts/verify-production-backup-runtime-blueprint.ps1`, and complete
the provider backup service runtime cutover before promotion.

Production backup runtime cutover manifests live under
`iac/kubernetes/production-backup-runtime` and are layered only by
`gitops/platform-production-backup-runtime`. This overlay first includes
`platform-production-backup`, then adds the disabled-by-default runtime
Deployment and runbooks. It is intentionally not included in the lab overlay;
replace placeholders, run
`iac/scripts/verify-production-backup-runtime-cutover.ps1`, keep the runtime at
`replicas: 0` by default, add `canary-enable-patch.example.yaml` for a
single-replica `RUNTIME_ENABLED=true` smoke test, and then replace it with
`ha-enable-patch.example.yaml` to scale to at least three replicas only after
`BackupStorageLocation`, `VolumeSnapshotLocation`, `BackupRepository`, and
tenant isolation evidence are captured.

Production scheduler and transactional admission manifests live under
`iac/kubernetes/production-scheduler` and are layered by
`gitops/platform-production-scheduler`. They are intentionally not included in
the lab overlay; build a real scheduler image, replace placeholders, promote
with multiple real `CapacityCell` objects, and run
`iac/scripts/verify-production-scheduler-blueprint.ps1` before runtime cutover.

Production scheduler runtime cutover manifests live under
`iac/kubernetes/production-scheduler-runtime` and are layered only by
`gitops/platform-production-scheduler-runtime`. This overlay first includes
`platform-production-scheduler`, then adds the disabled-by-default scheduler
runtime controller, fail-closed admission webhook contract, canary/HA patches,
and rollback runbooks. It is intentionally not included in the lab overlay;
replace placeholders, run
`iac/scripts/verify-production-scheduler-runtime-cutover.ps1`, keep the runtime
at `replicas: 0` by default, add `canary-enable-patch.example.yaml` for a
single-replica `RUNTIME_ENABLED=true` smoke test, and then replace it with
`ha-enable-patch.example.yaml` to scale to at least three replicas only after
CapacityCell, quota, reservation, journal, and tenant-isolation evidence is
captured.
