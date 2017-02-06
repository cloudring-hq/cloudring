#!/usr/bin/env python3
"""Append a safe archive-structure batch from a directory source.

The batch lists archive metadata and archive-member structure where supported.
It never extracts archive payloads to disk and writes no raw paths, member names,
domains, emails, URLs, vendor names, people, source text, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import re
import sys
import tarfile
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


ARCHIVE_EXTENSIONS = {"zip", "gz", "tgz", "tar", "bz2", "xz", "7z", "rar", "cab", "iso", "jar", "war", "ear"}
SUPPORTED_CONTAINER_EXTENSIONS = {"zip", "jar", "war", "ear", "tar", "tgz"}
GZIP_STREAM_EXTENSIONS = {"gz", "bz2", "xz"}
SAFE_MEMBER_EXTENSIONS = (
    set(directory_common.TEXT_EXTENSIONS)
    | set(directory_common.DOCUMENT_EXTENSIONS)
    | set(directory_common.ARCHIVE_EXTENSIONS)
    | set(directory_common.MEDIA_EXTENSIONS)
    | {
        "7z",
        "app",
        "bmp",
        "bundle",
        "cab",
        "car",
        "cer",
        "compressed_stream",
        "config",
        "crt",
        "csr",
        "dat",
        "db",
        "dll",
        "doc",
        "dot",
        "ear",
        "gz",
        "jar",
        "key",
        "lic",
        "log",
        "map",
        "mpp",
        "msg",
        "odt",
        "pem",
        "plist",
        "ppt",
        "rar",
        "resources",
        "strings",
        "tar",
        "tmp",
        "vbs",
        "vdx",
        "vsd",
        "vsdm",
        "vsdx",
        "vss",
        "war",
        "xls",
    }
)


def bucket_bytes(value: int) -> str:
    if value < 0:
        return "unknown"
    if value < 1024:
        return "lt_1_kib"
    if value < 1024 * 1024:
        return "lt_1_mib"
    if value < 100 * 1024 * 1024:
        return "lt_100_mib"
    if value < 1024 * 1024 * 1024:
        return "lt_1_gib"
    return "gte_1_gib"


def member_extension(name: str) -> str:
    ext = Path(name).suffix.lower().lstrip(".")
    if not ext:
        return "none"
    ext = re.sub(r"[^a-z0-9_+-]+", "_", ext)[:40] or "custom_ext"
    if ext in SAFE_MEMBER_EXTENSIONS:
        return ext
    if ext.isdigit():
        return "numeric_ext"
    return "custom_ext"


def path_depth(name: str) -> str:
    clean = name.replace("\\", "/").strip("/")
    if not clean:
        return "depth_0"
    depth = len([part for part in clean.split("/") if part])
    if depth <= 1:
        return "depth_1"
    if depth <= 3:
        return "depth_2_3"
    if depth <= 7:
        return "depth_4_7"
    return "depth_8_plus"


def archive_structure_tags(ext: str, status: str, member_count: int, member_kind_counts: dict[str, int]) -> list[str]:
    tags = [f"archive_extension_{ext}", f"archive_status_{status.split(':', 1)[0]}"]
    if member_count == 0:
        tags.append("empty_or_unlisted_archive")
    elif member_count <= 10:
        tags.append("small_archive_bundle")
    elif member_count <= 100:
        tags.append("medium_archive_bundle")
    else:
        tags.append("large_archive_bundle")
    for kind, count in sorted(member_kind_counts.items()):
        if count:
            tags.append(f"contains_{kind}")
    return sorted(set(tags))


def member_structure_tags(ext: str, size: int, depth: str, is_dir: bool) -> list[str]:
    kind = directory_common.file_kind(ext)
    tags = [f"member_kind_{kind}", f"member_extension_{ext}", depth, f"member_size_{bucket_bytes(size)}"]
    if is_dir:
        tags.append("directory_member")
    if kind == "archive_bundle":
        tags.append("nested_archive_member")
    if ext in {"pem", "key", "crt", "csr", "cer", "lic"}:
        tags.append("certificate_or_license_member")
    return sorted(set(tags))


def member_sensitive_flags(name: str, ext: str) -> list[str]:
    flags: list[str] = []
    if directory_common.SENSITIVE_RE.search(name):
        flags.append("member_name_sensitive_signal")
    if ext in {"pem", "key", "crt", "csr", "cer", "lic"}:
        flags.append("certificate_or_license_material")
    return sorted(set(flags))


def archive_sensitive_flags(relpath: str, ext: str) -> list[str]:
    flags: list[str] = []
    if directory_common.SENSITIVE_RE.search(relpath):
        flags.append("archive_path_sensitive_signal")
    if ext in {"7z", "rar"}:
        flags.append("unsupported_proprietary_archive_signal")
    return sorted(set(flags))


def classify_member(name: str, ext: str) -> tuple[list[str], list[str]]:
    kind = directory_common.file_kind(ext)
    return common.classify(f"{name}\n{ext}\n{kind}")


def zip_members(path: Path, archive_id: str, relpath: str, max_members: int) -> tuple[list[dict], dict, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            members: list[dict] = []
            for ordinal, info in enumerate(infos[:max_members]):
                ext = member_extension(info.filename)
                domain_tags, problem_tags = classify_member(info.filename, ext)
                size = int(getattr(info, "file_size", 0) or 0)
                compressed_size = int(getattr(info, "compress_size", 0) or 0)
                is_dir = bool(info.is_dir())
                depth = path_depth(info.filename)
                members.append(
                    {
                        "member_id": "member-" + common.stable_hash(f"{relpath}\0{info.filename}", 16),
                        "archive_id": archive_id,
                        "member_ordinal_bucket": text_common.bucket_count(ordinal + 1),
                        "extension": ext,
                        "kind": directory_common.file_kind(ext),
                        "is_directory": is_dir,
                        "size_bucket": bucket_bytes(size),
                        "compressed_size_bucket": bucket_bytes(compressed_size),
                        "path_depth_bucket": depth,
                        "domain_tags": domain_tags,
                        "problem_tags": problem_tags,
                        "structure_tags": member_structure_tags(ext, size, depth, is_dir),
                        "sensitive_flags": member_sensitive_flags(info.filename, ext),
                    }
                )
            meta = {
                "member_count": len(infos),
                "members_written": len(members),
                "listing_truncated": len(infos) > max_members,
            }
            return members, meta, "archive_listed"
    except Exception as exc:
        return [], {"member_count": 0, "members_written": 0, "listing_truncated": False}, f"archive_list_failed:{type(exc).__name__}"


def tar_members(path: Path, archive_id: str, relpath: str, max_members: int) -> tuple[list[dict], dict, str]:
    try:
        with tarfile.open(path) as archive:
            infos = archive.getmembers()
            members: list[dict] = []
            for ordinal, info in enumerate(infos[:max_members]):
                ext = member_extension(info.name)
                domain_tags, problem_tags = classify_member(info.name, ext)
                size = int(getattr(info, "size", 0) or 0)
                is_dir = bool(info.isdir())
                depth = path_depth(info.name)
                members.append(
                    {
                        "member_id": "member-" + common.stable_hash(f"{relpath}\0{info.name}", 16),
                        "archive_id": archive_id,
                        "member_ordinal_bucket": text_common.bucket_count(ordinal + 1),
                        "extension": ext,
                        "kind": directory_common.file_kind(ext),
                        "is_directory": is_dir,
                        "size_bucket": bucket_bytes(size),
                        "compressed_size_bucket": "unknown",
                        "path_depth_bucket": depth,
                        "domain_tags": domain_tags,
                        "problem_tags": problem_tags,
                        "structure_tags": member_structure_tags(ext, size, depth, is_dir),
                        "sensitive_flags": member_sensitive_flags(info.name, ext),
                    }
                )
            meta = {
                "member_count": len(infos),
                "members_written": len(members),
                "listing_truncated": len(infos) > max_members,
            }
            return members, meta, "archive_listed"
    except Exception as exc:
        return [], {"member_count": 0, "members_written": 0, "listing_truncated": False}, f"archive_list_failed:{type(exc).__name__}"


def gzip_stream_member(path: Path, archive_id: str, relpath: str) -> tuple[list[dict], dict, str]:
    try:
        with gzip.open(path, "rb") as handle:
            handle.peek(1)
        inner_ext = member_extension(path.stem)
        if inner_ext == "none":
            inner_ext = "compressed_stream"
        domain_tags, problem_tags = classify_member(path.name, inner_ext)
        members = [
            {
                "member_id": "member-" + common.stable_hash(f"{relpath}\0gzip-stream", 16),
                "archive_id": archive_id,
                "member_ordinal_bucket": "count_1",
                "extension": inner_ext,
                "kind": directory_common.file_kind(inner_ext),
                "is_directory": False,
                "size_bucket": "unknown",
                "compressed_size_bucket": bucket_bytes(path.stat().st_size),
                "path_depth_bucket": "depth_1",
                "domain_tags": domain_tags,
                "problem_tags": problem_tags,
                "structure_tags": member_structure_tags(inner_ext, -1, "depth_1", False),
                "sensitive_flags": member_sensitive_flags(path.name, inner_ext),
            }
        ]
        return members, {"member_count": 1, "members_written": 1, "listing_truncated": False}, "gzip_stream_indexed"
    except Exception as exc:
        return [], {"member_count": 0, "members_written": 0, "listing_truncated": False}, f"archive_list_failed:{type(exc).__name__}"


def list_archive_members(path: Path, archive_id: str, relpath: str, ext: str, max_members: int) -> tuple[list[dict], dict, str]:
    if ext in {"zip", "jar", "war", "ear"}:
        return zip_members(path, archive_id, relpath, max_members)
    if ext in {"tar", "tgz"}:
        return tar_members(path, archive_id, relpath, max_members)
    if ext == "gz":
        return gzip_stream_member(path, archive_id, relpath)
    return [], {"member_count": 0, "members_written": 0, "listing_truncated": False}, "archive_listing_unsupported"


def build_archive_signal(path: Path, root: Path, args: argparse.Namespace) -> tuple[dict, list[dict]]:
    relpath = directory_common.normalized_relpath(path, root)
    ext = directory_common.safe_extension(path)
    archive_id = "archive-" + common.stable_hash(relpath)
    size = path.stat().st_size
    domain_tags, problem_tags = common.classify(relpath)
    members, meta, status = list_archive_members(path, archive_id, relpath, ext, args.max_archive_members)
    member_domain_counter = collections.Counter(tag for row in members for tag in row["domain_tags"])
    member_problem_counter = collections.Counter(tag for row in members for tag in row["problem_tags"])
    member_kind_counter = collections.Counter(row["kind"] for row in members)
    member_ext_counter = collections.Counter(row["extension"] for row in members)
    if member_domain_counter:
        domain_tags = list(dict.fromkeys(domain_tags + [tag for tag, _ in member_domain_counter.most_common(6)]))
    if member_problem_counter:
        problem_tags = list(dict.fromkeys(problem_tags + [tag for tag, _ in member_problem_counter.most_common(6)]))
    signal = {
        "archive_id": archive_id,
        "case_id": "",
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(relpath.split("/", 1)[0] if "/" in relpath else "<root>"),
        "extension": ext,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(size),
        "size_bytes": size,
        "listing_status": status,
        "member_count": meta["member_count"],
        "members_written": meta["members_written"],
        "listing_truncated": meta["listing_truncated"],
        "member_kind_counts": dict(member_kind_counter.most_common(20)),
        "member_extension_counts": dict(member_ext_counter.most_common(40)),
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "structure_tags": archive_structure_tags(ext, status, meta["member_count"], dict(member_kind_counter)),
        "sensitive_flags": sorted(set(archive_sensitive_flags(relpath, ext) + [flag for row in members for flag in row["sensitive_flags"]])),
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }
    return signal, members


def build_archive_cases(signals: list[dict], members: list[dict]) -> list[dict]:
    members_by_archive: dict[str, list[dict]] = collections.defaultdict(list)
    for member in members:
        members_by_archive[member["archive_id"]].append(member)
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        status_counter = collections.Counter(row["listing_status"] for row in rows)
        archive_ext_counter = collections.Counter(row["extension"] for row in rows)
        member_kind_counter: collections.Counter[str] = collections.Counter()
        member_ext_counter: collections.Counter[str] = collections.Counter()
        structure_counter: collections.Counter[str] = collections.Counter()
        for row in rows:
            member_kind_counter.update(row["member_kind_counts"])
            member_ext_counter.update(row["member_extension_counts"])
            structure_counter.update(row["structure_tags"])
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "archive_unlisted"
        case_id = "archivecase-" + common.stable_hash(group_hash)
        case = {
            "case_id": case_id,
            "top_group_hash": group_hash,
            "archive_count": len(rows),
            "total_member_count": sum(row["member_count"] for row in rows),
            "members_written": sum(row["members_written"] for row in rows),
            "listing_truncated_count": sum(1 for row in rows if row["listing_truncated"]),
            "listing_status_counts": dict(status_counter.most_common()),
            "archive_extension_counts": dict(archive_ext_counter.most_common()),
            "member_kind_counts": dict(member_kind_counter.most_common(20)),
            "member_extension_counts": dict(member_ext_counter.most_common(30)),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "structure_tag_counts": dict(structure_counter.most_common(30)),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_archive_ids": [row["archive_id"] for row in rows[:50]],
            "evidence_archive_id_count": len(rows),
            "anonymized_situation": (
                f"An archive bundle cluster captured {primary_domain.replace('_', ' ')} "
                f"material; the dominant archive state is {primary_status.replace('_', ' ')} "
                f"and the dominant operational signal is {primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should treat archives as durable evidence of migrations, backups, "
                "deliverables, imports, exports, and historical product/customer packaging."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if "archive_listing_unsupported" in status_counter:
            implications.append("Keep unsupported archive formats in an explicit safe-processing queue instead of dropping them.")
        if case["listing_truncated_count"]:
            implications.append("Re-run archive inventory with a higher member limit before declaring full archive coverage.")
        if member_kind_counter.get("archive_bundle", 0):
            implications.append("Nested archive members require recursive safe inventory so migrations and backups are not hidden.")
        if case["sensitive_signal_count"]:
            implications.append("Archive names and member names can reveal credential-handling needs; model them as managed secrets workflows.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve archive inventory as traceable context and refine unsupported formats later."
        ]
        cases.append(case)
    case_by_group = {case["top_group_hash"]: case["case_id"] for case in cases}
    for signal in signals:
        signal["case_id"] = case_by_group[signal["top_group_hash"]]
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
    status_counts = counter_from_rows(signals, "listing_status")
    archive_ext_counts = counter_from_rows(signals, "extension")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    member_ext_counts = counter_from_rows(members, "extension")
    member_kind_counts = counter_from_rows(members, "kind")
    largest_cases = sorted(cases, key=lambda row: (row["total_member_count"], row["archive_count"]), reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Archive Batch Coverage

- Source kind: directory archive batch
- Archive-like files seen: {manifest["archive_like_files_seen"]}
- Archive signals written: {manifest["signals_written"]}
- Archive member signals written: {manifest["member_signals_written"]}
- Archive cases: {manifest["archive_case_count"]}
- Archives listed: {manifest["archives_listed"]}
- Archives unsupported or failed: {manifest["archives_not_listed"]}
- Truncated archive listings: {manifest["truncated_archive_count"]}
- Sensitive-signal archives: {manifest["sensitive_signal_count"]}
- Max archive members per archive: {manifest["max_archive_members"]}

## Listing Status

{common.markdown_table(status_counts, "status")}

## Archive Extensions

{common.markdown_table(archive_ext_counts, "extension")}

## Member Kinds

{common.markdown_table(member_kind_counts, "kind")}

## Member Extensions

{common.markdown_table(member_ext_counts, "extension")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "archive-batch-context.md").write_text(
        "# Directory Archive Batch Context\n\n"
        "This run inventories archive bundles without copying raw archive paths, member names, "
        "payload text, domains, addresses, provider names, people, or secrets. Supported "
        "containers are listed as anonymized member signals; unsupported formats are retained "
        "as explicit safe-processing backlog instead of being ignored.\n\n"
        "## Agent Use\n\n"
        "- Use `archive-cases.jsonl` for archive-level evidence about migrations, backups, exports, deliverables, and historical packaging.\n"
        "- Use `archive-signals.jsonl` for bundle-level traceability by stable ids only.\n"
        "- Use `archive-members.jsonl` for anonymized member composition, not raw file names.\n"
        "- Treat unsupported, failed, truncated, and nested archive signals as queues for later safe processing.\n\n"
        "## Largest Archive Cases\n\n"
        + "\n".join(
            f"- `{case['case_id']}` ({case['archive_count']} archives, {case['total_member_count']} members): {case['anonymized_situation']}"
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
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
        elif kind == "directory_document_batch":
            summary = (
                f"directory document batch, {manifest.get('signals_written', 0)} document signals, "
                f"{manifest.get('document_case_count', 0)} document cases"
            )
        elif kind == "directory_archive_batch":
            summary = (
                f"directory archive batch, {manifest.get('signals_written', 0)} archive signals, "
                f"{manifest.get('member_signals_written', 0)} anonymized member signals, "
                f"{manifest.get('archive_case_count', 0)} archive cases"
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
        ]
    )
    (output_root / "README.md").write_text(body, encoding="utf-8", newline="\n")


def run_import(args: argparse.Namespace) -> Path:
    source_root = Path(args.source).resolve()
    output_root = Path(args.output).resolve()
    run_dir = common.append_only_run_dir(output_root / "imports", args.run_id)
    run_dir.mkdir(parents=True)
    signals: list[dict] = []
    members: list[dict] = []
    archives_seen = 0
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        ext = directory_common.safe_extension(path)
        if ext not in ARCHIVE_EXTENSIONS and directory_common.file_kind(ext) != "archive_bundle":
            continue
        archives_seen += 1
        signal, archive_members = build_archive_signal(path, source_root, args)
        signals.append(signal)
        members.extend(archive_members)
        if args.progress_every and archives_seen % args.progress_every == 0:
            print(
                f"progress archives_seen={archives_seen} signals={len(signals)} members={len(members)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_archive_cases(signals, members)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_archive_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_snapshot_run": args.source_snapshot_run,
        "archive_like_files_seen": archives_seen,
        "signals_written": len(signals),
        "member_signals_written": len(members),
        "archives_listed": sum(1 for row in signals if row["listing_status"] in {"archive_listed", "gzip_stream_indexed"}),
        "archives_not_listed": sum(1 for row in signals if row["listing_status"] not in {"archive_listed", "gzip_stream_indexed"}),
        "truncated_archive_count": sum(1 for row in signals if row["listing_truncated"]),
        "archive_case_count": len(cases),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_archive_members": args.max_archive_members,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_member_names_copied": False,
            "raw_text_copied": False,
            "archive_payloads_extracted": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "archive-signals.jsonl", signals)
    common.write_jsonl(run_dir / "archive-members.jsonl", members)
    common.write_jsonl(run_dir / "archive-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-archive-batch")
    parser.add_argument("--source-snapshot-run", default="directory-snapshot-20260621")
    parser.add_argument("--max-archive-members", type=int, default=100_000)
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
    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
