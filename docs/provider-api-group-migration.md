# Provider API Group Migration

The platform API group is `platform.privatecloud.local`. Existing labs created
before this rename can be migrated without hardcoding the previous group name.
The helper discovers the previous provider API group from installed CRDs,
creates the new CRDs, copies custom resources, and only retires the previous
CRDs behind a separate confirmation gate.

## Workflow

1. Render and scan desired state:

   ```bash
   kubectl kustomize --load-restrictor=LoadRestrictionsNone gitops/platform \
     > tmp/platform-rendered-privatecloud.yaml
   ```

2. Plan the migration:

   ```bash
   KUBECTL="sudo k3s kubectl" MODE=plan \
     iac/scripts/migrate-provider-api-group.sh
   ```

3. Apply target CRDs and copy provider API resources:

   ```bash
   KUBECTL="sudo k3s kubectl" MODE=apply \
     CONFIRM_PROVIDER_API_GROUP_MIGRATION=true \
     iac/scripts/migrate-provider-api-group.sh
   ```

4. Rebuild and roll out provider-controller, provider-portal, and GitOps source
   images from the renamed repository state.

5. Repair provider-managed child object owner references. This is required for
   side-by-side migrations because Kubernetes treats controller owner references
   as exclusive, while ordinary merge patches can temporarily preserve a
   previous controller owner reference on child objects.

   ```bash
   KUBECTL="sudo k3s kubectl" MODE=plan \
     iac/scripts/repair-provider-ownerreferences.sh

   KUBECTL="sudo k3s kubectl" MODE=apply \
     CONFIRM_PROVIDER_OWNERREF_REPAIR=true \
     iac/scripts/repair-provider-ownerreferences.sh
   ```

6. Run provider verification against the new API group:

   ```bash
   KUBECTL="sudo k3s kubectl" iac/scripts/verify-provider-layer.sh
   KUBECTL="sudo k3s kubectl" iac/scripts/verify-provider-portal.sh
   KUBECTL="sudo k3s kubectl" iac/scripts/verify-flux-gitops.sh
   ```

7. Retire the previous CRDs only after the new API group is verified and a
   rollback snapshot exists:

   ```bash
   KUBECTL="sudo k3s kubectl" MODE=retire \
     CONFIRM_PROVIDER_API_GROUP_MIGRATION=true \
     CONFIRM_PROVIDER_API_GROUP_RETIRE=true \
     iac/scripts/migrate-provider-api-group.sh
   ```

## Safety Notes

- `MODE=plan` performs discovery only.
- `MODE=apply` applies the new CRDs and copies objects without deleting the
  previous CRDs.
- `repair-provider-ownerreferences.sh` does not hardcode the previous group. It
  discovers child objects whose controller owner reference points to a previous
  provider API group, then replaces that reference with the matching
  `platform.privatecloud.local` object UID.
- `MODE=retire` is intentionally separate because CRD deletion removes all
  remaining objects served by that previous API group.
- Flux `platform-base` currently uses `prune: false`, so introducing the new
  CRDs does not automatically prune the previous ones.

## 2026-06-22 Live Retirement Note

The live Hyper-V lab was checked with `repair-provider-ownerreferences.sh` from
n1 and n3. Both runs reported zero child owner reference repairs. The previous
provider API CRDs were then retired with `MODE=retire` and both confirmation
flags set. Kubernetes CRD deletion is asynchronous; keep polling API discovery
until only `platform.privatecloud.local` resources remain before accepting the
migration as fully settled.

After retirement, short names such as `kcc` and `vmc` must resolve to the new
provider API group. If discovery still reports a previous group, inspect the
remaining CRD `metadata.finalizers` and `deletionTimestamp` first; do not create
new workload claims until short-name ambiguity is gone.
