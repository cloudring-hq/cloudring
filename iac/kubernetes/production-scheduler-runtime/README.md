# Production Scheduler Runtime Cutover

This bundle is the opt-in production runtime cutover skeleton for the provider
scheduler and admission path. It is intentionally separate from
`iac/kubernetes/production-scheduler`, which remains the contract-only
scheduler and transactional admission blueprint.

The skeleton starts disabled with `replicas: 0`, placeholder image and webhook
certificate values, `RUNTIME_ENABLED=false`, and `CANARY_SCOPE=disabled`. The
fail-closed webhook also requires explicit canary namespace and object opt-in
labels before it matches provider claims, so applying the disabled base cannot
silently block the lab or non-canary tenants. Promote it only through
`gitops/platform-production-scheduler-runtime` after the production scheduler
blueprint, CRDs, admission locks, capacity inventory, and offline scheduler
admission seam verifier are all green.

Expected promotion order:

1. Apply the production management-plane substrate and the
   `platform-production-scheduler` overlay.
2. Verify `CapacityCell`, `CapacityReservation`, `AdmissionJournal`, and
   `Project.status.quotaUsage` contracts are installed and served.
3. Run `iac/scripts/verify-production-scheduler-blueprint.ps1`.
4. Run `iac/scripts/verify-production-scheduler-runtime-admission-seam.ps1`.
5. Replace `REPLACE_WITH_PROVIDER_SCHEDULER_RUNTIME_IMAGE` and
   `REPLACE_WITH_PROVIDER_SCHEDULER_WEBHOOK_CA_BUNDLE` through production
   release and certificate automation.
6. Run `iac/scripts/verify-production-scheduler-runtime-cutover.ps1`.
7. Enable the single-replica canary patch from
   `gitops/platform-production-scheduler-runtime/canary-enable-patch.example.yaml`
   so the controller moves from `0` to `1` with `RUNTIME_ENABLED=true`.
8. Run the smoke test against only `provider-scheduler-runtime-canary`.
9. Enable the HA patch from
   `gitops/platform-production-scheduler-runtime/ha-enable-patch.example.yaml`
   so the controller moves from `1` to at least `3` only after smoke passes.

Rollback sets the runtime Deployment back to `replicas: 0`, sets
`RUNTIME_ENABLED=false`, or suspends the Flux Kustomization that points at
`platform-production-scheduler-runtime`. Rollback must not delete
`CapacityReservation`, `AdmissionJournal`, `CapacityCell`, or quota history.

Runtime replay operations are documented in
`provider-scheduler-replay-operations-contract`. The contract starts in
`dry-run`, uses the `provider-scheduler-runtime-replay-owner` Lease for exactly
one replay owner, and allows promotion only through `disabled`, `dry-run`,
`canary-apply`, and `ha-apply` phases. Apply mode requires green quota replay
and admission seam verifiers, a tenant isolation probe, an audit sink, and a
maintenance repair window. Failover must repeat dry-run reconstruction before
any repair action is committed. Replay windows must not exceed
`AdmissionJournal` or `CapacityReservation` retention. The one-replica canary is
only a smoke phase; it is not HA while the runtime PDB expects
`minAvailable: 2`.

Runtime work-queue operations are documented in
`provider-scheduler-workqueue-runtime-contract`. The queue starts disabled, uses
the `provider-scheduler-runtime-workqueue-owner` Lease for exactly one queue
owner, and promotes only through `disabled`, `dry-run`, `canary-consume`, and
`ha-consume`. Events are ordered by namespace, project, claim identity,
generation, and resourceVersion, deduplicated by a claim UID/generation/event
key, and scheduled with weighted-round-robin per project so one tenant cannot
starve another. Retry backoff and dead-letter handling emit audit events and
metrics before any scheduler admission mutation is attempted. Pre-admission
queue events are durable `SchedulerWorkQueueEvent` records, so a replacement
queue owner can recover unacked queue work before reconciling
`AdmissionJournal` and `CapacityReservation` state.

Runtime observability and SLO operations are documented in
`provider-scheduler-observability-slo-contract`. The contract starts disabled
and defines `/healthz`, `/readyz`, and `/metrics`, readiness gates for leader
election, queue ownership, replay ownership, webhook certificates, and audit
sinks, plus queue, replay, and admission metric families. It also defines SLO
objectives, burn-rate alert windows, failure-domain drill evidence, the tenant
fairness dashboard fields, audit retention freshness signals, and owner
escalation. These signals are required before a canary or HA runtime promotion
can claim production-like scheduler readiness.
The SLO contract includes thresholds, burn-rate multipliers, PromQL inputs,
alert severity and routing, and binary failure-domain drill artifacts so the
release gate is observable instead of prose-only.

This is not wired into the Hyper-V lab overlay. The lab provider-controller
continues to own live admission until a production scheduler image, webhook
certificates, replay drills, and multi-cell cutover evidence exist.
