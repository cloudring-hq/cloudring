# Production Backup Runtime Cutover

This bundle is the opt-in production runtime cutover skeleton for the provider
backup service. It is intentionally separate from
`iac/kubernetes/production-backup`, which stays a contract-only backup and DR
blueprint.

The skeleton starts disabled with `replicas: 0` and placeholder image/secret
values. Promote it only through `gitops/platform-production-backup-runtime`
after the production-cell Velero locations, Velero CSI support, snapshot
controller, CSI driver, object-store retention, and provider API CRDs are
validated.

Expected promotion order:

1. Apply the production cell substrate and the `platform-production-backup`
   overlay.
2. Install Velero with `EnableCSI` and node-agent data movement.
3. Verify `BackupStorageLocation`, `VolumeSnapshotLocation`,
   `BackupRepository`, and `VolumeSnapshotClass` health.
4. Replace `REPLACE_WITH_VERSION` and
   `REPLACE_WITH_OBJECT_STORE_SECRET_NAME` through a production secret manager.
5. Run `iac/scripts/verify-production-backup-runtime-simulation.ps1` locally to
   prove the offline reconciliation contract and fail-closed restore behavior.
6. Run `iac/scripts/verify-production-backup-runtime-live-adapter.ps1` locally
   to prove the disabled live-adapter prototype renders the expected Velero and
   provider status payloads without cluster access.
7. Run `iac/scripts/verify-production-backup-runtime-cutover.ps1`.
8. Enable the single-replica canary patch from
   `gitops/platform-production-backup-runtime/canary-enable-patch.example.yaml`
   so the controller moves from `0` to `1` with `RUNTIME_ENABLED=true`.
9. Run the smoke test against only the canary tenant scope.
10. Enable the HA patch from
    `gitops/platform-production-backup-runtime/ha-enable-patch.example.yaml` so
    the controller moves from `1` to at least `3` only after smoke tests pass.

The simulation verifier is not a live controller test. It protects the contract
for `Volume`, `Namespace`, and `KubernetesClusterClaim` targets while the
current lab provider-controller remains VM backup/restore only.

The live-adapter verifier is also local and offline. It exercises the next
controller-adapter seam by rendering deterministic Velero `Schedule`, `Backup`,
`Restore`, and provider status payloads from provider fixtures, then proving
malformed preflight, canary mismatch, cross-tenant denial, missing restore
policy, target collision, and unapproved in-place restore cases create no Velero
manifests. It does not read kubeconfig, invoke `kubectl`, or enable the runtime
in the Hyper-V lab overlay.

## Service Runtime Integration Contract

`service-runtime-integration-contract.yaml` adds the disabled-by-default
`provider-backup-service-runtime-integration-contract` and drill evidence
contract. It binds the future controller implementation to the
`provider-backup-runtime-controller` owner, the object-store secret
`platform-system/provider-backup-runtime-object-store`, Velero
`BackupStorageLocation`, `VolumeSnapshotLocation`, `BackupRepository`, and the
Retain `VolumeSnapshotClass`.

Run the structural verifier before changing this contract:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-service-runtime-integration.ps1
```

The verifier checks `Volume`, `Namespace`, and `KubernetesClusterClaim` target
mapping, immutable object-store requirements, restore phase ordering,
preflight gates, status conditions, audit events, SLO alert hooks, and
tenant-isolation rules. It also proves fail-closed cases for missing owner,
missing object-store secret, mutable bucket policy, unsafe restore phase order,
cross-tenant restore, missing status/audit event, missing SLO hook, metadata
spoofing, comment-only requirements, and Hyper-V lab overlay references.

## Live Controller Contract

`live-controller-contract.yaml` adds the disabled-by-default
`provider-backup-live-controller-contract` for the next live controller
implementation seam. It records the runtime image handoff, `RUNTIME_ENABLED=false`
default, reconcile states, Velero creation boundaries, idempotency keys,
status patches, audit events, SLO hooks, and tenant-isolation rules.

Run the offline verifier before changing the live controller contract:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-live-controller.ps1
```

The verifier compiles `production-backup-live-controller.py`, renders
deterministic accepted and rejected controller outcomes for `Volume`,
`Namespace`, and `KubernetesClusterClaim`, and proves rejected paths create no
Velero objects. It does not read kubeconfig, invoke `kubectl`, use the network,
or enable the Hyper-V lab runtime.

## Runtime Image Seam

`runtime-image-seam.yaml` adds the disabled-by-default
`provider-backup-controller-runtime-image-seam` contract for the executable
controller image boundary. It records the image, entrypoint, required runtime
environment, provider input contract, Velero/status/audit/SLO output contract,
and disabled-to-canary-to-HA promotion gates.

Run the verifier before changing the runtime-image seam:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-controller-runtime-image-seam.ps1
```

The verifier compiles `production-backup-controller-runtime-image-seam.py`,
executes local `BackupPlan` and `RestoreRequest` fixtures for `Volume`,
`Namespace`, and `KubernetesClusterClaim`, checks deterministic Velero
`Schedule`, `Backup`, `Restore`, provider status, audit, SLO, idempotency, and
promotion payloads, then proves fail-closed cases create zero Velero objects.
It does not read kubeconfig, invoke `kubectl`, use the network, or enable the
Hyper-V lab runtime.

## API Runtime Seam

G005 widens the provider `RestoreRequest` API contract so the future
production runtime can accept `VirtualMachineClaim`, `Volume`, `Namespace`, and
`KubernetesClusterClaim` targets with `Copy` or `InPlace` mode. The disabled
runtime skeleton documents the implementation seam from provider objects to
Velero objects:

- `BackupPlan` maps to Velero `Schedule.spec.schedule` and
  `Schedule.spec.template` (`BackupSpec`), with optional one-shot Velero
  `Backup` creation for ad hoc runs.
- `RestoreRequest.spec.source.backupName` maps to Velero
  `Restore.spec.backupName`; `scheduleName` selects a backup from a Velero
  Schedule before restore creation.
- `namespaceMapping`, `resourcePolicyRef`, and `resourceModifierRefs` map to
  Velero restore namespace mapping, resource policy, and restore modifiers.
- Failed validation writes provider status with `FailedValidation`,
  `validationErrors`, and `failureReason` without creating Velero resources.

The lab controller boundary is unchanged: the current Hyper-V provider
controller still supports only VM-target KubeVirt snapshot backup and
`VirtualMachineClaim` `Copy` restore. Any other restore target kind or mode
must remain rejected with `UnsupportedTarget` until the production runtime is a
real, enabled controller.

Reference API shapes:

- https://github.com/vmware-tanzu/velero/blob/2826b98190ec16cf7bfc7e153bb61e8dff23644b/pkg/apis/velero/v1/schedule_types.go
- https://github.com/vmware-tanzu/velero/blob/2826b98190ec16cf7bfc7e153bb61e8dff23644b/pkg/apis/velero/v1/backup_types.go
- https://github.com/vmware-tanzu/velero/blob/2826b98190ec16cf7bfc7e153bb61e8dff23644b/pkg/apis/velero/v1/restore_types.go
- https://velero.io/docs/

Rollback sets the runtime Deployment back to `replicas: 0` or suspends the Flux
Kustomization that points at `platform-production-backup-runtime`. Rollback must
not delete Velero backup locations, backup repositories, retained object-store
data, or already-created recovery points.
