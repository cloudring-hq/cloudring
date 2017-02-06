from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from sys import argv
from typing import Final, assert_never

type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

CANARY_SCOPE: Final = "provider-scheduler-runtime-canary"
SUPPORTED_KINDS: Final = ("VirtualMachineClaim", "KubernetesClusterClaim")
PIPELINE: Final = ("Filter", "Score", "Reserve", "Permit")
MARKERS: Final = ("provider_scheduler_fixture_parse_ok", "production_scheduler_runtime_admission_seam_ok", "production_scheduler_runtime_fail_closed_ok", "production_scheduler_runtime_no_cluster_access_ok", "lab_overlay_no_scheduler_runtime_reference_ok")


class Phase(StrEnum):
    ADMITTED = "Admitted"
    REJECTED = "Rejected"
    DEGRADED = "Degraded"


@dataclass(frozen=True, slots=True)
class SchedulerRequest:
    kind: str
    namespace: str
    name: str
    uid: str
    generation: int
    project: str
    service_class: str
    cpu: int
    memory: int
    replicas: int
    capacity_cell: str | None
    domains: dict[str, str]


@dataclass(frozen=True, slots=True)
class ServiceClass:
    name: str
    kind: str
    min_replicas: int
    max_replicas: int


@dataclass(frozen=True, slots=True)
class CapacityCell:
    name: str
    phase: str
    stale: bool
    scheduling_disabled: bool
    available_cpu: int
    available_memory: int
    reserved_claims: int
    domains: dict[str, str]
    service_classes: tuple[ServiceClass, ...]


@dataclass(frozen=True, slots=True)
class ProjectQuota:
    name: str
    quota_cpu: int
    quota_memory: int
    quota_vms: int
    quota_clusters: int
    used_cpu: int
    used_memory: int
    used_vms: int
    used_clusters: int
    allowed_kinds: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReconcileCase:
    name: str
    request: SchedulerRequest
    cells: tuple[CapacityCell, ...]
    project: ProjectQuota
    locks: dict[str, bool]
    parse_error: bool = False


@dataclass(frozen=True, slots=True)
class Rejection:
    phase: Phase
    reason: str


def text(source: dict[str, object], key: str) -> str | None:
    return source.get(key) if isinstance(source.get(key), str) and len(source.get(key)) > 0 else None


def number(source: dict[str, object], key: str) -> int | None:
    value = source.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def flag(source: dict[str, object], key: str) -> bool:
    return source.get(key) if isinstance(source.get(key), bool) else False


def domains(source: object) -> dict[str, str]:
    return {str(key): item for key, item in source.items() if isinstance(item, str)} if isinstance(source, dict) else {}


def strings(value: object) -> tuple[str, ...]:
    return tuple(item for item in value if isinstance(item, str) and len(item) > 0) if isinstance(value, list) else ()


def malformed_case(name: str) -> ReconcileCase:
    request = SchedulerRequest("VirtualMachineClaim", "tenant-a", name, name, 1, "tenant-a", "small-vm", 0, 0, 1, None, {})
    project = ProjectQuota("tenant-a", 0, 0, 0, 0, 0, 0, 0, 0, SUPPORTED_KINDS)
    return ReconcileCase(name, request, (), project, {}, True)


def parse_request(source: object) -> SchedulerRequest | None:
    if not isinstance(source, dict) or source.get("kind") != "SchedulerAdmissionReview":
        return None
    spec = source.get("spec")
    if not isinstance(spec, dict):
        return None
    needed = (text(spec, "requestKind"), text(spec, "namespace"), text(spec, "name"), text(spec, "uid"), number(spec, "generation"), text(spec, "projectRef"), text(spec, "serviceClass"), number(spec, "cpuMillicores"), number(spec, "memoryMi"))
    if None in needed:
        return None
    return SchedulerRequest(needed[0], needed[1], needed[2], needed[3], needed[4], needed[5], needed[6], needed[7], needed[8], number(spec, "controlPlaneReplicas") or 1, text(spec, "capacityCell"), domains(spec.get("failureDomains")))


def parse_service_class(source: object) -> ServiceClass | None:
    if not isinstance(source, dict):
        return None
    min_replicas = number(source, "minControlPlaneReplicas") or 1
    max_replicas = number(source, "maxControlPlaneReplicas") or 99
    needed = (text(source, "name"), text(source, "kind"))
    return None if None in needed else ServiceClass(needed[0], needed[1], min_replicas, max_replicas)


def parse_cell(source: object) -> CapacityCell | None:
    if not isinstance(source, dict):
        return None
    classes = tuple(item for item in (parse_service_class(row) for row in source.get("serviceClasses", [])) if item is not None)
    needed = (text(source, "name"), text(source, "phase"), number(source, "availableCpuMillicores"), number(source, "availableMemoryMi"))
    return None if None in needed else CapacityCell(needed[0], needed[1], flag(source, "stale"), flag(source, "schedulingDisabled"), needed[2], needed[3], number(source, "reservedClaims") or 0, domains(source.get("failureDomains")), classes)


def parse_project(source: object) -> ProjectQuota | None:
    if not isinstance(source, dict):
        return None
    needed = (text(source, "name"), number(source, "quotaCpuMillicores"), number(source, "quotaMemoryMi"), number(source, "quotaVMs"), number(source, "quotaTenantClusters"))
    return None if None in needed else ProjectQuota(needed[0], needed[1], needed[2], needed[3], needed[4], number(source, "usedCpuMillicores") or 0, number(source, "usedMemoryMi") or 0, number(source, "usedVMs") or 0, number(source, "usedTenantClusters") or 0, strings(source.get("allowedKinds")))


def parse_case(source: object) -> ReconcileCase:
    if not isinstance(source, dict):
        return malformed_case("malformed-scheduler-fixture")
    name = text(source, "name") or "malformed-scheduler-fixture"
    request, project = parse_request(source.get("review")), parse_project(source.get("project"))
    cells = tuple(item for item in (parse_cell(row) for row in source.get("cells", [])) if item is not None)
    if request is None or project is None:
        return malformed_case(name)
    locks = source.get("locks")
    return ReconcileCase(name, request, cells, project, {"projectQuota": flag(locks, "projectQuota") if isinstance(locks, dict) else False, "capacity": flag(locks, "capacity") if isinstance(locks, dict) else False})


def load_cases(path: str) -> tuple[ReconcileCase, ...]:
    raw: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("canaryScope") != CANARY_SCOPE or not isinstance(raw.get("cases"), list):
        return (malformed_case("malformed-scheduler-fixture-root"),)
    return tuple(parse_case(item) for item in raw["cases"])


def count_key(kind: str) -> str:
    match kind:
        case "VirtualMachineClaim":
            return "vms"
        case "KubernetesClusterClaim":
            return "tenantClusters"
        case _:
            return "unsupported"


def service_for(cell: CapacityCell, request: SchedulerRequest) -> ServiceClass | None:
    matches = [item for item in cell.service_classes if item.kind == request.kind and item.name == request.service_class]
    return matches[0] if matches else None


def domain_match(cell: CapacityCell, request: SchedulerRequest) -> bool:
    return all(cell.domains.get(key) == value for key, value in request.domains.items())


def reject(case: ReconcileCase) -> Rejection | None:
    request, project = case.request, case.project
    if case.parse_error:
        return Rejection(Phase.REJECTED, "MalformedSchedulerFixture")
    if request.kind not in SUPPORTED_KINDS:
        return Rejection(Phase.REJECTED, "UnsupportedRequestKind")
    if request.kind not in project.allowed_kinds:
        return Rejection(Phase.REJECTED, "TenantPolicyDenied")
    if not case.locks.get("projectQuota") or not case.locks.get("capacity"):
        return Rejection(Phase.DEGRADED, "ReservationLockUnavailable")
    if quota_exceeded(request, project):
        return Rejection(Phase.REJECTED, "ProjectQuotaExceeded")
    cell, service, reason = select_cell(case)
    if cell is None or service is None:
        return Rejection(Phase.DEGRADED if reason == "StaleCapacitySnapshot" else Phase.REJECTED, reason)
    if request.kind == "KubernetesClusterClaim" and not service.min_replicas <= request.replicas <= service.max_replicas:
        return Rejection(Phase.REJECTED, "TenantPolicyDenied")
    return None


def quota_exceeded(request: SchedulerRequest, project: ProjectQuota) -> bool:
    if request.cpu + project.used_cpu > project.quota_cpu or request.memory + project.used_memory > project.quota_memory:
        return True
    return (project.used_vms + 1 > project.quota_vms) if count_key(request.kind) == "vms" else (project.used_clusters + 1 > project.quota_clusters)


def select_cell(case: ReconcileCase) -> tuple[CapacityCell | None, ServiceClass | None, str]:
    feasible: list[tuple[CapacityCell, ServiceClass]] = []
    requested_exists = False
    stale_seen = False
    for cell in case.cells:
        if case.request.capacity_cell and cell.name != case.request.capacity_cell:
            continue
        requested_exists = True
        service = service_for(cell, case.request)
        if service is None or not domain_match(cell, case.request):
            continue
        if cell.stale:
            stale_seen = True
            continue
        if cell.phase != "Ready" or cell.scheduling_disabled:
            continue
        if cell.available_cpu >= case.request.cpu and cell.available_memory >= case.request.memory:
            feasible.append((cell, service))
    if feasible:
        return (*max(feasible, key=lambda item: (item[0].available_cpu, item[0].available_memory, -item[0].reserved_claims, item[0].name)), "Admitted")
    if case.request.capacity_cell and not requested_exists:
        return None, None, "CapacityCellNotFound"
    return None, None, "StaleCapacitySnapshot" if stale_seen else "InsufficientCapacity"


def accepted_case(case: ReconcileCase) -> JsonValue:
    cell, service, _ = select_cell(case)
    assert cell is not None and service is not None
    request = case.request
    key = f"{request.uid}:{request.generation}"
    resources = {"cpuMillicores": request.cpu, "memoryMi": request.memory}
    count = case.project.used_vms if count_key(request.kind) == "vms" else case.project.used_clusters
    return {
        "name": case.name,
        "requestKind": request.kind,
        "pipeline": list(PIPELINE),
        "reservationIntents": [{"kind": "ReservationIntent", "name": f"{request.kind.lower()}-{request.namespace}-{request.name}", "claimRef": claim_ref(request), "capacityCell": cell.name, "serviceClass": service.name, "resources": resources, "idempotencyKey": key}],
        "quotaAdmissionDecision": {"kind": "QuotaAdmissionDecision", "projectRef": request.project, "allowed": True, "quotaSnapshot": {"cpuMillicores": case.project.used_cpu + request.cpu, "memoryMi": case.project.used_memory + request.memory, count_key(request.kind): count + 1}},
        "admissionJournal": journal(case, Rejection(Phase.ADMITTED, "CapacityAccepted"), cell.name),
        "statusPatch": {"phase": "Admitted", "admission": {"capacityCell": cell.name, "serviceClass": service.name, "estimatedResources": resources, "observedGeneration": request.generation}},
    }


def rejected_case(case: ReconcileCase, rejection: Rejection) -> JsonValue:
    cell, _, _ = select_cell(case)
    return {"name": case.name, "requestKind": case.request.kind, "reservationIntents": [], "quotaAdmissionDecision": {"kind": "QuotaAdmissionDecision", "projectRef": case.request.project, "allowed": False, "reason": rejection.reason}, "admissionJournal": journal(case, rejection, cell.name if cell else None), "statusPatch": {"phase": rejection.phase.value, "admission": {"reason": rejection.reason, "observedGeneration": case.request.generation}}}


def claim_ref(request: SchedulerRequest) -> JsonValue:
    return {"kind": request.kind, "namespace": request.namespace, "name": request.name, "uid": request.uid, "generation": request.generation}


def journal(case: ReconcileCase, rejection: Rejection, cell: str | None) -> JsonValue:
    return {"kind": "AdmissionJournal", "decision": rejection.phase.value, "reason": rejection.reason, "claimRef": claim_ref(case.request), "capacityCell": cell, "pipeline": list(PIPELINE)}


def case_json(case: ReconcileCase) -> JsonValue:
    rejection = reject(case)
    match rejection:
        case None:
            return accepted_case(case)
        case Rejection():
            return rejected_case(case, rejection)
        case unreachable:
            assert_never(unreachable)


def build_payload(cases: tuple[ReconcileCase, ...]) -> JsonValue:
    rendered = [case_json(item) for item in cases]
    return {
        "adapterMode": "disabled-by-default-scheduler-admission-seam",
        "clusterAccess": {"commandsInvoked": [], "configFilesRead": [], "mode": "offline", "networkClients": []},
        "accepted": [item for item in rendered if len(item["reservationIntents"]) > 0],
        "failClosed": [item for item in rendered if len(item["reservationIntents"]) == 0],
        "inputMode": "json-fixtures",
        "preflightGate": {"canaryScope": CANARY_SCOPE, "failClosed": True},
    }


def main() -> None:
    if len(argv) != 2:
        raise SystemExit("usage: production-scheduler-runtime-admission-seam.py <fixture.json>")
    print(f"ADMISSION_JSON:{json.dumps(build_payload(load_cases(argv[1])), separators=(',', ':'), sort_keys=True)}")
    for marker in MARKERS:
        print(marker)


if __name__ == "__main__":
    main()
