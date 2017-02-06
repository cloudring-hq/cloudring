#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from sys import argv
from typing import Any, Final

IMAGE: Final = "registry.example.invalid/privatecloud/provider-backup-controller:REPLACE_WITH_VERSION"
ENTRYPOINT: Final = "/usr/local/bin/provider-backup-controller"
CANARY_SCOPE: Final = "provider-backup-runtime-canary"
TARGETS: Final = ("Volume", "Namespace", "KubernetesClusterClaim")
STATES: Final = ("observed", "preflighted", "planned", "velero-objects-created", "status-patched", "audit-recorded", "slo-recorded", "completed")
SLO_HOOKS: Final = (
    "backup_runtime_reconcile_duration_seconds",
    "backup_runtime_velero_create_total",
    "backup_runtime_idempotency_replay_total",
    "backup_runtime_status_patch_total",
    "backup_runtime_audit_event_total",
)


class Phase(StrEnum):
    SUCCEEDED = "Succeeded"
    REJECTED = "Rejected"
    FAILED_VALIDATION = "FailedValidation"


@dataclass(frozen=True)
class Runtime:
    image: str
    entrypoint: str
    runtime_enabled: bool
    canary_scope: str


@dataclass(frozen=True)
class Case:
    name: str
    target_kind: str
    project_ref: str
    target_project_ref: str
    backup_uid: str
    restore_uid: str
    generation: int
    preflight: bool
    immutable: bool
    duplicate_key: bool = False
    missing_status: bool = False
    missing_audit: bool = False
    missing_slo: bool = False


def nested_get(raw: dict[str, Any], path: tuple[str, ...], default: object = "") -> object:
    cursor: object = raw
    for key in path:
        if not isinstance(cursor, dict) or key not in cursor:
            return default
        cursor = cursor[key]
    return cursor


def first_value(raw: dict[str, Any], paths: tuple[tuple[str, ...], ...], default: object = "") -> object:
    for path in paths:
        value = nested_get(raw, path, None)
        if value not in (None, ""):
            return value
    return default


def parse_runtime(raw: object) -> Runtime:
    if not isinstance(raw, dict):
        return Runtime("", "", False, "")
    return Runtime(
        image=str(raw.get("image") or ""),
        entrypoint=str(raw.get("entrypoint") or ""),
        runtime_enabled=bool(raw.get("runtimeEnabled")),
        canary_scope=str(raw.get("canaryScope") or ""),
    )


def parse_case(raw: object) -> Case:
    if not isinstance(raw, dict):
        return Case("malformed", "Volume", "", "", "", "", 0, False, False, missing_status=True)
    provider = raw
    backup_plan = raw.get("backupPlan") if isinstance(raw.get("backupPlan"), dict) else {}
    restore_request = raw.get("restoreRequest") if isinstance(raw.get("restoreRequest"), dict) else {}
    backup_metadata = backup_plan.get("metadata", {}) if isinstance(backup_plan, dict) else {}
    backup_spec = backup_plan.get("spec", {}) if isinstance(backup_plan, dict) else {}
    restore_metadata = restore_request.get("metadata", {}) if isinstance(restore_request, dict) else {}
    restore_spec = restore_request.get("spec", {}) if isinstance(restore_request, dict) else {}
    source = {
        **provider,
        "backupPlanMetadata": backup_metadata,
        "backupPlanSpec": backup_spec,
        "restoreRequestMetadata": restore_metadata,
        "restoreRequestSpec": restore_spec,
    }
    return Case(
        name=str(first_value(source, (("name",), ("backupPlanMetadata", "name")), "unnamed")),
        target_kind=str(first_value(source, (("targetKind",), ("backupPlanSpec", "targetKind")), "Volume")),
        project_ref=str(first_value(source, (("projectRef",), ("backupPlanSpec", "projectRef"), ("backupPlanMetadata", "labels", "platform.privatecloud.local/project")), "")),
        target_project_ref=str(first_value(source, (("targetProjectRef",), ("restoreRequestSpec", "targetProjectRef"), ("restoreRequestSpec", "projectRef")), "")),
        backup_uid=str(first_value(source, (("backupUid",), ("backupPlanMetadata", "uid")), "")),
        restore_uid=str(first_value(source, (("restoreUid",), ("restoreRequestMetadata", "uid")), "")),
        generation=int(first_value(source, (("generation",), ("backupPlanMetadata", "generation")), 0) or 0),
        preflight=bool(first_value(source, (("preflight",), ("backupPlanSpec", "preflightReady"), ("restoreRequestSpec", "preflightReady")), False)),
        immutable=bool(first_value(source, (("immutable",), ("backupPlanSpec", "immutableStorage"), ("restoreRequestSpec", "immutableStorage")), False)),
        duplicate_key=bool(first_value(source, (("duplicateKey",), ("backupPlanSpec", "duplicateKey")), False)),
        missing_status=bool(first_value(source, (("missingStatus",), ("backupPlanSpec", "missingStatus")), False)),
        missing_audit=bool(first_value(source, (("missingAudit",), ("backupPlanSpec", "missingAudit")), False)),
        missing_slo=bool(first_value(source, (("missingSlo",), ("backupPlanSpec", "missingSlo")), False)),
    )


def runtime_rejection(runtime: Runtime) -> str | None:
    if runtime.image != IMAGE or runtime.entrypoint != ENTRYPOINT:
        return "MissingRuntimeImageHandoff"
    if runtime.runtime_enabled and runtime.canary_scope != CANARY_SCOPE:
        return "EnabledWithoutCanaryScopeDenied"
    return None


def case_rejection(case: Case) -> str | None:
    if case.target_kind not in TARGETS:
        return "UnsupportedTargetKind"
    if not case.project_ref or not case.backup_uid or not case.restore_uid:
        return "MalformedProviderFixture"
    if case.duplicate_key:
        return "DuplicateIdempotencyKeySuppressed"
    if not case.preflight:
        return "VeleroCreateBeforePreflightDenied"
    if not case.immutable:
        return "MutableStoragePolicyDenied"
    if case.project_ref != case.target_project_ref:
        return "CrossTenantRestoreDenied"
    if case.missing_status:
        return "MissingStatusPatchDenied"
    if case.missing_audit:
        return "MissingAuditEventDenied"
    if case.missing_slo:
        return "MissingSloHookDenied"
    return None


def idempotency(case: Case) -> dict[str, str]:
    return {
        "schedule": f"{case.backup_uid}:{case.generation}:{case.target_kind}:schedule",
        "backup": f"{case.backup_uid}:{case.generation}:{case.target_kind}:backup",
        "restore": f"{case.restore_uid}:{case.generation}:{case.target_kind}:restore",
    }


def velero(case: Case) -> list[dict[str, object]]:
    labels = {"platform.privatecloud.local/project": case.project_ref, "platform.privatecloud.local/target-kind": case.target_kind}
    included_namespaces = [case.project_ref] if case.target_kind in {"Namespace", "KubernetesClusterClaim"} else []
    included_resources = {
        "Volume": ["persistentvolumes", "persistentvolumeclaims"],
        "Namespace": ["namespaces", "deployments", "services", "persistentvolumeclaims"],
        "KubernetesClusterClaim": ["kubernetesclusterclaims", "clusters.cluster.x-k8s.io", "machines.cluster.x-k8s.io"],
    }[case.target_kind]
    return [
        {
            "apiVersion": "velero.io/v1",
            "kind": "Schedule",
            "metadata": {"name": f"{case.name}-schedule", "labels": labels},
            "spec": {
                "schedule": "0 */6 * * *",
                "template": {
                    "includedNamespaces": included_namespaces,
                    "includedResources": included_resources,
                    "storageLocation": "primary-offsite",
                    "snapshotVolumes": True,
                    "ttl": "720h0m0s",
                },
            },
        },
        {
            "apiVersion": "velero.io/v1",
            "kind": "Backup",
            "metadata": {"name": f"{case.name}-backup", "labels": labels},
            "spec": {
                "includedNamespaces": included_namespaces,
                "includedResources": included_resources,
                "storageLocation": "primary-offsite",
                "snapshotVolumes": True,
                "ttl": "720h0m0s",
            },
        },
        {
            "apiVersion": "velero.io/v1",
            "kind": "Restore",
            "metadata": {"name": f"{case.name}-restore", "labels": labels},
            "spec": {
                "backupName": f"{case.name}-backup",
                "includedNamespaces": included_namespaces,
                "includedResources": included_resources,
                "namespaceMapping": {case.project_ref: case.target_project_ref},
                "restorePVs": True,
            },
        },
    ]


def status(case: Case) -> list[dict[str, object]]:
    return [
        {
            "apiKind": "BackupPlan",
            "phase": "Protected",
            "lastRun": f"{case.name}-backup",
            "lastSuccess": f"{case.name}-backup",
            "conditions": [{"type": "RuntimeImageReady", "status": "True"}, {"type": "VeleroObjectsCreated", "status": "True"}],
        },
        {
            "apiKind": "RestoreRequest",
            "phase": "Succeeded",
            "veleroRestoreName": f"{case.name}-restore",
            "conditions": [{"type": "TenantIsolationVerified", "status": "True"}, {"type": "RestoreCreated", "status": "True"}],
        },
    ]


def render_case(runtime: Runtime, case: Case) -> dict[str, object]:
    reason = runtime_rejection(runtime) or case_rejection(case)
    if reason is not None:
        return {
            "name": case.name,
            "targetKind": case.target_kind,
            "phase": Phase.FAILED_VALIDATION.value if reason in {"MalformedProviderFixture", "MissingRuntimeImageHandoff"} else Phase.REJECTED.value,
            "reason": reason,
            "veleroObjects": [],
            "statusPatches": [{"phase": "Rejected", "reason": reason}],
            "auditEvents": ["BackupControllerRuntimeRejected"],
            "sloHooks": ["backup_runtime_rejected_total"],
        }
    return {
        "name": case.name,
        "targetKind": case.target_kind,
        "phase": Phase.SUCCEEDED.value,
        "states": list(STATES),
        "runtime": {"image": runtime.image, "entrypoint": runtime.entrypoint, "runtimeEnabled": runtime.runtime_enabled, "canaryScope": runtime.canary_scope},
        "promotion": {"from": "disabled", "to": "canary" if runtime.runtime_enabled else "disabled", "haReadyAfterSmoke": True},
        "idempotencyKeys": idempotency(case),
        "veleroObjects": velero(case),
        "statusPatches": status(case),
        "auditEvents": ["BackupControllerRuntimeObserved", "BackupControllerRuntimeVeleroCreated", "BackupControllerRuntimeStatusPatched", "BackupControllerRuntimeSloRecorded"],
        "sloHooks": list(SLO_HOOKS),
    }


def main() -> None:
    if len(argv) != 2:
        raise SystemExit("usage: production-backup-controller-runtime-image-seam.py <fixture.json>")
    raw = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    runtime = parse_runtime(raw.get("runtime", {}) if isinstance(raw, dict) else {})
    cases = [parse_case(item) for item in raw.get("cases", [])] if isinstance(raw, dict) else [parse_case(raw)]
    rendered = [render_case(runtime, item) for item in cases]
    payload = {
        "mode": "offline-disabled-runtime-image-seam",
        "runtime": {"image": runtime.image, "entrypoint": runtime.entrypoint, "runtimeEnabled": runtime.runtime_enabled, "canaryScope": runtime.canary_scope},
        "clusterAccess": {"mode": "offline", "commandsInvoked": [], "networkClients": [], "configFilesRead": []},
        "accepted": [item for item in rendered if item["veleroObjects"]],
        "rejected": [item for item in rendered if not item["veleroObjects"]],
    }
    print("RUNTIME_IMAGE_SEAM_JSON:" + json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
