# GitOps And Portal Model

## GitOps

The provider must be operated from declarative desired state.

The lab currently uses Flux v2.8.8 to reconcile:

- platform add-ons;
- provider CRDs and controllers;
- Kyverno/Gatekeeper policies;
- APF configuration;
- tenant `Project` desired state;
- Cluster API templates and tenant cluster add-ons.

Generated namespace/RBAC/quota/policy objects should be owned by the provider
controller, not by GitOps directly. That keeps one reconciliation owner for
tenant guardrails and avoids drift fights between Argo/Flux and the controller.

The repository contains a `gitops/` layout with platform, policy, tenant, and
cell overlays. Flux watches an in-cluster immutable bare Git source served by
`platform-gitops-source` in `flux-system`; this keeps the lab self-contained
while preserving the same GitRepository/Kustomization operating model that a
real remote Git service would use.

Current Flux objects:

- `GitRepository/flux-system/platform-gitops` points at
  `http://platform-gitops-source.flux-system.svc.cluster.local/platform.git`.
- `Kustomization/flux-system/platform-base` applies `./gitops/platform` with
  `prune=false` for this shared lab.
- `platform-gitops-source` runs three replicas with a PDB `minAvailable=2`.
  Its pods use strict hostname topology spread with `minDomains=3` and
  `matchLabelKeys=[pod-template-hash]` so the in-cluster Git endpoint stays
  distributed across all three Hyper-V-backed failure domains during normal
  operation and rolling updates.
- `source-controller` runs three Running replicas with strict hostname topology
  spread, `minDomains=3`, `matchLabelKeys=[pod-template-hash]`, and PDB
  `minAvailable=1`. Its readiness probe targets the artifact HTTP endpoint
  (`/` on `http`), so the Service endpoint set contains only the current
  Lease-holder pod that is actually serving Git artifacts. The other replicas
  remain warm standbys for leader failover. `verify-flux-source-failover.sh`
  can delete the current lease-holder pod for pod-failover proof, or temporarily
  cordon the leader node to prove the Lease holder, `GitRepository`, and
  `Kustomization` recover on a different Hyper-V-backed node.
- `kustomize-controller`, `helm-controller`, and `notification-controller` run
  three Ready replicas with strict hostname topology spread,
  `minDomains=3`, `matchLabelKeys=[pod-template-hash]`, and PDBs
  `minAvailable=2`.

Use `iac/scripts/install-flux-gitops.sh` to install/update the lab Flux layer,
`iac/scripts/verify-flux-gitops.sh` to verify controller HA, source readiness,
GitRepository/Kustomization conditions, and provider object health, and
`CONFIRM_FLUX_SOURCE_FAILOVER=true FLUX_SOURCE_FAILOVER_SCOPE=leader-node-cordon
iac/scripts/verify-flux-source-failover.sh` for the disruptive cross-node
source-controller leader failover drill.

## Portal

The portal should be a thin product UI above the provider API. Backstage is a
reasonable first internal developer portal because it provides a catalog,
templates, and Kubernetes visibility. A custom admin UI can be added later for
deep operations.

Portal users should create:

- `Project`
- `ProductPlan`
- `Order`
- `Subscription`
- `VirtualMachineClaim`
- `KubernetesClusterClaim`
- `Volume`
- `Network`
- `FirewallRule`
- `AccessGrant`
- future approved backup, restore, image-import, order-change, and
  policy-exception requests

The portal must not grant direct access to raw infra namespaces.

## Admin Interface

Admin views must include:

- cell health and capacity;
- tenant quota and usage;
- policy violations and exception requests;
- API latency, APF queues, and throttling;
- VM/cluster lifecycle;
- storage rebuild, backup, and image import state;
- upgrade waves and rollback controls.

Initial Backstage catalog and templates are in `portal/backstage/`.
The lab also runs a first custom provider portal in `platform-system`:

- `provider-portal` Deployment with a six-replica autoscaling floor and PDB
  `minAvailable=4`;
- `provider-portal` HPA with `minReplicas=6`, `maxReplicas=9`, CPU and memory
  utilization targets, while GitOps seeds the Deployment at `spec.replicas=6`
  so a fresh apply is HA before the first HPA reconciliation;
- service account with read access to provider inventory plus constrained
  `create/delete` on admin-only `Project` onboarding plus tenant-scoped
  `Order`, `Subscription`, `VirtualMachineClaim`, `KubernetesClusterClaim`, `Volume`,
  `Network`, `FirewallRule`, and `AccessGrant`, plus admin-only `ProductPlan`
  catalog objects;
- platform admin users can create and delete `Project` and `ProductPlan`
  objects from the portal. The portal builds the cluster-scoped object,
  requires the `platform:admins` group, writes audit records in
  `platform-system`, and lets the provider controller create the backing tenant
  namespace, quota, RBAC, network guardrails, or catalog status.
- VM and tenant-cluster write payloads accept optional `failureDomains` for
  zone/storage/region/site/rack/network placement constraints, while the portal
  still server-side constructs the final CRD object instead of accepting raw
  tenant-supplied manifests;
- MetalLB endpoint `http://172.28.10.101/`;
- `/api/summary` compact read model for projects, quotas, VMs, tenant
  Kubernetes clusters, product plans, subscriptions, volumes, networks,
  orders, firewall rules, backup plans, access grants, capacity cells, active
  reservations, recent admission journals, health, and recent events;
- a per-replica TTL cache for `/api/summary`, with stale-if-error behavior and
  Prometheus-style `/metrics` for cache hit/miss/stale, refresh latency,
  refresh errors, `200`/`304` summary requests, and write requests. Explicit
  `fresh=1` reads synchronously refresh on the target replica when the local
  refresh lock is free, otherwise they return bounded stale data or a retryable
  error instead of blocking the HTTP worker indefinitely. The summary endpoint
  returns a weak semantic `ETag` and supports `If-None-Match` revalidation so
  dashboards and automation can poll the admin read model without repeatedly
  transferring unchanged inventory payloads.
- OIDC/JWKS bearer authentication for write requests. The lab validates a
  reproducible issuer/audience contract from `platform-system/provider-portal-auth`,
  allows only RS256, maps `sub`, `groups`, and `platform_namespaces` claims to a
  caller principal, and accepts writes only for `platform:admins` or the target
  `Project.spec.adminsGroup`. The same contract can be moved behind an external
  OIDC/JWKS issuer for production.
- The opt-in production identity blueprint lives in
  `iac/kubernetes/production-identity` and
  `gitops/platform-production-identity`. It defines the OIDC issuer/JWKS,
  groups, namespace-scope, and portal env cutover contract for a real external
  issuer. The lab overlay stays on its deterministic self-hosted JWKS until that
  external identity provider and live token evidence are supplied.
- shared write rate limiting keyed by caller subject and tenant namespace,
  currently `8` write attempts per `10s` in the lab. The portal stores the
  fixed-window counter in namespaced Kubernetes `Lease` objects with optimistic
  concurrency, so noisy tenants receive `429` consistently across autoscaled
  portal replicas before their traffic reaches the Kubernetes API through the
  shared portal service account.
- strict hostname topology spread for the six-replica portal floor, plus
  `minAvailable=4`, so the admin/API entrypoint does not concentrate on a
  single Hyper-V VM when all three lab hosts are available.
- durable `SelfServiceAuditEvent` records for portal write attempts. Allowed,
  rejected, rate-limited, and backend-error create/delete attempts include the
  caller subject, tenant namespace or Project reference, provider resource,
  outcome, HTTP status, and request path, giving the lab a provider API audit
  trail instead of only pod logs or transient Kubernetes Events. Project
  onboarding audit records are stored in `platform-system` so the trail exists
  before the new tenant namespace is reconciled.
- read-only access to provider-internal `AdmissionJournal` records in
  `/api/summary`, allowing the admin UI to show why recent VM and tenant
  Kubernetes claims were accepted, rejected, or left pending by quota/capacity
  admission. Tenant self-service RBAC remains denied for the journal resource.
- an opt-in production scheduler/admission blueprint under
  `iac/kubernetes/production-scheduler` and
  `gitops/platform-production-scheduler`. It keeps the current lab on the
  verified provider-controller admission path while defining the future
  multi-cell scheduler contract that will own filter/score/reserve/permit,
  transactional reservations, quota locks, and replayable admission journals.
- `verify-provider-portal.sh` creates and deletes a temporary admin-only
  `Project`, a temporary admin-only `ProductPlan`, a temporary tenant
  `Subscription`, a temporary tenant `Order` that provisions a target
  subscription, a scheduled suspension order that stays `Scheduled` without
  mutating the subscription before its execution window, suspension, resume,
  renewal, and cancellation orders against that target subscription, plus
  temporary VM, tenant Kubernetes, volume, network, firewall, and access-grant
  resources through the portal write API, then verifies audit records, metrics,
  cleanup, ETag summary caching, and shared rate limiting across Ready portal
  pods.
- The first console render requests a fresh provider summary so the user-facing
  health badge does not open on a stale post-rollout cache. The MVP UI exposes
  working navigation filters, tenant search, tenant/admin action groups,
  empty states, quota/capacity/audit/admission rails, and hides destructive
  row actions until a write token is present. The lab keeps larger-cell,
  public-network, and dedicated-placement choices out of the default UI while
  those remain promotion-gated backend/API capabilities.

The portal deliberately writes only provider claim objects; it does not grant
direct raw substrate access. This proves the portal/API shape, HA exposure, and
self-service write workflow while keeping tenant callers isolated from each
other and keeping the provider controller as the owner of backing KubeVirt,
CAPI/CAPK, networking, and reservation resources.

Current lab status:

- GitOps overlays exist under `gitops/`.
- Flux reconciliation is installed in `flux-system` and verified by
  `iac/scripts/verify-flux-gitops.sh`.
- `gitops/platform/kustomization.yaml` applies the custom provider portal/API
  manifest, including the write-auth Secret and HA Service.
- Backstage catalog and template skeletons exist under `portal/backstage/`.
- Custom provider portal/API IaC exists under `iac/kubernetes/provider-portal/`
  and is verified by `iac/scripts/verify-provider-portal.sh`.
