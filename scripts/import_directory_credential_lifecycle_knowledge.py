#!/usr/bin/env python3
"""Append derived secret-lifecycle requirements for credential artifacts.

This pass reads only the previous marker-only credential artifact run. It does
not read source files and does not copy key material, certificate subject or
issuer values, license text, paths, file names, payload text, domains, provider
names, people, brands, vendors, or secrets.
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
    "managed_secret_storage": "store sensitive artifacts in managed secret storage rather than general file stores",
    "rotation_workflow": "track rotation state and require auditable replacement workflow",
    "access_audit": "record least-privilege access, read events, and administrative handling",
    "training_exclusion": "exclude key, certificate, request, and entitlement payloads from training corpora",
    "ownership_registry": "bind the artifact to an accountable owner or service without copying identities",
    "renewal_monitoring": "monitor renewal and expiry lifecycle without storing subject or issuer values",
    "revocation_plan": "preserve revocation and emergency replacement playbooks",
    "deployment_binding": "track where the artifact is deployed using anonymized service/workload ids",
    "request_approval_flow": "treat certificate requests as issuance workflow evidence",
    "entitlement_review": "treat license-like artifacts as entitlement evidence without copying license text",
    "sensitive_path_quarantine": "route path-sensitive artifacts through quarantine and access review",
    "encrypted_key_handling": "separate encrypted private-key handling from plaintext private-key handling",
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


def material_classes(row: dict) -> list[str]:
    tags = set(row.get("credential_artifact_tags") or [])
    ext = str(row.get("extension") or "")
    classes: list[str] = []
    if "encrypted_key_marker_present" in tags:
        classes.append("encrypted_private_key")
    elif "private_key_marker_present" in tags:
        classes.append("private_key")
    if "certificate_request_marker_present" in tags:
        classes.append("certificate_request")
    if "certificate_marker_present" in tags:
        classes.append("certificate")
    if "license_or_entitlement_marker" in tags or ext == "lic":
        classes.append("license_or_entitlement")
    if not classes and ext in {"cer", "crt", "csr", "pem"}:
        classes.append("certificate_or_request_marker")
    if not classes:
        classes.append("credential_marker")
    return list(dict.fromkeys(classes))


def lifecycle_controls(row: dict, classes: list[str]) -> list[str]:
    tags = set(row.get("credential_artifact_tags") or [])
    flags = set(row.get("sensitive_flags") or [])
    controls = {"training_exclusion", "ownership_registry", "access_audit"}
    if any(cls in classes for cls in ["private_key", "encrypted_private_key", "credential_marker"]):
        controls.update({"managed_secret_storage", "rotation_workflow", "revocation_plan", "deployment_binding"})
    if "encrypted_private_key" in classes:
        controls.add("encrypted_key_handling")
    if any(cls in classes for cls in ["certificate", "certificate_or_request_marker"]):
        controls.update({"renewal_monitoring", "revocation_plan", "deployment_binding"})
    if "certificate_request" in classes:
        controls.update({"request_approval_flow", "ownership_registry"})
    if "license_or_entitlement" in classes:
        controls.update({"entitlement_review", "ownership_registry", "access_audit"})
    if "path_sensitive_signal" in flags or "path_sensitive_marker" in tags:
        controls.add("sensitive_path_quarantine")
    return sorted(controls)


def risk_bucket(row: dict, classes: list[str], controls: list[str]) -> str:
    tags = set(row.get("credential_artifact_tags") or [])
    if "private_key" in classes or "encrypted_private_key" in classes:
        return "high_secret_lifecycle_risk"
    if "certificate_request" in classes:
        return "issuance_lifecycle_risk"
    if "certificate" in classes or "certificate_or_request_marker" in classes:
        return "renewal_deployment_lifecycle_risk"
    if "license_or_entitlement" in classes:
        return "entitlement_compliance_lifecycle_risk"
    if "content_sensitive_marker" in tags or len(controls) >= 5:
        return "sensitive_artifact_lifecycle_risk"
    return "controlled_artifact_lifecycle_risk"


def lifecycle_status(classes: list[str], risk: str) -> str:
    if "private_key" in classes or "encrypted_private_key" in classes:
        return "private_key_lifecycle_requirements_modeled"
    if "certificate_request" in classes:
        return "certificate_request_lifecycle_requirements_modeled"
    if "certificate" in classes or "certificate_or_request_marker" in classes:
        return "certificate_lifecycle_requirements_modeled"
    if "license_or_entitlement" in classes:
        return "entitlement_lifecycle_requirements_modeled"
    return risk.replace("_risk", "_requirements_modeled")


def lifecycle_tags(row: dict, classes: list[str], controls: list[str], status: str, risk: str) -> list[str]:
    tags = [
        "credential_lifecycle_reviewed",
        "derived_from_marker_only_signal",
        "not_training_payload",
        f"lifecycle_status_{status}",
        f"risk_{risk}",
    ]
    tags.extend(f"material_{cls}" for cls in classes)
    tags.extend(f"control_{control}" for control in controls)
    for tag in row.get("credential_artifact_tags") or []:
        if tag in {
            "private_key_marker_present",
            "encrypted_key_marker_present",
            "certificate_marker_present",
            "certificate_request_marker_present",
            "license_or_entitlement_marker",
            "path_sensitive_marker",
            "content_sensitive_marker",
        }:
            tags.append(f"source_{tag}")
    return sorted(set(tags))


def build_lifecycle_signals(source_rows: list[dict]) -> list[dict]:
    signals: list[dict] = []
    for row in source_rows:
        classes = material_classes(row)
        controls = lifecycle_controls(row, classes)
        risk = risk_bucket(row, classes, controls)
        status = lifecycle_status(classes, risk)
        signal = {
            "credential_lifecycle_signal_id": "credentiallife-" + common.stable_hash(row["credential_artifact_signal_id"]),
            "case_id": "",
            "source_credential_artifact_signal_id": row["credential_artifact_signal_id"],
            "source_binary_signal_id": row.get("source_binary_signal_id", ""),
            "path_hash": row.get("path_hash", ""),
            "top_group_hash": row.get("top_group_hash", ""),
            "period": row.get("period", "unknown"),
            "extension": row.get("extension", "unknown"),
            "size_bucket": row.get("size_bucket", "unknown"),
            "byte_profile": row.get("byte_profile", "unknown"),
            "marker_status": row.get("marker_status", "unknown"),
            "marker_count_buckets": row.get("marker_count_buckets", {}),
            "material_classes": classes,
            "lifecycle_status": status,
            "risk_bucket": risk,
            "required_controls": controls,
            "domain_tags": row.get("domain_tags", []),
            "problem_tags": row.get("problem_tags", []),
            "credential_lifecycle_tags": lifecycle_tags(row, classes, controls, status, risk),
            "sensitive_flags": sorted(
                set(list(row.get("sensitive_flags") or []) + ["lifecycle_sensitive_artifact"])
            ),
            "source_integrity": row.get("source_integrity", {}),
        }
        signals.append(signal)
    return signals


def build_cases(signals: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        group_key = f"{signal.get('top_group_hash') or 'group-unknown'}:{signal['risk_bucket']}"
        by_group[group_key].append(signal)

    cases: list[dict] = []
    for group_key, rows in sorted(by_group.items()):
        group_hash = group_key.split(":", 1)[0]
        status_counter = collections.Counter(row["lifecycle_status"] for row in rows)
        class_counter = collections.Counter(cls for row in rows for cls in row["material_classes"])
        control_counter = collections.Counter(control for row in rows for control in row["required_controls"])
        domain_counter = collections.Counter(tag for row in rows for tag in row["domain_tags"])
        problem_counter = collections.Counter(tag for row in rows for tag in row["problem_tags"])
        tag_counter = collections.Counter(tag for row in rows for tag in row["credential_lifecycle_tags"])
        primary_status = status_counter.most_common(1)[0][0] if status_counter else "credential_lifecycle_requirements_modeled"
        primary_class = class_counter.most_common(1)[0][0] if class_counter else "credential_marker"
        implications = [
            "Model credential-like artifacts as lifecycle requirements rather than content payload.",
            "Keep evidence traceable through stable ids while excluding raw material from agent prompts and training corpora.",
        ]
        if control_counter.get("rotation_workflow", 0):
            implications.append("Cloud platforms need auditable rotation and replacement workflows for private-key evidence.")
        if control_counter.get("renewal_monitoring", 0):
            implications.append("Certificate-like evidence should drive renewal, deployment, and revocation product requirements.")
        if control_counter.get("entitlement_review", 0):
            implications.append("Entitlement-like evidence should drive compliance review without copying license text.")
        if control_counter.get("sensitive_path_quarantine", 0):
            implications.append("Path-sensitive credential evidence should enter quarantine and least-privilege review flows.")
        case = {
            "case_id": "credentiallifecase-" + common.stable_hash(group_key),
            "case_type": "credential_secret_lifecycle_requirements_case",
            "top_group_hash": group_hash,
            "signal_count": len(rows),
            "material_class_counts": dict(class_counter.most_common()),
            "lifecycle_status_counts": dict(status_counter.most_common()),
            "required_control_counts": dict(control_counter.most_common()),
            "domain_tags": [tag for tag, _ in domain_counter.most_common(8)] or ["general_business_context"],
            "problem_tags": [tag for tag, _ in problem_counter.most_common(8)] or ["context_signal"],
            "credential_lifecycle_tags": [tag for tag, _ in tag_counter.most_common()],
            "evidence_credential_lifecycle_signal_ids": [row["credential_lifecycle_signal_id"] for row in rows[:50]],
            "evidence_credential_lifecycle_signal_id_count": len(rows),
            "summary": (
                f"A credential lifecycle cluster modeled {primary_class.replace('_', ' ')} evidence; "
                f"the dominant requirement state is {primary_status.replace('_', ' ')} across "
                f"{len(rows)} marker-only artifacts."
            ),
            "platform_implications": implications,
            "agent_use": (
                "Use this case to design secret storage, rotation, renewal, revocation, access audit, "
                "and entitlement review behavior without copying secret or license payloads."
            ),
        }
        cases.append(case)
        for row in rows:
            row["case_id"] = case["case_id"]
    return cases


def build_control_rows(signals: list[dict]) -> list[dict]:
    control_to_signals: dict[str, list[dict]] = collections.defaultdict(list)
    for signal in signals:
        for control in signal["required_controls"]:
            control_to_signals[control].append(signal)
    rows: list[dict] = []
    for control, control_signals in sorted(control_to_signals.items()):
        class_counter = collections.Counter(cls for signal in control_signals for cls in signal["material_classes"])
        risk_counter = collections.Counter(signal["risk_bucket"] for signal in control_signals)
        rows.append(
            {
                "credential_lifecycle_control_id": "credentialcontrol-" + common.stable_hash(control),
                "control": control,
                "requirement": CONTROL_REQUIREMENTS[control],
                "signal_count": len(control_signals),
                "material_class_counts": dict(class_counter.most_common()),
                "risk_bucket_counts": dict(risk_counter.most_common()),
                "evidence_credential_lifecycle_signal_ids": [
                    signal["credential_lifecycle_signal_id"] for signal in control_signals[:50]
                ],
                "agent_use": "Use as a product requirement checkpoint, not as credential payload evidence.",
            }
        )
    return rows


def markdown_counter(counter: collections.Counter[str], label: str) -> str:
    if not counter:
        return "_No rows._"
    lines = [f"| {label} | count |", "| --- | ---: |"]
    for key, count in counter.most_common():
        lines.append(f"| `{key}` | {count} |")
    return "\n".join(lines)


def write_coverage(run_dir: Path, manifest: dict, signals: list[dict]) -> None:
    status_counts = counter_from_rows(signals, "lifecycle_status")
    class_counts = counter_from_rows(signals, "material_classes")
    control_counts = counter_from_rows(signals, "required_controls")
    body = f"""# Credential Lifecycle Coverage

- Source kind: directory credential lifecycle batch
- Source credential artifact run: `{manifest["source_credential_artifact_run"]}`
- Source marker-only signals: {manifest["source_target_signal_count"]}
- Lifecycle signals written: {manifest["signals_written"]}
- Lifecycle cases: {manifest["credential_lifecycle_case_count"]}
- Control requirements written: {manifest["control_requirement_count"]}
- Private-key lifecycle signals: {manifest["private_key_lifecycle_signal_count"]}
- Certificate/request lifecycle signals: {manifest["certificate_or_request_lifecycle_signal_count"]}
- Entitlement lifecycle signals: {manifest["entitlement_lifecycle_signal_count"]}
- Privacy/vendor scan hits: {manifest["privacy_hit_count"]}

## Lifecycle Status Counts

{markdown_counter(status_counts, "lifecycle_status")}

## Material Class Counts

{markdown_counter(class_counts, "material_class")}

## Required Control Counts

{markdown_counter(control_counts, "control")}

## Safety Notes

- This is a derived-only run over marker-only credential artifact signals.
- It does not read source files and does not copy key material, subject/issuer
  values, license text, payload text, source paths, names, domains, providers,
  people, brands, vendors, or secrets.
- Use these records for cloud product requirements around secret lifecycle,
  not as training payload.
"""
    (run_dir / "coverage.md").write_text(body, encoding="utf-8")


def write_context(run_dir: Path) -> None:
    (run_dir / "credential-lifecycle-context.md").write_text(
        "# Credential Lifecycle Context\n\n"
        "This run derives secret-lifecycle requirements from marker-only credential artifact records. "
        "It preserves the operational lesson that cloud platforms need first-class handling for "
        "private keys, encrypted keys, certificates, certificate requests, and entitlement-like "
        "artifacts, while excluding all payload material and identity-bearing values.\n\n"
        "Agent usage:\n\n"
        "- Use `credential-lifecycle-cases.jsonl` for secret lifecycle product situations.\n"
        "- Use `credential-lifecycle-signals.jsonl` for stable ids, material classes, risk buckets, and required controls.\n"
        "- Use `credential-lifecycle-controls.jsonl` as a product requirement checklist.\n"
        "- Never use this layer as proof of a key value, certificate subject, issuer, domain, account, or license text.\n",
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
    if kind == "directory_database_index_batch":
        return (
            f"directory database/index batch, {manifest.get('signals_written', 0)} metadata signals, "
            f"{manifest.get('database_index_case_count', 0)} database/index cases"
        )
    if kind == "directory_credential_artifact_batch":
        return (
            f"directory credential artifact batch, {manifest.get('signals_written', 0)} marker-only signals, "
            f"{manifest.get('credential_artifact_case_count', 0)} credential cases"
        )
    if kind == "directory_binary_batch":
        return (
            f"directory binary batch, {manifest.get('signals_written', 0)} binary/database signals, "
            f"{manifest.get('binary_case_count', 0)} binary cases"
        )
    return f"{kind or run_id} import"


def refresh_readme(output_root: Path) -> None:
    runs: list[str] = []
    imports_root = output_root / "imports"
    for manifest_path in sorted(imports_root.glob("*/manifest.json")):
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
    source_path = output_root / "imports" / args.source_credential_artifact_run / "credential-artifact-signals.jsonl"
    source_rows = read_jsonl(source_path)
    run_dir = output_root / "imports" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    signals = build_lifecycle_signals(source_rows)
    signals.sort(key=lambda row: row["credential_lifecycle_signal_id"])
    cases = build_cases(signals)
    cases.sort(key=lambda row: row["case_id"])
    control_rows = build_control_rows(signals)

    class_counts = counter_from_rows(signals, "material_classes")
    manifest = {
        "append_only_run_id": args.run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "directory_credential_lifecycle_batch",
        "source_credential_artifact_run": args.source_credential_artifact_run,
        "source_target_signal_count": len(source_rows),
        "signals_written": len(signals),
        "credential_lifecycle_case_count": len(cases),
        "control_requirement_count": len(control_rows),
        "private_key_lifecycle_signal_count": class_counts.get("private_key", 0) + class_counts.get("encrypted_private_key", 0),
        "certificate_or_request_lifecycle_signal_count": (
            class_counts.get("certificate", 0)
            + class_counts.get("certificate_request", 0)
            + class_counts.get("certificate_or_request_marker", 0)
        ),
        "entitlement_lifecycle_signal_count": class_counts.get("license_or_entitlement", 0),
        "sanitization": {
            "source_files_read": False,
            "raw_source_paths_copied": False,
            "raw_file_names_copied": False,
            "raw_key_material_copied": False,
            "raw_certificate_subject_or_issuer_copied": False,
            "raw_license_text_copied": False,
            "raw_payload_text_copied": False,
            "addresses_domains_people_masked": True,
            "brand_or_vendor_names_masked": True,
            "secrets_copied": False,
        },
    }

    common.write_jsonl(run_dir / "credential-lifecycle-signals.jsonl", signals)
    common.write_jsonl(run_dir / "credential-lifecycle-cases.jsonl", cases)
    common.write_jsonl(run_dir / "credential-lifecycle-controls.jsonl", control_rows)
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
    parser.add_argument("--run-id", default="directory-credential-lifecycle-batch")
    parser.add_argument("--source-credential-artifact-run", default="directory-credential-artifact-batch-20260622")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    run_dir = run(parse_args(argv))
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
