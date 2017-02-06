# Test Plan

Run these checks after the cluster is installed.

## Baseline

```powershell
kubectl get nodes -o wide
kubectl get pods -A
kubectl get storageclass
kubectl get kubevirt -n kubevirt
kubectl get l2advertisements,ipaddresspools -n metallb-system
```

## SDN And Tenancy

```powershell
kubectl -n tenant-a run a --image=curlimages/curl --command -- sleep 3600
kubectl -n tenant-b run b --image=curlimages/curl --command -- sleep 3600
kubectl -n tenant-a exec a -- curl -m 3 http://kubernetes.default.svc
kubectl -n tenant-a exec a -- curl -m 3 http://tenant-b-service.tenant-b.svc
```

Expected: default deny policies block cross-tenant traffic except explicitly
allowed paths.

## Admission Guardrails

```powershell
kubectl apply --dry-run=server -f iac/kubernetes/tests/tenant-deny-loadbalancer.yaml
kubectl get clusterpolicy tenant-guardrails
```

Expected: tenant-created `LoadBalancer` service is rejected by Kyverno.

## Storage

```powershell
kubectl apply -f iac/kubernetes/tests/pvc-test.yaml
kubectl -n platform-tests get pvc,pod
kubectl -n platform-tests exec storage-test -- sh -c "echo ok >/data/probe && cat /data/probe"
```

For the KubeVirt persistent-image path, CDI must also be installed and tested:

```powershell
iac/scripts/install-cdi.sh
iac/scripts/verify-cdi-storage.sh
kubectl -n cdi get cdi,deployment,pdb
kubectl -n platform-tests get datavolume,pvc cdi-blank-rootdisk
```

Expected: CDI phase is `Deployed`; `cdi-operator`, `cdi-apiserver`,
`cdi-deployment`, and `cdi-uploadproxy` run `3/3` after management HA
hardening; the test DataVolume reaches `Succeeded`; and the backing Longhorn
PVC reaches `Bound`.

## KubeVirt

```powershell
kubectl apply -f iac/kubernetes/tests/kubevirt-vm-cirros.yaml
kubectl -n tenant-a get vm,vmi
virtctl -n tenant-a start demo-cirros
virtctl -n tenant-a console demo-cirros
```

For KubeVirt management component HA:

```powershell
iac/scripts/apply-kubevirt-ha.sh
iac/scripts/verify-kubevirt-ha.sh
```

Expected: `virt-api`, `virt-controller`, and `virt-operator` each run `3/3`
with strict hostname topology spread across n1/n2/n3, PDB `minAvailable=2`,
`virt-handler` is ready on all three Hyper-V-backed nodes, and KubeVirt remains
`Available`/`Deployed`.

## Provider Self-Service

```powershell
kubectl apply -f iac/kubernetes/tests/provider-self-service.yaml
kubectl -n platform-system rollout status deploy/provider-controller
kubectl -n tenant-c get vmi claim-smoke-vm
kubectl -n tenant-c wait vmi/claim-smoke-vm --for=condition=Ready --timeout=180s
kubectl -n tenant-c get virtualmachineclaim smoke-vm -o yaml
kubectl get capacitycells
kubectl get images
kubectl -n tenant-a get volumes.platform.privatecloud.local,networks,firewallrules,backupplans,restorerequests,accessgrants
```

Expected: `Project tenant-c` creates namespace guardrails automatically, and
`VirtualMachineClaim tenant-c/smoke-vm` creates KubeVirt VM
`claim-smoke-vm` with claim status `Ready`.

Prefer `iac/scripts/test-provider-self-service.sh` for the repeatable smoke
test because it waits for VMI creation and asserts Project/claim status.

Expected: CRDs accept valid examples, `CapacityCell lab-hyperv` reports all
three Hyper-V-backed nodes Ready with allocatable, reserved, and available
capacity, active `CapacityReservation` objects match the sum of admitted VM and
tenant Kubernetes claims and expose heartbeat/TTL/future expiry status, VM and
tenant Kubernetes claims show
`status.admission.phase=Admitted` in `lab-hyperv`, a VM claim larger than
available capacity is rejected with `InsufficientCapacity` and no backing VM or
capacity reservation,
`ProductPlan` objects publish catalog status, tenant `Subscription` objects
activate only when their Project and ProductPlan references are valid, tenant
`Order` objects can provision an Active subscription through the
`CreateSubscription` path, drive `ChangeSubscription`, `SuspendSubscription`,
`ResumeSubscription`, `RenewSubscription`, and `CancelSubscription` transitions
against an existing subscription, hold a scheduled lifecycle order in
`Scheduled` without mutating the subscription before `spec.schedule.notBefore`,
execute after the verifier opens that window, reject missing-plan orders
without creating a subscription, and keep tenant RBAC namespace-scoped for
orders and subscriptions while catalog plans stay admin-managed,
`AdmissionJournal` records exist for live admitted claims and temporary
rejected/admitted probes with the matching claim UID, decision, reason, project
quota snapshot, and controller shard identity,
VM claims can only use Ready catalog images and a claim referencing a missing
image is rejected with `ImageNotFound` without creating a backing VM or capacity
reservation,
`Project.status.quotaUsage` reports admitted VM and tenant-cluster usage,
an extra tenant Kubernetes claim beyond `Project.spec.quotas.tenantClusters`
is rejected with `ProjectQuotaExceeded` and creates no backing CAPI resources
or capacity reservation,
automatic placement skips a temporary NotReady cell and admits a VM claim into
`lab-hyperv`,
an HA tenant Kubernetes claim requesting 3 control-plane replicas in the current
lab cell is rejected with `ControlPlaneReplicaLimitExceeded` and no backing CAPI
Cluster or capacity reservation,
RBAC allows tenant admins to manage namespaced requests, `Image` reaches
`Ready`, `Volume` reaches `Bound` with PVC `claim-demo-data`, `Network` and
allow-only `FirewallRule` render `NetworkPolicy` objects, `AccessGrant` renders
a `RoleBinding`, and the demo VM-target `BackupPlan` reports `Protected` with
at least one ready KubeVirt `VirtualMachineSnapshot` recovery point. The
verifier also creates a temporary `RestoreRequest`, confirms it creates a
KubeVirt `VirtualMachineRestore` and a restored VM labeled with the restore
request, then deletes the temporary restore objects.
Use `iac/scripts/verify-provider-api-contracts.sh` to verify the extended API
CRDs, example objects, image-catalog reader binding, tenant namespace access,
backing resources, and denial of cross-tenant or cluster-scoped writes.

## Provider Controller HA

```powershell
kubectl -n platform-system get deploy,pdb,pod -l app=provider-controller -o wide
kubectl -n platform-system delete pod -l app=provider-controller --field-selector spec.nodeName=n1
kubectl -n platform-system rollout status deploy/provider-controller --timeout=180s
```

Expected: provider-controller returns to `3/3` available, PDB remains
`minAvailable: 2`, controller pods are spread across at least two nodes, and
`platform-system/provider-controller` Lease holder points at a current pod.
The `provider-controller-metrics` Service exists, every Running controller pod
serves `/metrics`, metrics expose an active leader sample, and at least one
successful reconcile sample is present. The Deployment uses
`localhost/platform-provider-controller:dev` without a pod-start `pip install`
command. `iac/scripts/verify-provider-layer.sh` enforces these invariants.

## Provider Controller Sharding

```powershell
kubectl -n platform-system get deploy provider-controller -o yaml
iac/scripts/verify-controller-sharding.sh
iac/scripts/render-provider-controller-shards.sh
iac/scripts/verify-controller-shard-topology.sh
iac/scripts/cutover-provider-controller-shards.sh dry-run
```

Expected: the active lab runtime has `provider-controller-shard-0` and
`provider-controller-shard-1`, each with three available replicas,
`CONTROLLER_SHARD_TOTAL=2`, a unique Lease, and shard metrics on every Running
pod. Exactly one shard owns global reconciliation
(`CONTROLLER_GLOBAL_SHARD_INDEX=0`), the base `provider-controller` Deployment
is held at `replicas: 0`, and deterministic namespace ownership plus the
namespace allowlist override still pass. The generated topology manifest
validates by Kubernetes server-side dry-run, contains one Deployment/PDB/metrics
Service per shard, keeps unique Lease names, and assigns global reconciliation
to exactly one shard. A live cutover or rollback gate must run
`verify-provider-layer.sh`, `verify-controller-sharding.sh`,
`verify-api-fairness.sh`, and `probe-tenant-api-reachability.sh` before being
accepted. With Flux enabled, rollback to the singleton Deployment also requires
updating the GitOps overlay or suspending `platform-base`.

## API Fairness

```powershell
kubectl get prioritylevelconfiguration platform-control tenant-limited tenant-bulk-low
kubectl get flowschema platform-service-accounts platform-admins tenant-bulk-list-watch tenant-groups
iac/scripts/verify-api-fairness.sh
```

Expected: provider service accounts and platform admins use the
`platform-control` lane, tenant interactive traffic uses `tenant-limited` with
`ByNamespace`, tenant `list`/`watch` traffic uses the lower-share
`tenant-bulk-low` lane, tenant RBAC still denies provider-internal and
cross-tenant access, and a small impersonated tenant burst does not block
platform `/readyz`, provider-controller, or Flux reads.

## Management Control-Plane HA

```powershell
kubectl get deploy,pdb -A
```

Expected: Cluster API, kubeadm bootstrap/control-plane, CAPK, cert-manager, and
CDI critical deployments each run `3/3` with PDB `minAvailable: 2` and pods
spread across at least two Hyper-V-backed nodes. CDI operand replicas are set
through supported `CDI.spec.infra.apiServerReplicas`, `deploymentReplicas`, and
`uploadProxyReplicas` fields, not by directly patching operator-owned
Deployments. Use
`iac/scripts/apply-management-control-plane-ha.sh` to enforce this state and
`iac/scripts/verify-management-control-plane-ha.sh` to verify it.

## Failure Matrix

| Test | Command/action | Pass condition |
| --- | --- | --- |
| Node loss | Dry-run: `powershell.exe -ExecutionPolicy Bypass -File .\iac\scripts\hyperv-failure-drill.ps1 -Action RestartVm -VMName platform-n3`; elevated destructive run: `Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "C:\Users\yuri\Personal\Sources\Platform\iac\scripts\hyperv-failure-drill.ps1" -Action RestartVm -VMName platform-n3 -Execute -ConfirmDestructive'` | VM name matches the guarded `platform-n1..3` pattern, SSH returns, Kubernetes node `n3` returns `Ready`, API still responds, etcd quorum remains, and follow-up platform verifiers pass |
| Worker capacity loss | Stop/restart one Hyper-V VM through `iac/scripts/hyperv-failure-drill.ps1`, then run provider and tenant reachability gates | Workloads reschedule or degrade predictably; provider API, Flux, routed tenant API, and storage health remain within the expected one-node-loss envelope |
| Data disk loss | Detach `platform-n2-longhorn.vhdx` while stopped, then boot | Longhorn reports degraded volume, rebuild possible |
| Tenant isolation | Attempt tenant-a to tenant-b traffic | Blocked unless allow policy exists |
| KubeVirt nested virtualization | `kubectl -n kubevirt logs ds/virt-handler` and create VMI | No missing `/dev/kvm` errors on workers |
| KubeVirt management component HA | Run `iac/scripts/apply-kubevirt-ha.sh` and `iac/scripts/verify-kubevirt-ha.sh` | `virt-api`, `virt-controller`, and `virt-operator` are `3/3`, protected by PDB `minAvailable=2`, strictly spread across n1/n2/n3, `virt-handler` is ready on every node, and KubeVirt reports `Available`/`Deployed` |
| Provider controller pod loss | Delete the current holder pod for either `platform-system/provider-controller-shard-0` or `provider-controller-shard-1` Lease | The shard Deployment restores 3 available replicas, that shard's Lease holder moves to another pod, and provider verifier remains green |
| Provider controller metrics | Run `iac/scripts/verify-provider-layer.sh` | `provider-controller-metrics` exists; all Running controller pods expose `/metrics`; metrics show an active leader and successful reconcile counter |
| Provider controller runtime image | Run `iac/scripts/verify-provider-layer.sh` | Shard Deployments use `localhost/platform-provider-controller:dev`, have no pod-start `pip install` command, and each shard rolls out with 3 available replicas |
| Provider controller sharding | Run `iac/scripts/verify-controller-sharding.sh` | Active shard env is `0/2` and `1/2`, shard metrics are present on every Running controller pod, each Lease holder is current, exactly one shard owns global reconciliation, stable namespace ownership is deterministic, and allowlist ownership overrides hash routing |
| Provider controller active-active shard topology | Run `iac/scripts/render-provider-controller-shards.sh` and `iac/scripts/verify-controller-shard-topology.sh` | Generated shard manifest matches the live active topology, passes server-side dry-run, has one Deployment/PDB/metrics Service per shard, unique Lease names, shard-scoped selectors, three replicas per shard, and exactly one global shard owner |
| API noisy-tenant fairness | Run `iac/scripts/verify-api-fairness.sh` | APF has separate `platform-control`, `tenant-limited`, and `tenant-bulk-low` lanes; tenant list/watch bursts are isolated by namespace and lower shares; platform health/controller/Flux reads keep succeeding during the burst |
| Provider API read-load gate | Run `iac/scripts/verify-provider-api-load.sh` | A `fresh=1` warm-up waits for every Ready portal replica to report `health.ready=true`; conditional `/api/summary` reads across all Ready portal replicas then keep at least 90% `304 Not Modified`, save at least 80% response body bytes versus full summary downloads, keep p95 conditional latency below the lab budget, expose summary response-byte metrics, and platform `/readyz`, provider-controller, Flux, and routed tenant API probes keep succeeding during the read load |
| Flux GitOps reconciliation | Run `iac/scripts/install-flux-gitops.sh` if Flux is absent, then `iac/scripts/verify-flux-gitops.sh` | Flux controllers are HA where supported with strict hostname topology spread, `minDomains=3`, and `matchLabelKeys=[pod-template-hash]` across n1/n2/n3; `source-controller` has three Running pods, exactly one Ready artifact-serving endpoint, readiness probes `/` on `http`, PDB `minAvailable=1`, and the Service endpoint matches the Lease holder; the in-cluster `platform-gitops-source` Deployment is `3/3` with PDB `minAvailable=2`, `GitRepository/platform-gitops` and `Kustomization/platform-base` are Ready on `main@sha1:*`, provider CRDs/cells remain healthy, and Flux-owned provider portal HPA bounds are present |
| Flux source-controller leader failover | Run `CONFIRM_FLUX_SOURCE_FAILOVER=true FLUX_SOURCE_FAILOVER_SCOPE=leader-node-cordon iac/scripts/verify-flux-source-failover.sh` | The script temporarily cordons the current source-controller leader node, deletes the Lease holder pod, waits for another Ready artifact-serving pod on a different Hyper-V-backed node to become leader, verifies the Lease holder and transition count changed, forces GitRepository/Kustomization reconcile, confirms the platform revision remains Ready/applied, uncordons the node, and restores strict three-node source-controller spread with a single Ready artifact endpoint |
| Provider API group migration | Run `MODE=plan iac/scripts/migrate-provider-api-group.sh`; for a controlled migration run `MODE=apply CONFIRM_PROVIDER_API_GROUP_MIGRATION=true iac/scripts/migrate-provider-api-group.sh`, then rebuild provider images and rerun provider/Flux verifiers; retire previous CRDs only with `MODE=retire CONFIRM_PROVIDER_API_GROUP_MIGRATION=true CONFIRM_PROVIDER_API_GROUP_RETIRE=true` | The migration helper discovers any previous provider API group dynamically from installed CRDs, applies `platform.privatecloud.local` CRDs, copies provider API custom resources without deleting previous CRDs, and keeps CRD retirement behind a separate explicit gate |
| Boxed-product operations coverage | Read `docs/boxed-product-operations-coverage.md` and compare the coverage matrix with `requirements/conformance/capability-evidence-matrix.md` | Provider, reseller, customer, catalog, subscription, provisioning, support, monitoring, security, backup/DR, reporting, API, and upgrade scenarios are mapped to implemented evidence or explicit promotion gates; gaps are not marked complete without live evidence |
| Provider portal/API | Run `iac/scripts/verify-provider-portal.sh` and open `http://172.28.10.101/` | Portal Deployment has at least six available replicas, GitOps seeds `spec.replicas=6`, PDB `minAvailable=4`, strict hostname topology spread for the six-replica HA floor, HPA `minReplicas=6`/`maxReplicas=9` targeting CPU 60% and memory 75%, `ScalingActive=True`, LoadBalancer IP exists, `/api/summary` is compact and includes projects, product plans, orders, subscriptions, VMs, tenant Kubernetes clusters, volumes, networks, firewall rules, backup plans, access grants, capacity cells, health, write-enabled state, OIDC/JWKS write-auth mode with issuer/audience/JWKS URI/RS256-only/group/namespace claim metadata and no HS256 secret, shared Kubernetes Lease-backed write rate-limit config, recent `SelfServiceAuditEvent` records, and cache metadata; `fresh=1` reads synchronously refresh when the target replica can acquire its refresh lock and otherwise use bounded stale/retry behavior; `/oidc/jwks.json` and `/.well-known/openid-configuration` expose the lab discovery contract; repeated reads hit the per-replica read cache; `ETag` plus `If-None-Match` returns `304 Not Modified` for unchanged inventory; stale cache payloads remain available during temporary API 429/backpressure after writes; `/metrics` exposes cache/request counters including summary `304`; unauthenticated/invalid/tampered/HS256-downgrade/expired/wrong-audience JWT write calls return `401`, wrong-tenant write calls return `403`, tenant tokens cannot create/delete `Project` or `ProductPlan`, platform-admin JWT can create/delete temporary admin-only `Project` and `ProductPlan` objects, `projectRef` namespace mismatch returns `400`, valid tenant JWT can create/delete temporary `Order`, `Subscription`, VM, tenant Kubernetes, volume, network, firewall, and access-grant resources only in its namespace through constrained provider API endpoints, the temporary `Order` provisions an Active target subscription, a scheduled suspend order remains `Scheduled` without mutating that subscription before its window, suspend/resume orders drive `Suspended`/`Active`, a renewal order reaches `Succeeded`, a cancellation order drives the target subscription to `Cancelled`, noisy authenticated tenant write burst distributed across multiple portal pods returns `429` before reaching Kubernetes, and the verifier finds durable audit records plus metrics for allowed create/delete and rate-limited attempts |
| Provider portal rendered UX | Run a browser smoke against `http://172.28.10.101/` after a fresh summary reports `health.ready=true` | Page title is `Platform Console`, the first meaningful console screen renders on desktop and mobile without framework overlays or console warnings/errors, the health badge reaches `Healthy`, sidebar navigation filters resources, tenant filter and search expose an empty state and clear back to all resources, tenant/admin action tabs hide the inactive form group, destructive row actions are hidden until a write token is present, and screenshots show no obvious text clipping or overlapping controls |
| Management controller pod loss | Delete one CAPI/CAPK/cert-manager controller pod | Deployment restores 3 available replicas, PDB remains `minAvailable: 2`, tenant cluster verifier remains green |
| CDI controller pod loss | Delete one `cdi-apiserver`, `cdi-deployment`, or `cdi-uploadproxy` pod | Deployment restores 3 available replicas, PDB remains `minAvailable: 2`, and `verify-cdi-storage.sh` still reaches DataVolume `Succeeded` |
| Tenant cluster CAPI path | Run `iac/scripts/verify-tenant-cluster-layer.sh` | CAPI/CAPK providers Ready, `KubernetesClusterClaim` reconciled, CAPK control-plane VMI Running, CAPI Machine Ready, workload node Ready |
| Provider routed tenant API gateway | Run `iac/scripts/verify-tenant-cluster-layer.sh`, `iac/scripts/probe-tenant-api-reachability.sh`, then read the current endpoint with `kubectl -n tenant-a get kubernetesclusterclaims.platform.privatecloud.local routable-cluster -o wide` and run Windows `Test-NetConnection <endpoint-ip> -Port 6443` plus `/readyz` curls. Current lab snapshot uses `172.28.10.102:6443` | Provider gateway Services in `capk-system` have MetalLB IPs, proxy Deployments run on configured gateway nodes away from the tenant VMI host when possible, each gateway has a PDB with `minAvailable=1`, Windows/provider nodes reach TCP/6443, `/readyz` returns `ok`, CAPI `Cluster.spec.controlPlaneEndpoint` and generated kubeconfig Secrets point at the routed VIPs, CAPI/KCP/Machine availability is `True`, KCC `EndpointReachable=True`, `endpointProbeReachable=true`, `endpointFailureCount=0`, and tenant-created LoadBalancer remains denied |
| Degraded tenant API endpoint suppression | Break or observe an unhealthy tenant API backend, then inspect the KCC status, provider gateway Service/Deployment, tenant CAPK Service/Endpoints, and routed `/readyz` | Transient failures increment `status.endpointFailureCount` while keeping the last known endpoint until `TENANT_API_READYZ_FAILURE_THRESHOLD`; repeated failures move the claim to `Degraded`, suppress `status.apiEndpoint`, preserve `status.lastKnownApiEndpoint`, and TCP alone is not treated as sufficient health |
| Tenant worker admission guardrail | Patch `tenant-a/routable-cluster` worker replicas to `1` in the current lab profile | `status.admission.reason=WorkerReplicasCapped`, admitted workers stay `0`, MachineDeployment replicas stay `0`, and no extra tenant worker VMI is created |
| Multi-cell placement guardrail | Run `iac/scripts/verify-provider-api-contracts.sh` | Temporary NotReady `aaa-empty-cell` is skipped and an auto-placed VM claim is admitted to Ready cell `lab-hyperv` |
| Capacity reservation ledger | Run `iac/scripts/verify-provider-api-contracts.sh` | Active `CapacityReservation` totals match admitted claims and `CapacityCell.status.reserved`; active reservations have heartbeat, TTL, and future expiry; rejected VM and HA tenant-cluster probes create no reservation; tenant RBAC cannot read reservations |
| Admission decision journal | Run `iac/scripts/verify-provider-api-contracts.sh` | `AdmissionJournal` CRD exists; live VM and tenant Kubernetes claims plus quota, capacity, image, placement, and HA guardrail probes have journal records matching claim UID, decision, and reason; tenant RBAC cannot read journals |
| Control-plane record retention | Run `iac/scripts/verify-control-plane-retention.sh` | Synthetic old `AdmissionJournal` and `SelfServiceAuditEvent` records are deleted by the global-shard reaper, synthetic fresh records remain, and controller metrics expose deletion counters for both resources |
| Capacity admission lock | Run `iac/scripts/verify-capacity-admission-lock.sh` | A synthetic `platform-system/capacity-admission-lab-hyperv` Lease forces a temporary VM claim to remain `PendingAdmission` with no backing VM or reservation; after the Lease is released the claim becomes `Ready`, creates an Active `CapacityReservation`, cleans up, and restores temporary tenant-c quota changes |
| Project quota admission lock | Run `iac/scripts/verify-project-quota-admission-lock.sh` | A synthetic `platform-system/project-quota-admission-tenant-c` Lease forces a temporary VM claim to remain `PendingAdmission` with `ProjectQuotaAdmissionLocked` and no backing VM or reservation; after the Lease is released the claim becomes `Ready`, creates an Active `CapacityReservation`, cleans up, and restores temporary tenant-c quota changes |
| Claim delete lifecycle | Run `iac/scripts/verify-claim-lifecycle.sh` | Temporary VM claim gets provider finalizer, creates VM and reservation, then delete removes the claim, VM, and reservation; temporary rejected KCC gets finalizer, creates no backing CAPI objects or reservation, and delete releases the finalizer cleanly; temporary admitted KCC creates reservation, CAPI/CAPK objects, internal Service, provider gateway Service/Deployment, and NetworkPolicy, then delete removes all of them and restores temporary quota changes |
| Tenant self-service workflow | Run `iac/scripts/verify-self-service-tenant-workflow.sh` | Project reconciliation grants `tenant-self-service` RBAC to the tenant admin group; tenant can create/delete a VM claim in its own namespace, cannot create in another tenant namespace, cannot read provider-internal reservations, and delete cleans VM plus reservation |
| VM image catalog admission | Run `iac/scripts/verify-provider-api-contracts.sh` | Catalog images `cirros` and `ubuntu-2404-kubevirt` are Ready; a VM claim that references a missing image is rejected with `ImageNotFound` before creating a VM or capacity reservation |
| CapacityCell failure-domain placement | Run `iac/scripts/verify-provider-api-contracts.sh` | The verifier confirms a VM claim with matching `placement.failureDomains` is admitted to `lab-hyperv`, then confirms impossible VM and tenant-cluster zones are rejected with `FailureDomainNotFound` without creating backing workload objects or capacity reservations |
| VM backup recovery point | Run `iac/scripts/verify-provider-api-contracts.sh` and inspect `kubectl -n tenant-a get backupplan demo-daily` plus `kubectl -n tenant-a get virtualmachinesnapshot -l platform.privatecloud.local/backupplan=demo-daily` | KubeVirt `Snapshot` feature gate is enabled, `BackupPlan/demo-daily` reports `Protected`, `recoveryPoints>=1`, and at least one provider-managed KubeVirt `VirtualMachineSnapshot` is `Succeeded` and `READYTOUSE=true` |
| VM restore from recovery point | Run `iac/scripts/verify-provider-api-contracts.sh` or create a temporary `RestoreRequest` against `tenant-a/demo-daily` | The provider request reaches `Succeeded`, KubeVirt `VirtualMachineRestore.status.complete=true`, the restored VM exists with `platform.privatecloud.local/restore-request=<request>`, target collisions are rejected, tenant RBAC can create restore requests only in its namespace, and the verifier cleans temporary restore objects |
| Production backup runtime canary simulation | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-runtime-simulation.ps1` | The local simulator compiles and emits deterministic `SIMULATION_JSON:` for `Volume`, `Namespace`, and `KubernetesClusterClaim` targets, includes Velero `Schedule`/`Backup`/`Restore` plus status actions, validates backup preflight fields, proves fail-closed restore cases emit zero Velero actions, and does not import or invoke live cluster or network clients |
| Production backup runtime API seam | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-runtime-api-seam.ps1` | The provider `RestoreRequest` CRD accepts `VirtualMachineClaim`, `Volume`, `Namespace`, and `KubernetesClusterClaim` targets plus `Copy`/`InPlace`; restore policy/status fields exist; the disabled runtime skeleton documents `BackupPlan` to Velero `Schedule`/`Backup` and `RestoreRequest` to Velero `Restore`; lab overlays do not reference the runtime; and provider-controller still rejects non-VM or non-copy restore requests with `UnsupportedTarget` |
| Production backup runtime live adapter | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-runtime-live-adapter.ps1` | The disabled-by-default local adapter compiles and emits deterministic `ADAPTER_JSON:` for `Volume`, `Namespace`, and `KubernetesClusterClaim`, renders one Velero `Schedule`, `Backup`, `Restore`, and provider status set per target, proves malformed preflight, canary mismatch, cross-tenant denial, missing restore policy, target collision, and unapproved in-place restore cases emit zero Velero manifests, scans for no cluster/network/process access, and confirms lab overlays do not reference the adapter |
| Production backup service runtime integration contract | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-service-runtime-integration.ps1` | The disabled backup runtime bundle contains template-only service integration resources, controller ownership, `Volume`/`Namespace`/`KubernetesClusterClaim` target mapping, object-store secret and Velero location wiring, immutable storage checks, ordered restore phases, preflight gates, status/audit events, SLO alert hooks, tenant-isolation rules, fail-closed negative probes, and Hyper-V lab no-reference checks |
| Production backup live controller contract | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-live-controller.ps1` | The disabled live controller contract defines runtime image handoff, reconcile states, Velero creation boundaries, idempotency keys, status patches, audit events, SLO hooks, tenant isolation, fail-closed rejected paths with zero Velero objects, no live cluster access, and Hyper-V lab no-reference checks |
| Production backup controller runtime image seam | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-backup-controller-runtime-image-seam.ps1` | The disabled runtime-image seam defines the provider backup controller image, entrypoint, required env, `BackupPlan`/`RestoreRequest` inputs, Velero `Schedule`/`Backup`/`Restore` outputs, provider status, audit, SLO, idempotency, and promotion payloads for `Volume`, `Namespace`, and `KubernetesClusterClaim`, proves malformed/unsafe/cross-tenant/enabled-without-canary cases create zero Velero objects, scans for no cluster/network/process access, and confirms Hyper-V lab overlays do not reference the seam |
| Production platform runtime blockers closure | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-platform-runtime-blockers-closure.ps1` | The aggregate closure verifier emits `production_platform_runtime_blockers_closure_ok`, reruns scheduler runtime and quota replay seams, accounts CAPK/OIDC live gaps, scans for no live cluster/process/network usage, and confirms Hyper-V lab overlays do not reference the closure |
| CAPK/OIDC runtime cutover readiness | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-capk-oidc-runtime-cutover-readiness.ps1`; for a real larger-cell promotion, rerun with `-EvidenceFile <live-evidence.json>` | Offline verifier emits `production_capk_oidc_runtime_cutover_readiness_ok`, fail-closed and lab-overlay markers, and `production_capk_oidc_runtime_cutover_live_evidence_required`; a final live run must prove 3+ tenant control-plane replicas, worker scale/upgrade/kubeconfig handoff, anti-affinity, restart/replacement, routed endpoint, cross-tenant kubeconfig denial, and OIDC/JWKS token allow/deny behavior with HS256 absent |
| Live larger-cell CAPK/OIDC preflight | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\invoke-live-larger-cell-capk-oidc-preflight.ps1`, then `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-live-larger-cell-capk-oidc-preflight.ps1 -ReportPath .omo\ulw-loop\evidence\live-larger-cell-capk-oidc-preflight.json` | The preflight is read-only and emits either `live_larger_cell_capk_oidc_preflight_ok` for a live-ready cell or `live_larger_cell_capk_oidc_preflight_blocked` plus `live_larger_cell_capk_oidc_no_aggregate_completion_claim`; the report must include Hyper-V capacity, SSH/k3s kubectl access, CAPI/CAPK providers, tenant cluster shape, tenant VMI count, and provider portal OIDC/JWKS runtime checks |
| Actual CAPK/OIDC live cutover gate | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-actual-capk-oidc-live-cutover.ps1 -ReportPath .omo\ulw-loop\evidence\actual-capk-oidc-live-cutover-report.json`; for final completion the report must reference an accepted live EvidenceFile | A blocked report emits `actual_capk_oidc_live_cutover_blocked_report_ok` and `actual_capk_oidc_live_cutover_no_aggregate_completion_claim`, records host memory, disruptive-remediation, tenant-shape, and provider OIDC blockers, and contains no mutations. A final-ready report must reference an existing live EvidenceFile accepted by `verify-production-capk-oidc-runtime-cutover-readiness.ps1 -EvidenceFile` |
| Production scheduler runtime admission seam | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-scheduler-runtime-admission-seam.ps1` | The disabled-by-default local scheduler seam compiles and emits deterministic `ADMISSION_JSON:` for VM and tenant Kubernetes `SchedulerAdmissionReview` fixtures, evaluates `Filter`/`Score`/`Reserve`/`Permit`, renders `ReservationIntent`, `QuotaAdmissionDecision`, `AdmissionJournal`, and status payloads, proves malformed, unknown-cell, quota, stale-capacity, lock, tenant-policy, and unsupported-kind cases emit zero reservation intents, scans for no cluster/network/process access, and confirms lab overlays do not reference the scheduler runtime seam |
| Production scheduler quota replay seam | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-scheduler-quota-replay-seam.ps1` | The disabled-by-default local quota replay seam compiles and emits deterministic `QUOTA_REPLAY_JSON:` for `SchedulerQuotaReplay` fixtures, renders `QuotaReplayEvent`, `QuotaRepairPlan`, `ReservationReplayDecision`, and status patches for VM and tenant Kubernetes claims, proves malformed root, wrong canary scope, missing ledger inputs, stale reservations, conflicting duplicates, quota underflow/overflow repair, unknown request kind, and cross-project replay attempts commit zero repair actions, scans for no cluster/network/process access, and confirms lab overlays do not reference the scheduler quota replay seam |
| Production scheduler replay operations contract | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-scheduler-replay-operations.ps1` | The disabled-by-default replay operations contract defines a single replay owner Lease, dry-run/canary/HA promotion gates, failover grace behavior, repair windows, audit taxonomy, tenant isolation, rollback boundary, and confirms the Hyper-V lab overlays do not reference replay operations runtime resources |
| Production scheduler work-queue runtime contract | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-scheduler-workqueue-runtime.ps1` | The disabled-by-default work-queue contract defines queue ownership, event ordering, idempotency, per-tenant weighted-round-robin fairness, duplicate suppression, backoff/dead-letter behavior, failover handoff, metrics/audit events, and confirms the Hyper-V lab overlays do not reference work-queue runtime resources |
| Production scheduler observability and SLO contract | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-scheduler-observability-slo.ps1` | The disabled-by-default observability/SLO contract defines health/readiness endpoints, queue/replay/admission metric families, SLO objectives and burn-rate alert windows, failure-domain drill evidence, tenant fairness dashboard fields, audit retention freshness signals, owner escalation, and confirms the Hyper-V lab overlays do not reference observability/SLO runtime resources |
| Production scheduler runtime cutover skeleton | Run `powershell -NoProfile -ExecutionPolicy Bypass -File iac\scripts\verify-production-scheduler-runtime-cutover.ps1` | The opt-in cutover skeleton has a separate `production-scheduler-runtime` bundle and `platform-production-scheduler-runtime` overlay, starts with `provider-scheduler-runtime-controller` at `replicas: 0`, defines fail-closed admission webhook gates, canary and HA patch examples, smoke and rollback runbooks, confirms lab overlays and contract-only scheduler overlays do not reference the cutover, and emits `production_scheduler_runtime_cutover_ok` |
| Project quota usage and admission | Run `iac/scripts/verify-provider-api-contracts.sh` | `Project.status.quotaUsage` is present for admitted VM and tenant Kubernetes usage; the verifier temporarily lowers tenant-a `tenantClusters` quota to current usage, confirms an extra tenant Kubernetes claim is rejected with `ProjectQuotaExceeded` and creates no CAPI objects or reservation, then restores quota |
| Tenant HA admission guardrail | Create a temporary `KubernetesClusterClaim` with `controlPlane.replicas=3` and service class `ha-tenant-kubernetes` in the current lab profile | Claim is rejected with `ControlPlaneReplicaLimitExceeded` before any CAPI/CAPK resources are created |
| Tenant control-plane restart | Run `CONFIRM_TENANT_CP_RESTART=true CLUSTER_CLAIM_NAME=routable-cluster iac/scripts/verify-tenant-control-plane-restart.sh` for a healthy persistent-root test cluster | The script deletes only the CAPK control-plane VMI, the recreated VMI has a new UID, the Longhorn root PVC UID is preserved, VMI may receive a new KubeVirt pod IP, CAPI/KCP/Machine return Ready, KCC endpoint readiness returns true, routed `/readyz` succeeds, stale `Unknown`/`Failed`/`Terminating` tenant `kube-system` pods are force-cleaned, tenant `kube-system` settles to Running/Succeeded, and routed reachability probes pass |
| Provider-side tenant add-on job | Run `iac/scripts/install-tenant-cni.sh` | Job uses the CAPI service/controlPlaneEndpoint, avoids the tenant VMI host node when another Ready management node exists, and Cilium reaches `deployed` in the workload cluster |

Record results in `docs/operations-log.md`.
