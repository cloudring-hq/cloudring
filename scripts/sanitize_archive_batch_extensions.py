#!/usr/bin/env python3
"""Sanitize archive batch member extension buckets in an existing generated run."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_archive_batch_knowledge as archive_common
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
    if ext in archive_common.SAFE_MEMBER_EXTENSIONS or ext == "none":
        return ext
    if ext.isdigit():
        return "numeric_ext"
    return "custom_ext"


def sanitize_member(row: dict) -> dict:
    ext = sanitize_extension(str(row.get("extension") or "none"))
    kind = directory_common.file_kind(ext)
    tags = [
        tag
        for tag in row.get("structure_tags", [])
        if not tag.startswith("member_extension_") and not tag.startswith("member_kind_")
    ]
    tags.extend([f"member_extension_{ext}", f"member_kind_{kind}"])
    row["extension"] = ext
    row["kind"] = kind
    row["structure_tags"] = sorted(set(tags))
    return row


def rebuild_signals(signals: list[dict], members: list[dict]) -> list[dict]:
    members_by_archive: dict[str, list[dict]] = collections.defaultdict(list)
    for member in members:
        members_by_archive[member["archive_id"]].append(member)
    rebuilt: list[dict] = []
    for signal in signals:
        rows = members_by_archive.get(signal["archive_id"], [])
        member_kind_counter = collections.Counter(row["kind"] for row in rows)
        member_ext_counter = collections.Counter(row["extension"] for row in rows)
        signal["member_kind_counts"] = dict(member_kind_counter.most_common(20))
        signal["member_extension_counts"] = dict(member_ext_counter.most_common(40))
        signal["structure_tags"] = archive_common.archive_structure_tags(
            signal["extension"],
            signal["listing_status"],
            signal["member_count"],
            dict(member_kind_counter),
        )
        rebuilt.append(signal)
    return rebuilt


def run(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    output_root = Path(args.output_root).resolve()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    members = [sanitize_member(row) for row in load_jsonl(run_dir / "archive-members.jsonl")]
    signals = rebuild_signals(load_jsonl(run_dir / "archive-signals.jsonl"), members)
    cases = archive_common.build_archive_cases(signals, members)
    common.write_jsonl(run_dir / "archive-members.jsonl", members)
    common.write_jsonl(run_dir / "archive-signals.jsonl", signals)
    common.write_jsonl(run_dir / "archive-cases.jsonl", cases)
    archive_common.write_docs(output_root, run_dir, manifest, signals, cases, members)
    archive_common.refresh_root_readme(output_root)
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
