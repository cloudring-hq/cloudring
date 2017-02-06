#!/usr/bin/env python3
"""Append derived follow-up controls for archive residual queues.

This pass reads only the archive-residual metadata run. It does not open source
archives, extract payloads, copy archive names, copy member names, copy payload
text, or store domains, provider names, people, brands, vendors, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_legacy_mail_knowledge as common


CONTROL_REQUIREMENTS = {
    "raw_payload_text_exclusion": "exclude archive payload text from stored context and training payloads",
    "raw_member_name_exclusion": "exclude raw member names from parser and repair follow-up output",
    "archive_name_path_exclusion": "exclude raw archive names and source paths from agent context",
    "member_composition_only": "preserve only extension, kind, count, size, and status buckets",
    "parser_capability_vetting": "vet specialized archive parsers before using them on unsupported formats",
    "sandboxed_parser_execution": "run parser and repair work in a bounded sandbox with no payload export",
    "no_payload_extraction_to_disk": "avoid extracting archive payloads to disk during capability checks",
    "nested_container_boundary": "treat nested archive members as separate trust boundaries",
    "partial_listing_confidence_guard": "treat partial repair listings as incomplete evidence until verified",
    "repair_completion_gate": "require repair completion checks before declaring member coverage complete",
    "unsupported_format_customer_guidance": "surface customer-facing guidance for unsupported or damaged containers",
    "tool_failure_observability": "retain tool-exit and stderr buckets for support diagnostics",
    "integrity_traceability": "preserve stable ids and integrity hashes without copying payload data",
    "retention_minimization": "retain only the smallest useful parser and repair evidence",
    "training_payload_review_gate": "require a separate review before any derived summary becomes model-training material",
    "sensitive_archive_route": "route sensitive archive records through secret-aware handling before deeper processing",
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def counter_from_rows(rows: list[dict], field: str) -> collections.Counter[str]:
    counter: collections.Counter[str] = collections.Counter()
    for row in rows:
        value = row.get(field)
        if isinstance(value, list):
            counter.update(str(item) for item in value)
        elif isinstance(value, dict):
            counter.update({str(key): int(count) for key, count in value.items()})
        elif value not in (None, ""):
            counter[str(value)] += 1
    return counter


def followup_status(row: dict) -> str:
    status = str(row.get("residual_status") or "")
    target_type = str(row.get("target_type") or "")
    if status == "direct_format_parser_unavailable":
        return "direct_archive_parser_capability_requirements_modeled"
    if status == "nested_format_parser_unavailable":
        return "nested_archive_parser_capability_requirements_modeled"
    if status == "direct_zip_partial_listing_added":
        return "direct_zip_repair_completion_requirements_modeled"
    if status == "nested_zip_repair_probe_unlisted":
        return "nested_zip_repair_completion_requirements_modeled"
    if target_type == "nested_archive_member":
        return "nested_archive_followup_requirements_modeled"
    return "direct_archive_followup_requirements_modeled"


def followup_route(status: str) -> str:
    if status == "direct_archive_parser_capability_requirements_modeled":
        return "direct_parser_capability_gate"
    if status == "nested_archive_parser_capability_requirements_modeled":
        return "nested_parser_capability_gate"
    if status == "direct_zip_repair_completion_requirements_modeled":
        return "direct_zip_repair_completion_gate"
    if status == "nested_zip_repair_completion_requirements_modeled":
        return "nested_zip_repair_completion_gate"
    if status.startswith("nested_"):
        return "nested_archive_followup_gate"
    return "direct_archive_followup_gate"


def followup_readiness(status: str) -> str:
    if "parser_capability" in status:
        return "parser_needed_before_member_coverage"
    if "repair_completion" in status:
        return "repair_required_before_complete_member_coverage"
    return "followup_required_before_member_coverage"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "raw_payload_text_exclusion",
        "raw_member_name_exclusion",
        "archive_name_path_exclusion",
        "member_composition_only",
        "sandboxed_parser_execution",
        "no_payload_extraction_to_disk",
        "tool_failure_observability",
        "integrity_traceability",
        "retention_minimization",
        "training_payload_review_gate",
    }
    if "parser_capability" in status:
        controls.update({"parser_capability_vetting", "unsupported_format_customer_guidance"})
    if "repair_completion" in status:
        controls.update({"repair_completion_gate", "partial_listing_confidence_guard"})
    if str(row.get("target_type") or "") == "nested_archive_member" or status.startswith("nested_"):
        controls.add("nested_container_boundary")
    if int(row.get("member_count_observed") or 0) > 0 or row.get("members_written"):
        controls.add("partial_listing_confidence_guard")
    if row.get("sensitive_flags"):
        controls.add("sensitive_archive_route")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if row.get("sensitive_flags"):
        return "sensitive_archive_followup_risk"
    if status == "direct_archive_parser_capability_requirements_modeled":
        return "direct_unsupported_archive_parser_risk"
    if status == "nested_archive_parser_capability_requirements_modeled":
        return "nested_unsupported_archive_parser_risk"
    if status == "direct_zip_repair_completion_requirements_modeled":
        return "direct_damaged_archive_repair_risk"
    if status == "nested_zip_repair_completion_requirements_modeled":
        return "nested_damaged_archive_repair_risk"
    return "archive_followup_risk"


def followup_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    residual_status = str(row.get("residual_status") or "unknown")
    tags = [
        "archive_residual_followup_reviewed",
        "derived_from_residual_metadata_only",
        "not_training_payload",
        f"archive_followup_status_{status}",
        f"archive_followup_readiness_{followup_readiness(status)}",
        f"archive_followup_route_{route}",
        f"risk_{risk}",
        f"extension_{row.get('extension', 'unknown')}",
        f"target_{row.get('target_type', 'unknown')}",
        f"residual_status_{residual_status}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("archive_residual_tags") or []:
        if source_tag in {
            "external_parser_capability_missing",
            "partial_repair_inventory_added",
            "repair_probe_retained_without_members",
            "member_composition_added",
            "target_direct_unlisted_archive",
            "target_nested_archive_member",
        }:
            tags.append(f"source_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        status = followup_status(row)
        route = followup_route(status)
        controls = required_controls(row, status)
        risk = risk_bucket(row, status)
        signals.append(
            {
                "archive_residual_followup_signal_id": "archivefollowup-" + common.stable_hash(row["archive_residual_signal_id"]),
                "case_id": "",
                "source_archive_residual_signal_id": row["archive_residual_signal_id"],
                "source_archive_backlog_signal_id": row.get("source_archive_backlog_signal_id", ""),
                "archive_id": row.get("archive_id", ""),
                "outer_archive_id": row.get("outer_archive_id", ""),
                "source_nested_member_id": row.get("source_nested_member_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "target_type": row.get("target_type", "unknown"),
                "prior_backlog_status": row.get("prior_backlog_status", "unknown"),
                "residual_status": row.get("residual_status", "unknown"),
                "listing_confidence": row.get("listing_confidence", "unknown"),
                "listing_truncated": bool(row.get("listing_truncated", False)),
                "member_count_observed": int(row.get("member_count_observed") or 0),
                "member_kind_counts": row.get("member_kind_counts", {}),
                "member_extension_counts": row.get("member_extension_counts", {}),
                "members_written": int(row.get("members_written") or 0),
                "tool_family": row.get("tool_family", "unknown"),
                "tool_exit_bucket": row.get("tool_exit_bucket", "unknown"),
                "tool_stderr_bucket": row.get("tool_stderr_bucket", "unknown"),
                "archive_followup_status": status,
                "archive_followup_readiness": followup_readiness(status),
                "archive_followup_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "archive_residual_followup_tags": followup_tags(row, status, route, controls, risk),
                "sensitive_flags": row.get("sensitive_flags", []),
                "sensitive_route": bool(row.get("sensitive_flags")),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['archive_followup_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["archive_followup_status"] for row in rows)
        readiness_counter = collections.Counter(row["archive_followup_readiness"] for row in rows)
        route_counter = collections.Counter(row["archive_followup_route"] for row in rows)
        target_counter = collections.Counter(row["target_type"] for row in rows)
        extension_counter = collections.Counter(row["extension"] for row in rows)
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["archive_residual_followup_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "archive_residual_followup_modeled"
        implications = [
            "Treat archive residual records as explicit parser and repair work, not as missing context.",
            "Future parser work must preserve composition-only output unless a separate safe content path is proven.",
        ]
        if control_counter.get("parser_capability_vetting", 0):
            implications.append("Unsupported archive formats need vetted parser capability and support diagnostics before member coverage can improve.")
        if control_counter.get("repair_completion_gate", 0):
            implications.append("Damaged containers with partial listings need repair-completion checks before coverage is marked complete.")
        if control_counter.get("nested_container_boundary", 0):
            implications.append("Nested containers need separate trust boundaries and no payload extraction to disk.")
        if control_counter.get("sensitive_archive_route", 0):
            implications.append("Sensitive archive records need secret-aware handling before deeper parser work.")
        case = {
            "case_id": "archivefollowupcase-" + common.stable_hash(key),
            "case_type": "archive_residual_followup_handling_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
            "target_type_counts": dict(target_counter.most_common()),
            "extension_counts": dict(extension_counter.most_common()),
            "archive_followup_status_counts": dict(status_counter.most_common()),
            "archive_followup_readiness_counts": dict(readiness_counter.most_common()),
            "archive_followup_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "archive_residual_followup_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_archive_residual_followup_signal_ids": [row["archive_residual_followup_signal_id"] for row in rows[:50]],
            "evidence_archive_residual_followup_signal_id_count": len(rows),
            "summary": (
                f"An archive residual follow-up cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for parser-capability, repair-completion, nested-boundary, and support diagnostics "
                "without copying archive payloads or member names."
            ),
        }
        cases.append(case)
        for row in rows:
            row["case_id"] = case["case_id"]
    return cases


def build_control_rows(signals: list[dict]) -> list[dict]:
    by_control: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        for control in signal["required_controls"]:
            by_control[control].append(signal)
    controls: list[dict] = []
    for control, rows in sorted(by_control.items()):
        status_counter = collections.Counter(row["archive_followup_status"] for row in rows)
        route_counter = collections.Counter(row["archive_followup_route"] for row in rows)
        controls.append(
            {
                "archive_residual_followup_control_id": "archivefollowupcontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
                "archive_followup_status_counts": dict(status_counter.most_common()),
                "archive_followup_route_counts": dict(route_counter.most_common()),
                "evidence_archive_residual_followup_signal_ids": [row["archive_residual_followup_signal_id"] for row in rows[:50]],
                "agent_use": "Use as an archive parser/repair checkpoint, not as archive payload content.",
            }
        )
    return controls


def markdown_counter(counter: collections.Counter[str], label: str) -> str:
    if not counter:
        return "_No rows._"
    lines = [f"| {label} | count |", "| --- | ---: |"]
    for key, count in counter.most_common():
        lines.append(f"| `{key}` | {count} |")
    return "\n".join(lines)


def write_coverage(run_dir: Path, manifest: dict, signals: list[dict]) -> None:
    status_counts = counter_from_rows(signals, "archive_followup_status")
    route_counts = counter_from_rows(signals, "archive_followup_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Archive Residual Followup Coverage

- Source kind: directory archive residual followup batch
- Source archive residual run: `{manifest["source_archive_residual_run"]}`
- Source residual signals: {manifest["source_signal_count"]}
- Followup signals written: {manifest["signals_written"]}
- Followup cases: {manifest["archive_residual_followup_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Direct parser capability routes: {manifest["direct_parser_capability_route_count"]}
- Nested parser capability routes: {manifest["nested_parser_capability_route_count"]}
- Direct repair completion routes: {manifest["direct_repair_completion_route_count"]}
- Nested repair completion routes: {manifest["nested_repair_completion_route_count"]}
- Sensitive followup routes: {manifest["sensitive_followup_route_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Followup Status Counts

{markdown_counter(status_counts, "archive_followup_status")}

## Followup Route Counts

{markdown_counter(route_counts, "archive_followup_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over archive residual metadata records.
- It does not open source archives, extract payloads, or copy archive names,
  member names, payload text, paths, domains, providers, people, brands,
  vendors, or secrets.
- Use these records for parser and repair planning, not as archive content.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "archive-residual-followup-context.md").write_text(
        "# Archive Residual Followup Context\n\n"
        "This run derives parser-capability, repair-completion, and nested-boundary controls "
        "from archive residual metadata. It keeps archive payload text, member names, source "
        "names, and paths out of stored context while preserving support and migration signals.\n\n"
        "Agent usage:\n\n"
        "- Use `archive-residual-followup-cases.jsonl` for unsupported parser, damaged-container, and nested-boundary situations.\n"
        "- Use `archive-residual-followup-signals.jsonl` for stable ids, follow-up routes, status buckets, and composition counts.\n"
        "- Use `archive-residual-followup-controls.jsonl` as a parser and repair checklist.\n"
        "- Never treat this layer as archive payload text, raw member names, complete recovery, or training payload.\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_archive_residual_run / "archive-residual-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["archive_residual_followup_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    status_counts = counter_from_rows(signals, "archive_followup_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_archive_residual_followup_batch",
        "source_archive_residual_run": args.source_archive_residual_run,
        "source_signal_count": len(source_rows),
        "source_target_signal_count": len(source_rows),
        "signals_written": len(signals),
        "archive_residual_followup_case_count": len(cases),
        "control_requirement_count": len(controls),
        "direct_parser_capability_route_count": status_counts.get("direct_archive_parser_capability_requirements_modeled", 0),
        "nested_parser_capability_route_count": status_counts.get("nested_archive_parser_capability_requirements_modeled", 0),
        "direct_repair_completion_route_count": status_counts.get("direct_zip_repair_completion_requirements_modeled", 0),
        "nested_repair_completion_route_count": status_counts.get("nested_zip_repair_completion_requirements_modeled", 0),
        "sensitive_followup_route_count": sum(1 for row in signals if row["sensitive_route"]),
        "sanitization": {
            "source_archives_read": False,
            "archive_payloads_extracted_to_disk": False,
            "raw_archive_names_copied": False,
            "raw_member_names_copied": False,
            "raw_payload_text_copied": False,
            "raw_source_paths_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
            "training_payload_created": False,
        },
    }

    common.write_jsonl(run_dir / "archive-residual-followup-signals.jsonl", signals)
    common.write_jsonl(run_dir / "archive-residual-followup-cases.jsonl", cases)
    common.write_jsonl(run_dir / "archive-residual-followup-controls.jsonl", controls)
    write_context(run_dir)

    issues = common.scan_forbidden(output_root)
    manifest["privacy_hit_count"] = len(issues)
    (run_dir / "privacy-scan.json").write_text(
        json.dumps({"hit_count": len(issues), "issues": issues}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_coverage(run_dir, manifest, signals)
    return run_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="knowledge-context")
    parser.add_argument("--run-id", default="directory-archive-residual-followup-batch-20260622")
    parser.add_argument("--source-archive-residual-run", default="directory-archive-residual-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
