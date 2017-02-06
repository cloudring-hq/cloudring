# Scaling And Performance

## Horizontal Scaling Strategy

Scale by adding bounded cells, not by making one Kubernetes cluster enormous.

Recommended cell limits should be validated by load tests, but initial planning
targets are:

| Dimension | Starting target per cell |
| --- | ---: |
| Kubernetes nodes | 100-300 |
| KubeVirt compute nodes | 50-200 |
| Running VMs | 1,000-5,000 depending on size |
| Tenant namespaces/projects | 500-2,000 |
| API p99 write latency | SLO-defined, measured under load |

When a cell approaches SLO limits, create a new cell and place new tenants
there. Move tenants by backup/restore, image copy, VM export/import, or tenant
cluster migration workflows.

## API Protection

Use these layers:

- provider API rate limits per tenant and per token;
- Kubernetes API Priority and Fairness;
- horizontally replicated provider controllers with leader election or
  idempotent reconciliation, PodDisruptionBudgets, per-cell sharding, and
  per-`CapacityCell` admission locks for capacity-changing claims;
- controller concurrency limits;
- queue depth and reconcile latency SLOs;
- admission webhook timeout budgets;
- separate read models for portal inventory and search;
- watch cache sizing and etcd metrics alerts;
- tenant-specific quotas for object count, events, secrets, config maps, pods,
  PVCs, snapshots, VMs, and Services.
- conditional read caching with `ETag`/`304 Not Modified` on high-frequency
  provider inventory APIs so dashboards and automation can poll without
  repeatedly transferring the full inventory document.

The opt-in production scheduler blueprint adds the next admission layer for
real multi-cell deployments. It separates placement into a Kubernetes-style
pipeline: inventory snapshot, `Filter`, `Score`, `Reserve`, `Permit`, and
commit. `CapacityCell` stays the inventory source, `CapacityReservation` stays
the committed reservation ledger, and `AdmissionJournal` stays the durable
audit/replay surface. The blueprint also requires Kubernetes `Lease` objects
and `resourceVersion` optimistic concurrency for scheduler leadership,
per-project quota locks, per-cell capacity locks, and replay ownership.

The lab now has a concrete APF split for the provider API path:

- `platform-control` protects provider-controller, provider-portal, Flux, and
  CAPI/CAPK service accounts plus `platform:admins`;
- `tenant-limited` handles normal namespaced tenant self-service writes and
  reads with `ByNamespace` isolation;
- `tenant-bulk-low` catches tenant `list`/`watch` bursts separately so
  inventory polling or noisy tenants do not share the same queue as provider
  control loops.

`iac/scripts/verify-api-fairness.sh` checks those lanes and runs a small
impersonated tenant API burst while platform `/readyz`, provider-controller,
and Flux reads continue to succeed. `iac/scripts/verify-provider-api-load.sh`
adds the bounded portal/API read-load gate: it sends concurrent conditional
summary reads across all Ready portal replicas, requires a high `304` ratio,
checks response-byte savings and p95 latency, and continuously probes
Kubernetes `/readyz`, provider-controller, Flux, and the routed tenant API while
the read load is running.

## Load Tests

Required tests before claiming high-scale readiness:

- Kubernetes API list/watch/write load with tenant-like objects;
- KubeVirt VM create/start/stop/delete bursts;
- CDI image import concurrency;
- storage volume create/attach/detach/rebuild;
- Cilium policy churn and service churn;
- MetalLB/BGP route churn;
- node drain with live migration/restart;
- noisy tenant attempting to exhaust API, events, images, PVCs, and LB IPs.

## Observability SLOs

Track:

- apiserver request duration and inflight requests;
- APF queue length and rejected requests;
- etcd fsync, commit latency, db size, leader changes;
- controller queue depth and reconcile duration;
- provider portal summary request status, cache mode, response bytes, refresh
  latency, and refresh errors;
- Cilium agent health, policy regeneration time, drops;
- KubeVirt virt-handler and virt-controller errors;
- storage latency, rebuild throughput, replica health;
- tenant quota usage and throttling;
- per-cell capacity remaining.

## Current Lab HA Control Loop

The management control loops now follow the same availability shape expected
from production cell controllers:

- provider-controller, Cluster API core, kubeadm bootstrap/control-plane,
  CAPK, and cert-manager controller/cainjector/webhook run with three replicas;
- preferred pod anti-affinity and topology spread across Hyper-V-backed nodes;
- PodDisruptionBudget with `minAvailable: 2` for each critical controller;
- provider-controller uses a Kubernetes `Lease` in `platform-system` so only
  the current leader performs reconciliation while standby replicas remain
  ready for failover;
- provider-controller runs from the local
  `localhost/platform-provider-controller:dev` runtime image with pinned Python
  dependencies baked in, so pod startup, failover, and rolling updates no
  longer depend on PyPI or runtime `pip install`;
- each provider-controller replica exposes `/healthz` and Prometheus-style
  `/metrics` through the `provider-controller-metrics` Service. The current
  lab metrics include leader state, reconcile success/error/standby counters,
  reconcile duration sum/count, last success/error timestamps, and
  `provider_controller_shard_info`;
- provider-controller is shard-aware and the lab now runs the generated
  two-shard active-active topology. Each shard has three HA replicas, its own
  Lease, PDB, and metrics Service; namespaced tenant reconcilers split
  namespaces by stable hash or `CONTROLLER_NAMESPACE_ALLOWLIST`, while global
  resources are handled only by shard `0`;
- `iac/kubernetes/provider-controller/sharded-controller.yaml` is the active
  controller runtime topology. GitOps also includes the base
  `rendered-controller.yaml` manifest for namespace/RBAC and rollback material,
  but patches the base `provider-controller` Deployment to `replicas: 0` so the
  live runtime does not run both singleton and sharded topologies;
- tenant Kubernetes APIs are exposed through provider-owned gateway Deployments
  in `capk-system`, not tenant-created LoadBalancers. The lab gateway pool is
  `n1,n3`, proxies avoid the tenant VMI host to bypass the KubeVirt masquerade
  hairpin path, and `externalTrafficPolicy=Cluster` keeps the routed VIP
  reachable from all provider/controller nodes;
- provider-controller records routed endpoint health with `/readyz` hysteresis:
  `endpointProbeReachable`, `endpointFailureCount`, `EndpointReachable`, and
  `lastKnownApiEndpoint` distinguish transient probe loss from a real degraded
  tenant API;
- Kubernetes APF separates platform service accounts/admins from tenant
  interactive and tenant bulk list/watch traffic, with tenant flows
  distinguished by namespace;
- idempotent reconciliation keeps repeated leader runs convergent on the same
  provider API, CAPI, CAPK, and certificate state;
- capacity admission uses a short-lived `coordination.k8s.io/Lease` per
  `CapacityCell` (`capacity-admission-<cell>`) so active-active controller
  shards cannot concurrently admit VM or tenant Kubernetes claims into the
  same cell. Admitted claims store `status.admission.observedGeneration`; once
  the current generation is observed, normal reconciliation renews the
  reservation without reacquiring the admission lock.
- project quota admission uses a short-lived `coordination.k8s.io/Lease` per
  `Project` (`project-quota-admission-<project>`) around the quota snapshot,
  capacity admission, and reservation/status write. This keeps active-active
  shards and future multi-cell placement paths from concurrently
  oversubscribing one tenant's CPU, memory, VM count, or tenant-cluster quota.
- admission decisions are copied into cluster-scoped `AdmissionJournal`
  objects. The journal is write-once per claim UID/generation/decision/reason
  and records the quota snapshot, capacity cell, service class, admission lock
  names, and controller shard identity. This gives future scheduler-grade
  placement a durable audit/replay surface without making tenant-visible claim
  status the only record of why a request was accepted or rejected.
- the global controller shard prunes old and excessive control-plane durable
  records: `AdmissionJournal` by `projectRef`, `SelfServiceAuditEvent` by
  namespace. This bounds etcd/API object growth during high write-load while
  keeping retention tenant-fair.
- the provider portal keeps the last `/api/summary` payload when a write marks
  the cache stale, so temporary API Priority and Fairness 429/backpressure does
  not turn the self-service console into an error page immediately after a
  create/delete operation.
- explicit `/api/summary?fresh=1` requests synchronously refresh the target
  portal replica when its local refresh lock is free. If another refresh is
  already running or the API is temporarily backpressured, the endpoint returns
  bounded stale data or a retryable error instead of tying up HTTP workers.
- `/api/summary` returns a stable weak `ETag` computed from semantic provider
  inventory while excluding volatile cache metadata, per-replica generation
  timestamps, transient Kubernetes Events, and reservation heartbeat/expiry
  timestamps. Clients can revalidate with `If-None-Match` and receive
  `304 Not Modified`, while the portal still records the cache mode and request
  status in Prometheus metrics. The lab keeps each replica's summary cache
  fresh for 30 seconds so HPA scale-out and bounded conditional-read tests do
  not repeatedly fan out to Kubernetes. The read model also caps transient
  Kubernetes Events plus recent audit/journal records before serialization.
  This keeps dashboard polling from becoming a bandwidth and JSON parsing
  amplifier before the production inventory/search service exists.
- the provider portal is the first stateless provider-facing HTTP surface under
  HPA control. Its Deployment leaves `spec.replicas` to the autoscaling
  subresource, keeps a floor of six replicas, caps the lab at nine replicas,
  and scales on CPU and memory while the PDB keeps at least four replicas
  available for voluntary disruption. Leader-elected controller shards remain
  scaled by shard count and per-shard standby replicas instead of HPA, because
  extra pods inside one shard improve failover but not reconcile throughput.
- portal write requests are rate-limited by authenticated subject and tenant
  namespace before the portal service account calls Kubernetes. The lab uses a
  shared Kubernetes `Lease` counter with optimistic concurrency so the limit is
  consistent across HPA-scaled portal replicas. This closes the APF visibility
  gap where the apiserver sees all portal writes as
  `system:serviceaccount:platform-system:provider-portal` instead of the real
  tenant caller.

Production controllers should extend this active-active pattern with more
tenant or capacity-cell shards, external work queues, richer per-kind reconcile
metrics, and signed/published release images.

## Current Lab Capacity Guardrail

The current Hyper-V profile is deliberately small: three management/capacity
VMs with 4 vCPU and 7 GiB RAM each. After management controllers were hardened
to three replicas, a single tenant worker VM was enough to exhaust memory on one
node and temporarily degrade k3s. The lab therefore treats worker scale-out as a
capacity-admission scenario, not a default action.

Live guardrail:

- `MAX_TENANT_CLUSTER_WORKERS_PER_POOL=0` in the provider-controller Deployment;
- `tenant-a/routable-cluster` worker pools remain at replicas `0`;
- `CapacityCell lab-hyperv` reports live node inventory and service-class
  limits;
- `VirtualMachineClaim` and `KubernetesClusterClaim` status includes
  `admission` with selected cell, service class, estimated footprint, and
  effective worker replicas;
- provider-level `Project` quota usage reports admitted VM and tenant
  Kubernetes consumption; VM and tenant Kubernetes quota admission reject
  requests that would exceed self-service CPU, memory, VM count, or tenant
  cluster count before backing KubeVirt/CAPI resources are created;
- per-project quota admission locks prevent concurrent active-active
  reconciles from admitting multiple not-yet-reserved claims against the same
  tenant quota snapshot;
- `AdmissionJournal` records preserve accepted, rejected, and pending admission
  decisions for VM and tenant Kubernetes claims; tenant RBAC cannot read them,
  while platform admins and `/api/summary` can inspect recent decisions;
- global-shard retention deletes old `AdmissionJournal` and
  `SelfServiceAuditEvent` records and preserves fresh records, with Prometheus
  counters for deleted object totals;
- automatic placement filters cells by requested `placement.failureDomains`,
  rejects impossible constraints with `FailureDomainNotFound`, skips NotReady
  cells, and scores Ready cells by available CPU/memory before admitting a
  request;
- admitted claims create provider-internal `CapacityReservation` objects;
  `CapacityCell.status.reserved` and `CapacityCell.status.available` are
  computed from active reservations, with admitted-claim fallback during
  reconciliation. Reservations carry heartbeat, TTL, and expiry timestamps;
  stale reservations are ignored for capacity accounting, and oversized/rejected
  claims do not retain reservations or backing KubeVirt/CAPI resources;
- `iac/scripts/verify-capacity-admission-lock.sh` holds a synthetic
  `CapacityCell` Lease, verifies a temporary VM claim stays
  `PendingAdmission` without a VM or reservation, then releases the Lease and
  verifies the claim becomes `Ready` with an Active reservation. The verifier
  temporarily raises and restores tenant-c quota because the steady-state
  smoke VM already consumes most of the tiny lab namespace quota;
- `iac/scripts/verify-project-quota-admission-lock.sh` holds a synthetic
  `Project` Lease, verifies a temporary VM claim stays `PendingAdmission` with
  `ProjectQuotaAdmissionLocked` and no VM/reservation, then releases the Lease
  and verifies the claim becomes `Ready` with an Active reservation;
- tenant Kubernetes service classes can declare control-plane replica bounds;
  the lab exposes an HA class but rejects 3-control-plane claims because the
  current cell limit is intentionally `maxControlPlaneReplicas=1`;
- new CAPK tenant nodes use CDI `DataVolume` root disks on Longhorn instead of
  ephemeral `containerDisk` roots;
- the routable tenant control-plane and standalone demo VMs stay available for
  API, isolation, CAPI, KubeVirt, and add-on workflow evaluation. The older
  duplicate `demo-cluster` was removed from the live footprint after n1 etcd
  readiness degraded under the tiny Hyper-V memory profile.

Production path:

- inventory-driven placement before creating KubeVirt VMs;
- per-cell admission based on allocatable memory, storage, and disruption
  budget;
- the opt-in production scheduler/admission blueprint under
  `iac/kubernetes/production-scheduler`, then a real scheduler runtime across
  multiple real cells with transactional reservation decisions, placement
  constraints, anti-affinity, stronger cross-controller stale-reservation
  reaping, and durable admission replay;
- active-active provider-controller shard sets by tenant/cell, each with its
  own Lease and work queues so reconciliation throughput scales horizontally
  without a single active global loop;
- multi-control-plane tenant service classes with spread/anti-affinity across
  failure domains and tested replacement after management node loss;
- provider-managed routed SDN/LB endpoints for tenant APIs instead of the
  lab-internal CAPK ClusterIP/hairpin-sensitive path;
- quota and billing usage pipelines backed by durable events, not only current
  CR status snapshots;
- the opt-in `platform-production-backup-runtime` overlay with the
  `provider-backup-runtime-controller` held at `replicas: 0` until Velero CSI,
  object-store retention, BackupRepository health, and tenant isolation smoke
  evidence are captured;
- production backup runtime operations with RPO/RTO SLOs, BackupRepository
  maintenance, immutable-storage retention checks, and restore drills that
  include tenant isolation probes before upgrade waves;
- transactional multi-cell quota and reservation admission integrated with the
  scheduler-grade placement path, durable quota events, and concurrent
  admission protection;
- service-class limits that can be raised per cell without editing claims;
- load tests that include failed scheduling, node pressure, and noisy tenant
  retries.
