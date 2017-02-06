#!/usr/bin/env python3
"""Append safe residual archive parser and repair coverage.

This pass refines archive backlog records that still need a specialized
container parser or repair flow. It may ask the local archive listing tool for
member names, but it only stores stable ids, counts, extension/kind buckets,
status fields, and controlled tags. It writes no raw source paths, file names,
member names, payload text, domains, provider names, people, brands, or
secrets.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import subprocess
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_archive_batch_knowledge as archive_common
import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


DIRECT_RESIDUAL_STATUSES = {"direct_format_parser_needed", "direct_zip_repair_needed"}


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


def load_targets(output_root: Path, source_archive_backlog_run: str) -> tuple[dict[str, dict], dict[str, dict]]:
    source = output_root / "imports" / source_archive_backlog_run / "archive-backlog-signals.jsonl"
    direct_targets: dict[str, dict] = {}
    nested_targets: dict[str, dict] = {}
    for row in read_jsonl(source):
        if row.get("target_type") == "direct_unlisted_archive" and row.get("backlog_status") in DIRECT_RESIDUAL_STATUSES:
            direct_targets[row["path_hash"]] = row
        elif row.get("target_type") == "nested_archive_member" and row.get("backlog_status") != "nested_zip_listed":
            nested_targets[row["source_nested_member_id"]] = row
    return direct_targets, nested_targets


def split_tool_lines(stdout: bytes, max_members: int) -> tuple[list[str], bool, int]:
    lines = [line.strip() for line in stdout.decode("utf-8", errors="replace").splitlines() if line.strip()]
    total = len(lines)
    return lines[:max_members], total > max_members, total


def tool_exit_bucket(returncode: int | None, timed_out: bool, failed: bool) -> str:
    if timed_out:
        return "timeout"
    if failed:
        return "failed_to_start"
    if returncode == 0:
        return "exit_zero"
    return "exit_nonzero"


def run_archive_lister_path(path: Path, args: argparse.Namespace) -> dict:
    try:
        completed = subprocess.run(
            ["tar.exe", "-tf", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.tool_timeout_seconds,
            check=False,
        )
        names, truncated, total = split_tool_lines(completed.stdout, args.max_members)
        return {
            "names": names,
            "total_stdout_lines": total,
            "stdout_truncated": truncated,
            "exit_bucket": tool_exit_bucket(completed.returncode, False, False),
            "stderr_bucket": "present" if completed.stderr else "empty",
        }
    except subprocess.TimeoutExpired as exc:
        names, truncated, total = split_tool_lines(exc.stdout or b"", args.max_members)
        return {
            "names": names,
            "total_stdout_lines": total,
            "stdout_truncated": truncated,
            "exit_bucket": "timeout",
            "stderr_bucket": "present" if exc.stderr else "empty",
        }
    except Exception:
        return {
            "names": [],
            "total_stdout_lines": 0,
            "stdout_truncated": False,
            "exit_bucket": "failed_to_start",
            "stderr_bucket": "unknown",
        }


def run_archive_lister_bytes(data: bytes, args: argparse.Namespace) -> dict:
    try:
        completed = subprocess.run(
            ["tar.exe", "-tf", "-"],
            input=data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.tool_timeout_seconds,
            check=False,
        )
        names, truncated, total = split_tool_lines(completed.stdout, args.max_members)
        return {
            "names": names,
            "total_stdout_lines": total,
            "stdout_truncated": truncated,
            "exit_bucket": tool_exit_bucket(completed.returncode, False, False),
            "stderr_bucket": "present" if completed.stderr else "empty",
        }
    except subprocess.TimeoutExpired as exc:
        names, truncated, total = split_tool_lines(exc.stdout or b"", args.max_members)
        return {
            "names": names,
            "total_stdout_lines": total,
            "stdout_truncated": truncated,
            "exit_bucket": "timeout",
            "stderr_bucket": "present" if exc.stderr else "empty",
        }
    except Exception:
        return {
            "names": [],
            "total_stdout_lines": 0,
            "stdout_truncated": False,
            "exit_bucket": "failed_to_start",
            "stderr_bucket": "unknown",
        }


def residual_member_tags(ext: str, kind: str, depth: str, is_dir: bool) -> list[str]:
    tags = archive_common.member_structure_tags(ext, -1, depth, is_dir)
    tags.append("residual_archive_member")
    if kind == "archive_bundle":
        tags.append("nested_container_seen_in_residual_listing")
    return sorted(set(tags))


def build_residual_member(
    name: str,
    ordinal: int,
    signal_id: str,
    source_target_id: str,
    target_type: str,
) -> dict:
    ext = archive_common.member_extension(name)
    kind = directory_common.file_kind(ext)
    depth = archive_common.path_depth(name)
    is_dir = name.endswith("/") or name.endswith("\\")
    domain_tags, problem_tags = archive_common.classify_member(name, ext)
    return {
        "archive_residual_member_id": "archiveresmember-" + common.stable_hash(f"{signal_id}\0{ordinal}\0{name}", 16),
        "archive_residual_signal_id": signal_id,
        "source_archive_backlog_signal_id": source_target_id,
        "target_type": target_type,
        "member_ordinal_bucket": text_common.bucket_count(ordinal + 1),
        "extension": ext,
        "kind": kind,
        "is_directory": is_dir,
        "size_bucket": "unknown",
        "compressed_size_bucket": "unknown",
        "path_depth_bucket": depth,
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "structure_tags": residual_member_tags(ext, kind, depth, is_dir),
        "sensitive_flags": archive_common.member_sensitive_flags(name, ext),
    }


def status_from_tool(target_type: str, prior_status: str, ext: str, tool: dict) -> str:
    names = tool["names"]
    exit_bucket = tool["exit_bucket"]
    if names and prior_status == "direct_zip_repair_needed":
        return "direct_zip_partial_listing_added" if exit_bucket != "exit_zero" else "direct_zip_listing_added"
    if names and target_type == "nested_archive_member":
        return "nested_archive_partial_listing_added" if exit_bucket != "exit_zero" else "nested_archive_listing_added"
    if names:
        return "direct_format_partial_listing_added" if exit_bucket != "exit_zero" else "direct_format_listing_added"
    if ext in {"7z", "rar"}:
        return f"{target_type.split('_', 1)[0]}_format_parser_unavailable"
    if "zip" in prior_status:
        return f"{target_type.split('_', 1)[0]}_zip_repair_probe_unlisted"
    if exit_bucket == "timeout":
        return f"{target_type.split('_', 1)[0]}_archive_lister_timeout"
    return f"{target_type.split('_', 1)[0]}_archive_lister_unlisted"


def residual_tags(target_type: str, ext: str, prior_status: str, residual_status: str, member_count: int) -> list[str]:
    tags = [
        "archive_residual_probe",
        f"target_{target_type}",
        f"extension_{ext}",
        f"prior_{prior_status.split(':', 1)[0]}",
        f"residual_{residual_status}",
    ]
    if member_count:
        tags.append("member_composition_added")
    if "partial_listing_added" in residual_status:
        tags.append("partial_repair_inventory_added")
    if "parser_unavailable" in residual_status:
        tags.append("external_parser_capability_missing")
    if "repair_probe_unlisted" in residual_status:
        tags.append("repair_probe_retained_without_members")
    return sorted(set(tags))


def build_signal_from_tool(
    prior: dict,
    target_type: str,
    source_integrity: dict,
    tool: dict,
    members: list[dict],
    ext: str,
    size_bucket: str,
    period: str,
) -> dict:
    source_id = prior["archive_backlog_signal_id"]
    signal_id = "archiveresidual-" + common.stable_hash(f"{target_type}\0{source_id}")
    prior_status = str(prior.get("backlog_status") or "")
    residual_status = status_from_tool(target_type, prior_status, ext, tool)
    kind_counter = collections.Counter(member["kind"] for member in members)
    ext_counter = collections.Counter(member["extension"] for member in members)
    domain_counter = collections.Counter(tag for member in members for tag in member["domain_tags"])
    problem_counter = collections.Counter(tag for member in members for tag in member["problem_tags"])
    domain_tags = list(dict.fromkeys(list(prior.get("domain_tags") or []) + [tag for tag, _ in domain_counter.most_common(6)]))
    problem_tags = list(dict.fromkeys(list(prior.get("problem_tags") or []) + [tag for tag, _ in problem_counter.most_common(6)]))
    sensitive_flags = sorted(set(list(prior.get("sensitive_flags") or []) + [flag for member in members for flag in member["sensitive_flags"]]))
    signal = {
        "archive_residual_signal_id": signal_id,
        "case_id": "",
        "source_archive_backlog_signal_id": source_id,
        "target_type": target_type,
        "extension": ext,
        "top_group_hash": prior.get("top_group_hash", ""),
        "period": period,
        "size_bucket": size_bucket,
        "prior_backlog_status": prior_status,
        "residual_status": residual_status,
        "member_count_observed": tool["total_stdout_lines"],
        "members_written": len(members),
        "listing_truncated": bool(tool["stdout_truncated"]),
        "listing_confidence": "complete_tool_listing" if tool["exit_bucket"] == "exit_zero" else "partial_or_failed_tool_listing",
        "tool_family": "system_archive_lister",
        "tool_exit_bucket": tool["exit_bucket"],
        "tool_stderr_bucket": tool["stderr_bucket"],
        "member_kind_counts": dict(kind_counter.most_common(20)),
        "member_extension_counts": dict(ext_counter.most_common(40)),
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "archive_residual_tags": residual_tags(target_type, ext, prior_status, residual_status, tool["total_stdout_lines"]),
        "sensitive_flags": sensitive_flags,
        "source_integrity": source_integrity,
    }
    if target_type == "direct_unlisted_archive":
        signal["archive_id"] = prior.get("archive_id", "")
        signal["path_hash"] = prior.get("path_hash", "")
    else:
        signal["outer_archive_id"] = prior.get("outer_archive_id", "")
        signal["source_nested_member_id"] = prior.get("source_nested_member_id", "")
        signal["compressed_size_bucket"] = prior.get("compressed_size_bucket", "unknown")
    return signal


def build_unmatched_signal(prior: dict, target_type: str) -> dict:
    source_id = prior["archive_backlog_signal_id"]
    signal_id = "archiveresidual-" + common.stable_hash(f"{target_type}\0{source_id}")
    ext = str(prior.get("extension") or "unknown")
    status_prefix = target_type.split("_", 1)[0]
    signal = {
        "archive_residual_signal_id": signal_id,
        "case_id": "",
        "source_archive_backlog_signal_id": source_id,
        "target_type": target_type,
        "extension": ext,
        "top_group_hash": prior.get("top_group_hash", ""),
        "period": prior.get("period", "unknown"),
        "size_bucket": prior.get("size_bucket", "unknown"),
        "prior_backlog_status": prior.get("backlog_status", ""),
        "residual_status": f"{status_prefix}_source_target_unmatched",
        "member_count_observed": 0,
        "members_written": 0,
        "listing_truncated": False,
        "listing_confidence": "unmatched_source_target",
        "tool_family": "system_archive_lister",
        "tool_exit_bucket": "not_run",
        "tool_stderr_bucket": "not_run",
        "member_kind_counts": {},
        "member_extension_counts": {},
        "domain_tags": prior.get("domain_tags", []),
        "problem_tags": prior.get("problem_tags", []),
        "archive_residual_tags": residual_tags(target_type, ext, str(prior.get("backlog_status") or ""), f"{status_prefix}_source_target_unmatched", 0),
        "sensitive_flags": prior.get("sensitive_flags", []),
        "source_integrity": prior.get("source_integrity", {}),
    }
    if target_type == "direct_unlisted_archive":
        signal["archive_id"] = prior.get("archive_id", "")
        signal["path_hash"] = prior.get("path_hash", "")
    else:
        signal["outer_archive_id"] = prior.get("outer_archive_id", "")
        signal["source_nested_member_id"] = prior.get("source_nested_member_id", "")
        signal["compressed_size_bucket"] = prior.get("compressed_size_bucket", "unknown")
    return signal


def build_cases(signals: list[dict], members: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal.get("top_group_hash") or "group-" + common.stable_hash("unknown")].append(signal)
    members_by_signal: dict[str, list[dict]] = collections.defaultdict(list)
    for member in members:
        members_by_signal[member["archive_residual_signal_id"]].append(member)

    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        status_counter = collections.Counter(row["residual_status"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        tag_counter = collections.Counter(tag for row in rows for tag in row["archive_residual_tags"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        member_kind_counter: collections.Counter[str] = collections.Counter()
        member_ext_counter: collections.Counter[str] = collections.Counter()
        for signal in rows:
            member_kind_counter.update(signal.get("member_kind_counts") or {})
            member_ext_counter.update(signal.get("member_extension_counts") or {})
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "archive_residual_retained"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        implications = [
            "Archive residual evidence should remain traceable even when a complete parser is not available.",
        ]
        if tag_counter.get("partial_repair_inventory_added", 0):
            implications.append("Damaged container repair can still recover useful composition counts for support and migration planning.")
        if tag_counter.get("external_parser_capability_missing", 0):
            implications.append("Unsupported container families need a vetted parser capability before member-level context can be complete.")
        if member_kind_counter.get("document", 0) or member_kind_counter.get("text_or_code", 0):
            implications.append("Recovered archive composition may point to configuration, document, and migration evidence without exposing content.")
        case = {
            "case_id": "archiveresidualcase-" + common.stable_hash(group_hash),
            "case_type": "archive_residual_repair_or_parser_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "member_signal_count": sum(len(members_by_signal[row["archive_residual_signal_id"]]) for row in rows),
            "archive_residual_status_counts": dict(status_counter.most_common()),
            "archive_extension_counts": dict(ext_counter.most_common()),
            "member_kind_counts": dict(member_kind_counter.most_common(20)),
            "member_extension_counts": dict(member_ext_counter.most_common(30)),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "archive_residual_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_archive_residual_signal_ids": [row["archive_residual_signal_id"] for row in rows[:50]],
            "evidence_archive_residual_signal_id_count": len(rows),
            "summary": (
                f"An archive residual cluster preserved {primary_domain.replace('_', ' ')} context; "
                f"the dominant residual state is {primary_status.replace('_', ' ')} across "
                f"{len(rows)} anonymized archive targets."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for archive repair, migration evidence handling, parser capability planning, "
                "and customer-facing reingest guidance without quoting names or payloads."
            ),
        }
        cases.append(case)
        for row in rows:
            row["case_id"] = case["case_id"]
        for member in members:
            if member["archive_residual_signal_id"] in {row["archive_residual_signal_id"] for row in rows}:
                member["case_id"] = case["case_id"]
    return cases


def markdown_counter(counter: collections.Counter[str], label: str) -> str:
    if not counter:
        return "_No rows._"
    rows = [{"value": key, "count": count} for key, count in counter.most_common()]
    headers = ["value", "count"]
    lines = [f"| {label} | count |", "| --- | ---: |"]
    for row in rows:
        lines.append(f"| `{row['value']}` | {row['count']} |")
    return "\n".join(lines)


def write_coverage(run_dir: Path, manifest: dict, signals: list[dict], members: list[dict]) -> None:
    status_counts = counter_from_rows(signals, "residual_status")
    extension_counts = counter_from_rows(signals, "extension")
    member_kind_counts = counter_from_rows(members, "kind")
    body = f"""# Archive Residual Coverage

- Source kind: directory archive residual batch
- Source archive backlog run: `{manifest["source_archive_backlog_run"]}`
- Source residual targets: {manifest["source_target_signal_count"]}
- Residual signals written: {manifest["signals_written"]}
- Residual member signals written: {manifest["member_signals_written"]}
- Archive residual cases: {manifest["archive_residual_case_count"]}
- Direct zip repair targets with partial listings: {manifest["direct_zip_partial_listing_count"]}
- Direct format parser unavailable targets: {manifest["direct_format_parser_unavailable_count"]}
- Nested targets still unlisted after probe: {manifest["nested_targets_unlisted_after_probe"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Residual Status Counts

{markdown_counter(status_counts, "status")}

## Archive Extension Counts

{markdown_counter(extension_counts, "extension")}

## Recovered Member Kind Counts

{markdown_counter(member_kind_counts, "kind")}

## Safety Notes

- Raw source paths, archive names, member names, payload text, domains, brands,
  providers, people, and secrets are not written.
- Member names from the local archive lister are used only in memory to derive
  stable ids and controlled extension/kind/depth buckets.
- Partial listings from damaged containers are retained as evidence, not as a
  guarantee that the container was fully recovered.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "archive-residual-context.md").write_text(
        "# Archive Residual Context\n\n"
        "This run refines archive backlog targets that still needed parser or repair handling. "
        "It records partial repair inventory where the local archive lister could recover "
        "member composition, and preserves explicit parser-capability gaps where it could not. "
        "It does not store source paths, archive names, member names, payload text, domains, "
        "provider names, people, brands, or secrets.\n\n"
        "Agent usage:\n\n"
        "- Use `archive-residual-cases.jsonl` for parser-capability and damaged-container situations.\n"
        "- Use `archive-residual-signals.jsonl` for residual status, stable ids, and composition counts.\n"
        "- Use `archive-residual-members.jsonl` only for anonymized extension/kind/depth buckets.\n"
        "- Treat partial repair listings as useful composition evidence, not complete payload recovery.\n",
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
    if kind == "directory_media_batch":
        return f"directory media batch, {manifest.get('signals_written', 0)} media/design signals, {manifest.get('media_case_count', 0)} media cases"
    if kind == "directory_media_backlog_batch":
        return (
            f"directory media backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
            f"{manifest.get('media_backlog_case_count', 0)} media backlog cases"
        )
    if kind == "directory_database_index_batch":
        return (
            f"directory database/index batch, {manifest.get('signals_written', 0)} metadata signals, "
            f"{manifest.get('database_index_case_count', 0)} database/index cases"
        )
    if kind == "directory_credential_artifact_batch":
        return (
            f"directory credential artifact batch, {manifest.get('signals_written', 0)} marker-only signals, "
            f"{manifest.get('credential_artifact_case_count', 0)} credential cases"
        )
    if kind == "directory_binary_batch":
        return (
            f"directory binary batch, {manifest.get('signals_written', 0)} binary/database signals, "
            f"{manifest.get('binary_case_count', 0)} binary cases"
        )
    return f"{kind or run_id} import"


def refresh_readme(output_root: Path) -> None:
    runs: list[str] = []
    imports_root = output_root / "imports"
    for manifest_path in sorted(imports_root.glob("*/manifest.json")):
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


def process_direct(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> tuple[dict, list[dict]]:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = str(prior.get("extension") or directory_common.safe_extension(path))
    tool = run_archive_lister_path(path, args)
    signal_id = "archiveresidual-" + common.stable_hash(f"direct_unlisted_archive\0{prior['archive_backlog_signal_id']}")
    members = [
        build_residual_member(name, ordinal, signal_id, prior["archive_backlog_signal_id"], "direct_unlisted_archive")
        for ordinal, name in enumerate(tool["names"])
    ]
    signal = build_signal_from_tool(
        prior,
        "direct_unlisted_archive",
        directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
        tool,
        members,
        ext,
        archive_common.bucket_bytes(path.stat().st_size),
        directory_common.period_from_mtime(path),
    )
    return signal, members


def process_nested(
    outer_path: Path,
    source_root: Path,
    outer_relpath: str,
    outer_archive_id: str,
    info: zipfile.ZipInfo,
    outer_archive: zipfile.ZipFile,
    prior: dict,
    args: argparse.Namespace,
) -> tuple[dict, list[dict]]:
    ext = str(prior.get("extension") or archive_common.member_extension(info.filename))
    size = int(getattr(info, "file_size", 0) or 0)
    if size > args.max_nested_archive_bytes:
        tool = {
            "names": [],
            "total_stdout_lines": 0,
            "stdout_truncated": False,
            "exit_bucket": "not_run_too_large",
            "stderr_bucket": "not_run",
        }
    else:
        try:
            data = outer_archive.read(info)
            tool = run_archive_lister_bytes(data, args)
        except Exception:
            tool = {
                "names": [],
                "total_stdout_lines": 0,
                "stdout_truncated": False,
                "exit_bucket": "nested_read_failed",
                "stderr_bucket": "unknown",
            }
    signal_id = "archiveresidual-" + common.stable_hash(f"nested_archive_member\0{prior['archive_backlog_signal_id']}")
    members = [
        build_residual_member(name, ordinal, signal_id, prior["archive_backlog_signal_id"], "nested_archive_member")
        for ordinal, name in enumerate(tool["names"])
    ]
    signal = build_signal_from_tool(
        prior,
        "nested_archive_member",
        directory_common.digest_file(outer_path, outer_relpath, args.full_hash_max_bytes, args.metadata_only_hash),
        tool,
        members,
        ext,
        archive_common.bucket_bytes(size),
        directory_common.period_from_mtime(outer_path),
    )
    signal["outer_archive_id"] = outer_archive_id
    return signal, members


def run(args: argparse.Namespace) -> Path:
    source_root = Path(args.source).resolve()
    output_root = Path(args.output).resolve()
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    direct_targets, nested_targets = load_targets(output_root, args.source_archive_backlog_run)
    pending_direct = dict(direct_targets)
    pending_nested = dict(nested_targets)
    outer_ids = {row.get("outer_archive_id") for row in nested_targets.values()}

    signals: list[dict] = []
    members: list[dict] = []
    scanned = 0
    for path in source_root.rglob("*"):
        if not path.is_file():
            continue
        scanned += 1
        relpath = directory_common.normalized_relpath(path, source_root)
        path_hash = common.stable_hash(relpath, 24)
        if path_hash in pending_direct:
            prior = pending_direct.pop(path_hash)
            signal, signal_members = process_direct(path, source_root, prior, args)
            signals.append(signal)
            members.extend(signal_members)

        archive_id = "archive-" + common.stable_hash(relpath)
        if archive_id in outer_ids:
            outer_pending = {
                member_id: row
                for member_id, row in pending_nested.items()
                if row.get("outer_archive_id") == archive_id
            }
            if outer_pending:
                try:
                    with zipfile.ZipFile(path) as outer_archive:
                        for info in outer_archive.infolist():
                            member_id = "member-" + common.stable_hash(f"{relpath}\0{info.filename}", 16)
                            if member_id not in outer_pending:
                                continue
                            prior = pending_nested.pop(member_id)
                            signal, signal_members = process_nested(
                                path,
                                source_root,
                                relpath,
                                archive_id,
                                info,
                                outer_archive,
                                prior,
                                args,
                            )
                            signals.append(signal)
                            members.extend(signal_members)
                except Exception:
                    for member_id, prior in list(outer_pending.items()):
                        pending_nested.pop(member_id, None)
                        signal = build_unmatched_signal(prior, "nested_archive_member")
                        signal["residual_status"] = "nested_outer_archive_read_failed"
                        signal["archive_residual_tags"] = residual_tags(
                            "nested_archive_member",
                            signal["extension"],
                            str(prior.get("backlog_status") or ""),
                            "nested_outer_archive_read_failed",
                            0,
                        )
                        signals.append(signal)

        if args.progress_every and scanned % args.progress_every == 0:
            print(f"progress files_scanned={scanned} signals={len(signals)} members={len(members)}", flush=True)

    for prior in pending_direct.values():
        signals.append(build_unmatched_signal(prior, "direct_unlisted_archive"))
    for prior in pending_nested.values():
        signals.append(build_unmatched_signal(prior, "nested_archive_member"))

    signals.sort(key=lambda row: row["archive_residual_signal_id"])
    members.sort(key=lambda row: row["archive_residual_member_id"])
    cases = build_cases(signals, members)
    cases.sort(key=lambda row: row["case_id"])

    status_counts = counter_from_rows(signals, "residual_status")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_archive_residual_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_archive_backlog_run": args.source_archive_backlog_run,
        "source_target_signal_count": len(direct_targets) + len(nested_targets),
        "source_direct_target_signal_count": len(direct_targets),
        "source_nested_target_signal_count": len(nested_targets),
        "signals_written": len(signals),
        "member_signals_written": len(members),
        "archive_residual_case_count": len(cases),
        "direct_targets_matched": len(direct_targets) - len(pending_direct),
        "nested_targets_matched": len(nested_targets) - len(pending_nested),
        "direct_zip_partial_listing_count": status_counts.get("direct_zip_partial_listing_added", 0),
        "direct_format_parser_unavailable_count": status_counts.get("direct_format_parser_unavailable", 0),
        "nested_targets_unlisted_after_probe": sum(
            count for status, count in status_counts.items() if status.startswith("nested_") and "listing_added" not in status
        ),
        "status_counts": dict(status_counts.most_common()),
        "max_members": args.max_members,
        "max_nested_archive_bytes": args.max_nested_archive_bytes,
        "tool_family": "system_archive_lister",
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_archive_names_copied": False,
            "raw_member_names_copied": False,
            "raw_payload_text_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
            "archive_payloads_extracted_to_disk": False,
        },
    }

    common.write_jsonl(run_dir / "archive-residual-signals.jsonl", signals)
    common.write_jsonl(run_dir / "archive-residual-members.jsonl", members)
    common.write_jsonl(run_dir / "archive-residual-cases.jsonl", cases)
    write_context(run_dir)

    issues = common.scan_forbidden(output_root)
    manifest["privacy_hit_count"] = len(issues)
    (run_dir / "privacy-scan.json").write_text(
        json.dumps({"hit_count": len(issues), "issues": issues}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_coverage(run_dir, manifest, signals, members)
    refresh_readme(output_root)
    return run_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", default="knowledge-context")
    parser.add_argument("--run-id", default="directory-archive-residual-batch")
    parser.add_argument("--source-archive-backlog-run", default="directory-archive-backlog-batch-20260622")
    parser.add_argument("--max-members", type=int, default=100_000)
    parser.add_argument("--max-nested-archive-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--tool-timeout-seconds", type=int, default=30)
    parser.add_argument("--full-hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--metadata-only-hash", action="store_true", default=True)
    parser.add_argument("--progress-every", type=int, default=1000)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
