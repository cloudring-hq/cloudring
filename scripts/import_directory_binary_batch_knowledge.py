#!/usr/bin/env python3
"""Append a safe binary/database metadata batch from a directory source.

The batch samples file signatures and structure only. It writes no raw paths,
file names, payload text, domains, URLs, provider names, people, brand names, or
secrets.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_knowledge as directory_common
import import_legacy_mail_knowledge as common


BINARY_SIGNAL_KEYWORDS: dict[str, list[str]] = {
    "backup_or_dump_artifact": ["backup", "dump", "restore", "snapshot", "export", "archive"],
    "database_or_index_artifact": ["database", "sqlite", "index", "pack", "idx", "db", "dat"],
    "credential_or_certificate_artifact": ["key", "pem", "crt", "csr", "cert", "license", "secret"],
    "recording_or_capture_artifact": ["recording", "capture", "trace", "log", "session"],
    "application_binary_artifact": ["binary", "compiled", "library", "executable", "package"],
    "mail_or_message_artifact": ["mail", "message", "inbox", "msg"],
    "project_metadata_artifact": ["project", "config", "lock", "metadata", "cache"],
}


def bucket_bytes(value: int) -> str:
    if value < 1024:
        return "lt_1_kib"
    if value < 1024 * 1024:
        return "lt_1_mib"
    if value < 100 * 1024 * 1024:
        return "lt_100_mib"
    if value < 1024 * 1024 * 1024:
        return "lt_1_gib"
    return "gte_1_gib"


def entropy_bucket(data: bytes) -> str:
    if not data:
        return "empty"
    counts = collections.Counter(data)
    total = len(data)
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    if entropy < 1:
        return "very_low_entropy"
    if entropy < 4:
        return "low_entropy"
    if entropy < 7:
        return "medium_entropy"
    return "high_entropy"


def byte_profile(data: bytes) -> str:
    if not data:
        return "empty"
    sample = data[:8192]
    if not sample:
        return "empty"
    nul_ratio = sample.count(0) / len(sample)
    printable = sum(1 for byte in sample if byte in {9, 10, 13} or 32 <= byte <= 126)
    printable_ratio = printable / len(sample)
    if nul_ratio > 0.2:
        return "binary_with_nulls"
    if printable_ratio > 0.9:
        return "text_like_bytes"
    if printable_ratio > 0.55:
        return "mixed_bytes"
    return "binary_bytes"


def read_sample(path: Path, max_sample_bytes: int) -> bytes:
    size = path.stat().st_size
    with path.open("rb") as handle:
        first = handle.read(max_sample_bytes // 2)
        if size > max_sample_bytes:
            handle.seek(max(0, size - max_sample_bytes // 2))
            last = handle.read(max_sample_bytes // 2)
        else:
            last = b""
    return first + last


def magic_family(data: bytes, ext: str) -> str:
    lower = data[:256].lower()
    if data.startswith(b"SQLite format 3\x00"):
        return "sqlite_database"
    if data.startswith(b"PACK"):
        return "git_pack_or_packfile"
    if data.startswith(b"DIRC"):
        return "git_index"
    if data.startswith(b"PK\x03\x04"):
        return "zip_container_signature"
    if data.startswith(b"\x7fELF") or data.startswith(b"MZ"):
        return "executable_signature"
    if data.startswith(b"%PDF"):
        return "pdf_signature"
    if data.startswith(b"\x89PNG") or data.startswith(b"\xff\xd8\xff") or data.startswith(b"GIF8"):
        return "image_signature"
    if data.startswith(b"RIFF") or data.startswith(b"ID3") or data.startswith(b"\x00\x00\x00"):
        return "media_signature"
    if b"-----begin " in lower and (b"certificate" in lower or b"private key" in lower or b"public key" in lower):
        return "certificate_or_key_text"
    if ext in {"db", "dat", "idx", "pack", "sqlite"}:
        return "database_or_index_extension"
    if ext in {"pem", "crt", "csr", "cer", "lic"}:
        return "certificate_or_license_extension"
    if ext == "custom_ext":
        return "custom_extension_binary"
    if ext == "numeric_ext":
        return "numeric_extension_binary"
    return "unknown_binary_signature"


def binary_signal_tags(classify_text: str, ext: str, family: str, profile: str) -> list[str]:
    folded = classify_text.lower()
    tags = [
        name
        for name, words in BINARY_SIGNAL_KEYWORDS.items()
        if any(word in folded for word in words)
    ]
    if family in {"sqlite_database", "database_or_index_extension", "git_pack_or_packfile", "git_index"}:
        tags.append("database_or_index_artifact")
    if family in {"certificate_or_key_text", "certificate_or_license_extension"}:
        tags.append("credential_or_certificate_artifact")
    if family in {"zip_container_signature"}:
        tags.append("container_misclassified_as_binary")
    if profile == "text_like_bytes":
        tags.append("text_like_binary_backlog")
    if ext in {"custom_ext", "numeric_ext"}:
        tags.append("sanitized_unknown_extension")
    return sorted(set(tags or ["general_binary_signal"]))


def sensitive_flags(relpath: str, ext: str, family: str, sample: bytes) -> list[str]:
    flags: list[str] = []
    if directory_common.SENSITIVE_RE.search(relpath):
        flags.append("path_sensitive_signal")
    if ext in {"pem", "crt", "csr", "cer", "lic"} or family in {"certificate_or_key_text", "certificate_or_license_extension"}:
        flags.append("certificate_or_license_material")
    sample_text = common.decode_bytes(sample[:8192])
    if sample_text and (directory_common.SENSITIVE_RE.search(sample_text) or common.SECRET_LINE_RE.search(sample_text)):
        flags.append("content_sensitive_signal")
    return sorted(set(flags))


def build_binary_signal(path: Path, root: Path, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, root)
    ext = directory_common.safe_extension(path)
    kind = directory_common.file_kind(ext)
    size = path.stat().st_size
    sample = read_sample(path, args.max_sample_bytes)
    family = magic_family(sample, ext)
    profile = byte_profile(sample)
    entropy = entropy_bucket(sample)
    classify_text = f"{relpath}\n{ext}\n{family}\n{profile}"
    domain_tags, problem_tags = common.classify(classify_text)
    tags = binary_signal_tags(classify_text, ext, family, profile)
    flags = sensitive_flags(relpath, ext, family, sample)
    structure_tags = [
        f"extension_{ext}",
        f"kind_{kind}",
        f"magic_{family}",
        f"profile_{profile}",
        f"entropy_{entropy}",
        f"size_{bucket_bytes(size)}",
    ]
    if ext in {"custom_ext", "numeric_ext"}:
        structure_tags.append("source_extension_sanitized")
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    return {
        "binary_signal_id": "binary-" + common.stable_hash(relpath),
        "case_id": "",
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(top),
        "extension": ext,
        "kind": kind,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(size),
        "magic_family": family,
        "byte_profile": profile,
        "entropy_bucket": entropy,
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "binary_signal_tags": tags,
        "structure_tags": sorted(set(structure_tags)),
        "sensitive_flags": flags,
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }


def build_binary_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        ext_counter = collections.Counter(row["extension"] for row in rows)
        kind_counter = collections.Counter(row["kind"] for row in rows)
        family_counter = collections.Counter(row["magic_family"] for row in rows)
        profile_counter = collections.Counter(row["byte_profile"] for row in rows)
        tag_counter = collections.Counter(tag for row in rows for tag in row["binary_signal_tags"])
        structure_counter = collections.Counter(tag for row in rows for tag in row["structure_tags"])
        primary_family = family_counter.most_common(1)[0][0] if family_counter else "unknown_binary_signature"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case_id = "binarycase-" + common.stable_hash(group_hash)
        case = {
            "case_id": case_id,
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "extension_counts": dict(ext_counter.most_common(30)),
            "kind_counts": dict(kind_counter.most_common()),
            "magic_family_counts": dict(family_counter.most_common()),
            "byte_profile_counts": dict(profile_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "binary_signal_tags": [tag for tag, _ in tag_counter.most_common()],
            "structure_tag_counts": dict(structure_counter.most_common(30)),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_binary_signal_ids": [row["binary_signal_id"] for row in rows[:50]],
            "evidence_binary_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A binary/database cluster captured {primary_family.replace('_', ' ')} "
                f"artifacts for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should treat binary and database artifacts as evidence of backups, "
                "indexes, captures, local stores, package state, credentials, and operational residue."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if family_counter.get("sqlite_database", 0) or family_counter.get("database_or_index_extension", 0):
            implications.append("Database and index artifacts should be handled by schema-aware safe extractors before training use.")
        if family_counter.get("certificate_or_key_text", 0) or case["sensitive_signal_count"]:
            implications.append("Credential-like binary artifacts require secret-management modeling, redaction, and strict access controls.")
        if tag_counter.get("text_like_binary_backlog", 0):
            implications.append("Text-like binary files should be queued for a safer text decoder pass.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve binary metadata as traceable backlog for later safe extraction."
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
        elif value:
            counter[value] += 1
    return counter


def write_docs(output_root: Path, run_dir: Path, manifest: dict, signals: list[dict], cases: list[dict]) -> None:
    ext_counts = counter_from_rows(signals, "extension")
    kind_counts = counter_from_rows(signals, "kind")
    family_counts = counter_from_rows(signals, "magic_family")
    profile_counts = counter_from_rows(signals, "byte_profile")
    tag_counts = counter_from_rows(signals, "binary_signal_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Binary Batch Coverage

- Source kind: directory binary batch
- Binary/database files seen: {manifest["binary_like_files_seen"]}
- Binary signals written: {manifest["signals_written"]}
- Binary cases: {manifest["binary_case_count"]}
- Sample bytes per file: {manifest["max_sample_bytes"]}
- Sensitive-signal binary files: {manifest["sensitive_signal_count"]}

## Kinds

{common.markdown_table(kind_counts, "kind")}

## Extensions

{common.markdown_table(ext_counts, "extension")}

## Magic Families

{common.markdown_table(family_counts, "magic_family")}

## Byte Profiles

{common.markdown_table(profile_counts, "byte_profile")}

## Binary Signals

{common.markdown_table(tag_counts, "binary_signal")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "binary-batch-context.md").write_text(
        "# Directory Binary Batch Context\n\n"
        "This run samples binary and database-like artifacts without copying raw paths, "
        "file names, payload text, domains, URLs, provider names, people, brand names, or "
        "secrets. It records safe signature families, byte profiles, entropy buckets, "
        "size buckets, and controlled backlog tags.\n\n"
        "## Agent Use\n\n"
        "- Use `binary-cases.jsonl` for evidence about backups, local stores, captures, packages, indexes, and operational residue.\n"
        "- Use `binary-signals.jsonl` for stable-id traceability and safe signature metadata only.\n"
        "- Treat database, certificate, text-like, and custom-extension signals as queues for specialized safe extractors.\n"
        "- Do not treat sampled binary metadata as user-visible content.\n\n"
        "## Largest Binary Cases\n\n"
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
        ]
    )
    (output_root / "README.md").write_text(body, encoding="utf-8", newline="\n")


def run_import(args: argparse.Namespace) -> Path:
    source_root = Path(args.source).resolve()
    output_root = Path(args.output).resolve()
    run_dir = common.append_only_run_dir(output_root / "imports", args.run_id)
    run_dir.mkdir(parents=True)
    signals: list[dict] = []
    files_seen = 0
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        ext = directory_common.safe_extension(path)
        kind = directory_common.file_kind(ext)
        if kind not in {"binary_or_unknown", "database_or_index"}:
            continue
        files_seen += 1
        signals.append(build_binary_signal(path, source_root, args))
        if args.progress_every and files_seen % args.progress_every == 0:
            print(
                f"progress binary_seen={files_seen} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_binary_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_binary_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_snapshot_run": args.source_snapshot_run,
        "binary_like_files_seen": files_seen,
        "signals_written": len(signals),
        "binary_case_count": len(cases),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_sample_bytes": args.max_sample_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_payload_text_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "binary-signals.jsonl", signals)
    common.write_jsonl(run_dir / "binary-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-binary-batch")
    parser.add_argument("--source-snapshot-run", default="directory-snapshot-20260621")
    parser.add_argument("--max-sample-bytes", type=int, default=131_072)
    parser.add_argument("--full-hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--metadata-only-hash", action="store_true", default=True)
    parser.add_argument("--progress-every", type=int, default=100)
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
