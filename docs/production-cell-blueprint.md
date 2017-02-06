# Production Cell Blueprint

The Hyper-V lab proves the provider control-plane mechanics on one small cell.
The production target needs a stronger cell substrate before it can be repeated
as a private-cloud provider product.

This repository now carries an opt-in production cell blueprint under
`iac/kubernetes/production-cell` and a GitOps copy point under
`gitops/cells/production-cell-template`.

## Substrate Contract

Each real capacity cell should provide:

- Rook-Ceph backed block, shared filesystem, and object storage with explicit
  topology labels and rack-level failure domains.
- Cilium LoadBalancer IPAM and BGP control-plane resources for routed service
  VIP advertisement.
- Velero backup locations that send control-plane metadata to a dedicated
  off-cell object-store prefix and use CSI snapshot integration for volumes.
- Node pools and labels for storage, fabric, infra, KubeVirt, and tenants.

The manifests are marked with
`platform.privatecloud.local/template-only: "true"` and contain
`REPLACE_WITH_*` placeholders. That is deliberate: they are a repeatable
production-cell starting point, not something the workstation lab should apply.

## Promotion Steps

1. Install and verify Rook-Ceph, Cilium, and Velero CRDs/operators in the target
   cell.
2. Copy `gitops/cells/production-cell-template` to a concrete cell overlay.
3. Replace placeholder OSD devices, BGP ASNs, ToR addresses, load-balancer
   ranges, object-store endpoint, bucket, region, and cell ID.
4. Label nodes for storage, fabric, infra, KubeVirt, tenants, region, zone, and
   rack before creating the CephCluster.
5. Run `iac/scripts/verify-production-cell-blueprint.ps1`.
6. Apply in a non-critical cell, wait for Ceph `HEALTH_OK`, confirm Cilium IP
   pool status is not conflicting, and run backup/restore drills.

## Current Scope

This does not replace Longhorn in the Hyper-V lab and does not prove a real
multi-cell deployment yet. It moves the repository closer to the target state by
making the production substrate explicit, reviewable, and promotable through
GitOps instead of leaving storage, fabric, and backup as prose-only roadmap
items.
