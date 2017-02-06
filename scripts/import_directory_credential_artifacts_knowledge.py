#!/usr/bin/env python3
"""Append marker-only coverage for credential and certificate-like artifacts.

The pass refines credential/certificate backlog from the binary batch. It
records only controlled markers, count buckets, stable ids, and handling
requirements. It writes no raw paths, file names, key material, certificate
subject or issuer values, license text, payload text, domains, URLs, provider
names, people, brand names, vendor names, or secrets.
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


PEM_BEGIN_RE = re.compile(r"-----BEGIN ([A-Z0-9 ]{3,80})-----")


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
        if "credential_or_certificate_artifact" in row.get("binary_signal_tags", []):
            targets[row["path_hash"]] = row
    return targets


def read_limited(path: Path, limit: int) -> tuple[bytes, bool]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        data = handle.read(limit)
    return data, size > limit


def normalized_block_type(label: str) -> str:
    folded = label.strip().upper()
    if "ENCRYPTED" in folded and "PRIVATE KEY" in folded:
        return "encrypted_private_key_block"
    if "PRIVATE KEY" in folded:
        return "private_key_block"
    if "PUBLIC KEY" in folded:
        return "public_key_block"
    if "CERTIFICATE REQUEST" in folded or "NEW CERTIFICATE REQUEST" in folded:
        return "certificate_request_block"
    if "CERTIFICATE" in folded:
        return "certificate_block"
    return "other_armor_block"


def marker_profile(path: Path, ext: str, args: argparse.Namespace) -> tuple[dict[str, int], str, list[str], bool]:
    data, truncated = read_limited(path, args.max_marker_bytes)
    text = data.decode("ascii", errors="ignore")
    counts: collections.Counter[str] = collections.Counter()
    tags: list[str] = []
    labels = PEM_BEGIN_RE.findall(text)
    for label in labels:
        counts[normalized_block_type(label)] += 1
    if counts:
        status = "armor_markers_counted"
        tags.append("armor_markers_present")
    else:
        status = "binary_or_text_marker_retained"
    if counts.get("private_key_block") or counts.get("encrypted_private_key_block"):
        tags.append("private_key_marker_present")
    if counts.get("encrypted_private_key_block") or "Proc-Type: 4,ENCRYPTED" in text:
        tags.append("encrypted_key_marker_present")
    if counts.get("certificate_block"):
        tags.append("certificate_marker_present")
    if counts.get("certificate_request_block"):
        tags.append("certificate_request_marker_present")
    if counts.get("public_key_block"):
        tags.append("public_key_marker_present")
    if ext == "lic":
        tags.append("license_or_entitlement_marker")
    line_count = data.count(b"\n") + (1 if data else 0)
    counts["line_count"] = line_count
    if truncated:
        tags.append("marker_scan_truncated")
    return dict(counts), status, sorted(set(tags)), truncated


def marker_count_buckets(counts: dict[str, int]) -> dict[str, str]:
    return {key: bucket_count(value) for key, value in sorted(counts.items()) if value}


def credential_tags(ext: str, status: str, marker_tags: list[str], prior: dict) -> list[str]:
    tags = [
        f"extension_{ext}",
        f"marker_status_{status}",
        "secret_management_required",
        "not_training_payload",
    ]
    tags.extend(marker_tags)
    if prior.get("sensitive_flags"):
        tags.append("sensitive_signal")
    if "content_sensitive_signal" in prior.get("sensitive_flags", []):
        tags.append("content_sensitive_marker")
    if "path_sensitive_signal" in prior.get("sensitive_flags", []):
        tags.append("path_sensitive_marker")
    return sorted(set(tags))


def build_credential_signal(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    counts, status, marker_tags, truncated = marker_profile(path, ext, args)
    classify_text = f"{relpath}\n{ext}\n{status}\n{' '.join(marker_tags)}"
    domain_tags, problem_tags = common.classify(classify_text)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    return {
        "credential_artifact_signal_id": "credential-" + common.stable_hash(relpath),
        "case_id": "",
        "source_binary_signal_id": prior.get("binary_signal_id", ""),
        "path_hash": prior.get("path_hash", common.stable_hash(relpath, 24)),
        "top_group_hash": prior.get("top_group_hash", "group-" + common.stable_hash(top)),
        "extension": ext,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(path.stat().st_size),
        "prior_magic_family": prior.get("magic_family", ""),
        "byte_profile": prior.get("byte_profile", ""),
        "entropy_bucket": prior.get("entropy_bucket", ""),
        "marker_status": status,
        "marker_scan_truncated": truncated,
        "marker_count_buckets": marker_count_buckets(counts),
        "domain_tags": list(dict.fromkeys(list(prior.get("domain_tags") or []) + domain_tags)),
        "problem_tags": list(dict.fromkeys(list(prior.get("problem_tags") or []) + problem_tags)),
        "credential_artifact_tags": credential_tags(ext, status, marker_tags, prior),
        "sensitive_flags": list(prior.get("sensitive_flags") or []),
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }


def build_credential_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        ext_counter = collections.Counter(row["extension"] for row in rows)
        status_counter = collections.Counter(row["marker_status"] for row in rows)
        tag_counter = collections.Counter(tag for row in rows for tag in row["credential_artifact_tags"])
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "credential_marker_retained"
        case = {
            "case_id": "credentialcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "extension_counts": dict(ext_counter.most_common(20)),
            "marker_status_counts": dict(status_counter.most_common()),
            "credential_artifact_tags": [tag for tag, _ in tag_counter.most_common()],
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_credential_artifact_signal_ids": [row["credential_artifact_signal_id"] for row in rows[:50]],
            "evidence_credential_artifact_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A credential artifact cluster preserved {primary_status.replace('_', ' ')} "
                f"evidence for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should model certificate, key, request, and license-like artifacts "
                "as managed secret lifecycle evidence rather than training payload."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if tag_counter.get("private_key_marker_present", 0):
            implications.append("Private-key markers require managed secret storage, rotation, audit, and exclusion from model-training payloads.")
        if tag_counter.get("certificate_marker_present", 0) or tag_counter.get("certificate_request_marker_present", 0):
            implications.append("Certificate/request markers should feed renewal, expiry, ownership, and deployment workflow requirements without copying subject values.")
        if tag_counter.get("license_or_entitlement_marker", 0):
            implications.append("License-like artifacts should be modeled as entitlement evidence without copying license text.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Retain credential artifact markers only and require secret-aware handling before any deeper processing."
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
    status_counts = counter_from_rows(signals, "marker_status")
    tag_counts = counter_from_rows(signals, "credential_artifact_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Credential Artifact Coverage

- Source kind: directory credential artifact batch
- Source target signals: {manifest["source_target_signal_count"]}
- Target hashes matched: {manifest["target_hashes_matched"]}
- Credential artifact signals written: {manifest["signals_written"]}
- Credential artifact cases: {manifest["credential_artifact_case_count"]}
- Armor-marker artifacts: {manifest["armor_marker_artifacts"]}
- Private-key marker artifacts: {manifest["private_key_marker_artifacts"]}
- Certificate/request marker artifacts: {manifest["certificate_or_request_marker_artifacts"]}
- License-like marker artifacts: {manifest["license_like_marker_artifacts"]}
- Truncated marker scans: {manifest["truncated_marker_scan_count"]}
- Sensitive-signal artifacts: {manifest["sensitive_signal_count"]}

## Extensions

{common.markdown_table(ext_counts, "extension")}

## Marker Status

{common.markdown_table(status_counts, "marker_status")}

## Credential Artifact Tags

{common.markdown_table(tag_counts, "tag")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "credential-artifact-context.md").write_text(
        "# Directory Credential Artifact Context\n\n"
        "This run refines credential and certificate-like artifacts from the binary batch. "
        "It records marker-only evidence: controlled armor block types, count buckets, "
        "sensitive handling tags, stable ids, and status fields. It does not copy raw "
        "paths, file names, key material, certificate subject or issuer values, license "
        "text, payload text, URLs, domains, people, provider names, brand names, vendor "
        "names, or secrets.\n\n"
        "## Agent Use\n\n"
        "- Use `credential-artifact-cases.jsonl` for secret-lifecycle and certificate/request/license-like situations.\n"
        "- Use `credential-artifact-signals.jsonl` only for marker counts, stable ids, and handling requirements.\n"
        "- Treat every signal in this layer as excluded from training payload unless a future redaction policy explicitly allows derived metadata.\n"
        "- Never infer identities, domains, issuers, subjects, file names, or secret values from marker buckets.\n\n"
        "## Largest Credential Artifact Cases\n\n"
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
        elif kind == "directory_credential_artifact_batch":
            summary = (
                f"directory credential artifact batch, {manifest.get('signals_written', 0)} marker-only signals, "
                f"{manifest.get('credential_artifact_case_count', 0)} credential cases"
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
        signals.append(build_credential_signal(path, source_root, prior, args))
        if args.progress_every and len(signals) % args.progress_every == 0:
            print(
                f"progress credential_seen={len(signals)} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_credential_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_credential_artifact_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_binary_run": args.source_binary_run,
        "source_target_signal_count": len(targets),
        "target_hashes_matched": len(matched_hashes),
        "target_hashes_unmatched": max(0, len(targets) - len(matched_hashes)),
        "signals_written": len(signals),
        "credential_artifact_case_count": len(cases),
        "armor_marker_artifacts": sum(1 for row in signals if row["marker_status"] == "armor_markers_counted"),
        "private_key_marker_artifacts": sum(
            1 for row in signals if "private_key_marker_present" in row["credential_artifact_tags"]
        ),
        "certificate_or_request_marker_artifacts": sum(
            1
            for row in signals
            if "certificate_marker_present" in row["credential_artifact_tags"]
            or "certificate_request_marker_present" in row["credential_artifact_tags"]
        ),
        "license_like_marker_artifacts": sum(
            1 for row in signals if "license_or_entitlement_marker" in row["credential_artifact_tags"]
        ),
        "truncated_marker_scan_count": sum(1 for row in signals if row["marker_scan_truncated"]),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_marker_bytes": args.max_marker_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_key_material_copied": False,
            "raw_certificate_subject_or_issuer_copied": False,
            "raw_license_text_copied": False,
            "raw_payload_text_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "credential-artifact-signals.jsonl", signals)
    common.write_jsonl(run_dir / "credential-artifact-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-credential-artifact-batch")
    parser.add_argument("--source-binary-run", default="directory-binary-batch-20260622")
    parser.add_argument("--max-marker-bytes", type=int, default=1024 * 1024)
    parser.add_argument("--full-hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--metadata-only-hash", action="store_true", default=True)
    parser.add_argument("--progress-every", type=int, default=5)
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
