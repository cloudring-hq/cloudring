# CAPK And OIDC Runtime Cutover Readiness

This readiness contract is the gate between the current compact Hyper-V lab and
the final production-style platform claim.

## Current Live Lab Evidence

The existing lab has already proven a single-control-plane CAPK tenant cluster
path:

- Cluster API and CAPK controllers are installed and HA in the management
  cluster.
- `tenant-a/routable-cluster` reconciles through `KubernetesClusterClaim`,
  Cluster API, CAPK, KubeVirt, Longhorn-backed CDI root disks, Cilium, and a
  provider-owned routed tenant API gateway.
- `verify-tenant-cluster-layer.sh`, `verify-claim-lifecycle.sh`, and
  `verify-tenant-control-plane-restart.sh` cover the current small-cell
  lifecycle, routed kubeconfig handoff, finalizer cleanup, persistent-root
  restart recovery, and tenant API reachability.

That evidence is not enough for the final production claim, because the current
cell intentionally caps worker replicas at `0` and rejects 3-control-plane
tenant clusters.

## Required Larger-Cell Evidence

A final production run must capture all of these fields in a live evidence file
before the aggregate goal can be closed:

- `cellProfile.name`
- `cellProfile.managementNodesReady >= 3`
- `tenantCluster.claim`
- `tenantCluster.controlPlaneReplicas >= 3`
- `tenantCluster.workerPools[].replicas >= 1`
- `tenantCluster.scaleProof.status == passed`
- `tenantCluster.upgradeProof.status == passed`
- `tenantCluster.kubeconfigHandoff.status == passed`
- `tenantCluster.antiAffinity.status == passed`
- `tenantCluster.restartReplacement.status == passed`
- `tenantCluster.providerRoutedEndpoint.status == passed`
- `tenantCluster.crossTenantKubeconfig.status == denied`

The live run must be produced by a larger-cell promotion, not by the default
`gitops/cells/lab-hyperv` overlay.

## OIDC/JWKS Runtime Evidence

A final production run must also capture provider-portal runtime evidence:

- `identity.mode == oidc-jwks`
- `identity.issuer` is not a `REPLACE_WITH_*` placeholder.
- `identity.jwksUri` is not a `REPLACE_WITH_*` placeholder.
- `identity.allowedAlgorithms` contains `RS256` or `ES256` and excludes
  `HS256`.
- `identity.groupsClaim` and `identity.namespacesClaim` are set.
- `identity.labHs256EnvPresent == false`
- `identity.validTenantToken.status == allowed`
- `identity.crossTenantToken.status == denied`
- `identity.invalidSignature.status == denied`
- `identity.expiredToken.status == denied`

The production identity overlay exists today, and the lab runtime exercises the
same `oidc-jwks` RS256 validation path with deterministic self-hosted keys.
That is acceptable for the compact demo and still insufficient for the final
production-style claim, which must use an external issuer and accepted live
token/JWKS evidence.

## Promotion Rule

The readiness verifier added for this contract is disabled-by-default and
offline. It validates the IaC contracts, evidence schema, fail-closed behavior,
and lab-overlay boundary. It does not mutate Hyper-V, Kubernetes, identity
providers, or tenant clusters.

Offline contract evidence is non-final.
