# Billing Runtime Evidence And Settlement Trust

Этот документ углубляет `CR-BILL-*`: не заменяет billing capability, а задает
runtime evidence layer для billable usage ingestion, receipt, replay,
quarantine, release history and settlement freeze.

Downstream financial closure, reconciliation, dispute hold/release and closeout
export are specified separately in
[39-settlement-closure-and-dispute-evidence.md](39-settlement-closure-and-dispute-evidence.md).

Главный продуктовый урок source-slice: successful API response не должен
читаться как "деньги уже правильно начислены". Для CloudRING нужно различать
received, validated, accepted, enqueued, published, settled, rejected,
quarantined, corrected and disputed states, иначе support, provider, buyer and
AI agents не смогут доказать, что произошло.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-BILLRUN-001 | Billable usage intake must separate transport success from financial truth. | `2xx` or command success can mean only local acceptance, not invoice/settlement readiness. | Receipt and status model distinguish received, validated, accepted, enqueued, published, settled, rejected, quarantined, corrected and disputed states. |
| CR-BILLRUN-002 | Usage event contract must include commercial attribution fields. | Product/resource identity alone cannot prove active order, offer, entitlement or price context. | Event or linked context includes account/tenant, order, offer, entitlement, product/service, resource, instance, period, unit, amount, source and version. |
| CR-BILLRUN-003 | Resource registration lifecycle must be explicit before billable usage. | Billing cannot charge honestly for unregistered or stale value units. | Resource record supports create, update, retire, version, tariff binding, compatibility and behavior for unregistered or retired resource usage. |
| CR-BILLRUN-004 | Usage event identity must be canonical and payload-bound. | Retries, metadata ordering and migrations can create duplicate or conflicting charges. | Identity algorithm or declared external identity is stable, versioned, redaction-safe, collision-reviewed and covered by duplicate/replay fixtures. |
| CR-BILLRUN-005 | Request idempotency and event identity must be separate concepts. | One request can contain many events, and one event can be replayed through different requests. | Contract separately defines request idempotency key, event identity, batch identity and conflict behavior. |
| CR-BILLRUN-006 | Reused idempotency key with different payload must not be silently accepted. | Duplicate suppression without payload comparison hides data corruption and disputes. | Gateway returns original receipt for same payload or conflict/quarantine for changed payload with reason and evidence. |
| CR-BILLRUN-007 | Batch semantics must be all-or-nothing or per-item explicit. | Silent post-accept drops are unacceptable for money events. | Batch response states atomic reject or item-level accepted/rejected/quarantined records with IDs, reasons and retryability. |
| CR-BILLRUN-008 | Accepted usage must produce a support-safe receipt. | Support and agents need a handle without raw payload or credentials. | Receipt includes operation id, event IDs or redacted hashes, counts, status URL/reference, timestamps, version, warnings, retryability and evidence retention. |
| CR-BILLRUN-009 | Asynchronous processing must expose status transitions. | Users and providers need to know whether usage is waiting, published, failed or settled. | Status query/report shows current stage, last transition, owner, retry/quarantine state, downstream evidence refs and freshness. |
| CR-BILLRUN-010 | Usage gateway must either persist before success or declare a bounded volatile acceptance contract. | Crash after success before publish can lose billable usage. | Readiness evidence proves durable outbox/ledger before success, or clearly marks volatile mode with resend/reconciliation rules and stage limitation. |
| CR-BILLRUN-011 | Queue/backpressure response must be retry-safe and machine-readable. | Generic server failure causes unsafe retry behavior and hidden invoice delay. | Response includes stable code, retry class, backoff guidance, correlation id, affected scope and customer/provider impact. |
| CR-BILLRUN-012 | Shutdown and drain must be a billing state transition. | Best-effort flush is not enough for audit-grade money events. | Shutdown stops new intake, drains within policy, persists or quarantines remaining events, emits drain summary and blocks readiness if residue is unknown. |
| CR-BILLRUN-013 | Replay and quarantine must be first-class product flows. | Invalid, poison, transform-failed or not-published usage must not disappear into logs. | Quarantine supports search, reason, owner, replay, void, correction, dispute link, retention and audit approval. |
| CR-BILLRUN-014 | Conversion/serialization failures after validation must be visible. | A valid request can still fail while becoming downstream event. | Decision ledger records transform-rejected or serialization-rejected states with safe reason and no invoice impact until corrected. |
| CR-BILLRUN-015 | Access freshness must gate billable acceptance. | Stale access cache can accept usage after revocation or reject valid usage after grant. | Decision evidence includes access source, last sync, active/stale/revoked/degraded state, fail-open/fail-closed policy and affected scope. |
| CR-BILLRUN-016 | Usage access scopes must be separate for registration, submission, admin and correction. | One broad product credential creates commercial blast radius. | Scope model distinguishes resource registration, usage submission, replay/correction, admin, settlement and support-read actions. |
| CR-BILLRUN-017 | Readiness must include dependencies that affect billing truth. | Process liveness is weaker than billable intake readiness. | Readiness checks intake, datastore, idempotency store, broker/outbox, queue headroom, access freshness, docs/spec freshness and evidence sink. |
| CR-BILLRUN-018 | Usage observability must estimate blast radius. | Incidents need fast understanding of affected offers, customers and invoices. | Metrics/reports cover received, accepted, rejected, duplicate, queued, published, delayed, quarantined, replayed, corrected, disputed, queue depth, flush latency, access age and drain duration. |
| CR-BILLRUN-019 | Error envelopes must be stable across usage API versions. | Clients and agents need one interpretation even when APIs evolve. | Error/result object includes stable code, reason, field path, retryability, owner, correlation, human detail and source-safe diagnostics. |
| CR-BILLRUN-020 | Time and period policy must be canonical. | Period bugs cause double charging, missing charges and disputes. | Contract validates time normalization, period ordering, non-zero duration, late-arrival policy, overlap, replacement, correction and timezone handling. |
| CR-BILLRUN-021 | Unit catalog must be canonical and versioned. | Unit drift breaks tariff, invoice and settlement interpretation. | Usage resource binds allowed units, unit versions, conversion policy, tariff basis and incompatible-change handling. |
| CR-BILLRUN-022 | Correction, reversal and replacement must be explicit usage operations. | Negative or compensating events need governance, not ad hoc payload tricks. | Correction flow links original event, reason, approver/policy, replacement/reversal semantics, invoice/credit impact and dispute state. |
| CR-BILLRUN-023 | Metadata must be bounded, classified and identity-aware. | Metadata can help uniqueness but also leak data or destabilize billing identity. | Contract defines allowed keys/classes, size/count/length, identity participation, retention, redaction, rejection and quarantine behavior. |
| CR-BILLRUN-024 | Generated API docs and deployment profiles must be source-safety gates for billing. | Docs/config can leak private context or stale commercial promises. | Publication and settlement readiness block on generated docs/config freshness, redaction, internal-marker scan, example safety and contract drift check. |
| CR-BILLRUN-025 | Billing release readiness cannot be inferred from tag existence. | Debug-like, lightweight or duplicate-target tags are weak evidence for money systems. | Release evidence includes artifact identity, API contract version, test result, owner, tag/ref quality, rollback/deprecation note and source-safety scan. |
| CR-BILLRUN-026 | Billing readiness must include billing-specific history coverage. | Deleted tests and non-default refs can contain product decisions missing from current tree. | Evidence manifest records all-refs counts, tag classes, duplicate-target signals, dirty state, deleted-path themes, repeated-fix themes and non-claims. |
| CR-BILLRUN-027 | Repeated billing-critical fixes must become learning artifacts. | Fix repetition in money flows is a product signal, not background noise. | Repeated validation, access, queue, docs, config or migration fixes create regression fixtures, conformance checks, runbook/ADR updates or signed no-change decision. |
| CR-BILLRUN-028 | Deleted or replaced tests/mocks must become fixture backlog when they encode billing behavior. | Current-tree tests can be weaker than historical intent. | Source pass records deleted test themes and creates source-safe fixture backlog with coverage status and owner. |
| CR-BILLRUN-029 | Version migration must be simulated before billing depends on a new usage contract. | Mixed clients and delayed events are normal in cloud platforms. | Evidence covers old/new client compatibility, replay, idempotency, period/correction behavior, rollback and settlement impact. |
| CR-BILLRUN-030 | Settlement freeze must depend on a complete usage evidence bundle. | Accepted usage alone is not settlement truth. | Settlement evidence freezes order, entitlement, usage receipt/status, decision ledger, invoice/credit/dispute path, access freshness, release provenance and participant-scoped visibility. |
| CR-BILLRUN-031 | Provider-local billing and federation settlement must use staged evidence. | Stage 4 must work alone; Stage 5 must not invent trust without Stage 4 proof. | Stage 4 requires provider-local usage/invoice/dispute evidence; Stage 5 adds participant shares and cross-participant replay/dispute evidence. |
| CR-BILLRUN-032 | Billing runtime evidence must remain source-safe and party-scoped. | Money investigations often touch credentials, tenant data and private topology. | Evidence redacts credentials, private topology and tenant-sensitive data while preserving enough hashes/IDs/states for dispute and audit. |

## Evidence Model

Minimum billing runtime evidence bundle:

```yaml
billing_runtime_evidence:
  evidence_id: billing-runtime-evidence-id
  profile_refs:
    - stage4-public-provider-ready
  scenario_refs:
    - SCENARIO-STAGE4-004
  usage_contract:
    version: usage-contract-version
    attribution_status: passed | warning | failed | blocked
    resource_lifecycle_status: passed | warning | failed | blocked
    unit_period_policy_status: passed | warning | failed | blocked
  intake_result_model:
    receipt_status: passed | warning | failed | blocked
    async_status_transitions: passed | warning | failed | blocked
    batch_semantics: atomic | per-item | blocked | unknown
    error_envelope_status: passed | warning | failed | blocked
  idempotency_and_identity:
    event_identity_status: passed | warning | failed | blocked
    request_idempotency_status: passed | warning | failed | blocked
    conflict_detection_status: passed | warning | failed | blocked
  operations:
    readiness_status: passed | warning | failed | blocked
    backpressure_status: passed | warning | failed | blocked
    shutdown_drain_status: passed | warning | failed | blocked
    replay_quarantine_status: passed | warning | failed | blocked
    observability_status: passed | warning | failed | blocked
  release_history:
    release_evidence_status: passed | warning | failed | blocked
    history_coverage_status: passed | warning | failed | blocked
    repeated_fix_learning_status: passed | warning | failed | blocked
    generated_docs_config_status: passed | warning | failed | blocked
  settlement_freeze:
    provider_local_status: passed | warning | failed | blocked | not-applicable
    cross_participant_status: passed | warning | failed | blocked | not-applicable
    dispute_support_status: passed | warning | failed | blocked
  source_safety:
    redaction_status: passed | warning | failed | blocked
    party_scope_status: passed | warning | failed | blocked
  unresolved_gaps:
    - gap
```

## Stop Conditions

Agent must stop and request owner/review if:

- accepted usage could be lost after success without durable evidence or clear
  volatile contract;
- idempotency hides a changed payload or event identity conflict;
- batch success can hide dropped or transform-failed items;
- access freshness, queue state or generated docs/config freshness is unknown
  but readiness is claimed;
- settlement is created without frozen usage/order/entitlement/invoice/dispute
  evidence;
- release readiness is claimed from tags without artifact/test/source-safety
  evidence;
- source-derived billing evidence would include credentials, tenant data,
  internal endpoints, private paths, raw source snippets or raw commit subjects.

## Non-Goals

- Не выбирать конкретный брокер, базу данных, payment processor, tax engine или
  settlement rail.
- Не переносить старую реализацию usage gateway.
- Не утверждать downstream settlement correctness из одного intake slice.
- Не делать universal tax/legal automation.
- Не использовать billing как механизм удержания пользователя.
