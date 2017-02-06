# Decision Record

## 2026-06-17: Local HA Shape

Decision: use three converged Hyper-V VMs instead of six split
control-plane/worker VMs.

Rationale: the host has about 32 GiB RAM. Three 7 GiB nodes leave enough memory
for Windows while still demonstrating etcd quorum, Cilium policy, Longhorn
replication, and KubeVirt nested virtualization. A 9 GiB profile was attempted
and the third VM could not start due to host memory pressure.

Tradeoff: this is not a production control-plane isolation pattern. It is a
resource-fit architecture demo.

## 2026-06-17: Kubernetes Distribution

Decision: use k3s with embedded etcd.

Rationale: k3s supports HA embedded etcd with an odd number of server nodes and
is much simpler to bootstrap repeatedly on local VMs than kubeadm for this demo.

## 2026-06-17: Network

Decision: start with a Hyper-V internal switch plus Windows NAT.

Rationale: it avoids disrupting the host Wi-Fi adapter. MetalLB uses a pool on
the lab L2 subnet. External LAN access can be added later with portproxy rules
or by moving the lab to an external switch.

## Source Notes

The Slite documents requested by the user were not readable anonymously from
this environment. The interim build decisions use public primary docs:

- Kubernetes HA with kubeadm and multi-tenancy concepts.
- K3s HA embedded etcd documentation.
- Cilium Kubernetes and k3s installation documentation.
- KubeVirt installation, architecture, authorization, CDI, networking, and live
  migration documentation.
- MetalLB concepts and configuration documentation.
- Longhorn installation and best-practice documentation.
