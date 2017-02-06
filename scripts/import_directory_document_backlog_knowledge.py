#!/usr/bin/env python3
"""Append a safe structural pass for document artifacts without extracted text.

The pass records document/container structure only. It writes no raw document
text, source paths, file names, internal member names, metadata values, domains,
URLs, provider names, people, brand names, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_document_batch_knowledge as document_common
import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional runtime dependency
    PdfReader = None  # type: ignore[assignment]


DOCUMENT_BACKLOG_STATUSES = {
    "extract_failed:AttributeError",
    "extract_failed:BadZipFile",
    "unsupported_document_format",
    "too_large_for_document_batch",
    "extract_failed:KeyError",
    "extract_failed:FileNotDecryptedError",
    "extract_failed:EmptyFileError",
    "extract_failed:PdfStreamError",
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


def read_header(path: Path, size: int = 8192) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def magic_family(header: bytes, ext: str) -> str:
    if header.startswith(b"%PDF"):
        return "pdf_document"
    if header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06") or header.startswith(b"PK\x07\x08"):
        return "zip_document_container"
    if header.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "legacy_ole_container"
    if header.startswith(b"{\\rtf"):
        return "rtf_document"
    if ext in {"doc", "xls", "ppt", "mpp", "vsd", "vss", "vdx", "vsdx", "vsdm"}:
        return "legacy_or_diagram_document"
    return "unknown_document_signature"


def zero_counts() -> dict[str, int]:
    return {
        "generic_member_count": 0,
        "document_body_parts": 0,
        "slide_parts": 0,
        "worksheet_parts": 0,
        "chart_parts": 0,
        "diagram_parts": 0,
        "media_parts": 0,
        "embedded_object_parts": 0,
        "comment_parts": 0,
        "notes_parts": 0,
        "macro_parts": 0,
        "custom_xml_parts": 0,
        "style_or_theme_parts": 0,
    }


def bucketed_counts(counts: dict[str, int]) -> dict[str, str]:
    return {key: text_common.bucket_count(value) for key, value in sorted(counts.items()) if value}


def zip_structure(path: Path) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            counts["generic_member_count"] = len(names)
            for name in names:
                folded = name.lower().replace("\\", "/")
                if folded == "word/document.xml":
                    counts["document_body_parts"] += 1
                if folded.startswith("ppt/slides/slide") and folded.endswith(".xml"):
                    counts["slide_parts"] += 1
                if folded.startswith("xl/worksheets/sheet") and folded.endswith(".xml"):
                    counts["worksheet_parts"] += 1
                if "/charts/" in folded:
                    counts["chart_parts"] += 1
                if "/diagrams/" in folded:
                    counts["diagram_parts"] += 1
                if "/media/" in folded:
                    counts["media_parts"] += 1
                if "/embeddings/" in folded or "oleobject" in folded:
                    counts["embedded_object_parts"] += 1
                if "comment" in folded:
                    counts["comment_parts"] += 1
                if "notesslides" in folded or "notesmasters" in folded:
                    counts["notes_parts"] += 1
                if folded.endswith("vbaproject.bin"):
                    counts["macro_parts"] += 1
                if folded.startswith("customxml/"):
                    counts["custom_xml_parts"] += 1
                if "styles.xml" in folded or "/theme/" in folded:
                    counts["style_or_theme_parts"] += 1
        if counts["slide_parts"]:
            tags.append("presentation_container_structure")
        if counts["worksheet_parts"]:
            tags.append("spreadsheet_container_structure")
        if counts["document_body_parts"]:
            tags.append("word_processing_container_structure")
        if counts["macro_parts"]:
            tags.append("macro_enabled_structure")
        if counts["embedded_object_parts"]:
            tags.append("embedded_objects_structure")
        if counts["media_parts"]:
            tags.append("embedded_media_structure")
        return counts, "zip_structure_extracted", tags
    except Exception as exc:
        return counts, f"zip_structure_failed:{type(exc).__name__}", tags


def pdf_structure(path: Path) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    if PdfReader is None:
        return counts, "pdf_structure_unavailable", tags
    try:
        reader = PdfReader(str(path), strict=False)
        if getattr(reader, "is_encrypted", False):
            tags.append("encrypted_document_structure")
            return counts, "pdf_structure_encrypted", tags
        counts["document_body_parts"] = len(reader.pages)
        tags.append("pdf_page_structure")
        return counts, "pdf_structure_extracted", tags
    except Exception as exc:
        return counts, f"pdf_structure_failed:{type(exc).__name__}", tags


def legacy_structure(ext: str, magic: str) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags = [f"legacy_extension_{ext}"]
    if magic == "legacy_ole_container":
        tags.append("legacy_ole_structure")
        return counts, "legacy_ole_identified", tags
    if ext in {"vsd", "vss", "vdx", "vsdx", "vsdm"}:
        tags.append("diagram_document_structure")
    if ext == "mpp":
        tags.append("project_plan_document_structure")
    return counts, "legacy_structure_identified", tags


def structural_probe(path: Path, ext: str) -> tuple[dict[str, int], str, str, list[str]]:
    try:
        header = read_header(path)
    except Exception as exc:
        return zero_counts(), f"header_read_failed:{type(exc).__name__}", "unknown_document_signature", []
    magic = magic_family(header, ext)
    if magic == "zip_document_container" or ext in {"docx", "pptx", "xlsx", "xlsm", "vsdx"}:
        counts, status, tags = zip_structure(path)
    elif magic == "pdf_document" or ext == "pdf":
        counts, status, tags = pdf_structure(path)
    else:
        counts, status, tags = legacy_structure(ext, magic)
    return counts, status, magic, tags


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_targets(output_root: Path, args: argparse.Namespace) -> dict[str, dict]:
    target_path = output_root / "imports" / args.source_document_batch_run / "document-signals.jsonl"
    targets: dict[str, dict] = {}
    for row in load_jsonl(target_path):
        if row.get("text_status") in DOCUMENT_BACKLOG_STATUSES:
            targets[row["path_hash"]] = row
    return targets


def backlog_tags(ext: str, prior_status: str, structure_status: str, magic: str, counts: dict[str, int]) -> list[str]:
    tags = [f"prior_{prior_status.split(':', 1)[0]}", f"magic_{magic}", f"extension_{ext}"]
    if structure_status.endswith("_extracted") or structure_status.endswith("_identified"):
        tags.append("structural_coverage_added")
    if prior_status == "too_large_for_document_batch":
        tags.append("large_document_structured")
    if prior_status == "unsupported_document_format":
        tags.append("legacy_document_structured")
    if counts.get("slide_parts"):
        tags.append("presentation_structure")
    if counts.get("worksheet_parts"):
        tags.append("spreadsheet_structure")
    if counts.get("document_body_parts"):
        tags.append("document_body_structure")
    if counts.get("media_parts"):
        tags.append("embedded_media_structure")
    if counts.get("embedded_object_parts"):
        tags.append("embedded_objects_structure")
    if counts.get("macro_parts"):
        tags.append("macro_enabled_structure")
    if "encrypted" in structure_status.lower():
        tags.append("encrypted_document_backlog")
    if "failed" in structure_status.lower():
        tags.append("structural_probe_failed")
    return sorted(set(tags))


def build_document_backlog_signal(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    size = path.stat().st_size
    counts, structure_status, magic, structural_tags = structural_probe(path, ext)
    prior_domain_tags = list(prior.get("domain_tags") or [])
    prior_problem_tags = list(prior.get("problem_tags") or [])
    classify_source = f"{relpath}\n{ext}\n{magic}\n{structure_status}\n{' '.join(structural_tags)}"
    domain_tags, problem_tags = common.classify(classify_source)
    domain_tags = list(dict.fromkeys(prior_domain_tags + domain_tags))
    problem_tags = list(dict.fromkeys(prior_problem_tags + problem_tags))
    flags = directory_common.sensitive_flags(relpath, "", ext)
    if counts.get("macro_parts"):
        flags = sorted(set(flags + ["macro_enabled_document_signal"]))
    structure_tags = structural_tags + backlog_tags(ext, prior.get("text_status", ""), structure_status, magic, counts)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    return {
        "document_backlog_signal_id": "docbacklog-" + common.stable_hash(relpath),
        "case_id": "",
        "file_id": "file-" + common.stable_hash(relpath),
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(top),
        "extension": ext,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(size),
        "prior_text_status": prior.get("text_status", ""),
        "structure_status": structure_status,
        "magic_family": magic,
        "structure_count_buckets": bucketed_counts(counts),
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "document_backlog_tags": sorted(set(structure_tags)),
        "sensitive_flags": flags,
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }


def build_document_backlog_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["document_backlog_tags"])
        status_counter = collections.Counter(row["structure_status"] for row in rows)
        prior_counter = collections.Counter(row["prior_text_status"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        magic_counter = collections.Counter(row["magic_family"] for row in rows)
        primary_tag = tag_counter.most_common(1)[0][0] if tag_counter else "document_backlog"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "docbacklogcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "extension_counts": dict(ext_counter.most_common(30)),
            "prior_text_status_counts": dict(prior_counter.most_common()),
            "structure_status_counts": dict(status_counter.most_common()),
            "magic_family_counts": dict(magic_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "document_backlog_tags": [tag for tag, _ in tag_counter.most_common()],
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_document_backlog_signal_ids": [row["document_backlog_signal_id"] for row in rows[:50]],
            "evidence_document_backlog_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A document backlog cluster added {primary_tag.replace('_', ' ')} "
                f"evidence for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should preserve document structure even when raw text extraction "
                "is unsafe, unsupported, encrypted, too large, or parser-dependent."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if tag_counter.get("macro_enabled_structure", 0):
            implications.append("Macro-enabled documents require controlled handling and security review before training use.")
        if tag_counter.get("embedded_objects_structure", 0):
            implications.append("Embedded objects in documents should be traced as delivery, evidence, or migration artifacts.")
        if tag_counter.get("encrypted_document_backlog", 0):
            implications.append("Encrypted document signals should remain backlog until keys/permissions are explicitly provided.")
        if case["sensitive_signal_count"]:
            implications.append("Sensitive document backlog signals require redaction and access-control requirements.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Use document structure as traceable context and refine with safer parsers later."
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
    prior_counts = counter_from_rows(signals, "prior_text_status")
    status_counts = counter_from_rows(signals, "structure_status")
    magic_counts = counter_from_rows(signals, "magic_family")
    ext_counts = counter_from_rows(signals, "extension")
    tag_counts = counter_from_rows(signals, "document_backlog_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Document Backlog Coverage

- Source kind: directory document backlog batch
- Source target documents: {manifest["source_target_signal_count"]}
- Target hashes matched: {manifest["target_hashes_matched"]}
- Document backlog signals written: {manifest["signals_written"]}
- Document backlog cases: {manifest["document_backlog_case_count"]}
- Structural coverage added: {manifest["structural_coverage_added"]}
- Structural probe failed: {manifest["structural_probe_failed"]}
- Sensitive-signal backlog documents: {manifest["sensitive_signal_count"]}

## Prior Text Status

{common.markdown_table(prior_counts, "prior_status")}

## Structure Status

{common.markdown_table(status_counts, "structure_status")}

## Magic Families

{common.markdown_table(magic_counts, "magic_family")}

## Extensions

{common.markdown_table(ext_counts, "extension")}

## Document Backlog Tags

{common.markdown_table(tag_counts, "tag")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "document-backlog-context.md").write_text(
        "# Directory Document Backlog Context\n\n"
        "This run adds structural coverage for documents whose raw text was not safely "
        "extracted in the document batch. It records container/page/slide/sheet/media/"
        "macro/embedded-object structure only, without copying raw document text, source "
        "paths, file names, internal member names, metadata values, domains, provider "
        "names, people, brand names, or secrets.\n\n"
        "## Agent Use\n\n"
        "- Use `document-backlog-cases.jsonl` for structural evidence from large, failed, encrypted, and legacy documents.\n"
        "- Use `document-backlog-signals.jsonl` for stable-id traceability and controlled structure buckets only.\n"
        "- Treat structural probe failures as retained backlog, not as dropped experience.\n"
        "- Route macro, embedded-object, encrypted, and sensitive signals to specialized safe handling.\n\n"
        "## Largest Document Backlog Cases\n\n"
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
    targets = load_targets(output_root, args)
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
        signals.append(build_document_backlog_signal(path, source_root, prior, args))
        if args.progress_every and len(signals) % args.progress_every == 0:
            print(
                f"progress document_backlog_seen={len(signals)} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_document_backlog_cases(signals)
    structural_coverage_added = sum(
        1
        for row in signals
        if "structural_coverage_added" in row["document_backlog_tags"]
    )
    structural_probe_failed = sum(
        1
        for row in signals
        if "structural_probe_failed" in row["document_backlog_tags"]
    )
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_document_backlog_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_document_batch_run": args.source_document_batch_run,
        "source_target_signal_count": len(targets),
        "target_hashes_matched": len(matched_hashes),
        "target_hashes_unmatched": max(0, len(targets) - len(matched_hashes)),
        "signals_written": len(signals),
        "document_backlog_case_count": len(cases),
        "structural_coverage_added": structural_coverage_added,
        "structural_probe_failed": structural_probe_failed,
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_document_text_copied": False,
            "raw_internal_member_names_copied": False,
            "raw_metadata_values_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "document-backlog-signals.jsonl", signals)
    common.write_jsonl(run_dir / "document-backlog-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-document-backlog-batch")
    parser.add_argument("--source-document-batch-run", default="directory-document-batch-20260622")
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
