#!/usr/bin/env python3
"""Append a safe media/design metadata batch from a directory source.

The batch records visual/audio/design structure only. It does not run OCR,
does not copy EXIF text, raw paths, file names, URLs, domains, people, provider
names, brand names, source text, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import re
import sys
import warnings
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


warnings.simplefilter("ignore", Image.DecompressionBombWarning)

RASTER_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "tif", "tiff", "bmp", "ico", "icns"}
VECTOR_EXTENSIONS = {"svg", "svgz", "eps", "ps"}
VIDEO_EXTENSIONS = {"mp4", "mov", "m4v", "avi", "flv", "wmv", "swf"}
AUDIO_EXTENSIONS = {"wav", "mp3", "m4a", "aif", "flac", "ogg"}
FONT_EXTENSIONS = {"ttf", "otf", "eot", "woff", "woff2"}
DESIGN_SOURCE_EXTENSIONS = {
    "afassets",
    "afdesign",
    "afpalette",
    "aep",
    "ai",
    "chm",
    "drawing",
    "epub",
    "indb",
    "key",
    "numbers",
    "pages",
    "potx",
    "prproj",
    "psd",
    "xd",
}
PACKAGE_MEDIA_EXTENSIONS = {"dmg", "exe"}
WEB_REFERENCE_EXTENSIONS = {"webloc"}


MEDIA_SIGNAL_KEYWORDS: dict[str, list[str]] = {
    "screen_capture_or_ui": ["screen", "screenshot", "capture", "ui", "interface", "console", "dashboard", "panel"],
    "architecture_diagram": ["diagram", "schema", "scheme", "topology", "architecture", "map", "flow"],
    "product_demo": ["demo", "walkthrough", "recording", "webinar", "presentation", "pitch"],
    "marketing_visual": ["banner", "landing", "ad", "creative", "brand", "logo", "campaign"],
    "training_media": ["training", "lesson", "course", "tutorial", "guide"],
    "support_evidence": ["ticket", "incident", "error", "bug", "issue", "support", "case"],
    "commercial_media": ["price", "pricing", "offer", "proposal", "invoice", "contract"],
    "backup_or_export_media": ["backup", "export", "archive", "dump", "restore", "snapshot"],
    "design_source_asset": ["design", "source", "layout", "prototype", "mockup", "asset"],
    "audio_video_recording": ["audio", "video", "call", "meeting", "recording"],
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


def bucket_dimension(value: int) -> str:
    if value <= 0:
        return "unknown"
    if value < 256:
        return "lt_256_px"
    if value < 800:
        return "lt_800_px"
    if value < 1600:
        return "lt_1600_px"
    if value < 3200:
        return "lt_3200_px"
    if value < 6400:
        return "lt_6400_px"
    return "gte_6400_px"


def bucket_megapixels(width: int, height: int) -> str:
    mp = (width * height) / 1_000_000 if width > 0 and height > 0 else 0
    if mp <= 0:
        return "unknown"
    if mp < 0.5:
        return "lt_0_5_mp"
    if mp < 2:
        return "lt_2_mp"
    if mp < 8:
        return "lt_8_mp"
    if mp < 24:
        return "lt_24_mp"
    return "gte_24_mp"


def aspect_bucket(width: int, height: int) -> str:
    if width <= 0 or height <= 0:
        return "unknown"
    ratio = width / height
    if 0.95 <= ratio <= 1.05:
        return "square"
    if ratio > 1.05:
        if ratio >= 2:
            return "wide_landscape"
        return "landscape"
    if ratio <= 0.5:
        return "tall_portrait"
    return "portrait"


def mode_bucket(mode: str) -> str:
    folded = (mode or "").upper()
    if folded in {"RGBA", "LA", "PA"}:
        return "alpha"
    if folded in {"RGB", "BGR"}:
        return "rgb"
    if folded in {"L", "1"}:
        return "grayscale"
    if folded == "CMYK":
        return "cmyk"
    if folded == "P":
        return "palette"
    return "other_mode"


def media_type(ext: str) -> str:
    if ext in RASTER_IMAGE_EXTENSIONS:
        return "raster_image"
    if ext in VECTOR_EXTENSIONS:
        return "vector_or_print_graphic"
    if ext in VIDEO_EXTENSIONS:
        return "video_recording"
    if ext in AUDIO_EXTENSIONS:
        return "audio_recording"
    if ext in FONT_EXTENSIONS:
        return "font_asset"
    if ext in DESIGN_SOURCE_EXTENSIONS:
        return "design_source"
    if ext in PACKAGE_MEDIA_EXTENSIONS:
        return "package_or_binary_media"
    if ext in WEB_REFERENCE_EXTENSIONS:
        return "web_reference"
    return "other_media_or_design"


def media_signal_tags(classify_text: str, ext: str, kind: str, analysis_status: str) -> list[str]:
    folded = classify_text.lower()
    tags = [
        name
        for name, words in MEDIA_SIGNAL_KEYWORDS.items()
        if any(word in folded for word in words)
    ]
    if kind == "raster_image":
        tags.append("visual_evidence")
    if kind == "vector_or_print_graphic":
        tags.append("vector_or_diagram_asset")
    if kind == "video_recording":
        tags.append("audio_video_recording")
    if kind == "audio_recording":
        tags.append("audio_video_recording")
    if kind == "design_source":
        tags.append("design_source_asset")
    if kind == "font_asset":
        tags.append("font_asset")
    if analysis_status.endswith("metadata_unavailable"):
        tags.append("future_media_processing_backlog")
    return sorted(set(tags or ["general_media_signal"]))


def sensitive_flags(relpath: str, classify_text: str, ext: str) -> list[str]:
    flags: list[str] = []
    if directory_common.SENSITIVE_RE.search(relpath):
        flags.append("path_sensitive_signal")
    if classify_text and (directory_common.SENSITIVE_RE.search(classify_text) or common.SECRET_LINE_RE.search(classify_text)):
        flags.append("content_sensitive_signal")
    if ext in {"webloc"}:
        flags.append("external_reference_signal")
    return sorted(set(flags))


def raster_metadata(path: Path) -> tuple[dict, str]:
    try:
        with Image.open(path) as image:
            width, height = image.size
            frames = int(getattr(image, "n_frames", 1) or 1)
            metadata = {
                "width_bucket": bucket_dimension(width),
                "height_bucket": bucket_dimension(height),
                "aspect_bucket": aspect_bucket(width, height),
                "megapixels_bucket": bucket_megapixels(width, height),
                "mode_bucket": mode_bucket(image.mode),
                "frame_count_bucket": text_common.bucket_count(frames),
                "has_animation_or_pages": frames > 1,
                "has_exif_or_metadata": bool(getattr(image, "info", None)),
            }
            return metadata, "image_metadata_extracted"
    except Exception as exc:
        return {}, f"image_metadata_failed:{type(exc).__name__}"


def read_vector_text(path: Path, ext: str, max_bytes: int) -> tuple[str, str]:
    try:
        size = path.stat().st_size
        if size > max_bytes:
            return "", "vector_text_too_large"
        data = path.read_bytes()
        if ext == "svgz":
            data = gzip.decompress(data)
        text = common.decode_bytes(data[:max_bytes])
        return common.normalize_space(text), "vector_text_indexed"
    except Exception as exc:
        return "", f"vector_text_failed:{type(exc).__name__}"


def vector_metadata(text: str, status: str) -> dict:
    if status != "vector_text_indexed":
        return {}
    folded = text.lower()
    return {
        "has_text_nodes": bool(re.search(r"<text\b|<tspan\b", folded)),
        "has_script_nodes": "<script" in folded,
        "has_external_references": bool(re.search(r"https?://|www\.|href=", folded)),
        "has_filters_or_masks": any(token in folded for token in ["<filter", "<mask", "<clippath"]),
        "vector_complexity_bucket": text_common.bucket_count(len(re.findall(r"<[a-zA-Z]", text))),
    }


def build_media_signal(path: Path, root: Path, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, root)
    ext = directory_common.safe_extension(path)
    kind = media_type(ext)
    size = path.stat().st_size
    metadata: dict = {}
    classify_text = relpath
    if kind == "raster_image":
        metadata, analysis_status = raster_metadata(path)
    elif kind == "vector_or_print_graphic" and ext in {"svg", "svgz"}:
        vector_text, analysis_status = read_vector_text(path, ext, args.max_vector_bytes)
        classify_text = f"{relpath}\n{vector_text}"
        metadata = vector_metadata(vector_text, analysis_status)
    elif kind == "video_recording":
        analysis_status = "video_metadata_unavailable"
    elif kind == "audio_recording":
        analysis_status = "audio_metadata_unavailable"
    elif kind == "design_source":
        analysis_status = "design_source_metadata_unavailable"
    elif kind == "font_asset":
        analysis_status = "font_metadata_unavailable"
    elif kind == "web_reference":
        analysis_status = "web_reference_not_read"
    else:
        analysis_status = "media_metadata_unavailable"
    domain_tags, problem_tags = common.classify(classify_text)
    flags = sensitive_flags(relpath, classify_text, ext)
    tags = media_signal_tags(classify_text, ext, kind, analysis_status)
    structure_tags = [f"extension_{ext}", f"media_type_{kind}", f"status_{analysis_status.split(':', 1)[0]}", f"size_{bucket_bytes(size)}"]
    if metadata.get("has_text_nodes"):
        structure_tags.append("vector_contains_text_nodes")
    if metadata.get("has_external_references"):
        structure_tags.append("vector_contains_external_reference")
    if metadata.get("has_animation_or_pages"):
        structure_tags.append("multi_frame_image")
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    signal = {
        "media_signal_id": "media-" + common.stable_hash(relpath),
        "case_id": "",
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(top),
        "extension": ext,
        "media_type": kind,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(size),
        "analysis_status": analysis_status,
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "media_signal_tags": tags,
        "structure_tags": sorted(set(structure_tags)),
        "sensitive_flags": flags,
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }
    signal.update(metadata)
    return signal


def build_media_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        media_counter = collections.Counter(row["media_type"] for row in rows)
        ext_counter = collections.Counter(row["extension"] for row in rows)
        status_counter = collections.Counter(row["analysis_status"] for row in rows)
        tag_counter = collections.Counter(tag for row in rows for tag in row["media_signal_tags"])
        structure_counter = collections.Counter(tag for row in rows for tag in row["structure_tags"])
        aspect_counter = collections.Counter(row.get("aspect_bucket") for row in rows if row.get("aspect_bucket"))
        primary_media = media_counter.most_common(1)[0][0] if media_counter else "media_or_design"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case_id = "mediacase-" + common.stable_hash(group_hash)
        case = {
            "case_id": case_id,
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "media_type_counts": dict(media_counter.most_common()),
            "extension_counts": dict(ext_counter.most_common(30)),
            "analysis_status_counts": dict(status_counter.most_common()),
            "aspect_bucket_counts": dict(aspect_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "media_signal_tags": [tag for tag, _ in tag_counter.most_common()],
            "structure_tag_counts": dict(structure_counter.most_common(30)),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_media_signal_ids": [row["media_signal_id"] for row in rows[:50]],
            "evidence_media_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A media/design cluster captured {primary_media.replace('_', ' ')} "
                f"evidence for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should use media/design artifacts as evidence for UI, diagrams, "
                "training, demos, support proof, product visuals, and later OCR/visual review."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if media_counter.get("raster_image", 0):
            implications.append("Screenshots and images should feed future OCR/visual review workflows before final product decisions.")
        if media_counter.get("video_recording", 0) or media_counter.get("audio_recording", 0):
            implications.append("Recordings should be queued for safe transcription and summarized into product/support journeys.")
        if media_counter.get("design_source", 0):
            implications.append("Design source assets should be connected to product requirements and UI implementation history.")
        if case["sensitive_signal_count"]:
            implications.append("Media clusters with sensitive signals require redaction and access controls before model training.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve media/design metadata as traceable context and refine with OCR/transcription later."
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
    media_type_counts = counter_from_rows(signals, "media_type")
    extension_counts = counter_from_rows(signals, "extension")
    status_counts = counter_from_rows(signals, "analysis_status")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    media_tag_counts = counter_from_rows(signals, "media_signal_tags")
    aspect_counts = counter_from_rows(signals, "aspect_bucket")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Media Batch Coverage

- Source kind: directory media batch
- Media/design files seen: {manifest["media_like_files_seen"]}
- Media signals written: {manifest["signals_written"]}
- Media cases: {manifest["media_case_count"]}
- Raster image metadata extracted: {manifest["raster_metadata_extracted"]}
- Vector text indexed safely: {manifest["vector_text_indexed"]}
- Media/design items queued for later OCR/transcription/deep inspection: {manifest["future_processing_backlog_count"]}
- Sensitive-signal media files: {manifest["sensitive_signal_count"]}

## Media Types

{common.markdown_table(media_type_counts, "media_type")}

## Extensions

{common.markdown_table(extension_counts, "extension")}

## Analysis Status

{common.markdown_table(status_counts, "status")}

## Media Signals

{common.markdown_table(media_tag_counts, "media_signal")}

## Image Aspect Buckets

{common.markdown_table(aspect_counts, "aspect_bucket")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "media-batch-context.md").write_text(
        "# Directory Media Batch Context\n\n"
        "This run indexes media and design artifacts without copying raw paths, file names, "
        "EXIF text, OCR text, URLs, domains, provider names, people, brand names, or secrets. "
        "Raster images receive safe metadata buckets; vector files are inspected only for "
        "controlled structure signals; audio, video, and design-source files are retained as "
        "explicit future-processing backlog.\n\n"
        "## Agent Use\n\n"
        "- Use `media-cases.jsonl` for media/design evidence about UI, diagrams, demos, training, support proof, and product visuals.\n"
        "- Use `media-signals.jsonl` for stable-id traceability and safe metadata buckets only.\n"
        "- Treat future-processing statuses as OCR/transcription/visual-review backlog, not as missing coverage.\n"
        "- Do not infer brand identity from visual assets unless a future redacted visual pipeline explicitly provides safe tags.\n\n"
        "## Largest Media Cases\n\n"
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
    media_seen = 0
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        ext = directory_common.safe_extension(path)
        if directory_common.file_kind(ext) != "media_or_design":
            continue
        media_seen += 1
        signals.append(build_media_signal(path, source_root, args))
        if args.progress_every and media_seen % args.progress_every == 0:
            print(
                f"progress media_seen={media_seen} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_media_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_media_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_snapshot_run": args.source_snapshot_run,
        "media_like_files_seen": media_seen,
        "signals_written": len(signals),
        "media_case_count": len(cases),
        "raster_metadata_extracted": sum(1 for row in signals if row["analysis_status"] == "image_metadata_extracted"),
        "vector_text_indexed": sum(1 for row in signals if row["analysis_status"] == "vector_text_indexed"),
        "future_processing_backlog_count": sum(1 for row in signals if row["analysis_status"].endswith("metadata_unavailable")),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_vector_bytes": args.max_vector_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_visual_text_copied": False,
            "raw_exif_text_copied": False,
            "ocr_text_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "media-signals.jsonl", signals)
    common.write_jsonl(run_dir / "media-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-media-batch")
    parser.add_argument("--source-snapshot-run", default="directory-snapshot-20260621")
    parser.add_argument("--max-vector-bytes", type=int, default=5 * 1024 * 1024)
    parser.add_argument("--full-hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--metadata-only-hash", action="store_true", default=True)
    parser.add_argument("--progress-every", type=int, default=250)
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
