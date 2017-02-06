#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# --- How to run ---
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run directly (no venv, no pip install needed):
#      uv run simulate-production-backup-runtime-canary.py
# 3. Or run with the bundled interpreter:
#      python simulate-production-backup-runtime-canary.py
# ------------------

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum, unique
from typing import Final, NewType, assert_never

Name = NewType("Name", str)
Tenant = NewType("Tenant", str)
type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

CANARY_SCOPE: Final = "provider-backup-runtime-canary"
VELO_NAMESPACE: Final = "velero"
MARKERS: Final = (
    "velero_backup_actions_ok",
    "velero_restore_actions_ok",
    "fail_closed_boundary_ok",
    "no_cluster_access_ok",
    "production_backup_runtime_canary_simulation_ok",
)


@unique
class TargetKind(StrEnum):
    VOLUME = "Volume"
    NAMESPACE = "Namespace"
    TENANT_CLUSTER = "KubernetesClusterClaim"


@unique
class VeleroKind(StrEnum):
    SCHEDULE = "Schedule"
    BACKUP = "Backup"
    RESTORE = "Restore"


@unique
class StatusPhase(StrEnum):
    PROTECTED = "Protected"
    SUCCEEDED = "Succeeded"
    REJECTED = "Rejected"
    DEGRADED = "Degraded"


@dataclass(frozen=True, slots=True)
class Preflight:
    backup_storage_location: str
    volume_snapshot_location: str
    backup_repository: str
    volume_snapshot_class: str
    canary_scope: str


@dataclass(frozen=True, slots=True)
class HappyScenario:
    target_kind: TargetKind
    backup_plan: Name
    restore_request: Name
    source_tenant: Tenant
    restore_tenant: Tenant


@dataclass(frozen=True, slots=True)
class FailClosedScenario:
    name: str
    target_kind: TargetKind
    phase: StatusPhase
    reason: str


def resources_for(kind: TargetKind) -> tuple[str, ...]:
    match kind:
        case TargetKind.VOLUME:
            return (
                "persistentvolumeclaims",
                "persistentvolumes",
                "volumesnapshots.snapshot.storage.k8s.io",
                "volumes.platform.privatecloud.local",
            )
        case TargetKind.NAMESPACE:
            return ("namespaces", "networkpolicies.networking.k8s.io", "resourcequotas", "limitranges")
        case TargetKind.TENANT_CLUSTER:
            return (
                "kubernetesclusterclaims.platform.privatecloud.local",
                "clusters.cluster.x-k8s.io",
                "machines.cluster.x-k8s.io",
                "kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
                "kubevirtclusters.infrastructure.cluster.x-k8s.io",
                "secrets",
                "services",
                "networkpolicies.networking.k8s.io",
            )
        case unreachable:
            assert_never(unreachable)


def restore_namespaces(kind: TargetKind, tenant: Tenant) -> tuple[str, ...]:
    match kind:
        case TargetKind.VOLUME | TargetKind.NAMESPACE:
            return (str(tenant),)
        case TargetKind.TENANT_CLUSTER:
            return (str(tenant), "capk-system")
        case unreachable:
            assert_never(unreachable)


def action_metadata(
    kind: VeleroKind,
    scenario: HappyScenario,
) -> tuple[Name, tuple[str, ...], tuple[tuple[str, str], ...]]:
    match kind:
        case VeleroKind.SCHEDULE:
            return (Name(f"{scenario.backup_plan}-schedule"), (str(scenario.source_tenant),), ())
        case VeleroKind.BACKUP:
            return (Name(f"{scenario.backup_plan}-canary-001"), (str(scenario.source_tenant),), ())
        case VeleroKind.RESTORE:
            return (
                Name(f"{scenario.restore_request}-restore"),
                restore_namespaces(scenario.target_kind, scenario.source_tenant),
                ((str(scenario.source_tenant), str(scenario.restore_tenant)),),
            )
        case unreachable:
            assert_never(unreachable)


def velero_action(kind: VeleroKind, scenario: HappyScenario, preflight: Preflight) -> JsonValue:
    name, namespaces, namespace_mapping = action_metadata(kind, scenario)
    return {
        "includedNamespaces": list(namespaces),
        "includedResources": list(resources_for(scenario.target_kind)),
        "kind": kind.value,
        "name": str(name),
        "namespace": VELO_NAMESPACE,
        "namespaceMapping": [{"from": source, "to": target} for source, target in namespace_mapping],
        "snapshotLocation": preflight.volume_snapshot_location,
        "storageLocation": preflight.backup_storage_location,
        "targetKind": scenario.target_kind.value,
    }


def backup_plan_status(scenario: HappyScenario) -> JsonValue:
    return {
        "apiKind": "BackupPlan",
        "name": str(scenario.backup_plan),
        "namespace": str(scenario.source_tenant),
        "phase": StatusPhase.PROTECTED.value,
        "reason": "VeleroBackupCompleted",
        "targetKind": scenario.target_kind.value,
    }


def restore_request_status(scenario: HappyScenario) -> JsonValue:
    return {
        "apiKind": "RestoreRequest",
        "name": str(scenario.restore_request),
        "namespace": str(scenario.source_tenant),
        "phase": StatusPhase.SUCCEEDED.value,
        "reason": "VeleroRestoreCompleted",
        "targetKind": scenario.target_kind.value,
    }


def fail_closed_status(scenario: FailClosedScenario) -> JsonValue:
    return {
        "apiKind": "RestoreRequest",
        "name": f"{scenario.name}-restore",
        "namespace": "tenant-a",
        "phase": scenario.phase.value,
        "reason": scenario.reason,
        "targetKind": scenario.target_kind.value,
    }


def happy_to_json(scenario: HappyScenario, preflight: Preflight) -> JsonValue:
    return {
        "backupPlan": str(scenario.backup_plan),
        "restoreRequest": str(scenario.restore_request),
        "statusActions": [backup_plan_status(scenario), restore_request_status(scenario)],
        "targetKind": scenario.target_kind.value,
        "veleroActions": [velero_action(kind, scenario, preflight) for kind in VeleroKind],
    }


def fail_closed_to_json(scenario: FailClosedScenario) -> JsonValue:
    return {
        "name": scenario.name,
        "statusActions": [fail_closed_status(scenario)],
        "targetKind": scenario.target_kind.value,
        "veleroActions": [],
    }


def happy_scenarios() -> tuple[HappyScenario, ...]:
    return (
        HappyScenario(TargetKind.VOLUME, Name("canary-volume-hourly"), Name("canary-volume-copy-restore"), Tenant("tenant-a"), Tenant("tenant-a-restore-volume")),
        HappyScenario(TargetKind.NAMESPACE, Name("canary-namespace-daily"), Name("canary-namespace-copy-restore"), Tenant("tenant-a"), Tenant("tenant-a-restore-namespace")),
        HappyScenario(TargetKind.TENANT_CLUSTER, Name("canary-tenant-cluster-daily"), Name("canary-tenant-cluster-copy-restore"), Tenant("tenant-a"), Tenant("tenant-a-restore-cluster")),
    )


def fail_closed_scenarios() -> tuple[FailClosedScenario, ...]:
    return (
        FailClosedScenario("missing-malformed-preflight", TargetKind.VOLUME, StatusPhase.DEGRADED, "PreflightUnavailableOrMalformed"),
        FailClosedScenario("cross-tenant-restore", TargetKind.VOLUME, StatusPhase.REJECTED, "CrossTenantRestoreDenied"),
        FailClosedScenario("missing-restore-safety-controls", TargetKind.NAMESPACE, StatusPhase.REJECTED, "NamespaceMappingResourcePolicyOrModifierMissing"),
        FailClosedScenario("target-collision", TargetKind.VOLUME, StatusPhase.REJECTED, "TargetCollision"),
        FailClosedScenario("unapproved-in-place-namespace-restore", TargetKind.NAMESPACE, StatusPhase.REJECTED, "InPlaceNamespaceRestoreApprovalMissing"),
        FailClosedScenario("unapproved-in-place-tenant-cluster-restore", TargetKind.TENANT_CLUSTER, StatusPhase.REJECTED, "InPlaceTenantClusterRestoreApprovalMissing"),
    )


def preflight_to_json(preflight: Preflight) -> JsonValue:
    return {
        "backupRepository": preflight.backup_repository,
        "backupStorageLocation": preflight.backup_storage_location,
        "canaryScope": preflight.canary_scope,
        "volumeSnapshotClass": preflight.volume_snapshot_class,
        "volumeSnapshotLocation": preflight.volume_snapshot_location,
    }


def build_payload() -> JsonValue:
    preflight = Preflight("primary-offsite", "primary-csi", "tenant-a-primary-offsite", "provider-production-csi-retain", CANARY_SCOPE)
    return {
        "apiBoundary": {
            "backupPlanTargets": ["VirtualMachineClaim", "Volume", "Namespace", "KubernetesClusterClaim"],
            "restoreRequestLiveTarget": "VirtualMachineClaim",
            "runtimeSupport": "offline-contract-simulation-only",
        },
        "clusterAccess": {"commandsInvoked": [], "mode": "offline", "networkClients": [], "readConfig": False},
        "failClosed": [fail_closed_to_json(scenario) for scenario in fail_closed_scenarios()],
        "happyPath": [happy_to_json(scenario, preflight) for scenario in happy_scenarios()],
        "preflight": preflight_to_json(preflight),
    }


def main() -> None:
    payload = build_payload()
    print(f"SIMULATION_JSON:{json.dumps(payload, separators=(',', ':'), sort_keys=True)}")
    for marker in MARKERS:
        print(marker)


if __name__ == "__main__":
    main()
