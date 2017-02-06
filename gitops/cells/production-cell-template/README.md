# Production Cell Template

This overlay is a copy point for real capacity cells. Do not add it to
`gitops/platform` or `gitops/cells/lab-hyperv` until the target cell has the
required operators, CRDs, node labels, OSD devices, BGP peers, and backup
object storage credentials.

For a real cell:

1. Copy this directory to `gitops/cells/<cell-id>`.
2. Replace all `REPLACE_WITH_*` values under
   `../../iac/kubernetes/production-cell` or add patches in the copied overlay.
3. Run `iac/scripts/verify-production-cell-blueprint.ps1`.
4. Promote the copied overlay through GitOps waves.
