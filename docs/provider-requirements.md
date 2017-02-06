# Provider Requirements

This is the requirement set for turning the local demo into a private cloud
provider platform.

## Scale

- Add capacity horizontally by adding cells, racks, clusters, and nodes.
- Avoid a single global Kubernetes cluster for all workloads.
- Keep blast radius bounded by region, availability zone, cell, tenant, node
  pool, and storage pool.
- Shard high-cardinality APIs and controllers by cell and tenant.
- Use API Priority and Fairness for Kubernetes API overload isolation.

## Availability

- No single point of failure in API, identity, DNS, registry, GitOps, ingress,
  storage monitors, network control plane, observability, and tenant-facing
  control planes.
- Survive loss of one host, one rack/AZ, one storage device, one top-of-rack
  switch, one control-plane node, and one controller replica.
- Support rolling upgrades, node drain, live migration where storage/networking
  permits, and workload evacuation.

## Tenancy

- Tenant isolation is not only namespace isolation.
- Default tenancy unit is a Project with isolated RBAC, quotas, network,
  images, volumes, audit, and policy.
- Hard isolation tier uses per-tenant workload clusters or dedicated node pools.
- Shared-cell tier uses namespace/project isolation only for trusted or
  low-risk workloads.
- Tenants cannot create privileged pods, hostPath, host networking, arbitrary
  LoadBalancer IPs, arbitrary NetworkAttachmentDefinitions, host devices, or
  broad RBAC.

## Self-Service

- Tenants can create VMs, VM images, volumes, networks, firewall rules,
  Kubernetes clusters, kubeconfigs, backups, and service endpoints through an
  API and portal.
- Every self-service action is declarative, auditable, policy-checked, and
  reconciled by controllers.
- Admins can approve exceptions without hand-editing cluster state.

## Operations

- GitOps is the source of truth for platform add-ons and policy.
- Cluster API manages tenant Kubernetes clusters and node lifecycle.
- Observability covers platform, tenant, network, storage, API latency,
  controller queues, and saturation.
- Runbooks exist for node loss, disk loss, storage rebuild, network partition,
  API overload, tenant abuse, upgrade rollback, and disaster recovery.

## Evidence Required For Completion

The provider architecture is complete only when these are proven:

- At least two independent capacity cells can be created from IaC.
- A tenant project can self-service a VM and a Kubernetes cluster.
- Tenant A cannot affect Tenant B through network, RBAC, quota, API overload,
  image registry, storage, or privileged resource paths.
- A cell can lose one node and keep tenant workloads available within stated
  SLOs.
- Control-plane API latency and APF fairness remain within SLO during load.
- Platform upgrades are executed through GitOps with rollback evidence.
