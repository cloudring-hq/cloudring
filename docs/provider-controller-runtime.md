# Provider Controller Runtime

The lab provider-controller now runs from a local immutable runtime image instead
of installing Python dependencies during pod startup.

## Image

- Image ref: `localhost/platform-provider-controller:dev`
- Base: `docker.io/library/python:3.12-slim`
- Dependencies: [requirements.txt](../iac/kubernetes/provider-controller/requirements.txt)
- Entrypoint: `python /opt/platform-provider-controller/controller.py`

The source still renders into the manifest ConfigMap for auditability, but the
Deployment does not mount or execute that ConfigMap. Runtime code and pinned
dependencies are packaged into the image.

## Build And Import

Run on a k3s node that already has the base image:

```bash
cd /path/to/Platform
IMAGE=localhost/platform-provider-controller:dev \
OUT=/tmp/platform-provider-controller-image.tar \
iac/scripts/build-provider-controller-image.sh
```

Import the resulting archive into every node's k3s containerd store:

```bash
sudo k3s ctr images import --base-name localhost/platform-provider-controller \
  /tmp/platform-provider-controller-image.tar
```

Then apply the active GitOps overlay, or for a manual lab rollout apply
[rendered-controller.yaml](../iac/kubernetes/provider-controller/rendered-controller.yaml),
scale the base Deployment to zero, apply
[sharded-controller.yaml](../iac/kubernetes/provider-controller/sharded-controller.yaml),
and roll the shard Deployments.

## Sharding

The lab now runs the production-style active-active shard topology:

- `provider-controller-shard-0` has `CONTROLLER_SHARD_INDEX=0`,
  `CONTROLLER_SHARD_TOTAL=2`, and owns global reconciliation with
  `CONTROLLER_GLOBAL_SHARD_INDEX=0`;
- `provider-controller-shard-1` has `CONTROLLER_SHARD_INDEX=1`,
  `CONTROLLER_SHARD_TOTAL=2`, and does not reconcile global resources;
- each shard has three HA replicas, its own Lease, PDB, and metrics Service;
- the base `provider-controller` Deployment is kept at `replicas: 0` as a
  rollback/RBAC anchor.

Namespaced reconcilers only process namespaces owned by their shard. Ownership
is computed with a stable namespace hash unless `CONTROLLER_NAMESPACE_ALLOWLIST`
is set, in which case that shard owns only the listed namespaces. Cluster-wide
resources such as `CapacityCell`, `Project`, and `Image` are reconciled only by
`CONTROLLER_GLOBAL_SHARD_INDEX`.

The checked-in shard topology is generated from:

```bash
SHARD_TOTAL=2 REPLICAS_PER_SHARD=3 iac/scripts/render-provider-controller-shards.sh
iac/scripts/verify-controller-shard-topology.sh
```

This writes
[sharded-controller.yaml](../iac/kubernetes/provider-controller/sharded-controller.yaml),
which contains two active shard Deployments with three replicas each,
shard-scoped PDBs, shard-scoped metrics Services, unique Lease names, and
`CONTROLLER_GLOBAL_SHARD_INDEX=0`. GitOps applies this shard set together with
[rendered-controller.yaml](../iac/kubernetes/provider-controller/rendered-controller.yaml)
and patches the base `provider-controller` Deployment to `replicas: 0`, so both
new installs and Flux reconciles converge on the active sharded runtime.

Cutover helpers for manual rehearsal and emergency rollback:

```bash
iac/scripts/cutover-provider-controller-shards.sh status
iac/scripts/cutover-provider-controller-shards.sh dry-run
SUSPEND_FLUX=false iac/scripts/cutover-provider-controller-shards.sh cutover
SUSPEND_FLUX=false iac/scripts/cutover-provider-controller-shards.sh rollback
```

Because Flux now owns the active sharded state, a rollback to the base
Deployment must either update the GitOps overlay or temporarily suspend
`platform-base`; otherwise Flux will reapply the sharded desired state. Keep
`verify-provider-layer.sh`, `verify-controller-sharding.sh`,
`verify-api-fairness.sh`, and `probe-tenant-api-reachability.sh` in the cutover
gate.

## Tenant API Runtime Knobs

- `TENANT_API_PROXY_NODE_HOSTNAMES=n1,n3` defines the lab provider gateway node
  pool. The controller still avoids the tenant VMI host when a non-VMI gateway
  node is available, which bypasses the known KubeVirt masquerade hairpin path.
- `TENANT_API_PROXY_MAX_REPLICAS=3` caps provider TCP proxy replicas per tenant
  cluster.
- Tenant API gateway Services use `externalTrafficPolicy=Cluster`, so routed
  MetalLB VIPs remain reachable from all provider/controller nodes while proxy
  pods run on the managed gateway pool.
- `TENANT_API_READYZ_FAILURE_THRESHOLD=3` adds endpoint health hysteresis:
  transient `/readyz` failures keep the last known endpoint, while repeated
  failures mark the claim `Degraded` and suppress `status.apiEndpoint`.
- `TENANT_API_KUBECONFIG_INSECURE_SKIP_TLS_VERIFY=true` is enabled in this
  Hyper-V lab so Cluster API remote-cluster inspection can use the provider
  routed VIP even though the current kubeadm tenant apiserver certificate was
  minted before the VIP was known. A production build should pre-allocate the
  tenant API DNS/VIP and include it in kubeadm `apiServer.certSANs`, then set
  this flag to `false`.
- The controller keeps CAPI `Cluster.spec.controlPlaneEndpoint` and the CAPI
  kubeconfig Secret aligned with the routed provider endpoint. This prevents
  CAPI/KCP inspection from depending on the raw CAPK ClusterIP path, which is
  diagnostic-only in this nested KubeVirt masquerade lab.

## Verification

```bash
kubectl -n platform-system get deploy \
  provider-controller provider-controller-shard-0 provider-controller-shard-1
kubectl -n platform-system logs deploy/provider-controller-shard-0 --tail=20
kubectl -n platform-system logs deploy/provider-controller-shard-1 --tail=20
iac/scripts/verify-controller-sharding.sh
iac/scripts/verify-controller-shard-topology.sh
```

Expected:

- image is `localhost/platform-provider-controller:dev`;
- container command is empty and comes from the image entrypoint;
- logs do not contain `Collecting kubernetes` or `pip install`;
- shard metric `provider_controller_shard_info` is present on every Running pod
  and reports shard total `2`;
- the active shard topology has one Deployment, Lease, PDB, and metrics Service
  per shard, with exactly one global shard owner;
- `iac/scripts/verify-provider-layer.sh` passes.
