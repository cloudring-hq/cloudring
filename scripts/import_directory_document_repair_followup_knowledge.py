#!/usr/bin/env python3
"""Append derived lifecycle controls for document repair/access queues.

This pass reads only document-residual metadata. It does not open source
documents, decrypt content, repair payloads, copy document text, copy metadata
values, copy internal member names, copy source names, copy paths, or store
domains, provider names, people, brands, vendors, or secrets.
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
    "metadata_value_exclusion": "avoid copying author, title, subject, revision, and similar metadata values",
    "internal_member_name_exclusion": "avoid copying internal container member names during repair lifecycle work",
    "source_name_path_exclusion": "avoid copying raw source names and paths into agent context",
    "repair_sandbox": "run repair, conversion, and parser work in a bounded sandbox with no payload export",
    "container_integrity_check": "distinguish damaged containers from unsupported or placeholder artifacts before migration",
    "repair_or_reingest_guidance": "surface repair or reingest guidance as a product support workflow",
    "tiny_placeholder_validation": "treat tiny damaged containers as possible placeholders, partial transfers, or failed exports",
    "pdf_parser_fallback_vetting": "vet PDF fallback parsers before content-level handling",
    "encrypted_access_ownership_gate": "require ownership and access workflow before encrypted document handling",
    "non_decryption_default": "default to non-decryption metadata handling unless authorization and keys are present",
    "chain_of_custody_traceability": "preserve stable ids, integrity hashes, and status buckets for support audit trails",
    "customer_communication_guidance": "retain product guidance for explaining repair, reingest, or access next steps",
    "support_traceability": "retain stable evidence ids for support handoff without exposing document content",
    "retention_minimization": "retain only the smallest useful lifecycle evidence",
    "training_payload_review_gate": "require a separate review before any derived summary becomes model-training material",
    "sensitive_document_route": "route sensitive document records through secret-aware handling before deeper processing",
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


def lifecycle_status(row: dict) -> str:
    status = str(row.get("residual_status") or "")
    if status == "damaged_zip_document_repair_requirements_modeled":
        return "damaged_document_repair_lifecycle_requirements_modeled"
    if status == "pdf_parser_failure_requirements_modeled":
        return "pdf_parser_fallback_lifecycle_requirements_modeled"
    if status == "encrypted_document_access_requirements_modeled":
        return "encrypted_document_access_lifecycle_requirements_modeled"
    return "document_repair_access_lifecycle_requirements_modeled"


def lifecycle_route(status: str) -> str:
    if status == "damaged_document_repair_lifecycle_requirements_modeled":
        return "document_repair_or_reingest_lifecycle_route"
    if status == "pdf_parser_fallback_lifecycle_requirements_modeled":
        return "pdf_parser_fallback_lifecycle_route"
    if status == "encrypted_document_access_lifecycle_requirements_modeled":
        return "encrypted_document_access_lifecycle_route"
    return "document_lifecycle_triage_route"


def lifecycle_readiness(status: str) -> str:
    if status == "damaged_document_repair_lifecycle_requirements_modeled":
        return "repair_or_reingest_required_before_content_handling"
    if status == "pdf_parser_fallback_lifecycle_requirements_modeled":
        return "fallback_parser_required_before_content_handling"
    if status == "encrypted_document_access_lifecycle_requirements_modeled":
        return "access_workflow_required_before_content_handling"
    return "lifecycle_triage_required_before_content_handling"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "raw_document_text_exclusion",
        "metadata_value_exclusion",
        "internal_member_name_exclusion",
        "source_name_path_exclusion",
        "repair_sandbox",
        "chain_of_custody_traceability",
        "support_traceability",
        "retention_minimization",
        "training_payload_review_gate",
    }
    if status == "damaged_document_repair_lifecycle_requirements_modeled":
        controls.update({"container_integrity_check", "repair_or_reingest_guidance", "customer_communication_guidance"})
        if row.get("size_bucket") == "lt_1_kib":
            controls.add("tiny_placeholder_validation")
    if status == "pdf_parser_fallback_lifecycle_requirements_modeled":
        controls.update({"pdf_parser_fallback_vetting", "customer_communication_guidance"})
    if status == "encrypted_document_access_lifecycle_requirements_modeled":
        controls.update({"encrypted_access_ownership_gate", "non_decryption_default", "customer_communication_guidance"})
    if row.get("sensitive_flags"):
        controls.add("sensitive_document_route")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if row.get("sensitive_flags"):
        return "sensitive_document_lifecycle_risk"
    if status == "damaged_document_repair_lifecycle_requirements_modeled" and row.get("size_bucket") == "lt_1_kib":
        return "tiny_damaged_document_repair_lifecycle_risk"
    if status == "damaged_document_repair_lifecycle_requirements_modeled":
        return "damaged_document_repair_lifecycle_risk"
    if status == "pdf_parser_fallback_lifecycle_requirements_modeled":
        return "pdf_parser_fallback_lifecycle_risk"
    if status == "encrypted_document_access_lifecycle_requirements_modeled":
        return "encrypted_document_access_lifecycle_risk"
    return "document_lifecycle_risk"


def lifecycle_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    tags = [
        "document_repair_followup_reviewed",
        "derived_from_residual_metadata_only",
        "not_training_payload",
        f"document_lifecycle_status_{status}",
        f"document_lifecycle_readiness_{lifecycle_readiness(status)}",
        f"document_lifecycle_route_{route}",
        f"risk_{risk}",
        f"extension_{row.get('extension', 'unknown')}",
        f"residual_status_{row.get('residual_status', 'unknown')}",
        f"structure_status_{str(row.get('structure_status', 'unknown')).split(':', 1)[0]}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("document_residual_tags") or []:
        if source_tag.startswith("source_") or source_tag in {
            "document_residual_reviewed",
            "derived_from_structural_metadata_only",
        }:
            tags.append(f"prior_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        status = lifecycle_status(row)
        route = lifecycle_route(status)
        controls = required_controls(row, status)
        risk = risk_bucket(row, status)
        signals.append(
            {
                "document_repair_followup_signal_id": "docrepair-" + common.stable_hash(row["document_residual_signal_id"]),
                "case_id": "",
                "source_document_residual_signal_id": row["document_residual_signal_id"],
                "source_document_backlog_signal_id": row.get("source_document_backlog_signal_id", ""),
                "file_id": row.get("file_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "magic_family": row.get("magic_family", "unknown"),
                "size_bucket": row.get("size_bucket", "unknown"),
                "prior_text_status": row.get("prior_text_status", "unknown"),
                "structure_status": row.get("structure_status", "unknown"),
                "residual_status": row.get("residual_status", "unknown"),
                "handling_route": row.get("handling_route", "unknown"),
                "document_lifecycle_status": status,
                "document_lifecycle_readiness": lifecycle_readiness(status),
                "document_lifecycle_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "document_repair_followup_tags": lifecycle_tags(row, status, route, controls, risk),
                "sensitive_flags": row.get("sensitive_flags", []),
                "sensitive_route": bool(row.get("sensitive_flags")),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['document_lifecycle_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["document_lifecycle_status"] for row in rows)
        readiness_counter = collections.Counter(row["document_lifecycle_readiness"] for row in rows)
        route_counter = collections.Counter(row["document_lifecycle_route"] for row in rows)
        extension_counter = collections.Counter(row["extension"] for row in rows)
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["document_repair_followup_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "document_lifecycle_modeled"
        implications = [
            "Treat document repair/access residuals as explicit product lifecycle work, not as missing context.",
            "Future repair or parser work must keep document text, metadata values, and internal member names excluded unless a separate safe path is proven.",
        ]
        if control_counter.get("repair_or_reingest_guidance", 0):
            implications.append("Damaged document containers need repair, reingest, integrity checks, and clear support communication.")
        if control_counter.get("tiny_placeholder_validation", 0):
            implications.append("Tiny damaged containers should be treated as possible placeholders, partial transfers, or failed exports.")
        if control_counter.get("pdf_parser_fallback_vetting", 0):
            implications.append("PDF parser failures need vetted fallback parser capability before content handling.")
        if control_counter.get("encrypted_access_ownership_gate", 0):
            implications.append("Encrypted documents need ownership and access workflow before deeper processing.")
        if control_counter.get("sensitive_document_route", 0):
            implications.append("Sensitive documents require secret-aware handling before lifecycle work continues.")
        case = {
            "case_id": "docrepaircase-" + common.stable_hash(key),
            "case_type": "document_repair_access_lifecycle_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
            "extension_counts": dict(extension_counter.most_common()),
            "document_lifecycle_status_counts": dict(status_counter.most_common()),
            "document_lifecycle_readiness_counts": dict(readiness_counter.most_common()),
            "document_lifecycle_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "document_repair_followup_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_document_repair_followup_signal_ids": [row["document_repair_followup_signal_id"] for row in rows[:50]],
            "evidence_document_repair_followup_signal_id_count": len(rows),
            "summary": (
                f"A document repair/access lifecycle cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} residual metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for document repair, reingest, parser fallback, encrypted access, and support workflows "
                "without copying document content or metadata values."
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
        status_counter = collections.Counter(row["document_lifecycle_status"] for row in rows)
        route_counter = collections.Counter(row["document_lifecycle_route"] for row in rows)
        controls.append(
            {
                "document_repair_followup_control_id": "docrepaircontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
                "document_lifecycle_status_counts": dict(status_counter.most_common()),
                "document_lifecycle_route_counts": dict(route_counter.most_common()),
                "evidence_document_repair_followup_signal_ids": [row["document_repair_followup_signal_id"] for row in rows[:50]],
                "agent_use": "Use as a document repair/access lifecycle checkpoint, not as document content.",
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
    status_counts = counter_from_rows(signals, "document_lifecycle_status")
    route_counts = counter_from_rows(signals, "document_lifecycle_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Document Repair Followup Coverage

- Source kind: directory document repair followup batch
- Source document residual run: `{manifest["source_document_residual_run"]}`
- Source residual signals: {manifest["source_signal_count"]}
- Followup signals written: {manifest["signals_written"]}
- Followup cases: {manifest["document_repair_followup_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Damaged repair lifecycle routes: {manifest["damaged_repair_lifecycle_route_count"]}
- PDF fallback lifecycle routes: {manifest["pdf_fallback_lifecycle_route_count"]}
- Encrypted access lifecycle routes: {manifest["encrypted_access_lifecycle_route_count"]}
- Sensitive lifecycle routes: {manifest["sensitive_lifecycle_route_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Lifecycle Status Counts

{markdown_counter(status_counts, "document_lifecycle_status")}

## Lifecycle Route Counts

{markdown_counter(route_counts, "document_lifecycle_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over document residual metadata records.
- It does not open, repair, decrypt, or parse source documents, and it does not
  copy document text, metadata values, internal member names, source names,
  paths, domains, providers, people, brands, vendors, or secrets.
- Use these records for repair/access/parser lifecycle planning, not as
  document content or training material.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "document-repair-followup-context.md").write_text(
        "# Document Repair Followup Context\n\n"
        "This run derives repair, reingest, parser fallback, encrypted access, and support "
        "lifecycle controls from document residual metadata. It keeps document text, metadata "
        "values, internal member names, source names, and paths out of stored context.\n\n"
        "Agent usage:\n\n"
        "- Use `document-repair-followup-cases.jsonl` for damaged-container, fallback-parser, encrypted-access, and support workflow situations.\n"
        "- Use `document-repair-followup-signals.jsonl` for stable ids, lifecycle routes, readiness, and risk buckets.\n"
        "- Use `document-repair-followup-controls.jsonl` as a repair/access lifecycle checklist.\n"
        "- Never treat this layer as document text, metadata values, internal member names, decrypted content, or training payload.\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_document_residual_run / "document-residual-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["document_repair_followup_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    status_counts = counter_from_rows(signals, "document_lifecycle_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_document_repair_followup_batch",
        "source_document_residual_run": args.source_document_residual_run,
        "source_signal_count": len(source_rows),
        "source_target_signal_count": len(source_rows),
        "signals_written": len(signals),
        "document_repair_followup_case_count": len(cases),
        "control_requirement_count": len(controls),
        "damaged_repair_lifecycle_route_count": status_counts.get("damaged_document_repair_lifecycle_requirements_modeled", 0),
        "pdf_fallback_lifecycle_route_count": status_counts.get("pdf_parser_fallback_lifecycle_requirements_modeled", 0),
        "encrypted_access_lifecycle_route_count": status_counts.get("encrypted_document_access_lifecycle_requirements_modeled", 0),
        "sensitive_lifecycle_route_count": sum(1 for row in signals if row["sensitive_route"]),
        "sanitization": {
            "source_documents_read": False,
            "documents_repaired": False,
            "documents_decrypted": False,
            "raw_document_text_copied": False,
            "raw_internal_member_names_copied": False,
            "raw_metadata_values_copied": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
            "training_payload_created": False,
        },
    }

    common.write_jsonl(run_dir / "document-repair-followup-signals.jsonl", signals)
    common.write_jsonl(run_dir / "document-repair-followup-cases.jsonl", cases)
    common.write_jsonl(run_dir / "document-repair-followup-controls.jsonl", controls)
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
    parser.add_argument("--run-id", default="directory-document-repair-followup-batch-20260622")
    parser.add_argument("--source-document-residual-run", default="directory-document-residual-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
