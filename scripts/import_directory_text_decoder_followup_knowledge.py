#!/usr/bin/env python3
"""Append derived lifecycle controls for text residual decoder queues.

This pass reads only text-residual-followup metadata. It does not open source
files, decode payloads, copy raw bytes, copy text, copy source names, copy
paths, or store domains, provider names, people, brands, vendors, or secrets.
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
    "raw_text_exclusion": "exclude raw decoded text from stored context and training payloads",
    "raw_payload_bytes_exclusion": "exclude raw payload bytes and byte slices from follow-up output",
    "source_name_path_exclusion": "exclude raw source names and paths from agent context",
    "metadata_only_inventory": "preserve extension, magic family, byte-shape, entropy, and status buckets only",
    "byte_shape_traceability": "retain stable ids and byte-shape buckets for safe decoder selection",
    "payload_export_block": "block payload export during decoder and routing lifecycle work",
    "special_decoder_sandbox": "run any future decoder in a bounded sandbox with no payload export",
    "decoder_capability_vetting": "vet special decoders before using them on retained candidates",
    "mixed_binary_text_gate": "treat mixed binary/text candidates as unsafe until decoder output is redacted",
    "signature_identification_gate": "identify unknown signatures before parser or decoder assumptions",
    "structured_artifact_routing_gate": "route structured artifacts to structural pipelines instead of text ingestion",
    "image_structural_pipeline_gate": "route image-like artifacts to image structure handling without OCR text export",
    "property_list_structural_pipeline_gate": "route property-list-like artifacts to structural metadata handling",
    "training_payload_review_gate": "require a separate review before any derived decoder output becomes model-training material",
    "retention_minimization": "retain only the smallest useful decoder and routing evidence",
    "support_traceability": "retain stable evidence ids for support handoff without exposing payload content",
    "sensitive_text_route": "route sensitive residual records through secret-aware handling before deeper processing",
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
    status = str(row.get("followup_status") or "")
    if status == "mixed_printable_special_decoder_requirements_modeled":
        return "mixed_printable_decoder_lifecycle_requirements_modeled"
    if status == "unknown_signature_identification_requirements_modeled":
        return "unknown_signature_identification_lifecycle_requirements_modeled"
    if status == "misrouted_image_structural_route_modeled":
        return "misrouted_image_structural_routing_lifecycle_requirements_modeled"
    if status == "misrouted_property_list_route_modeled":
        return "misrouted_property_list_routing_lifecycle_requirements_modeled"
    return "text_decoder_lifecycle_requirements_modeled"


def lifecycle_route(status: str) -> str:
    if status == "mixed_printable_decoder_lifecycle_requirements_modeled":
        return "mixed_binary_text_decoder_lifecycle_route"
    if status == "unknown_signature_identification_lifecycle_requirements_modeled":
        return "unknown_signature_identification_lifecycle_route"
    if status == "misrouted_image_structural_routing_lifecycle_requirements_modeled":
        return "image_structural_routing_lifecycle_route"
    if status == "misrouted_property_list_routing_lifecycle_requirements_modeled":
        return "property_list_structural_routing_lifecycle_route"
    return "text_decoder_lifecycle_triage_route"


def lifecycle_readiness(status: str) -> str:
    if "unknown_signature" in status:
        return "signature_identification_required_before_decoder"
    if "mixed_printable" in status:
        return "special_decoder_required_before_text_use"
    if "misrouted" in status:
        return "structural_routing_required_before_text_use"
    return "decoder_triage_required_before_text_use"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "raw_text_exclusion",
        "raw_payload_bytes_exclusion",
        "source_name_path_exclusion",
        "metadata_only_inventory",
        "byte_shape_traceability",
        "payload_export_block",
        "special_decoder_sandbox",
        "training_payload_review_gate",
        "retention_minimization",
        "support_traceability",
    }
    if status == "mixed_printable_decoder_lifecycle_requirements_modeled":
        controls.update({"decoder_capability_vetting", "mixed_binary_text_gate"})
    if status == "unknown_signature_identification_lifecycle_requirements_modeled":
        controls.update({"signature_identification_gate", "decoder_capability_vetting"})
    if status == "misrouted_image_structural_routing_lifecycle_requirements_modeled":
        controls.update({"structured_artifact_routing_gate", "image_structural_pipeline_gate"})
    if status == "misrouted_property_list_routing_lifecycle_requirements_modeled":
        controls.update({"structured_artifact_routing_gate", "property_list_structural_pipeline_gate"})
    if row.get("sensitive_flags"):
        controls.add("sensitive_text_route")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if row.get("sensitive_flags"):
        return "sensitive_text_decoder_lifecycle_risk"
    if status == "mixed_printable_decoder_lifecycle_requirements_modeled":
        return "mixed_binary_text_decoder_lifecycle_risk"
    if status == "unknown_signature_identification_lifecycle_requirements_modeled":
        return "unknown_signature_decoder_lifecycle_risk"
    if "misrouted" in status:
        return "misrouted_structural_artifact_lifecycle_risk"
    return "text_decoder_lifecycle_risk"


def lifecycle_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    tags = [
        "text_decoder_followup_reviewed",
        "derived_from_byte_shape_metadata_only",
        "not_training_payload",
        f"text_decoder_lifecycle_status_{status}",
        f"text_decoder_lifecycle_readiness_{lifecycle_readiness(status)}",
        f"text_decoder_lifecycle_route_{route}",
        f"risk_{risk}",
        f"extension_{row.get('extension', 'unknown')}",
        f"magic_{row.get('magic_family', 'unknown')}",
        f"prior_followup_status_{row.get('followup_status', 'unknown')}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("text_residual_followup_tags") or []:
        if source_tag.startswith("source_") or source_tag in {
            "text_residual_followup_reviewed",
            "derived_from_byte_shape_metadata_only",
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
                "text_decoder_followup_signal_id": "textdecoder-" + common.stable_hash(row["text_residual_followup_signal_id"]),
                "case_id": "",
                "source_text_residual_followup_signal_id": row["text_residual_followup_signal_id"],
                "source_text_residual_signal_id": row.get("source_text_residual_signal_id", ""),
                "source_text_backlog_signal_id": row.get("source_text_backlog_signal_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "kind": row.get("kind", "unknown"),
                "magic_family": row.get("magic_family", "unknown"),
                "size_bucket": row.get("size_bucket", "unknown"),
                "entropy_bucket": row.get("entropy_bucket", "unknown"),
                "byte_shape_buckets": row.get("byte_shape_buckets", {}),
                "source_residual_status": row.get("source_residual_status", "unknown"),
                "prior_followup_status": row.get("followup_status", "unknown"),
                "prior_decoder_route": row.get("decoder_route", "unknown"),
                "text_decoder_lifecycle_status": status,
                "text_decoder_lifecycle_readiness": lifecycle_readiness(status),
                "text_decoder_lifecycle_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "text_decoder_followup_tags": lifecycle_tags(row, status, route, controls, risk),
                "sensitive_flags": row.get("sensitive_flags", []),
                "sensitive_route": bool(row.get("sensitive_flags")),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['text_decoder_lifecycle_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["text_decoder_lifecycle_status"] for row in rows)
        readiness_counter = collections.Counter(row["text_decoder_lifecycle_readiness"] for row in rows)
        route_counter = collections.Counter(row["text_decoder_lifecycle_route"] for row in rows)
        magic_counter = collections.Counter(row["magic_family"] for row in rows)
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["text_decoder_followup_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "text_decoder_lifecycle_modeled"
        implications = [
            "Treat text residual decoder queues as explicit lifecycle work, not as decoded text.",
            "Future decoder output must remain excluded until redaction, routing, and training-payload review gates pass.",
        ]
        if control_counter.get("mixed_binary_text_gate", 0):
            implications.append("Mixed binary/text candidates need special decoder sandboxing before any text use.")
        if control_counter.get("signature_identification_gate", 0):
            implications.append("Unknown signatures need identification before parser assumptions.")
        if control_counter.get("structured_artifact_routing_gate", 0):
            implications.append("Misrouted structured artifacts should move to structural pipelines, not text ingestion.")
        if control_counter.get("sensitive_text_route", 0):
            implications.append("Sensitive residual records need secret-aware routing before deeper processing.")
        case = {
            "case_id": "textdecodercase-" + common.stable_hash(key),
            "case_type": "text_decoder_lifecycle_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
            "magic_family_counts": dict(magic_counter.most_common()),
            "text_decoder_lifecycle_status_counts": dict(status_counter.most_common()),
            "text_decoder_lifecycle_readiness_counts": dict(readiness_counter.most_common()),
            "text_decoder_lifecycle_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "text_decoder_followup_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_text_decoder_followup_signal_ids": [row["text_decoder_followup_signal_id"] for row in rows[:50]],
            "evidence_text_decoder_followup_signal_id_count": len(rows),
            "summary": (
                f"A text decoder lifecycle cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} byte-shape metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for special decoder, signature identification, and structured routing lifecycle planning "
                "without copying decoded text or payload bytes."
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
        status_counter = collections.Counter(row["text_decoder_lifecycle_status"] for row in rows)
        route_counter = collections.Counter(row["text_decoder_lifecycle_route"] for row in rows)
        controls.append(
            {
                "text_decoder_followup_control_id": "textdecodercontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
                "text_decoder_lifecycle_status_counts": dict(status_counter.most_common()),
                "text_decoder_lifecycle_route_counts": dict(route_counter.most_common()),
                "evidence_text_decoder_followup_signal_ids": [row["text_decoder_followup_signal_id"] for row in rows[:50]],
                "agent_use": "Use as a decoder/routing lifecycle checkpoint, not as decoded text or payload bytes.",
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
    status_counts = counter_from_rows(signals, "text_decoder_lifecycle_status")
    route_counts = counter_from_rows(signals, "text_decoder_lifecycle_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Text Decoder Followup Coverage

- Source kind: directory text decoder followup batch
- Source text residual follow-up run: `{manifest["source_text_residual_followup_run"]}`
- Source follow-up signals: {manifest["source_signal_count"]}
- Followup signals written: {manifest["signals_written"]}
- Followup cases: {manifest["text_decoder_followup_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Mixed printable decoder routes: {manifest["mixed_printable_decoder_route_count"]}
- Unknown signature routes: {manifest["unknown_signature_route_count"]}
- Structured routing routes: {manifest["structured_routing_route_count"]}
- Sensitive decoder routes: {manifest["sensitive_decoder_route_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Lifecycle Status Counts

{markdown_counter(status_counts, "text_decoder_lifecycle_status")}

## Lifecycle Route Counts

{markdown_counter(route_counts, "text_decoder_lifecycle_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over text residual follow-up metadata records.
- It does not open source files, decode payloads, copy raw bytes, copy text,
  copy source names, paths, domains, providers, people, brands, vendors, or
  secrets.
- Use these records for decoder and routing lifecycle planning, not as decoded
  text, payload bytes, or training material.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "text-decoder-followup-context.md").write_text(
        "# Text Decoder Followup Context\n\n"
        "This run derives decoder, signature-identification, and structured-routing lifecycle "
        "controls from text residual follow-up metadata. It keeps raw text, payload bytes, "
        "source names, and paths out of stored context.\n\n"
        "Agent usage:\n\n"
        "- Use `text-decoder-followup-cases.jsonl` for mixed binary/text decoder, unknown signature, image-routing, and property-list-routing situations.\n"
        "- Use `text-decoder-followup-signals.jsonl` for stable ids, lifecycle routes, byte-shape buckets, and risk buckets.\n"
        "- Use `text-decoder-followup-controls.jsonl` as a decoder and routing lifecycle checklist.\n"
        "- Never treat this layer as decoded text, payload bytes, source names, paths, or training payload.\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_text_residual_followup_run / "text-residual-followup-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["text_decoder_followup_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    status_counts = counter_from_rows(signals, "text_decoder_lifecycle_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_text_decoder_followup_batch",
        "source_text_residual_followup_run": args.source_text_residual_followup_run,
        "source_signal_count": len(source_rows),
        "source_target_signal_count": len(source_rows),
        "signals_written": len(signals),
        "text_decoder_followup_case_count": len(cases),
        "control_requirement_count": len(controls),
        "mixed_printable_decoder_route_count": status_counts.get("mixed_printable_decoder_lifecycle_requirements_modeled", 0),
        "unknown_signature_route_count": status_counts.get("unknown_signature_identification_lifecycle_requirements_modeled", 0),
        "structured_routing_route_count": (
            status_counts.get("misrouted_image_structural_routing_lifecycle_requirements_modeled", 0)
            + status_counts.get("misrouted_property_list_routing_lifecycle_requirements_modeled", 0)
        ),
        "sensitive_decoder_route_count": sum(1 for row in signals if row["sensitive_route"]),
        "sanitization": {
            "source_files_read": False,
            "payloads_decoded": False,
            "raw_text_copied": False,
            "raw_payload_bytes_copied": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
            "training_payload_created": False,
        },
    }

    common.write_jsonl(run_dir / "text-decoder-followup-signals.jsonl", signals)
    common.write_jsonl(run_dir / "text-decoder-followup-cases.jsonl", cases)
    common.write_jsonl(run_dir / "text-decoder-followup-controls.jsonl", controls)
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
    parser.add_argument("--run-id", default="directory-text-decoder-followup-batch-20260622")
    parser.add_argument("--source-text-residual-followup-run", default="directory-text-residual-followup-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
