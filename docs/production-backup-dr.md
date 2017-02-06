# Production Backup And Disaster Recovery

The lab already proves the first data-protection workflow: a `BackupPlan` can
protect a `VirtualMachineClaim` through KubeVirt `VirtualMachineSnapshot`, and
a `RestoreRequest` can copy-restore that recovery point into a new VM target.

Production needs a broader contract:

- `Volume` targets use CSI `VolumeSnapshot` plus Velero CSI backup/export into
  off-cell object storage.
- `Namespace` targets use Velero resource filtering with CSI snapshots and a
  restore policy that defaults to copy restore into a new namespace.
- `KubernetesClusterClaim` targets protect the provider claim, CAPI/CAPK
  objects, kubeconfig/control-plane secrets, provider API gateway resources,
  and persistent control-plane volumes.
- Remote and immutable destinations require object-lock or an equivalent
  retention control before tenant data is stored there.
- Tenant-visible restores must reject target collisions, preserve tenant
  isolation, and require approval for namespace or tenant-cluster restore.

## Repository Artifacts

- `iac/kubernetes/production-backup` contains the opt-in backup/DR blueprint.
- `gitops/platform-production-backup` layers the production-cell Velero
  locations and the backup/DR contract over the shared platform overlay.
- `iac/scripts/verify-production-backup-blueprint.ps1` checks that the
  blueprint remains opt-in, placeholder-backed, and aligned with the current
  provider API target kinds.
- `docs/production-backup-operations.md` describes the Production Backup
  Runtime Operations contract: service ownership, preflight gates, SLOs,
  restore drills, and tenant isolation.
- `iac/scripts/verify-production-backup-runtime-blueprint.ps1` checks the
  runtime operations contract and the lab opt-in boundary.
- `iac/kubernetes/production-backup-runtime` contains the opt-in production
  runtime cutover skeleton for the provider backup controller.
- `gitops/platform-production-backup-runtime` layers
  `platform-production-backup` first and then adds the runtime cutover skeleton.
- `iac/scripts/verify-production-backup-runtime-cutover.ps1` checks the runtime
  cutover skeleton, GitOps ordering, smoke/rollback contracts, and lab
  no-contamination boundary.
- `iac/scripts/simulate-production-backup-runtime-canary.py` is a local,
  non-cluster simulator for provider backup runtime reconciliation of `Volume`,
  `Namespace`, and `KubernetesClusterClaim` targets into deterministic Velero
  actions.
- `iac/scripts/verify-production-backup-runtime-simulation.ps1` compiles and
  runs that simulator, parses `SIMULATION_JSON:`, verifies fail-closed
  scenarios, and proves the simulator has no cluster or network access tokens.
- `iac/scripts/verify-production-backup-runtime-api-seam.ps1` checks the
  widened provider `RestoreRequest` API contract, the template-only runtime
  Velero mapping contract, and the Hyper-V lab fail-closed boundary.
- `iac/scripts/production-backup-runtime-live-adapter.py` is a local offline
  adapter prototype that renders deterministic Velero and provider status
  payloads from provider backup fixtures while staying disabled by default.
- `iac/scripts/verify-production-backup-runtime-live-adapter.ps1` compiles and
  runs that adapter, parses `ADAPTER_JSON:`, verifies fail-closed scenarios, and
  proves the adapter has no cluster, network, or process access tokens.

## Production Backup Runtime Operations

The production runtime operations layer defines service ownership, preflight gates, SLOs, restore drills, and tenant isolation before multi-target backup and restore can be enabled.

## Runtime Gap

The current provider-controller runtime supports VM-target backup and VM copy restore only.
The production blueprint defines the desired multi-target contract; the runtime still needs an implementation for `Volume`, `Namespace`, and `KubernetesClusterClaim` backup/restore before the roadmap item is fully complete.

The runtime operations contract now defines the production service envelope,
including Velero CSI data movement, BackupRepository health and maintenance,
object-lock timing after completed backups, restore resource filtering,
namespace mapping, restore modifiers, and tenant-safe copy restore. It is still
not a live controller implementation.

The local canary simulator is also not live controller support. It is an
offline implementation contract that fixes the expected Velero action shape and
fail-closed restore behavior while preserving the current runtime truth:
provider-controller supports VM-target backup and VM copy restore only. The
`RestoreRequest` CRD is widened for the production seam, but lab reconciliation
still rejects non-`VirtualMachineClaim` target kinds and non-`Copy` modes with
`UnsupportedTarget`.

The local live-adapter prototype is one step closer to controller logic because
it parses provider-style fixtures and renders Velero resources plus provider
status patches. It is still offline, disabled by default, and guarded by a
verifier that rejects hidden cluster access and lab overlay references.

The service runtime integration contract
`service-runtime-integration-contract.yaml` now fixes the disabled-by-default
runtime envelope for controller ownership, object-store secret wiring,
immutable storage, restore phase ordering, status/audit events, SLO alert
hooks, and tenant isolation. Its verifier
`verify-production-backup-service-runtime-integration.ps1` fails closed on
missing object-store secrets, mutable bucket policy, unsafe phase ordering,
cross-tenant restore targets, and missing alerts such as
`BackupRuntimeImmutableStorageMissing`.

The runtime cutover skeleton now defines the disabled-by-default production
Deployment/RBAC/Service/PDB shape, object-store secret contract, canary smoke
test, HA promotion patch, and rollback path under `production-backup-runtime`.
It also documents the provider-to-Velero seam:
`BackupPlan` to Velero `Schedule.spec.schedule` and
`Schedule.spec.template` (`BackupSpec`), optional Velero `Backup`, and
`RestoreRequest` to Velero `Restore.spec.backupName` or a backup selected from
`scheduleName`. It still requires a real controller image and implementation
before `Volume`, `Namespace`, and `KubernetesClusterClaim` backup/restore can
be claimed as production ready.

## Promotion Gates

1. Render the overlay with real placeholder values.
2. Verify Velero CSI feature support and snapshot controller health.
3. Prove object-store immutability by attempting and failing to delete a locked
   backup before retention expiry.
4. Run `iac/scripts/verify-production-backup-runtime-simulation.ps1`.
5. Run `iac/scripts/verify-production-backup-runtime-api-seam.ps1`.
6. Run `iac/scripts/verify-production-backup-runtime-live-adapter.ps1`.
7. Run `iac/scripts/verify-production-backup-service-runtime-integration.ps1`.
8. Run `iac/scripts/verify-production-backup-runtime-cutover.ps1`.
9. Promote `gitops/platform-production-backup-runtime` only after
   `platform-production-backup` is healthy.
10. Add `canary-enable-patch.example.yaml` so
   `provider-backup-runtime-controller` runs 1/1 with `RUNTIME_ENABLED=true`.
11. Run the smoke test against only the canary tenant scope.
12. Replace the canary patch with `ha-enable-patch.example.yaml` so the runtime
    scales from `1` to `3` only after the smoke test passes.
13. Run restore drills for VM, volume, namespace, and tenant-cluster targets.
14. Record RPO/RTO evidence and keep the restored objects isolated from the
    source tenant namespace unless an approved in-place restore is requested.
