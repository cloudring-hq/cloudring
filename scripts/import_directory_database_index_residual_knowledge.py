#!/usr/bin/env python3
"""Append derived residual handling for database/index metadata queues.

This pass reads only the previous safe database/index metadata run. It does
not open source files and does not copy table names, column names, row values,
schema text, payload text, source paths, file names, domains, provider names,
people, brands, vendors, or secrets.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import import_legacy_mail_knowledge as common


CONTROL_REQUIREMENTS = {
    "row_value_exclusion": "exclude raw row values and payload records from agent and training contexts",
    "schema_name_exclusion": "avoid table, column, index, trigger, or view names unless separately redacted",
    "secret_aware_decoder_gate": "require secret-aware routing before deeper decoding of sensitive database/index artifacts",
    "safe_parser_sandbox": "run any future local-store parser in a bounded sandbox with no payload export",
    "metadata_only_inventory": "preserve storage family, size, entropy, and count buckets as inventory evidence",
    "migration_residue_analysis": "treat local stores and generic indexes as migration residue or product-support context",
    "cache_rebuild_policy": "distinguish rebuildable caches from customer-owned state before migration or cleanup",
    "retention_minimization": "avoid long-term retention of decoded local-store content unless there is explicit product need",
    "source_state_separation": "treat content-addressed source/build state differently from customer data stores",
    "billing_context_review": "route billing/commercial context through metadata-only review when database/index artifacts are involved",
    "support_handoff_traceability": "keep stable ids and status buckets so support can hand off cases without raw data",
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def counter_from_rows(rows: list[dict], field: str) -> collections.Counter[str]:
    counter: collections.Counter[str] = collections.Counter()
    for row in rows:
        value = row.get(field)
        if isinstance(value, list):
            counter.update(str(item) for item in value)
        elif isinstance(value, dict):
            counter.update({str(key): int(count) for key, count in value.items()})
        elif value not in (None, ""):
            counter[str(value)] += 1
    return counter


def is_residual_target(row: dict) -> bool:
    return row.get("metadata_status") == "generic_metadata_retained"


def sensitive_route(row: dict) -> bool:
    tags = set(row.get("database_index_tags") or [])
    return bool(row.get("sensitive_flags")) or "sensitive_database_index_signal" in tags


def residual_status(row: dict) -> str:
    sensitive = sensitive_route(row)
    byte_profile = str(row.get("byte_profile") or "")
    storage = str(row.get("storage_family") or "")
    if sensitive and byte_profile == "text_like_bytes":
        return "sensitive_text_like_index_decoder_gate_modeled"
    if sensitive:
        return "sensitive_database_index_decoder_gate_modeled"
    if byte_profile == "text_like_bytes":
        return "generic_text_like_index_decoder_candidate_modeled"
    if storage == "generic_local_store":
        return "generic_local_store_parser_candidate_modeled"
    if byte_profile == "mixed_bytes":
        return "generic_mixed_binary_index_probe_modeled"
    return "generic_binary_index_probe_modeled"


def decoder_route(row: dict, status: str) -> str:
    if status.startswith("sensitive_"):
        return "secret_aware_metadata_only_decoder"
    if "text_like" in status:
        return "redacted_text_like_index_decoder"
    if "local_store" in status:
        return "bounded_local_store_metadata_parser"
    if "mixed_binary" in status:
        return "bounded_mixed_binary_probe"
    return "bounded_binary_index_probe"


def required_controls(row: dict, status: str) -> list[str]:
    controls = {
        "row_value_exclusion",
        "schema_name_exclusion",
        "metadata_only_inventory",
        "support_handoff_traceability",
        "safe_parser_sandbox",
        "retention_minimization",
    }
    if status.startswith("sensitive_"):
        controls.add("secret_aware_decoder_gate")
    if row.get("storage_family") in {"generic_local_store", "generic_database_index_artifact"}:
        controls.update({"migration_residue_analysis", "cache_rebuild_policy"})
    if row.get("storage_family") in {"content_addressed_pack_index", "content_addressed_packfile"}:
        controls.add("source_state_separation")
    if "billing_commercial" in (row.get("domain_tags") or []) or "billing_friction" in (row.get("problem_tags") or []):
        controls.add("billing_context_review")
    return sorted(controls)


def risk_bucket(row: dict, status: str) -> str:
    if status.startswith("sensitive_"):
        return "sensitive_database_index_handling_risk"
    if row.get("byte_profile") == "text_like_bytes":
        return "text_like_database_index_payload_risk"
    if row.get("size_bucket") in {"lt_100_mib", "lt_1_gib", "gte_1_gib"}:
        return "large_database_index_residue_risk"
    return "generic_database_index_residue_risk"


def residual_tags(row: dict, status: str, route: str, controls: list[str], risk: str) -> list[str]:
    tags = [
        "database_index_residual_reviewed",
        "derived_from_metadata_only_signal",
        "not_training_payload",
        f"residual_status_{status}",
        f"decoder_route_{route}",
        f"risk_{risk}",
        f"storage_family_{row.get('storage_family', 'unknown')}",
        f"byte_profile_{row.get('byte_profile', 'unknown')}",
    ]
    tags.extend(f"control_{control}" for control in controls)
    for source_tag in row.get("database_index_tags") or []:
        if source_tag in {
            "generic_index_or_store_metadata",
            "sensitive_database_index_signal",
            "text_like_database_index_backlog",
            "storage_family_generic_database_index_artifact",
            "storage_family_generic_local_store",
        }:
            tags.append(f"source_{source_tag}")
    return sorted(set(tags))


def build_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        if not is_residual_target(row):
            continue
        status = residual_status(row)
        route = decoder_route(row, status)
        controls = required_controls(row, status)
        risk = risk_bucket(row, status)
        signals.append(
            {
                "database_index_residual_signal_id": "dbindexresidual-" + common.stable_hash(row["database_index_signal_id"]),
                "case_id": "",
                "source_database_index_signal_id": row["database_index_signal_id"],
                "source_binary_signal_id": row.get("source_binary_signal_id", ""),
                "path_hash": row.get("path_hash", ""),
                "top_group_hash": row.get("top_group_hash", ""),
                "period": row.get("period", "unknown"),
                "extension": row.get("extension", "unknown"),
                "storage_family": row.get("storage_family", "unknown"),
                "byte_profile": row.get("byte_profile", "unknown"),
                "entropy_bucket": row.get("entropy_bucket", "unknown"),
                "size_bucket": row.get("size_bucket", "unknown"),
                "prior_metadata_status": row.get("metadata_status", "unknown"),
                "prior_magic_family": row.get("prior_magic_family", "unknown"),
                "metadata_count_buckets": row.get("metadata_count_buckets", {}),
                "metadata_property_buckets": row.get("metadata_property_buckets", {}),
                "residual_status": status,
                "decoder_route": route,
                "risk_bucket": risk,
                "required_controls": controls,
                "sensitive_route": sensitive_route(row),
                "domain_tags": row.get("domain_tags", []),
                "problem_tags": row.get("problem_tags", []),
                "database_index_residual_tags": residual_tags(row, status, route, controls, risk),
                "sensitive_flags": sorted(set(list(row.get("sensitive_flags") or []) + (["database_index_residual_sensitive_route"] if sensitive_route(row) else []))),
                "source_integrity": row.get("source_integrity", {}),
            }
        )
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['residual_status']}"
        by_group[key].append(signal)
    cases: list[dict] = []
    for key, rows in sorted(by_group.items()):
        group_hash = key.split(":", 1)[0]
        status_counter = collections.Counter(row["residual_status"] for row in rows)
        storage_counter = collections.Counter(row["storage_family"] for row in rows)
        route_counter = collections.Counter(row["decoder_route"] for row in rows)
        risk_counter = collections.Counter(row["risk_bucket"] for row in rows)
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["database_index_residual_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "database_index_residual_modeled"
        primary_storage = storage_counter.most_common(1)[0][0] if storage_counter else "database_index_artifact"
        implications = [
            "Treat database/index residuals as metadata-only platform evidence, not as decoded data.",
            "Future parser work must preserve row-value and schema-name exclusion unless a separate redaction gate is proven.",
        ]
        if control_counter.get("secret_aware_decoder_gate", 0):
            implications.append("Sensitive database/index artifacts require secret-aware routing before any deeper decoder is attempted.")
        if control_counter.get("cache_rebuild_policy", 0):
            implications.append("Cloud platforms need policy to separate rebuildable local caches from state that must migrate.")
        if control_counter.get("billing_context_review", 0):
            implications.append("Commercial or billing-adjacent index residue should be handled with metadata-only traceability.")
        case = {
            "case_id": "dbindexresidualcase-" + common.stable_hash(key),
            "case_type": "database_index_residual_handling_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
            "storage_family_counts": dict(storage_counter.most_common()),
            "residual_status_counts": dict(status_counter.most_common()),
            "decoder_route_counts": dict(route_counter.most_common()),
            "risk_bucket_counts": dict(risk_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "database_index_residual_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_database_index_residual_signal_ids": [row["database_index_residual_signal_id"] for row in rows[:50]],
            "evidence_database_index_residual_signal_id_count": len(rows),
            "summary": (
                f"A database/index residual cluster modeled {primary_storage.replace('_', ' ')} evidence; "
                f"the dominant residual state is {primary_status.replace('_', ' ')} across {len(rows)} metadata-only signals."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case for safe local-store, cache, index, migration residue, and secret-aware decoder planning "
                "without copying rows, schema names, or payload text."
            ),
        }
        cases.append(case)
        for row in rows:
            row["case_id"] = case["case_id"]
    return cases


def build_control_rows(signals: list[dict]) -> list[dict]:
    by_control: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        for control in signal["required_controls"]:
            by_control[control].append(signal)
    controls: list[dict] = []
    for control, rows in sorted(by_control.items()):
        storage_counter = collections.Counter(row["storage_family"] for row in rows)
        route_counter = collections.Counter(row["decoder_route"] for row in rows)
        controls.append(
            {
                "database_index_residual_control_id": "dbindexcontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(rows),
                "sensitive_signal_count": sum(1 for row in rows if row["sensitive_route"]),
                "storage_family_counts": dict(storage_counter.most_common()),
                "decoder_route_counts": dict(route_counter.most_common()),
                "evidence_database_index_residual_signal_ids": [
                    row["database_index_residual_signal_id"] for row in rows[:50]
                ],
                "agent_use": "Use as a database/index product requirement checkpoint, not as decoded content.",
            }
        )
    return controls


def markdown_counter(counter: collections.Counter[str], label: str) -> str:
    if not counter:
        return "_No rows._"
    lines = [f"| {label} | count |", "| --- | ---: |"]
    for key, count in counter.most_common():
        lines.append(f"| `{key}` | {count} |")
    return "\n".join(lines)


def write_coverage(run_dir: Path, manifest: dict, signals: list[dict]) -> None:
    status_counts = counter_from_rows(signals, "residual_status")
    route_counts = counter_from_rows(signals, "decoder_route")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Database/Index Residual Coverage

- Source kind: directory database/index residual batch
- Source database/index run: `{manifest["source_database_index_run"]}`
- Source generic metadata targets: {manifest["source_generic_metadata_signal_count"]}
- Residual signals written: {manifest["signals_written"]}
- Residual cases: {manifest["database_index_residual_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Sensitive residual routes: {manifest["sensitive_residual_signal_count"]}
- Text-like residual routes: {manifest["text_like_residual_signal_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Residual Status Counts

{markdown_counter(status_counts, "residual_status")}

## Decoder Route Counts

{markdown_counter(route_counts, "decoder_route")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over safe database/index metadata signals.
- It does not open source files or copy row values, schema names, table names,
  column names, payload text, paths, domains, providers, people, brands,
  vendors, or secrets.
- Use these records for parser planning, migration requirements, and
  secret-aware routing, not as decoded database content.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "database-index-residual-context.md").write_text(
        "# Database/Index Residual Context\n\n"
        "This run derives safe handling requirements for database/index artifacts whose first metadata pass "
        "retained generic or sensitive statuses. It records decoder routes, risk buckets, required controls, "
        "and platform implications only. It does not read source files or copy rows, schema names, table names, "
        "column names, payload text, source paths, domains, provider names, people, brands, vendors, or secrets.\n\n"
        "Agent usage:\n\n"
        "- Use `database-index-residual-cases.jsonl` for local-store, cache, index, and migration-residue product situations.\n"
        "- Use `database-index-residual-signals.jsonl` for stable ids, residual statuses, decoder routes, and risk buckets.\n"
        "- Use `database-index-residual-controls.jsonl` as a safe parser and migration-planning checklist.\n"
        "- Never treat this layer as decoded database rows, schema text, or customer payload.\n",
        encoding="utf-8",
    )


def summarize_manifest(run_id: str, manifest: dict) -> str:
    kind = manifest.get("source_kind")
    if kind == "legacy_mail_archive":
        return (
            f"legacy mail archive import, {manifest.get('parsed_messages', 0)} parsed messages, "
            f"{manifest.get('case_count', 0)} derived cases, {manifest.get('attachments_referenced', 0)} referenced attachments"
        )
    if kind == "directory_snapshot":
        return (
            f"directory snapshot import, {manifest.get('files_indexed', 0)} indexed files, "
            f"{manifest.get('directory_case_count', 0)} derived directory cases"
        )
    if kind == "directory_text_batch":
        return f"directory text batch, {manifest.get('signals_written', 0)} text signals, {manifest.get('text_case_count', 0)} text cases"
    if kind == "directory_text_backlog_batch":
        return (
            f"directory text backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
            f"{manifest.get('text_backlog_case_count', 0)} backlog cases"
        )
    if kind == "directory_text_residual_batch":
        return (
            f"directory text residual batch, {manifest.get('signals_written', 0)} residual signals, "
            f"{manifest.get('text_residual_case_count', 0)} residual cases"
        )
    if kind == "directory_binary_textlike_batch":
        return (
            f"directory binary text-like batch, {manifest.get('signals_written', 0)} decoded-metadata signals, "
            f"{manifest.get('binary_textlike_case_count', 0)} binary text-like cases"
        )
    if kind == "directory_document_batch":
        return f"directory document batch, {manifest.get('signals_written', 0)} document signals, {manifest.get('document_case_count', 0)} document cases"
    if kind == "directory_document_backlog_batch":
        return (
            f"directory document backlog batch, {manifest.get('signals_written', 0)} document backlog signals, "
            f"{manifest.get('document_backlog_case_count', 0)} document backlog cases"
        )
    if kind == "directory_archive_batch":
        return (
            f"directory archive batch, {manifest.get('signals_written', 0)} archive signals, "
            f"{manifest.get('member_signals_written', 0)} anonymized member signals, "
            f"{manifest.get('archive_case_count', 0)} archive cases"
        )
    if kind == "directory_archive_backlog_batch":
        return (
            f"directory archive backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
            f"{manifest.get('member_signals_written', 0)} recursive member signals, "
            f"{manifest.get('archive_backlog_case_count', 0)} backlog cases"
        )
    if kind == "directory_archive_residual_batch":
        return (
            f"directory archive residual batch, {manifest.get('signals_written', 0)} residual signals, "
            f"{manifest.get('member_signals_written', 0)} repaired member signals, "
            f"{manifest.get('archive_residual_case_count', 0)} residual cases"
        )
    if kind == "directory_database_index_batch":
        return (
            f"directory database/index batch, {manifest.get('signals_written', 0)} metadata signals, "
            f"{manifest.get('database_index_case_count', 0)} database/index cases"
        )
    if kind == "directory_database_index_residual_batch":
        return (
            f"directory database/index residual batch, {manifest.get('signals_written', 0)} residual signals, "
            f"{manifest.get('control_requirement_count', 0)} control requirements, "
            f"{manifest.get('database_index_residual_case_count', 0)} residual cases"
        )
    if kind == "directory_credential_artifact_batch":
        return (
            f"directory credential artifact batch, {manifest.get('signals_written', 0)} marker-only signals, "
            f"{manifest.get('credential_artifact_case_count', 0)} credential cases"
        )
    if kind == "directory_credential_lifecycle_batch":
        return (
            f"directory credential lifecycle batch, {manifest.get('signals_written', 0)} lifecycle signals, "
            f"{manifest.get('control_requirement_count', 0)} control requirements, "
            f"{manifest.get('credential_lifecycle_case_count', 0)} lifecycle cases"
        )
    if kind == "directory_media_batch":
        return f"directory media batch, {manifest.get('signals_written', 0)} media/design signals, {manifest.get('media_case_count', 0)} media cases"
    if kind == "directory_media_backlog_batch":
        return (
            f"directory media backlog batch, {manifest.get('signals_written', 0)} backlog signals, "
            f"{manifest.get('media_backlog_case_count', 0)} media backlog cases"
        )
    if kind == "directory_binary_batch":
        return (
            f"directory binary batch, {manifest.get('signals_written', 0)} binary/database signals, "
            f"{manifest.get('binary_case_count', 0)} binary cases"
        )
    return f"{kind or run_id} import"


def refresh_readme(output_root: Path) -> None:
    runs: list[str] = []
    for manifest_path in sorted((output_root / "imports").glob("*/manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        run_id = manifest_path.parent.name
        runs.append(f"- `{run_id}`: {summarize_manifest(run_id, manifest)}.")
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
    (output_root / "README.md").write_text(body, encoding="utf-8")


def run(args: argparse.Namespace) -> Path:
    output_root = Path(args.output).resolve()
    source_path = output_root / "imports" / args.source_database_index_run / "database-index-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_signals(source_rows)
    signals.sort(key=lambda row: row["database_index_residual_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    controls = build_control_rows(signals)
    sensitive_count = sum(1 for row in signals if row["sensitive_route"])
    text_like_count = sum(1 for row in signals if row["byte_profile"] == "text_like_bytes")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_database_index_residual_batch",
        "source_database_index_run": args.source_database_index_run,
        "source_signal_count": len(source_rows),
        "source_generic_metadata_signal_count": sum(1 for row in source_rows if is_residual_target(row)),
        "signals_written": len(signals),
        "database_index_residual_case_count": len(cases),
        "control_requirement_count": len(controls),
        "sensitive_residual_signal_count": sensitive_count,
        "text_like_residual_signal_count": text_like_count,
        "sanitization": {
            "source_files_read": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_table_names_copied": False,
            "raw_column_names_copied": False,
            "raw_schema_text_copied": False,
            "raw_row_values_copied": False,
            "raw_payload_text_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
        },
    }

    common.write_jsonl(run_dir / "database-index-residual-signals.jsonl", signals)
    common.write_jsonl(run_dir / "database-index-residual-cases.jsonl", cases)
    common.write_jsonl(run_dir / "database-index-residual-controls.jsonl", controls)
    write_context(run_dir)

    issues = common.scan_forbidden(output_root)
    manifest["privacy_hit_count"] = len(issues)
    (run_dir / "privacy-scan.json").write_text(
        json.dumps({"hit_count": len(issues), "issues": issues}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_coverage(run_dir, manifest, signals)
    refresh_readme(output_root)
    return run_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="knowledge-context")
    parser.add_argument("--run-id", default="directory-database-index-residual-batch")
    parser.add_argument("--source-database-index-run", default="directory-database-index-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
