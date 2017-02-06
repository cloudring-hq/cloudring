#!/usr/bin/env python3
"""Sanitize extension buckets in an existing directory snapshot run."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_knowledge as directory_common
import import_legacy_mail_knowledge as common


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sanitize_extension(ext: str) -> str:
    ext = (ext or "none").lower()
    if ext == "none":
        return "none"
    if ext.isdigit():
        return "numeric_ext"
    if ext in directory_common.SAFE_EXTENSIONS:
        return ext
    return "custom_ext"


def rebuild_manifest(manifest: dict, file_records: list[dict], cases: list[dict], errors: list[dict]) -> dict:
    text_classified = sum(1 for row in file_records if row["text_status"] == "text_extracted")
    text_supported = sum(
        1
        for row in file_records
        if row["kind"] in {"text_or_code", "document"} or row["extension"] == "eml"
    )
    archive_bundles = [row for row in file_records if row["kind"] == "archive_bundle"]
    manifest = dict(manifest)
    manifest.update(
        {
            "files_indexed": len(file_records),
            "files_failed": len(errors),
            "directory_case_count": len(cases),
            "total_size_bytes": sum(row["size_bytes"] for row in file_records),
            "text_artifacts_classified": text_classified,
            "text_artifacts_not_classified": max(0, text_supported - text_classified),
            "archive_bundles_indexed": len(archive_bundles),
            "archive_bundles_listed": sum(1 for row in archive_bundles if row["archive_status"] == "archive_listed"),
        }
    )
    manifest.setdefault("sanitization", {})["extension_buckets_sanitized"] = True
    return manifest


def run(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    output_root = Path(args.output_root).resolve()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    file_records = load_jsonl(run_dir / "files.jsonl")
    errors = load_jsonl(run_dir / "failed-files.jsonl") if (run_dir / "failed-files.jsonl").exists() else []
    changed_counter: collections.Counter[str] = collections.Counter()
    for row in file_records:
        old_ext = str(row.get("extension") or "none")
        new_ext = sanitize_extension(old_ext)
        if new_ext != old_ext:
            changed_counter[new_ext] += 1
            row["extension"] = new_ext
            row["kind"] = directory_common.file_kind(new_ext)
    cases = directory_common.build_directory_cases(file_records)
    manifest = rebuild_manifest(manifest, file_records, cases, errors)
    manifest["extension_bucket_sanitization_counts"] = dict(changed_counter.most_common())
    common.write_jsonl(run_dir / "files.jsonl", file_records)
    common.write_jsonl(run_dir / "directory-cases.jsonl", cases)
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    directory_common.write_docs(output_root, run_dir, manifest, file_records, cases)
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        run(parse_args(argv))
    except Exception as exc:
        print(f"sanitize failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
