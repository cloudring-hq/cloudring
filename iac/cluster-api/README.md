# Cluster API Tenant Cluster Layer

Tenant Kubernetes clusters must be lifecycle-managed through Cluster API, not
hand-created VMs.

The intended production path is:

1. Management plane runs Cluster API core.
2. Capacity cell exposes KubeVirt as one infrastructure provider.
3. `KubernetesClusterClaim` is translated into Cluster API `Cluster`,
   `KubeadmControlPlane`, `MachineDeployment`, and CAPK `KubevirtCluster` /
   `KubevirtMachineTemplate` resources.
4. GitOps applies add-ons into the tenant cluster after it becomes reachable.

Current lab status:

- KubeVirt is installed and working.
- Provider API CRDs exist for tenant cluster claims.
- `install-capi-capk.sh` installs CAPI/CAPK through `clusterctl` and records
  provider inventory objects.
- The provider controller reconciles `KubernetesClusterClaim` into CAPI/CAPK
  objects.
- `tenant-a/demo-cluster` has been rebuilt on the current persistent-root path
  and verified through CAPK-created control-plane VMI `Running`, kubeadm
  bootstrap, Cilium installation, and workload node `Ready`.
- New CAPK tenant node templates use CDI `DataVolume` root disks on Longhorn
  and expose KubeVirt masquerade ports `22` and `6443`. The live
  `tenant-a/demo-cluster` and `tenant-a/routable-cluster` both have Longhorn
  root PVCs; `routable-cluster` was also verified through VMI delete/recreate,
  root PVC UID preservation, and CAPI Machine recovery after the KubeVirt pod
  IP changed.
- `iac/scripts/install-tenant-cni.sh` installs Cilium into the tenant cluster
  from the provider namespace using the generated kubeconfig. In the Hyper-V
  lab it uses the CAPI service/controlPlaneEndpoint and schedules the installer
  on a Ready management node different from the tenant VMI node when possible
  to avoid KubeVirt masquerade same-node hairpin timeouts.
- `iac/scripts/apply-management-control-plane-ha.sh` hardens CAPI/CAPK and
  cert-manager controllers with 3 replicas, PDBs, and topology spread. When CDI
  is installed, the same script sets CDI operand HA through the supported
  `CDI.spec.infra.*Replicas` fields and verifies the operator-owned
  deployments at `3/3`.
- `iac/scripts/install-cdi.sh` installs CDI and `iac/scripts/verify-cdi-storage.sh`
  verifies the DataVolume-to-Longhorn storage path.

Production target:

- Tenant cluster control plane can be 1, 3, or 5 replicas.
- Workers are MachineDeployments with autoscaling node pools.
- Tenant cluster API endpoint is exposed through a provider-managed load
  balancer, not tenant-created LoadBalancer resources. The lab-internal
  ClusterIP endpoint is sufficient only for provider-side jobs inside the
  management cluster.
- Upgrades are Cluster API rolling upgrades with surge/partition controls.
