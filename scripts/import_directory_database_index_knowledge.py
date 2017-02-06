#!/usr/bin/env python3
"""Append safe metadata coverage for database and index artifacts.

The pass refines database/index backlog from the binary batch. It records
headers, schema type counts, object-count buckets, member composition buckets,
and status fields only. It writes no raw paths, file names, table names, column
names, row values, payload text, domains, URLs, provider names, people, brand
names, vendor names, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import json
import sqlite3
import struct
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_archive_batch_knowledge as archive_common
import import_directory_binary_batch_knowledge as binary_common
import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


PRIOR_MAGIC_FAMILY_MAP = {
    "git_pack_or_packfile": "content_addressed_packfile",
    "git_index": "content_addressed_pack_index",
    "sqlite_database": "embedded_sql_database",
}


def safe_prior_family(value: str) -> str:
    return PRIOR_MAGIC_FAMILY_MAP.get(value, value)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_header(path: Path, size: int = 8192) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def bucket_bytes(value: int) -> str:
    return binary_common.bucket_bytes(value)


def bucket_count(value: int) -> str:
    return text_common.bucket_count(value)


def target_binary_signals(output_root: Path, source_binary_run: str) -> dict[str, dict]:
    source = output_root / "imports" / source_binary_run / "binary-signals.jsonl"
    targets: dict[str, dict] = {}
    for row in read_jsonl(source):
        if "database_or_index_artifact" in row.get("binary_signal_tags", []):
            targets[row["path_hash"]] = row
    return targets


def header_family(header: bytes, ext: str) -> str:
    if header.startswith(b"SQLite format 3\x00"):
        return "embedded_sql_database"
    if header.startswith(b"PACK"):
        return "content_addressed_packfile"
    if header.startswith(b"\xfftOc"):
        return "content_addressed_pack_index"
    if header.startswith(b"DIRC"):
        return "working_tree_index"
    if header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06") or header.startswith(b"PK\x07\x08"):
        return "zip_container"
    if ext in {"idx"}:
        return "generic_index_file"
    if ext in {"db", "dat"}:
        return "generic_local_store"
    if ext == "pack":
        return "generic_packfile"
    return "generic_database_index_artifact"


def zero_counts() -> dict[str, int]:
    return {
        "schema_table_count": 0,
        "schema_index_count": 0,
        "schema_view_count": 0,
        "schema_trigger_count": 0,
        "pack_object_count": 0,
        "index_object_count": 0,
        "zip_member_count": 0,
        "zip_document_members": 0,
        "zip_media_members": 0,
        "zip_text_members": 0,
        "zip_binary_members": 0,
    }


def bucketed_counts(counts: dict[str, int]) -> dict[str, str]:
    return {key: bucket_count(value) for key, value in sorted(counts.items()) if value}


def parse_pack_header(header: bytes) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    if len(header) < 12 or not header.startswith(b"PACK"):
        return counts, "packfile_header_unrecognized", tags
    version, object_count = struct.unpack(">II", header[4:12])
    counts["pack_object_count"] = int(object_count)
    tags.extend(["packfile_header_parsed", f"pack_version_{version}" if version in {2, 3} else "pack_version_other"])
    return counts, "packfile_header_parsed", tags


def parse_pack_index_header(path: Path, header: bytes) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    if header.startswith(b"\xfftOc") and len(header) >= 8 + 256 * 4:
        fanout_end = header[8 + 255 * 4 : 8 + 256 * 4]
        counts["index_object_count"] = struct.unpack(">I", fanout_end)[0]
        tags.extend(["pack_index_header_parsed", "pack_index_versioned"])
        return counts, "pack_index_header_parsed", tags
    if path.stat().st_size >= 256 * 4:
        with path.open("rb") as handle:
            fanout = handle.read(256 * 4)
        if len(fanout) == 256 * 4:
            values = struct.unpack(">256I", fanout)
            if all(a <= b for a, b in zip(values, values[1:])):
                counts["index_object_count"] = int(values[-1])
                tags.extend(["pack_index_header_parsed", "pack_index_legacy"])
                return counts, "pack_index_header_parsed", tags
    return counts, "index_header_retained", ["generic_index_metadata"]


def sqlite_schema_counts(path: Path) -> tuple[dict[str, int], dict[str, str], str, list[str]]:
    counts = zero_counts()
    properties: dict[str, str] = {}
    tags: list[str] = []
    uri = f"file:{path.as_posix()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=1.0)
        try:
            conn.execute("PRAGMA query_only=ON")
            for key in ["page_count", "page_size", "freelist_count", "user_version", "application_id"]:
                try:
                    value = conn.execute(f"PRAGMA {key}").fetchone()
                except Exception:
                    continue
                if value and isinstance(value[0], int):
                    properties[key] = bucket_count(int(value[0])) if key.endswith("count") else str(int(value[0]))
            try:
                rows = conn.execute("SELECT type, count(*) FROM sqlite_schema GROUP BY type").fetchall()
            except Exception:
                rows = []
            for schema_type, count in rows:
                if schema_type == "table":
                    counts["schema_table_count"] = int(count)
                elif schema_type == "index":
                    counts["schema_index_count"] = int(count)
                elif schema_type == "view":
                    counts["schema_view_count"] = int(count)
                elif schema_type == "trigger":
                    counts["schema_trigger_count"] = int(count)
            tags.append("schema_type_counts_available")
            if counts["schema_table_count"]:
                tags.append("contains_table_schema")
            if counts["schema_index_count"]:
                tags.append("contains_index_schema")
            if counts["schema_view_count"]:
                tags.append("contains_view_schema")
            if counts["schema_trigger_count"]:
                tags.append("contains_trigger_schema")
            return counts, properties, "embedded_sql_schema_counted", tags
        finally:
            conn.close()
    except Exception as exc:
        return counts, properties, f"embedded_sql_probe_failed:{type(exc).__name__}", tags


def zip_member_counts(path: Path, max_members: int) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            counts["zip_member_count"] = len(infos)
            for info in infos[:max_members]:
                ext = archive_common.member_extension(info.filename)
                kind = directory_common.file_kind(ext)
                if kind == "document":
                    counts["zip_document_members"] += 1
                elif kind == "media_or_design":
                    counts["zip_media_members"] += 1
                elif kind == "text_or_code":
                    counts["zip_text_members"] += 1
                else:
                    counts["zip_binary_members"] += 1
            tags.append("zip_member_counts_available")
            if len(infos) > max_members:
                tags.append("zip_member_count_truncated")
            return counts, "zip_container_counted", tags
    except Exception as exc:
        return counts, f"zip_container_probe_failed:{type(exc).__name__}", tags


def metadata_probe(path: Path, ext: str, args: argparse.Namespace) -> tuple[dict[str, int], dict[str, str], str, str, list[str]]:
    try:
        header = read_header(path)
    except Exception as exc:
        return zero_counts(), {}, f"header_read_failed:{type(exc).__name__}", "unknown_header", []
    family = header_family(header, ext)
    properties: dict[str, str] = {}
    if family == "embedded_sql_database":
        counts, properties, status, tags = sqlite_schema_counts(path)
    elif family == "content_addressed_packfile":
        counts, status, tags = parse_pack_header(header)
    elif family == "content_addressed_pack_index":
        counts, status, tags = parse_pack_index_header(path, header)
    elif family == "zip_container":
        counts, status, tags = zip_member_counts(path, args.max_zip_members)
    else:
        counts = zero_counts()
        status = "generic_metadata_retained"
        tags = ["generic_index_or_store_metadata"]
    return counts, properties, status, family, tags


def database_index_tags(ext: str, status: str, family: str, counts: dict[str, int], prior: dict) -> list[str]:
    tags = [
        f"extension_{ext}",
        f"metadata_status_{status.split(':', 1)[0]}",
        f"storage_family_{family}",
        f"prior_magic_{safe_prior_family(str(prior.get('magic_family') or 'unknown'))}",
    ]
    if "failed" in status:
        tags.append("metadata_probe_failed")
    if counts.get("schema_table_count") or counts.get("schema_index_count"):
        tags.append("schema_counts_available")
    if counts.get("pack_object_count"):
        tags.append("packfile_object_count_available")
    if counts.get("index_object_count"):
        tags.append("pack_index_object_count_available")
    if counts.get("zip_member_count"):
        tags.append("container_member_counts_available")
    if prior.get("sensitive_flags"):
        tags.append("sensitive_database_index_signal")
    if "text_like_binary_backlog" in prior.get("binary_signal_tags", []):
        tags.append("text_like_database_index_backlog")
    return sorted(set(tags))


def build_database_index_signal(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    counts, properties, status, family, metadata_tags = metadata_probe(path, ext, args)
    classify_text = f"{relpath}\n{ext}\n{family}\n{status}\n{' '.join(metadata_tags)}"
    domain_tags, problem_tags = common.classify(classify_text)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    safe_family = safe_prior_family(str(prior.get("magic_family") or "unknown"))
    signal = {
        "database_index_signal_id": "dbindex-" + common.stable_hash(relpath),
        "case_id": "",
        "source_binary_signal_id": prior.get("binary_signal_id", ""),
        "path_hash": prior.get("path_hash", common.stable_hash(relpath, 24)),
        "top_group_hash": prior.get("top_group_hash", "group-" + common.stable_hash(top)),
        "extension": ext,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(path.stat().st_size),
        "prior_kind": prior.get("kind", ""),
        "prior_magic_family": safe_family,
        "byte_profile": prior.get("byte_profile", ""),
        "entropy_bucket": prior.get("entropy_bucket", ""),
        "storage_family": family,
        "metadata_status": status,
        "metadata_count_buckets": bucketed_counts(counts),
        "metadata_property_buckets": properties,
        "domain_tags": list(dict.fromkeys(list(prior.get("domain_tags") or []) + domain_tags)),
        "problem_tags": list(dict.fromkeys(list(prior.get("problem_tags") or []) + problem_tags)),
        "database_index_tags": sorted(set(metadata_tags + database_index_tags(ext, status, family, counts, prior))),
        "sensitive_flags": list(prior.get("sensitive_flags") or []),
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }
    return signal


def build_database_index_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        ext_counter = collections.Counter(row["extension"] for row in rows)
        family_counter = collections.Counter(row["storage_family"] for row in rows)
        status_counter = collections.Counter(row["metadata_status"] for row in rows)
        tag_counter = collections.Counter(tag for row in rows for tag in row["database_index_tags"])
        primary_family = family_counter.most_common(1)[0][0] if family_counter else "database_index_artifact"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "dbindexcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "extension_counts": dict(ext_counter.most_common(30)),
            "storage_family_counts": dict(family_counter.most_common()),
            "metadata_status_counts": dict(status_counter.most_common()),
            "database_index_tags": [tag for tag, _ in tag_counter.most_common()],
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_database_index_signal_ids": [row["database_index_signal_id"] for row in rows[:50]],
            "evidence_database_index_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A database/index cluster preserved {primary_family.replace('_', ' ')} "
                f"metadata for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should treat local stores, indexes, packfiles, and metadata caches "
                "as evidence of build state, migration residue, backups, and operational tooling."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if tag_counter.get("schema_counts_available", 0):
            implications.append("Schema-level inventory can guide migration planning without exposing table names or row values.")
        if tag_counter.get("packfile_object_count_available", 0) or tag_counter.get("pack_index_object_count_available", 0):
            implications.append("Content-addressed pack/index artifacts should be modeled as build and source-state evidence, not customer content.")
        if tag_counter.get("container_member_counts_available", 0):
            implications.append("Misclassified container stores need routing to archive-safe inventory before deeper processing.")
        if case["sensitive_signal_count"]:
            implications.append("Sensitive local-store signals require access controls and secret-aware handling before any further extraction.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve database/index metadata as traceable backlog and refine only with safe schema-aware extractors."
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


def write_docs(output_root: Path, run_dir: Path, manifest: dict, signals: list[dict], cases: list[dict]) -> None:
    ext_counts = counter_from_rows(signals, "extension")
    family_counts = counter_from_rows(signals, "storage_family")
    status_counts = counter_from_rows(signals, "metadata_status")
    tag_counts = counter_from_rows(signals, "database_index_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Database/Index Coverage

- Source kind: directory database/index batch
- Source target signals: {manifest["source_target_signal_count"]}
- Target hashes matched: {manifest["target_hashes_matched"]}
- Database/index signals written: {manifest["signals_written"]}
- Database/index cases: {manifest["database_index_case_count"]}
- Schema-capable artifacts: {manifest["schema_counted_artifacts"]}
- Pack/index headers parsed: {manifest["pack_or_index_headers_parsed"]}
- Container member-count artifacts: {manifest["container_member_count_artifacts"]}
- Generic metadata retained: {manifest["generic_metadata_retained"]}
- Probe failures: {manifest["metadata_probe_failed"]}
- Sensitive-signal artifacts: {manifest["sensitive_signal_count"]}

## Extensions

{common.markdown_table(ext_counts, "extension")}

## Storage Families

{common.markdown_table(family_counts, "storage_family")}

## Metadata Status

{common.markdown_table(status_counts, "metadata_status")}

## Database/Index Tags

{common.markdown_table(tag_counts, "tag")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "database-index-context.md").write_text(
        "# Directory Database/Index Context\n\n"
        "This run refines database and index artifacts from the binary batch. It records "
        "safe metadata only: header families, schema type counts, object-count buckets, "
        "container member-count buckets, size buckets, stable ids, and status fields. "
        "It does not copy raw paths, file names, table names, column names, row values, "
        "payload text, URLs, domains, people, provider names, brand names, vendor names, or secrets.\n\n"
        "## Agent Use\n\n"
        "- Use `database-index-cases.jsonl` for local-store, index, packfile, metadata-cache, and migration-residue cases.\n"
        "- Use `database-index-signals.jsonl` for stable-id traceability and safe metadata buckets only.\n"
        "- Treat probe failures, generic stores, and sensitive signals as retained queues, not dropped context.\n"
        "- Never infer source identities from schema counts or object-count buckets.\n\n"
        "## Largest Database/Index Cases\n\n"
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
        elif kind == "directory_database_index_batch":
            summary = (
                f"directory database/index batch, {manifest.get('signals_written', 0)} metadata signals, "
                f"{manifest.get('database_index_case_count', 0)} database/index cases"
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
    targets = target_binary_signals(output_root, args.source_binary_run)
    matched_hashes: set[str] = set()
    signals: list[dict] = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        relpath = directory_common.normalized_relpath(path, source_root)
        path_hash = common.stable_hash(relpath, 24)
        prior = targets.get(path_hash)
        if prior is None:
            continue
        matched_hashes.add(path_hash)
        signals.append(build_database_index_signal(path, source_root, prior, args))
        if args.progress_every and len(signals) % args.progress_every == 0:
            print(
                f"progress database_index_seen={len(signals)} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_database_index_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_database_index_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_binary_run": args.source_binary_run,
        "source_target_signal_count": len(targets),
        "target_hashes_matched": len(matched_hashes),
        "target_hashes_unmatched": max(0, len(targets) - len(matched_hashes)),
        "signals_written": len(signals),
        "database_index_case_count": len(cases),
        "schema_counted_artifacts": sum(1 for row in signals if row["metadata_status"] == "embedded_sql_schema_counted"),
        "pack_or_index_headers_parsed": sum(
            1
            for row in signals
            if row["metadata_status"] in {"packfile_header_parsed", "pack_index_header_parsed"}
        ),
        "container_member_count_artifacts": sum(1 for row in signals if row["metadata_status"] == "zip_container_counted"),
        "generic_metadata_retained": sum(1 for row in signals if row["metadata_status"] == "generic_metadata_retained"),
        "metadata_probe_failed": sum(1 for row in signals if "failed" in row["metadata_status"]),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_zip_members": args.max_zip_members,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_table_names_copied": False,
            "raw_column_names_copied": False,
            "raw_row_values_copied": False,
            "raw_payload_text_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "database-index-signals.jsonl", signals)
    common.write_jsonl(run_dir / "database-index-cases.jsonl", cases)
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_docs(output_root, run_dir, manifest, signals, cases)
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
    parser.add_argument("--run-id", default="directory-database-index-batch")
    parser.add_argument("--source-binary-run", default="directory-binary-batch-20260622")
    parser.add_argument("--max-zip-members", type=int, default=100_000)
    parser.add_argument("--full-hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--metadata-only-hash", action="store_true", default=True)
    parser.add_argument("--progress-every", type=int, default=20)
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
