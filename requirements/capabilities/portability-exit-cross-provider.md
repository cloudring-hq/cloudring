# Capability Contract - Portability Exit And Cross-Provider Operations

## Назначение

Portability Exit And Cross-Provider Operations превращает anti-lock-in из
обещания в проверяемую продуктовую capability. Пользователь должен понимать,
что можно export/import/restore/migrate/replicate/failover, какие есть limits,
какие data/metadata/state/secrets затронуты, какие providers/jurisdictions
участвуют, как проверить success и как уйти без потери контроля.

Contract описывает product contract and evidence. Он не обещает universal
portability и не выбирает конкретный migration tool, backup system or replication
protocol.

## Продуктовая Граница

- Portability profile describes exportable data, metadata, runtime/service state,
  secret boundary, compatible targets, limitations and verified import/restore.
- Exit covers customer exit, provider exit, jurisdiction exit, technology exit
  and service deprecation/migration.
- Cross-provider operation covers backup, restore, replication, migration, DR,
  burst capacity, support handoff and validation drills between independent
  presence.
- Non-portable and manual-migration outcomes are valid if visible before order
  and backed by honest evidence.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-PORTX-001 | Every supported service class must declare portability profile before production/private use. | Exit cannot be retrofitted after lock-in. | Profile lists exportable data, metadata, state, secret boundary, compatible targets, limits and evidence. |
| CR-PORTX-002 | Marketplace/service card must show portability class before order/install. | Buyer must see lock-in risk before commitment. | Service card marks portable, partially portable, export-only, manual-migration, non-portable or unknown with reason. |
| CR-PORTX-003 | Export must include data and required metadata where allowed. | Data without context may be unusable. | Export plan shows included data, metadata, excluded items, format promise, owner and verification method. |
| CR-PORTX-004 | Secret values must not be exported as ordinary service data. | Secrets belong to trust boundary and require separate handling. | Export uses secret references/rotation/rebinding flow or explicit owner-approved secret transfer. |
| CR-PORTX-005 | Import/restore verification is required for portability evidence. | Export without restore is not proof of exit. | Profile includes latest import/restore test or explicit unverified warning. |
| CR-PORTX-006 | Backup/restore, migration and DR must share lifecycle semantics. | Separate tools with separate truths create failures. | Operation plan links backup/export/import/restore/failover to service instance lifecycle and audit events. |
| CR-PORTX-007 | Cross-provider operation must declare source, target and participants. | Federation operations cross ownership and support boundaries. | Plan lists source presence, target presence, providers/participants, tenant, owner and support responsibility. |
| CR-PORTX-008 | Cross-provider operation must declare data/metadata/state scope. | Users need to know what moves and what stays. | Plan shows affected data classes, metadata, state, logs, backups, secrets boundary and unsupported items. |
| CR-PORTX-009 | Policy must approve jurisdiction/data residency/provider-chain before operation. | Moving data to the wrong place can be irreversible. | Operation cannot start without policy decision covering jurisdiction, data residency, provider class, encryption and budget. |
| CR-PORTX-010 | Compatibility must be checked before migration/replication/failover. | Not every target can safely run every service. | Plan shows compatible, degraded, blocked or manual target state with reason. |
| CR-PORTX-011 | User must see impact before approval. | Migration/DR can affect downtime, consistency, cost and SLA. | Plan shows downtime, consistency, data loss risk, performance impact, cost, support/SLA and rollback/compensation. |
| CR-PORTX-012 | Risk class and approval must be explicit. | Cross-provider operations are high-impact by default. | Plan includes risk class, required approvals and allowed agent actions. |
| CR-PORTX-013 | Operation must have validation and known final state. | Failed migration should not leave unknown reality. | Completion evidence shows source/target state, validation result, rollback/compensation or manual remediation. |
| CR-PORTX-014 | DR and failover must support rehearsal/drill. | Disaster recovery that was never rehearsed is a hope. | DR profile includes latest drill, RTO/RPO expectation, gaps and next action. |
| CR-PORTX-015 | Replication must expose consistency and lag. | Users must understand freshness of protected data. | Replication view shows lag, consistency model, last successful sync and blocked/degraded state. |
| CR-PORTX-016 | Provider exit must preserve export, billing closure and support evidence. | Leaving provider should not destroy proof or invoices. | Exit bundle includes service data/export, usage/invoices, entitlements, support history, incidents, credits/disputes and closure status. |
| CR-PORTX-017 | Jurisdiction exit must be supported as first-class scenario. | Legal/policy changes can require moving data or workload. | Plan shows source/target jurisdictions, data classes, policy decision, deadlines, residual data and verification. |
| CR-PORTX-018 | Technology exit must be supported through replaceable contracts. | Runtime/database/provider technology can become obsolete. | Profile states which parts are contract-based, which are backend-specific and how migration/deprecation is handled. |
| CR-PORTX-019 | Deprecation must include migration or honest end-of-life path. | Marketplace must not abandon users on old versions. | Deprecated service/version shows timeline, alternatives, export/migration path, support terms and risk. |
| CR-PORTX-020 | Cross-provider support handoff must preserve evidence and SLA state. | Support can be lost between participants. | Handoff shows owner transfer, SLA clock, evidence shared, data scope, customer-visible status and dispute path. |
| CR-PORTX-021 | Billing/settlement impact must be tied to operation. | Migration/DR/burst can change costs and participant shares. | Operation plan shows cost estimate, billing start/stop, credits risk and settlement impact where applicable. |
| CR-PORTX-022 | User must retain access to exit evidence after suspension/dispute where policy permits. | Commercial conflict must not trap data. | Suspension/dispute state shows allowed export, invoices, evidence access, appeal and limitations. |
| CR-PORTX-023 | Cross-provider operation evidence must be dispute-ready. | Independent participants may disagree. | Evidence bundle links policy, usage, support, audit, validation, billing and participant signatures/attestations where relevant. |
| CR-PORTX-024 | Agent must be able to plan but not silently execute high-impact exit/migration. | Autonomy needs human-visible control. | Agent can compare targets and draft plan; execution requires approval for data movement, destructive, financial or SLA-impacting steps. |
| CR-PORTX-025 | Partial portability must be visible and useful. | Honest limits are better than false universal portability. | Profile explains what can move, what cannot, what loses fidelity and what manual steps remain. |
| CR-PORTX-026 | Exit must not require global portal ownership. | Global layer must not become new lock-in. | Local/private/provider presence can export required evidence and data according to policy without central owner takeover. |
| CR-PORTX-027 | Cross-provider operation catalog must not imply universal compatibility. | Choice requires truthful options. | UI/API separates compatible, degraded, manual, blocked, unsupported and unknown paths. |
| CR-PORTX-028 | Portability capability must evolve from incidents and failed migrations. | Migration lessons are product memory. | Failed/limited operation creates requirement, ADR, runbook update or no-change rationale. |
| CR-PORTX-029 | Migration, restore, DR and cross-provider operations must have dry-run/preflight before data movement where possible. | High-impact moves need consequence preview. | Preflight report shows target diff, policy, cost, downtime, risks, validation plan and confirms zero mutation. |
| CR-PORTX-030 | Exit must include residual data, retention, erase and closure plan. | Exit without cleanup/retention truth is hidden lock-in. | Plan states retained data, deletion/retention windows, legal holds, backups, verification and closure certificate or retained-data statement. |
| CR-PORTX-031 | Provider/participant offboarding must be self-service-capable and evidence-preserving. | Network participants will leave; exit should not become manual chaos. | Offboarding flow shows affected offers, users, data, settlement, support ownership, trust status, timeline, alternatives and evidence retention. |
| CR-PORTX-032 | Exit/offboarding evidence must remain accessible by policy after service/provider closure. | Disputes and audits often happen after exit. | Evidence retention shows invoices, usage, support, incidents, policy decisions, export/closure records, access scope and retention window. |
| CR-PORTX-033 | Risky portability operations must prove rollback/compensation where feasible. | A written rollback idea is not enough for high-impact migration. | Plan links rehearsal, tested rollback, compensation path or explicit irreversible warning with approval. |

## Evidence

- Service portability profile.
- Marketplace portability class snapshot.
- Export/import/restore validation record.
- Cross-provider operation plan.
- Dry-run/preflight report.
- Policy decision for jurisdiction/data/provider-chain.
- DR drill result and RTO/RPO evidence.
- Migration/replication/failover final-state validation.
- Provider/jurisdiction/technology exit bundle.
- Residual data/retention/closure record.
- Provider/participant offboarding record.
- Support handoff and SLA evidence.
- Evidence retention after exit/offboarding.
- Rollback/compensation rehearsal where applicable.
- Failed operation learning record.

## Stage Guardrails

- Stage 1 requires at least honest export story for generated services.
- Stage 2 requires private backup/restore and local exit evidence.
- Stage 3 exposes portability in private store and lifecycle actions.
- Stage 4 adds provider exit, billing closure and support evidence.
- Stage 5 introduces cross-provider operation contracts.
- Stage 6 requires global discovery to compare portability and exit risk across
  participants and jurisdictions.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/ADR, если:

- portability profile is missing for production/private service;
- data movement would start without policy decision;
- data movement would start without green preflight where preflight is
  applicable;
- target compatibility is unknown or degraded without user-visible warning;
- export has no import/restore validation but is presented as proven;
- operation affects billing, SLA, support ownership or data residency without
  approval;
- secret transfer would expose secret value outside approved trust boundary;
- source/backup residual data state is unknown during exit;
- provider/participant offboarding would lose support, billing, trust or dispute
  evidence;
- failed operation leaves unknown source/target state;
- global portal becomes required owner for customer exit.

## Non-Goals

- Не обещать universal, instant or bit-for-bit portability.
- Не выбирать конкретный backup/migration/replication tool.
- Не скрывать non-portable dependencies.
- Не использовать commercial dispute as exit blocker.
- Не выполнять cross-provider migration/DR как hidden automation без user-visible
  plan, evidence and approval.
