#!/usr/bin/env python3
"""Build an anonymized knowledge-context run from a directory tree.

This importer indexes every file in the source tree, classifies supported text
and office-like documents, and writes only neutral metadata, hashes, tags, and
derived cases. It intentionally avoids copying raw paths, raw names, source
text, secrets, domains, vendor names, or personal data into knowledge-context.
"""

from __future__ import annotations

import argparse
import collections
import csv
import email
import email.policy
import hashlib
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_legacy_mail_knowledge as common


TEXT_EXTENSIONS = {
    "",
    "none",
    "1",
    "5",
    "bat",
    "BUILD_EXE_TIME".lower(),
    "conf",
    "css",
    "csv",
    "diff",
    "dist",
    "dump",
    "editorconfig",
    "eml",
    "gitignore",
    "gitattributes",
    "htaccess",
    "htm",
    "html",
    "in",
    "ini",
    "inp",
    "js",
    "json",
    "less",
    "log",
    "markdown",
    "md",
    "netcfg",
    "out",
    "patch",
    "patch2",
    "php",
    "pl",
    "plist",
    "pm",
    "pod",
    "ps1",
    "py",
    "rb",
    "rss",
    "sample",
    "scss",
    "shtml",
    "sh",
    "sql",
    "strings",
    "t",
    "t2t",
    "taskpaper",
    "tpl",
    "txt",
    "xml",
    "yml",
}

DOCUMENT_EXTENSIONS = {
    "docx",
    "pptx",
    "xlsx",
    "xlsm",
    "pdf",
    "rtf",
}

ARCHIVE_EXTENSIONS = {
    "7z",
    "gz",
    "rar",
    "zip",
}

MEDIA_EXTENSIONS = {
    "aep",
    "afassets",
    "afdesign",
    "afpalette",
    "ai",
    "aif",
    "avi",
    "bmp",
    "chm",
    "dmg",
    "drawing",
    "eot",
    "epub",
    "eps",
    "exe",
    "flac",
    "flv",
    "gif",
    "icns",
    "ico",
    "indb",
    "jpg",
    "jpeg",
    "key",
    "m4a",
    "m4v",
    "mov",
    "mp3",
    "mp4",
    "numbers",
    "ogg",
    "otf",
    "pages",
    "png",
    "potx",
    "prproj",
    "ps",
    "psd",
    "QT-cb4d-d010ebd4-bfffdc58-00".lower(),
    "QT-cb7a-d010ed61-bfffdc58-00".lower(),
    "svg",
    "svgz",
    "swf",
    "tif",
    "tiff",
    "ttf",
    "wav",
    "webloc",
    "wmv",
    "woff",
    "woff2",
    "xd",
}

KNOWN_BINARY_EXTENSIONS = {
    "arf",
    "bak",
    "bmml",
    "bpmn",
    "car",
    "cer",
    "com",
    "crt",
    "csr",
    "dot",
    "grammar",
    "iba",
    "imb",
    "iml",
    "lib",
    "lic",
    "lock",
    "map",
    "nib",
    "odt",
    "orig",
    "partial",
    "pem",
    "rpp",
    "rpp-bak",
    "scc",
    "scap",
    "scandeps",
    "scssc",
    "sesx",
    "spec",
    "td y".replace(" ", ""),
    "textclipping",
    "tmp",
    "trec",
    "tscproj",
    "url",
    "wma",
}

SAFE_EXTENSIONS = (
    TEXT_EXTENSIONS
    | DOCUMENT_EXTENSIONS
    | ARCHIVE_EXTENSIONS
    | MEDIA_EXTENSIONS
    | KNOWN_BINARY_EXTENSIONS
    | {"custom_ext", "numeric_ext", "doc", "xls", "ppt", "mpp", "vsd", "vsdx", "vdx", "vsdm", "vss", "db", "dat", "idx", "pack", "sqlite"}
)

SENSITIVE_RE = re.compile(
    r"password|passwd|secret|token|credential|private|access|key|pem|csr|crt|"
    r"парол|секрет|доступ|ключ|персональн|паспорт|банк|оплат",
    re.IGNORECASE,
)


def normalized_relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def safe_extension(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    if not ext:
        return "none"
    ext = re.sub(r"[^a-z0-9_+-]+", "_", ext)[:40] or "custom_ext"
    if ext.isdigit():
        return "numeric_ext"
    if ext in SAFE_EXTENSIONS:
        return ext
    return "custom_ext"


def file_kind(ext: str) -> str:
    if ext in TEXT_EXTENSIONS:
        return "text_or_code"
    if ext in DOCUMENT_EXTENSIONS:
        return "document"
    if ext in ARCHIVE_EXTENSIONS:
        return "archive_bundle"
    if ext in MEDIA_EXTENSIONS:
        return "media_or_design"
    if ext in {"doc", "xls", "ppt", "mpp", "vsd", "vsdx", "vdx", "vsdm", "vss"}:
        return "legacy_document_or_diagram"
    if ext in {"db", "dat", "idx", "pack", "sqlite"}:
        return "database_or_index"
    return "binary_or_unknown"


def period_from_mtime(path: Path) -> str:
    try:
        stamp = path.stat().st_mtime
    except OSError:
        return "unknown"
    import datetime as dt

    return dt.datetime.fromtimestamp(stamp).strftime("%Y-%m")


def digest_file(path: Path, relpath: str, full_hash_max_bytes: int, metadata_only: bool) -> dict:
    size = path.stat().st_size
    if metadata_only:
        try:
            mtime_ns = path.stat().st_mtime_ns
        except OSError:
            mtime_ns = 0
        digest = hashlib.sha256()
        digest.update(relpath.encode("utf-8", errors="replace"))
        digest.update(str(size).encode("ascii"))
        digest.update(str(mtime_ns).encode("ascii"))
        return {"hash": digest.hexdigest(), "hash_mode": "metadata_sha256"}
    digest = hashlib.sha256()
    if size <= full_hash_max_bytes:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return {"hash": digest.hexdigest(), "hash_mode": "full_sha256"}

    with path.open("rb") as handle:
        first = handle.read(64 * 1024)
        if size > 128 * 1024:
            handle.seek(max(0, size - 64 * 1024))
        last = handle.read(64 * 1024)
    digest.update(str(size).encode("ascii"))
    digest.update(first)
    digest.update(last)
    return {"hash": digest.hexdigest(), "hash_mode": "partial_size_edges_sha256"}


def decode_text_bytes(data: bytes) -> str:
    return common.decode_bytes(data)


def is_probably_text(data: bytes) -> bool:
    if not data:
        return True
    if b"\x00" in data[:4096]:
        return False
    control = sum(1 for byte in data[:4096] if byte < 9 or 13 < byte < 32)
    return control / max(1, min(len(data), 4096)) < 0.08


def extract_text_for_classification(
    path: Path,
    ext: str,
    kind: str,
    max_bytes: int,
    skip_document_text: bool,
) -> tuple[str, str]:
    try:
        size = path.stat().st_size
        if size > max_bytes and kind != "document":
            return "", "too_large_for_text_read"
        if ext == "eml":
            return extract_eml_text(path, max_bytes), "text_extracted"
        if kind == "document" and ext in {"docx", "pptx", "xlsx", "xlsm", "pdf"}:
            if skip_document_text:
                return "", "document_text_skipped"
            if size > max_bytes:
                return "", "too_large_for_document_extract"
            data = path.read_bytes()
            text, status = common.extract_text_from_attachment(ext, kind, data, max_bytes)
            return text, status
        if ext == "rtf":
            data = path.open("rb").read(min(size, max_bytes))
            return strip_rtf(decode_text_bytes(data)), "text_extracted"
        if kind == "text_or_code":
            data = path.open("rb").read(min(size, max_bytes))
            if ext == "none" and not is_probably_text(data):
                return "", "unknown_binary_without_extension"
            text = decode_text_bytes(data)
            if ext in {"html", "htm", "shtml"}:
                text = common.strip_html(text)
            return common.normalize_space(text), "text_extracted"
    except Exception as exc:  # pragma: no cover - depends on source files
        return "", f"extract_failed:{type(exc).__name__}"
    return "", "unsupported"


def strip_rtf(text: str) -> str:
    text = re.sub(r"\\'[0-9a-fA-F]{2}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return common.normalize_space(text)


def extract_eml_text(path: Path, max_bytes: int) -> str:
    data = path.open("rb").read(max_bytes)
    message = email.message_from_bytes(data, policy=email.policy.default)
    parts: list[str] = []
    subject = message.get("subject")
    if subject:
        parts.append(str(subject))
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type not in {"text/plain", "text/html"}:
                continue
            try:
                payload = part.get_content()
            except Exception:
                continue
            parts.append(common.strip_html(payload) if content_type == "text/html" else str(payload))
    else:
        payload = message.get_content()
        if message.get_content_type() == "text/html":
            payload = common.strip_html(str(payload))
        parts.append(str(payload))
    return common.normalize_space("\n".join(parts))


def zip_summary(path: Path, max_members: int) -> tuple[dict, str]:
    if safe_extension(path) != "zip":
        return {}, "archive_listing_unsupported"
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            counter: collections.Counter[str] = collections.Counter()
            for info in infos[:max_members]:
                suffix = Path(info.filename).suffix.lower().lstrip(".") or "none"
                suffix = re.sub(r"[^a-z0-9_+-]+", "_", suffix)[:40] or "custom"
                counter[suffix] += 1
            return {
                "archive_member_count": len(infos),
                "archive_member_extension_counts": dict(counter.most_common(30)),
                "archive_listing_truncated": len(infos) > max_members,
            }, "archive_listed"
    except Exception as exc:
        return {}, f"archive_list_failed:{type(exc).__name__}"


def sensitive_flags(relpath: str, text: str, ext: str) -> list[str]:
    flags: list[str] = []
    if SENSITIVE_RE.search(relpath):
        flags.append("path_sensitive_signal")
    if text and (SENSITIVE_RE.search(text) or common.SECRET_LINE_RE.search(text)):
        flags.append("content_sensitive_signal")
    if ext in {"pem", "crt", "csr", "cer", "lic"}:
        flags.append("certificate_or_license_material")
    return sorted(set(flags))


def build_file_record(path: Path, root: Path, args: argparse.Namespace) -> dict:
    relpath = normalized_relpath(path, root)
    ext = safe_extension(path)
    kind = file_kind(ext)
    size = path.stat().st_size
    digest = digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash)
    text, text_status = extract_text_for_classification(
        path,
        ext,
        kind,
        args.max_text_bytes,
        args.skip_document_text,
    )
    archive_info: dict = {}
    archive_status = ""
    if kind == "archive_bundle" and args.skip_archive_listing:
        archive_status = "archive_listing_skipped"
    elif kind == "archive_bundle":
        archive_info, archive_status = zip_summary(path, args.max_archive_members)
    classify_source = f"{relpath}\n{text}"
    domain_tags, problem_tags = common.classify(classify_source)
    flags = sensitive_flags(relpath, text, ext)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    record = {
        "file_id": "file-" + common.stable_hash(relpath),
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(top),
        "extension": ext,
        "kind": kind,
        "size_bytes": size,
        "period": period_from_mtime(path),
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "sensitive_flags": flags,
        "text_status": text_status,
        "archive_status": archive_status,
        "source_integrity": digest,
    }
    record.update(archive_info)
    return record


def summarize_case(case: dict) -> tuple[str, str, list[str]]:
    domains = case.get("domain_tags", [])
    problems = case.get("problem_tags", [])
    primary_domain = domains[0] if domains else "general_business_context"
    primary_problem = problems[0] if problems else "context_signal"
    situation = (
        f"A source directory cluster captured {primary_domain.replace('_', ' ')} "
        f"artifacts; the dominant signal is {primary_problem.replace('_', ' ')}."
    )
    need = (
        "Future agents should treat this artifact cluster as accumulated product, "
        "operations, customer, and delivery evidence while preserving anonymity."
    )
    implications: list[str] = []
    for domain in domains[:5]:
        implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
    if case.get("sensitive_file_count", 0):
        implications.append(
            "Sensitive access and credential artifacts must become controlled secret-management workflows, never informal documents."
        )
    if not implications:
        implications.append("Keep the artifact cluster traceable for later refinement.")
    return situation, need, list(dict.fromkeys(implications))[:7]


def build_directory_cases(file_records: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for row in file_records:
        by_group[row["top_group_hash"]].append(row)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        kind_counter = collections.Counter(row["kind"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        periods = sorted({row["period"] for row in rows if row["period"] != "unknown"})
        case_id = "dircase-" + common.stable_hash(group_hash)
        case = {
            "case_id": case_id,
            "top_group_hash": group_hash,
            "file_count": len(rows),
            "total_size_bytes": sum(row["size_bytes"] for row in rows),
            "period_start": periods[0] if periods else "unknown",
            "period_end": periods[-1] if periods else "unknown",
            "kind_counts": dict(kind_counter.most_common()),
            "extension_counts": dict(ext_counter.most_common(20)),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "sensitive_file_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_file_ids": [row["file_id"] for row in rows[:50]],
            "evidence_file_id_count": len(rows),
        }
        situation, need, implications = summarize_case(case)
        case.update(
            {
                "anonymized_situation": situation,
                "user_or_business_need": need,
                "platform_implications": implications,
            }
        )
        cases.append(case)
    case_by_group = {case["top_group_hash"]: case["case_id"] for case in cases}
    for row in file_records:
        row["case_id"] = case_by_group[row["top_group_hash"]]
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


def write_docs(output_root: Path, run_dir: Path, manifest: dict, files: list[dict], cases: list[dict]) -> None:
    domain_counts = counter_from_rows(files, "domain_tags")
    problem_counts = counter_from_rows(files, "problem_tags")
    kind_counts = counter_from_rows(files, "kind")
    sensitive_count = sum(1 for row in files if row["sensitive_flags"])
    largest_cases = sorted(cases, key=lambda row: row["file_count"], reverse=True)[:20]

    (run_dir / "coverage.md").write_text(
        f"""# Directory Source Coverage

- Source kind: directory snapshot
- Files indexed: {manifest["files_indexed"]}
- Directory cases: {manifest["directory_case_count"]}
- Total bytes: {manifest["total_size_bytes"]}
- Text/doc artifacts classified: {manifest["text_artifacts_classified"]}
- Text/doc artifacts not classified: {manifest["text_artifacts_not_classified"]}
- Archive bundles indexed: {manifest["archive_bundles_indexed"]}
- Archive bundles listed: {manifest["archive_bundles_listed"]}
- Sensitive-signal files: {sensitive_count}

## Files By Kind

{common.markdown_table(kind_counts, "kind")}

## Files By Domain

{common.markdown_table(domain_counts, "domain")}

## Files By Problem Signal

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )

    (run_dir / "directory-context.md").write_text(
        "# Directory Experience Context\n\n"
        "This run adds an anonymized directory snapshot to the cloud-platform memory. "
        "Raw paths, source text, brand names, provider names, domains, personal names, "
        "and secrets are not copied. Every file is represented by a stable id, hashes, "
        "type, size, period, domain/problem tags, and a case id.\n\n"
        "## Reusable Lessons\n\n"
        "- Product history lives across documents, scripts, proposals, screenshots, media, and archives; agents should treat all of them as evidence, not only polished requirements.\n"
        "- Access and password documents in a product history are signals that a future platform needs managed secrets, ownership, rotation, and audit workflows.\n"
        "- Sales, support, billing, migration, infrastructure, and compliance artifacts should be connected into one customer journey model.\n"
        "- Binary and media artifacts still matter: count them, preserve traceability, and route them to later visual/OCR processing when needed.\n"
        "- Large archive bundles should be inventoried before extraction so later processing can be prioritized without losing coverage.\n\n"
        "## Largest Directory Cases\n\n"
        + "\n".join(
            f"- `{case['case_id']}` ({case['file_count']} files, {case['total_size_bytes']} bytes): {case['anonymized_situation']}"
            for case in largest_cases
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def refresh_root_readme(output_root: Path) -> None:
    runs: list[dict] = []
    for manifest_path in sorted((output_root / "imports").glob("*/manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        run_id = manifest_path.parent.name
        if manifest.get("source_kind") == "legacy_mail_archive":
            summary = (
                f"legacy mail archive import, {manifest.get('parsed_messages', 0)} parsed messages, "
                f"{manifest.get('case_count', 0)} derived cases, "
                f"{manifest.get('attachments_referenced', 0)} referenced attachments"
            )
        elif manifest.get("source_kind") == "directory_snapshot":
            summary = (
                f"directory snapshot import, {manifest.get('files_indexed', 0)} indexed files, "
                f"{manifest.get('directory_case_count', 0)} derived directory cases"
            )
        else:
            summary = f"{manifest.get('source_kind', 'source')} import"
        runs.append({"run_id": run_id, "summary": summary})

    lines = [
        "# Knowledge Context",
        "",
        "This folder is append-only context for future cloud-platform agents. It stores",
        "anonymized experience records, derived cases, and coverage reports. Raw source",
        "messages, source paths, addresses, domains, company names, product names,",
        "provider names, and secrets are intentionally not copied here.",
        "",
        "Current source runs:",
        "",
    ]
    for run in runs:
        lines.append(f"- `{run['run_id']}`: {run['summary']}.")
    lines.extend(
        [
            "",
            "Usage rule for agents: prefer `cloud-experience-context.md` and per-run",
            "`*-context.md` files for principles, then retrieve JSONL case files for",
            "traceable anonymized evidence.",
            "",
        ]
    )
    (output_root / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run_import(args: argparse.Namespace) -> Path:
    source_root = Path(args.source).resolve()
    output_root = Path(args.output).resolve()
    run_id = args.run_id or "directory-snapshot"
    run_dir = common.append_only_run_dir(output_root / "imports", run_id)
    run_dir.mkdir(parents=True)

    file_records: list[dict] = []
    errors: list[dict] = []
    processed = 0
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        processed += 1
        try:
            file_records.append(build_file_record(path, source_root, args))
        except Exception as exc:
            relpath = normalized_relpath(path, source_root)
            errors.append(
                {
                    "file_id": "file-" + common.stable_hash(relpath),
                    "path_hash": common.stable_hash(relpath, 24),
                    "error": type(exc).__name__,
                }
            )
        if args.progress_every and processed % args.progress_every == 0:
            print(
                f"progress files_seen={processed} indexed={len(file_records)} errors={len(errors)}",
                file=sys.stderr,
                flush=True,
            )

    cases = build_directory_cases(file_records)
    text_classified = sum(1 for row in file_records if row["text_status"] == "text_extracted")
    text_supported = sum(
        1
        for row in file_records
        if row["kind"] in {"text_or_code", "document"} or row["extension"] == "eml"
    )
    archive_bundles = [row for row in file_records if row["kind"] == "archive_bundle"]
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_snapshot",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "files_indexed": len(file_records),
        "files_failed": len(errors),
        "directory_case_count": len(cases),
        "total_size_bytes": sum(row["size_bytes"] for row in file_records),
        "text_artifacts_classified": text_classified,
        "text_artifacts_not_classified": max(0, text_supported - text_classified),
        "archive_bundles_indexed": len(archive_bundles),
        "archive_bundles_listed": sum(1 for row in archive_bundles if row["archive_status"] == "archive_listed"),
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_text_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
            "secrets_copied": False,
        },
    }

    common.write_jsonl(run_dir / "files.jsonl", file_records)
    common.write_jsonl(run_dir / "directory-cases.jsonl", cases)
    common.write_jsonl(run_dir / "failed-files.jsonl", errors)
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_docs(output_root, run_dir, manifest, file_records, cases)
    refresh_root_readme(output_root)
    issues = common.scan_forbidden(output_root)
    (run_dir / "privacy-scan.json").write_text(
        json.dumps(
            {
                "created_at": common.utc_now_iso(),
                "hit_count": len(issues),
                "privacy_or_vendor_hits": issues,
            },
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
    parser.add_argument("--source", required=True, help="Directory source to index")
    parser.add_argument("--output", default="knowledge-context", help="Knowledge context output directory")
    parser.add_argument("--run-id", default="", help="Append-only run id")
    parser.add_argument("--max-text-bytes", type=int, default=1_500_000)
    parser.add_argument("--full-hash-max-bytes", type=int, default=5_000_000)
    parser.add_argument("--max-archive-members", type=int, default=20_000)
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--skip-archive-listing", action="store_true")
    parser.add_argument("--skip-document-text", action="store_true")
    parser.add_argument("--metadata-only-hash", action="store_true")
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
