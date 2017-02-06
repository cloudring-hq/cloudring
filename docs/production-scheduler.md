# Production Scheduler And Admission Blueprint

The current Hyper-V lab has first-pass automatic placement, per-cell admission
locks, per-project quota locks, `CapacityReservation` records, and durable
`AdmissionJournal` records. That is enough for the small single-cell demo, but
it is not the final multi-cell provider scheduler.

The opt-in production scheduler blueprint in
`iac/kubernetes/production-scheduler` defines the next runtime contract without
changing the lab overlay by default.

This blueprint does not replace current lab controller runtime behavior.

## Target Shape

- A dedicated `provider-scheduler` Deployment runs three replicas with strict
  hostname spread and a PDB with `minAvailable: 2`.
- Kubernetes `Lease` objects coordinate active scheduler leadership, admission
  locks, and replay ownership.
- `CapacityCell` is the source of cell inventory, service classes, failure
  domains, and available capacity.
- `CapacityReservation` is the committed reservation ledger.
- `AdmissionJournal` is the durable audit and replay surface for accepted,
  rejected, and pending decisions.
- `Project.status.quotaUsage` remains the quota snapshot until a dedicated
  quota and billing event stream exists.

The scheduling pipeline follows the same shape as the Kubernetes scheduler
framework: snapshot inventory, filter infeasible cells, score feasible cells,
reserve capacity, permit backing reconciliation, and commit the decision.

## Required Invariants

- NotReady or draining cells are excluded before scoring.
- Failure-domain constraints must exactly match the selected
  `CapacityCell.spec.failureDomains`.
- Tenant Kubernetes control-plane replica counts must satisfy the selected
  service class.
- The scheduler must acquire project quota and capacity Leases before
  committing an admission decision.
- No KubeVirt, CAPI/CAPK, CDI, storage, or network backing object may be
  created until quota, reservation, and journal commits succeed.
- Rejected claims must not retain Active reservations.
- Admission replay after scheduler failover must be able to reconstruct quota
  and reservation intent from `AdmissionJournal` and unexpired
  `CapacityReservation` objects.

## Promotion Boundary

`gitops/platform-production-scheduler` layers this blueprint on top of the
shared platform overlay for a real management plane. It is intentionally not
referenced by `gitops/platform` or `gitops/cells/lab-hyperv`, because the lab
must stay on the already verified lightweight provider-controller admission
path until a real scheduler image and multi-cell runtime are implemented.

Run:

```powershell
iac/scripts/verify-production-scheduler-blueprint.ps1
```

The verifier checks the scheduler manifests, placement policy, transactional
ledger contract, provider CRD support, GitOps overlay, and lab opt-in boundary.

## Local Admission Seam Prototype

`iac/scripts/production-scheduler-runtime-admission-seam.py` is the first
disabled-by-default runtime seam for the production scheduler contract. It does
not watch Kubernetes and does not replace the lab controller. Instead, it reads
local `SchedulerAdmissionReview` JSON fixtures, evaluates VM and tenant
Kubernetes requests through `Filter`, `Score`, `Reserve`, and `Permit`, and
renders deterministic `ReservationIntent`, `QuotaAdmissionDecision`,
`AdmissionJournal`, and claim status patch payloads.

Run:

```powershell
iac/scripts/verify-production-scheduler-runtime-admission-seam.ps1
```

The verifier checks accepted VM and tenant-cluster payloads, fail-closed
malformed, unknown-cell, quota, stale-capacity, lock, policy, and unsupported
kind cases, no cluster/network/process access, and no scheduler runtime
reference from the Hyper-V lab overlays.

## Local Quota Replay Seam

`iac/scripts/production-scheduler-quota-replay-seam.py` is a second
disabled-by-default offline seam for the scheduler quota ledger. It reads local
`SchedulerQuotaReplay` fixtures, replays accepted `AdmissionJournal` entries
against `CapacityReservation` and `Project` quota snapshots, and renders
deterministic `QuotaReplayEvent`, `QuotaRepairPlan`,
`ReservationReplayDecision`, and claim status patch payloads for
`VirtualMachineClaim` and `KubernetesClusterClaim`.

Run:

```powershell
iac/scripts/verify-production-scheduler-quota-replay-seam.ps1
```

The verifier checks accepted VM and tenant-cluster replay, duplicate
idempotency, fail-closed malformed roots, wrong canary scope, missing journal,
reservation, or quota inputs, stale reservation generation, conflicting
duplicate journals, quota underflow/overflow repair, unknown request kinds,
cross-project replay attempts, no cluster/network/process access, and no
scheduler quota replay reference from the Hyper-V lab overlays.

## Runtime Cutover Skeleton

`iac/kubernetes/production-scheduler-runtime` contains the opt-in scheduler
runtime cutover skeleton. It is separate from the contract-only
`iac/kubernetes/production-scheduler` blueprint and is layered only by
`gitops/platform-production-scheduler-runtime`.

The skeleton starts disabled with `provider-scheduler-runtime-controller`
`replicas: 0`, placeholder image and webhook CA values, `RUNTIME_ENABLED=false`,
`CANARY_SCOPE=disabled`, and `RUNTIME_CUTOVER_MODE=fail-closed`. It also
defines a template-only `provider-scheduler-admission-webhook` with
`failurePolicy: Fail`, canary namespace/object opt-in selectors, canary and HA
patch examples, cutover gates, a smoke-test runbook, and a rollback/fail-closed
runbook.

Run:

```powershell
iac/scripts/verify-production-scheduler-runtime-cutover.ps1
```

The verifier checks the disabled-by-default runtime bundle, fail-closed webhook
contract, GitOps overlay layering, promotion-only boundary, docs, runbooks, and
the fact that `gitops/platform`, `gitops/cells/lab-hyperv`,
`iac/kubernetes/production-scheduler`, and `gitops/platform-production-scheduler`
do not reference the runtime cutover overlay.

## Runtime Replay Operations Contract

`iac/kubernetes/production-scheduler-runtime/replay-operations-contract.yaml`
defines the disabled-by-default replay ownership and failover contract for the
future production scheduler runtime. It does not enable a live replay controller
in the Hyper-V lab. The contract requires exactly one owner of the
`platform-scheduler/provider-scheduler-runtime-replay-owner` Lease, starts in
`dry-run`, and can promote only through `disabled`, `dry-run`, `canary-apply`,
and `ha-apply` phases.

The replay owner must reconstruct accepted admissions from `AdmissionJournal`,
`CapacityReservation`, and `Project` quota snapshots before it plans repair.
Apply phases are allowed to patch only `CapacityReservation` status,
`Project` status, claim status, and provider audit Events. Cross-project replay
is rejected before repair planning, so one tenant cannot repair or mutate
another tenant's admission state.

Audit events are part of the contract: `ReplayDryRunStarted`,
`ReplayDecisionReconstructed`, `ReplayRepairPlanned`, `ReplayRepairApplied`,
`ReplayRejected`, `ReplayFailoverObserved`, and `ReplayLeaseLost`. On failover,
the new owner must emit `ReplayFailoverObserved`, repeat dry-run
reconstruction, and only then consider a maintenance-window repair.

Run:

```powershell
iac/scripts/verify-production-scheduler-replay-operations.ps1
```

The verifier checks replay ownership, lease/failover settings, promotion gates,
audit taxonomy, tenant isolation, docs, and the boundary that the Hyper-V lab
overlays do not reference replay operations runtime resources.

Replay windows must be shorter than the `AdmissionJournal` and
`CapacityReservation` retention windows. The one-replica canary is a smoke
phase only and is not a high-availability state while the runtime PDB expects
`minAvailable: 2`.

## Runtime Work-Queue Contract

`iac/kubernetes/production-scheduler-runtime/workqueue-runtime-contract.yaml`
defines the disabled-by-default event queue contract for the future production
scheduler runtime. It does not enable a live queue in the Hyper-V lab. The
contract requires exactly one owner of the
`platform-scheduler/provider-scheduler-runtime-workqueue-owner` Lease and
promotes only through `disabled`, `dry-run`, `canary-consume`, and
`ha-consume`.

Queue events are ordered by namespace, project, claim kind, claim name, claim
UID, generation, and resourceVersion. Duplicate event identities are suppressed
before `Filter` or `Reserve`, and tenant fairness uses weighted-round-robin per
`projectRef` with bounded in-flight work per project. Backoff and dead-letter
handling emit `WorkQueueBackoffScheduled`, `WorkQueueDeadLettered`,
`WorkQueueOwnerFailover`, `WorkQueueDuplicateSuppressed`, and
`WorkQueueTenantThrottled` audit events plus scheduler workqueue metrics.
Pre-admission queue state is durable as `SchedulerWorkQueueEvent` records, so a
new owner can replay unacked queue events before reconciling
`AdmissionJournal` and `CapacityReservation` state.

Run:

```powershell
iac/scripts/verify-production-scheduler-workqueue-runtime.ps1
```

The verifier checks queue ownership, event ordering, idempotency, per-tenant
fairness, backoff/dead-letter behavior, failover handoff, metrics/audit events,
docs, and the boundary that the Hyper-V lab overlays do not reference
work-queue runtime resources.

## Runtime Observability And SLO Contract

`iac/kubernetes/production-scheduler-runtime/observability-slo-contract.yaml`
defines the disabled-by-default observability and SLO contract for the future
production scheduler runtime. It does not enable monitoring resources in the
Hyper-V lab. The contract requires `/healthz`, `/readyz`, and `/metrics`,
readiness gates for leader election, queue and replay ownership, webhook
certificates, and audit sinks, plus queue, replay, and admission metric
families.

The SLO surface includes admission success rate, replay lag, oldest queue event
age, tenant fairness throttling, and dead-letter rate objectives. Alerting uses
5m, 30m, 2h, and 6h burn-rate windows with rules such as
`SchedulerAdmissionErrorBudgetBurn`, `SchedulerReplayLagHigh`,
`SchedulerWorkQueueBacklogHigh`, `SchedulerTenantFairnessThrottleHigh`,
`SchedulerDeadLetterRateHigh`, and
`SchedulerAuditRetentionSignalMissing`.
The contract defines concrete thresholds, burn-rate multipliers, PromQL query
inputs, alert severity, and routing owners so the SLO layer cannot pass with
only prose.

The tenant fairness dashboard must include project, namespace, queue depth,
in-flight work, retries, dead letters, throttle count, p95 wait seconds, and
last admitted timestamp. Audit retention freshness signals include
`AdmissionJournalRetentionFresh`, `SelfServiceAuditRetentionFresh`,
`SchedulerWorkQueueEventRetentionFresh`, and
`SchedulerReplayAuditRetentionFresh`.
Failure-domain drill evidence must be binary and artifact-backed, including
leader lease transition, node cordon event, `CapacityCell` NotReady condition,
queue/replay owner failover events, and zero duplicate reservation or
cross-tenant mutation reports.

Run:

```powershell
iac/scripts/verify-production-scheduler-observability-slo.ps1
```

The verifier checks health/readiness, queue/replay/admission metrics, SLO
windows, alert rules, failure-domain drill evidence, tenant fairness dashboard
inputs, audit retention signals, owner escalation, docs, and the boundary that
the Hyper-V lab overlays do not reference observability/SLO runtime resources.

## Runtime Gap

This blueprint is not a runtime cutover. The offline admission seam is also not
a runtime cutover. The cutover skeleton is a promotion path, not a live lab
runtime. The provider-controller still owns live lab admission. Production
readiness requires a scheduler implementation, work queue, admission replay
tests, multi-cell failure drills, quota contention tests, and a migration path
that prevents duplicate admission between the current controller and the new
scheduler.
