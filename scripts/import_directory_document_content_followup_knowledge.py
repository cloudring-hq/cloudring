#!/usr/bin/env python3
"""Append safe content-followup routing for document backlog signals.

This pass reads only the previously generated document-backlog structural
records. It does not open source documents and does not copy document text,
internal member names, metadata values, source paths, file names, domains,
provider names, people, brands, vendors, or secrets.
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
    "redacted_chunk_summarization_gate": "allow future document summaries only through bounded redaction and chunk review",
    "metadata_value_exclusion": "avoid copying author, title, subject, revision, and similar metadata values",
    "internal_member_name_exclusion": "avoid copying internal container member names during content preparation",
    "source_name_path_exclusion": "avoid copying raw source names and paths into agent context",
    "structure_bucket_traceability": "preserve stable ids, extensions, status buckets, and count buckets as traceability evidence",
    "training_payload_review_gate": "require a separate review before any derived summary becomes model-training material",
    "support_traceability": "retain stable evidence ids for support handoff without exposing payload content",
    "retention_minimization": "retain only the smallest useful structural and route evidence",
    "parser_sandbox": "run future parser or conversion work in a bounded sandbox with no payload export",
    "spreadsheet_formula_value_guard": "treat formulas, sheet labels, and cell values as sensitive until redacted",
    "presentation_media_ocr_gate": "gate slide media, speaker notes, and visual text through redacted review",
    "word_processing_embedded_object_gate": "gate embedded objects and linked content before text summarization",
    "diagram_visual_text_gate": "gate shape labels and diagram text through redacted review",
    "project_plan_schedule_value_guard": "treat task names, schedules, dependencies, and resource labels as sensitive until redacted",
    "legacy_parser_capability_gate": "require a vetted legacy parser before any content-level handling",
    "damaged_container_repair_before_content": "repair or reingest damaged containers before content summarization",
    "pdf_parser_fallback_before_content": "use fallback parser planning before PDF content summarization",
    "encrypted_document_access_gate": "require ownership and access workflow before encrypted document handling",
    "non_decryption_default": "default to non-decryption metadata handling unless authorization and keys are present",
    "secret_aware_document_content_route": "route sensitive document records through secret-aware handling before deeper processing",
    "visual_media_ocr_gate": "gate embedded images and media through redacted OCR or visual review",
    "macro_embedded_object_gate": "gate macro-enabled or executable document parts before parser expansion",
}


READY_STATUSES = {
    "zip_structure_extracted",
    "pdf_structure_extracted",
    "legacy_ole_identified",
    "legacy_structure_identified",
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


def content_family(row: dict) -> str:
    extension = str(row.get("extension") or "").lower()
    if extension in {"doc", "docx"}:
        return "word_processing"
    if extension in {"xls", "xlsx"}:
        return "spreadsheet"
    if extension in {"ppt", "pptx"}:
        return "presentation"
    if extension == "pdf":
        return "pdf"
    if extension in {"vsd", "vsdx", "vss", "vdx", "vsdm"}:
        return "diagram"
    if extension == "mpp":
        return "project_plan"
    return "generic_document"


def content_followup_status(row: dict) -> str:
    status = str(row.get("structure_status") or "")
    family = content_family(row)
    if status == "zip_structure_extracted":
        if family == "word_processing":
            return "structured_word_processing_redacted_summarization_requirements_modeled"
        if family == "spreadsheet":
            return "structured_spreadsheet_redacted_summarization_requirements_modeled"
        if family == "presentation":
            return "structured_presentation_redacted_summarization_requirements_modeled"
        if family == "diagram":
            return "structured_diagram_redacted_summarization_requirements_modeled"
        return "structured_package_redacted_summarization_requirements_modeled"
    if status == "pdf_structure_extracted":
        return "structured_pdf_redacted_summarization_requirements_modeled"
    if status in {"legacy_ole_identified", "legacy_structure_identified"}:
        return "legacy_document_parser_requirements_modeled"
    if "BadZipFile" in status:
        return "damaged_document_repair_before_content_requirements_modeled"
    if status == "pdf_structure_encrypted":
        return "encrypted_document_access_before_content_requirements_modeled"
    if status.startswith("pdf_structure_failed"):
        return "pdf_parser_fallback_before_content_requirements_modeled"
    return "document_content_followup_requirements_modeled"


def content_readiness(row: dict) -> str:
    status = str(row.get("structure_status") or "")
    if status in READY_STATUSES:
        return "structure_ready_for_redacted_summarization"
    return "repair_or_access_required_before_content"


def content_route(row: dict, status: str) -> str:
    family = content_family(row)
    if status == "damaged_document_repair_before_content_requirements_modeled":
        return "damaged_container_repair_first_route"
    if status == "encrypted_document_access_before_content_requirements_modeled":
        return "encrypted_access_gate_route"
    if status == "pdf_parser_fallback_before_content_requirements_modeled":
        return "pdf_parser_fallback_first_route"
    if status == "legacy_document_parser_requirements_modeled":
        return "legacy_parser_then_redacted_summarization_route"
    if family == "spreadsheet":
        return "spreadsheet_redacted_summarization_route"
    if family == "presentation":
        return "presentation_redacted_summarization_route"
    if family == "diagram":
        return "diagram_visual_text_redaction_route"
    if family == "project_plan":
        return "project_plan_redacted_summarization_route"
    if family == "pdf":
        return "pdf_redacted_summarization_route"
    if family == "word_processing":
        return "word_processing_redacted_summarization_route"
    return "redacted_chunk_summarization_route"


def required_controls(row: dict, status: str) -> list[str]:
    family = content_family(row)
    tags = set(row.get("document_backlog_tags") or [])
    readiness = content_readiness(row)
    controls = {
        "raw_document_text_exclusion",
        "metadata_value_exclusion",
        "source_name_path_exclusion",
        "structure_bucket_traceability",
        "training_payload_review_gate",
        "support_traceability",
        "retention_minimization",
    }
    if readiness == "structure_ready_for_redacted_summarization":
        controls.update({"redacted_chunk_summarization_gate", "parser_sandbox"})
    if str(row.get("structure_status") or "").startswith("zip_"):
        controls.add("internal_member_name_exclusion")
    if family == "spreadsheet":
        controls.add("spreadsheet_formula_value_guard")
    if family == "presentation":
        controls.add("presentation_media_ocr_gate")
    if family == "word_processing":
        controls.add("word_processing_embedded_object_gate")
    if family == "diagram":
        controls.add("diagram_visual_text_gate")
    if family == "project_plan":
        controls.add("project_plan_schedule_value_guard")
    if status == "legacy_document_parser_requirements_modeled":
        controls.update({"legacy_parser_capability_gate", "parser_sandbox"})
    if status == "damaged_document_repair_before_content_requirements_modeled":
        controls.update({"damaged_container_repair_before_content", "parser_sandbox", "internal_member_name_exclusion"})
    if status == "pdf_parser_fallback_before_content_requirements_modeled":
        controls.update({"pdf_parser_fallback_before_content", "parser_sandbox"})
    if status == "encrypted_document_access_before_content_requirements_modeled":
        controls.update({"encrypted_document_access_gate", "non_decryption_default"})
    if "embedded_media_structure" in tags:
        controls.add("visual_media_ocr_gate")
    if "embedded_objects_structure" in tags:
        controls.add("word_processing_embedded_object_gate")
    if "macro_enabled_structure" in tags:
        controls.add("macro_embedded_object_gate")
    if row.get("sensitive_flags"):
        controls.add("secret_aware_document_content_route")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if status == "encrypted_document_access_before_content_requirements_modeled":
        return "encrypted_document_content_risk"
    if row.get("sensitive_flags"):
        return "sensitive_document_content_route_risk"
    if status == "damaged_document_repair_before_content_requirements_modeled":
        return "damaged_document_container_content_risk"
    if status == "pdf_parser_fallback_before_content_requirements_modeled":
        return "pdf_parser_fallback_content_risk"
    if status == "legacy_document_parser_requirements_modeled":
        return "legacy_document_content_parser_risk"
    if content_family(row) in {"spreadsheet", "project_plan"}:
        return "structured_planning_or_value_content_risk"
    if content_family(row) in {"presentation", "diagram"}:
        return "visual_text_content_risk"
    return "document_redacted_summarization_risk"


def followup_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    source_status = str(row.get("structure_status") or "unknown").split(":", 1)[0]
    tags = [
        "document_content_followup_reviewed",
        "derived_from_structural_metadata_only",
        "not_training_payload",
        f"content_family_{content_family(row)}",
        f"content_followup_status_{status}",
        f"content_readiness_{content_readiness(row)}",
        f"content_route_{route}",
        f"risk_{risk}",
        f"extension_{row.get('extension', 'unknown')}",
        f"structure_status_{source_status}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("document_backlog_tags") or []:
        if source_tag in {
            "structural_coverage_added",
            "structural_probe_failed",
            "encrypted_document_backlog",
            "embedded_media_structure",
            "embedded_objects_structure",
            "macro_enabled_structure",
            "presentation_structure",
            "document_body_structure",
            "diagram_document_structure",
            "legacy_document_structured",
            "pdf_page_structure",
        }:
            tags.append(f"source_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        status = content_followup_status(row)
        route = content_route(row, status)
        controls = required_controls(row, status)
        risk = risk_bucket(row, status)
        signals.append(
            {
                "document_content_followup_signal_id": "doccontent-" + common.stable_hash(row["document_backlog_signal_id"]),
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
                "content_family": content_family(row),
                "content_followup_status": status,
                "content_readiness": content_readiness(row),
                "content_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "document_content_followup_tags": followup_tags(row, status, route, controls, risk),
                "sensitive_flags": row.get("sensitive_flags", []),
                "sensitive_route": bool(row.get("sensitive_flags")),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['content_followup_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["content_followup_status"] for row in rows)
        readiness_counter = collections.Counter(row["content_readiness"] for row in rows)
        family_counter = collections.Counter(row["content_family"] for row in rows)
        route_counter = collections.Counter(row["content_route"] for row in rows)
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["document_content_followup_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "document_content_followup_modeled"
        implications = [
            "Treat document backlog content handling as a staged workflow: structure, redaction, summarization, and review.",
            "Do not promote structural evidence directly into content or training material without the required controls.",
        ]
        if readiness_counter.get("structure_ready_for_redacted_summarization", 0):
            implications.append("Structure-ready documents can move to bounded redacted summarization with stable-id traceability.")
        if readiness_counter.get("repair_or_access_required_before_content", 0):
            implications.append("Repair, parser fallback, or access workflow must finish before any content-level handling.")
        if control_counter.get("spreadsheet_formula_value_guard", 0):
            implications.append("Spreadsheet-like artifacts need formula, cell-value, and sheet-label protection.")
        if control_counter.get("presentation_media_ocr_gate", 0) or control_counter.get("visual_media_ocr_gate", 0):
            implications.append("Presentation and visual media content needs redacted OCR or visual review before summarization.")
        if control_counter.get("legacy_parser_capability_gate", 0):
            implications.append("Legacy document formats require vetted parser capability before extraction.")
        if control_counter.get("encrypted_document_access_gate", 0):
            implications.append("Encrypted documents require ownership and access workflow before deeper processing.")
        case = {
            "case_id": "doccontentcase-" + common.stable_hash(key),
            "case_type": "document_content_followup_handling_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
            "content_family_counts": dict(family_counter.most_common()),
            "content_followup_status_counts": dict(status_counter.most_common()),
            "content_readiness_counts": dict(readiness_counter.most_common()),
            "content_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "document_content_followup_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_document_content_followup_signal_ids": [row["document_content_followup_signal_id"] for row in rows[:50]],
            "evidence_document_content_followup_signal_id_count": len(rows),
            "summary": (
                f"A document content-followup cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} structural metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case to plan redacted document summarization, repair-first flows, legacy parser gates, "
                "and access controls without copying document content."
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
        status_counter = collections.Counter(row["content_followup_status"] for row in rows)
        readiness_counter = collections.Counter(row["content_readiness"] for row in rows)
        route_counter = collections.Counter(row["content_route"] for row in rows)
        controls.append(
            {
                "document_content_followup_control_id": "doccontentcontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
                "content_followup_status_counts": dict(status_counter.most_common()),
                "content_readiness_counts": dict(readiness_counter.most_common()),
                "content_route_counts": dict(route_counter.most_common()),
                "evidence_document_content_followup_signal_ids": [row["document_content_followup_signal_id"] for row in rows[:50]],
                "agent_use": "Use as a document content-handling checkpoint, not as document text.",
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
    status_counts = counter_from_rows(signals, "content_followup_status")
    readiness_counts = counter_from_rows(signals, "content_readiness")
    route_counts = counter_from_rows(signals, "content_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Document Content Followup Coverage

- Source kind: directory document content followup batch
- Source document backlog run: `{manifest["source_document_backlog_run"]}`
- Source document backlog signals: {manifest["source_signal_count"]}
- Followup signals written: {manifest["signals_written"]}
- Followup cases: {manifest["document_content_followup_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Structure-ready content routes: {manifest["structure_ready_content_route_count"]}
- Repair or access-before-content routes: {manifest["repair_or_access_before_content_count"]}
- Sensitive content routes: {manifest["sensitive_content_route_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Followup Status Counts

{markdown_counter(status_counts, "content_followup_status")}

## Content Readiness Counts

{markdown_counter(readiness_counts, "content_readiness")}

## Content Route Counts

{markdown_counter(route_counts, "content_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over structural metadata records.
- It does not read source documents or copy document text, internal member
  names, metadata values, paths, domains, providers, people, brands, vendors,
  or secrets.
- Use these records for content-handling routes and controls, not as document
  content or training material.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "document-content-followup-context.md").write_text(
        "# Document Content Followup Context\n\n"
        "This run derives safe content-handling routes from document backlog structural records. "
        "It separates structure-ready documents from records that require repair, parser fallback, "
        "or access workflow before content handling. It keeps document text, metadata values, "
        "internal member names, and source names out of stored context.\n\n"
        "Agent usage:\n\n"
        "- Use `document-content-followup-cases.jsonl` for redacted summarization, repair-first, legacy parser, and access-gate situations.\n"
        "- Use `document-content-followup-signals.jsonl` for stable ids, content readiness, routes, and risk buckets.\n"
        "- Use `document-content-followup-controls.jsonl` as a content-handling checklist before summarization or training use.\n"
        "- Never treat this layer as document text, internal member names, metadata values, decrypted content, or a training payload.\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_document_backlog_run / "document-backlog-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["document_content_followup_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    readiness_counts = counter_from_rows(signals, "content_readiness")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_document_content_followup_batch",
        "source_document_backlog_run": args.source_document_backlog_run,
        "source_signal_count": len(source_rows),
        "source_target_signal_count": len(source_rows),
        "signals_written": len(signals),
        "document_content_followup_case_count": len(cases),
        "control_requirement_count": len(controls),
        "structure_ready_content_route_count": readiness_counts.get("structure_ready_for_redacted_summarization", 0),
        "repair_or_access_before_content_count": readiness_counts.get("repair_or_access_required_before_content", 0),
        "sensitive_content_route_count": sum(1 for row in signals if row["sensitive_route"]),
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
            "training_payload_created": False,
        },
    }

    common.write_jsonl(run_dir / "document-content-followup-signals.jsonl", signals)
    common.write_jsonl(run_dir / "document-content-followup-cases.jsonl", cases)
    common.write_jsonl(run_dir / "document-content-followup-controls.jsonl", controls)
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
    parser.add_argument("--run-id", default="directory-document-content-followup-batch-20260622")
    parser.add_argument("--source-document-backlog-run", default="directory-document-backlog-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
