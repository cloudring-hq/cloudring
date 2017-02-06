#!/usr/bin/env python3
"""Append safe structural coverage for media/design backlog artifacts.

The pass refines media/design artifacts that need later OCR, transcription, or
deep visual/design review. It records only headers, container/chunk/table-count
buckets, stable ids, and status fields. It writes no raw paths, file names,
OCR text, transcripts, EXIF text, visual text, audio text, URLs, domains,
provider names, people, brand names, vendor names, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_archive_batch_knowledge as archive_common
import import_directory_knowledge as directory_common
import import_directory_media_batch_knowledge as media_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


MEDIA_BACKLOG_STATUSES = {
    "video_metadata_unavailable",
    "design_source_metadata_unavailable",
    "audio_metadata_unavailable",
    "font_metadata_unavailable",
    "media_metadata_unavailable",
    "vector_text_too_large",
    "image_metadata_failed:DecompressionBombError",
    "image_metadata_failed:UnidentifiedImageError",
    "web_reference_not_read",
}


MP4_BOXES = {
    "ftyp",
    "moov",
    "mdat",
    "mvhd",
    "trak",
    "tkhd",
    "mdia",
    "minf",
    "stbl",
    "free",
    "wide",
}
RIFF_CHUNKS = {"fmt ", "data", "fact", "LIST"}
FLAC_BLOCKS = {
    0: "streaminfo_block",
    1: "padding_block",
    2: "application_block",
    3: "seektable_block",
    4: "comment_block",
    5: "cuesheet_block",
    6: "picture_block",
}
FONT_TABLES = {"cmap", "glyf", "head", "hhea", "hmtx", "loca", "maxp", "name", "OS/2", "post", "CFF "}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_sample(path: Path, limit: int) -> tuple[bytes, bool]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        data = handle.read(limit)
    return data, size > limit


def bucket_bytes(value: int) -> str:
    return media_common.bucket_bytes(value)


def bucket_count(value: int) -> str:
    return text_common.bucket_count(value)


def bucket_dimension(value: int) -> str:
    return media_common.bucket_dimension(value)


def target_media_signals(output_root: Path, source_media_run: str) -> dict[str, dict]:
    source = output_root / "imports" / source_media_run / "media-signals.jsonl"
    targets: dict[str, dict] = {}
    for row in read_jsonl(source):
        if row.get("analysis_status") in MEDIA_BACKLOG_STATUSES:
            targets[row["path_hash"]] = row
    return targets


def zero_counts() -> dict[str, int]:
    return {
        "container_box_count": 0,
        "known_container_box_count": 0,
        "riff_chunk_count": 0,
        "flac_block_count": 0,
        "font_table_count": 0,
        "font_known_table_count": 0,
        "zip_member_count": 0,
        "zip_document_members": 0,
        "zip_media_members": 0,
        "zip_text_members": 0,
        "zip_binary_members": 0,
        "postscript_page_markers": 0,
        "vector_marker_count": 0,
    }


def bucketed_counts(counts: dict[str, int]) -> dict[str, str]:
    return {key: bucket_count(value) for key, value in sorted(counts.items()) if value}


def mp4_box_counts(path: Path, sample: bytes, max_boxes: int) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    offset = 0
    sample_len = len(sample)
    while offset + 8 <= sample_len and counts["container_box_count"] < max_boxes:
        size = struct.unpack(">I", sample[offset : offset + 4])[0]
        box = sample[offset + 4 : offset + 8].decode("ascii", errors="ignore")
        if not box or any(ord(ch) < 32 or ord(ch) > 126 for ch in box):
            break
        counts["container_box_count"] += 1
        if box in MP4_BOXES:
            counts["known_container_box_count"] += 1
            tags.append(f"contains_box_{box}")
        if size == 1:
            if offset + 16 > sample_len:
                break
            size = struct.unpack(">Q", sample[offset + 8 : offset + 16])[0]
        if size < 8:
            break
        offset += int(size)
    if counts["container_box_count"]:
        tags.append("iso_media_boxes_counted")
        return counts, "iso_media_container_counted", sorted(set(tags))
    if path.suffix.lower().lstrip(".") in {"mp4", "m4v", "mov"}:
        return counts, "iso_media_header_retained", ["iso_media_container_retained"]
    return counts, "media_container_retained", []


def riff_counts(sample: bytes) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    if len(sample) < 12 or sample[:4] != b"RIFF":
        return counts, "riff_header_unrecognized", tags
    kind = sample[8:12]
    if kind == b"WAVE":
        tags.append("riff_wave_container")
    offset = 12
    while offset + 8 <= len(sample):
        chunk = sample[offset : offset + 4].decode("ascii", errors="ignore")
        size = struct.unpack("<I", sample[offset + 4 : offset + 8])[0]
        counts["riff_chunk_count"] += 1
        if chunk in RIFF_CHUNKS:
            tags.append(f"contains_riff_chunk_{chunk.strip().lower() or 'data'}")
        if size < 0:
            break
        offset += 8 + int(size) + (int(size) % 2)
        if counts["riff_chunk_count"] >= 200:
            tags.append("riff_chunk_count_truncated")
            break
    return counts, "riff_audio_counted", sorted(set(tags))


def flac_counts(sample: bytes) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    if not sample.startswith(b"fLaC"):
        return counts, "flac_header_unrecognized", tags
    offset = 4
    while offset + 4 <= len(sample):
        header = sample[offset]
        block_type = header & 0x7F
        block_len = int.from_bytes(sample[offset + 1 : offset + 4], "big")
        counts["flac_block_count"] += 1
        tags.append(FLAC_BLOCKS.get(block_type, "other_flac_block"))
        offset += 4 + block_len
        if header & 0x80:
            break
        if counts["flac_block_count"] >= 64:
            tags.append("flac_block_count_truncated")
            break
    return counts, "flac_audio_counted", sorted(set(tags + ["flac_stream_retained"]))


def mp3_markers(sample: bytes) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    if sample.startswith(b"ID3") and len(sample) >= 10:
        tags.append("id3_header_present")
        tags.append("mpeg_audio_stream_retained")
        return counts, "mpeg_audio_header_retained", tags
    if len(sample) >= 2 and sample[0] == 0xFF and (sample[1] & 0xE0) == 0xE0:
        tags.append("mpeg_frame_sync_present")
        return counts, "mpeg_audio_header_retained", tags
    return counts, "audio_header_retained", tags


def aiff_markers(sample: bytes) -> tuple[dict[str, int], str, list[str]]:
    if sample[:4] == b"FORM" and sample[8:12] in {b"AIFF", b"AIFC"}:
        return zero_counts(), "aiff_audio_header_retained", ["aiff_container_retained"]
    return zero_counts(), "audio_header_retained", []


def font_counts(sample: bytes, ext: str) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    if sample.startswith(b"wOFF") or sample.startswith(b"wOF2"):
        if len(sample) >= 14:
            counts["font_table_count"] = struct.unpack(">H", sample[12:14])[0]
        tags.append("webfont_header_retained")
        return counts, "font_header_counted", tags
    if len(sample) >= 12 and (sample[:4] in {b"\x00\x01\x00\x00", b"OTTO", b"true", b"typ1"}):
        num_tables = struct.unpack(">H", sample[4:6])[0]
        counts["font_table_count"] = int(num_tables)
        offset = 12
        for _ in range(min(num_tables, 256)):
            if offset + 16 > len(sample):
                break
            table = sample[offset : offset + 4].decode("latin1", errors="ignore")
            if table in FONT_TABLES:
                counts["font_known_table_count"] += 1
                tags.append(f"font_table_{table.strip().replace('/', '_').lower() or 'standard'}")
            offset += 16
        tags.append("sfnt_font_header_counted")
        return counts, "font_header_counted", sorted(set(tags))
    if ext == "eot":
        return counts, "font_header_retained", ["embedded_font_header_retained"]
    return counts, "font_header_retained", []


def psd_metadata(sample: bytes) -> tuple[dict[str, int], dict[str, str], str, list[str]]:
    counts = zero_counts()
    props: dict[str, str] = {}
    if not sample.startswith(b"8BPS") or len(sample) < 26:
        return counts, props, "design_header_retained", []
    channels = struct.unpack(">H", sample[12:14])[0]
    height = struct.unpack(">I", sample[14:18])[0]
    width = struct.unpack(">I", sample[18:22])[0]
    depth = struct.unpack(">H", sample[22:24])[0]
    color_mode = struct.unpack(">H", sample[24:26])[0]
    props = {
        "width_bucket": bucket_dimension(int(width)),
        "height_bucket": bucket_dimension(int(height)),
        "channel_count_bucket": bucket_count(int(channels)),
        "bit_depth_bucket": bucket_count(int(depth)),
        "color_mode_bucket": bucket_count(int(color_mode)),
    }
    return counts, props, "design_raster_header_counted", ["design_raster_header_counted"]


def postscript_markers(sample: bytes) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    text = sample.decode("latin1", errors="ignore")
    if not text.startswith("%!") and "%%BoundingBox" not in text[:4096]:
        return counts, "print_graphic_header_retained", []
    counts["postscript_page_markers"] = len(re.findall(r"(?m)^%%Page:", text))
    tags = ["print_graphic_markers_counted"]
    if "%%BoundingBox" in text[:8192]:
        tags.append("bounding_box_marker_present")
    return counts, "print_graphic_markers_counted", tags


def vector_markers(sample: bytes, ext: str) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    text = sample.decode("utf-8", errors="ignore").lower()
    tags: list[str] = []
    for token, tag in [
        ("<svg", "svg_root_marker"),
        ("<text", "vector_text_marker_present"),
        ("<image", "vector_image_marker_present"),
        ("<script", "vector_script_marker_present"),
        ("<filter", "vector_filter_marker_present"),
        ("<mask", "vector_mask_marker_present"),
    ]:
        if token in text:
            tags.append(tag)
            counts["vector_marker_count"] += text.count(token)
    if tags:
        return counts, "vector_sample_markers_counted", sorted(set(tags))
    if ext in {"svg", "svgz"}:
        return counts, "vector_sample_retained", ["vector_too_large_retained"]
    return counts, "vector_header_retained", []


def zip_member_counts(path: Path, max_members: int) -> tuple[dict[str, int], str, list[str]]:
    counts = zero_counts()
    tags: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            counts["zip_member_count"] = len(infos)
            for info in infos[:max_members]:
                ext = archive_common.member_extension(info.filename)
                kind = directory_common.file_kind(ext)
                if kind == "document":
                    counts["zip_document_members"] += 1
                elif kind == "media_or_design":
                    counts["zip_media_members"] += 1
                elif kind == "text_or_code":
                    counts["zip_text_members"] += 1
                else:
                    counts["zip_binary_members"] += 1
            tags.append("package_member_counts_available")
            if len(infos) > max_members:
                tags.append("package_member_count_truncated")
            return counts, "package_container_counted", tags
    except Exception as exc:
        return counts, f"package_container_probe_failed:{type(exc).__name__}", tags


def media_backlog_probe(path: Path, ext: str, media_type: str, prior_status: str, args: argparse.Namespace) -> tuple[dict[str, int], dict[str, str], str, str, list[str], bool]:
    sample, truncated = read_sample(path, args.max_probe_bytes)
    counts = zero_counts()
    props: dict[str, str] = {}
    family = "media_design_artifact"
    tags: list[str] = []
    if ext in {"mp4", "m4v", "mov"}:
        counts, status, tags = mp4_box_counts(path, sample, args.max_container_boxes)
        family = "iso_media_container"
    elif ext == "wav":
        counts, status, tags = riff_counts(sample)
        family = "riff_audio_container"
    elif ext in {"mp3", "m4a"}:
        counts, status, tags = mp3_markers(sample)
        family = "audio_stream"
    elif ext in {"aif"}:
        counts, status, tags = aiff_markers(sample)
        family = "aiff_audio_container"
    elif ext == "flac":
        counts, status, tags = flac_counts(sample)
        family = "flac_audio_container"
    elif media_type == "font_asset":
        counts, status, tags = font_counts(sample, ext)
        family = "font_asset"
    elif ext == "psd":
        counts, props, status, tags = psd_metadata(sample)
        family = "design_raster_source"
    elif ext in {"ai", "eps", "ps"}:
        counts, status, tags = postscript_markers(sample)
        family = "print_graphic_source"
    elif ext in {"svg", "svgz"} or prior_status == "vector_text_too_large":
        counts, status, tags = vector_markers(sample, ext)
        family = "vector_graphic_source"
    elif zipfile.is_zipfile(path) and ext in {"epub", "key", "numbers", "pages", "potx"}:
        counts, status, tags = zip_member_counts(path, args.max_package_members)
        family = "package_design_container"
    elif ext == "webloc":
        status = "external_reference_retained_without_url"
        family = "external_reference"
        tags = ["external_reference_without_url"]
    elif sample.startswith(b"MZ"):
        status = "binary_package_header_retained"
        family = "binary_package_media"
        tags = ["binary_package_retained"]
    else:
        status = "generic_media_backlog_retained"
        tags = ["generic_media_backlog_retained"]
    if truncated:
        tags.append("probe_sample_truncated")
    return counts, props, status, family, sorted(set(tags)), truncated


def media_backlog_tags(ext: str, prior_status: str, status: str, family: str, tags: list[str], prior: dict) -> list[str]:
    out = [
        f"extension_{ext}",
        f"prior_{prior_status.split(':', 1)[0]}",
        f"media_family_{family}",
        f"probe_status_{status.split(':', 1)[0]}",
    ]
    out.extend(tags)
    if "failed" in status:
        out.append("probe_failed")
    if prior.get("sensitive_flags"):
        out.append("sensitive_media_signal")
    if prior_status.endswith("metadata_unavailable"):
        out.append("metadata_gap_refined")
    if prior_status.startswith("image_metadata_failed"):
        out.append("image_failure_retained")
    if prior_status == "vector_text_too_large":
        out.append("large_vector_retained")
    return sorted(set(out))


def build_media_backlog_signal(path: Path, source_root: Path, prior: dict, args: argparse.Namespace) -> dict:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    media_type = prior.get("media_type") or media_common.media_type(ext)
    prior_status = str(prior.get("analysis_status") or "")
    counts, props, status, family, probe_tags, truncated = media_backlog_probe(path, ext, media_type, prior_status, args)
    classify_text = f"{relpath}\n{ext}\n{media_type}\n{family}\n{status}\n{' '.join(probe_tags)}"
    domain_tags, problem_tags = common.classify(classify_text)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    signal = {
        "media_backlog_signal_id": "mediabacklog-" + common.stable_hash(relpath),
        "case_id": "",
        "source_media_signal_id": prior.get("media_signal_id", ""),
        "path_hash": prior.get("path_hash", common.stable_hash(relpath, 24)),
        "top_group_hash": prior.get("top_group_hash", "group-" + common.stable_hash(top)),
        "extension": ext,
        "media_type": media_type,
        "period": directory_common.period_from_mtime(path),
        "size_bucket": bucket_bytes(path.stat().st_size),
        "prior_analysis_status": prior_status,
        "probe_status": status,
        "media_family": family,
        "probe_sample_truncated": truncated,
        "structure_count_buckets": bucketed_counts(counts),
        "structure_property_buckets": props,
        "domain_tags": list(dict.fromkeys(list(prior.get("domain_tags") or []) + domain_tags)),
        "problem_tags": list(dict.fromkeys(list(prior.get("problem_tags") or []) + problem_tags)),
        "media_backlog_tags": media_backlog_tags(ext, prior_status, status, family, probe_tags, prior),
        "sensitive_flags": list(prior.get("sensitive_flags") or []),
        "source_integrity": directory_common.digest_file(path, relpath, args.full_hash_max_bytes, args.metadata_only_hash),
    }
    return signal


def build_media_backlog_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        media_counter = collections.Counter(row["media_type"] for row in rows)
        family_counter = collections.Counter(row["media_family"] for row in rows)
        status_counter = collections.Counter(row["probe_status"] for row in rows)
        tag_counter = collections.Counter(tag for row in rows for tag in row["media_backlog_tags"])
        ext_counter = collections.Counter(row["extension"] for row in rows)
        primary_family = family_counter.most_common(1)[0][0] if family_counter else "media_design_artifact"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "mediabacklogcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "media_type_counts": dict(media_counter.most_common()),
            "media_family_counts": dict(family_counter.most_common()),
            "probe_status_counts": dict(status_counter.most_common()),
            "extension_counts": dict(ext_counter.most_common(30)),
            "media_backlog_tags": [tag for tag, _ in tag_counter.most_common()],
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_media_backlog_signal_ids": [row["media_backlog_signal_id"] for row in rows[:50]],
            "evidence_media_backlog_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A media/design backlog cluster preserved {primary_family.replace('_', ' ')} "
                f"structure for {primary_domain.replace('_', ' ')}; the dominant signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should preserve media and design evidence for UI, demos, diagrams, "
                "training, support proof, and product history while deferring OCR/transcription."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if media_counter.get("video_recording", 0) or media_counter.get("audio_recording", 0):
            implications.append("Recordings should be queued for redacted transcription and journey extraction before training use.")
        if media_counter.get("design_source", 0):
            implications.append("Design-source assets should be linked to UI/product requirements through safe structural metadata first.")
        if tag_counter.get("font_header_counted", 0):
            implications.append("Font and asset dependencies should be modeled as packaging and UI delivery constraints without copying names.")
        if case["sensitive_signal_count"]:
            implications.append("Sensitive media/design backlog requires redaction and access controls before visual or transcript processing.")
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Preserve media/design backlog structure and refine with OCR, transcription, or visual review later."
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
    media_counts = counter_from_rows(signals, "media_type")
    family_counts = counter_from_rows(signals, "media_family")
    status_counts = counter_from_rows(signals, "probe_status")
    ext_counts = counter_from_rows(signals, "extension")
    tag_counts = counter_from_rows(signals, "media_backlog_tags")
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Media Backlog Coverage

- Source kind: directory media backlog batch
- Source target signals: {manifest["source_target_signal_count"]}
- Target hashes matched: {manifest["target_hashes_matched"]}
- Media backlog signals written: {manifest["signals_written"]}
- Media backlog cases: {manifest["media_backlog_case_count"]}
- Audio/video structural signals: {manifest["audio_video_structural_signals"]}
- Design/font/package structural signals: {manifest["design_font_package_structural_signals"]}
- Generic retained signals: {manifest["generic_retained_signals"]}
- Probe failures: {manifest["probe_failed_count"]}
- Sensitive-signal artifacts: {manifest["sensitive_signal_count"]}

## Media Types

{common.markdown_table(media_counts, "media_type")}

## Media Families

{common.markdown_table(family_counts, "media_family")}

## Probe Status

{common.markdown_table(status_counts, "probe_status")}

## Extensions

{common.markdown_table(ext_counts, "extension")}

## Media Backlog Tags

{common.markdown_table(tag_counts, "tag")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "media-backlog-context.md").write_text(
        "# Directory Media Backlog Context\n\n"
        "This run refines media/design backlog with structural metadata only. It records "
        "container headers, chunk/table/member-count buckets, marker buckets, stable ids, "
        "and statuses. It does not copy raw paths, file names, OCR text, transcripts, EXIF "
        "text, visual text, audio text, URLs, domains, people, provider names, brand names, "
        "vendor names, or secrets.\n\n"
        "## Agent Use\n\n"
        "- Use `media-backlog-cases.jsonl` for media/design backlog situations around UI, demos, diagrams, training, support proof, and product history.\n"
        "- Use `media-backlog-signals.jsonl` only for stable-id traceability and controlled structure buckets.\n"
        "- Treat audio/video/design/font/vector/image-failure statuses as retained queues for future redacted OCR, transcription, or visual review.\n"
        "- Never infer visual text, speaker text, names, brands, domains, or file names from this layer.\n\n"
        "## Largest Media Backlog Cases\n\n"
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
    targets = target_media_signals(output_root, args.source_media_run)
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
        signals.append(build_media_backlog_signal(path, source_root, prior, args))
        if args.progress_every and len(signals) % args.progress_every == 0:
            print(
                f"progress media_backlog_seen={len(signals)} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_media_backlog_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_media_backlog_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_media_run": args.source_media_run,
        "source_target_signal_count": len(targets),
        "target_hashes_matched": len(matched_hashes),
        "target_hashes_unmatched": max(0, len(targets) - len(matched_hashes)),
        "signals_written": len(signals),
        "media_backlog_case_count": len(cases),
        "audio_video_structural_signals": sum(
            1 for row in signals if row["media_type"] in {"audio_recording", "video_recording"}
        ),
        "design_font_package_structural_signals": sum(
            1
            for row in signals
            if row["media_type"] in {"design_source", "font_asset", "vector_or_print_graphic"}
            or row["media_family"] in {"package_design_container", "print_graphic_source", "font_asset"}
        ),
        "generic_retained_signals": sum(1 for row in signals if row["probe_status"] == "generic_media_backlog_retained"),
        "probe_failed_count": sum(1 for row in signals if "failed" in row["probe_status"]),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_probe_bytes": args.max_probe_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_ocr_text_copied": False,
            "raw_transcripts_copied": False,
            "raw_exif_text_copied": False,
            "raw_visual_text_copied": False,
            "raw_audio_text_copied": False,
            "raw_urls_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "media-backlog-signals.jsonl", signals)
    common.write_jsonl(run_dir / "media-backlog-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-media-backlog-batch")
    parser.add_argument("--source-media-run", default="directory-media-batch-20260622-02")
    parser.add_argument("--max-probe-bytes", type=int, default=1024 * 1024)
    parser.add_argument("--max-container-boxes", type=int, default=400)
    parser.add_argument("--max-package-members", type=int, default=100_000)
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
