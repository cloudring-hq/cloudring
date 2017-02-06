#!/usr/bin/env python3
"""Append a safe document-signal batch from a directory source.

The batch indexes every document-like artifact from the source tree and extracts
text only for supported formats within size limits. Output contains no raw text,
paths, names, domains, emails, URLs, provider names, people, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_directory_knowledge as directory_common
import import_directory_text_batch_knowledge as text_common
import import_legacy_mail_knowledge as common


logging.getLogger("pypdf").setLevel(logging.ERROR)


SUPPORTED_DOCUMENT_EXTENSIONS = {"pdf", "docx", "pptx", "xlsx", "xlsm", "rtf"}
DOCUMENT_SIGNAL_KEYWORDS: dict[str, list[str]] = {
    "commercial_offer": [
        "proposal",
        "offer",
        "quotation",
        "price",
        "pricing",
        "тариф",
        "коммерческ",
        "предлож",
        "стоим",
    ],
    "contract_legal": [
        "contract",
        "agreement",
        "license",
        "terms",
        "договор",
        "лиценз",
        "соглаш",
        "услов",
    ],
    "product_presentation": [
        "presentation",
        "slide",
        "roadmap",
        "feature",
        "deck",
        "презентац",
        "слайд",
        "продукт",
        "функц",
    ],
    "architecture_design": [
        "architecture",
        "design",
        "diagram",
        "scheme",
        "topology",
        "архитект",
        "дизайн",
        "схем",
        "тополог",
    ],
    "operations_runbook": [
        "runbook",
        "procedure",
        "manual",
        "checklist",
        "process",
        "регламент",
        "процесс",
        "инструкц",
        "чеклист",
    ],
    "support_customer_case": [
        "case",
        "support",
        "ticket",
        "customer",
        "incident",
        "кейс",
        "поддерж",
        "клиент",
        "инцидент",
    ],
    "finance_billing": [
        "invoice",
        "payment",
        "bill",
        "act",
        "budget",
        "счет",
        "оплат",
        "акт",
        "бюджет",
    ],
    "compliance_security": [
        "security",
        "audit",
        "compliance",
        "personal data",
        "policy",
        "безопас",
        "аудит",
        "соответств",
        "персональн",
    ],
    "training_enablement": [
        "training",
        "guide",
        "webinar",
        "lesson",
        "обуч",
        "гайд",
        "вебинар",
        "урок",
    ],
    "migration_plan": [
        "migration",
        "transfer",
        "sync",
        "cutover",
        "миграц",
        "перенос",
        "синхрон",
        "переезд",
    ],
    "capacity_performance": [
        "capacity",
        "performance",
        "benchmark",
        "load",
        "latency",
        "емкост",
        "производ",
        "нагруз",
        "задерж",
    ],
    "backup_recovery": [
        "backup",
        "restore",
        "snapshot",
        "replication",
        "бэкап",
        "резерв",
        "восстанов",
        "снапшот",
    ],
    "access_credentials": [
        "password",
        "credential",
        "login",
        "token",
        "secret",
        "парол",
        "доступ",
        "логин",
        "секрет",
        "ключ",
    ],
}


def bucket_count(value: int) -> str:
    return text_common.bucket_count(value)


def document_signal_tags(text: str, ext: str, status: str) -> list[str]:
    if status != "text_extracted":
        if ext in SUPPORTED_DOCUMENT_EXTENSIONS:
            return ["unread_supported_document"]
        return ["unsupported_legacy_document"]
    folded = text.lower()
    tags = [
        name
        for name, words in DOCUMENT_SIGNAL_KEYWORDS.items()
        if any(word.lower() in folded for word in words)
    ]
    return tags or ["general_document_signal"]


def document_structure_tags(text: str, ext: str, status: str) -> list[str]:
    tags: list[str] = [f"extension_{ext}"]
    if status != "text_extracted":
        return tags
    tags.extend(text_common.structure_tags(text))
    if len(text) > 50_000:
        tags.append("long_document_text")
    return sorted(set(tags))


def extract_document_text(path: Path, ext: str, max_bytes: int) -> tuple[str, str]:
    size = path.stat().st_size
    if ext not in SUPPORTED_DOCUMENT_EXTENSIONS:
        return "", "unsupported_document_format"
    if size > max_bytes:
        return "", "too_large_for_document_batch"
    try:
        if ext == "rtf":
            return directory_common.strip_rtf(common.decode_bytes(path.read_bytes())), "text_extracted"
        data = path.read_bytes()
        text, status = common.extract_text_from_attachment(ext, "document", data, max_bytes)
        return text, status
    except Exception as exc:
        return "", f"extract_failed:{type(exc).__name__}"


def build_document_signal(path: Path, source_root: Path, args: argparse.Namespace) -> dict | None:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    kind = directory_common.file_kind(ext)
    if kind not in {"document", "legacy_document_or_diagram"}:
        return None
    text, status = extract_document_text(path, ext, args.max_file_bytes)
    classify_source = f"{relpath}\n{text}"
    domain_tags, problem_tags = common.classify(classify_source)
    flags = directory_common.sensitive_flags(relpath, text, ext)
    top = relpath.split("/", 1)[0] if "/" in relpath else "<root>"
    return {
        "signal_id": "docsig-" + common.stable_hash(relpath),
        "file_id": "file-" + common.stable_hash(relpath),
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(top),
        "extension": ext,
        "document_kind": "supported_document" if ext in SUPPORTED_DOCUMENT_EXTENSIONS else "legacy_or_unsupported_document",
        "period": directory_common.period_from_mtime(path),
        "size_bytes": path.stat().st_size,
        "text_status": status,
        "language_hint": text_common.language_hint(text) if text else "unknown",
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "document_signal_tags": document_signal_tags(text, ext, status),
        "structure_tags": document_structure_tags(text, ext, status),
        "sensitive_flags": flags,
        "stat_buckets": {
            "chars": bucket_count(len(text)),
            "lines": bucket_count(text.count("\n") + (1 if text else 0)),
            "words": bucket_count(len(re.findall(r"\w+", text))),
        },
    }


def build_document_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        signal_counter = collections.Counter(tag for row in rows for tag in row["document_signal_tags"])
        structure_counter = collections.Counter(tag for row in rows for tag in row["structure_tags"])
        status_counter = collections.Counter(row["text_status"] for row in rows)
        periods = sorted({row["period"] for row in rows if row["period"] != "unknown"})
        primary_signal = signal_counter.most_common(1)[0][0] if signal_counter else "general_document_signal"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "doccase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "total_size_bytes": sum(row["size_bytes"] for row in rows),
            "period_start": periods[0] if periods else "unknown",
            "period_end": periods[-1] if periods else "unknown",
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "document_signal_tags": [tag for tag, _ in signal_counter.most_common()],
            "structure_tag_counts": dict(structure_counter.most_common(20)),
            "text_status_counts": dict(status_counter.most_common()),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_signal_ids": [row["signal_id"] for row in rows[:50]],
            "evidence_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A document cluster captured {primary_signal.replace('_', ' ')} "
                f"within {primary_domain.replace('_', ' ')}; the dominant operational signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should use document-derived signals as durable evidence of "
                "product, commercial, operations, compliance, support, and architecture work."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if "access_credentials" in case["document_signal_tags"]:
            implications.append(
                "Replace access documents with managed secret storage, rotation, approval, and audit trails."
            )
        if "commercial_offer" in case["document_signal_tags"]:
            implications.append(
                "Connect pricing promises, proposal templates, billing state, and product limits into one controlled workflow."
            )
        if "architecture_design" in case["document_signal_tags"]:
            implications.append(
                "Promote design documents into versioned architecture decisions and deployable platform contracts."
            )
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Keep the document cluster traceable and refine unsupported formats later."
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
    domain_counts = counter_from_rows(signals, "domain_tags")
    problem_counts = counter_from_rows(signals, "problem_tags")
    doc_signal_counts = counter_from_rows(signals, "document_signal_tags")
    status_counts = counter_from_rows(signals, "text_status")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Document Batch Coverage

- Source kind: directory document batch
- Document-like files seen: {manifest["document_like_files_seen"]}
- Signals written: {manifest["signals_written"]}
- Text extracted: {manifest["text_extracted"]}
- Text skipped or failed: {manifest["text_not_extracted"]}
- Document cases: {manifest["document_case_count"]}
- Sensitive-signal documents: {manifest["sensitive_signal_count"]}
- Max file bytes for extraction: {manifest["max_file_bytes"]}

## Signals By Document Theme

{common.markdown_table(doc_signal_counts, "document_signal")}

## Extraction Status

{common.markdown_table(status_counts, "status")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "document-batch-context.md").write_text(
        "# Directory Document Batch Context\n\n"
        "This run classifies document-like artifacts without copying raw document text, "
        "paths, domains, addresses, provider names, people, or secrets. It adds signals "
        "from proposals, presentations, runbooks, architecture materials, billing/legal "
        "documents, support cases, and compliance artifacts.\n\n"
        "## Agent Use\n\n"
        "- Use `document-cases.jsonl` for document-derived cloud product and operations evidence.\n"
        "- Use `document-signals.jsonl` for file-level traceability by stable ids only.\n"
        "- Treat unsupported or too-large document statuses as a queue for later safe extraction, not as missing coverage.\n"
        "- Convert access-credential document signals into product requirements for managed secrets and audit workflows.\n\n"
        "## Largest Document Cases\n\n"
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
    docs_seen = 0
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        ext = directory_common.safe_extension(path)
        if directory_common.file_kind(ext) not in {"document", "legacy_document_or_diagram"}:
            continue
        docs_seen += 1
        signal = build_document_signal(path, source_root, args)
        if signal is not None:
            signals.append(signal)
        if args.progress_every and docs_seen % args.progress_every == 0:
            print(
                f"progress docs_seen={docs_seen} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_document_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_document_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_snapshot_run": args.source_snapshot_run,
        "document_like_files_seen": docs_seen,
        "signals_written": len(signals),
        "text_extracted": sum(1 for row in signals if row["text_status"] == "text_extracted"),
        "text_not_extracted": sum(1 for row in signals if row["text_status"] != "text_extracted"),
        "document_case_count": len(cases),
        "sensitive_signal_count": sum(1 for row in signals if row["sensitive_flags"]),
        "max_file_bytes": args.max_file_bytes,
        "sanitization": {
            "raw_source_paths_copied": False,
            "raw_text_copied": False,
            "secrets_copied": False,
            "brand_or_vendor_names_masked": True,
            "addresses_domains_people_masked": True,
        },
    }
    common.write_jsonl(run_dir / "document-signals.jsonl", signals)
    common.write_jsonl(run_dir / "document-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-document-batch")
    parser.add_argument("--source-snapshot-run", default="directory-snapshot-20260621")
    parser.add_argument("--max-file-bytes", type=int, default=10 * 1024 * 1024)
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
