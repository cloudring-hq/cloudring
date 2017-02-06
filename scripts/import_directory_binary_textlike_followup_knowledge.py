#!/usr/bin/env python3
"""Append derived follow-up handling for binary text-like metadata queues.

This pass reads only the previous decoded-metadata binary text-like run. It
does not read source files and does not copy raw decoded text, source paths,
file names, domains, provider names, people, brands, vendors, or secrets.
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
    "raw_text_exclusion": "exclude raw decoded text from stored context, prompts, and training payloads",
    "secret_aware_review": "route sensitive decoded-metadata artifacts through secret-aware review before deeper handling",
    "credential_marker_routing": "keep credential-like text marker-only and route to secret lifecycle controls",
    "chunked_redacted_ingestion": "require deduplicated and redacted chunk ingestion before any content summarization",
    "large_artifact_sampling_policy": "separate representative sampling from full artifact ingestion for large text-like binaries",
    "redaction_marker_accounting": "preserve redaction/count buckets as audit evidence without reconstructing text",
    "configuration_residue_modeling": "treat code/config-shaped binary text as operational residue and migration evidence",
    "training_payload_gate": "require explicit approval before using any decoded metadata as model-training source",
    "support_traceability": "preserve stable ids and status buckets for support handoff without exposing content",
    "retention_minimization": "retain only metadata buckets and derived requirements unless a safer decoder is proven",
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
    status = row.get("decode_status")
    return (
        bool(row.get("sensitive_flags"))
        or bool(row.get("decode_truncated"))
        or status == "credential_text_excluded_marker_only"
        or status == "large_textlike_binary_chunk_decoded"
    )


def followup_status(row: dict) -> str:
    status = row.get("decode_status")
    truncated = bool(row.get("decode_truncated"))
    sensitive = bool(row.get("sensitive_flags"))
    if status == "credential_text_excluded_marker_only":
        return "credential_marker_followup_modeled"
    if sensitive and truncated:
        return "sensitive_chunked_followup_modeled"
    if sensitive:
        return "sensitive_counts_only_followup_modeled"
    if status == "large_textlike_binary_chunk_decoded" or truncated:
        return "large_chunked_followup_modeled"
    return "binary_textlike_followup_modeled"


def route(row: dict, status: str) -> str:
    if status == "credential_marker_followup_modeled":
        return "credential_marker_secret_lifecycle_route"
    if status == "sensitive_chunked_followup_modeled":
        return "secret_aware_chunked_decoder_gate"
    if status == "sensitive_counts_only_followup_modeled":
        return "secret_aware_counts_only_review"
    if status == "large_chunked_followup_modeled":
        return "redacted_large_artifact_chunk_review"
    return "metadata_only_textlike_review"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "raw_text_exclusion",
        "redaction_marker_accounting",
        "training_payload_gate",
        "support_traceability",
        "retention_minimization",
    }
    if status == "credential_marker_followup_modeled":
        controls.update({"credential_marker_routing", "secret_aware_review"})
    if status in {"sensitive_chunked_followup_modeled", "sensitive_counts_only_followup_modeled"}:
        controls.add("secret_aware_review")
    if "chunked" in status or row.get("decode_truncated"):
        controls.update({"chunked_redacted_ingestion", "large_artifact_sampling_policy"})
    structure_tags = set(row.get("structure_tags") or [])
    if {
        "code_like_shape",
        "has_config_shape",
        "has_script_or_code",
        "key_value_shape",
        "json_like_shape",
        "markup_like_shape",
    } & structure_tags:
        controls.add("configuration_residue_modeling")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if status == "credential_marker_followup_modeled":
        return "credential_text_payload_risk"
    if status == "sensitive_chunked_followup_modeled":
        return "sensitive_large_textlike_binary_risk"
    if status == "sensitive_counts_only_followup_modeled":
        return "sensitive_textlike_binary_risk"
    if status == "large_chunked_followup_modeled":
        return "large_textlike_binary_ingestion_risk"
    return "metadata_only_textlike_binary_risk"


def sensitive_route(row: dict, status: str) -> bool:
    return bool(row.get("sensitive_flags")) or status == "credential_marker_followup_modeled"


def followup_tags(row: dict, status: str, decoder_route: str, controls: list[str], risk: str) -> list[str]:
    tags = [
        "binary_textlike_followup_reviewed",
        "derived_from_decoded_metadata_only",
        "not_training_payload",
        f"followup_status_{status}",
        f"decoder_route_{decoder_route}",
        f"risk_{risk}",
        f"decode_status_{row.get('decode_status', 'unknown')}",
        f"decode_mode_{row.get('decode_mode', 'unknown')}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("structure_tags") or []:
        if source_tag in {
            "decode_truncated",
            "sensitive_source_signal",
            "content_sensitive_source_signal",
            "path_sensitive_source_signal",
            "credential_or_license_text_excluded",
            "code_like_shape",
            "has_config_shape",
            "key_value_shape",
            "json_like_shape",
            "markup_like_shape",
        }:
            tags.append(f"source_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        if not is_followup_target(row):
            continue
        status = followup_status(row)
        decoder_route = route(row, status)
        controls = required_controls(row, status)
        risk = risk_bucket(row, status)
        is_sensitive_route = sensitive_route(row, status)
        flags = set(row.get("sensitive_flags") or [])
        if is_sensitive_route:
            flags.add("binary_textlike_secret_aware_followup_route")
        signals.append(
            {
                "binary_textlike_followup_signal_id": "binarytextfollow-" + common.stable_hash(row["binary_textlike_signal_id"]),
                "case_id": "",
                "source_binary_textlike_signal_id": row["binary_textlike_signal_id"],
                "source_binary_signal_id": row.get("source_binary_signal_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "kind": row.get("kind", "unknown"),
                "byte_profile": row.get("byte_profile", "unknown"),
                "entropy_bucket": row.get("entropy_bucket", "unknown"),
                "size_bucket": row.get("size_bucket", "unknown"),
                "language_hint": row.get("language_hint", "unknown"),
                "decode_mode": row.get("decode_mode", "unknown"),
                "decode_status": row.get("decode_status", "unknown"),
                "decode_truncated": bool(row.get("decode_truncated")),
                "stat_buckets": row.get("stat_buckets", {}),
                "followup_status": status,
                "decoder_route": decoder_route,
                "risk_bucket": risk,
                "required_controls": controls,
                "sensitive_route": is_sensitive_route,
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "text_signal_tags": row.get("text_signal_tags", []),
                "binary_textlike_followup_tags": followup_tags(row, status, decoder_route, controls, risk),
                "sensitive_flags": sorted(flags),
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
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["binary_textlike_followup_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "binary_textlike_followup_modeled"
        implications = [
            "Use text-like binary evidence as metadata-only context unless a redacted decoder gate is proven.",
            "Do not treat counts-only or chunked decoded metadata as a raw text corpus.",
        ]
        if control_counter.get("secret_aware_review", 0):
            implications.append("Sensitive text-like binaries require secret-aware review before deeper summarization or training use.")
        if control_counter.get("credential_marker_routing", 0):
            implications.append("Credential-like text should stay marker-only and flow into secret lifecycle controls.")
        if control_counter.get("chunked_redacted_ingestion", 0):
            implications.append("Large chunked artifacts need deduplication, redaction, and sampling policy before any content ingestion.")
        case = {
            "case_id": "binarytextfollowcase-" + common.stable_hash(key),
            "case_type": "binary_textlike_followup_handling_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "chunked_signal_count": sum(1 for row in rows if row["decode_truncated"]),
            "followup_status_counts": dict(status_counter.most_common()),
            "decoder_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "binary_textlike_followup_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_binary_textlike_followup_signal_ids": [row["binary_textlike_followup_signal_id"] for row in rows[:50]],
            "evidence_binary_textlike_followup_signal_id_count": len(rows),
            "summary": (
                f"A binary text-like follow-up cluster modeled {primary_status.replace('_', ' ')} "
                f"across {len(rows)} decoded-metadata signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for secret-aware review, chunked ingestion policy, migration residue handling, "
                "and training-payload gates without copying or reconstructing decoded text."
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
                "binary_textlike_followup_control_id": "binarytextcontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "chunked_signal_count": sum(1 for row in rows if row["decode_truncated"]),
                "followup_status_counts": dict(status_counter.most_common()),
                "decoder_route_counts": dict(route_counter.most_common()),
                "evidence_binary_textlike_followup_signal_ids": [
                    row["binary_textlike_followup_signal_id"] for row in rows[:50]
                ],
                "agent_use": "Use as a decoded-metadata safety checkpoint, not as decoded text.",
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
    body = f"""# Binary Text-Like Follow-Up Coverage

- Source kind: directory binary text-like follow-up batch
- Source binary text-like run: `{manifest["source_binary_textlike_run"]}`
- Source follow-up targets: {manifest["source_followup_target_signal_count"]}
- Follow-up signals written: {manifest["signals_written"]}
- Follow-up cases: {manifest["binary_textlike_followup_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Sensitive follow-up signals: {manifest["sensitive_followup_signal_count"]}
- Chunked follow-up signals: {manifest["chunked_followup_signal_count"]}
- Credential-marker follow-up signals: {manifest["credential_marker_followup_signal_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Follow-Up Status Counts

{markdown_counter(status_counts, "followup_status")}

## Decoder Route Counts

{markdown_counter(route_counts, "decoder_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over decoded-metadata records.
- It does not read source files and does not copy raw decoded text, paths,
  names, domains, providers, people, brands, vendors, or secrets.
- Use these records for secret-aware handling, redacted chunk policy, and
  training-payload gates, not as text content.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "binary-textlike-followup-context.md").write_text(
        "# Binary Text-Like Follow-Up Context\n\n"
        "This run derives safe follow-up handling from decoded-metadata records for text-like binary artifacts. "
        "It preserves evidence that cloud platforms encounter sensitive, credential-like, and large chunked "
        "text-shaped residues, while keeping raw decoded text out of stored context.\n\n"
        "Agent usage:\n\n"
        "- Use `binary-textlike-followup-cases.jsonl` for secret-aware and chunked-ingestion product situations.\n"
        "- Use `binary-textlike-followup-signals.jsonl` for stable ids, follow-up statuses, decoder routes, and risk buckets.\n"
        "- Use `binary-textlike-followup-controls.jsonl` as a safety checklist before any deeper text-like binary ingestion.\n"
        "- Never treat this layer as decoded text or reconstruct content from counters.\n",
        encoding="utf-8",
    )


def summarize_manifest(run_id: str, manifest: dict) -> str:
    kind = manifest.get("source_kind")
    if kind == "legacy_mail_archive":
        return (
            f"legacy mail archive import, {manifest.get('parsed_messages', 0)} parsed messages, "
            f"{manifest.get('case_count', 0)} derived cases, {manifest.get('attachments_referenced', 0)} referenced attachments"
        )
    if kind == "directory_snapshot":
        return (
            f"directory snapshot import, {manifest.get('files_indexed', 0)} indexed files, "
            f"{manifest.get('directory_case_count', 0)} derived directory cases"
        )
    if kind == "directory_text_batch":
        return f"directory text batch, {manifest.get('signals_written', 0)} text signals, {manifest.get('text_case_count', 0)} text cases"
    if kind == "directory_text_backlog_batch":
        return (
            f"directory text backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
            f"{manifest.get('text_backlog_case_count', 0)} backlog cases"
        )
    if kind == "directory_text_residual_batch":
        return (
            f"directory text residual batch, {manifest.get('signals_written', 0)} residual signals, "
            f"{manifest.get('text_residual_case_count', 0)} residual cases"
        )
    if kind == "directory_binary_textlike_batch":
        return (
            f"directory binary text-like batch, {manifest.get('signals_written', 0)} decoded-metadata signals, "
            f"{manifest.get('binary_textlike_case_count', 0)} binary text-like cases"
        )
    if kind == "directory_binary_textlike_followup_batch":
        return (
            f"directory binary text-like follow-up batch, {manifest.get('signals_written', 0)} follow-up signals, "
            f"{manifest.get('control_requirement_count', 0)} control requirements, "
            f"{manifest.get('binary_textlike_followup_case_count', 0)} follow-up cases"
        )
    if kind == "directory_document_batch":
        return f"directory document batch, {manifest.get('signals_written', 0)} document signals, {manifest.get('document_case_count', 0)} document cases"
    if kind == "directory_document_backlog_batch":
        return (
            f"directory document backlog batch, {manifest.get('signals_written', 0)} document backlog signals, "
            f"{manifest.get('document_backlog_case_count', 0)} document backlog cases"
        )
    if kind == "directory_archive_batch":
        return (
            f"directory archive batch, {manifest.get('signals_written', 0)} archive signals, "
            f"{manifest.get('member_signals_written', 0)} anonymized member signals, "
            f"{manifest.get('archive_case_count', 0)} archive cases"
        )
    if kind == "directory_archive_backlog_batch":
        return (
            f"directory archive backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
            f"{manifest.get('member_signals_written', 0)} recursive member signals, "
            f"{manifest.get('archive_backlog_case_count', 0)} backlog cases"
        )
    if kind == "directory_archive_residual_batch":
        return (
            f"directory archive residual batch, {manifest.get('signals_written', 0)} residual signals, "
            f"{manifest.get('member_signals_written', 0)} repaired member signals, "
            f"{manifest.get('archive_residual_case_count', 0)} residual cases"
        )
    if kind == "directory_database_index_batch":
        return (
            f"directory database/index batch, {manifest.get('signals_written', 0)} metadata signals, "
            f"{manifest.get('database_index_case_count', 0)} database/index cases"
        )
    if kind == "directory_database_index_residual_batch":
        return (
            f"directory database/index residual batch, {manifest.get('signals_written', 0)} residual signals, "
            f"{manifest.get('control_requirement_count', 0)} control requirements, "
            f"{manifest.get('database_index_residual_case_count', 0)} residual cases"
        )
    if kind == "directory_credential_artifact_batch":
        return (
            f"directory credential artifact batch, {manifest.get('signals_written', 0)} marker-only signals, "
            f"{manifest.get('credential_artifact_case_count', 0)} credential cases"
        )
    if kind == "directory_credential_lifecycle_batch":
        return (
            f"directory credential lifecycle batch, {manifest.get('signals_written', 0)} lifecycle signals, "
            f"{manifest.get('control_requirement_count', 0)} control requirements, "
            f"{manifest.get('credential_lifecycle_case_count', 0)} lifecycle cases"
        )
    if kind == "directory_media_batch":
        return f"directory media batch, {manifest.get('signals_written', 0)} media/design signals, {manifest.get('media_case_count', 0)} media cases"
    if kind == "directory_media_backlog_batch":
        return (
            f"directory media backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
            f"{manifest.get('media_backlog_case_count', 0)} media backlog cases"
        )
    if kind == "directory_binary_batch":
        return (
            f"directory binary batch, {manifest.get('signals_written', 0)} binary/database signals, "
            f"{manifest.get('binary_case_count', 0)} binary cases"
        )
    return f"{kind or run_id} import"


def refresh_readme(output_root: Path) -> None:
    runs: list[str] = []
    for manifest_path in sorted((output_root / "imports").glob("*/manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        run_id = manifest_path.parent.name
        runs.append(f"- `{run_id}`: {summarize_manifest(run_id, manifest)}.")
    body = "\n".join(
        [
            "# Knowledge Context",
            "",
            "This folder is append-only context for future cloud-platform agents. It stores",
            "anonymized experience records, derived cases, and coverage reports. Raw source",
            "messages, source paths, addresses, domains, company names, product names,",
            "provider names, and secrets are intentionally not copied here.",
            "",
            "Current source runs:",
            "",
            *runs,
            "",
            "Usage rule for agents: prefer `cloud-experience-context.md` and per-run",
            "`*-context.md` files for principles, then retrieve JSONL case files for",
            "traceable anonymized evidence.",
            "",
            "Coverage/backlog rule: read `coverage-backlog.md` before planning new",
            "extractors so unsupported artifacts are refined instead of ignored.",
            "",
        ]
    )
    (output_root / "README.md").write_text(body, encoding="utf-8")


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_binary_textlike_run / "binary-textlike-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["binary_textlike_followup_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    status_counts = counter_from_rows(signals, "followup_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_binary_textlike_followup_batch",
        "source_binary_textlike_run": args.source_binary_textlike_run,
        "source_signal_count": len(source_rows),
        "source_followup_target_signal_count": len(signals),
        "signals_written": len(signals),
        "binary_textlike_followup_case_count": len(cases),
        "control_requirement_count": len(controls),
        "sensitive_followup_signal_count": sum(1 for row in signals if row["sensitive_route"]),
        "chunked_followup_signal_count": sum(1 for row in signals if row["decode_truncated"]),
        "credential_marker_followup_signal_count": status_counts.get("credential_marker_followup_modeled", 0),
        "non_sensitive_chunked_signal_count": status_counts.get("large_chunked_followup_modeled", 0),
        "sanitization": {
            "source_files_read": False,
            "raw_decoded_text_copied": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_domains_urls_people_brands_or_vendors_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
        },
    }

    common.write_jsonl(run_dir / "binary-textlike-followup-signals.jsonl", signals)
    common.write_jsonl(run_dir / "binary-textlike-followup-cases.jsonl", cases)
    common.write_jsonl(run_dir / "binary-textlike-followup-controls.jsonl", controls)
    write_context(run_dir)

    issues = common.scan_forbidden(output_root)
    manifest["privacy_hit_count"] = len(issues)
    (run_dir / "privacy-scan.json").write_text(
        json.dumps({"hit_count": len(issues), "issues": issues}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_coverage(run_dir, manifest, signals)
    refresh_readme(output_root)
    return run_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="knowledge-context")
    parser.add_argument("--run-id", default="directory-binary-textlike-followup-batch")
    parser.add_argument("--source-binary-textlike-run", default="directory-binary-textlike-batch-20260622-02")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
