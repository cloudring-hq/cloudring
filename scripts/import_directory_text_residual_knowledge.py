#!/usr/bin/env python3
"""Append safe structural coverage for text backlog residual artifacts.

The pass refines files that were originally considered text candidates but
whose bounded samples were not text-like. It records signatures, byte-shape
buckets, stable ids, and status fields only. It writes no raw text, paths, file
names, domains, URLs, provider names, people, brand names, vendor names, or
secrets.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_binary_batch_knowledge as binary_common
import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


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


def target_text_residuals(output_root: Path, source_text_backlog_run: str) -> dict[str, dict]:
    source = output_root / "imports" / source_text_backlog_run / "text-backlog-signals.jsonl"
    targets: dict[str, dict] = {}
    for row in read_jsonl(source):
        if row.get("text_backlog_status") == "sample_not_text_like":
            targets[row["path_hash"]] = row
    return targets


def read_probe(path: Path, max_probe_bytes: int) -> tuple[bytes, bool]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        data = handle.read(max_probe_bytes)
    return data, size > max_probe_bytes


def entropy_bucket(data: bytes) -> str:
    return binary_common.entropy_bucket(data)


def byte_shape(data: bytes) -> dict[str, str]:
    if not data:
        return {
            "nul_ratio_bucket": "empty",
            "printable_ratio_bucket": "empty",
            "unique_byte_count_bucket": "0",
        }
    sample = data[:8192]
    nul_ratio = sample.count(0) / max(1, len(sample))
    printable_ratio = sum(1 for byte in sample if byte in {9, 10, 13} or 32 <= byte <= 126) / max(1, len(sample))
    unique_count = len(set(sample))
    def ratio_bucket(value: float) -> str:
        if value == 0:
            return "0"
        if value < 0.05:
            return "lt_5_percent"
        if value < 0.2:
            return "lt_20_percent"
        if value < 0.5:
            return "lt_50_percent"
        if value < 0.8:
            return "lt_80_percent"
        return "gte_80_percent"
    return {
        "nul_ratio_bucket": ratio_bucket(nul_ratio),
        "printable_ratio_bucket": ratio_bucket(printable_ratio),
        "unique_byte_count_bucket": bucket_count(unique_count),
    }


def magic_family(data: bytes) -> str:
    if not data:
        return "empty_artifact"
    if data.startswith(b"PK\x03\x04") or data.startswith(b"PK\x05\x06") or data.startswith(b"PK\x07\x08"):
        return "zip_container"
    if data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "legacy_ole_container"
    if data.startswith(b"\x89PNG") or data.startswith(b"\xff\xd8\xff") or data.startswith(b"GIF8"):
        return "image_signature"
    if data.startswith(b"%PDF"):
        return "pdf_signature"
    if data.startswith(b"bplist"):
        return "binary_property_list"
    if data.startswith(b"SQLite format 3\x00"):
        return "sqlite_database"
    if data.startswith(b"MZ"):
        return "executable_signature"
    if data.startswith(b"\x7fELF"):
        return "elf_signature"
    if data.startswith(b"RIFF"):
        return "riff_container"
    if data.startswith(b"\x1f\x8b"):
        return "gzip_stream"
    if data.startswith(b"Rar!\x1a\x07"):
        return "rar_container"
    if data.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "seven_z_container"
    sample = data[:8192]
    nul_ratio = sample.count(0) / max(1, len(sample))
    printable_ratio = sum(1 for byte in sample if byte in {9, 10, 13} or 32 <= byte <= 126) / max(1, len(sample))
    if len(sample) < 128 and nul_ratio > 0.75:
        return "mostly_null_or_padding"
    if nul_ratio > 0.5:
        return "null_heavy_binary"
    if nul_ratio > 0.2:
        return "null_mixed_binary"
    if printable_ratio > 0.55:
        return "mixed_printable_binary"
    return "unknown_binary_signature"


def residual_status(family: str) -> str:
    if family in {"image_signature", "pdf_signature", "zip_container", "legacy_ole_container", "binary_property_list", "sqlite_database"}:
        return "misrouted_structured_artifact_identified"
    if family in {"null_heavy_binary", "null_mixed_binary", "mostly_null_or_padding"}:
        return "binary_residual_identified"
    if family == "mixed_printable_binary":
        return "mixed_binary_text_candidate_retained"
    return "unknown_binary_residual_retained"


def residual_tags(ext: str, family: str, status: str, prior: dict, truncated: bool) -> list[str]:
    tags = [
        f"extension_{ext}",
        f"magic_{family}",
        f"residual_status_{status}",
        "not_text_like_after_sample_pass",
    ]
    if prior.get("sensitive_flags"):
        tags.append("sensitive_source_signal")
    if truncated:
        tags.append("probe_sample_truncated")
    if family in {"image_signature", "pdf_signature", "zip_container", "legacy_ole_container", "binary_property_list", "sqlite_database"}:
        tags.append("route_to_specialized_artifact_layer")
    if family.startswith("null_") or family == "mostly_null_or_padding":
        tags.append("binary_padding_or_compiled_shape")
    if family == "mixed_printable_binary":
        tags.append("possible_special_decoder_candidate")
    return sorted(set(tags))


def build_text_residual_signal(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    data, truncated = read_probe(path, args.max_probe_bytes)
    family = magic_family(data)
    status = residual_status(family)
    shape = byte_shape(data)
    classify_text = f"{relpath}\n{ext}\n{family}\n{status}"
    domain_tags, problem_tags = common.classify(classify_text)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    return {
        "text_residual_signal_id": "textresidual-" + common.stable_hash(relpath),
        "case_id": "",
        "source_text_backlog_signal_id": prior.get("backlog_signal_id", ""),
        "path_hash": prior.get("path_hash", common.stable_hash(relpath, 24)),
        "top_group_hash": prior.get("top_group_hash", "group-" + common.stable_hash(top)),
        "extension": ext,
        "kind": prior.get("kind", directory_common.file_kind(ext)),
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(path.stat().st_size),
        "prior_text_backlog_status": prior.get("text_backlog_status", ""),
        "prior_target_reason": prior.get("target_reason", ""),
        "prior_byte_profile": prior.get("byte_profile", ""),
        "prior_entropy_bucket": prior.get("entropy_bucket", ""),
        "magic_family": family,
        "residual_status": status,
        "probe_sample_truncated": truncated,
        "byte_shape_buckets": shape,
        "entropy_bucket": entropy_bucket(data),
        "domain_tags": list(dict.fromkeys(list(prior.get("domain_tags") or []) + domain_tags)),
        "problem_tags": list(dict.fromkeys(list(prior.get("problem_tags") or []) + problem_tags)),
        "text_residual_tags": residual_tags(ext, family, status, prior, truncated),
        "sensitive_flags": list(prior.get("sensitive_flags") or []),
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }


def build_text_residual_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        family_counter = collections.Counter(row["magic_family"] for row in rows)
        status_counter = collections.Counter(row["residual_status"] for row in rows)
        tag_counter = collections.Counter(tag for row in rows for tag in row["text_residual_tags"])
        ext_counter = collections.Counter(row["extension"] for row in rows)
        primary_family = family_counter.most_common(1)[0][0] if family_counter else "binary_residual"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "textresidualcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "extension_counts": dict(ext_counter.most_common(30)),
            "magic_family_counts": dict(family_counter.most_common()),
            "residual_status_counts": dict(status_counter.most_common()),
            "text_residual_tags": [tag for tag, _ in tag_counter.most_common()],
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_text_residual_signal_ids": [row["text_residual_signal_id"] for row in rows[:50]],
            "evidence_text_residual_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A text residual cluster preserved {primary_family.replace('_', ' ')} "
                f"structure for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should preserve non-text residual artifacts as evidence of "
                "compiled outputs, binary project state, misrouted structured assets, and migration residue."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if tag_counter.get("route_to_specialized_artifact_layer", 0):
            implications.append("Misrouted structured artifacts should be routed to their specialized safe extractors instead of retried as text.")
        if tag_counter.get("binary_padding_or_compiled_shape", 0):
            implications.append("Null-heavy residuals often represent compiled, cached, or padded artifacts; keep them as operational residue evidence.")
        if tag_counter.get("possible_special_decoder_candidate", 0):
            implications.append("Mixed printable residuals require specialized decoders before any text-derived training use.")
        if case["sensitive_signal_count"]:
            implications.append("Sensitive residual artifacts require access controls and secret-aware handling before deeper analysis.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve residual binary structure and refine only with specialized safe decoders."
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
    family_counts = counter_from_rows(signals, "magic_family")
    status_counts = counter_from_rows(signals, "residual_status")
    ext_counts = counter_from_rows(signals, "extension")
    tag_counts = counter_from_rows(signals, "text_residual_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Text Residual Coverage

- Source kind: directory text residual batch
- Source target signals: {manifest["source_target_signal_count"]}
- Target hashes matched: {manifest["target_hashes_matched"]}
- Text residual signals written: {manifest["signals_written"]}
- Text residual cases: {manifest["text_residual_case_count"]}
- Binary residuals identified: {manifest["binary_residual_identified_count"]}
- Misrouted structured artifacts identified: {manifest["misrouted_structured_artifact_count"]}
- Mixed binary/text candidates retained: {manifest["mixed_binary_text_candidate_count"]}
- Unknown residuals retained: {manifest["unknown_residual_count"]}
- Sensitive-signal residual artifacts: {manifest["sensitive_signal_count"]}

## Magic Families

{common.markdown_table(family_counts, "magic_family")}

## Residual Status

{common.markdown_table(status_counts, "status")}

## Extensions

{common.markdown_table(ext_counts, "extension")}

## Residual Tags

{common.markdown_table(tag_counts, "tag")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}

## Largest Residual Cases

""" + "\n".join(
            f"- `{case['case_id']}` ({case['signal_count']} signals): {case['anonymized_situation']}"
            for case in largest_cases
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "text-residual-context.md").write_text(
        "# Directory Text Residual Context\n\n"
        "This run refines text backlog artifacts whose samples were not text-like. It "
        "records signatures, byte-shape buckets, stable ids, and residual statuses only. "
        "It does not copy raw text, paths, file names, URLs, domains, people, provider "
        "names, brand names, vendor names, or secrets.\n\n"
        "## Agent Use\n\n"
        "- Use `text-residual-cases.jsonl` for non-text residual evidence from prior text candidates.\n"
        "- Use `text-residual-signals.jsonl` only for stable ids, magic families, byte-shape buckets, and routing statuses.\n"
        "- Treat null-heavy, mixed-printable, and misrouted artifacts as retained evidence, not missing text.\n"
        "- Never infer raw source names or content from residual byte-shape buckets.\n",
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
        elif kind == "directory_text_residual_batch":
            summary = (
                f"directory text residual batch, {manifest.get('signals_written', 0)} residual signals, "
                f"{manifest.get('text_residual_case_count', 0)} residual cases"
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
    targets = target_text_residuals(output_root, args.source_text_backlog_run)
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
        signals.append(build_text_residual_signal(path, source_root, prior, args))
        if args.progress_every and len(signals) % args.progress_every == 0:
            print(
                f"progress text_residual_seen={len(signals)} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_text_residual_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_text_residual_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_text_backlog_run": args.source_text_backlog_run,
        "source_target_signal_count": len(targets),
        "target_hashes_matched": len(matched_hashes),
        "target_hashes_unmatched": max(0, len(targets) - len(matched_hashes)),
        "signals_written": len(signals),
        "text_residual_case_count": len(cases),
        "binary_residual_identified_count": sum(
            1 for row in signals if row["residual_status"] == "binary_residual_identified"
        ),
        "misrouted_structured_artifact_count": sum(
            1 for row in signals if row["residual_status"] == "misrouted_structured_artifact_identified"
        ),
        "mixed_binary_text_candidate_count": sum(
            1 for row in signals if row["residual_status"] == "mixed_binary_text_candidate_retained"
        ),
        "unknown_residual_count": sum(
            1 for row in signals if row["residual_status"] == "unknown_binary_residual_retained"
        ),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_probe_bytes": args.max_probe_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_text_copied": False,
            "raw_domains_urls_people_brands_or_vendors_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "text-residual-signals.jsonl", signals)
    common.write_jsonl(run_dir / "text-residual-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-text-residual-batch")
    parser.add_argument("--source-text-backlog-run", default="directory-text-backlog-batch-20260622-02")
    parser.add_argument("--max-probe-bytes", type=int, default=512 * 1024)
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
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
