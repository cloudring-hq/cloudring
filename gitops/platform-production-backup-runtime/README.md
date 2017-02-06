# Platform Production Backup Runtime Overlay

This overlay is the promotion-only desired-state entry point for the provider
backup runtime cutover skeleton. It layers `platform-production-backup` first
and then adds `iac/kubernetes/production-backup-runtime`.

Do not apply it to the current Hyper-V lab. Replace all placeholders, verify
Velero CSI support, verify object-store immutability, run
`iac/scripts/verify-production-backup-runtime-cutover.ps1`, and keep the
runtime Deployment at `replicas: 0` by default.

For cutover, first add `canary-enable-patch.example.yaml` to this overlay's
`patches` list so the controller runs 1/1 with `RUNTIME_ENABLED=true` and
`CANARY_SCOPE=provider-backup-runtime-canary`. Run the smoke test against only
that canary scope. After it passes, replace the canary patch with
`ha-enable-patch.example.yaml` so the runtime scales to at least three replicas
only after `BackupStorageLocation`,
`VolumeSnapshotLocation`, `BackupRepository`, and tenant isolation probes are
green.
