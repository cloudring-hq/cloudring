# Conformance Profile - Stage 4 Public Provider Ready

---
profile_id: stage4-public-provider-ready
profile_version: 0.9
stage: 4
stage_file: ../stages/04-public-cloud-provider-kit.md
change_note: SRC-PASS-028 added portal experience evidence gates.
---

## Purpose

Доказать, что Stage 4 позволяет независимому оператору запустить public provider
presence, продавать услуги, принимать tenants, собирать usage, выставлять
provider-local invoices and operate support/SLA before federation.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE4-001 | Provider onboarding is self-service readiness flow. | Public provider ecosystem cannot scale manually. | Identity, presence profile, regions, services, billing/support readiness and blockers. | Provider cannot become active without hidden manual integration. |
| CONF-STAGE4-002 | Public offer has lifecycle and certification state. | Provider active does not mean every offer is safe. | Offer candidate/active/blocked/limited/public-ready state with policy gate, artifact identity, provenance, freshness and rollback/deprecation target where artifacts/images are sold or installed. | Offer can be sold without certification or warning scope. |
| CONF-STAGE4-003 | Tenant order flow works end to end. | Provider kit must sell actual cloud service. | Tenant selects plan/region/SLA/support, confirms price, gets service instance. | Order cannot complete without operator intervention. |
| CONF-STAGE4-019 | Provider portal experience evidence exists before provider portal or self-service UI readiness is claimed. | Public provider readiness cannot rely on a blank frontend shell, local dev mode, static documentation landing, screenshot or embedded component without product journeys. | Portal experience evidence links `CR-PORTALUX-001..032`, `SCENARIO-STAGE4-009`, surface identity, role-to-intent journeys, first useful tasks, docs/portal split, UI/API/CLI/Agent action parity, shared states, consequence-before-action, blocked/degraded/error handling, support-ready handoff, mode claims, artifact/release evidence, party-scoped views, metrics, accessibility/localization/responsive evidence or gaps, source-safety and non-claims. | Provider portal is marked ready while role journeys are missing, visible actions lack shared intent/result/evidence mapping, consequences are hidden, docs/demo mode is treated as live self-service, party views leak restricted state or agents can execute high-impact portal actions without approval. |
| CONF-STAGE4-004 | Usage and provider-local billing evidence exists. | Public cloud requires transparent money flow. | Usage metrics, invoice profile, credit/dispute path and billing audit. | Usage cannot be traced to invoice/credit. |
| CONF-STAGE4-011 | Usage gateway is scoped, versioned, idempotent and backpressure-aware. | Billing correctness depends on event quality. | Usage fixtures prove scope, version, mandatory or explicitly exempted idempotency, duplicate/replay, period order/overlap/correction, metadata limits/redaction, stale-token denial, queue flush, shutdown delay, backpressure and shared decision-state mapping. | Duplicate, missing, stale or overloaded usage can double-charge or disappear without correction evidence. |
| CONF-STAGE4-013 | Billing runtime evidence proves receipt/status and settlement freeze boundaries. | Provider-local invoices must not rely on opaque intake success. | Billing runtime evidence covers support-safe receipt, async status, batch semantics, event identity, idempotency conflict, access freshness, queue/backpressure, replay/quarantine, release/history evidence, generated docs/config safety and provider-local settlement freeze. | Provider-local invoice or dispute uses usage that lacks receipt/status, replay/quarantine or release/history evidence. |
| CONF-STAGE4-015 | Provider-local settlement closure evidence exists before period closeout. | Public provider money cannot be closed from intake success or invoice draft alone. | Settlement closure evidence covers closure run, input manifest, reconciliation, freeze gate, invoice/credit/refund trace, dispute hold/release, closeout export, approvals, release/history evidence and source safety for provider-local scope. | Provider closes period with unknown usage/backlog, missing reconciliation, missing dispute evidence or unapproved financial adjustment. |
| CONF-STAGE4-005 | Tenant isolation, security baseline and source-safe evidence handling are proven. | Public provider increases blast radius and evidence can expose sensitive operational context. | Isolation evidence, audit, supply chain verification, image/template hardening/residue evidence, secret boundary and redacted/classified operational evidence handling. | Tenant boundary is unknown, unverified or evidence leaks secret/source-private material. |
| CONF-STAGE4-006 | SLA/SLO and support are productized. | Buyer pays for operating promise, not only runtime. | Service card, support owner, incident flow, maintenance window and SLA/SLO evidence. | Support ownership unclear. |
| CONF-STAGE4-007 | Operations readiness is visible and blocks unsafe provider claims. | Provider must run services, not just publish them. | Health, incidents, stateful audit bundle, backup/restore/failover freshness, normalized audit failures, capacity, image/template freshness, diagnostic boundary, source-safe redaction/classification and support queue evidence. | Provider cannot see capacity/incidents/recovery/revenue/support state, or blocking stateful audit failures are ignored. |
| CONF-STAGE4-014 | Stateful provider recovery evidence is visible before selling stateful service promises. | Tenants buy supportable recovery outcomes, not hidden internal backup notes. | Provider offer/support evidence links restore/PITR/failover freshness, endpoint ownership, tenant impact, audit blockers, source-safe diagnostic boundary, waiver expiry and remediation path. | Provider sells stateful service/SLA while recovery evidence is stale, raw, ownerless, hidden from tenant decision or blocked by unresolved audit findings. |
| CONF-STAGE4-016 | Release environment promotion evidence exists before provider-impacting artifact activation. | Public provider readiness cannot be inferred from build success, CI entrypoint, tag, badge, manual job or local archive. | Release promotion evidence links `CR-RELPROM-001..032`, `SCENARIO-STAGE4-006`, module identity, dependency/toolchain evidence, check matrix, runner semantics, immutable artifact, environment bundle, parity limits, secret/topology redaction, approval, promotion state, rollback/retention and post-promotion verification. | Provider-visible artifact is activated while artifact identity, environment bundle, approval, rollback, retention, source safety or post-promotion verification is unknown. |
| CONF-STAGE4-017 | Support diagnostics evidence exists before provider support readiness is claimed. | Public provider support cannot rely on scattered logs, generic health, generated docs or unsafe diagnostic exports. | Support diagnostics evidence links `CR-SUPDIAG-001..032`, `SCENARIO-STAGE4-007`, read-only collection, target identity, lifecycle state, correlation, primary failure story, error taxonomy, retry/backpressure, image/stateful summaries, issue classification, staged disclosure, owner approval, retention, source-safety and validation gaps. | Provider support is marked ready while diagnostics collection mutates state, health/readiness/drain are ambiguous, correlation is missing, owner/retention is unknown, raw sensitive evidence leaks or log/status export is unimplemented. |
| CONF-STAGE4-018 | Support case/SLA/credit evidence exists before provider support, SLA or credit readiness is claimed. | Public provider support cannot rely on informal tickets, diagnostics, usage intake, maintenance notes or manual finance decisions. | Support case evidence links `CR-SUPCASE-001..032`, `SCENARIO-STAGE4-008`, offer/order/instance/plan/entitlement binding, owner/escalation, support boundary, severity, lifecycle state, SLA clock, maintenance relation, customer impact, communication cadence, diagnostics/billing/settlement links, credit/refund review, dispute hold/release, party-scoped views, source-safety, agent boundaries and non-claims. | Provider support/SLA/credit is marked ready while case owner is unknown, SLA clock/policy is missing, credit decision lacks approval/calculation/correction lineage, disputed amount can settle silently, party views leak restricted data or agents can mutate financial/status state without approval. |
| CONF-STAGE4-008 | Federation-ready metadata exists without requiring federation. | Stage 4 prepares Stage 5 but works alone. | Catalog, usage, support and certification metadata are future-sync-ready. | Provider-local operation depends on multi-provider federation. |
| CONF-STAGE4-009 | Stage 4 does not require cross-participant settlement. | Multi-party economy belongs to Stage 5. | Provider-local invoice works; cross-settlement is marked future gap. | Profile blocks readiness because federation settlement is absent. |
| CONF-STAGE4-010 | Suspension/cancel preserves export, recovery and appeal path. | Public cloud must not trap or silently destroy customer state. | Cancel/suspend audit includes reason, customer impact, export/recovery/appeal and billing closeout. | Suspension hides data controls or has no appeal/recovery path. |
| CONF-STAGE4-012 | Role scenario coverage matrix exists for public provider kit. | Provider readiness must prove provider, tenant, support, billing and agent journeys. | Scenario matrix links provider onboarding, tenant order, usage/billing, support incident, cancellation/export and agent operation fixtures. | Stage 4 passes without reusable provider/tenant/support scenario evidence. |

## Required Report Outcome

`stage4-public-provider-ready` is passed when one provider can sell and operate
services responsibly, with portal experience, billing/support/SLA/
support-diagnostics/support-case evidence and federation only as a future-ready
path.

## Profile Non-Goals

- Multi-provider catalog sync.
- Cross-participant settlement.
- Global trust fabric.
- Worldwide marketplace discovery.
