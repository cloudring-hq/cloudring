#!/usr/bin/env python3
"""Append a safe backlog pass for large and text-like binary artifacts.

The pass samples bounded chunks for classification only. It writes no raw text,
paths, file names, domains, URLs, provider names, people, brand names, or
secrets.
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


TARGET_KINDS = {"text_or_code", "binary_or_unknown", "database_or_index"}
TEXT_BACKLOG_STATUSES = {"too_large_for_batch", "unknown_binary_without_extension"}


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


def read_bounded_sample(path: Path, max_sample_bytes: int) -> tuple[bytes, str]:
    size = path.stat().st_size
    if size <= max_sample_bytes:
        return path.read_bytes(), "full_file_sampled"
    chunk = max(1, max_sample_bytes // 3)
    parts: list[bytes] = []
    with path.open("rb") as handle:
        parts.append(handle.read(chunk))
        midpoint = max(0, size // 2 - chunk // 2)
        handle.seek(midpoint)
        parts.append(handle.read(chunk))
        handle.seek(max(0, size - chunk))
        parts.append(handle.read(chunk))
    return b"".join(parts)[:max_sample_bytes], "edge_middle_sampled"


def text_readiness(profile: str, data: bytes) -> str:
    if not data:
        return "empty_sample"
    if profile == "text_like_bytes":
        return "safe_text_like_sample"
    if profile == "mixed_bytes" and data[:8192].count(0) == 0:
        return "mixed_text_candidate_sample"
    return "not_text_like_sample"


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_target_reasons(output_root: Path, args: argparse.Namespace) -> dict[str, str]:
    target_reasons: dict[str, str] = {}
    text_signals = output_root / "imports" / args.source_text_batch_run / "text-signals.jsonl"
    binary_signals = output_root / "imports" / args.source_binary_batch_run / "binary-signals.jsonl"
    for row in load_jsonl(text_signals):
        status = row.get("text_status")
        if status not in TEXT_BACKLOG_STATUSES:
            continue
        reason = "large_text_from_previous_batch" if status == "too_large_for_batch" else "unknown_extension_text_candidate"
        target_reasons[row["path_hash"]] = reason
    for row in load_jsonl(binary_signals):
        if row.get("byte_profile") == "text_like_bytes":
            target_reasons.setdefault(row["path_hash"], "binary_or_database_text_probe")
    return target_reasons


def decode_sample_for_classification(data: bytes, ext: str) -> str:
    text = common.decode_bytes(data)
    if ext in {"html", "htm", "shtml"}:
        return common.strip_html(text)
    return common.normalize_space(text)


def backlog_status(kind: str, reason: str, readiness: str, sample_mode: str) -> str:
    if readiness == "empty_sample":
        return "sample_empty"
    if readiness == "not_text_like_sample":
        return "sample_not_text_like"
    if kind == "text_or_code" and reason == "large_text_from_previous_batch":
        return f"large_text_{sample_mode}_classified"
    if kind == "text_or_code":
        return f"unknown_extension_{sample_mode}_classified"
    return f"text_like_binary_{sample_mode}_classified"


def build_backlog_signal(path: Path, source_root: Path, args: argparse.Namespace, reason: str) -> dict | None:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    kind = directory_common.file_kind(ext)
    if kind not in TARGET_KINDS:
        return None
    size = path.stat().st_size
    try:
        sample, sample_mode = read_bounded_sample(path, args.max_sample_bytes)
        profile = binary_common.byte_profile(sample)
        entropy = binary_common.entropy_bucket(sample)
        readiness = text_readiness(profile, sample)
        if readiness == "not_text_like_sample":
            text = ""
        else:
            text = decode_sample_for_classification(sample, ext)
        status = backlog_status(kind, reason, readiness, sample_mode)
    except Exception as exc:
        sample = b""
        profile = "sample_unavailable"
        entropy = "unknown"
        readiness = "sample_unavailable"
        text = ""
        sample_mode = "sample_failed"
        status = f"sample_failed:{type(exc).__name__}"
    classify_source = f"{relpath}\n{ext}\n{kind}\n{reason}\n{profile}\n{text}"
    domain_tags, problem_tags = common.classify(classify_source)
    flags = directory_common.sensitive_flags(relpath, text, ext)
    if readiness == "not_text_like_sample" and kind == "text_or_code":
        flags = sorted(set(flags + ["text_backlog_not_text_like"]))
    signal_tags = text_common.signal_tags(text) if text else ["unclassified_text_backlog"]
    if reason == "large_text_from_previous_batch":
        signal_tags = sorted(set(signal_tags + ["large_text_artifact"]))
    if kind in {"binary_or_unknown", "database_or_index"}:
        signal_tags = sorted(set(signal_tags + ["text_like_binary_backlog"]))
    structure_tags = text_common.structure_tags(text) if text else []
    structure_tags.extend(
        [
            f"extension_{ext}",
            f"kind_{kind}",
            f"profile_{profile}",
            f"entropy_{entropy}",
            f"target_{reason}",
            f"sample_{sample_mode}",
            f"size_{bucket_bytes(size)}",
        ]
    )
    stat_buckets = {
        "sample_bytes": text_common.bucket_count(len(sample)),
        "sample_chars": text_common.bucket_count(len(text)),
        "sample_lines": text_common.bucket_count(text.count("\n") + (1 if text else 0)),
        "sample_words": text_common.bucket_count(len(re.findall(r"\w+", text))),
    }
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    return {
        "backlog_signal_id": "textbacklog-" + common.stable_hash(relpath),
        "case_id": "",
        "file_id": "file-" + common.stable_hash(relpath),
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(top),
        "extension": ext,
        "kind": kind,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(size),
        "target_reason": reason,
        "sample_mode": sample_mode,
        "byte_profile": profile,
        "entropy_bucket": entropy,
        "text_backlog_status": status,
        "language_hint": text_common.language_hint(text),
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "text_signal_tags": sorted(set(signal_tags)),
        "structure_tags": sorted(set(structure_tags)),
        "sensitive_flags": flags,
        "stat_buckets": stat_buckets,
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }


def build_backlog_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        signal_counter = collections.Counter(tag for row in rows for tag in row["text_signal_tags"])
        structure_counter = collections.Counter(tag for row in rows for tag in row["structure_tags"])
        status_counter = collections.Counter(row["text_backlog_status"] for row in rows)
        reason_counter = collections.Counter(row["target_reason"] for row in rows)
        kind_counter = collections.Counter(row["kind"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        primary_signal = signal_counter.most_common(1)[0][0] if signal_counter else "text_backlog"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "textbacklogcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "kind_counts": dict(kind_counter.most_common()),
            "extension_counts": dict(ext_counter.most_common(30)),
            "target_reason_counts": dict(reason_counter.most_common()),
            "status_counts": dict(status_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "text_signal_tags": [tag for tag, _ in signal_counter.most_common()],
            "structure_tag_counts": dict(structure_counter.most_common(30)),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_backlog_signal_ids": [row["backlog_signal_id"] for row in rows[:50]],
            "evidence_backlog_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A text backlog cluster refined {primary_signal.replace('_', ' ')} "
                f"evidence for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should treat large, unknown-extension, and text-like binary "
                "artifacts as operational context only after bounded safe sampling."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if reason_counter.get("large_text_from_previous_batch", 0):
            implications.append("Large text artifacts need chunked ingestion, deduplication, and redaction before training use.")
        if reason_counter.get("binary_or_database_text_probe", 0):
            implications.append("Text-like binary artifacts should be routed through safer decoders instead of raw quoting.")
        if case["sensitive_signal_count"]:
            implications.append("Sensitive text backlog signals must become requirements for secret handling, redaction, and audit controls.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve backlog sampling as traceable context and refine with specialized safe decoders later."
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


def markdown_table(counter: collections.Counter, label: str) -> str:
    return common.markdown_table(counter, label)


def write_docs(output_root: Path, run_dir: Path, manifest: dict, signals: list[dict], cases: list[dict]) -> None:
    status_counts = counter_from_rows(signals, "text_backlog_status")
    reason_counts = counter_from_rows(signals, "target_reason")
    kind_counts = counter_from_rows(signals, "kind")
    profile_counts = counter_from_rows(signals, "byte_profile")
    signal_counts = counter_from_rows(signals, "text_signal_tags")
    structure_counts = counter_from_rows(signals, "structure_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Text Backlog Coverage

- Source kind: directory text backlog batch
- Backlog candidates seen: {manifest["backlog_candidates_seen"]}
- Backlog signals written: {manifest["signals_written"]}
- Backlog cases: {manifest["text_backlog_case_count"]}
- Sample-classified signals: {manifest["sample_classified_count"]}
- Not-text-like samples retained as backlog: {manifest["not_text_like_count"]}
- Sensitive-signal backlog files: {manifest["sensitive_signal_count"]}
- Max sample bytes per file: {manifest["max_sample_bytes"]}

## Target Reasons

{markdown_table(reason_counts, "target_reason")}

## Status

{markdown_table(status_counts, "status")}

## Kinds

{markdown_table(kind_counts, "kind")}

## Byte Profiles

{markdown_table(profile_counts, "byte_profile")}

## Text Signals

{markdown_table(signal_counts, "text_signal")}

## Structural Signals

{markdown_table(structure_counts, "structure")}

## Signals By Domain

{markdown_table(domain_counts, "domain")}

## Signals By Problem

{markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "text-backlog-context.md").write_text(
        "# Directory Text Backlog Context\n\n"
        "This run refines large text artifacts, unknown-extension text candidates, and "
        "text-like binary/database artifacts through bounded sampling only. It does not "
        "copy raw text, source paths, file names, URLs, domains, provider names, people, "
        "brand names, or secrets.\n\n"
        "## Agent Use\n\n"
        "- Use `text-backlog-cases.jsonl` for large/backlog text-derived platform evidence.\n"
        "- Use `text-backlog-signals.jsonl` for stable-id traceability, statuses, and controlled tags only.\n"
        "- Treat `sample_not_text_like` as retained backlog, not as missing source coverage.\n"
        "- Route sensitive backlog signals to redaction, managed secrets, and audit requirements.\n\n"
        "## Largest Text Backlog Cases\n\n"
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
    target_reasons = load_target_reasons(output_root, args)
    signals: list[dict] = []
    candidates_seen = 0
    matched_hashes: set[str] = set()
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        relpath = directory_common.normalized_relpath(path, source_root)
        path_hash = common.stable_hash(relpath, 24)
        reason = target_reasons.get(path_hash)
        if reason is None:
            continue
        ext = directory_common.safe_extension(path)
        kind = directory_common.file_kind(ext)
        if kind not in TARGET_KINDS:
            continue
        matched_hashes.add(path_hash)
        candidates_seen += 1
        signal = build_backlog_signal(path, source_root, args, reason)
        if signal is not None:
            signals.append(signal)
        if args.progress_every and candidates_seen % args.progress_every == 0:
            print(
                f"progress text_backlog_seen={candidates_seen} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_backlog_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_text_backlog_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_text_batch_run": args.source_text_batch_run,
        "source_binary_batch_run": args.source_binary_batch_run,
        "source_target_signal_count": len(target_reasons),
        "target_hashes_matched": len(matched_hashes),
        "target_hashes_unmatched": max(0, len(target_reasons) - len(matched_hashes)),
        "backlog_candidates_seen": candidates_seen,
        "signals_written": len(signals),
        "sample_classified_count": sum(1 for row in signals if row["text_backlog_status"].endswith("_classified")),
        "not_text_like_count": sum(1 for row in signals if row["text_backlog_status"] == "sample_not_text_like"),
        "text_backlog_case_count": len(cases),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_sample_bytes": args.max_sample_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_text_copied": False,
            "sample_text_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "text-backlog-signals.jsonl", signals)
    common.write_jsonl(run_dir / "text-backlog-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-text-backlog-batch")
    parser.add_argument("--source-text-batch-run", default="directory-text-batch-20260622")
    parser.add_argument("--source-binary-batch-run", default="directory-binary-batch-20260622")
    parser.add_argument("--max-sample-bytes", type=int, default=262_144)
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
