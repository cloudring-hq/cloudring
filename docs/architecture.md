# Lab Architecture

## Goals

Build a complete local demo platform that shows how a multi-tenant Kubernetes
environment can host containers and KubeVirt virtual machines with SDN,
distributed storage, tenant isolation, and operational documentation.

For the production/provider target architecture, see
`docs/target-provider-architecture.md`. This file describes the local Hyper-V
lab profile that proves the core stack on one workstation.

## Stack

| Layer | Component | Reason |
| --- | --- | --- |
| Hypervisor | Hyper-V | Available on the Windows host; VMs model physical servers |
| Guest OS | Ubuntu Server 24.04 cloud image | Fast unattended Hyper-V provisioning with cloud-init |
| Kubernetes | k3s HA | Lightweight Kubernetes distribution with embedded etcd and simple bootstrap |
| CNI / SDN | Cilium | NetworkPolicy, eBPF datapath, Hubble observability |
| LoadBalancer | MetalLB | Bare-metal style service exposure on the lab subnet |
| Storage | Longhorn | Replicated block storage across worker-node data disks |
| VM runtime | KubeVirt + CDI | Kubernetes-native VM lifecycle and image upload/import |
| Policy | Kyverno + Pod Security Admission | Admission guardrails for tenant workloads |
| Extra VM networking | Multus planned | Secondary network attachment demos for VM/pod workloads |
| Tenancy | Namespaces, RBAC, ResourceQuota, LimitRange, NetworkPolicy, Kyverno | Basic boundaries for demo tenants |

## HA Model

The lab uses three converged Kubernetes VMs. Each VM is a k3s server, etcd
member, schedulable worker, Longhorn storage node, and KubeVirt-capable host.
This is intentionally compact for a 32 GiB Windows workstation while retaining
the ability to demonstrate quorum and single-node failure.

Expected survivable failures:

| Failure | Expected behavior |
| --- | --- |
| Stop one node VM | Kubernetes API remains available with 2/3 etcd quorum |
| Stop one node VM hosting workloads | Pods/VMs reschedule if policy and storage allow it |
| Detach one node data disk | Longhorn marks replicas degraded and rebuilds elsewhere |
| Block one tenant namespace egress | Other tenant namespaces are unaffected |

Not survivable:

| Failure | Reason |
| --- | --- |
| Physical host power-off | Single host contains every simulated physical node |
| Physical disk loss | VM disks and Longhorn replicas share host storage |
| Host Wi-Fi/network loss | External access depends on the same Windows host |

## Network Design

The default build uses a Hyper-V internal switch named `Platform-Fabric` and a
Windows NAT named `PlatformNAT`.

| Address | Use |
| --- | --- |
| 172.28.10.1 | Windows host gateway on the Hyper-V switch |
| 172.28.10.11-13 | Converged Kubernetes nodes |
| 172.28.10.100-119 | MetalLB pool |

This avoids changing the user's Wi-Fi adapter during initial provisioning. If
LAN clients must access services directly, add explicit Windows portproxy rules
or later replace the lab switch with an external Hyper-V switch.
