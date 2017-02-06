#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from sys import argv
from typing import Final, NewType, assert_never

Name = NewType("Name", str)
Namespace = NewType("Namespace", str)
Tenant = NewType("Tenant", str)
type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

CANARY_SCOPE: Final = "provider-backup-runtime-canary"
VELO_NAMESPACE: Final = "velero"
MARKERS: Final = ("provider_fixture_parse_ok", "velero_live_adapter_actions_ok", "live_adapter_status_patches_ok", "live_adapter_fail_closed_ok", "live_adapter_no_cluster_access_ok", "lab_overlay_no_live_adapter_reference_ok", "production_backup_runtime_live_adapter_ok")
VELERO_KINDS: Final = ("Schedule", "Backup", "Restore")


class TargetKind(StrEnum):
    VOLUME = "Volume"
    NAMESPACE = "Namespace"
    TENANT_CLUSTER = "KubernetesClusterClaim"


class RestoreMode(StrEnum):
    COPY = "Copy"
    IN_PLACE = "InPlace"


@dataclass(frozen=True, slots=True)
class Preflight:
    backup_storage_location: str
    volume_snapshot_location: str
    backup_repository: str
    volume_snapshot_class: str
    canary_scope: str


@dataclass(frozen=True, slots=True)
class BackupPlanFixture:
    name: Name
    namespace: Namespace
    tenant: Tenant
    target_kind: TargetKind
    schedule: str
    canary_scope: str


@dataclass(frozen=True, slots=True)
class RestoreRequestFixture:
    name: Name
    namespace: Namespace
    source_tenant: Tenant
    target_tenant: Tenant
    target_kind: TargetKind
    mode: RestoreMode
    canary_scope: str
    namespace_mapping: tuple[tuple[Namespace, Namespace], ...]
    resource_policy_ref: Name
    resource_modifier_refs: tuple[Name, ...]
    provider_approved: bool
    allow_cross_tenant: bool
    target_exists: bool


@dataclass(frozen=True, slots=True)
class ReconcileCase:
    name: str
    backup_plan: BackupPlanFixture
    restore_request: RestoreRequestFixture
    preflight: Preflight | None
    parse_error: bool = False


@dataclass(frozen=True, slots=True)
class Rejection:
    phase: str
    reason: str


def resources_for(kind: TargetKind) -> tuple[str, ...]:
    match kind:
        case TargetKind.VOLUME:
            return ("persistentvolumeclaims", "persistentvolumes", "volumesnapshots.snapshot.storage.k8s.io")
        case TargetKind.NAMESPACE:
            return ("namespaces", "networkpolicies.networking.k8s.io", "resourcequotas", "limitranges")
        case TargetKind.TENANT_CLUSTER:
            return (
                "kubernetesclusterclaims.platform.privatecloud.local",
                "clusters.cluster.x-k8s.io",
                "machines.cluster.x-k8s.io",
                "kubevirtclusters.infrastructure.cluster.x-k8s.io",
                "secrets",
                "services",
            )
        case unreachable:
            assert_never(unreachable)


def preflight_json(preflight: Preflight) -> JsonValue:
    return {
        "backupRepository": preflight.backup_repository,
        "backupStorageLocation": preflight.backup_storage_location,
        "canaryScope": preflight.canary_scope,
        "volumeSnapshotClass": preflight.volume_snapshot_class,
        "volumeSnapshotLocation": preflight.volume_snapshot_location,
    }


def reject(case: ReconcileCase) -> Rejection | None:
    restore = case.restore_request
    if case.parse_error:
        return Rejection("FailedValidation", "MalformedProviderFixture")
    if case.preflight is None or case.preflight.canary_scope != CANARY_SCOPE:
        return Rejection("Degraded", "PreflightUnavailableOrMalformed")
    if restore.canary_scope != CANARY_SCOPE or case.backup_plan.canary_scope != CANARY_SCOPE:
        return Rejection("Rejected", "CanaryScopeMismatch")
    if restore.source_tenant != restore.target_tenant and not (restore.allow_cross_tenant and restore.provider_approved):
        return Rejection("Rejected", "CrossTenantRestoreDenied")
    if len(restore.namespace_mapping) == 0 or len(restore.resource_policy_ref) == 0 or len(restore.resource_modifier_refs) == 0:
        return Rejection("FailedValidation", "NamespaceMappingResourcePolicyOrModifierMissing")
    if restore.target_exists:
        return Rejection("Rejected", "TargetCollision")
    if restore.mode == RestoreMode.IN_PLACE and restore.target_kind == TargetKind.NAMESPACE and not restore.provider_approved:
        return Rejection("Rejected", "InPlaceNamespaceRestoreApprovalMissing")
    if restore.mode == RestoreMode.IN_PLACE and restore.target_kind == TargetKind.TENANT_CLUSTER and not restore.provider_approved:
        return Rejection("Rejected", "InPlaceTenantClusterRestoreApprovalMissing")
    return None


def velero_manifest(kind: str, case: ReconcileCase, preflight: Preflight) -> JsonValue:
    plan = case.backup_plan
    restore = case.restore_request
    match kind:
        case "Schedule":
            name = f"{plan.name}-schedule"
            spec = {"schedule": plan.schedule, "template": backup_spec(case, preflight)}
        case "Backup":
            name = f"{plan.name}-canary-001"
            spec = backup_spec(case, preflight)
        case "Restore":
            name = f"{restore.name}-restore"
            spec = {
                "backupName": f"{plan.name}-canary-001",
                "includedNamespaces": [str(target) for _, target in restore.namespace_mapping],
                "includedResources": list(resources_for(plan.target_kind)),
                "namespaceMapping": [{"from": str(source), "to": str(target)} for source, target in restore.namespace_mapping],
                "resourceModifierRefs": [{"name": str(item)} for item in restore.resource_modifier_refs],
                "resourcePolicyRef": {"name": str(restore.resource_policy_ref)},
            }
        case unreachable:
            assert_never(unreachable)
    return {"apiVersion": "velero.io/v1", "kind": kind, "metadata": {"name": name, "namespace": VELO_NAMESPACE}, "spec": spec}


def backup_spec(case: ReconcileCase, preflight: Preflight) -> JsonValue:
    plan = case.backup_plan
    return {
        "includedNamespaces": [str(plan.namespace)],
        "includedResources": list(resources_for(plan.target_kind)),
        "snapshotVolumes": True,
        "storageLocation": preflight.backup_storage_location,
        "ttl": "720h0m0s",
        "volumeSnapshotLocations": [preflight.volume_snapshot_location],
    }


def happy_statuses(case: ReconcileCase) -> list[JsonValue]:
    reason = "VeleroRuntimeRendered"
    return [
        {"apiKind": "BackupPlan", "name": str(case.backup_plan.name), "namespace": str(case.backup_plan.namespace), "phase": "Protected", "reason": reason, "targetKind": case.backup_plan.target_kind.value},
        {"apiKind": "RestoreRequest", "name": str(case.restore_request.name), "namespace": str(case.restore_request.namespace), "phase": "Succeeded", "reason": reason, "targetKind": case.restore_request.target_kind.value},
    ]


def rejected_status(case: ReconcileCase, rejection: Rejection) -> JsonValue:
    return {
        "apiKind": "RestoreRequest",
        "name": str(case.restore_request.name),
        "namespace": str(case.restore_request.namespace),
        "phase": rejection.phase,
        "reason": rejection.reason,
        "targetKind": case.restore_request.target_kind.value,
    }


def case_json(case: ReconcileCase) -> JsonValue:
    rejection = reject(case)
    match rejection:
        case None:
            preflight = case.preflight
            assert preflight is not None
            return {
                "backupPlan": str(case.backup_plan.name),
                "preflight": preflight_json(preflight),
                "providerStatus": happy_statuses(case),
                "restoreRequest": str(case.restore_request.name),
                "targetKind": case.backup_plan.target_kind.value,
                "veleroManifests": [velero_manifest(kind, case, preflight) for kind in VELERO_KINDS],
            }
        case Rejection():
            return {
                "name": case.name,
                "providerStatus": [rejected_status(case, rejection)],
                "targetKind": case.backup_plan.target_kind.value,
                "veleroManifests": [],
            }
        case unreachable:
            assert_never(unreachable)


def text(source: dict[str, object], key: str) -> str | None:
    return source.get(key) if isinstance(source.get(key), str) and len(source.get(key)) > 0 else None


def flag(source: dict[str, object], key: str) -> bool:
    return source.get(key) if isinstance(source.get(key), bool) else False


def target_kind(value: object) -> TargetKind | None:
    values = (TargetKind.VOLUME.value, TargetKind.NAMESPACE.value, TargetKind.TENANT_CLUSTER.value)
    return TargetKind(value) if isinstance(value, str) and value in values else None


def restore_mode(value: object) -> RestoreMode | None:
    return RestoreMode(value) if isinstance(value, str) and value in (RestoreMode.COPY.value, RestoreMode.IN_PLACE.value) else None


def name_list(value: object) -> tuple[Name, ...]:
    return tuple(Name(item) for item in value if isinstance(item, str) and len(item) > 0) if isinstance(value, list) else ()


def mappings(value: object) -> tuple[tuple[Namespace, Namespace], ...]:
    pairs: list[tuple[Namespace, Namespace]] = []
    for item in value if isinstance(value, list) else ():
        if isinstance(item, dict) and isinstance(item.get("from"), str) and isinstance(item.get("to"), str):
            pairs.append((Namespace(item["from"]), Namespace(item["to"])))
    return tuple(pairs)


def parse_preflight(source: object) -> Preflight | None:
    if not isinstance(source, dict): return None
    bsl, vsl, repo = text(source, "backupStorageLocation"), text(source, "volumeSnapshotLocation"), text(source, "backupRepository")
    vsc, scope = text(source, "volumeSnapshotClass"), text(source, "canaryScope")
    return None if None in (bsl, vsl, repo, vsc, scope) else Preflight(bsl, vsl, repo, vsc, scope)


def malformed_case(name: str) -> ReconcileCase:
    plan = BackupPlanFixture(Name(name), Namespace("tenant-a"), Tenant("tenant-a"), TargetKind.VOLUME, "0 * * * *", CANARY_SCOPE)
    restore = RestoreRequestFixture(Name(name), Namespace("tenant-a"), Tenant("tenant-a"), Tenant("tenant-a"), TargetKind.VOLUME, RestoreMode.COPY, CANARY_SCOPE, (), Name(""), (), False, False, False)
    return ReconcileCase(name, plan, restore, None, True)


def parse_plan(source: object, name: str) -> BackupPlanFixture | None:
    if not isinstance(source, dict): return None
    kind = target_kind(source.get("targetKind"))
    required = (text(source, "name"), text(source, "namespace"), text(source, "tenant"), kind, text(source, "schedule"), text(source, "canaryScope"))
    return None if None in required else BackupPlanFixture(Name(required[0]), Namespace(required[1]), Tenant(required[2]), kind, required[4], required[5])


def parse_restore(source: object) -> RestoreRequestFixture | None:
    if not isinstance(source, dict): return None
    kind, mode = target_kind(source.get("targetKind")), restore_mode(source.get("mode"))
    required = (text(source, "name"), text(source, "namespace"), text(source, "sourceTenant"), text(source, "targetTenant"), kind, mode, text(source, "canaryScope"))
    if None in required:
        return None
    return RestoreRequestFixture(Name(required[0]), Namespace(required[1]), Tenant(required[2]), Tenant(required[3]), kind, mode, required[6], mappings(source.get("namespaceMapping")), Name(text(source, "resourcePolicyRef") or ""), name_list(source.get("resourceModifierRefs")), flag(source, "providerApproved"), flag(source, "allowCrossTenant"), flag(source, "targetExists"))


def parse_case(source: object, default_preflight: Preflight | None) -> ReconcileCase:
    if not isinstance(source, dict):
        return malformed_case("malformed-provider-fixture")
    name = text(source, "name") or "malformed-provider-fixture"
    plan, restore = parse_plan(source.get("backupPlan"), name), parse_restore(source.get("restoreRequest"))
    if plan is None or restore is None:
        return malformed_case(name)
    preflight = parse_preflight(source["preflight"]) if "preflight" in source else default_preflight
    return ReconcileCase(name, plan, restore, preflight)


def load_cases(path: str) -> tuple[ReconcileCase, ...]:
    raw: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("cases"), list):
        return (malformed_case("malformed-fixture-root"),)
    preflight = parse_preflight(raw.get("preflight"))
    return tuple(parse_case(item, preflight) for item in raw["cases"])


def build_payload(cases: tuple[ReconcileCase, ...]) -> JsonValue:
    rendered = [case_json(item) for item in cases]
    return {
        "adapterMode": "disabled-by-default-live-adapter-prototype",
        "clusterAccess": {"commandsInvoked": [], "configFilesRead": [], "mode": "offline", "networkClients": []},
        "failClosed": [item for item in rendered if len(item["veleroManifests"]) == 0],
        "happyPath": [item for item in rendered if len(item["veleroManifests"]) > 0],
        "inputMode": "json-fixtures",
        "preflightGate": {"canaryScope": CANARY_SCOPE, "failClosed": True},
    }


def main() -> None:
    if len(argv) != 2:
        raise SystemExit("usage: production-backup-runtime-live-adapter.py <fixture.json>")
    payload = build_payload(load_cases(argv[1]))
    print(f"ADAPTER_JSON:{json.dumps(payload, separators=(',', ':'), sort_keys=True)}")
    for marker in MARKERS:
        print(marker)


if __name__ == "__main__":
    main()
