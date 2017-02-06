from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from sys import argv
from typing import Final

type Json = str | int | bool | None | list["Json"] | dict[str, "Json"]

CANARY_SCOPE: Final = "provider-scheduler-quota-replay-canary"
SUPPORTED_KINDS: Final = ("VirtualMachineClaim", "KubernetesClusterClaim")
MARKERS: Final = (
    "provider_scheduler_quota_replay_fixture_parse_ok",
    "production_scheduler_quota_replay_seam_ok",
    "production_scheduler_quota_replay_fail_closed_ok",
    "production_scheduler_quota_replay_no_cluster_access_ok",
    "lab_overlay_no_scheduler_quota_replay_reference_ok",
)


@dataclass(frozen=True, slots=True)
class ReplayCase:
    name: str
    journal: dict[str, Json] | None
    reservation: dict[str, Json] | None
    quota: dict[str, Json] | None
    repair: dict[str, int]
    malformed: bool = False


def text(source: dict[str, Json], key: str) -> str | None:
    value = source.get(key)
    return value if isinstance(value, str) and value else None


def number(source: dict[str, Json], key: str) -> int | None:
    value = source.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def record(value: Json | None) -> dict[str, Json] | None:
    return value if isinstance(value, dict) else None


def malformed_case(name: str) -> ReplayCase:
    return ReplayCase(name, None, None, None, {}, True)


def parse_case(value: Json) -> ReplayCase:
    if not isinstance(value, dict):
        return malformed_case("malformed-quota-replay-case")
    name = text(value, "name") or "malformed-quota-replay-case"
    repair_raw = record(value.get("repair"))
    repair: dict[str, int] = {}
    if repair_raw is not None:
        for key, item in repair_raw.items():
            if isinstance(item, int) and not isinstance(item, bool):
                repair[key] = item
    return ReplayCase(name, record(value.get("admissionJournal")), record(value.get("capacityReservation")), record(value.get("projectQuota")), repair)


def load_cases(path: str) -> tuple[ReplayCase, ...]:
    raw: Json = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("canaryScope") != CANARY_SCOPE or not isinstance(raw.get("cases"), list):
        return (malformed_case("malformed-quota-replay-root"),)
    return tuple(parse_case(item) for item in raw["cases"])


def claim_ref(journal: dict[str, Json]) -> dict[str, Json] | None:
    ref = record(journal.get("claimRef"))
    if ref is None:
        return None
    required = (text(ref, "kind"), text(ref, "namespace"), text(ref, "name"), text(ref, "uid"), number(ref, "generation"))
    if None in required:
        return None
    return {"kind": required[0], "namespace": required[1], "name": required[2], "uid": required[3], "generation": required[4]}


def count_key(kind: str) -> str:
    return "vms" if kind == "VirtualMachineClaim" else "tenantClusters"


def fail(case: ReplayCase, reason: str) -> dict[str, Json]:
    ref = claim_ref(case.journal) if case.journal is not None else None
    return {
        "name": case.name,
        "quotaReplayEvent": {"kind": "QuotaReplayEvent", "decision": "FailClosed", "reason": reason, "claimRef": ref},
        "quotaRepairPlan": {"kind": "QuotaRepairPlan", "committedActions": [], "reason": reason},
        "reservationReplayDecision": {"kind": "ReservationReplayDecision", "allowed": False, "reason": reason},
        "statusPatch": {"phase": "Degraded", "admission": {"reason": reason, "observedGeneration": ref.get("generation") if ref else 0}},
    }


def validate(case: ReplayCase) -> str | None:
    if case.malformed:
        return "MalformedSchedulerQuotaReplay"
    if case.journal is None:
        return "MissingAdmissionJournal"
    if case.reservation is None:
        return "MissingCapacityReservation"
    if case.quota is None:
        return "MissingProjectQuota"
    ref = claim_ref(case.journal)
    if ref is None:
        return "MalformedAdmissionJournal"
    kind = text(ref, "kind")
    if kind not in SUPPORTED_KINDS:
        return "UnknownRequestKind"
    project = text(case.journal, "projectRef")
    if project is None or project != text(case.quota, "name") or project != text(case.reservation, "projectRef"):
        return "CrossProjectReplayAttempt"
    if text(case.journal, "decision") != "Admitted":
        return "JournalNotAccepted"
    if text(case.reservation, "phase") != "Active":
        return "ReservationNotActive"
    if ref.get("uid") != text(case.reservation, "claimUid"):
        return "ReservationClaimMismatch"
    if ref.get("generation") != number(case.reservation, "claimGeneration"):
        return "StaleReservationGeneration"
    duplicate = record(case.journal.get("duplicate"))
    if duplicate is not None and duplicate.get("decision") != case.journal.get("decision"):
        return "ConflictingDuplicateJournal"
    for key, value in case.repair.items():
        current = number(case.quota, key)
        if current is None or current + value < 0:
            return "QuotaUnderflowRepair"
        limit = number(case.quota, f"quota{key[0].upper()}{key[1:]}")
        if limit is not None and current + value > limit:
            return "QuotaOverflowRepair"
    return None


def accepted(case: ReplayCase) -> dict[str, Json]:
    assert case.journal is not None
    assert case.reservation is not None
    assert case.quota is not None
    ref = claim_ref(case.journal)
    assert ref is not None
    resources = record(case.reservation.get("resources")) or {}
    generation = number(case.reservation, "claimGeneration") or 0
    key = count_key(str(ref["kind"]))
    repair_actions = [{"field": field, "delta": delta, "after": (number(case.quota, field) or 0) + delta} for field, delta in sorted(case.repair.items())]
    return {
        "name": case.name,
        "quotaReplayEvent": {
            "kind": "QuotaReplayEvent",
            "decision": "Replayed",
            "idempotencyKey": f"{ref['uid']}:{generation}",
            "projectRef": case.journal["projectRef"],
            "claimRef": ref,
        },
        "quotaRepairPlan": {"kind": "QuotaRepairPlan", "committedActions": repair_actions, "quotaSnapshot": {key: number(case.quota, key) or 0}},
        "reservationReplayDecision": {
            "kind": "ReservationReplayDecision",
            "allowed": True,
            "capacityCell": case.reservation["capacityCell"],
            "resources": resources,
        },
        "statusPatch": {
            "phase": "Admitted",
            "admission": {
                "capacityCell": case.reservation["capacityCell"],
                "replayedFromJournal": case.journal["name"],
                "observedGeneration": generation,
            },
        },
    }


def render(case: ReplayCase) -> dict[str, Json]:
    reason = validate(case)
    return fail(case, reason) if reason else accepted(case)


def build_payload(cases: tuple[ReplayCase, ...]) -> dict[str, Json]:
    rendered = [render(case) for case in cases]
    return {
        "adapterMode": "disabled-by-default-scheduler-quota-replay-seam",
        "clusterAccess": {"commandsInvoked": [], "configFilesRead": [], "mode": "offline", "networkClients": []},
        "inputMode": "SchedulerQuotaReplay fixtures",
        "preflightGate": {"canaryScope": CANARY_SCOPE, "failClosed": True},
        "replayed": [item for item in rendered if item["reservationReplayDecision"]["allowed"] is True],
        "failClosed": [item for item in rendered if item["reservationReplayDecision"]["allowed"] is False],
    }


def main() -> None:
    if len(argv) != 2:
        raise SystemExit("usage: production-scheduler-quota-replay-seam.py <fixture.json>")
    print(f"QUOTA_REPLAY_JSON:{json.dumps(build_payload(load_cases(argv[1])), separators=(',', ':'), sort_keys=True)}")
    for marker in MARKERS:
        print(marker)


if __name__ == "__main__":
    main()
