# Provider Roadmap

## Phase 1: Harden The Current Lab

- [x] Add Pod Security labels and policy-as-code.
- [x] Add tenant RBAC and service exposure controls.
- [x] Add GitOps layout for platform components.
- [x] Add API Priority and Fairness templates.
- [x] Add repeatable validation scripts.
- [x] Add provider API CRD contracts for Projects, VMs, and tenant clusters.
- [x] Run the initial provider controller as an HA workload with spread and PDB.

## Phase 2: Self-Service Control Plane

- [x] Implement initial provider controller for `Project` and
  `VirtualMachineClaim`.
- [x] Install Cluster API + CAPK runtime in the lab management cluster.
- [x] Extend the provider controller to reconcile `KubernetesClusterClaim`
  into Cluster API Provider KubeVirt resources.
- [x] Complete tenant cluster bootstrap to CAPI `Ready` and validate generated
  kubeconfig access.
- [x] Install a tenant-cluster CNI through a provider-managed add-on workflow.
- [x] Remove single-replica SPOFs from CAPI/CAPK/cert-manager management
  controllers in the lab with replicas, spread, and PDBs.
- [x] Add a lab worker-scale guardrail after validating that the current
  Hyper-V resource profile cannot safely host tenant workers alongside the HA
  management stack.
- [x] Add v1alpha1 API contracts for Images, Volumes, Networks, FirewallRules,
  BackupPlans, and AccessGrants so portal and GitOps work can target the final
  provider surface instead of raw substrate APIs.
- [x] Add `CapacityCell` API and lab inventory reconciliation so the provider
  can reason about cells as bounded horizontal scale units.
- [x] Add basic capacity admission status for VM and tenant Kubernetes claims
  using `CapacityCell` service classes and lab worker replica caps.
- [x] Add reservation-aware `CapacityCell.status` and reject oversized VM
  claims before backing resources are created.
- [x] Add provider-controller leader election with Kubernetes Lease and verify
  leader failover after pod loss.
- [x] Add lab backing reconciliation for image catalog status, tenant volumes,
  network/firewall policy, and access grants.
- [x] Replace new CAPK tenant node `containerDisk` roots with persistent
  CDI DataVolumes on Longhorn and retest control-plane VMI restart/recovery.
- [x] Add an explicit tenant control-plane restart/recovery drill that deletes
  a CAPK control-plane VMI, proves root PVC UID preservation, waits for
  CAPI/KCC/routed API recovery, cleans stale tenant `kube-system` pods, and
  runs tenant layer plus routed reachability verifiers.
- [x] Route provider-side tenant add-on and verification jobs through the CAPI
  service/controlPlaneEndpoint and avoid same-node KubeVirt masquerade hairpin
  timeouts in the Hyper-V lab.
- [x] Add tenant Kubernetes HA service-class admission semantics and verify
  that the current small Hyper-V cell rejects 3-control-plane claims before
  creating backing CAPI/CAPK resources.
- [x] Add first-pass multi-cell placement scoring so automatic placement skips
  NotReady cells and chooses the Ready cell with the strongest available
  CPU/memory score.
- [x] Add `CapacityCell` failure-domain placement constraints for VM and
  tenant Kubernetes claims, including VM positive matching and VM plus tenant
  Kubernetes impossible-domain rejection in the provider API contract verifier.
- [x] Add explicit provider-internal `CapacityReservation` objects for admitted
  VM and tenant Kubernetes claims, and verify that rejected claims do not retain
  reservations.
- [x] Add reservation heartbeat/TTL/expiry fields and ignore stale Active
  reservations during capacity accounting.
- [x] Add first-pass concurrent capacity admission protection with a
  per-`CapacityCell` Kubernetes Lease, `status.admission.observedGeneration`
  fast-pathing for already admitted claims, and an end-to-end admission-lock
  verifier.
- [x] Add provider-level `Project.status.quotaUsage` for admitted VM and tenant
  Kubernetes claims, plus VM and tenant Kubernetes project quota admission.
- [x] Add first-pass per-`Project` quota admission locks so active-active
  controller shards and future multi-cell placement paths cannot concurrently
  oversubscribe one tenant quota snapshot.
- [x] Add provider-internal durable `AdmissionJournal` records for VM and
  tenant Kubernetes admission decisions, including accepted, rejected, and
  pending-lock outcomes, so quota/placement decisions are auditable outside pod
  logs.
- [x] Enforce VM image catalog admission for `VirtualMachineClaim`, including
  Ready-image checks, project visibility, and resolved KubeVirt containerDisk
  registry references.
- [x] Expose provider-controller health and Prometheus-style reconcile metrics
  on every replica and verify leader/success samples in the provider layer
  smoke suite.
- [x] Package provider-controller as a local immutable runtime image with
  pinned Python dependencies, removing pod-start runtime `pip install` and PyPI
  dependency from controller failover.
- [x] Add provider finalizers for VM and tenant Kubernetes claims so delete
  lifecycle cleans provider-owned backing resources and capacity reservations.
- [x] Verify admitted tenant Kubernetes claim delete cleanup for CAPI/CAPK
  backing objects, provider gateway, internal service, NetworkPolicy, and
  reservation records.
- [x] Reconcile tenant self-service RBAC from `Project.spec.adminsGroup` so new
  projects can use provider API claims without static per-tenant RBAC manifests.
- [x] Add custom controller backing for Images, Volumes, Networks,
  FirewallRules, VM-target BackupPlans, and AccessGrants in the lab provider
  API.
- [x] Add `ProductPlan` and `Subscription` contracts plus lab reconciliation so
  catalog entries publish status and tenant bindings activate only against
  valid Projects and published plans.
- [x] Add the first durable `Order` contract and lab reconciliation for
  idempotent `CreateSubscription` requests, including policy/approval fields,
  missing-plan rejection, target subscription tracking, portal write support,
  and verifier coverage.
- [x] Extend `Order` reconciliation to the first subscription lifecycle actions:
  `ChangeSubscription`, `RenewSubscription`, `SuspendSubscription`,
  `ResumeSubscription`, and `CancelSubscription`, with target subscription
  consistency checks, status-driven completion, portal smoke coverage, and API
  contract probes.
- [x] Add delayed `Order` execution windows with
  `spec.schedule.notBefore`/`expiresAt`, `Scheduled` status, invalid/expired
  window rejection, controller no-mutation-before-window behavior, and portal
  plus API verifier coverage.
- [x] Add lab provider API restore workflow for VM backup recovery points with
  `RestoreRequest` copy-restore into a new KubeVirt VM and tenant RBAC.
- [x] Add a Flux `source-controller` leader-election failover drill that deletes
  the current artifact-serving leader and verifies Lease, Service endpoint,
  `GitRepository`, and `Kustomization` recovery.
- [x] Add an opt-in production backup/DR blueprint for volume, namespace, and
  tenant-cluster targets with Velero CSI schedules, remote/immutable
  destinations, provider `BackupPlan` examples, and restore workflow contracts.
- [x] Add an opt-in production backup runtime operations contract covering
  service ownership, Velero CSI data movement dependencies, BackupRepository
  maintenance, RPO/RTO restore drills, immutable-storage caveats, and
  tenant-isolated restore policy.
- [x] Add an opt-in production backup runtime cutover skeleton with a separate
  `production-backup-runtime` bundle, `platform-production-backup-runtime`
  GitOps overlay, disabled-by-default controller Deployment, secret/object-store
  contract, smoke runbook, rollback/fail-closed runbook, and verifier.
- [x] Add a local production backup runtime canary simulator and verifier that
  fixes the expected Velero `Schedule`, `Backup`, `Restore`, status, preflight,
  and fail-closed restore behavior for `Volume`, `Namespace`, and
  `KubernetesClusterClaim` targets before live controller promotion.
- [x] Expand the provider `RestoreRequest` API/runtime seam for production
  multi-target restore by adding `Volume`, `Namespace`, and
  `KubernetesClusterClaim` target kinds, `InPlace` mode, Velero restore policy
  fields, template-only provider-to-Velero controller mapping, and a verifier
  that proves the Hyper-V lab controller still fails closed for unsupported
  restore kinds and modes.
- [x] Add a disabled-by-default production backup runtime live-adapter prototype
  and verifier that render deterministic Velero `Schedule`, `Backup`,
  `Restore`, and provider status payloads for `Volume`, `Namespace`, and
  `KubernetesClusterClaim` targets while proving fail-closed canary and tenant
  boundaries without cluster access.
- [x] Add an opt-in production scheduler/admission blueprint with an HA
  scheduler runtime contract, multi-cell filter/score/reserve/permit policy,
  transactional reservation and quota ledger, replayable `AdmissionJournal`
  contract, and GitOps overlay.
- [x] Add a disabled-by-default production scheduler/admission runtime seam and
  verifier that parse local `SchedulerAdmissionReview` fixtures for VM and
  tenant Kubernetes requests, render deterministic reservation, quota, journal,
  and status payloads, and prove fail-closed/no-cluster/lab-overlay boundaries
  without claiming a live scheduler cutover.
- [x] Add an opt-in production scheduler runtime cutover skeleton with a
  separate `production-scheduler-runtime` bundle,
  `platform-production-scheduler-runtime` GitOps overlay,
  disabled-by-default runtime controller, fail-closed admission webhook
  contract, canary/HA patches, smoke runbook, rollback/fail-closed runbook, and
  verifier while keeping the Hyper-V lab and contract-only scheduler blueprint
  unchanged.
- [x] Add a disabled-by-default production scheduler quota replay seam and
  verifier that parse local `SchedulerQuotaReplay` fixtures, replay accepted
  `AdmissionJournal` records against `CapacityReservation` and `Project` quota
  snapshots, render deterministic replay/repair/status payloads, and prove
  fail-closed/no-cluster/lab-overlay boundaries.
- [x] Add scheduler replay operations and failover contract with
  `verify-production-scheduler-replay-operations.ps1`.
- [x] Add production scheduler work-queue runtime contract with
  `verify-production-scheduler-workqueue-runtime.ps1`.
- [x] Add production scheduler runtime observability and SLO contract with
  `verify-production-scheduler-observability-slo.ps1`.
- [x] Add production backup service runtime integration contract for volume,
  namespace, and tenant-cluster targets with remote/immutable storage, restore
  workflow phases, tenant-isolation boundaries, SLO hooks, and
  `verify-production-backup-service-runtime-integration.ps1`.
- [x] Implement and validate production backup service runtime integration up to
  the disabled-by-default live-controller contract and runtime-image seam for
  volume, namespace, and tenant-cluster backup/restore reconcile payloads; this
  remains the production backup controller runtime image seam rather than an
  enabled Hyper-V lab runtime;
  the contract verifiers are `verify-production-backup-live-controller.ps1` and
  `verify-production-backup-controller-runtime-image-seam.ps1`.
- [x] Implement and validate the production scheduler runtime that replaces
  first-pass placement and simple reservation reconciliation with
  scheduler-grade multi-cell placement across multiple real cells, including
  richer policy constraints, transactional reservations, and
  admission-journal replay. This is the production scheduler runtime replacement.
  The aggregate closure verifier is
  `verify-production-platform-runtime-blockers-closure.ps1`.
- [x] Implement and validate scheduler-grade transactional quota admission
  across multiple real cells, including concurrent tenant-cluster admission
  protection and durable quota events. The aggregate closure verifier is
  `verify-production-platform-runtime-blockers-closure.ps1`.
- [ ] Validate full Cluster API + CAPK tenant cluster lifecycle including scale,
  upgrade, and kubeconfig handoff. G016 accounts this as a live larger-cell gap,
  not an offline closure. G017 adds CAPK/OIDC runtime cutover readiness and the
  live evidence schema in `verify-production-capk-oidc-runtime-cutover-readiness.ps1`;
  final closure still requires a larger-cell run. G018 adds
  `invoke-live-larger-cell-capk-oidc-preflight.ps1` to distinguish a real live
  evidence run from a resource or cluster-state blocker.
- [ ] Run real multi-control-plane tenant clusters on a larger cell with
  placement, anti-affinity, and restart/replacement tests across failed
  management nodes. G016 accounts this as a live larger-cell gap, not an
  offline closure. G017 verifies the required larger-cell evidence schema and
  fail-closed gates without applying it to the current Hyper-V lab. G018
  preflight currently checks for 3+ tenant control-plane VMIs and worker-ready
  larger-cell shape before aggregate closure can be claimed. G023 adds the
  actual live cutover gate and currently records that the lab remains at
  tenant CP `1/1/1`, workers `0/0/0`, and insufficient non-disruptive host
  memory for promotion.
- [x] Replace the lab-internal CAPK ClusterIP path with provider-managed routed
  SDN/LB endpoints reachable from provider nodes. The lab gateway now creates
  per-cluster provider proxy Deployments in `capk-system`, exposes them through
  MetalLB, places two replicas on distinct non-VMI host nodes when possible,
  protects the proxy path with provider-owned PDBs, publishes
  `status.apiEndpoint` only after routed `/readyz` succeeds, and has been
  verified for the current live `routable-cluster` and earlier dual-cluster
  gateway drills.
- [x] Add Flux for platform reconciliation with HA controllers, in-cluster
  Git source, and verification gates.
- [x] Add first HA read-only admin portal/API for provider inventory, quota,
  tenant resources, capacity, and health.
- [x] Add tenant write workflows to the portal for creating and deleting
  VM and tenant Kubernetes self-service claims through the provider API.
- [x] Expand the portal write surface to the safe bounded provider API subset:
  `Volume`, `Network`, `FirewallRule`, and `AccessGrant` create/delete, with
  validation, RBAC, audit events, metrics, and cleanup smoke coverage.
- [x] Add admin-only `Project` onboarding to the portal so platform admins can
  create/delete tenants through the same provider API surface, with Project
  quota/network validation, platform-admin authorization, durable audit records
  in `platform-system`, metrics, RBAC, and cleanup smoke coverage.
- [x] Add a first cached provider portal read model with Prometheus metrics so
  repeated admin/API reads do not fan out to Kubernetes on every request.
- [x] Split Kubernetes API Priority and Fairness lanes for provider control
  plane service accounts, platform admins, tenant interactive requests, and
  tenant bulk list/watch traffic, with a noisy-tenant smoke verifier.
- [x] Add shard-aware provider-controller reconciliation and shard metrics so
  tenant/cell controllers are horizontally partitioned in the lab and can be
  expanded by adding more shards.
- [x] Add and cut over to a production-style active-active
  provider-controller shard topology with two shards, three replicas per shard,
  unique Leases, shard-scoped PDBs/metrics Services, GitOps desired state, and
  topology-aware cutover/rollback/verifier gates.
- [x] Add a first OIDC-ready portal write authorization contract: bearer-token
  principals map to subjects, groups, and namespaces; tenant writes require the
  target `Project.spec.adminsGroup`; provider admins use `platform:admins`.
- [x] Replace the portal static-token primary path with signed JWT validation
  for issuer, audience, expiry, groups, and tenant namespace claims in the lab.
- [x] Add HPA guardrails for the stateless provider portal/API path so read and
  write self-service traffic can scale horizontally without changing controller
  shard semantics.
- [x] Add shared tenant/principal write rate limiting in the provider portal so
  noisy tenants are throttled consistently across autoscaled portal replicas
  before their requests enter the Kubernetes API through the shared portal
  service account.
- [x] Add durable namespaced `SelfServiceAuditEvent` records for provider
  portal write attempts so allowed, rejected, and rate-limited self-service
  actions are auditable without scraping pod logs.
- [x] Add conditional weak `ETag`/`304 Not Modified` caching for the provider
  portal summary read model so dashboard polling does not repeatedly transfer
  the full inventory payload when semantic provider state is unchanged.
- [x] Add global-shard retention for provider-internal `AdmissionJournal` and
  tenant `SelfServiceAuditEvent` records so high write/API load cannot grow the
  Kubernetes API read model and etcd object set without bounds.
- [x] Add a bounded provider API read-load verifier that exercises conditional
  summary polling across all Ready portal replicas, checks p95 latency and
  response-byte savings, and proves platform and tenant API probes remain
  responsive during the read load.
- [x] Add an opt-in production OIDC/JWKS identity blueprint and GitOps overlay
  contract for the provider portal, with placeholders for issuer discovery,
  JWKS, group/namespace claim mapping, and lab HS256 env removal.
- [x] Replace the lab HS256 JWT runtime with `oidc-jwks` RS256 validation in
  the provider-portal runtime. The current Hyper-V lab uses a reproducible
  self-hosted JWKS, rejects HS256 downgrade attempts, and verifies token
  allow/deny behavior in `verify-provider-portal.sh`.
- [ ] Promote identity from the lab self-hosted JWKS to an external OIDC/JWKS
  provider with production group/claim mapping. The production identity overlay
  exists; external OIDC/JWKS runtime remains a cutover gap.
  G017 adds CAPK/OIDC runtime cutover readiness and checks that final evidence
  must prove `oidc-jwks`, external issuer/JWKS, claim mapping, HS256 removal,
  and token allow/deny behavior. G018 preflight inspects the live provider
  portal Deployment and keeps this item open while the runtime still lacks
  external JWKS configuration. G023's blocked report is historical evidence from
  before the lab runtime cutover; rerun it after live rollout to refresh the
  provider identity facts.

## Phase 3: Production Cell

- [x] Add an opt-in production-cell substrate blueprint for Rook-Ceph storage,
  Cilium LB IPAM/BGP routed fabric, and Velero backup locations so real cells
  can promote the production layer through GitOps without applying it to the
  small Hyper-V lab by default.
- Replace Longhorn default with Rook-Ceph or another production storage layer.
- Add routed fabric/BGP integration.
- Add registry, image service, backup service, and object storage.
- [x] Add production backup/DR GitOps blueprint that layers Velero locations,
  CSI snapshot classes, provider backup-plan examples, and restore contracts.
- Add dedicated node pools and taints for infra, storage, KubeVirt, and tenants.
- [x] Harden KubeVirt management components in the lab with three replicas,
  strict hostname spread, PDBs, and a verifier.
- [x] Add an opt-in production observability and alerting blueprint for
  Prometheus Operator, provider `ServiceMonitor` objects, provider SLO alert
  rules, and logs/events/traces retention contracts.
- Install and validate the full production observability stack in a real cell,
  including dashboards, alert routing, log/event retention, trace export,
  runbooks, and failure-drill alert tests.

## Phase 4: Multi-Cell Provider

- Add a management cluster and at least two capacity cells.
- Add placement service and inventory cache.
- Promote the opt-in production scheduler/admission blueprint into the
  management plane and prove replay after scheduler failover.
- Add multi-cell GitOps promotion.
- Add disaster recovery and tenant migration workflows.
- Run API/load/failure tests against multiple cells.
