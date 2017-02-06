#!/usr/bin/env python3
"""Append derived follow-up handling for text residual special decoder queues.

This pass reads only the previous text-residual metadata run. It does not open
source files and does not copy raw text, decoded payload, source paths, file
names, domains, provider names, people, brands, vendors, or secrets.
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


TARGET_STATUSES = {
    "mixed_binary_text_candidate_retained",
    "unknown_binary_residual_retained",
    "misrouted_structured_artifact_identified",
}

CONTROL_REQUIREMENTS = {
    "raw_text_exclusion": "exclude raw text and decoded payload from stored context and training payloads",
    "payload_export_block": "do not export payload bytes while routing residual artifacts",
    "metadata_only_inventory": "preserve magic family, byte-shape, size, and status buckets as inventory evidence",
    "special_decoder_sandbox": "run any future decoder in a bounded sandbox with no raw payload export",
    "signature_identification": "identify unknown signatures before attempting content interpretation",
    "mixed_binary_text_gate": "treat mixed printable artifacts as special-decoder candidates, not safe text",
    "structured_artifact_routing": "route misrouted structured artifacts to the correct structural pipeline",
    "visual_or_design_route": "route image-like structured artifacts to visual/design handling without OCR by default",
    "property_list_route": "route binary property-list artifacts to metadata-only structured parsing",
    "training_payload_gate": "require explicit approval before any residual-derived content enters model training",
    "support_traceability": "preserve stable ids and status buckets for support handoff without exposing content",
    "retention_minimization": "retain only derived metadata unless a safer decoder is proven",
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


def is_followup_target(row: dict) -> bool:
    return row.get("residual_status") in TARGET_STATUSES


def followup_status(row: dict) -> str:
    status = row.get("residual_status")
    family = row.get("magic_family")
    if status == "mixed_binary_text_candidate_retained":
        return "mixed_printable_special_decoder_requirements_modeled"
    if status == "unknown_binary_residual_retained":
        return "unknown_signature_identification_requirements_modeled"
    if family == "image_signature":
        return "misrouted_image_structural_route_modeled"
    if family == "binary_property_list":
        return "misrouted_property_list_route_modeled"
    return "misrouted_structured_artifact_route_modeled"


def decoder_route(status: str) -> str:
    if status == "mixed_printable_special_decoder_requirements_modeled":
        return "bounded_mixed_binary_text_decoder_gate"
    if status == "unknown_signature_identification_requirements_modeled":
        return "signature_identification_before_decoder"
    if status == "misrouted_image_structural_route_modeled":
        return "visual_design_structural_route"
    if status == "misrouted_property_list_route_modeled":
        return "property_list_metadata_route"
    return "structured_artifact_metadata_route"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "raw_text_exclusion",
        "payload_export_block",
        "metadata_only_inventory",
        "special_decoder_sandbox",
        "training_payload_gate",
        "support_traceability",
        "retention_minimization",
    }
    if status == "mixed_printable_special_decoder_requirements_modeled":
        controls.add("mixed_binary_text_gate")
    if status == "unknown_signature_identification_requirements_modeled":
        controls.add("signature_identification")
    if status.startswith("misrouted_"):
        controls.add("structured_artifact_routing")
    if status == "misrouted_image_structural_route_modeled":
        controls.add("visual_or_design_route")
    if status == "misrouted_property_list_route_modeled":
        controls.add("property_list_route")
    return sorted(controls)


def risk_bucket(status: str) -> str:
    if status == "mixed_printable_special_decoder_requirements_modeled":
        return "mixed_binary_text_decoder_risk"
    if status == "unknown_signature_identification_requirements_modeled":
        return "unknown_binary_signature_risk"
    if status == "misrouted_image_structural_route_modeled":
        return "misrouted_visual_artifact_risk"
    if status == "misrouted_property_list_route_modeled":
        return "misrouted_structured_metadata_risk"
    return "misrouted_structured_artifact_risk"


def followup_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    tags = [
        "text_residual_followup_reviewed",
        "derived_from_byte_shape_metadata_only",
        "not_training_payload",
        f"followup_status_{status}",
        f"decoder_route_{route}",
        f"risk_{risk}",
        f"magic_{row.get('magic_family', 'unknown')}",
        f"source_residual_status_{row.get('residual_status', 'unknown')}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("text_residual_tags") or []:
        if source_tag in {
            "possible_special_decoder_candidate",
            "structured_artifact_misrouted_from_text",
            "not_text_like_after_sample_pass",
            "sensitive_source_signal",
        }:
            tags.append(f"source_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        if not is_followup_target(row):
            continue
        status = followup_status(row)
        route = decoder_route(status)
        controls = required_controls(row, status)
        risk = risk_bucket(status)
        signals.append(
            {
                "text_residual_followup_signal_id": "textresfollow-" + common.stable_hash(row["text_residual_signal_id"]),
                "case_id": "",
                "source_text_residual_signal_id": row["text_residual_signal_id"],
                "source_text_backlog_signal_id": row.get("source_text_backlog_signal_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "kind": row.get("kind", "unknown"),
                "magic_family": row.get("magic_family", "unknown"),
                "byte_shape_buckets": row.get("byte_shape_buckets", {}),
                "entropy_bucket": row.get("entropy_bucket", "unknown"),
                "size_bucket": row.get("size_bucket", "unknown"),
                "prior_text_backlog_status": row.get("prior_text_backlog_status", "unknown"),
                "source_residual_status": row.get("residual_status", "unknown"),
                "followup_status": status,
                "decoder_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "text_residual_followup_tags": followup_tags(row, status, route, controls, risk),
                "sensitive_flags": row.get("sensitive_flags", []),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['followup_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["followup_status"] for row in rows)
        route_counter = collections.Counter(row["decoder_route"] for row in rows)
        magic_counter = collections.Counter(row["magic_family"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["text_residual_followup_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "text_residual_followup_modeled"
        implications = [
            "Treat special text residual candidates as metadata-only routing evidence, not as decoded text.",
            "Future decoder work must preserve raw-text and payload-export exclusion unless a separate safe path is proven.",
        ]
        if control_counter.get("mixed_binary_text_gate", 0):
            implications.append("Mixed printable artifacts need a bounded special decoder gate before any text interpretation.")
        if control_counter.get("signature_identification", 0):
            implications.append("Unknown signatures should be identified before parser or content assumptions are made.")
        if control_counter.get("structured_artifact_routing", 0):
            implications.append("Misrouted structured artifacts should move to the correct structural pipeline rather than text ingestion.")
        case = {
            "case_id": "textresfollowcase-" + common.stable_hash(key),
            "case_type": "text_residual_followup_handling_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "followup_status_counts": dict(status_counter.most_common()),
            "decoder_route_counts": dict(route_counter.most_common()),
            "magic_family_counts": dict(magic_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "text_residual_followup_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_text_residual_followup_signal_ids": [row["text_residual_followup_signal_id"] for row in rows[:50]],
            "evidence_text_residual_followup_signal_id_count": len(rows),
            "summary": (
                f"A text residual follow-up cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} byte-shape metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for special decoder, signature-identification, and structured-routing planning "
                "without copying raw text or payload bytes."
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
        status_counter = collections.Counter(row["followup_status"] for row in rows)
        route_counter = collections.Counter(row["decoder_route"] for row in rows)
        controls.append(
            {
                "text_residual_followup_control_id": "textrescontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "followup_status_counts": dict(status_counter.most_common()),
                "decoder_route_counts": dict(route_counter.most_common()),
                "evidence_text_residual_followup_signal_ids": [
                    row["text_residual_followup_signal_id"] for row in rows[:50]
                ],
                "agent_use": "Use as a text residual safety checkpoint, not as decoded text.",
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
    status_counts = counter_from_rows(signals, "followup_status")
    route_counts = counter_from_rows(signals, "decoder_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Text Residual Follow-Up Coverage

- Source kind: directory text residual follow-up batch
- Source text residual run: `{manifest["source_text_residual_run"]}`
- Source follow-up targets: {manifest["source_followup_target_signal_count"]}
- Follow-up signals written: {manifest["signals_written"]}
- Follow-up cases: {manifest["text_residual_followup_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Mixed printable candidates: {manifest["mixed_printable_followup_count"]}
- Unknown signature candidates: {manifest["unknown_signature_followup_count"]}
- Misrouted structured artifacts: {manifest["misrouted_structured_followup_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Follow-Up Status Counts

{markdown_counter(status_counts, "followup_status")}

## Decoder Route Counts

{markdown_counter(route_counts, "decoder_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over byte-shape and magic-family metadata.
- It does not read source files or copy raw text, decoded payload, paths,
  names, domains, providers, people, brands, vendors, or secrets.
- Use these records for special decoder and routing planning, not as text.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "text-residual-followup-context.md").write_text(
        "# Text Residual Follow-Up Context\n\n"
        "This run derives safe follow-up handling from text residual byte-shape metadata. "
        "It separates mixed printable candidates, unknown binary signatures, and misrouted structured artifacts "
        "without reading source files or decoding payloads.\n\n"
        "Agent usage:\n\n"
        "- Use `text-residual-followup-cases.jsonl` for special decoder and routing product situations.\n"
        "- Use `text-residual-followup-signals.jsonl` for stable ids, follow-up statuses, decoder routes, and risk buckets.\n"
        "- Use `text-residual-followup-controls.jsonl` as a safety checklist before any residual decoder work.\n"
        "- Never treat this layer as decoded text or reconstruct payload from byte-shape buckets.\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_text_residual_run / "text-residual-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["text_residual_followup_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    status_counts = counter_from_rows(signals, "followup_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_text_residual_followup_batch",
        "source_text_residual_run": args.source_text_residual_run,
        "source_signal_count": len(source_rows),
        "source_followup_target_signal_count": len(signals),
        "signals_written": len(signals),
        "text_residual_followup_case_count": len(cases),
        "control_requirement_count": len(controls),
        "mixed_printable_followup_count": status_counts.get("mixed_printable_special_decoder_requirements_modeled", 0),
        "unknown_signature_followup_count": status_counts.get("unknown_signature_identification_requirements_modeled", 0),
        "misrouted_structured_followup_count": (
            status_counts.get("misrouted_image_structural_route_modeled", 0)
            + status_counts.get("misrouted_property_list_route_modeled", 0)
            + status_counts.get("misrouted_structured_artifact_route_modeled", 0)
        ),
        "sanitization": {
            "source_files_read": False,
            "raw_text_copied": False,
            "raw_payload_bytes_copied": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
        },
    }

    common.write_jsonl(run_dir / "text-residual-followup-signals.jsonl", signals)
    common.write_jsonl(run_dir / "text-residual-followup-cases.jsonl", cases)
    common.write_jsonl(run_dir / "text-residual-followup-controls.jsonl", controls)
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
    parser.add_argument("--run-id", default="directory-text-residual-followup-batch")
    parser.add_argument("--source-text-residual-run", default="directory-text-residual-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
