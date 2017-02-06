# Settlement Closure And Dispute Evidence

Этот документ углубляет `CR-BILL-*` и `CR-BILLRUN-*`: usage gateway может
принять событие, но CloudRING не должен считать деньги доказанными, пока период,
invoice/credit/refund, settlement shares, corrections and disputes не закрыты
через воспроизводимый evidence package.

Главный продуктовый урок source-slice: ingestion, queue delivery, generated API
docs and release tags дают важные сигналы, но не доказывают downstream
settlement correctness. CloudRING должен явно проектировать финансовое закрытие
как продуктовый workflow, а не как побочный эффект pipeline.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SETTLE-001 | Settlement closure должен быть named product workflow, а не скрытый batch job. | Деньги нельзя закрывать неявно: buyer, provider, participant, support and agents должны понимать состояние периода. | Closure run has id, scope, period, stage, owner, status, evidence bundle, blockers and next allowed actions. |
| CR-SETTLE-002 | Closure scope must be period-scoped, party-scoped and offer/order-scoped. | Один сбой в периоде или participant chain не должен загрязнять всю экономику платформы. | Scope declares provider/local/federation/global level, participants, orders, offers, resources, currencies and excluded/non-applicable items. |
| CR-SETTLE-003 | Closure input manifest должен перечислять все входы финансовой правды. | Без manifest невозможно доказать полноту reconciliation. | Manifest links orders, entitlements, usage receipts/statuses, decision ledger, invoices, credits/refunds, disputes, support/SLA events, policy decisions, release evidence and generated-doc/config safety. |
| CR-SETTLE-004 | Period cannot close while billable usage state is unknown. | Unknown usage silently creates lost revenue, overcharge or future dispute. | Close blocks or marks manual review when usage is received, queued, delayed, quarantined, transform-rejected, replaying, disputed, corrected or freshness-unknown without closure decision. |
| CR-SETTLE-005 | Late-arriving usage policy must be explicit before period close. | Cloud systems retry and reconnect; late usage must not become surprise invoice magic. | Policy defines cutoff, grace, backfill, adjustment, rejection, customer/provider notice and dispute impact. |
| CR-SETTLE-006 | Reconciliation must compare pipeline stages and financial outputs. | Accepted, published, invoiced and settled are different truths. | Reconciliation report compares counts, units, amounts and identities across intake, accepted, published/downstream, invoice, credit/refund and settlement-share states. |
| CR-SETTLE-007 | Reconciliation differences must have stable reason taxonomy. | Agents and support need repeatable handling, not ad hoc explanations. | Difference reasons include duplicate, missing identity, late usage, stale access, invalid period, transform failure, quarantine, correction, dispute, release/config drift and manual override. |
| CR-SETTLE-008 | Settlement freeze must happen only after reconciliation and source-safety gates pass. | Frozen money evidence should not preserve unsafe docs, internal examples or stale commercial promises. | Freeze records reconciliation status, redaction status, generated artifact freshness, release evidence, unresolved warnings and owner approval. |
| CR-SETTLE-009 | Closed period must be immutable except through governed reopen or adjustment. | Silent mutation destroys audit, trust and participant accounting. | After close, changes require reopen, adjustment period or credit/refund/correction record with reason, approver, affected parties and lineage. |
| CR-SETTLE-010 | Correction, reversal and replacement must preserve lineage to original usage. | Commercial corrections should explain what changed and why. | Correction evidence links original event/line/share, reason, policy, approver, replacement/reversal, invoice/credit/refund impact and dispute state. |
| CR-SETTLE-011 | Invoice, credit and refund lines must trace to closure evidence. | Customer-visible money needs the same truth as provider accounting. | Each line references usage/resource/period, order/entitlement, price basis, policy decision, correction/dispute status and source-safe evidence reference. |
| CR-SETTLE-012 | Participant share calculation must be explainable and scoped. | Federation commerce fails if participants cannot verify their share without seeing unrelated customer data. | Share record shows participant role, commercial term version, scope, period, base amount, adjustments, withheld/disputed amount, visibility boundary and evidence refs. |
| CR-SETTLE-013 | Provider-local closure and cross-participant settlement must be separate stages. | Stage 4 must be useful alone; Stage 5 must add trust without rewriting provider-local billing. | Stage 4 closes provider-local invoices; Stage 5 adds participant shares/reconciliation/disputes; Stage 6 adds global/multi-jurisdiction overlays. |
| CR-SETTLE-014 | Dispute can be opened before or after closure with defined financial effect. | Real disputes do not always arrive at a convenient time. | Dispute record states open time, affected lines/shares, amount hold/release behavior, SLA/support context, evidence bundle, owner and decision deadline. |
| CR-SETTLE-015 | Disputed amounts must not settle silently. | Participants and buyers need confidence that disagreement is not hidden in payout. | Closure report separates undisputed settled amount, disputed held amount, waived amount, credited amount and manual-review amount. |
| CR-SETTLE-016 | Dispute evidence bundle must be human-readable and agent-readable. | Support resolution across providers cannot rely on tribal memory. | Bundle includes order, entitlement, usage status, decision ledger, reconciliation delta, policy, support timeline, participant chain, correction history and decision outcome. |
| CR-SETTLE-017 | Settlement closure must provide scoped party views. | Evidence must prove money without over-sharing tenant, topology or participant-private data. | Buyer, provider, actual provider, ISV, reseller, governance and agent views expose only relevant charges/shares/evidence/actions. |
| CR-SETTLE-018 | Closeout export must be available for customer exit and provider offboarding. | Anti-lock-in includes commercial exit, not only data export. | Export includes invoices, credits/refunds, disputes, entitlements, usage summary, closure status, retained evidence and unresolved obligations. |
| CR-SETTLE-019 | Suspension or cancellation must include billing closeout before destructive action. | Commercial enforcement must not trap data or erase dispute evidence. | Cancel/suspend flow shows reason, scope, export/recovery/appeal, final invoice/credit/dispute state and retained evidence. |
| CR-SETTLE-020 | Agent actions that close, reopen, credit, refund, settle or release disputed money require approval. | AI agents may assist finance operations, but must not become hidden financial authority. | Approval record covers actor, approver, scope, risk, policy, evidence reviewed, compensation/rollback and audit result. |
| CR-SETTLE-021 | Manual override must be visible as a risk, not hidden as normal closure. | Manual finance fixes are sometimes needed but can become silent lock-in or fraud risk. | Override records reason, owner, approver, affected parties, amount, evidence gap, expiry/review trigger and follow-up requirement/ADR/runbook decision. |
| CR-SETTLE-022 | Tax, legal and regulatory metadata must be captured without claiming universal automation. | Global cloud commerce needs context but cannot pretend one rules engine solves every jurisdiction. | Closure carries jurisdiction, tax/commercial metadata, manual-review state, limitation statement and exportable evidence for specialist review. |
| CR-SETTLE-023 | Currency, rounding and minimum-charge policy must be explicit. | Small rounding differences can create recurring disputes and participant mistrust. | Closure evidence states currency, conversion source class, rounding rule, precision, minimum/maximum charge behavior, participant-share rounding and dispute threshold. |
| CR-SETTLE-024 | Closure observability must expose financial blast radius. | Operators need to know who and what is affected before touching money. | Metrics/reports cover close status, blocked periods, unresolved deltas, late usage, disputed amount, held shares, correction count, manual overrides and aging. |
| CR-SETTLE-025 | Closure must preserve audit retention and immutability expectations. | Future investigations need stable evidence even after services exit or participants leave. | Evidence retention policy defines summary vs restricted detail, immutability, redaction, access roles, retention period, deletion limits and appeal/dispute retention. |
| CR-SETTLE-026 | Release/history evidence must gate closure logic changes. | A changed validation, idempotency or reconciliation rule can alter money. | Closure readiness links release identity, compatibility impact, migration/replay simulation, regression/negative fixtures, rollback note and source-safety review. |
| CR-SETTLE-027 | Mixed-version and delayed-event migration must be simulated before close. | Cloud clients and federation participants update at different speeds. | Evidence covers old/new usage contract, replay, correction, idempotency, period policy, participant-share impact and rollback/adjustment behavior. |
| CR-SETTLE-028 | Generated docs/config must be checked as commercial evidence surfaces. | Docs can teach clients wrong billing behavior or leak unsafe examples. | Closure blocks or warns on stale docs, unsafe examples, internal markers, endpoint/credential leakage or mismatch between published contract and runtime behavior. |
| CR-SETTLE-029 | Closure fixtures must include happy path, negative path and recovery path. | Money readiness needs proof for normal and abnormal operations. | Fixture set covers clean close, duplicate usage, late usage, quarantine, correction, dispute, participant-share hold/release, manual override and source-safety failure. |
| CR-SETTLE-030 | Settlement closure status taxonomy must be shared across UI/API/CLI/Agent API. | Human and agent must reason over the same financial state. | Status vocabulary includes draft, reconciling, blocked, manual-review, closed, reopened, adjusted, voided, disputed, partially-settled and settled. |
| CR-SETTLE-031 | Settlement closure evidence must feed learning loop. | Repeated money deltas are product requirements, not accounting noise. | Repeated closure failures create requirement, ADR, runbook, conformance check, fixture or owner-approved no-change rationale. |
| CR-SETTLE-032 | Settlement closure requirements must remain source-safe and reimplementation-oriented. | The product memory must survive old source disappearance without copying it. | Evidence and requirements contain no raw source paths, private names, endpoints, secrets, tenant data, copied docs, exact commands or raw commit subjects. |

## Evidence Model

Minimum settlement closure evidence bundle:

```yaml
settlement_closure_evidence:
  evidence_id: settlement-closure-evidence-id
  profile_refs:
    - stage4-public-provider-ready
    - stage5-federation-ready
  scenario_refs:
    - SCENARIO-STAGE5-006
  closure_run:
    scope_status: passed | warning | failed | blocked
    period_status: passed | warning | failed | blocked
    party_scope_status: passed | warning | failed | blocked
    status_taxonomy_status: passed | warning | failed | blocked
  input_manifest:
    usage_status: passed | warning | failed | blocked
    order_entitlement_status: passed | warning | failed | blocked
    invoice_credit_refund_status: passed | warning | failed | blocked
    dispute_support_policy_status: passed | warning | failed | blocked
    generated_docs_config_status: passed | warning | failed | blocked
  reconciliation:
    pipeline_comparison_status: passed | warning | failed | blocked
    difference_taxonomy_status: passed | warning | failed | blocked
    late_usage_status: passed | warning | failed | blocked
    correction_lineage_status: passed | warning | failed | blocked
  freeze_and_financial_output:
    settlement_freeze_status: passed | warning | failed | blocked
    invoice_trace_status: passed | warning | failed | blocked
    participant_share_status: passed | warning | failed | blocked | not-applicable
    currency_rounding_status: passed | warning | failed | blocked | not-applicable
  dispute_and_closeout:
    dispute_bundle_status: passed | warning | failed | blocked
    disputed_amount_status: passed | warning | failed | blocked
    closeout_export_status: passed | warning | failed | blocked
    suspension_closeout_status: passed | warning | failed | blocked | not-applicable
  governance:
    approval_status: passed | warning | failed | blocked
    manual_override_status: passed | warning | failed | blocked | not-applicable
    release_history_status: passed | warning | failed | blocked
    learning_loop_status: passed | warning | failed | blocked
  source_safety:
    redaction_status: passed | warning | failed | blocked
    party_scope_status: passed | warning | failed | blocked
  unresolved_gaps:
    - gap
```

## Stop Conditions

Agent must stop and request owner/review if:

- closure would proceed while usage, invoice, credit/refund, dispute or
  participant-share state is unknown;
- late usage, correction, reversal, manual override or disputed amount has no
  governed policy;
- provider-local Stage 4 readiness depends on cross-participant settlement;
- cross-participant Stage 5 settlement lacks participant-scoped views or dispute
  hold/release behavior;
- closure evidence includes raw source snippets, private paths, internal
  endpoints, credentials, tenant data, copied documentation or raw commit text;
- an AI agent is asked to close, reopen, credit, refund, settle or release
  disputed money without approval evidence.

## Non-Goals

- Не выбирать payment processor, accounting package, tax engine, banking rail or
  settlement protocol.
- Не утверждать, что analyzed source already implements downstream settlement.
- Не обещать universal tax/legal automation.
- Не переносить старую implementation technology.
- Не использовать billing/settlement как customer retention trap.
