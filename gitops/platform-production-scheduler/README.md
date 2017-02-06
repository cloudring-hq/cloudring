# Platform Production Scheduler Overlay

This opt-in GitOps overlay layers the production scheduler and transactional
admission blueprint on top of the shared platform components.

It is intentionally separate from `gitops/platform` so the current Hyper-V lab
does not start a placeholder scheduler or require production work-queue,
identity, observability, and multi-cell prerequisites.

Before promotion:

1. Replace `REPLACE_WITH_PROVIDER_SCHEDULER_IMAGE`.
2. Decide whether the scheduler runs in the management plane or per-cell.
3. Promote with at least two real `CapacityCell` objects.
4. Run `iac/scripts/verify-production-scheduler-blueprint.ps1`.
5. Run scheduler admission replay, lock contention, and failed-cell drills.
