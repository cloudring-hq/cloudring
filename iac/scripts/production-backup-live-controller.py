#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from sys import argv
from typing import Final

CANARY_SCOPE: Final = "provider-backup-runtime-canary"
IMAGE: Final = "registry.example.invalid/privatecloud/provider-backup-controller:REPLACE_WITH_VERSION"
STATES: Final = ("observed", "preflighted", "planned", "velero-objects-created", "status-patched", "audit-recorded", "slo-recorded", "completed")
TARGETS: Final = ("Volume", "Namespace", "KubernetesClusterClaim")


class Phase(StrEnum):
    SUCCEEDED = "Succeeded"
    REJECTED = "Rejected"
    FAILED_VALIDATION = "FailedValidation"


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


def parse_case(raw: object) -> Case:
    if not isinstance(raw, dict):
        return Case("malformed", "Volume", "tenant-a", "tenant-a", "", "", 0, False, False, missing_status=True)
    return Case(
        name=str(raw.get("name") or "unnamed"),
        target_kind=str(raw.get("targetKind") or "Volume"),
        project_ref=str(raw.get("projectRef") or ""),
        target_project_ref=str(raw.get("targetProjectRef") or ""),
        backup_uid=str(raw.get("backupUid") or ""),
        restore_uid=str(raw.get("restoreUid") or ""),
        generation=int(raw.get("generation") or 0),
        preflight=bool(raw.get("preflight")),
        immutable=bool(raw.get("immutable")),
        duplicate_key=bool(raw.get("duplicateKey")),
        missing_status=bool(raw.get("missingStatus")),
        missing_audit=bool(raw.get("missingAudit")),
        missing_slo=bool(raw.get("missingSlo")),
    )


def reject_reason(case: Case) -> str | None:
    if case.target_kind not in TARGETS:
        return "UnsupportedTargetKind"
    if not case.project_ref or not case.backup_uid or not case.restore_uid:
        return "MalformedProviderFixture"
    if not case.preflight:
        return "VeleroCreateBeforePreflightDenied"
    if not case.immutable:
        return "MutableStoragePolicyDenied"
    if case.project_ref != case.target_project_ref:
        return "CrossTenantRestoreDenied"
    if case.duplicate_key:
        return "DuplicateIdempotencyKeySuppressed"
    if case.missing_status:
        return "MissingStatusPatchDenied"
    if case.missing_audit:
        return "MissingAuditEventDenied"
    if case.missing_slo:
        return "MissingSloHookDenied"
    return None


def idempotency(case: Case) -> dict[str, str]:
    return {
        "backup": f"{case.backup_uid}:{case.generation}:{case.target_kind}:schedule",
        "restore": f"{case.restore_uid}:{case.generation}:{case.target_kind}:sourceBackup:targetNamespace",
    }


def velero(case: Case) -> list[dict[str, object]]:
    return [
        {"kind": "Schedule", "name": f"{case.name}-schedule"},
        {"kind": "Backup", "name": f"{case.name}-backup"},
        {"kind": "Restore", "name": f"{case.name}-restore"},
    ]


def status_patches(case: Case) -> list[dict[str, object]]:
    return [
        {
            "apiKind": "BackupPlan",
            "phase": "Protected",
            "lastRun": f"{case.name}-backup",
            "lastSuccess": f"{case.name}-backup",
            "conditions": [
                {"type": "PreflightReady", "status": "True", "reason": "ImmutableStorageVerified"},
                {"type": "VeleroScheduleReady", "status": "True", "reason": "ScheduleCreated"},
            ],
        },
        {
            "apiKind": "RestoreRequest",
            "phase": "Succeeded",
            "veleroRestoreName": f"{case.name}-restore",
            "conditions": [
                {"type": "TenantIsolationVerified", "status": "True", "reason": "SourceMatchesTargetProject"},
                {"type": "VeleroRestoreReady", "status": "True", "reason": "RestoreCreated"},
            ],
        },
    ]


def render_case(case: Case) -> dict[str, object]:
    reason = reject_reason(case)
    if reason is not None:
        return {
            "name": case.name,
            "targetKind": case.target_kind,
            "phase": Phase.REJECTED.value if reason != "MalformedProviderFixture" else Phase.FAILED_VALIDATION.value,
            "reason": reason,
            "veleroObjects": [],
            "statusPatches": [{"phase": "Rejected", "reason": reason}],
            "auditEvents": ["BackupLiveControllerRejected", "RestoreTenantIsolationRejected" if reason == "CrossTenantRestoreDenied" else "BackupLiveControllerRejected"],
            "sloHooks": ["backup_runtime_rejected_total"],
        }
    return {
        "name": case.name,
        "targetKind": case.target_kind,
        "phase": Phase.SUCCEEDED.value,
        "states": list(STATES),
        "idempotencyKeys": idempotency(case),
        "veleroObjects": velero(case),
        "statusPatches": status_patches(case),
        "auditEvents": ["BackupLiveControllerObserved", "BackupLiveControllerPreflightPassed", "BackupLiveControllerVeleroCreated", "BackupLiveControllerStatusPatched"],
        "sloHooks": ["backup_runtime_reconcile_duration_seconds", "backup_runtime_velero_create_total", "backup_runtime_idempotency_replay_total", "backup_runtime_status_patch_total", "backup_runtime_audit_event_total"],
    }


def main() -> None:
    if len(argv) != 2:
        raise SystemExit("usage: production-backup-live-controller.py <fixture.json>")
    raw = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    cases = [parse_case(item) for item in raw.get("cases", [])] if isinstance(raw, dict) else [parse_case(raw)]
    rendered = [render_case(item) for item in cases]
    payload = {
        "mode": "offline-disabled-live-controller-contract",
        "runtime": {"image": IMAGE, "runtimeEnabled": False, "canaryScope": CANARY_SCOPE},
        "clusterAccess": {"mode": "offline", "commandsInvoked": [], "networkClients": [], "configFilesRead": []},
        "accepted": [item for item in rendered if item["veleroObjects"]],
        "rejected": [item for item in rendered if not item["veleroObjects"]],
    }
    print("LIVE_CONTROLLER_JSON:" + json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
