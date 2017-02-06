# Production Backup And DR Blueprint

This directory is an opt-in production backup and disaster-recovery template.
It extends the existing lab `BackupPlan` / `RestoreRequest` model toward
remote, immutable, multi-target protection without applying the backup service
to the small Hyper-V lab by default.

The blueprint assumes these dependencies exist in the target cell:

- Velero CRDs and controller with CSI support enabled.
- Kubernetes CSI snapshot CRDs, snapshot controller, and a CSI driver that
  supports snapshots for the production storage class.
- An off-cell S3-compatible object store with immutability/Object Lock or an
  equivalent retention control.
- Production secret-manager wiring for object-store credentials.
- A restore approval workflow for tenant-visible restores and provider-admin
  break-glass restores.

The lab currently proves VM-target `BackupPlan` and `RestoreRequest` with
KubeVirt `VirtualMachineSnapshot` and copy restore. This blueprint adds the
production contract for `Volume`, `Namespace`, and `KubernetesClusterClaim`
targets, but the provider-controller runtime cutover for those target kinds is
still a follow-up.

The runtime operations contracts in this directory add the service ownership,
preflight checks, restore-drill SLOs, BackupRepository maintenance, immutable
object-store caveat, and tenant restore isolation rules required before that
runtime cutover.

## Promotion Checklist

1. Install Velero with CSI support in the target cell.
2. Replace every `REPLACE_WITH_*` placeholder.
3. Verify object-store immutability and retention before storing tenant data.
4. Run backup and restore drills for VM, volume, namespace, and tenant-cluster
   targets.
5. Run `iac/scripts/verify-production-backup-runtime-blueprint.ps1`.
6. Promote through GitOps only after the provider API exposes tenant-safe
   restore semantics for every target kind being enabled.
