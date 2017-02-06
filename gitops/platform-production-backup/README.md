# Platform Production Backup Overlay

This overlay layers the production backup and disaster-recovery blueprint over
the shared platform desired state.

Do not apply it to the current Hyper-V lab as-is. Replace all placeholders,
install Velero with CSI support, verify object-store immutability, run both
backup blueprint verifiers, and complete the provider-controller runtime
cutover for volume, namespace, and tenant cluster backup/restore targets before
promoting this overlay to a real cell. The runtime cutover skeleton is a
separate promotion step in `gitops/platform-production-backup-runtime`.
