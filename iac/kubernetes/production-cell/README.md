# Production Cell Blueprint

This directory is an opt-in substrate blueprint for a real capacity cell. It is
not referenced by the current Hyper-V lab overlay because the lab does not have
the nodes, disks, fabric peers, or CRDs required for this layer.

The blueprint covers the production-cell primitives that the lab intentionally
does not install by default:

- Rook-Ceph storage with explicit OSD devices, CRUSH topology labels, RBD,
  CephFS, and RGW object storage.
- Cilium LoadBalancer IPAM plus BGP control-plane resources for routed service
  VIP advertisement.
- Velero backup location wiring for off-cell object storage and CSI snapshot
  integration.

Before applying in a real cell:

1. Install the Rook-Ceph operator and CRDs.
2. Install Cilium with LB IPAM and BGP control plane enabled.
3. Install Velero and its object-store provider plugin.
4. Replace every `REPLACE_WITH_*` value in these manifests.
5. Label storage and fabric nodes with the topology labels referenced here.
6. Run `iac/scripts/verify-production-cell-blueprint.ps1`.

The current workstation lab remains on Longhorn and MetalLB. This blueprint is
the repeatable production target that a larger cell should promote into GitOps.
