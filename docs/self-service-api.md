# Self-Service API

The portal and admin UI must talk to a provider API, not directly to raw
infrastructure namespaces.

## Current Contract

The repository now defines these API contracts under
`platform.privatecloud.local/v1alpha1`:

| Kind | Scope | Purpose |
| --- | --- | --- |
| `Project` | Cluster | Tenant boundary, quotas, isolation tier, ownership |
| `CapacityCell` | Cluster | Provider capacity cell inventory, failure-domain metadata, service-class limits |
| `CapacityReservation` | Cluster | Provider-internal reservation record for admitted claims; not exposed to tenant self-service RBAC |
| `AdmissionJournal` | Cluster | Provider-internal write-once admission decision journal for VM and tenant Kubernetes claims; not exposed to tenant self-service RBAC |
| `ProductPlan` | Cluster | Provider product catalog entry that maps a visible plan to a service kind, service class, defaults, quota profile, lifecycle, and commercial metadata |
| `Subscription` | Namespace | Tenant binding from a `Project` to a published `ProductPlan`, including requested state, requester metadata, and reconciled lifecycle status |
| `Order` | Namespace | Tenant self-service provisioning request with action, optional execution window, policy/approval decision, idempotency key, and reconciled target subscription status |
| `VirtualMachineClaim` | Namespace | Tenant VM request that a controller maps to KubeVirt/CDI |
| `KubernetesClusterClaim` | Namespace | Tenant Kubernetes cluster request that a controller maps to Cluster API |
| `Image` | Cluster | Provider image catalog, source metadata, visibility, trust state |
| `Volume` | Namespace | Tenant block/shared volume request backed by CSI/DataVolume |
| `Network` | Namespace | Tenant network intent, routing, egress, load balancer eligibility |
| `FirewallRule` | Namespace | Ordered tenant ingress/egress policy intent |
| `BackupPlan` | Namespace | Backup schedule, target selector, retention, consistency contract |
| `RestoreRequest` | Namespace | Tenant/admin restore request from a recovery point into a new VM target |
| `AccessGrant` | Namespace | OIDC/user/group access request for kubeconfig, console, or project roles |
| `SelfServiceAuditEvent` | Namespace | Durable audit record for portal/API self-service actions, including caller, action, resource, outcome, and status |

The CRDs are in `iac/kubernetes/provider-api/crds.yaml`.

Current lab status:

- CRDs and RBAC are applied.
- Example `tenant-a` objects exist for the full v1alpha1 contract surface.
- A lightweight provider controller is deployed in `platform-system`.
- The provider controller runs as three replicas with pod anti-affinity,
  topology spread, and a PodDisruptionBudget requiring two available replicas.
- The provider controller uses a Kubernetes `Lease` for leader election; one
  active leader reconciles provider state while the other replicas stay ready
  for failover.
- The provider controller exposes `/healthz` and `/metrics` on every replica
  through the `provider-controller-metrics` Service for portal/admin health,
  SLO, and alerting integration.
- The controller reconciles `Project` into namespace guardrails: Pod Security
  labels, quota, LimitRange, DNS egress policy, default-deny network policy, and
  tenant RBAC.
- `Project.status.quotaUsage` reports provider-level usage for admitted VM and
  tenant Kubernetes claims. VM and tenant Kubernetes admission check
  `Project.spec.quotas` before creating backing resources or reservations.
  The lab controller calculates quota with the current claim excluded from
  usage, so existing reconciled claims do not self-count during periodic
  reconciliation.
- The controller writes cluster-scoped `AdmissionJournal` records for VM and
  tenant Kubernetes admission outcomes. Each journal captures the claim UID and
  generation, project quota snapshot, selected cell/service class, lock names,
  controller shard identity, decision, reason, and observed timestamp. Tenant
  self-service RBAC cannot read these provider-internal records; platform
  admins and the portal summary can.
- The global provider-controller shard enforces bounded retention for
  `AdmissionJournal` and `SelfServiceAuditEvent` records. The lab defaults keep
  records for 7 days, cap admission journals to 5000 records per `projectRef`,
  and cap self-service audit events to 1000 records per namespace. This keeps
  high write/API load from turning auditability into unbounded etcd growth,
  while preserving tenant fairness so one tenant cannot evict another tenant's
  recent audit history.
- The global provider-controller shard publishes `ProductPlan` status from the
  declared lifecycle state, reconciles tenant `Subscription` objects against
  existing Projects and published plans, and reconciles tenant `Order` objects
  for durable `CreateSubscription`, `ChangeSubscription`, `RenewSubscription`,
  `SuspendSubscription`, `ResumeSubscription`, and `CancelSubscription` paths.
  The current lab supports
  policy/approval/idempotency fields, missing-plan rejection, target
  subscription tracking, plan-change, auto-renew, cancellation state
  transitions, suspension/resume holds, optional
  `spec.schedule.notBefore`/`expiresAt` execution windows, `Scheduled` status
  while the window is pending, `Succeeded` order evidence, and portal/API smoke
  coverage. A production queue, dependency retries, dependency-aware
  hold/cancel consequences, calendar UX, and commercial rate-card integration
  remain promotion work.
- The controller reconciles `VirtualMachineClaim` into KubeVirt
  `VirtualMachine` objects and reports claim phase, backing VM name, and VMI IP.
- The controller reconciles `KubernetesClusterClaim` into Cluster API + CAPK
  resources and reports phase plus the expected kubeconfig Secret name.
- `VirtualMachineClaim` and `KubernetesClusterClaim` receive provider
  finalizers. On deletion, the controller removes provider-owned backing
  resources, provider-routed API gateway resources, internal API Services,
  NetworkPolicies, and capacity reservations before releasing the claim, so
  self-service delete does not leave stale quota or gateway state behind.
- Every reconciled `Project` receives a tenant namespace RoleBinding named
  `tenant-self-service` from its `adminsGroup` to the shared
  `platform-tenant-self-service` ClusterRole. New tenant groups can therefore
  create, read, and delete provider API claims inside their own namespace
  without static per-tenant RBAC manifests, while cross-tenant namespaces and
  provider-internal resources remain denied.
- New tenant Kubernetes clusters use CAPK `DataVolume` root disks on Longhorn
  and KubeVirt masquerade ports for SSH/API. Tenant cluster access should use
  the generated kubeconfig and provider-managed API endpoint/service; direct
  VMI pod IPs are substrate details and can change across VMI restart.
- `VirtualMachineClaim` and `KubernetesClusterClaim` now support
  `spec.placement.capacityCell`, `spec.placement.serviceClass`, and
  `spec.placement.failureDomains` with `region`, `site`, `zone`, `rack`,
  `network`, and `storage` exact-match constraints. The controller records
  `status.admission` with the selected cell, service class, estimated
  footprint, and effective tenant-cluster worker replicas.
- `VirtualMachineClaim.spec.image.source: catalog` is enforced for VM claims.
  The controller resolves the named `Image` object, requires it to be `Ready`,
  checks `visibility`/`allowedProjects`, records the resolved registry reference
  in `status.admission.image`, and rejects missing or unauthorized images before
  creating a KubeVirt VM or capacity reservation.
- If `spec.placement.capacityCell` is omitted, the controller evaluates all
  cells that provide the requested service class and match any requested
  failure-domain constraints, skips NotReady cells, and selects the Ready cell
  with the strongest available CPU/memory score. Explicit cell placement still
  pins the request to that cell and fails fast if it is not Ready or does not
  match the requested failure domain.
- `CapacityCell.spec.serviceClasses` can express tenant-cluster HA intent with
  `minControlPlaneReplicas` and `maxControlPlaneReplicas`. The lab publishes an
  `ha-tenant-kubernetes` class for the API contract, but the current
  `lab-hyperv` cell limit remains `maxControlPlaneReplicas: 1`; 3-control-plane
  claims are rejected before CAPI/CAPK resources are created.
- `CapacityCell.status` now includes `reserved` and `available` capacity,
  derived from active provider-internal `CapacityReservation` objects, with
  admitted-claim fallback during reconciliation. Active reservations include
  `lastHeartbeatTime`, `reservationTTLSeconds`, and `expiresAt`; stale
  reservations are not counted toward cell capacity. Oversized VM claims are
  rejected before the controller creates a backing KubeVirt VM, and rejected
  claims do not retain reservations.
- The demo `KubernetesClusterClaim` reaches CAPI/KCP/Machine `Ready` after
  provider-side Cilium installation into the workload cluster.
- `CapacityCell`, `Image`, `ProductPlan`, `Subscription`, `Order`, `Volume`,
  `Network`, `FirewallRule`, and `AccessGrant` now have lab backing
  reconciliation.
  `CapacityCell` is reconciled from Kubernetes node inventory, `Image` is
  accepted into catalog status, `ProductPlan` is published into catalog status,
  `Subscription` is activated when its Project and ProductPlan references are
  valid, `Order` can create and track a target subscription for a published
  plan, drive change/suspend/resume/renew/cancel lifecycle transitions on an
  existing subscription, and hold execution at `Scheduled` without mutating the
  subscription before `spec.schedule.notBefore`; `Volume` creates a PVC,
  `Network` creates an isolation
  `NetworkPolicy`, allow-only `FirewallRule` creates a `NetworkPolicy`, and
  `AccessGrant` creates a `RoleBinding`.
- `BackupPlan` for `VirtualMachineClaim` targets is backed by KubeVirt
  `VirtualMachineSnapshot` recovery points in the lab. The demo plan
  `tenant-a/demo-daily` protects backing VM `claim-demo-vm`, reports
  `Protected`, and publishes `lastSuccess` plus `recoveryPoints`. Volume,
  namespace, remote, immutable, and tenant-cluster backups still require a
  production Velero/Kasten/CSI/object-storage integration; the opt-in
  production contract now lives in `iac/kubernetes/production-backup`.
- `RestoreRequest` supports the lab VM recovery workflow for those KubeVirt
  recovery points. The controller resolves the latest ready snapshot from a
  `BackupPlan` or an explicit `recoveryPointRef`, rejects target-name
  collisions, creates a KubeVirt `VirtualMachineRestore` in copy mode with
  `volumeRestorePolicy: PrefixTargetName` and `volumeOwnershipPolicy: None`,
  and reports `Pending`, `Running`, `Succeeded`, `Rejected`, or `Degraded`.
  Restored VMs are labeled `platform.privatecloud.local/managed-by:
  provider-restore`, `restore-request`, and `restored-from` so they are
  distinguishable from the original claim-backed VM.
- `SelfServiceAuditEvent` is the durable lab audit surface for portal actions.
  The portal writes namespaced audit records for allowed, rejected,
  rate-limited, and backend-error create/delete attempts. Admin-only `Project`
  onboarding is audited in `platform-system` with the target Project reference,
  because the tenant namespace may not exist yet. Tenant self-service RBAC can
  read audit records in its own namespace, but cannot create or edit them;
  platform admins keep provider-wide access.

## Portal Workflow

1. Admin creates or approves a `Project` and publishes `ProductPlan` catalog
   entries; the current provider portal exposes these as admin-only
   self-service actions guarded by the `platform:admins` group.
2. Portal maps tenant users to `platform:<tenant>:admins` and the shared
   `platform:tenants` image-catalog reader group. The Project controller binds
   the tenant admin group to namespaced provider self-service permissions.
3. Tenant creates `Order`, `Subscription`, `VirtualMachineClaim`,
   `KubernetesClusterClaim`, `Volume`, `Network`, `FirewallRule`,
   `BackupPlan`, `RestoreRequest`, or `AccessGrant`
   objects through the provider API. The current portal write surface exposes
   admin-only `Project` and `ProductPlan` onboarding plus the bounded
   create/delete subset for `Order`, `Subscription`, `VirtualMachineClaim`,
   `KubernetesClusterClaim`, `Volume`, `Network`, `FirewallRule`, and
   `AccessGrant`; backup and restore objects remain controller/API workflows
   until the approval and data-protection guardrails are production-shaped.
4. Current provider controller creates backing namespace guardrails and KubeVirt
   VMs for VM claims.
5. Provider controllers validate quota, placement, policy, identity, backup,
   and image access, then create backing KubeVirt, CDI, CAPI, Cilium, CSI,
   backup, and RBAC resources. The lab implements placement admission against
   `CapacityCell`, including provider-internal `CapacityReservation`
   accounting, durable `AdmissionJournal` decision records, and provider-level
   `Project` quota usage reporting plus VM quota admission, VM image catalog
   admission, and KubeVirt VM snapshot recovery points for VM-target
   `BackupPlan` objects, plus copy restore from those recovery points through
   `RestoreRequest`, and the safe subset listed above.
6. Status fields expose phase, admission result, IP/API endpoint, kubeconfig
   secret, and errors.

## Admin UI Workflow

The admin interface must show:

- cell capacity and saturation;
- tenant quota and usage;
- pending approvals and policy exceptions;
- VM, tenant cluster, product catalog, order, subscription, image, volume,
  network, backup, restore, and access inventory;
- API fairness and throttling;
- failure domains and placement;
- upgrade waves and rollback state;
- storage rebuild and backup status.

The current lab has the first HA implementation of this surface:
`provider-portal` exposes `http://172.28.10.101/` and `/api/summary` from
autoscaled replicas in `platform-system`, with a three-replica floor and a
nine-replica lab cap, plus a constrained write API for creating and deleting
admin-only `Project` and `ProductPlan` objects plus tenant-scoped
`Order`, `Subscription`, `VirtualMachineClaim`, `KubernetesClusterClaim`, `Volume`,
`Network`, `FirewallRule`, and `AccessGrant` objects. The portal server
constructs the provider API objects itself, validates namespace/name, Project
tier, quotas, network defaults, plan lifecycle, service kind, order action,
order policy/approval fields, optional order schedule timestamps,
subscription state, resource quantities, CIDRs, IPs, ports, class,
service-class, role,
access-target, and enum values, and never accepts raw `status`, finalizers,
owner references, or arbitrary substrate objects from the browser.

Portal writes now require a signed JWT bearer token validated with
OIDC/JWKS-style RS256 signature checks. The lab runtime uses
`PORTAL_WRITE_AUTH_MODE=oidc-jwks`, validates
`issuer=https://issuer.platform.local`, `audience=platform-portal`, `exp`/`nbf`
/`iat`, allows only `RS256`, and publishes a reproducible lab JWKS at
`/oidc/jwks.json` for smoke testing. Caller identity comes from `sub`, `groups`,
and `platform_namespaces` claims. A caller may write a tenant namespace only
when its token is scoped to that namespace and its groups include the
`Project.spec.adminsGroup` value, or when it belongs to the provider admin
group `platform:admins`. Production should replace the lab self-hosted JWKS
with an external OIDC issuer and remote JWKS while preserving the same
principal contract. Read-only `/api/summary`, health, discovery, JWKS, and
metrics remain unauthenticated in the lab. The portal also enforces a shared
write rate limit keyed by caller subject and tenant namespace before it calls
the Kubernetes API. The lab stores the fixed-window counter in
`coordination.k8s.io/Lease` objects in `platform-system` using optimistic
`resourceVersion` updates, so the default 8 write attempts per 10 seconds is
consistent across all autoscaled portal replicas. Production can replace this
Lease-backed lab store with the same contract at a global gateway or dedicated
rate-limit service.

`/api/summary` is backed by a per-replica TTL read cache. The current lab keeps
the cache fresh for 30 seconds, can serve stale data for up to 60 seconds during
temporary Kubernetes API read errors, and invalidates the cache after portal
claim create/delete requests by marking the previous payload stale rather than
dropping it. That keeps the portal responsive under API Priority and Fairness
backpressure after a write. The summary endpoint also emits a weak `ETag`
based on semantic provider inventory while ignoring volatile cache and
heartbeat timestamps plus transient Kubernetes Events, and honors
`If-None-Match` with `304 Not Modified`, so dashboard polling can revalidate
cheaply instead of downloading and parsing the full JSON payload every time.
`/metrics` exposes cache hit/miss/stale counters, `200`/`304` summary request
counters, summary response-byte counters, summary refresh latency, refresh
errors, and write request counters so the portal read path can be included in
provider API SLO dashboards. `iac/scripts/verify-provider-api-load.sh` is the
current bounded read-load gate for this contract.
The same summary includes compact inventory for product plans, subscriptions,
VM claims, tenant Kubernetes claims, volumes, networks, firewall rules, backup
plans, and access grants, as well as bounded recent Kubernetes Events,
`SelfServiceAuditEvent` records, and `AdmissionJournal` objects so the admin
interface can correlate write attempts, caller subjects, outcomes, rate-limit
decisions, and controller admission decisions without scraping pod logs.
Retention keeps durable audit/journal records bounded before they reach the
summary cap.

## Controller Boundary

The API contract deliberately hides:

- raw KubeVirt host device settings;
- raw NetworkAttachmentDefinitions;
- arbitrary LoadBalancer IP assignment;
- cluster-scoped RBAC;
- privileged pod fields;
- low-level storage class choice unless a service class exposes it.
- long-lived static credentials; `AccessGrant` should issue short-lived access
  or bind OIDC groups through audited workflow.

This is how the platform keeps self-service useful without giving tenants the
keys to the substrate.
