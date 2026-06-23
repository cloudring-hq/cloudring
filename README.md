# CloudRING

CloudRING is an open platform project for building private, public, and
federated cloud-provider environments. It combines Kubernetes, KubeVirt,
software-defined networking, GitOps/IaC, tenant self-service, and provider
operations into a control-plane model that can start in a compact lab and grow
toward bare-metal, colocated, or corporate virtualization deployments.

This repository contains the documentation and infrastructure-as-code for a
multi-tenant upstream Kubernetes platform with KubeVirt, SDN, storage,
provider APIs, tenant self-service, and high-availability operating patterns.

## Architecture Direction

The target architecture is a horizontally scalable, cell-based cloud platform:

- a management plane for identity, portal/API, billing/quota, GitOps, policy,
  inventory, and fleet lifecycle;
- many independent capacity cells, each with upstream Kubernetes, KubeVirt,
  storage, network, ingress, observability, and failure-domain boundaries;
- self-service APIs for tenant projects, VMs, tenant Kubernetes clusters,
  networks, volumes, images, backup, and access;
- hard multi-tenancy with per-tenant projects, policy, quotas, network
  isolation, audit, and a path to dedicated clusters/pools for high-trust or
  noisy tenants;
- no single point of failure inside a site, and a multi-site pattern for
  disaster recovery.

See `docs/target-provider-architecture.md` for the provider-grade design and
`docs/boxed-product-operations-coverage.md` for the boxed-provider operations
coverage matrix.

## Platform Layers

| Layer | Purpose |
| --- | --- |
| Provider management plane | Identity, portal/API, catalog, billing/quota, policy, GitOps, audit, and fleet lifecycle |
| Capacity cells | Upstream Kubernetes, KubeVirt, storage, network fabric, ingress, observability, and cell-local failure domains |
| Tenant foundation | Projects, quotas, RBAC, network isolation, image access, backup policy, and tenant-scoped audit |
| Self-service services | VM, tenant Kubernetes cluster, network, volume, object storage, backup, and access workflows |
| Operations plane | Upgrade, repair, placement, capacity, observability, incident, and disaster-recovery workflows |

## Repository Layout

| Path | Purpose |
| --- | --- |
| `docs/` | Architecture notes, operating model, test plan, and Slite import notes |
| `iac/powershell/` | Windows-based lab and bootstrap automation |
| `iac/cloud-init/` | Generated NoCloud seed files for lab nodes |
| `iac/kubernetes/` | Kubernetes add-on and tenant manifests |
| `iac/scripts/` | In-cluster verification and provider smoke-test scripts |
| `gitops/` | Initial GitOps overlay structure |
| `portal/` | Initial Backstage catalog/template skeletons |
| `scripts/` | Local helper scripts |
| `logs/` | Execution logs from elevated and provisioning runs |

## Build Order

1. Provision a lab or target environment with the selected IaC profile.
2. Wait for node bootstrap to complete and administrative access to become available.
3. Install upstream Kubernetes control-plane and worker nodes.
4. Install Cilium, MetalLB, Longhorn, KubeVirt, Kyverno, and tenant policies.
5. Apply provider API CRDs/RBAC.
6. Render and deploy the lightweight provider controller.
7. Run `iac/scripts/verify-provider-layer.sh` and
   `iac/scripts/test-provider-self-service.sh`.
8. Run the broader verification matrix in `docs/test-plan.md`.

## Lab Boundary

Lab profiles are compact validation environments. Production deployments should
place management services, capacity cells, storage, network paths, and backup
targets across independent fault domains.
