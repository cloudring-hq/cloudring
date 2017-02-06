# Platform Runtime Blockers Closure

This note records the disabled-by-default closure layer for the aggregate
platform blockers found during the G015 final gate.

## Closed By This Layer

- Production scheduler runtime replacement is validated by
  `verify-production-scheduler-runtime-admission-seam.ps1`. The proof covers
  multi-cell `VirtualMachineClaim` and `KubernetesClusterClaim` placement,
  `Filter`/`Score`/`Reserve`/`Permit` ordering, deterministic
  `ReservationIntent`, `QuotaAdmissionDecision`, `AdmissionJournal`, and status
  patches.
- Scheduler-grade transactional quota admission is validated by
  `verify-production-scheduler-quota-replay-seam.ps1` and the aggregate
  `verify-production-platform-runtime-blockers-closure.ps1` wrapper. The proof
  covers concurrent admission lock requirements, duplicate journal idempotency,
  durable quota replay events, repair plans, and cross-project fail-closed
  behavior.
- The aggregate wrapper also reruns scheduler cutover, workqueue,
  replay-operations, observability SLO, and blueprint verifiers so the runtime
  closure remains tied to the existing production scheduler bundle.

## Still Accounted As Live-Lab Gaps

- Full Cluster API + CAPK tenant cluster lifecycle scale, upgrade, and
  kubeconfig handoff require a live larger-cell Hyper-V run with CAPK controllers
  and tenant cluster workloads.
- Real multi-control-plane tenant clusters with placement, anti-affinity, and
  restart/replacement tests require a larger cell than the current offline
  verifier surface.
- Replacing the lab self-hosted JWKS issuer with an external OIDC/JWKS provider
  remains a production identity evidence task. The production identity contract
  and GitOps overlay exist, and the lab runtime now exercises the same
  `oidc-jwks` RS256 validation path with deterministic keys for smoke testing.

The closure is intentionally disabled-by-default. It must not add production
scheduler, quota replay, CAPK lifecycle, or OIDC runtime resources to the
current Hyper-V lab overlays unless a future opt-in promotion explicitly does so.
