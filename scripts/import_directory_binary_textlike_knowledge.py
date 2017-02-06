#!/usr/bin/env python3
"""Append safe decoded-metadata coverage for text-like binary artifacts.

The pass refines text-like binary backlog from the binary batch. It decodes
small artifacts fully and large artifacts in bounded chunks for classification
and controlled counters only. It writes no raw decoded text, paths, file names,
domains, URLs, provider names, people, brand names, vendor names, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_binary_batch_knowledge as binary_common
import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


CREDENTIAL_EXTENSIONS = {"pem", "crt", "csr", "cer", "lic"}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def bucket_bytes(value: int) -> str:
    return binary_common.bucket_bytes(value)


def bucket_count(value: int) -> str:
    return text_common.bucket_count(value)


def target_binary_signals(output_root: Path, source_binary_run: str) -> dict[str, dict]:
    source = output_root / "imports" / source_binary_run / "binary-signals.jsonl"
    targets: dict[str, dict] = {}
    for row in read_jsonl(source):
        if "text_like_binary_backlog" in row.get("binary_signal_tags", []):
            targets[row["path_hash"]] = row
    return targets


def read_decoding_bytes(path: Path, max_decode_bytes: int) -> tuple[bytes, str, bool]:
    size = path.stat().st_size
    if size <= max_decode_bytes:
        return path.read_bytes(), "full_file_decoded", False
    chunk = max(1, max_decode_bytes // 3)
    parts: list[bytes] = []
    with path.open("rb") as handle:
        parts.append(handle.read(chunk))
        midpoint = max(0, size // 2 - chunk // 2)
        handle.seek(midpoint)
        parts.append(handle.read(chunk))
        handle.seek(max(0, size - chunk))
        parts.append(handle.read(chunk))
    return b"".join(parts)[:max_decode_bytes], "edge_middle_chunks_decoded", True


def redaction_counts(raw: str, sanitized: str) -> dict[str, str]:
    counts = {
        "raw_chars": len(raw),
        "sanitized_chars": len(sanitized),
        "redaction_markers": len(re.findall(r"\[[a-z_-]+]", sanitized)),
        "line_count": raw.count("\n") + (1 if raw else 0),
        "word_count": len(re.findall(r"\w+", sanitized)),
    }
    return {key: bucket_count(value) for key, value in counts.items()}


def text_shape_tags(text: str, sanitized: str, prior: dict) -> list[str]:
    tags = text_common.structure_tags(sanitized) if sanitized else []
    folded = sanitized.lower()
    if re.search(r"^\s*[{[]", text[:4096]):
        tags.append("json_like_shape")
    if re.search(r"^\s*<", text[:4096]):
        tags.append("markup_like_shape")
    if re.search(r"^\s*[A-Za-z0-9_.-]+\s*=", text, re.MULTILINE):
        tags.append("key_value_shape")
    if re.search(r"\b(function|class|var|const|let|def|import|export)\b", folded):
        tags.append("code_like_shape")
    if "content_sensitive_signal" in prior.get("sensitive_flags", []):
        tags.append("content_sensitive_source_signal")
    if "path_sensitive_signal" in prior.get("sensitive_flags", []):
        tags.append("path_sensitive_source_signal")
    return sorted(set(tags))


def decode_status(ext: str, prior: dict, mode: str, truncated: bool) -> str:
    if ext in CREDENTIAL_EXTENSIONS or "certificate_or_license_material" in prior.get("sensitive_flags", []):
        return "credential_text_excluded_marker_only"
    if "content_sensitive_signal" in prior.get("sensitive_flags", []):
        return "sensitive_text_decoded_for_counts_only"
    if truncated:
        return "large_textlike_binary_chunk_decoded"
    if mode == "full_file_decoded":
        return "textlike_binary_full_decoded"
    return "textlike_binary_chunk_decoded"


def build_binary_textlike_signal(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    size = path.stat().st_size
    if ext in CREDENTIAL_EXTENSIONS or "certificate_or_license_material" in prior.get("sensitive_flags", []):
        status = "credential_text_excluded_marker_only"
        mode = "content_not_decoded"
        truncated = False
        raw_text = ""
        sanitized = ""
        domain_tags = list(prior.get("domain_tags") or [])
        problem_tags = list(prior.get("problem_tags") or [])
        signal_tags = ["credential_text_excluded", "text_like_binary_backlog"]
        structure_tags = ["credential_or_license_text_excluded", f"extension_{ext}"]
        stat_buckets = {"raw_chars": "0", "sanitized_chars": "0", "redaction_markers": "0", "line_count": "0", "word_count": "0"}
    else:
        data, mode, truncated = read_decoding_bytes(path, args.max_decode_bytes)
        raw_text = common.decode_bytes(data)
        raw_text = common.normalize_space(raw_text)
        sanitized = common.sanitize_text(raw_text, max_chars=args.max_sanitized_chars_for_classification)
        status = decode_status(ext, prior, mode, truncated)
        classify_text = f"{relpath}\n{ext}\n{status}\n{sanitized}"
        domain_tags, problem_tags = common.classify(classify_text)
        domain_tags = list(dict.fromkeys(list(prior.get("domain_tags") or []) + domain_tags))
        problem_tags = list(dict.fromkeys(list(prior.get("problem_tags") or []) + problem_tags))
        signal_tags = text_common.signal_tags(sanitized) if sanitized else ["unclassified_textlike_binary"]
        signal_tags = sorted(set(signal_tags + ["text_like_binary_decoded_metadata"]))
        structure_tags = text_shape_tags(raw_text, sanitized, prior)
        structure_tags.extend([f"extension_{ext}", f"decode_mode_{mode}", f"decode_status_{status}"])
        stat_buckets = redaction_counts(raw_text, sanitized)
    if prior.get("sensitive_flags"):
        structure_tags.append("sensitive_source_signal")
    if truncated:
        structure_tags.append("decode_truncated")
    signal = {
        "binary_textlike_signal_id": "binarytextlike-" + common.stable_hash(relpath),
        "case_id": "",
        "source_binary_signal_id": prior.get("binary_signal_id", ""),
        "path_hash": prior.get("path_hash", common.stable_hash(relpath, 24)),
        "top_group_hash": prior.get("top_group_hash", "group-" + common.stable_hash(top)),
        "extension": ext,
        "kind": prior.get("kind", directory_common.file_kind(ext)),
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(size),
        "prior_magic_family": prior.get("magic_family", ""),
        "byte_profile": prior.get("byte_profile", ""),
        "entropy_bucket": prior.get("entropy_bucket", ""),
        "decode_mode": mode,
        "decode_status": status,
        "decode_truncated": truncated,
        "language_hint": text_common.language_hint(sanitized),
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "text_signal_tags": sorted(set(signal_tags)),
        "structure_tags": sorted(set(structure_tags)),
        "sensitive_flags": list(prior.get("sensitive_flags") or []),
        "stat_buckets": stat_buckets,
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }
    return signal


def build_binary_textlike_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["text_signal_tags"])
        structure_counter = collections.Counter(tag for row in rows for tag in row["structure_tags"])
        status_counter = collections.Counter(row["decode_status"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        primary_signal = tag_counter.most_common(1)[0][0] if tag_counter else "text_like_binary"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "binarytextlikecase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "extension_counts": dict(ext_counter.most_common(30)),
            "decode_status_counts": dict(status_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "text_signal_tags": [tag for tag, _ in tag_counter.most_common()],
            "structure_tag_counts": dict(structure_counter.most_common(30)),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_binary_textlike_signal_ids": [row["binary_textlike_signal_id"] for row in rows[:50]],
            "evidence_binary_textlike_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A text-like binary cluster refined {primary_signal.replace('_', ' ')} "
                f"evidence for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should use decoded text-like binary metadata as evidence of "
                "configuration, project state, exports, backups, and operational residue without raw quoting."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if status_counter.get("credential_text_excluded_marker_only", 0):
            implications.append("Credential-like text must remain marker-only and excluded from training payload.")
        if case["sensitive_signal_count"]:
            implications.append("Sensitive text-like artifacts require redaction, access controls, and audit before deeper decoding.")
        if status_counter.get("large_textlike_binary_chunk_decoded", 0):
            implications.append("Large text-like binary artifacts need chunked, deduplicated, redacted ingestion before training use.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve text-like binary metadata and refine only through safe redacted decoders."
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
    status_counts = counter_from_rows(signals, "decode_status")
    ext_counts = counter_from_rows(signals, "extension")
    signal_counts = counter_from_rows(signals, "text_signal_tags")
    structure_counts = counter_from_rows(signals, "structure_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Binary Text-Like Coverage

- Source kind: directory binary text-like batch
- Source target signals: {manifest["source_target_signal_count"]}
- Target hashes matched: {manifest["target_hashes_matched"]}
- Binary text-like signals written: {manifest["signals_written"]}
- Binary text-like cases: {manifest["binary_textlike_case_count"]}
- Full-file decoded for metadata: {manifest["full_file_decoded_count"]}
- Chunk decoded for metadata: {manifest["chunk_decoded_count"]}
- Credential-like text excluded: {manifest["credential_text_excluded_count"]}
- Sensitive-signal artifacts: {manifest["sensitive_signal_count"]}
- Raw decoded text copied: false

## Decode Status

{common.markdown_table(status_counts, "decode_status")}

## Extensions

{common.markdown_table(ext_counts, "extension")}

## Text Signals

{common.markdown_table(signal_counts, "text_signal")}

## Structure Signals

{common.markdown_table(structure_counts, "structure")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "binary-textlike-context.md").write_text(
        "# Directory Binary Text-Like Context\n\n"
        "This run refines text-like binary backlog by decoding for classification and "
        "controlled counters only. It writes no raw decoded text, paths, file names, "
        "domains, URLs, people, provider names, brand names, vendor names, or secrets. "
        "Credential-like text remains marker-only and excluded from decoded content handling.\n\n"
        "## Agent Use\n\n"
        "- Use `binary-textlike-cases.jsonl` for configuration, project-state, export, backup, and operational-residue situations.\n"
        "- Use `binary-textlike-signals.jsonl` only for stable ids, decode statuses, redaction/count buckets, and controlled tags.\n"
        "- Treat sensitive and credential-like statuses as backlog for secret-aware handling, not training payload.\n"
        "- Never reconstruct raw text, paths, source names, domains, brands, or secrets from this layer.\n\n"
        "## Largest Binary Text-Like Cases\n\n"
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
        elif kind == "directory_binary_textlike_batch":
            summary = (
                f"directory binary text-like batch, {manifest.get('signals_written', 0)} decoded-metadata signals, "
                f"{manifest.get('binary_textlike_case_count', 0)} binary text-like cases"
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
        elif kind == "directory_credential_artifact_batch":
            summary = (
                f"directory credential artifact batch, {manifest.get('signals_written', 0)} marker-only signals, "
                f"{manifest.get('credential_artifact_case_count', 0)} credential cases"
            )
        elif kind == "directory_media_backlog_batch":
            summary = (
                f"directory media backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
                f"{manifest.get('media_backlog_case_count', 0)} media backlog cases"
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
        signals.append(build_binary_textlike_signal(path, source_root, prior, args))
        if args.progress_every and len(signals) % args.progress_every == 0:
            print(
                f"progress binary_textlike_seen={len(signals)} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_binary_textlike_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_binary_textlike_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_binary_run": args.source_binary_run,
        "source_target_signal_count": len(targets),
        "target_hashes_matched": len(matched_hashes),
        "target_hashes_unmatched": max(0, len(targets) - len(matched_hashes)),
        "signals_written": len(signals),
        "binary_textlike_case_count": len(cases),
        "full_file_decoded_count": sum(1 for row in signals if row["decode_mode"] == "full_file_decoded"),
        "chunk_decoded_count": sum(1 for row in signals if row["decode_mode"] == "edge_middle_chunks_decoded"),
        "credential_text_excluded_count": sum(
            1 for row in signals if row["decode_status"] == "credential_text_excluded_marker_only"
        ),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_decode_bytes": args.max_decode_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_decoded_text_copied": False,
            "raw_domains_urls_people_brands_or_vendors_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "binary-textlike-signals.jsonl", signals)
    common.write_jsonl(run_dir / "binary-textlike-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-binary-textlike-batch")
    parser.add_argument("--source-binary-run", default="directory-binary-batch-20260622")
    parser.add_argument("--max-decode-bytes", type=int, default=512 * 1024)
    parser.add_argument("--max-sanitized-chars-for-classification", type=int, default=100_000)
    parser.add_argument("--full-hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--metadata-only-hash", action="store_true", default=True)
    parser.add_argument("--progress-every", type=int, default=25)
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
