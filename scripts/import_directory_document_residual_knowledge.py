#!/usr/bin/env python3
"""Append derived handling for document structural failure queues.

This pass reads only the previous safe document-backlog structural run. It does
not open source documents and does not copy document text, internal member
names, metadata values, source paths, file names, domains, provider names,
people, brands, vendors, or secrets.
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
    "raw_document_text_exclusion": "exclude raw document text from stored context and training payloads",
    "internal_member_name_exclusion": "avoid copying internal container member names during repair analysis",
    "metadata_value_exclusion": "avoid copying author, subject, title, and other metadata values",
    "metadata_only_inventory": "preserve extension, size, status, and count buckets as structural evidence",
    "safe_parser_sandbox": "run future document repair or parser work in a bounded sandbox with no payload export",
    "support_traceability": "preserve stable ids and status buckets for support handoff without exposing content",
    "retention_minimization": "retain only structural evidence unless a safer content path is proven",
    "container_integrity_check": "distinguish damaged document containers from unsupported content before migration",
    "repair_or_reingest_guidance": "surface damaged container guidance for customer-facing reingest or repair workflows",
    "tiny_container_validation": "treat tiny damaged containers as possible placeholders, partial transfers, or failed exports",
    "pdf_parser_fallback": "route PDF parser failures through fallback parser planning without text extraction",
    "encrypted_document_access_gate": "require explicit access and ownership workflow before encrypted document handling",
    "non_decryption_default": "default to non-decryption metadata handling unless authorization and keys are present",
    "secret_aware_document_handling": "route sensitive document failures through secret-aware handling",
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


def is_residual_target(row: dict) -> bool:
    tags = set(row.get("document_backlog_tags") or [])
    status = str(row.get("structure_status") or "").lower()
    return "structural_probe_failed" in tags or "encrypted" in status


def residual_status(row: dict) -> str:
    status = str(row.get("structure_status") or "")
    if "encrypted" in status.lower():
        return "encrypted_document_access_requirements_modeled"
    if "BadZipFile" in status:
        return "damaged_zip_document_repair_requirements_modeled"
    if status.startswith("pdf_structure_failed"):
        return "pdf_parser_failure_requirements_modeled"
    return "document_structural_failure_requirements_modeled"


def handling_route(status: str) -> str:
    if status == "encrypted_document_access_requirements_modeled":
        return "encrypted_document_access_gate"
    if status == "damaged_zip_document_repair_requirements_modeled":
        return "damaged_container_repair_or_reingest_route"
    if status == "pdf_parser_failure_requirements_modeled":
        return "bounded_pdf_parser_fallback_route"
    return "bounded_document_parser_triage_route"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "raw_document_text_exclusion",
        "internal_member_name_exclusion",
        "metadata_value_exclusion",
        "metadata_only_inventory",
        "safe_parser_sandbox",
        "support_traceability",
        "retention_minimization",
    }
    if status == "damaged_zip_document_repair_requirements_modeled":
        controls.update({"container_integrity_check", "repair_or_reingest_guidance"})
        if row.get("size_bucket") == "lt_1_kib":
            controls.add("tiny_container_validation")
    if status == "pdf_parser_failure_requirements_modeled":
        controls.add("pdf_parser_fallback")
    if status == "encrypted_document_access_requirements_modeled":
        controls.update({"encrypted_document_access_gate", "non_decryption_default"})
    if row.get("sensitive_flags"):
        controls.add("secret_aware_document_handling")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if status == "encrypted_document_access_requirements_modeled":
        return "encrypted_document_access_risk"
    if row.get("sensitive_flags"):
        return "sensitive_document_structural_failure_risk"
    if status == "damaged_zip_document_repair_requirements_modeled" and row.get("size_bucket") == "lt_1_kib":
        return "tiny_damaged_document_container_risk"
    if status == "damaged_zip_document_repair_requirements_modeled":
        return "damaged_document_container_risk"
    if status == "pdf_parser_failure_requirements_modeled":
        return "pdf_parser_failure_risk"
    return "document_structural_failure_risk"


def residual_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    tags = [
        "document_residual_reviewed",
        "derived_from_structural_metadata_only",
        "not_training_payload",
        f"residual_status_{status}",
        f"handling_route_{route}",
        f"risk_{risk}",
        f"extension_{row.get('extension', 'unknown')}",
        f"structure_status_{str(row.get('structure_status', 'unknown')).split(':', 1)[0]}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("document_backlog_tags") or []:
        if source_tag in {
            "structural_probe_failed",
            "encrypted_document_backlog",
            "prior_extract_failed",
            "prior_unsupported_document_format",
            "magic_unknown_document_signature",
        }:
            tags.append(f"source_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        if not is_residual_target(row):
            continue
        status = residual_status(row)
        route = handling_route(status)
        controls = required_controls(row, status)
        risk = risk_bucket(row, status)
        signals.append(
            {
                "document_residual_signal_id": "docresidual-" + common.stable_hash(row["document_backlog_signal_id"]),
                "case_id": "",
                "source_document_backlog_signal_id": row["document_backlog_signal_id"],
                "file_id": row.get("file_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "magic_family": row.get("magic_family", "unknown"),
                "size_bucket": row.get("size_bucket", "unknown"),
                "prior_text_status": row.get("prior_text_status", "unknown"),
                "structure_status": row.get("structure_status", "unknown"),
                "structure_count_buckets": row.get("structure_count_buckets", {}),
                "residual_status": status,
                "handling_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "document_residual_tags": residual_tags(row, status, route, controls, risk),
                "sensitive_flags": row.get("sensitive_flags", []),
                "sensitive_route": bool(row.get("sensitive_flags")),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['residual_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["residual_status"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        route_counter = collections.Counter(row["handling_route"] for row in rows)
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["document_residual_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "document_residual_modeled"
        implications = [
            "Treat failed or encrypted document structure as durable context, not as dropped evidence.",
            "Future repair or parser work must keep text, metadata values, and internal member names excluded unless a separate safe path is proven.",
        ]
        if control_counter.get("repair_or_reingest_guidance", 0):
            implications.append("Damaged document containers need customer-facing repair or reingest guidance and migration integrity checks.")
        if control_counter.get("encrypted_document_access_gate", 0):
            implications.append("Encrypted documents need ownership and access workflow before any content handling.")
        if control_counter.get("pdf_parser_fallback", 0):
            implications.append("PDF parser failures should have fallback parser planning while preserving metadata-only handling.")
        if control_counter.get("secret_aware_document_handling", 0):
            implications.append("Sensitive failed documents require secret-aware routing before deeper processing.")
        case = {
            "case_id": "docresidualcase-" + common.stable_hash(key),
            "case_type": "document_structural_residual_handling_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
            "extension_counts": dict(ext_counter.most_common()),
            "residual_status_counts": dict(status_counter.most_common()),
            "handling_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "document_residual_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_document_residual_signal_ids": [row["document_residual_signal_id"] for row in rows[:50]],
            "evidence_document_residual_signal_id_count": len(rows),
            "summary": (
                f"A document residual cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} structural metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for damaged document repair, encrypted access workflow, parser fallback, "
                "and migration integrity planning without copying document content."
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
        status_counter = collections.Counter(row["residual_status"] for row in rows)
        route_counter = collections.Counter(row["handling_route"] for row in rows)
        controls.append(
            {
                "document_residual_control_id": "doccontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
                "residual_status_counts": dict(status_counter.most_common()),
                "handling_route_counts": dict(route_counter.most_common()),
                "evidence_document_residual_signal_ids": [row["document_residual_signal_id"] for row in rows[:50]],
                "agent_use": "Use as a document repair/access/parser requirement checkpoint, not as document content.",
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
    status_counts = counter_from_rows(signals, "residual_status")
    route_counts = counter_from_rows(signals, "handling_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Document Residual Coverage

- Source kind: directory document residual batch
- Source document backlog run: `{manifest["source_document_backlog_run"]}`
- Source residual targets: {manifest["source_residual_target_signal_count"]}
- Residual signals written: {manifest["signals_written"]}
- Residual cases: {manifest["document_residual_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Damaged zip-document containers: {manifest["damaged_zip_document_count"]}
- PDF parser failures: {manifest["pdf_parser_failure_count"]}
- Encrypted documents: {manifest["encrypted_document_count"]}
- Sensitive residual signals: {manifest["sensitive_residual_signal_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Residual Status Counts

{markdown_counter(status_counts, "residual_status")}

## Handling Route Counts

{markdown_counter(route_counts, "handling_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over structural metadata records.
- It does not read source documents or copy document text, internal member
  names, metadata values, paths, domains, providers, people, brands, vendors,
  or secrets.
- Use these records for repair/access/parser planning, not as document content.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "document-residual-context.md").write_text(
        "# Document Residual Context\n\n"
        "This run derives safe handling requirements from document backlog records where structural probing failed "
        "or detected encryption. It preserves damaged-container, parser-failure, encrypted-access, and sensitive "
        "routing context while keeping document text and metadata values out of stored context.\n\n"
        "Agent usage:\n\n"
        "- Use `document-residual-cases.jsonl` for damaged document, encrypted document, and parser-fallback situations.\n"
        "- Use `document-residual-signals.jsonl` for stable ids, residual statuses, handling routes, and risk buckets.\n"
        "- Use `document-residual-controls.jsonl` as a repair/access/parser planning checklist.\n"
        "- Never treat this layer as document text, internal member names, metadata values, or decrypted content.\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_document_backlog_run / "document-backlog-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["document_residual_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    status_counts = counter_from_rows(signals, "residual_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_document_residual_batch",
        "source_document_backlog_run": args.source_document_backlog_run,
        "source_signal_count": len(source_rows),
        "source_residual_target_signal_count": len(signals),
        "signals_written": len(signals),
        "document_residual_case_count": len(cases),
        "control_requirement_count": len(controls),
        "damaged_zip_document_count": status_counts.get("damaged_zip_document_repair_requirements_modeled", 0),
        "pdf_parser_failure_count": status_counts.get("pdf_parser_failure_requirements_modeled", 0),
        "encrypted_document_count": status_counts.get("encrypted_document_access_requirements_modeled", 0),
        "sensitive_residual_signal_count": sum(1 for row in signals if row["sensitive_route"]),
        "sanitization": {
            "source_files_read": False,
            "raw_document_text_copied": False,
            "raw_internal_member_names_copied": False,
            "raw_metadata_values_copied": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
        },
    }

    common.write_jsonl(run_dir / "document-residual-signals.jsonl", signals)
    common.write_jsonl(run_dir / "document-residual-cases.jsonl", cases)
    common.write_jsonl(run_dir / "document-residual-controls.jsonl", controls)
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
    parser.add_argument("--run-id", default="directory-document-residual-batch")
    parser.add_argument("--source-document-backlog-run", default="directory-document-backlog-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
