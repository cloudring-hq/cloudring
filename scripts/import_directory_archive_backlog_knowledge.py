#!/usr/bin/env python3
"""Append safe backlog coverage for failed and nested archive artifacts.

The pass refines archive backlog from a previous archive inventory. It never
extracts payloads to disk and writes no raw paths, file names, member names,
domains, addresses, people, brand names, vendor names, source text, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import io
import json
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


LISTED_ARCHIVE_STATUSES = {"archive_listed", "gzip_stream_indexed"}
ZIP_LIKE_EXTENSIONS = {"zip", "jar", "war", "ear"}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def bucket_bytes(value: int) -> str:
    return archive_common.bucket_bytes(value)


def read_header(path: Path, size: int = 8192) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def magic_family_from_header(header: bytes, ext: str) -> str:
    if header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06") or header.startswith(b"PK\x07\x08"):
        return "zip_container"
    if header.startswith(b"Rar!\x1a\x07"):
        return "rar_container"
    if header.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "seven_z_container"
    if header.startswith(b"\x1f\x8b"):
        return "gzip_stream"
    if len(header) > 265 and header[257:262] in {b"ustar", b"ustar\x00"}:
        return "tar_container"
    if ext == "cab":
        return "cab_container"
    return "unknown_archive_signature"


def direct_backlog_status(prior_status: str, ext: str, magic: str) -> str:
    if "BadZipFile" in prior_status or (ext == "zip" and magic == "zip_container"):
        return "direct_zip_repair_needed"
    if ext in {"rar", "7z"}:
        return "direct_format_parser_needed"
    if prior_status.startswith("archive_list_failed"):
        return "direct_archive_probe_failed"
    return "direct_archive_structured"


def archive_backlog_tags(
    target_type: str,
    ext: str,
    prior_status: str,
    backlog_status: str,
    magic: str,
    member_count: int,
    listed: bool,
) -> list[str]:
    tags = [
        f"target_{target_type}",
        f"extension_{ext}",
        f"prior_{prior_status.split(':', 1)[0]}",
        f"backlog_{backlog_status}",
        f"magic_{magic}",
    ]
    if listed:
        tags.append("recursive_listing_added")
    if member_count:
        tags.append("nested_member_composition_captured")
    if "repair" in backlog_status:
        tags.append("repair_or_reingest_required")
    if "parser" in backlog_status:
        tags.append("specialized_parser_required")
    if "too_large" in backlog_status:
        tags.append("large_nested_archive_retained")
    if "unsupported" in backlog_status:
        tags.append("unsupported_nested_archive_retained")
    return sorted(set(tags))


def classify_signal(parts: list[str]) -> tuple[list[str], list[str]]:
    return common.classify("\n".join(parts))


def build_inner_member(
    info: zipfile.ZipInfo,
    ordinal: int,
    signal_id: str,
    outer_archive_id: str,
    source_nested_member_id: str,
) -> dict:
    ext = archive_common.member_extension(info.filename)
    domain_tags, problem_tags = archive_common.classify_member(info.filename, ext)
    size = int(getattr(info, "file_size", 0) or 0)
    compressed_size = int(getattr(info, "compress_size", 0) or 0)
    is_dir = bool(info.is_dir())
    depth = archive_common.path_depth(info.filename)
    return {
        "archive_backlog_member_id": "archivebacklogmember-"
        + common.stable_hash(f"{outer_archive_id}\0{source_nested_member_id}\0{info.filename}", 16),
        "archive_backlog_signal_id": signal_id,
        "outer_archive_id": outer_archive_id,
        "source_nested_member_id": source_nested_member_id,
        "member_ordinal_bucket": text_common.bucket_count(ordinal + 1),
        "extension": ext,
        "kind": directory_common.file_kind(ext),
        "is_directory": is_dir,
        "size_bucket": bucket_bytes(size),
        "compressed_size_bucket": bucket_bytes(compressed_size),
        "path_depth_bucket": depth,
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "structure_tags": archive_common.member_structure_tags(ext, size, depth, is_dir),
        "sensitive_flags": archive_common.member_sensitive_flags(info.filename, ext),
    }


def list_nested_zip_bytes(
    data: bytes,
    signal_id: str,
    outer_archive_id: str,
    source_nested_member_id: str,
    max_members: int,
) -> tuple[list[dict], dict, str]:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as nested:
            infos = nested.infolist()
            members = [
                build_inner_member(info, ordinal, signal_id, outer_archive_id, source_nested_member_id)
                for ordinal, info in enumerate(infos[:max_members])
            ]
            return (
                members,
                {
                    "member_count": len(infos),
                    "members_written": len(members),
                    "listing_truncated": len(infos) > max_members,
                },
                "nested_zip_listed",
            )
    except Exception as exc:
        return (
            [],
            {"member_count": 0, "members_written": 0, "listing_truncated": False},
            f"nested_zip_list_failed:{type(exc).__name__}",
        )


def load_targets(output_root: Path, source_archive_run: str) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict]]:
    archive_root = output_root / "imports" / source_archive_run
    archive_signals = read_jsonl(archive_root / "archive-signals.jsonl")
    archive_members = read_jsonl(archive_root / "archive-members.jsonl")
    signals_by_archive_id = {row["archive_id"]: row for row in archive_signals}
    direct_targets = {
        row["path_hash"]: row
        for row in archive_signals
        if row.get("listing_status") not in LISTED_ARCHIVE_STATUSES
    }
    nested_targets = {
        row["member_id"]: row
        for row in archive_members
        if row.get("kind") == "archive_bundle" or "nested_archive_member" in row.get("structure_tags", [])
    }
    return direct_targets, nested_targets, signals_by_archive_id


def build_direct_signal(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    size = path.stat().st_size
    try:
        header = read_header(path)
        magic = magic_family_from_header(header, ext)
    except Exception as exc:
        magic = f"header_read_failed:{type(exc).__name__}"
    prior_status = str(prior.get("listing_status") or "")
    backlog_status = direct_backlog_status(prior_status, ext, magic)
    domain_tags, problem_tags = classify_signal([relpath, ext, magic, prior_status, backlog_status])
    flags = archive_common.archive_sensitive_flags(relpath, ext)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    return {
        "archive_backlog_signal_id": "archivebacklog-" + common.stable_hash(f"direct\0{relpath}"),
        "case_id": "",
        "target_type": "direct_unlisted_archive",
        "archive_id": prior.get("archive_id", "archive-" + common.stable_hash(relpath)),
        "path_hash": prior.get("path_hash", common.stable_hash(relpath, 24)),
        "top_group_hash": prior.get("top_group_hash", "group-" + common.stable_hash(top)),
        "extension": ext,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(size),
        "prior_listing_status": prior_status,
        "backlog_status": backlog_status,
        "magic_family": magic,
        "member_count": 0,
        "members_written": 0,
        "listing_truncated": False,
        "domain_tags": list(dict.fromkeys(list(prior.get("domain_tags") or []) + domain_tags)),
        "problem_tags": list(dict.fromkeys(list(prior.get("problem_tags") or []) + problem_tags)),
        "archive_backlog_tags": archive_backlog_tags(
            "direct_unlisted_archive",
            ext,
            prior_status,
            backlog_status,
            magic,
            0,
            False,
        ),
        "sensitive_flags": sorted(set(flags + list(prior.get("sensitive_flags") or []))),
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }


def build_nested_signal(
    outer_path: Path,
    source_root: Path,
    outer_signal: dict,
    prior_member: dict,
    info: zipfile.ZipInfo,
    args: argparse.Namespace,
    outer_archive: zipfile.ZipFile,
) -> tuple[dict, list[dict]]:
    relpath = directory_common.normalized_relpath(outer_path, source_root)
    ext = archive_common.member_extension(info.filename)
    outer_archive_id = str(outer_signal.get("archive_id") or "archive-" + common.stable_hash(relpath))
    source_nested_member_id = str(prior_member["member_id"])
    signal_id = "archivebacklog-" + common.stable_hash(f"nested\0{outer_archive_id}\0{source_nested_member_id}")
    size = int(getattr(info, "file_size", 0) or 0)
    compressed_size = int(getattr(info, "compress_size", 0) or 0)
    members: list[dict] = []
    meta = {"member_count": 0, "members_written": 0, "listing_truncated": False}
    if ext in ZIP_LIKE_EXTENSIONS:
        if size > args.max_nested_archive_bytes:
            backlog_status = "nested_listing_skipped_too_large"
        else:
            try:
                nested_bytes = outer_archive.read(info)
                members, meta, backlog_status = list_nested_zip_bytes(
                    nested_bytes,
                    signal_id,
                    outer_archive_id,
                    source_nested_member_id,
                    args.max_nested_archive_members,
                )
            except Exception as exc:
                backlog_status = f"nested_read_failed:{type(exc).__name__}"
    else:
        backlog_status = "nested_listing_unsupported_format"
    member_domain_counter = collections.Counter(tag for row in members for tag in row["domain_tags"])
    member_problem_counter = collections.Counter(tag for row in members for tag in row["problem_tags"])
    member_kind_counter = collections.Counter(row["kind"] for row in members)
    member_ext_counter = collections.Counter(row["extension"] for row in members)
    domain_tags, problem_tags = classify_signal([relpath, ext, backlog_status, str(prior_member.get("kind") or "")])
    if member_domain_counter:
        domain_tags = list(dict.fromkeys(domain_tags + [tag for tag, _ in member_domain_counter.most_common(6)]))
    if member_problem_counter:
        problem_tags = list(dict.fromkeys(problem_tags + [tag for tag, _ in member_problem_counter.most_common(6)]))
    listed = backlog_status == "nested_zip_listed"
    signal = {
        "archive_backlog_signal_id": signal_id,
        "case_id": "",
        "target_type": "nested_archive_member",
        "outer_archive_id": outer_archive_id,
        "source_nested_member_id": source_nested_member_id,
        "top_group_hash": outer_signal.get("top_group_hash", ""),
        "extension": ext,
        "period": directory_common.period_from_mtime(outer_path),
        "size_bucket": bucket_bytes(size),
        "compressed_size_bucket": bucket_bytes(compressed_size),
        "prior_listing_status": "nested_archive_member",
        "backlog_status": backlog_status,
        "magic_family": "nested_zip_container" if ext in ZIP_LIKE_EXTENSIONS else f"nested_{ext}_container",
        "member_count": meta["member_count"],
        "members_written": meta["members_written"],
        "listing_truncated": meta["listing_truncated"],
        "member_kind_counts": dict(member_kind_counter.most_common(20)),
        "member_extension_counts": dict(member_ext_counter.most_common(40)),
        "domain_tags": list(dict.fromkeys(list(prior_member.get("domain_tags") or []) + domain_tags)),
        "problem_tags": list(dict.fromkeys(list(prior_member.get("problem_tags") or []) + problem_tags)),
        "archive_backlog_tags": archive_backlog_tags(
            "nested_archive_member",
            ext,
            "nested_archive_member",
            backlog_status,
            "nested_zip_container" if ext in ZIP_LIKE_EXTENSIONS else f"nested_{ext}_container",
            meta["member_count"],
            listed,
        ),
        "sensitive_flags": sorted(
            set(list(prior_member.get("sensitive_flags") or []) + [flag for row in members for flag in row["sensitive_flags"]])
        ),
        "source_integrity": directory_common.digest_file(outer_path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }
    return signal, members


def build_archive_backlog_cases(signals: list[dict], members: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"] or "group-" + common.stable_hash("unknown")].append(signal)
    members_by_signal: dict[str, list[dict]] = collections.defaultdict(list)
    for member in members:
        members_by_signal[member["archive_backlog_signal_id"]].append(member)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["archive_backlog_tags"])
        status_counter = collections.Counter(row["backlog_status"] for row in rows)
        target_counter = collections.Counter(row["target_type"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        member_kind_counter: collections.Counter[str] = collections.Counter()
        member_ext_counter: collections.Counter[str] = collections.Counter()
        for row in rows:
            member_kind_counter.update(row.get("member_kind_counts") or {})
            member_ext_counter.update(row.get("member_extension_counts") or {})
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "archive_backlog_retained"
        case = {
            "case_id": "archivebacklogcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "target_type_counts": dict(target_counter.most_common()),
            "extension_counts": dict(ext_counter.most_common(30)),
            "backlog_status_counts": dict(status_counter.most_common()),
            "archive_backlog_tags": [tag for tag, _ in tag_counter.most_common()],
            "member_kind_counts": dict(member_kind_counter.most_common(20)),
            "member_extension_counts": dict(member_ext_counter.most_common(30)),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_archive_backlog_signal_ids": [row["archive_backlog_signal_id"] for row in rows[:50]],
            "evidence_archive_backlog_signal_id_count": len(rows),
            "anonymized_situation": (
                f"An archive backlog cluster preserved {primary_domain.replace('_', ' ')} "
                f"context; the dominant backlog state is {primary_status.replace('_', ' ')} "
                f"and the dominant operational signal is {primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should keep failed, unsupported, and nested archive evidence "
                "traceable so migrations, backups, imports, exports, and delivery bundles are not lost."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if tag_counter.get("recursive_listing_added", 0):
            implications.append("Recursive archive inventory can reveal hidden migration and backup composition without copying member names.")
        if tag_counter.get("specialized_parser_required", 0):
            implications.append("Unsupported archive families should stay queued for vetted parsers that preserve anonymized member-only output.")
        if tag_counter.get("repair_or_reingest_required", 0):
            implications.append("Damaged archive containers need repair-oriented inventory flows and clear customer-facing reingest guidance.")
        if case["sensitive_signal_count"]:
            implications.append("Archive backlog can signal credential or license handling needs; route it through managed secret workflows.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve archive backlog as traceable context and refine it with safer parsers later."
        ]
        cases.append(case)
    case_by_group = {case["top_group_hash"]: case["case_id"] for case in cases}
    for signal in signals:
        group = signal["top_group_hash"] or "group-" + common.stable_hash("unknown")
        signal["case_id"] = case_by_group[group]
    return cases


def counter_from_rows(rows: list[dict], field: str) -> collections.Counter:
    counter: collections.Counter = collections.Counter()
    for row in rows:
        value = row.get(field)
        if isinstance(value, list):
            counter.update(value)
        elif isinstance(value, dict):
            counter.update(value)
        elif value:
            counter[value] += 1
    return counter


def write_docs(output_root: Path, run_dir: Path, manifest: dict, signals: list[dict], cases: list[dict], members: list[dict]) -> None:
    target_counts = counter_from_rows(signals, "target_type")
    status_counts = counter_from_rows(signals, "backlog_status")
    magic_counts = counter_from_rows(signals, "magic_family")
    ext_counts = counter_from_rows(signals, "extension")
    tag_counts = counter_from_rows(signals, "archive_backlog_tags")
    member_ext_counts = counter_from_rows(members, "extension")
    member_kind_counts = counter_from_rows(members, "kind")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Archive Backlog Coverage

- Source kind: directory archive backlog batch
- Source direct unlisted archive targets: {manifest["source_direct_target_signal_count"]}
- Source nested archive targets: {manifest["source_nested_target_member_count"]}
- Direct targets matched: {manifest["direct_targets_matched"]}
- Nested targets matched: {manifest["nested_targets_matched"]}
- Archive backlog signals written: {manifest["signals_written"]}
- Nested member signals written: {manifest["member_signals_written"]}
- Archive backlog cases: {manifest["archive_backlog_case_count"]}
- Direct archives structurally triaged: {manifest["direct_archives_structured"]}
- Direct archives still requiring member parser or repair: {manifest["direct_archives_requiring_member_parser_or_repair"]}
- Nested archives listed: {manifest["nested_archives_listed"]}
- Nested archives not listed: {manifest["nested_archives_not_listed"]}
- Truncated nested listings: {manifest["truncated_nested_listing_count"]}

## Target Types

{common.markdown_table(target_counts, "target_type")}

## Backlog Status

{common.markdown_table(status_counts, "status")}

## Magic Families

{common.markdown_table(magic_counts, "magic_family")}

## Archive Extensions

{common.markdown_table(ext_counts, "extension")}

## Backlog Tags

{common.markdown_table(tag_counts, "tag")}

## Nested Member Kinds

{common.markdown_table(member_kind_counts, "kind")}

## Nested Member Extensions

{common.markdown_table(member_ext_counts, "extension")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "archive-backlog-context.md").write_text(
        "# Directory Archive Backlog Context\n\n"
        "This run refines archive backlog that could not be fully listed in the archive batch. "
        "It adds structural triage for direct failed or unsupported containers and recursively "
        "lists nested zip-like containers in memory, without copying raw paths, file names, "
        "member names, payload text, addresses, domains, people, provider names, brand names, "
        "vendor names, or secrets.\n\n"
        "## Agent Use\n\n"
        "- Use `archive-backlog-cases.jsonl` for failed, unsupported, and nested archive situations.\n"
        "- Use `archive-backlog-signals.jsonl` for stable-id traceability and backlog status.\n"
        "- Use `archive-backlog-members.jsonl` only for anonymized recursive member composition.\n"
        "- Treat direct parser/repair needs and unsupported nested containers as retained queues, not dropped context.\n\n"
        "## Largest Archive Backlog Cases\n\n"
        + "\n".join(
            f"- `{case['case_id']}` ({case['signal_count']} signals): {case['anonymized_situation']}"
            for case in largest_cases
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def refresh_root_readme(output_root: Path) -> None:
    runs: list[str] = []
    for manifest_path in sorted((output_root / "imports").glob("*/manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        run_id = manifest_path.parent.name
        kind = manifest.get("source_kind")
        if kind == "legacy_mail_archive":
            summary = (
                f"legacy mail archive import, {manifest.get('parsed_messages', 0)} parsed messages, "
                f"{manifest.get('case_count', 0)} derived cases, "
                f"{manifest.get('attachments_referenced', 0)} referenced attachments"
            )
        elif kind == "directory_snapshot":
            summary = (
                f"directory snapshot import, {manifest.get('files_indexed', 0)} indexed files, "
                f"{manifest.get('directory_case_count', 0)} derived directory cases"
            )
        elif kind == "directory_text_batch":
            summary = (
                f"directory text batch, {manifest.get('signals_written', 0)} text signals, "
                f"{manifest.get('text_case_count', 0)} text cases"
            )
        elif kind == "directory_text_backlog_batch":
            summary = (
                f"directory text backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
                f"{manifest.get('text_backlog_case_count', 0)} backlog cases"
            )
        elif kind == "directory_document_batch":
            summary = (
                f"directory document batch, {manifest.get('signals_written', 0)} document signals, "
                f"{manifest.get('document_case_count', 0)} document cases"
            )
        elif kind == "directory_document_backlog_batch":
            summary = (
                f"directory document backlog batch, {manifest.get('signals_written', 0)} document backlog signals, "
                f"{manifest.get('document_backlog_case_count', 0)} document backlog cases"
            )
        elif kind == "directory_archive_batch":
            summary = (
                f"directory archive batch, {manifest.get('signals_written', 0)} archive signals, "
                f"{manifest.get('member_signals_written', 0)} anonymized member signals, "
                f"{manifest.get('archive_case_count', 0)} archive cases"
            )
        elif kind == "directory_archive_backlog_batch":
            summary = (
                f"directory archive backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
                f"{manifest.get('member_signals_written', 0)} recursive member signals, "
                f"{manifest.get('archive_backlog_case_count', 0)} backlog cases"
            )
        elif kind == "directory_media_batch":
            summary = (
                f"directory media batch, {manifest.get('signals_written', 0)} media/design signals, "
                f"{manifest.get('media_case_count', 0)} media cases"
            )
        elif kind == "directory_binary_batch":
            summary = (
                f"directory binary batch, {manifest.get('signals_written', 0)} binary/database signals, "
                f"{manifest.get('binary_case_count', 0)} binary cases"
            )
        else:
            summary = f"{kind or 'source'} import"
        runs.append(f"- `{run_id}`: {summary}.")
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
    (output_root / "README.md").write_text(body, encoding="utf-8", newline="\n")


def run_import(args: argparse.Namespace) -> Path:
    source_root = Path(args.source).resolve()
    output_root = Path(args.output).resolve()
    run_dir = common.append_only_run_dir(output_root / "imports", args.run_id)
    run_dir.mkdir(parents=True)
    direct_targets, nested_targets, signals_by_archive_id = load_targets(output_root, args.source_archive_run)
    direct_matched: set[str] = set()
    nested_matched: set[str] = set()
    signals: list[dict] = []
    members: list[dict] = []
    outer_archive_ids = {row.get("archive_id") for row in nested_targets.values()}
    scanned_archives = 0
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        ext = directory_common.safe_extension(path)
        if ext not in archive_common.ARCHIVE_EXTENSIONS and directory_common.file_kind(ext) != "archive_bundle":
            continue
        scanned_archives += 1
        relpath = directory_common.normalized_relpath(path, source_root)
        path_hash = common.stable_hash(relpath, 24)
        archive_id = "archive-" + common.stable_hash(relpath)
        prior_direct = direct_targets.get(path_hash)
        if prior_direct is not None:
            direct_matched.add(path_hash)
            signals.append(build_direct_signal(path, source_root, prior_direct, args))
        if archive_id in outer_archive_ids and ext in ZIP_LIKE_EXTENSIONS:
            targets_for_outer = {
                member_id: row
                for member_id, row in nested_targets.items()
                if row.get("archive_id") == archive_id and member_id not in nested_matched
            }
            if targets_for_outer:
                try:
                    with zipfile.ZipFile(path) as outer_archive:
                        for info in outer_archive.infolist():
                            member_id = "member-" + common.stable_hash(f"{relpath}\0{info.filename}", 16)
                            prior_member = targets_for_outer.get(member_id)
                            if prior_member is None:
                                continue
                            nested_matched.add(member_id)
                            signal, inner_members = build_nested_signal(
                                path,
                                source_root,
                                signals_by_archive_id.get(archive_id, {"archive_id": archive_id}),
                                prior_member,
                                info,
                                args,
                                outer_archive,
                            )
                            signals.append(signal)
                            members.extend(inner_members)
                except Exception as exc:
                    for member_id, prior_member in targets_for_outer.items():
                        nested_matched.add(member_id)
                        outer_signal = signals_by_archive_id.get(archive_id, {"archive_id": archive_id})
                        signal_id = "archivebacklog-" + common.stable_hash(f"nested\0{archive_id}\0{member_id}")
                        signal = {
                            "archive_backlog_signal_id": signal_id,
                            "case_id": "",
                            "target_type": "nested_archive_member",
                            "outer_archive_id": archive_id,
                            "source_nested_member_id": member_id,
                            "top_group_hash": outer_signal.get("top_group_hash", ""),
                            "extension": str(prior_member.get("extension") or "custom_ext"),
                            "period": directory_common.period_from_mtime(path),
                            "size_bucket": str(prior_member.get("size_bucket") or "unknown"),
                            "compressed_size_bucket": str(prior_member.get("compressed_size_bucket") or "unknown"),
                            "prior_listing_status": "nested_archive_member",
                            "backlog_status": f"outer_archive_read_failed:{type(exc).__name__}",
                            "magic_family": "outer_zip_container",
                            "member_count": 0,
                            "members_written": 0,
                            "listing_truncated": False,
                            "member_kind_counts": {},
                            "member_extension_counts": {},
                            "domain_tags": list(prior_member.get("domain_tags") or []),
                            "problem_tags": list(prior_member.get("problem_tags") or []),
                            "archive_backlog_tags": archive_backlog_tags(
                                "nested_archive_member",
                                str(prior_member.get("extension") or "custom_ext"),
                                "nested_archive_member",
                                "outer_archive_read_failed",
                                "outer_zip_container",
                                0,
                                False,
                            ),
                            "sensitive_flags": list(prior_member.get("sensitive_flags") or []),
                            "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
                        }
                        signals.append(signal)
        if args.progress_every and scanned_archives % args.progress_every == 0:
            print(
                f"progress archives_scanned={scanned_archives} signals={len(signals)} nested_members={len(members)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_archive_backlog_cases(signals, members)
    direct_requiring_parser_or_repair = sum(
        1
        for row in signals
        if row["target_type"] == "direct_unlisted_archive"
        and row["backlog_status"] in {"direct_format_parser_needed", "direct_zip_repair_needed", "direct_archive_probe_failed"}
    )
    nested_listed = sum(1 for row in signals if row["target_type"] == "nested_archive_member" and row["backlog_status"] == "nested_zip_listed")
    nested_not_listed = sum(1 for row in signals if row["target_type"] == "nested_archive_member" and row["backlog_status"] != "nested_zip_listed")
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_archive_backlog_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_archive_run": args.source_archive_run,
        "source_direct_target_signal_count": len(direct_targets),
        "source_nested_target_member_count": len(nested_targets),
        "direct_targets_matched": len(direct_matched),
        "direct_targets_unmatched": max(0, len(direct_targets) - len(direct_matched)),
        "nested_targets_matched": len(nested_matched),
        "nested_targets_unmatched": max(0, len(nested_targets) - len(nested_matched)),
        "signals_written": len(signals),
        "member_signals_written": len(members),
        "archive_backlog_case_count": len(cases),
        "direct_archives_structured": sum(1 for row in signals if row["target_type"] == "direct_unlisted_archive"),
        "direct_archives_requiring_member_parser_or_repair": direct_requiring_parser_or_repair,
        "nested_archives_listed": nested_listed,
        "nested_archives_not_listed": nested_not_listed,
        "nested_archives_skipped_too_large": sum(
            1 for row in signals if row["backlog_status"] == "nested_listing_skipped_too_large"
        ),
        "truncated_nested_listing_count": sum(1 for row in signals if row["listing_truncated"]),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_nested_archive_bytes": args.max_nested_archive_bytes,
        "max_nested_archive_members": args.max_nested_archive_members,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_member_names_copied": False,
            "raw_payload_text_copied": False,
            "archive_payloads_extracted_to_disk": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "archive-backlog-signals.jsonl", signals)
    common.write_jsonl(run_dir / "archive-backlog-members.jsonl", members)
    common.write_jsonl(run_dir / "archive-backlog-cases.jsonl", cases)
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_docs(output_root, run_dir, manifest, signals, cases, members)
    refresh_root_readme(output_root)
    issues = common.scan_forbidden(output_root)
    (run_dir / "privacy-scan.json").write_text(
        json.dumps(
            {"created_at": common.utc_now_iso(), "hit_count": len(issues), "privacy_or_vendor_hits": issues},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if issues:
        raise RuntimeError(f"Generated context still contains {len(issues)} privacy/vendor term hits")
    return run_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", default="knowledge-context")
    parser.add_argument("--run-id", default="directory-archive-backlog-batch")
    parser.add_argument("--source-archive-run", default="directory-archive-batch-20260622")
    parser.add_argument("--max-nested-archive-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--max-nested-archive-members", type=int, default=100_000)
    parser.add_argument("--full-hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--metadata-only-hash", action="store_true", default=True)
    parser.add_argument("--progress-every", type=int, default=10)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        run_dir = run_import(parse_args(argv))
    except Exception as exc:
        print(f"import failed: {exc}", file=sys.stderr)
        return 1
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
