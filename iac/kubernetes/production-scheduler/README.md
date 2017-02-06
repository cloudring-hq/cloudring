# Production Scheduler Blueprint

This directory is an opt-in production scheduler and admission template for a
multi-cell provider control plane. It is not referenced by the Hyper-V lab
overlay.

The current lab controller already has first-pass placement, quota admission,
per-cell and per-project Leases, `CapacityReservation` objects, and durable
`AdmissionJournal` records. This blueprint defines the next production runtime
contract: a dedicated highly available scheduler service that can evaluate
many real cells, reserve capacity transactionally, and replay admission state
after failover.

## Contract

- The scheduler uses a Kubernetes-style `Filter`, `Score`, `Reserve`,
  `Permit`, and `Commit` pipeline for provider claims.
- `CapacityCell` remains the source of cell inventory, service classes, and
  failure-domain constraints.
- `CapacityReservation` remains the committed reservation ledger.
- `AdmissionJournal` remains the durable admission audit and replay surface.
- `Project.status.quotaUsage` remains the provider quota usage snapshot until
  a dedicated billing/quota event pipeline is added.
- Kubernetes `Lease` objects and `resourceVersion` optimistic concurrency are
  the coordination primitives for active replicas, admission locks, and replay
  ownership.
- No backing KubeVirt, CAPI/CAPK, CDI, storage, or network resource may be
  created until quota admission, cell reservation, and journal commit have all
  succeeded.

## Promotion Checklist

1. Build and publish a real provider-scheduler image.
2. Replace every `REPLACE_WITH_*` placeholder.
3. Decide shard count, work-queue backend, and replay ownership model.
4. Run `iac/scripts/verify-production-scheduler-blueprint.ps1`.
5. Run `iac/scripts/verify-production-scheduler-runtime-admission-seam.ps1`
   against the local disabled runtime seam before wiring a live controller.
6. Promote in a non-lab management plane with at least two real cells.
7. Validate admission replay, lock contention, cell outage, quota rejection,
   and rollback drills before replacing the current controller admission path.

This blueprint is intentionally honest: it defines the production scheduler
contract and GitOps shape, but it does not replace the lab provider-controller
runtime yet.

## Local Admission Seam

`iac/scripts/production-scheduler-runtime-admission-seam.py` is a
disabled-by-default offline seam for scheduler/admission behavior. It parses
local `SchedulerAdmissionReview` JSON fixtures, evaluates `Filter`, `Score`,
`Reserve`, and `Permit` decisions for `VirtualMachineClaim` and
`KubernetesClusterClaim`, and renders deterministic `ReservationIntent`,
`QuotaAdmissionDecision`, `AdmissionJournal`, and status patch payloads.

Run:

```powershell
iac/scripts/verify-production-scheduler-runtime-admission-seam.ps1
```

The verifier proves accepted VM and tenant-cluster decisions, malformed and
unsafe fail-closed cases, no cluster/network/process access, and no Hyper-V lab
overlay reference to the scheduler runtime seam. It is still only an offline
implementation contract; it does not deploy a scheduler controller.
