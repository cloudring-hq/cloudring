# Target Provider Architecture

## Summary

The scalable target is a cell-based private cloud provider built on Kubernetes,
KubeVirt, Cluster API, Cilium, Ceph-class storage, GitOps, policy-as-code, and a
self-service platform API.

The local Hyper-V lab is one tiny capacity cell. A production deployment repeats
that pattern many times and adds a separate management plane above it.

## Planes

| Plane | Responsibility | Scale model |
| --- | --- | --- |
| Management plane | Tenant API, portal, identity, billing/quota, fleet inventory, placement, approvals, GitOps orchestration | 3+ nodes per site, active/active across management zones |
| Capacity cell | Runs tenant VMs, tenant Kubernetes clusters, storage, ingress, load balancers, node pools | Add more cells; keep each cell bounded |
| Network fabric | EVPN/VXLAN or routed leaf-spine, BGP, service IP advertisement, tenant routing/firewalls | Add racks/AZs; avoid L2 beyond cell boundary |
| Storage plane | Replicated/block/object storage, image registry backend, backup targets | Scale by storage pools and failure domains |
| Observability plane | Metrics, logs, traces, events, audit, SLOs, capacity forecasting | Sharded ingestion, long-term remote storage |

## Cell Pattern

Each capacity cell should be independently useful:

- 3 or 5 Kubernetes control-plane nodes.
- N worker nodes split into node pools: general containers, KubeVirt compute,
  storage, infra, GPU/high-memory if needed.
- KubeVirt with CDI, live migration policy, CPU model policy, image templates,
  and VM export/import.
- Cilium CNI with NetworkPolicy, Hubble, BGP/LB integration, and optional
  Cluster Mesh for selected cross-cell services.
- Storage using Rook-Ceph or another production storage system with explicit
  failure domains. Longhorn remains suitable for small labs and edge cells, not
  the default high-scale provider storage layer.
- MetalLB/Cilium BGP or fabric-integrated load balancing.
- Kyverno or Gatekeeper for admission policy.
- Argo CD or Flux for GitOps.
- Per-cell Prometheus agents and log collectors with remote write.

Cells are disposable capacity units. If one grows too large, add another cell
instead of stretching the Kubernetes API and etcd indefinitely.

## Self-Service API

Expose a provider API above Kubernetes primitives. Tenants should not need raw
cluster-admin access to infrastructure namespaces.

Recommended API resources:

| Resource | Backing implementation |
| --- | --- |
| `Project` | namespace/project set, RBAC, quotas, policy, audit sinks |
| `CapacityCell` | node inventory, service-class limits, placement boundary |
| `CapacityReservation` | provider-internal reservation ledger for admitted tenant requests |
| `VirtualMachine` | KubeVirt VM/DataVolume templates |
| `Image` | CDI import pipeline and registry/object storage metadata |
| `Volume` | CSI PVC/snapshot/backup |
| `Network` | Cilium policy, NAD where approved, fabric integration |
| `FirewallRule` | CiliumNetworkPolicy or provider firewall controller |
| `KubernetesCluster` | Cluster API, Cluster API Provider KubeVirt/OpenStack/bare metal |
| `BackupPlan` | CSI snapshots, Velero/Kasten-style backup integration |
| `AccessGrant` | OIDC group bindings, short-lived kubeconfig/console tokens |

Implementation choices:

- Crossplane compositions or custom controllers can expose the provider API.
- Cluster API should own tenant Kubernetes cluster lifecycle.
- Argo CD/Flux should reconcile platform components, policies, and per-tenant
  generated configuration.
- Backstage, Rancher, Port, or a custom portal can be the UI; the API remains
  the contract.

## Tenancy Tiers

| Tier | Isolation | Use |
| --- | --- | --- |
| Shared project | Namespace/project isolation in a shared cell | Trusted internal tenants, demos, low-risk workloads |
| Dedicated node pool | Tenant-only workers inside a shared cell | Noisy tenants, compliance-sensitive workloads |
| Dedicated workload cluster | Tenant Kubernetes cluster via Cluster API | Default for self-service Kubernetes clusters |
| Dedicated cell | Separate capacity cell and storage/network pool | Regulated, very large, or hostile tenants |

Namespace-only tenancy must never be treated as the strongest boundary. The
provider should default to stronger isolation as tenant trust decreases or load
increases.

## API Scale

Kubernetes APIs are protected by:

- API Priority and Fairness for tenant, platform, and controller traffic.
- Controller sharding by cell and tenant.
- Separate management and workload clusters.
- Rate limits and quotas at the provider API before requests reach Kubernetes.
- Admission policy budgets and fail-open/fail-closed decisions per risk class.
- Read-heavy APIs backed by cached inventory/search indexes, not direct
  list-watch fanout across every cell.

## Failure Domains

Use labels and placement policies for:

- region
- site
- availability zone
- cell
- rack
- host
- storage failure domain
- network fabric domain

Tenant workloads and storage replicas should spread across the smallest set of
failure domains required by the service class.

## Upgrade Model

1. Upgrade management-plane controllers in canary mode.
2. Upgrade one non-critical cell.
3. Drain one node pool at a time.
4. Validate API latency, error rate, Cilium health, storage rebuild, KubeVirt
   migration/restart, and tenant SLOs.
5. Promote by waves across cells.
6. Keep rollback manifests and previous images available.

## Current Lab Gap

The Hyper-V lab proves the stack mechanics but still lacks:

- separate management plane;
- full Cluster API tenant cluster lifecycle across create, upgrade, scale,
  delete, kubeconfig rotation, and multi-control-plane service classes. The lab
  has working create/readiness for single-control-plane clusters, persistent
  root disks, and safe admission rejection for 3-control-plane claims that do
  not fit the current cell;
- production storage such as Ceph;
- an opt-in production-cell blueprint now exists under
  `iac/kubernetes/production-cell` for Rook-Ceph, Cilium LB IPAM/BGP, and
  Velero backup locations, but it has not yet been promoted into a real cell or
  proven with Ceph health, routed fabric, and restore drills;
- real multi-AZ/rack/network failure domains;
- production self-service portal/API; the lab has expanded CRD contracts, with
  controller reconciliation currently implemented for `Project`,
  `VirtualMachineClaim`, `KubernetesClusterClaim`, service-class admission, and
  basic capacity admission against `CapacityCell` with explicit
  provider-internal `CapacityReservation` records plus provider-level
  `Project` quota usage and VM/tenant Kubernetes quota admission;
- registry/image service;
- full policy engine and exception workflow;
- API load tests;
- multi-cell automation. The lab now has a `CapacityCell` contract for the
  current Hyper-V cell, visible claim admission status, simple reservation
  objects with heartbeat/TTL/expiry, and first-pass Ready-cell scoring for
  automatic placement, but not a separate management plane, transactional
  scheduler-grade reservations, or multiple real cells. An opt-in production
  scheduler/admission blueprint now exists under
  `iac/kubernetes/production-scheduler`, but the scheduler runtime cutover and
  multi-cell replay/failure drills remain future work.
