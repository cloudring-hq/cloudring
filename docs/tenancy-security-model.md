# Tenancy And Security Model

## Baseline

The current provider controller creates these guardrails for every tenant
Project:

- namespace labels for Pod Security Admission;
- ResourceQuota and LimitRange;
- default-deny NetworkPolicy;
- scoped RBAC;
- explicit allowed service exposure paths;
- audit labels and ownership metadata.

VM claims are constrained to provider catalog images: the controller only
accepts `spec.image.source: catalog`, requires a Ready `Image`, enforces
`visibility`/`allowedProjects`, and passes the catalog `registryRef` to
KubeVirt. The target production baseline still needs isolated registry
credentials and signed-image enforcement.

## Tenant Namespace Labels

For namespaces that may host KubeVirt VMs, use:

- `pod-security.kubernetes.io/enforce=baseline`
- `pod-security.kubernetes.io/warn=restricted`
- `pod-security.kubernetes.io/audit=restricted`

For container-only namespaces, use restricted enforcement:

- `pod-security.kubernetes.io/enforce=restricted`
- `pod-security.kubernetes.io/warn=restricted`
- `pod-security.kubernetes.io/audit=restricted`

KubeVirt launcher pods may need permissions that are not compatible with strict
restricted enforcement, so VM namespaces use baseline enforcement plus admission
policies for KubeVirt-specific dangerous fields.

## Deny By Default

Tenants must not create:

- privileged pods;
- hostPath volumes;
- hostNetwork, hostPID, or hostIPC pods;
- arbitrary `LoadBalancer` Services;
- arbitrary `NetworkAttachmentDefinition` resources;
- KubeVirt host devices;
- node selectors that target privileged node pools;
- RBAC bindings outside their Project;
- cluster-scoped objects.

## Strong Isolation

For untrusted tenants, provide one of:

- dedicated tenant workload cluster;
- dedicated worker pool with taints/tolerations controlled by platform policy;
- dedicated capacity cell.

Hard tenant isolation is proven by tests across network, API, storage, RBAC,
quota, scheduling, and controller behavior, not by namespace presence alone.
