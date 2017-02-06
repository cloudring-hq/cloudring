# #CloudRING Platform by OPENCLOUDTECH

#CloudRING Platform by OPENCLOUDTECH is a private cloud and cloud-provider
platform project. This
repository contains the documentation and infrastructure-as-code for a local
Hyper-V demo of a multi-tenant Kubernetes platform with KubeVirt, SDN, storage,
and high-availability behavior at the VM-as-physical-host layer.

The target machine is a Windows 11 Pro Hyper-V host. Every Hyper-V VM is treated
as a physical server. Nested virtualization is enabled on every Kubernetes VM so
KubeVirt can use KVM inside the guest.

## Architecture Direction

The current Hyper-V lab is a compact proof point, not the final private-cloud
provider shape. The target architecture is a horizontally scalable, cell-based
private cloud:

- a management plane for identity, portal/API, billing/quota, GitOps, policy,
  inventory, and fleet lifecycle;
- many independent capacity cells, each with its own Kubernetes/KubeVirt,
  storage, network, ingress, observability, and failure domain boundaries;
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

## Current Topology

| Node | Role | vCPU | RAM | OS disk | Data disk | IP |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| n1 | k3s server / etcd / worker / KubeVirt / Longhorn | 4 | 7 GiB | 64 GiB | 180 GiB | 172.28.10.11 |
| n2 | k3s server / etcd / worker / KubeVirt / Longhorn | 4 | 7 GiB | 64 GiB | 180 GiB | 172.28.10.12 |
| n3 | k3s server / etcd / worker / KubeVirt / Longhorn | 4 | 7 GiB | 64 GiB | 180 GiB | 172.28.10.13 |

The lab uses an internal Hyper-V switch with Windows NAT:

| Network | Purpose |
| --- | --- |
| 172.28.10.0/24 | Node management, Kubernetes API, LoadBalancer demo pool |
| 172.28.10.1 | Windows host gateway |
| 172.28.10.100-172.28.10.119 | MetalLB L2 pool for services |

The first runnable target is `iac/powershell/New-PlatformHyperVLab.ps1`.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `docs/` | Architecture notes, operating model, test plan, and Slite import notes |
| `iac/powershell/` | Hyper-V host and VM provisioning scripts |
| `iac/cloud-init/` | Generated NoCloud seed files per VM |
| `iac/kubernetes/` | Kubernetes add-on and tenant manifests |
| `iac/scripts/` | In-cluster verification and provider smoke-test scripts |
| `gitops/` | Initial GitOps overlay structure |
| `portal/` | Initial Backstage catalog/template skeletons |
| `scripts/` | Local helper scripts |
| `logs/` | Execution logs from elevated and provisioning runs |

## Build Order

1. Run the Hyper-V provisioning script elevated.
2. Wait for cloud-init to complete and SSH to become available.
3. Install Kubernetes with k3s embedded etcd.
4. Install Cilium, MetalLB, Longhorn, KubeVirt, Kyverno, and tenant policies.
5. Apply provider API CRDs/RBAC.
6. Render and deploy the lightweight provider controller.
7. Run `iac/scripts/verify-provider-layer.sh` and
   `iac/scripts/test-provider-self-service.sh`.
8. Run the broader verification matrix in `docs/test-plan.md`.

## Important Reality Boundary

The lab can demonstrate failure of individual Hyper-V VMs, guest disks, and
virtual networks. It cannot survive loss of the single physical Windows host,
host storage, or host network adapter, because all simulated physical hosts live
on the same computer.

## License

#CloudRING Platform by OPENCLOUDTECH, including the CloudRING source code, source texts,
architecture, documentation, specifications, designs, scripts, and other
authored project materials in this repository, belongs to Elena Trukhina ZZP
and is controlled by Elena Trukhina ZZP as the project owner and licensor,
except for third-party materials and files that carry their own notices.

Development, packaging, deployment assistance, support, operations, and
commercial services for #CloudRING Platform by OPENCLOUDTECH are performed by
Elena Trukhina ZZP.

#CloudRING Platform by OPENCLOUDTECH is licensed under the Elastic License 2.0. See
`LICENSE`, `NOTICE`, `BRANDING.md`, and
`docs/legal/cloudring-licensing-and-ownership.md`.

The license permits broad private and internal use, including private cloud
infrastructure. Installing, accessing, running, funding, reviewing, modifying,
integrating, or operating the platform inside a company environment is licensed
use only and does not transfer ownership, relicensing authority, trademark
rights, product direction, or exclusive rights to that company.

Company-specific changes must stay in a fork, branch, patch set, or separate
integration layer that preserves the repository notices and remains subject to
this license. All commits, pull requests, patches, forks, mirrors, copies,
clones, and derivative repositories for OPENCLOUDTECH/opencloudtech company
projects are made subject to the license used in this project unless Elena
Trukhina ZZP signs a separate written agreement. The license does not permit
providing #CloudRING Platform by OPENCLOUDTECH itself, or a substantial set of
CloudRING features, as a hosted or managed service, public cloud provider
offering, SaaS, PaaS, IaaS, MSP, or similar third-party cloud service without
prior written permission from Elena Trukhina ZZP.
