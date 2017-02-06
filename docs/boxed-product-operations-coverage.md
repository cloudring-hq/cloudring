# Boxed-Product Operations Coverage

This note maps an external boxed-provider operating model to this private
cloud provider MVP. It is a coverage guide, not a claim that every scenario is
finished. The source documentation is a MadCap WebHelp site; the crawler used
the public home page and TOC/search index from the external reference source.

- `SearchTopic_Chunk*.js` and `SearchUrl_Chunk*.js`

The local crawl found 4,320 TOC pages. The operations-oriented subset contains
4,147 pages across provider, reseller, customer, billing/order, public API,
deployment, disaster recovery, firewall/security, identity, privileges,
reporting, monitoring, upgrade, store, and marketplace guides. The normalized
index is saved in `tmp/boxed-product-toc-pages.json` and
`tmp/boxed-product-operations-pages.json` for auditability.

## Scenario Taxonomy

| Area | Boxed-product scenarios | Current platform coverage | Remaining product gap |
| --- | --- | --- | --- |
| Provider hierarchy | Provider, reseller, customer, staff member, service user, account ownership, account disable/delete | `Project`, tenant namespace, admin group, tenant self-service RBAC, audit events | Add reseller/delegated-provider hierarchy, branded delegated admin scopes, customer account lifecycle, account suspension/hold |
| Catalog and offers | Service templates, service plans, sales categories, store visibility, plan periods, included/max resources, overuse rates | Provider API service classes, capacity cells, image catalog, `ProductPlan` catalog objects with service/quota/commercial metadata, Backstage templates, and admin portal create/delete smoke coverage | Add offer bundles, sales categories, rate cards, subscription periods, richer plan visibility rules, and plan-change policy |
| Orders and subscriptions | Buy, activate, renew, cancel, hold, sync, upgrade/downgrade, delayed downgrade, provisioning queue | Tenant-scoped `Order` objects now capture durable `CreateSubscription`, `ChangeSubscription`, `RenewSubscription`, `SuspendSubscription`, `ResumeSubscription`, and `CancelSubscription` requests with idempotency key, optional `notBefore`/`expiresAt` execution window, policy/approval fields, target subscription, status, and portal/API smoke evidence; `Subscription` objects bind a project to a `ProductPlan`, reconcile to `Active`/`Suspended`/`Cancelled`, and appear in portal summary; direct self-service create/delete also exists for VM, tenant Kubernetes, volume, network, firewall, and access grant | Add production provisioning queue, dependency graph, retry/cancel controls, dependency-aware hold/cancel consequences, upgrade/downgrade consequences, calendar UX, and commercial rate-card integration |
| Provisioning model | Resource types, activation parameters, attributes, external system handoff, manual intervention | CRDs and controller reconciliation for VM, KCC, Volume, Network, FirewallRule, BackupPlan, RestoreRequest, AccessGrant | Add typed activation parameters, validation schema per offer, manual approval/intervention workflow, external integration contracts |
| Placement and capacity | Service nodes, IP pools, resource pools, readiness, attributes, least-loaded placement, tiers | `CapacityCell`, service classes, failure-domain filters, quotas, reservation ledger, admission journals | Promote disabled scheduler runtime into live multi-cell placement; prove compute/storage/network tier scoring across at least two cells |
| Customer self-service | Purchase/change/cancel services, resize, users, service credentials, usage visibility, backup/restore | Provider portal write API and summary, tenant-scoped RBAC, subscription activation/change/renew/suspend/resume/cancel against catalog plans, kubeconfig access grants, VM backup/restore | Add user management, credential rotation, resize/change workflows, usage/cost export, richer UX for lifecycle actions |
| Reseller self-service | Branded panel, customer management, delegated plans, reseller permissions | Requirements and Backstage skeleton only | Add reseller model, delegated catalog/quotas, branded customer portal, reseller-scoped reporting and support access |
| Security and compliance | Roles/privileges, ACL/trusted networks, API restrictions, login history, OTP, TLS/firewall hardening, GDPR/PCI | RBAC, tenant default-deny, Kyverno guardrails, OIDC/JWKS lab auth, APF, audit events, network policies | Add login/session history, API allowlists, tenant ACLs, MFA/OTP integration, certificate lifecycle, compliance export/erase workflows |
| Monitoring and support | Component health, task/event monitoring, notifications, failed task restart/cancel, support diagnostics | Metrics endpoints, direct verifiers, production observability blueprint, operations log | Install production observability stack, dashboards, alerts, notification routing, support bundles, task queue UI, failure-drill alert evidence |
| Backup and DR | Provider DR role inventory, scheduled backups, RPO/RTO, backup windows, full/partial restore, customer backup | KubeVirt VM snapshot/copy restore, backup/DR blueprints and runtime contracts | Implement live volume/namespace/KCC backup runtime, off-cell immutable storage, restore drills, concurrency limits, role inventory |
| Reporting | Receivables, sales, commissions, usage, capacity, churn/renewal-style operations | Capacity, reservations, audit, summary API, operations log | Add usage metering, capacity/failed-provisioning reports, commercial export, renewal/risk dashboards |
| API lifecycle | Provider and billing public APIs, event receivers, automation hooks | Kubernetes-native API, portal REST API, GitOps, APF | Add versioned external provider API, event webhooks, idempotency keys, supportable SDK/CLI contract |
| Upgrade and maintenance | Package/module updates, service controller monitoring, upgrade workflows, rollback | GitOps, Flux HA, kubeadm timeout hardening, component HA verifiers | Prove full platform/cell/tenant upgrade waves with rollback, maintenance windows, tenant notification, compatibility gates |

## Promotion Gates

The current Hyper-V lab is a useful live proof point, but the boxed-product
boxed-product bar requires these gates before production claims:

1. Multi-cell runtime: at least two capacity cells, production storage/fabric,
   scheduler runtime, placement replay, and cross-cell failure tests.
2. Tenant Kubernetes lifecycle: 3+ control-plane replicas, worker pools,
   upgrade, scale, kubeconfig rotation, replacement, and anti-affinity evidence.
3. Subscription/order layer: production order queue, retry/cancel operations,
   dependency-aware hold/cancel policy, calendar UX, rate-card
   integration, and user-facing consequence/rollback UX for lifecycle actions.
4. Delegated provider/reseller layer: scoped catalog, branding, reseller admin,
   customer management, and delegated reporting.
5. Backup/DR runtime: immutable off-cell backups for VM, volume, namespace, and
   tenant Kubernetes targets with RPO/RTO drills and restore-owner evidence.
6. Production identity/security: external OIDC/JWKS, MFA/OTP integration path,
   API allowlists, login history, certificate lifecycle, compliance export and
   erase workflows.
7. Support/observability: production monitoring stack, alert routing,
   dashboards, support bundle generation, event/task queue operations, and
   failure-drill alert evidence.

## Current Live Evidence

- Management cluster has three Ready k3s/etcd/KubeVirt nodes after an n3 k3s
  restart/recovery event.
- `tenant-a/routable-cluster` is Ready through the current provider API group,
  with CAPI/KCP/Machine Ready and routed API `/readyz` returning `ok` through
  `172.28.10.102:6443`.
- Tenant CNI is Cilium `1.19.5`; tenant CoreDNS and Cilium pods are Running.
- The provider API includes live `ProductPlan`, tenant `Order`, and tenant
  `Subscription` contracts. `ProductPlan/vm-basic`,
  `tenant-a/tenant-a-vm-basic-order`, `tenant-a/tenant-a-vm-basic-ordered`, and
  `tenant-a/tenant-a-vm-basic` are present in desired state or reconciled state,
  and the portal/API smoke creates, observes, schedules, suspends, resumes,
  renews, cancels, and deletes temporary catalog/order/subscription objects
  with audit coverage.
- Local and management-node live verification tooling is installed: `kubectl`,
  `helm`, `flux`, `virtctl`, `clusterctl`, `kubeconform`, `conftest`, `yq`,
  and `jq`.
- Legacy provider API owner reference scan returned zero repairs before CRD
  retirement.
