#!/usr/bin/env python3
"""Append derived deep-processing controls for media/design backlog queues.

This pass reads only the media-backlog structural metadata run. It does not
open source media/design files, run OCR, transcribe audio, fetch references,
copy EXIF text, copy visual text, copy transcripts, copy source names, copy
paths, copy URLs, or store domains, provider names, people, brands, vendors,
or secrets.
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
    "raw_ocr_text_exclusion": "exclude raw OCR text from stored context and training payloads",
    "raw_transcript_exclusion": "exclude raw transcripts and speech text from stored context",
    "raw_audio_text_exclusion": "exclude raw audio-derived text until redacted review is complete",
    "raw_visual_text_exclusion": "exclude raw visual text from images, slides, frames, and design assets",
    "raw_exif_text_exclusion": "exclude EXIF, comment, and author metadata values",
    "source_name_path_exclusion": "exclude raw source names and paths from agent context",
    "url_domain_exclusion": "exclude raw URLs and domains from retained external-reference context",
    "structure_bucket_traceability": "preserve stable ids, media families, status buckets, and count buckets as evidence",
    "training_payload_review_gate": "require a separate review before derived media summaries become model-training material",
    "retention_minimization": "retain only the smallest useful structural and route evidence",
    "support_traceability": "retain stable evidence ids for support handoff without exposing payload content",
    "transcription_redaction_gate": "allow audio transcription only through bounded redaction and speaker review",
    "speaker_identity_exclusion": "avoid storing speaker names, voices, or identities from recordings",
    "video_frame_ocr_gate": "gate video frames and screen text through redacted OCR or visual review",
    "audio_track_transcription_gate": "gate video audio tracks through redacted transcription review",
    "visual_identity_exclusion": "avoid storing face, badge, screen, or personal visual identifiers",
    "design_layer_text_gate": "gate design-layer text through redacted parser review",
    "design_source_parser_sandbox": "run design-source parsers in a bounded sandbox with no payload export",
    "embedded_asset_name_exclusion": "avoid copying embedded asset names, layer names, and package member names",
    "font_name_table_value_exclusion": "avoid copying font name-table values, author fields, and embedded labels",
    "font_embedding_rights_review": "treat font embedding and reuse evidence as a rights-review requirement",
    "vector_text_redaction_gate": "gate vector text and print marks through redacted review",
    "print_graphic_ocr_gate": "gate print and raster graphics through redacted OCR or visual inspection",
    "package_member_name_exclusion": "avoid copying package member names from media/design bundles",
    "package_parser_sandbox": "run package parser work in a bounded sandbox with no payload export",
    "external_reference_non_fetch_default": "default to metadata-only handling for external references unless a safe fetch workflow exists",
    "parser_capability_vetting": "vet specialized media/design parsers before using them on retained generic formats",
    "sample_truncation_confidence_guard": "treat truncated probes as incomplete structural evidence until deeper safe processing",
    "sensitive_media_route": "route sensitive media/design records through secret-aware handling before deeper processing",
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


def deep_status(row: dict) -> str:
    media_type = str(row.get("media_type") or "")
    media_family = str(row.get("media_family") or "")
    probe_status = str(row.get("probe_status") or "")
    if probe_status == "generic_media_backlog_retained":
        return "generic_media_parser_triage_requirements_modeled"
    if media_type == "audio_recording":
        return "audio_transcription_redaction_requirements_modeled"
    if media_type == "video_recording":
        return "video_transcription_and_visual_review_requirements_modeled"
    if media_type == "font_asset" or media_family == "font_asset":
        return "font_asset_review_requirements_modeled"
    if media_type == "design_source":
        return "design_source_parser_redaction_requirements_modeled"
    if media_type in {"vector_or_print_graphic", "raster_image"}:
        return "visual_ocr_review_requirements_modeled"
    if media_type == "package_or_binary_media":
        return "media_package_parser_requirements_modeled"
    if media_type == "web_reference" or media_family == "external_reference":
        return "external_reference_metadata_only_requirements_modeled"
    return "media_deep_processing_requirements_modeled"


def deep_route(status: str) -> str:
    if status == "generic_media_parser_triage_requirements_modeled":
        return "generic_media_parser_triage_route"
    if status == "audio_transcription_redaction_requirements_modeled":
        return "audio_transcription_redaction_route"
    if status == "video_transcription_and_visual_review_requirements_modeled":
        return "video_transcription_visual_ocr_route"
    if status == "font_asset_review_requirements_modeled":
        return "font_asset_embedding_review_route"
    if status == "design_source_parser_redaction_requirements_modeled":
        return "design_source_parser_redaction_route"
    if status == "visual_ocr_review_requirements_modeled":
        return "visual_ocr_redaction_route"
    if status == "media_package_parser_requirements_modeled":
        return "media_package_parser_sandbox_route"
    if status == "external_reference_metadata_only_requirements_modeled":
        return "external_reference_metadata_only_route"
    return "media_deep_processing_triage_route"


def deep_readiness(status: str) -> str:
    if status == "generic_media_parser_triage_requirements_modeled":
        return "parser_triage_required_before_deep_processing"
    if status == "external_reference_metadata_only_requirements_modeled":
        return "safe_fetch_workflow_required_before_reference_content"
    return "redacted_review_required_before_content_use"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "raw_ocr_text_exclusion",
        "raw_transcript_exclusion",
        "raw_audio_text_exclusion",
        "raw_visual_text_exclusion",
        "raw_exif_text_exclusion",
        "source_name_path_exclusion",
        "url_domain_exclusion",
        "structure_bucket_traceability",
        "training_payload_review_gate",
        "retention_minimization",
        "support_traceability",
    }
    if status == "generic_media_parser_triage_requirements_modeled":
        controls.update({"parser_capability_vetting", "design_source_parser_sandbox"})
    if status == "audio_transcription_redaction_requirements_modeled":
        controls.update({"transcription_redaction_gate", "speaker_identity_exclusion"})
    if status == "video_transcription_and_visual_review_requirements_modeled":
        controls.update({"video_frame_ocr_gate", "audio_track_transcription_gate", "visual_identity_exclusion"})
    if status == "design_source_parser_redaction_requirements_modeled":
        controls.update({"design_layer_text_gate", "design_source_parser_sandbox", "embedded_asset_name_exclusion"})
    if status == "font_asset_review_requirements_modeled":
        controls.update({"font_name_table_value_exclusion", "font_embedding_rights_review"})
    if status == "visual_ocr_review_requirements_modeled":
        controls.update({"vector_text_redaction_gate", "print_graphic_ocr_gate", "visual_identity_exclusion"})
    if status == "media_package_parser_requirements_modeled":
        controls.update({"package_member_name_exclusion", "package_parser_sandbox", "embedded_asset_name_exclusion"})
    if status == "external_reference_metadata_only_requirements_modeled":
        controls.update({"external_reference_non_fetch_default", "url_domain_exclusion"})
    if bool(row.get("probe_sample_truncated")):
        controls.add("sample_truncation_confidence_guard")
    if row.get("sensitive_flags"):
        controls.add("sensitive_media_route")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if row.get("sensitive_flags"):
        return "sensitive_media_deep_processing_risk"
    if status == "generic_media_parser_triage_requirements_modeled":
        return "generic_media_parser_gap_risk"
    if status == "video_transcription_and_visual_review_requirements_modeled":
        return "video_audio_visual_privacy_risk"
    if status == "audio_transcription_redaction_requirements_modeled":
        return "audio_speech_privacy_risk"
    if status == "design_source_parser_redaction_requirements_modeled":
        return "design_source_layer_text_risk"
    if status == "font_asset_review_requirements_modeled":
        return "font_metadata_and_rights_risk"
    if status == "visual_ocr_review_requirements_modeled":
        return "visual_text_and_identity_risk"
    if status == "external_reference_metadata_only_requirements_modeled":
        return "external_reference_fetch_risk"
    return "media_deep_processing_risk"


def deep_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    tags = [
        "media_deep_followup_reviewed",
        "derived_from_structural_metadata_only",
        "not_training_payload",
        f"media_deep_status_{status}",
        f"media_deep_readiness_{deep_readiness(status)}",
        f"media_deep_route_{route}",
        f"risk_{risk}",
        f"extension_{row.get('extension', 'unknown')}",
        f"media_type_{row.get('media_type', 'unknown')}",
        f"media_family_{row.get('media_family', 'unknown')}",
        f"probe_status_{row.get('probe_status', 'unknown')}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("media_backlog_tags") or []:
        if source_tag in {
            "generic_media_backlog_retained",
            "probe_sample_truncated",
            "iso_media_boxes_counted",
            "riff_audio_counted",
            "sfnt_font_header_counted",
            "zip_package_structure_counted",
            "print_graphic_markers_counted",
            "vector_sample_markers_counted",
        }:
            tags.append(f"source_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        status = deep_status(row)
        route = deep_route(status)
        controls = required_controls(row, status)
        risk = risk_bucket(row, status)
        signals.append(
            {
                "media_deep_followup_signal_id": "mediadeep-" + common.stable_hash(row["media_backlog_signal_id"]),
                "case_id": "",
                "source_media_backlog_signal_id": row["media_backlog_signal_id"],
                "source_media_signal_id": row.get("source_media_signal_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "media_type": row.get("media_type", "unknown"),
                "media_family": row.get("media_family", "unknown"),
                "prior_analysis_status": row.get("prior_analysis_status", "unknown"),
                "probe_status": row.get("probe_status", "unknown"),
                "probe_sample_truncated": bool(row.get("probe_sample_truncated", False)),
                "size_bucket": row.get("size_bucket", "unknown"),
                "structure_count_buckets": row.get("structure_count_buckets", {}),
                "structure_property_buckets": row.get("structure_property_buckets", {}),
                "media_deep_status": status,
                "media_deep_readiness": deep_readiness(status),
                "media_deep_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "media_deep_followup_tags": deep_tags(row, status, route, controls, risk),
                "sensitive_flags": row.get("sensitive_flags", []),
                "sensitive_route": bool(row.get("sensitive_flags")),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['media_deep_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["media_deep_status"] for row in rows)
        route_counter = collections.Counter(row["media_deep_route"] for row in rows)
        readiness_counter = collections.Counter(row["media_deep_readiness"] for row in rows)
        media_type_counter = collections.Counter(row["media_type"] for row in rows)
        family_counter = collections.Counter(row["media_family"] for row in rows)
        extension_counter = collections.Counter(row["extension"] for row in rows)
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["media_deep_followup_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "media_deep_followup_modeled"
        implications = [
            "Treat media/design backlog as durable evidence for support, product history, demos, training, and migration planning.",
            "Do not convert visual, speech, or design-layer evidence into content or training material without redaction gates.",
        ]
        if control_counter.get("transcription_redaction_gate", 0) or control_counter.get("audio_track_transcription_gate", 0):
            implications.append("Audio and video recordings need transcription redaction and speaker-identity exclusion.")
        if control_counter.get("video_frame_ocr_gate", 0) or control_counter.get("print_graphic_ocr_gate", 0):
            implications.append("Video frames and graphics need redacted OCR or visual review before summarization.")
        if control_counter.get("design_source_parser_sandbox", 0):
            implications.append("Design source files need sandboxed parsers and layer-text redaction.")
        if control_counter.get("font_embedding_rights_review", 0):
            implications.append("Font assets need metadata-value exclusion and embedding-rights review.")
        if control_counter.get("parser_capability_vetting", 0):
            implications.append("Generic retained media requires vetted parser triage before deep processing.")
        if control_counter.get("sensitive_media_route", 0):
            implications.append("Sensitive media/design records require secret-aware routing before deeper processing.")
        case = {
            "case_id": "mediadeepcase-" + common.stable_hash(key),
            "case_type": "media_deep_followup_handling_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
            "media_type_counts": dict(media_type_counter.most_common()),
            "media_family_counts": dict(family_counter.most_common()),
            "extension_counts": dict(extension_counter.most_common()),
            "media_deep_status_counts": dict(status_counter.most_common()),
            "media_deep_readiness_counts": dict(readiness_counter.most_common()),
            "media_deep_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "media_deep_followup_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_media_deep_followup_signal_ids": [row["media_deep_followup_signal_id"] for row in rows[:50]],
            "evidence_media_deep_followup_signal_id_count": len(rows),
            "summary": (
                f"A media/design deep follow-up cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} structural metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for redacted OCR, transcription, design parser, font review, package parser, "
                "and media triage planning without copying visual text, speech text, source names, or payload content."
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
        status_counter = collections.Counter(row["media_deep_status"] for row in rows)
        route_counter = collections.Counter(row["media_deep_route"] for row in rows)
        controls.append(
            {
                "media_deep_followup_control_id": "mediadeepcontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
                "media_deep_status_counts": dict(status_counter.most_common()),
                "media_deep_route_counts": dict(route_counter.most_common()),
                "evidence_media_deep_followup_signal_ids": [row["media_deep_followup_signal_id"] for row in rows[:50]],
                "agent_use": "Use as a media/design processing checkpoint, not as OCR, transcript, visual text, or payload content.",
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
    status_counts = counter_from_rows(signals, "media_deep_status")
    route_counts = counter_from_rows(signals, "media_deep_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Media Deep Followup Coverage

- Source kind: directory media deep followup batch
- Source media backlog run: `{manifest["source_media_backlog_run"]}`
- Source backlog signals: {manifest["source_signal_count"]}
- Followup signals written: {manifest["signals_written"]}
- Followup cases: {manifest["media_deep_followup_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Audio transcription routes: {manifest["audio_transcription_route_count"]}
- Video visual/transcription routes: {manifest["video_visual_transcription_route_count"]}
- Design parser routes: {manifest["design_parser_route_count"]}
- Font review routes: {manifest["font_review_route_count"]}
- Generic parser triage routes: {manifest["generic_parser_triage_route_count"]}
- Sensitive followup routes: {manifest["sensitive_followup_route_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Deep Status Counts

{markdown_counter(status_counts, "media_deep_status")}

## Deep Route Counts

{markdown_counter(route_counts, "media_deep_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over media/design structural metadata records.
- It does not run OCR, transcribe audio, fetch references, copy visual text,
  copy speech text, copy EXIF text, copy source names, copy paths, copy URLs,
  or store domains, providers, people, brands, vendors, or secrets.
- Use these records for media/design processing routes and controls, not as
  OCR output, transcript output, design-layer text, or training material.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "media-deep-followup-context.md").write_text(
        "# Media Deep Followup Context\n\n"
        "This run derives safe deep-processing routes from media/design backlog records. "
        "It separates audio transcription, video visual review, design-source parsing, "
        "font review, visual OCR, package parsing, external-reference handling, and generic "
        "parser triage while keeping OCR text, transcripts, visual text, EXIF text, source "
        "names, paths, URLs, and domains out of stored context.\n\n"
        "Agent usage:\n\n"
        "- Use `media-deep-followup-cases.jsonl` for OCR, transcription, design-parser, font-review, package-parser, and generic media triage situations.\n"
        "- Use `media-deep-followup-signals.jsonl` for stable ids, deep-processing routes, status buckets, and risk buckets.\n"
        "- Use `media-deep-followup-controls.jsonl` as a redaction and parser checklist before summarization or training use.\n"
        "- Never treat this layer as OCR text, transcript text, visual text, design-layer text, EXIF text, source names, URLs, or training payload.\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_media_backlog_run / "media-backlog-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["media_deep_followup_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    status_counts = counter_from_rows(signals, "media_deep_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_media_deep_followup_batch",
        "source_media_backlog_run": args.source_media_backlog_run,
        "source_signal_count": len(source_rows),
        "source_target_signal_count": len(source_rows),
        "signals_written": len(signals),
        "media_deep_followup_case_count": len(cases),
        "control_requirement_count": len(controls),
        "audio_transcription_route_count": status_counts.get("audio_transcription_redaction_requirements_modeled", 0),
        "video_visual_transcription_route_count": status_counts.get("video_transcription_and_visual_review_requirements_modeled", 0),
        "design_parser_route_count": status_counts.get("design_source_parser_redaction_requirements_modeled", 0),
        "font_review_route_count": status_counts.get("font_asset_review_requirements_modeled", 0),
        "generic_parser_triage_route_count": status_counts.get("generic_media_parser_triage_requirements_modeled", 0),
        "sensitive_followup_route_count": sum(1 for row in signals if row["sensitive_route"]),
        "sanitization": {
            "source_media_files_read": False,
            "ocr_run": False,
            "transcription_run": False,
            "external_references_fetched": False,
            "raw_ocr_text_copied": False,
            "raw_transcripts_copied": False,
            "raw_audio_text_copied": False,
            "raw_visual_text_copied": False,
            "raw_exif_text_copied": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_urls_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
            "training_payload_created": False,
        },
    }

    common.write_jsonl(run_dir / "media-deep-followup-signals.jsonl", signals)
    common.write_jsonl(run_dir / "media-deep-followup-cases.jsonl", cases)
    common.write_jsonl(run_dir / "media-deep-followup-controls.jsonl", controls)
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
    parser.add_argument("--run-id", default="directory-media-deep-followup-batch-20260622")
    parser.add_argument("--source-media-backlog-run", default="directory-media-backlog-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
