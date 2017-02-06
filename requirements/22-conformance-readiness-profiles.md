# Conformance Readiness Profiles

Этот документ задает общий стандарт readiness/conformance profiles для
CloudRING. Stage-файлы описывают, каким должен быть продуктовый инкремент.
Conformance profiles описывают, какие доказательства нужны, чтобы считать этот
инкремент готовым, какие блокеры нельзя игнорировать и какой отчет должен
понимать человек и AI-агент.

Conformance здесь не является технической инструкцией реализации. Это
продуктовый контракт проверки: что должно быть доказано, зачем это важно, какие
исключения допустимы и какие решения требуют owner approval or ADR.

## Profile Index

- [conformance/stage0-requirements-memory-ready.md](conformance/stage0-requirements-memory-ready.md)
- [conformance/stage1-service-ready.md](conformance/stage1-service-ready.md)
- [conformance/stage2-private-presence-ready.md](conformance/stage2-private-presence-ready.md)
- [conformance/stage3-private-store-ready.md](conformance/stage3-private-store-ready.md)
- [conformance/stage4-public-provider-ready.md](conformance/stage4-public-provider-ready.md)
- [conformance/stage5-federation-ready.md](conformance/stage5-federation-ready.md)
- [conformance/stage6-global-ready.md](conformance/stage6-global-ready.md)
- [conformance/stage7-self-evolving-ready.md](conformance/stage7-self-evolving-ready.md)

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-CONF-001 | Каждый stage должен иметь named readiness profile. | Stage должен быть законченным продуктом, а не набором намерений. | Profile name, scope, required evidence and blockers are documented. |
| CR-CONF-002 | Conformance report должен быть human-readable and agent-readable. | Человек и агент должны видеть одну реальность готовности. | Report has summary, check results, evidence references, blockers, exceptions and next actions. |
| CR-CONF-003 | Check result must use standard statuses and distinguish check status from profile summary. | Разные статусы готовности нельзя трактовать произвольно. | Check status uses the full standard list: passed, failed, blocked, warning, skipped, waived, stale, not-applicable, degraded, manual_review_required or unknown; profile summary may aggregate these into ready/limited/not-ready decision. |
| CR-CONF-004 | Critical blocker cannot be waived by the same actor that failed the check. | Иначе conformance теряет смысл. | Waiver requires owner, reason, expiry/review and impact statement. |
| CR-CONF-005 | Waiver/exception must be scoped and temporary unless ADR accepts it. | Исключения не должны становиться скрытым стандартом. | Exception shows scope, expiry/review trigger, affected users and linked requirement/ADR. |
| CR-CONF-006 | Evidence must be referenced, not pasted as sensitive raw data. | Отчет не должен переносить секреты, tenant data or private source content. | Evidence reference is redacted/scoped and safe for agent context. |
| CR-CONF-007 | Readiness profile must distinguish hard gates, warnings and next-stage gaps. | Не все пробелы одинаковы: одни блокируют текущий stage, другие готовят будущий. | Report separates blockers, warnings, limitations and future-stage gaps. |
| CR-CONF-008 | Profile version must be explicit. | Conformance evolves with requirements and cannot change silently. | Report shows profile version, date/freshness and changed checks. |
| CR-CONF-009 | Profile changes must follow `ADR-0016`. | Conformance должен эволюционировать безопасно. | New/changed check has reason, affected profiles, compatibility impact and rollout/migration note. |
| CR-CONF-010 | Readiness must include product experience checks. | Рабочая реализация без понятного self-service не готова. | Key flows are checked against `ADR-0012` and relevant `CR-UX-*`. |
| CR-CONF-011 | Readiness must include agent-operability checks. | CloudRING должен обслуживаться человеком с AI-агентами. | Agent tasks have scope, risk, evidence, validation and approval boundaries. |
| CR-CONF-012 | Security and secret handling must be checked at every stage. | Ошибки доверия масштабируются вместе с platform maturity. | Profile verifies secret-safe evidence, audit and trust boundaries relevant to the stage. |
| CR-CONF-013 | Portability/exit evidence must be checked whenever a service or customer state is created. | Anti-lock-in должен быть доказан в готовности, а не только в принципах. | Report shows export/migration/exit story or explicit limitations. |
| CR-CONF-014 | Billing/settlement readiness must be checked when money or entitlements are involved. | Экономика marketplace требует доказуемой прозрачности. | Report links order, usage, entitlement, invoice/credit/settlement and dispute evidence as applicable. |
| CR-CONF-015 | Operational readiness must include health, observability, incident and recovery evidence. | Готовность без эксплуатации не является cloud readiness. | Report shows health, telemetry, support/runbook and recovery evidence for stage scope. |
| CR-CONF-016 | Local autonomy and degradation must be checked where relevant. | CloudRING не должен становиться single point of lock-in. | Profile verifies disconnected/degraded mode and local ownership boundaries. |
| CR-CONF-017 | Source-derived conformance updates must remain anonymized and copyright-safe. | Проверки не должны переносить внутренний контекст источников. | Update passes forbidden-name/secret/source-copy scan or is rejected for repair. |
| CR-CONF-018 | Failed readiness must produce actionable next steps. | Conformance должен помогать строить продукт, а не просто запрещать. | Failed report includes reason, impact, owner, suggested artifact and next review. |
| CR-CONF-019 | Stage profile must explicitly state non-goals. | Иначе профиль начнет требовать будущие stages. | Report can mark future-stage gaps without blocking current stage. |
| CR-CONF-020 | Readiness claim must be reproducible from evidence. | "Готово" должно выдерживать аудит. | Another agent can review report and evidence references without relying on memory. |
| CR-CONF-021 | Profile must name owners for profile, requirement, evidence, exception and approval. | Готовность без ответственности превращается в анонимный отчет. | Report identifies profile owner, evidence owner, exception owner and approver for high-impact decisions. |
| CR-CONF-022 | Unknown evidence state must not be treated as passed. | Отсутствие данных не является доказательством готовности. | Unknown state becomes warning or blocker according to check criticality. |
| CR-CONF-023 | Waiver schema must be standard. | Исключения должны быть сравнимы между stages and participants. | Waiver includes id, profile, check, owner, approver, reason, scope, risk, compensation, review trigger, expiry and links. |
| CR-CONF-024 | Report must include next-stage readiness and non-blocking gaps. | Stage должен быть законченным сейчас и понятным для развития дальше. | Report separates current blockers from future-stage readiness gaps. |
| CR-CONF-025 | Agent handoff must state allowed and forbidden actions. | Conformance report должен безопасно запускать следующую агентскую работу. | Report lists allowed_actions, forbidden_actions, required_approvals and validation_needed. |
| CR-CONF-026 | Evidence freshness must be visible. | Устаревшее доказательство создает ложную уверенность. | Each critical evidence item has freshness, stale state or review trigger. |
| CR-CONF-027 | Blocking classes must be explicit and mission-aligned. | Blocker means broken product promise, not arbitrary failed check. | Framework lists blocker classes for ownership, secrets, policy, portability, agent approval, billing/support, trust and lock-in. |
| CR-CONF-028 | Readiness must include role scenario coverage matrix. | Capability gates can pass while real users, providers, support owners or agents still cannot complete the product journey. | Profile report links scenario fixtures or marks not-applicable for user, admin, developer/ISV, provider, support, governance and AI-agent roles in the stage scope. |
| CR-CONF-029 | Scenario fixtures must include negative stop-condition cases. | Product readiness must prove safe refusal, not only happy paths. | Scenario evidence covers policy denied, missing owner/support, stale trust/evidence, unapproved agent action, unsupported portability, duplicate billing or unsafe evidence where relevant. |
| CR-CONF-030 | Readiness must include product design quality review for user-impacting flows. | A stage can pass technical checks while hiding cost, jurisdiction, provider chain, support owner or unsafe defaults. | Report links product design quality review, scenario refs, consequence-before-action coverage, alternative analysis and unresolved design gaps. |
| CR-CONF-031 | Readiness must include OCS information model evidence when OCS compatibility is claimed. | OCS-compatible without model/version/field evidence is not reproducible. | Report links OCS model version, field registry, validation catalog, conformance suite, compatibility review and source-safety result. |
| CR-CONF-032 | Readiness must include lifecycle command surface evidence when a stage exposes commands, API actions or agent actions. | Runnable self-service without command evidence can hide unsafe automation. | Report links command catalog, preflight, risk, approval, result shape, cleanup, task/plugin boundaries, generated artifacts and support evidence. |
| CR-CONF-033 | Readiness must include billing runtime evidence when billable usage, invoices, credits, disputes or settlement are claimed. | Money flow readiness cannot be inferred from intake success or release tags. | Report links usage contract, receipt/status model, idempotency, backpressure, replay/quarantine, access freshness, release/history evidence, generated docs/config safety and settlement freeze evidence. |
| CR-CONF-034 | Readiness must include stateful recovery evidence when backup, restore, PITR, failover, HA or stateful provider operation is claimed. | Recoverability cannot be inferred from backup config, HA inventory or operational logs alone. | Report links topology, backup/archive, restore/PITR, failover, endpoint ownership, audit findings, role matrix, source/history coverage, source-safety and recovery non-claims. |
| CR-CONF-035 | Readiness must include documentation decision-memory evidence when docs, ADR, feedback, source-pass learning or developer guidance are used as proof. | A documented flow is not reproducible product memory unless the requirement, decision rationale, scenario, evidence, owner, freshness and non-claim chain is visible. | Report links docs package, ADR/no-ADR rationale, template, synthetic example, scenario, source pass, owner, freshness, source-safety and explicit non-claims. |
| CR-CONF-036 | Readiness must include secret runtime evidence when encrypted secrets, credential references, key custody, rotation or secret-managed runtime access are claimed. | A secret-safe boundary is not the same as runtime credential readiness. | Report links scope binding, key custody, public certificate freshness, generation/status, install/delete behavior, RBAC, health/metrics, rotation/degraded mode, source-safety and explicit non-claims. |
| CR-CONF-037 | Readiness must include service dependency/deployment evidence when dependencies, generated runtime artifacts, profile resolution or env handoff are claimed. | A manifest or successful local start does not prove portable dependency readiness. | Report links effective service model, dependency graph, generated artifact inventory, env classification, conflict preflight, portability, source-safety and explicit non-claims. |
| CR-CONF-038 | Readiness must include base OS image factory evidence when reusable VM images, golden images, templates or provider image catalogs are claimed. | Build success does not prove first-boot, cleanup, provenance, portability, supportability or source safety. | Report links image identity, build input classification, unattended install summary, provisioning role inventory, guest readiness, cleanup/sealing, immutable artifact identity, first-boot smoke, promotion state, source-safety and explicit non-claims. |
| CR-CONF-039 | Readiness must include UI extension runtime certification evidence when embedded UI, validation runtime, private-store UI publication or provider UI publication is claimed. | Build/local preview success does not prove host authority, validation parity, browser behavior, accessibility, localization, lifecycle cleanup or publication trust. | Report links typed embed descriptor, scoped context, runtime lifecycle, validation phases, stable error identity, parity matrix, browser/runtime evidence, accessibility/localization, artifact identity, support owner, source-safety and explicit non-claims. |
| CR-CONF-040 | Readiness must include settlement closure evidence when provider-local closeout, cross-participant settlement, dispute hold/release, credit/refund or participant share is claimed. | Money cannot be called settled from usage intake, invoice draft or release tag alone. | Report links closure run, input manifest, reconciliation, freeze gate, invoice/credit/refund trace, participant shares, dispute evidence, closeout export, approvals, release/history evidence, source-safety and explicit non-claims. |
| CR-CONF-041 | Readiness must include presence bootstrap activation evidence when local runtime bootstrap, private presence install, trusted bootstrap config/assets or activation automation are claimed. | A binary, config download or local runtime start does not prove an activated CloudRING presence. | Report links activation workflow, artifact identity/provenance, distribution mode, config schema/profile, preflight, runtime provider matrix, diagnostics, rollback/cleanup, infrastructure profile update, agent approval, source-safety and explicit non-claims. |
| CR-CONF-042 | Readiness must include controlled extension/task automation evidence when tasks, plugins, dependency/library mutations, boilerplate generation or task/plugin managed execution are claimed. | Local executable automation can hide arbitrary code, full env exposure, unsafe artifacts, mutation side effects and false production readiness. | Report links automation kind, owner, selection rationale, artifact provenance/integrity, version policy, scope, env/secret boundary, argument schema, runtime budget, rollback/compensation, structured result, agent approval, source-safety and explicit non-claims. |
| CR-CONF-043 | Readiness must include service registry/catalog publication evidence when service registry records, catalog cards, publication lifecycle, private store visibility or registry sync/cache are claimed. | Static files, seed rows, local manifests and debug/build success do not prove governed catalog publication. | Report links registry identity, publication intent, lifecycle event, policy visibility, manifest/effective model validation, artifact trust, support chain, portability, sync/cache behavior, source coverage, source-safety and explicit non-claims. |
| CR-CONF-044 | Readiness must include developer workflow scenario evidence when a stage claims developer onboarding, local lifecycle, command journey, e2e readiness or showcase-driven workflow proof. | Binary availability, run profiles, docs and examples can hide missing behavior, unsupported modes, unsafe values and absent cleanup. | Report links role intent, prerequisites, workflow steps, state vocabulary, e2e scope, confidence, negative fixtures, cleanup/handoff, linked lifecycle/dependency/automation/docs evidence, source-safety and explicit non-claims. |
| CR-CONF-045 | Readiness must include release environment promotion evidence when a stage claims releasable artifact, provider/public promotion, task-image publication, UI bundle publication, base image promotion or production-like environment readiness. | Build success, CI entrypoints, tags, badges, manual jobs and local archives can hide missing artifact identity, environment bundle, approval, rollback and source safety. | Report links module identity, dependency/toolchain evidence, checks, runner semantics, immutable artifact, environment bundle, parity limits, secret/topology redaction, approval, promotion state, rollback, retention, post-promotion verification and explicit non-claims. |
| CR-CONF-046 | Readiness must include product service integration contract evidence when a service connects to shared platform capabilities such as catalog, usage, entitlement, support or audit. | API docs, generated specs, token existence and local tests can hide identity drift, broad credentials, unregistered resources, docs/spec/runtime drift and unsafe examples. | Report links product identity, scoped access, resource lifecycle, docs/spec/runtime drift, API version policy, submission semantics, positive/negative fixtures, support handoff, decommission, source-safety and explicit non-claims. |
| CR-CONF-047 | Readiness must include support diagnostics evidence when a stage claims provider support, operational diagnostics, incident triage, log/status export, stateful recovery support or agent-operated support flow. | Scattered logs, probes, generated docs and unimplemented export surfaces can hide unsafe bundles, missing owners, weak redaction, no retention and unsupported agent actions. | Report links support diagnostics package, target identity, lifecycle state, correlation, primary failure story, error taxonomy, retry/backpressure, image/stateful summaries, staged disclosure, owner approval, retention, source-safety, validation gaps and explicit non-claims. |
| CR-CONF-048 | Readiness must include support case/SLA/credit evidence when a stage claims tenant-facing support, SLA/SLO, maintenance impact, incident credit, refund, billing dispute or support escalation flow. | Support diagnostics, usage intake, service docs and maintenance notes can hide missing case ownership, ambiguous SLA clocks, unsafe party views, unapproved credits and settlement rewrite risk. | Report links support case object, offer/order/instance/plan/entitlement binding, owner/escalation, support boundary, severity, lifecycle state, SLA clock, maintenance relation, customer impact, communication cadence, diagnostics/billing/settlement links, credit/refund review, dispute hold/release, party-scoped views, source-safety, agent action boundaries and explicit non-claims. |
| CR-CONF-049 | Readiness must include portal experience evidence when a stage claims provider portal, self-service UI, role dashboard, operational portal, docs-as-entrypoint readiness or embedded portal surface readiness. | A blank module, local dev shell, static docs landing, screenshot or navigation tree can hide missing role journeys, consequences, states, owners, handoff and agent boundaries. | Report links portal surface identity, role-to-intent journeys, first useful tasks, docs/portal split, UI/API/CLI/Agent action parity, shared states, consequence-before-action, blocked/degraded/error handling, support-ready handoff, mode claims, artifact/release evidence, party-scoped views, accessibility/localization/responsive evidence or gaps, metrics, scenario coverage, source-safety and explicit non-claims. |
| CR-CONF-050 | Readiness must include reference service portfolio evidence when a stage claims golden services, showcase suite, service template readiness, boilerplate readiness or portfolio-based platform proof. | A single sample, docs scaffold, local start or integration demo can hide missing archetypes, placeholder docs, unsafe demo values, unproven task semantics and false production/provider claims. | Report links `CR-REFSVC-001..032`, archetype registry, portfolio coverage matrix, service purpose/stage/non-goals, first useful behavior, contract source-of-truth, run-mode boundaries, dependency ownership, docs/template readiness, observability semantics, task/data/object/secret evidence, positive/negative fixtures, support handoff, portability lessons, source-safety and explicit non-claims. |

## Standard Statuses

| Status | Meaning |
|---|---|
| passed | Evidence proves the check for the declared scope. |
| failed | Evidence contradicts the check or proves an unacceptable gap. |
| blocked | Required evidence is missing or prerequisite decision is absent. |
| warning | Product risk exists, but stage can be accepted with visible limitation. |
| skipped | Check is intentionally not run in this profile version with reason. |
| waived | Owner-approved temporary exception with scope and review trigger. |
| stale | Evidence is too old or contradicted by later signal. |
| not-applicable | Check does not apply to this scope and explains why. |
| degraded | Capability works with visible limitations and user/agent consequences. |
| manual_review_required | Owner, policy, legal, trust or governance decision is required. |
| unknown | Evidence is missing or unreadable; must be treated as warning or blocker. |

## Evidence Types

| Evidence | Product Meaning |
|---|---|
| Requirement trace | Check links to requirement, ADR, acceptance criteria or stage gate. |
| Product flow evidence | User/admin/developer/ISV/provider/support/governance/agent can complete or be explicitly marked not-applicable for the intended scenario. |
| Product design quality review | Flow proves role intent, visible consequences, alternatives, provider economics, jurisdiction overlay, failure handling and human-agent parity. |
| OCS information model evidence | OCS compatibility claim links model version, field registry, validation catalog, conformance suite and compatibility review. |
| Lifecycle command surface evidence | Command/API/Agent action claim links lifecycle contract, preflight, risk, structured result, cleanup and support-ready evidence. |
| Billing runtime evidence | Billable usage claim links receipt/status, event identity, idempotency, access freshness, backpressure, replay/quarantine, release/history evidence and settlement freeze. |
| Settlement closure evidence | Financial closeout claim links closure run, input manifest, reconciliation, freeze, correction lineage, disputes, participant shares, approval, export, retention and source safety. |
| Presence bootstrap activation evidence | Local/private activation claim links trusted assets, config schema, preflight, runtime provider state, diagnostics, rollback, offline/private behavior, infrastructure profile and source safety. |
| Controlled extension/task automation evidence | Task/plugin/dependency/boilerplate claim links automation kind, owner, selection rationale, artifact trust, execution scope, env/secret boundary, rollback/compensation, structured result, conformance and agent approval. |
| Service registry/catalog publication evidence | Registry/catalog publication claim links service identity, visibility, lifecycle, publication plan, policy result, manifest/effective model validation, artifact/dependency/support evidence, sync/cache, source coverage and source safety. |
| Developer workflow scenario evidence | Developer workflow claim links role intent, prerequisites, action sequence, expected states, e2e scope, confidence, negative cases, cleanup, handoff and source-safe non-claims. |
| Release environment promotion evidence | Release or promotion claim links module identity, dependency lock, checks, runner, immutable artifact, environment bundle, approval, rollback, retention, post-promotion verification and source-safe non-claims. |
| Product service integration contract evidence | Shared-capability integration claim links product identity, scoped credential, resource lifecycle, human guide, machine contract, docs/spec/runtime drift, fixtures, support handoff, decommission and source-safety non-claims. |
| Support diagnostics evidence | Support or incident claim links read-only diagnostics package, target identity, lifecycle state, correlation, primary failure story, signal matrix, image/stateful summaries, redaction, staged disclosure, approval, retention and source-safety non-claims. |
| Support case/SLA/credit evidence | Tenant-facing support, SLA or credit claim links support case object, support owner, offer/order/instance/plan/entitlement binding, support boundary, lifecycle state, SLA clock, diagnostics, billing receipt/status, settlement closure, credit/refund review, party-scoped views, agent handoff and source-safety non-claims. |
| Stateful recovery evidence | Stateful readiness claim links topology, backup/archive, restore, PITR, failover, endpoint ownership, audit findings, role matrix, recovery impact, history coverage and source safety. |
| Documentation decision-memory evidence | Docs/ADR/source-pass claim links requirement, decision rationale, template, example, scenario, conformance gate, owner, freshness, source-safety and non-claims. |
| Secret runtime readiness evidence | Encrypted credential claim links secret reference boundary, scope binding, key and certificate custody, reconciliation status, install/delete behavior, RBAC, health/metrics, rotation/degraded behavior, source-safety and non-claims. |
| Service dependency/deployment evidence | Dependency or generated deployment claim links effective service model, dependency graph, component ownership, connection outputs, generated artifacts, env handoff, preflight, portability, source-safety and non-claims. |
| Contract evidence | Manifest/API/lifecycle/policy contract expresses the expected behavior. |
| Operational evidence | Health, telemetry, incident, backup/restore, runbook or support trace. |
| Trust evidence | Identity, certification, audit, secret boundary, supply-chain or policy result. |
| Policy evidence | Placement, jurisdiction, data residency, budget, trust or approval decision. |
| Audit evidence | Actor, action, time, risk class, approval, correlation and validation record. |
| Economic evidence | Order, usage, entitlement, invoice, credit, settlement or dispute state. |
| Support evidence | Owner, SLA/SLO, incident timeline, handoff and escalation state. |
| Portability evidence | Export, migration, replication, restore, exit or limitation proof. |
| Experience evidence | Intent-first flow, consequence-before-action, explanation and useful failure. |
| Agent evidence | Scope, risk class, plan, validation, rollback/compensation and audit summary. |
| Evolution evidence | Signal, triage, requirement/ADR/runbook/check update and closure outcome. |

## Blocking Classes

Critical blocker means CloudRING cannot honestly claim the profile promise.

Mandatory blocker classes:

- no trace to requirement/ADR for accepted requirement;
- no validation path and no documented exception;
- no user-visible readiness report;
- missing owner or unclear responsibility boundary;
- plaintext secret/private data appears in manifest, docs, report or artifacts;
- policy decision is missing for placement, data movement, billing or trust action;
- portability is promised without export/migration/limitation evidence;
- risky/destructive agent action lacks approval, validation or rollback/compensation;
- billing, settlement, support or SLA claim lacks evidence bundle;
- certification/trust downgrade is hidden from user/admin/agent;
- outage creates central lock-in where local autonomy was promised;
- conformance exception is expired, ownerless or lacks review trigger.

## Waiver Schema

```yaml
id: waiver-id
profile: stageN-profile-ready
check_id: CONF-STAGEN-000
status: proposed | approved | expired | revoked | superseded
owner: role-or-person
approver: role-or-person
reason: product reason
scope: affected service/presence/participant/profile
affected_users: summary
risk: risk statement
compensation: mitigation or customer/support plan
review_trigger: date, incident, dependency, policy or metric
expiry: date-or-condition
linked_requirement: CR-...
linked_adr: ADR-...
```

Waiver cannot approve violation of mission-level boundaries: secret safety,
auditability, ownership, user control over data, explicit policy decisions and
anti-lock-in guarantees.

## Owners

| Role | Responsibility |
|---|---|
| Profile owner | Owns meaning, version and evolution of the readiness profile. |
| Requirement owner | Owns product why, acceptance and superseding decisions. |
| Domain owner | Owns domain-specific risk such as IAM, billing, federation, security, marketplace or agent governance. |
| Evidence owner | Owns freshness and truthfulness of linked evidence. |
| Exception owner | Owns waiver risk until expiry/review. |
| Approver | Accepts high-impact trade-off or waiver. |
| Operator | Executes readiness/remediation activity. |
| AI agent | Collects evidence and proposes remediation within scope; does not accept major trade-offs. |
| Participant owner | Owns provider/private/edge/ISV responsibility boundary. |
| Governance owner | Resolves conflicts, certification downgrades and federation/global policy changes. |

## Report Shape

```yaml
profile_id: stageN-name-ready
profile_version: 0.1
stage: N
status: passed | failed | blocked | warning | skipped | waived | stale | not-applicable | degraded | manual_review_required | unknown
scope:
  product_increment: name
  environment_profile: local | private | provider | federation | global | edge
summary:
  decision: ready | ready-with-limitations | not-ready
  blockers: []
  warnings: []
  next_stage_gaps: []
role_coverage:
  user: passed | blocked | waived | not-applicable | unknown
  admin: passed | blocked | waived | not-applicable | unknown
  developer_or_isv: passed | blocked | waived | not-applicable | unknown
  provider: passed | blocked | waived | not-applicable | unknown
  support: passed | blocked | waived | not-applicable | unknown
  governance: passed | blocked | waived | not-applicable | unknown
  ai_agent: passed | blocked | waived | not-applicable | unknown
scenario_refs:
  - SCENARIO-...
owners:
  profile_owner: role
  evidence_owner: role
  exception_owner: role
  approver: role
checks:
  - id: CONF-STAGEN-001
    status: passed
    requirement_refs:
      - CR-CONF-001
    evidence_refs:
      - safe-reference
    owner: role
    freshness: current | stale | unknown
    notes: concise human explanation
exceptions:
  - scope: optional
    reason: optional
    owner: optional
    review_trigger: optional
agent_review:
  risk_class: read-only
  allowed_actions: []
  forbidden_actions: []
  required_approvals: []
  validation_needed: []
  remaining_gaps: []
```

## Non-Goals

Conformance profiles are not:

- implementation test scripts;
- vendor-specific certification programs;
- legal guarantees for every jurisdiction;
- a way to bypass ADR or owner approval;
- a reason to demand future-stage capabilities from an earlier stage;
- a place to store raw source snippets, secrets, tenant data or private paths.
