#!/usr/bin/env python3
"""Append a safe text-signal batch from a directory source.

This batch reads text-like files for classification, but writes no raw source
paths, names, text snippets, domains, emails, URLs, vendor names, or secrets.
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

import import_directory_knowledge as directory_common
import import_legacy_mail_knowledge as common


TEXT_SIGNAL_KEYWORDS: dict[str, list[str]] = {
    "product_positioning": [
        "value proposition",
        "positioning",
        "roadmap",
        "feature",
        "landing",
        "продукт",
        "позиционир",
        "функцион",
        "ценност",
    ],
    "pricing_packaging": [
        "price",
        "pricing",
        "tariff",
        "plan",
        "calculator",
        "тариф",
        "цена",
        "стоим",
        "калькулятор",
    ],
    "trial_onboarding": [
        "trial",
        "signup",
        "welcome",
        "onboarding",
        "start",
        "пробн",
        "подключ",
        "старт",
        "регистрац",
    ],
    "access_secret_management": [
        "password",
        "passwd",
        "secret",
        "token",
        "credential",
        "ssh",
        "login",
        "парол",
        "секрет",
        "ключ",
        "логин",
        "доступ",
    ],
    "backup_recovery": [
        "backup",
        "restore",
        "snapshot",
        "replication",
        "retention",
        "бэкап",
        "резерв",
        "восстанов",
        "снапшот",
        "репликац",
    ],
    "migration_transfer": [
        "migration",
        "transfer",
        "import",
        "export",
        "sync",
        "миграц",
        "перенос",
        "переезд",
        "импорт",
        "экспорт",
    ],
    "managed_support": [
        "support",
        "ticket",
        "sla",
        "escalation",
        "поддерж",
        "обращен",
        "тикет",
        "эскалац",
    ],
    "incident_outage": [
        "incident",
        "outage",
        "downtime",
        "blackout",
        "unavailable",
        "авар",
        "инцидент",
        "недоступ",
        "простой",
    ],
    "performance_capacity": [
        "performance",
        "capacity",
        "load",
        "latency",
        "benchmark",
        "quota",
        "нагруз",
        "производ",
        "емкост",
        "квот",
        "задерж",
    ],
    "compliance_policy": [
        "compliance",
        "policy",
        "audit",
        "personal data",
        "security",
        "соответств",
        "политик",
        "аудит",
        "персональн",
        "безопас",
    ],
    "billing_contract": [
        "invoice",
        "contract",
        "payment",
        "act",
        "refund",
        "счет",
        "договор",
        "оплат",
        "акт",
        "возврат",
    ],
    "developer_automation": [
        "api",
        "webhook",
        "script",
        "automation",
        "sdk",
        "json",
        "интеграц",
        "автоматизац",
        "скрипт",
    ],
    "network_connectivity": [
        "dns",
        "ip",
        "vpn",
        "ssl",
        "certificate",
        "route",
        "сеть",
        "сертификат",
        "маршрут",
        "домен",
    ],
    "compute_storage": [
        "server",
        "vm",
        "cpu",
        "ram",
        "disk",
        "storage",
        "сервер",
        "ядр",
        "диск",
        "хранилищ",
    ],
    "community_education": [
        "blog",
        "community",
        "webinar",
        "training",
        "guide",
        "article",
        "обуч",
        "статья",
        "сообществ",
        "вебинар",
    ],
    "partner_channel": [
        "partner",
        "reseller",
        "referral",
        "channel",
        "партнер",
        "рефера",
        "канал",
    ],
    "lead_sales": [
        "lead",
        "crm",
        "sale",
        "offer",
        "proposal",
        "лид",
        "продаж",
        "предлож",
        "коммерческ",
    ],
}


STRUCTURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "has_form_fields": re.compile(r"<form\b|input\b|textarea\b|select\b", re.IGNORECASE),
    "has_table_markup": re.compile(r"<table\b|<tr\b|<td\b", re.IGNORECASE),
    "has_script_or_code": re.compile(r"function\b|class\b|def\b|var\b|const\b|=>|#!/"),
    "has_config_shape": re.compile(r"^\s*[A-Za-z0-9_.-]+\s*[:=]", re.MULTILINE),
    "has_currency_signal": re.compile(r"\b(?:usd|eur|rub|руб|₽|\$|€)\b", re.IGNORECASE),
    "has_percent_signal": re.compile(r"\d+(?:[.,]\d+)?\s*%"),
    "has_version_signal": re.compile(r"\b\d+\.\d+(?:\.\d+)?\b"),
}


def bucket_count(value: int) -> str:
    if value <= 0:
        return "0"
    if value <= 10:
        return "1-10"
    if value <= 100:
        return "11-100"
    if value <= 1000:
        return "101-1000"
    if value <= 10000:
        return "1001-10000"
    return "10000+"


def language_hint(text: str) -> str:
    cyr = sum(1 for char in text if "а" <= char.lower() <= "я" or char.lower() == "ё")
    latin = sum(1 for char in text if "a" <= char.lower() <= "z")
    if cyr and latin:
        ratio = cyr / max(1, latin)
        if 0.25 <= ratio <= 4:
            return "mixed_ru_en"
    if cyr > latin:
        return "ru"
    if latin:
        return "en_or_code"
    return "unknown"


def signal_tags(text: str) -> list[str]:
    folded = text.lower()
    tags = [
        name
        for name, words in TEXT_SIGNAL_KEYWORDS.items()
        if any(word.lower() in folded for word in words)
    ]
    return tags or ["general_text_signal"]


def structure_tags(text: str) -> list[str]:
    tags = [name for name, pattern in STRUCTURE_PATTERNS.items() if pattern.search(text)]
    if common.EMAIL_RE.search(text) or common.LOOSE_EMAIL_RE.search(text):
        tags.append("has_email_shape")
    if common.URL_RE.search(text) or common.DOMAIN_RE.search(text):
        tags.append("has_url_or_domain_shape")
    if common.SECRET_LINE_RE.search(text):
        tags.append("has_secret_line_shape")
    return sorted(set(tags))


def extract_text(path: Path, ext: str, max_bytes: int) -> tuple[str, str, bool]:
    size = path.stat().st_size
    if size > max_bytes:
        return "", "too_large_for_batch", False
    try:
        if ext == "eml":
            return directory_common.extract_eml_text(path, max_bytes), "text_extracted", False
        data = path.open("rb").read(max_bytes + 1)
        truncated = len(data) > max_bytes
        data = data[:max_bytes]
        if ext == "none" and not directory_common.is_probably_text(data):
            return "", "unknown_binary_without_extension", truncated
        text = common.decode_bytes(data)
        if ext in {"html", "htm", "shtml"}:
            text = common.strip_html(text)
        else:
            text = common.normalize_space(text)
        return text, "text_extracted", truncated
    except Exception as exc:
        return "", f"extract_failed:{type(exc).__name__}", False


def build_text_signal(path: Path, source_root: Path, args: argparse.Namespace) -> dict | None:
    relpath = directory_common.normalized_relpath(path, source_root)
    ext = directory_common.safe_extension(path)
    kind = directory_common.file_kind(ext)
    if kind != "text_or_code":
        return None
    if path.stat().st_size > args.max_file_bytes:
        return {
            "signal_id": "textsig-" + common.stable_hash(relpath),
            "file_id": "file-" + common.stable_hash(relpath),
            "path_hash": common.stable_hash(relpath, 24),
            "top_group_hash": "group-" + common.stable_hash(relpath.split("/", 1)[0] if "/" in relpath else "<root>"),
            "extension": ext,
            "period": directory_common.period_from_mtime(path),
            "size_bytes": path.stat().st_size,
            "text_status": "too_large_for_batch",
            "language_hint": "unknown",
            "domain_tags": ["general_business_context"],
            "problem_tags": ["context_signal"],
            "text_signal_tags": ["large_text_artifact"],
            "structure_tags": [],
            "sensitive_flags": directory_common.sensitive_flags(relpath, "", ext),
            "stat_buckets": {"chars": "0", "lines": "0", "words": "0"},
        }
    text, status, truncated = extract_text(path, ext, args.max_file_bytes)
    classify_source = f"{relpath}\n{text}"
    domain_tags, problem_tags = common.classify(classify_source)
    stat_buckets = {
        "chars": bucket_count(len(text)),
        "lines": bucket_count(text.count("\n") + (1 if text else 0)),
        "words": bucket_count(len(re.findall(r"\w+", text))),
    }
    flags = directory_common.sensitive_flags(relpath, text, ext)
    if truncated:
        flags = sorted(set(flags + ["text_truncated_for_batch"]))
    return {
        "signal_id": "textsig-" + common.stable_hash(relpath),
        "file_id": "file-" + common.stable_hash(relpath),
        "path_hash": common.stable_hash(relpath, 24),
        "top_group_hash": "group-" + common.stable_hash(relpath.split("/", 1)[0] if "/" in relpath else "<root>"),
        "extension": ext,
        "period": directory_common.period_from_mtime(path),
        "size_bytes": path.stat().st_size,
        "text_status": status,
        "language_hint": language_hint(text),
        "domain_tags": domain_tags,
        "problem_tags": problem_tags,
        "text_signal_tags": signal_tags(text) if text else ["unread_text_signal"],
        "structure_tags": structure_tags(text) if text else [],
        "sensitive_flags": flags,
        "stat_buckets": stat_buckets,
    }


def build_text_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        by_group[signal["top_group_hash"]].append(signal)
    cases: list[dict] = []
    for group_hash, rows in sorted(by_group.items()):
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        signal_counter = collections.Counter(tag for row in rows for tag in row["text_signal_tags"])
        structure_counter = collections.Counter(tag for row in rows for tag in row["structure_tags"])
        periods = sorted({row["period"] for row in rows if row["period"] != "unknown"})
        primary_signal = signal_counter.most_common(1)[0][0] if signal_counter else "general_text_signal"
        primary_domain = domain_counter.most_common(1)[0][0] if domain_counter else "general_business_context"
        primary_problem = problem_counter.most_common(1)[0][0] if problem_counter else "context_signal"
        case = {
            "case_id": "textcase-" + common.stable_hash(group_hash),
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "total_size_bytes": sum(row["size_bytes"] for row in rows),
            "period_start": periods[0] if periods else "unknown",
            "period_end": periods[-1] if periods else "unknown",
            "domain_tags": [tag for tag, _ in domain_counter.most_common()],
            "problem_tags": [tag for tag, _ in problem_counter.most_common()],
            "text_signal_tags": [tag for tag, _ in signal_counter.most_common()],
            "structure_tag_counts": dict(structure_counter.most_common(20)),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_flags"]),
            "evidence_signal_ids": [row["signal_id"] for row in rows[:50]],
            "evidence_signal_id_count": len(rows),
            "anonymized_situation": (
                f"A text artifact cluster captured {primary_signal.replace('_', ' ')} "
                f"within {primary_domain.replace('_', ' ')}; the dominant operational signal is "
                f"{primary_problem.replace('_', ' ')}."
            ),
            "user_or_business_need": (
                "Future agents should use these text-derived signals as product, operations, "
                "support, commercial, and education evidence without reconstructing source identity."
            ),
        }
        implications: list[str] = []
        for domain in case["domain_tags"][:5]:
            implications.extend(common.DOMAIN_IMPLICATIONS.get(domain, []))
        if "access_secret_management" in case["text_signal_tags"]:
            implications.append(
                "Convert informal access artifacts into managed secret, ownership, rotation, and audit workflows."
            )
        if "community_education" in case["text_signal_tags"]:
            implications.append(
                "Treat education and community content as product surface that reduces support load and shapes onboarding."
            )
        case["platform_implications"] = list(dict.fromkeys(implications))[:8] or [
            "Keep the text cluster traceable and refine with deeper extraction later."
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
    text_signal_counts = counter_from_rows(signals, "text_signal_tags")
    structure_counts = counter_from_rows(signals, "structure_tags")
    largest_cases = sorted(cases, key=lambda row: row["signal_count"], reverse=True)[:20]
    (run_dir / "coverage.md").write_text(
        f"""# Directory Text Batch Coverage

- Source kind: directory text batch
- Text-like files seen: {manifest["text_like_files_seen"]}
- Signals written: {manifest["signals_written"]}
- Text extracted: {manifest["text_extracted"]}
- Text skipped or failed: {manifest["text_not_extracted"]}
- Text cases: {manifest["text_case_count"]}
- Sensitive-signal text files: {manifest["sensitive_signal_count"]}

## Signals By Text Theme

{common.markdown_table(text_signal_counts, "text_signal")}

## Signals By Domain

{common.markdown_table(domain_counts, "domain")}

## Signals By Problem

{common.markdown_table(problem_counts, "signal")}

## Structural Signals

{common.markdown_table(structure_counts, "structure")}
""",
        encoding="utf-8",
        newline="\n",
    )
    (run_dir / "text-batch-context.md").write_text(
        "# Directory Text Batch Context\n\n"
        "This run classifies text-like source artifacts without copying raw text, paths, "
        "domains, addresses, provider names, people, or secrets. It adds deeper signals "
        "on product, operations, support, billing, migration, community, and automation themes.\n\n"
        "## Agent Use\n\n"
        "- Use `text-cases.jsonl` when retrieving thematic text evidence for platform design.\n"
        "- Use `text-signals.jsonl` for file-level traceability by stable ids only.\n"
        "- Treat sensitive-signal counts as requirements for managed secrets and audit workflows, not as recoverable secret material.\n"
        "- Prefer recurring themes over isolated artifacts when forming platform requirements.\n\n"
        "## Largest Text Cases\n\n"
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
    text_like_seen = 0
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        ext = directory_common.safe_extension(path)
        if directory_common.file_kind(ext) != "text_or_code":
            continue
        text_like_seen += 1
        signal = build_text_signal(path, source_root, args)
        if signal is not None:
            signals.append(signal)
        if args.progress_every and text_like_seen % args.progress_every == 0:
            print(
                f"progress text_seen={text_like_seen} signals={len(signals)}",
                file=sys.stderr,
                flush=True,
            )
    cases = build_text_cases(signals)
    manifest = {
        "append_only_run_id": run_dir.name,
        "created_at": common.utc_now_iso(),
        "source_kind": "directory_text_batch",
        "source_root_hash": common.stable_hash(str(source_root), 24),
        "source_snapshot_run": args.source_snapshot_run,
        "text_like_files_seen": text_like_seen,
        "signals_written": len(signals),
        "text_extracted": sum(1 for row in signals if row["text_status"] == "text_extracted"),
        "text_not_extracted": sum(1 for row in signals if row["text_status"] != "text_extracted"),
        "text_case_count": len(cases),
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
    common.write_jsonl(run_dir / "text-signals.jsonl", signals)
    common.write_jsonl(run_dir / "text-cases.jsonl", cases)
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
    parser.add_argument("--run-id", default="directory-text-batch")
    parser.add_argument("--source-snapshot-run", default="directory-snapshot-20260621")
    parser.add_argument("--max-file-bytes", type=int, default=262_144)
    parser.add_argument("--progress-every", type=int, default=500)
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
