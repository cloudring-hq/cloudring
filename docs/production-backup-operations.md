# Production Backup Runtime Operations

The production backup/DR blueprint defines the backup targets and restore
templates. The runtime operations contract adds the service ownership,
preflight gates, SLOs, restore drills, and tenant isolation rules needed before
the blueprint can become a production service.

## Runtime Ownership

The provider backup service owns `BackupPlan` and `RestoreRequest`
reconciliation. In production it should translate those provider API objects
into Velero `Schedule`, `Backup`, and `Restore` resources while publishing
provider-facing status for RPO, RTO, last successful backup, restore drill
evidence, repository health, and tenant-visible restore state.

Required runtime dependencies:

- Velero with CSI support and node-agent data movement.
- CSI snapshot CRDs, snapshot-controller, and a production CSI driver with
  `VolumeSnapshot` support.
- Off-cell `BackupStorageLocation` and `VolumeSnapshotLocation` objects.
- `BackupRepository` health and repository maintenance for every protected
  namespace that uses CSI data movement.
- A production secret manager for object-store credentials.
- Object-lock or equivalent retention for immutable destinations, applied only
  after backups reach `Complete`.

## Restore Drills

Every production cell must run restore drills monthly and before upgrade waves.
The required matrix covers `VirtualMachineClaim`, `Volume`, `Namespace`, and
`KubernetesClusterClaim`.

Each drill must capture:

- `velero backup describe` and `velero restore describe`;
- `BackupStorageLocation`, `VolumeSnapshotLocation`, and `BackupRepository`
  health;
- restored PVC, namespace, provider API, and tenant-cluster readiness;
- source workload unchanged evidence for copy restore;
- RPO/RTO timestamp calculation;
- tenant isolation probe between source and restored namespaces.

## Tenant Isolation

Tenant-visible restores default to copy restore. Namespace and tenant-cluster
restores require `namespaceMapping`, resource filtering or resource policies,
and restore resource modifiers when labels, namespaces, or provider ownership
must change.

In-place restore requires provider-admin approval. Cross-tenant restore, restore
to a namespace outside token namespace scope, and restore from a BackupPlan the
tenant cannot read must fail closed.

## Runtime Cutover Skeleton

`iac/kubernetes/production-backup-runtime` contains the opt-in runtime cutover
skeleton for the provider backup service. It is separate from the
contract-only `iac/kubernetes/production-backup` bundle and is layered only by
`gitops/platform-production-backup-runtime`.

The cutover skeleton defines a disabled-by-default
`provider-backup-runtime-controller` Deployment, ServiceAccount, RBAC, metrics
Service, and PodDisruptionBudget. The Deployment keeps `replicas: 0` until a
production operator replaces the image tag, wires the object-store secret from a
production secret manager, and proves Velero CSI, `BackupStorageLocation`,
`VolumeSnapshotLocation`, `BackupRepository`, and `VolumeSnapshotClass` health.

Before scaling the runtime from `0` to at least `3`, run
`iac/scripts/verify-production-backup-runtime-cutover.ps1`, enable the
`canary-enable-patch.example.yaml` patch so one controller replica runs with
`RUNTIME_ENABLED=true`, and run the cutover smoke runbook against only the
canary scope. Promote to the HA patch only after the canary passes. Rollback is
fail-closed: set the Deployment back to `replicas: 0`, set
`RUNTIME_ENABLED=false`, or suspend the Flux Kustomization for
`platform-production-backup-runtime`, while preserving backup locations, backup
repositories, retained snapshots, and object-store retention.

## API Runtime Seam

The provider API now exposes the production restore contract needed by the
future runtime: `RestoreRequest.spec.target.kind` accepts
`VirtualMachineClaim`, `Volume`, `Namespace`, and `KubernetesClusterClaim`, and
`spec.target.mode` accepts `Copy` and `InPlace`. The API also carries Velero
restore policy fields: `namespaceMapping`, `resourcePolicyRef`,
`resourceModifierRefs`, source `backupName`, source `scheduleName`, and
fail-closed approval fields for provider-admin and cross-tenant decisions.

The disabled runtime skeleton documents the controller implementation seam:
`BackupPlan` reconciles to Velero `Schedule.spec.schedule` plus
`Schedule.spec.template` (`BackupSpec`) and optional Velero `Backup`;
`RestoreRequest` reconciles to Velero `Restore.spec.backupName` or a backup
selected from `scheduleName`, plus namespace mapping, resource policy, and
restore modifiers. Failed preflight or policy validation must create no Velero
objects and must publish `FailedValidation`, `validationErrors`, and
`failureReason` on provider status. Production admission must use
`failurePolicy: Fail`.

This is an API/runtime integration seam only. The Hyper-V lab controller still
uses KubeVirt snapshots for VM backup and rejects any `RestoreRequest` where
the target kind is not `VirtualMachineClaim` or the mode is not `Copy` with
`UnsupportedTarget`.

## Local Canary Simulation

`iac/scripts/simulate-production-backup-runtime-canary.py` is a local,
non-cluster simulator for the production runtime contract. It emits a
deterministic `SIMULATION_JSON:` payload that models provider reconciliation of
`BackupPlan` and `RestoreRequest` into Velero `Schedule`, `Backup`, `Restore`,
and provider status actions for `Volume`, `Namespace`, and
`KubernetesClusterClaim` targets.

Run the verifier before claiming runtime-contract changes:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-runtime-simulation.ps1
```

The verifier compiles the simulator, executes it offline, checks the Velero
action counts, checks fail-closed restore boundaries, and scans the simulator
source for forbidden cluster or network access tokens. This is an offline
implementation contract only; it does not prove a live production controller.

## Local Live Adapter Prototype

`iac/scripts/production-backup-runtime-live-adapter.py` is the next local,
disabled-by-default adapter seam. It parses provider-style `BackupPlan`,
`RestoreRequest`, and preflight fixtures and emits deterministic `ADAPTER_JSON:`
payloads for Velero `Schedule`, `Backup`, `Restore`, and provider status patch
actions for `Volume`, `Namespace`, and `KubernetesClusterClaim` targets.

Run the verifier before changing the production backup runtime adapter contract:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-runtime-live-adapter.ps1
```

The verifier checks one rendered Velero action set per target and proves
malformed preflight, canary mismatch, denied cross-tenant restore, missing
restore safety controls, target collision, and unapproved in-place namespace or
tenant-cluster restore all emit zero Velero manifests with failed provider
status. It also scans for forbidden cluster, network, and process access tokens
and confirms the Hyper-V lab overlays do not reference the adapter.

## Production Backup Service Runtime Integration

`iac/kubernetes/production-backup-runtime/service-runtime-integration-contract.yaml`
adds the template-only
`provider-backup-service-runtime-integration-contract` for the future live
backup service. The contract keeps the runtime disabled by default, assigns
ownership to `provider-backup-runtime-controller`, and requires the object-store
secret `platform-system/provider-backup-runtime-object-store` plus Velero
`BackupStorageLocation`, `VolumeSnapshotLocation`, `BackupRepository`, and
Retain `VolumeSnapshotClass` wiring before any `Backup`, `Schedule`, or
`Restore` object can be created.

The integration contract defines target mapping for `Volume`, `Namespace`, and
`KubernetesClusterClaim`, immutable storage checks, restore phases from
`request-accepted` through `cleanup`, preflight gates, provider status
conditions, audit events such as `RestoreTenantIsolationRejected`, and SLO hooks
including `backup_runtime_cross_tenant_denied_total`. Missing ownership,
missing credentials, mutable storage, unsafe phase ordering, cross-tenant
restore targets, absent audit/status events, or absent SLO hooks fail closed.

Run the verifier before changing the runtime integration contract:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-service-runtime-integration.ps1
```

This is still not a live controller in the Hyper-V lab. The verifier keeps
`gitops/platform`, `gitops/cells/lab-hyperv`, and the contract-only production
backup overlays free of backup service runtime integration references.

## Production Backup Live Controller Contract

`iac/kubernetes/production-backup-runtime/live-controller-contract.yaml` adds
the disabled-by-default live controller implementation seam. The contract fixes
the controller image handoff, `RUNTIME_ENABLED=false` default, reconcile state
ordering, Velero `Schedule`/`Backup`/`Restore` creation boundaries,
idempotency keys, status patch requirements, audit events, SLO hooks, and
tenant-isolation rules.

Run the verifier before changing this live controller contract:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-live-controller.ps1
```

The verifier uses only local JSON fixtures and
`production-backup-live-controller.py`. Accepted `Volume`, `Namespace`, and
`KubernetesClusterClaim` cases render deterministic Velero objects, status
patches, audit events, and SLO hooks. Rejected cases such as duplicate
idempotency keys, mutable storage, cross-tenant restore, missing status patch,
missing audit event, and missing SLO hook create zero Velero objects and emit
`BackupLiveControllerRejected`.

## Production Backup Controller Runtime Image Seam

`iac/kubernetes/production-backup-runtime/runtime-image-seam.yaml` and
`iac/scripts/production-backup-controller-runtime-image-seam.py` define the next
disabled-by-default runtime-image boundary. The seam fixes the controller image
handoff, `/usr/local/bin/provider-backup-controller` entrypoint, required
runtime environment, `BackupPlan` and `RestoreRequest` inputs, Velero
`Schedule`/`Backup`/`Restore` outputs, provider status patches, audit events,
and SLO hooks including `backup_runtime_idempotency_replay_total`.

Run the verifier before changing this runtime-image seam:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-controller-runtime-image-seam.ps1
```

The verifier proves `Volume`, `Namespace`, and `KubernetesClusterClaim` happy
paths render deterministic Velero objects and provider-visible status while the
runtime remains disabled by default. It also proves malformed fixtures,
unsupported targets, missing image handoff, `RUNTIME_ENABLED=true` without the
canary scope, duplicate idempotency keys, preflight failure, mutable storage,
cross-tenant restore, missing status, missing audit, and missing SLO cases fail
closed with zero Velero objects. The Hyper-V lab overlays remain free of
Production Backup Controller Runtime Image Seam resources.

## Current Gap

The Hyper-V lab remains on VM-target KubeVirt snapshot/copy restore. This
operations contract is opt-in production guidance; it does not install or run a
production backup service in the lab. The provider-controller runtime still
needs the multi-target implementation for `Volume`, `Namespace`, and
`KubernetesClusterClaim`; the cutover skeleton and local simulator only define
the production deployment and reconciliation contracts, guardrails, smoke test,
and rollback path. The provider API restore contract is now widened for the
future runtime, but the live lab controller remains VM-target copy-restore only
until the production runtime implementation is built and promoted.

This operations contract does not install or run a production backup service in the lab; the simulator and local adapter are offline validation helpers only.
