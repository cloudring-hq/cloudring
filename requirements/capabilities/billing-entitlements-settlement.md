# Capability Contract - Billing Entitlements And Settlement

## Назначение

Billing Entitlements And Settlement - экономический trust layer CloudRING. Он
связывает orders, usage, subscriptions, entitlements, invoices, credits, refunds,
disputes и participant shares так, чтобы commercial state был объяснимым,
проверяемым, scoped by party и не превращался в механизм удержания пользователя.

Contract описывает product promises and evidence. Он не выбирает payment
processor, accounting system, tax engine, currency provider или settlement rail.

## Продуктовая Граница

- Billing отвечает за usage, charges, invoices, credits, refunds, disputes,
  exports and commercial evidence.
- Entitlements отвечают за право use/update/support/features и за degraded/grace
  behavior, especially for private/offline presence.
- Settlement отвечает за распределение value между provider, actual provider,
  ISV, reseller, federation participant и network roles, но появляется поэтапно.
- Settlement closure отвечает за доказуемое закрытие периода: input manifest,
  reconciliation, freeze, corrections, disputes, participant shares and closeout
  export.
- Commercial state должен быть visible before commitment, auditable after action
  and exportable on exit.
- Billing не должен уничтожать data, блокировать exit или скрывать provider chain.

## Staged Topology

- Local/private entitlement: installed service remains understandable and locally
  controllable during disconnect with cached entitlement, grace/degraded behavior
  and support/update limitations.
- Provider-local billing: Stage 4 provider can issue coherent invoice, usage
  evidence, provider-local closure, credits/refunds and disputes for its own
  offers without federation settlement.
- Federation settlement: Stage 5 adds cross-participant shares, duplicate
  prevention, closure reconciliation, dispute hold/release evidence and
  participant-scoped views.
- Global settlement/dispute: Stage 6 adds multi-jurisdiction freshness,
  corrections, global search/order consequences and explainable commercial
  routing.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-BILL-001 | Commercial service должен объявлять measurable usage resources before billing. | Нельзя честно выставить счет за неописанную product value. | Offer lists usage resources, units, pricing basis, included limits, overage behavior and non-commercial exceptions. |
| CR-BILL-002 | Usage event должен быть product-scoped, period-scoped и idempotent. | Duplicate или ambiguous usage разрушает trust. | Usage event has service/product, offer/order, resource, instance, period, unit, amount, idempotency key, version and source. |
| CR-BILL-003 | Usage gateway должен accept, reject, quarantine, delay, dispute or correct events with reason. | Bad usage не должен молча превращаться в invoice line. | Event state shows accepted, rejected, duplicate, delayed, disputed, corrected or quarantined with reason and owner. |
| CR-BILL-004 | Usage должен trace to order, entitlement and invoice/credit/refund. | Customer disputes требуют evidence chain. | Invoice/credit line links usage records, order/subscription, entitlement state, policy decision and correction history. |
| CR-BILL-005 | Billing preview должен быть visible before order, scale, migration or feature enablement. | User должен видеть cost consequence before commitment. | Plan shows estimated price, units, recurring/usage charges, credits, budget impact, policy outcome and approval need. |
| CR-BILL-006 | Entitlement должен описывать rights to use, update, support and features. | License/subscription - product promise, а не скрытый feature flag. | Entitlement shows active, grace, degraded, expired, suspended or revoked state with consequences and appeal/remediation. |
| CR-BILL-007 | Offline/private entitlement не должен быть kill switch for basic local operation. | Private cloud должен сохранять local control и avoid central lock-in. | Disconnected mode shows cached entitlement, freshness, grace/degraded behavior, allowed local actions and support/update limits. |
| CR-BILL-008 | Entitlement changes должны быть audited. | Commercial rights влияют на access, support, updates and customer trust. | Change record shows actor, delegated subject, reason, previous/new state, affected service, policy decision and appeal/remediation. |
| CR-BILL-009 | Invoice должен объяснять charges human-readable and agent-readable. | Human и AI-agent должны видеть одну billing reality. | Invoice includes service, offer/plan, resource, period, units, rates/credits, taxes/fees metadata, evidence links and export form. |
| CR-BILL-010 | Credits/refunds должны link to SLA, support, dispute or correction evidence. | Commercial correction должна быть traceable и не ручной магией. | Credit/refund record references incident, SLA decision, dispute, correction reason, affected usage and approval. |
| CR-BILL-011 | Dispute должен сохранять evidence bundle. | Independent participants, customers and providers will disagree. | Dispute includes order, usage, policy, support timeline, entitlement state, settlement shares, corrections and decision history. |
| CR-BILL-012 | Settlement должен поддерживать provider, actual provider, ISV, reseller, federation participant and network roles. | Federation commerce multi-party by design. | Settlement record shows participants, shares, source commercial terms, scope, period, correction state and visibility rules. |
| CR-BILL-013 | Settlement должен prevent double charging and double settlement. | Multi-party usage легко дублируется на provider chain. | Duplicate detection, idempotency, correction evidence and dispute path are visible. |
| CR-BILL-014 | Settlement должен быть staged by product maturity. | Provider-local billing должен работать до federation/global settlement. | Stage 4 passes with provider-local invoice; cross-participant settlement is Stage 5+; global multi-jurisdiction settlement is Stage 6+. |
| CR-BILL-015 | Billing не должен блокировать customer exit. | Anti-lock-in включает commercial exit and evidence portability. | Customer can export invoices, usage history, entitlements, dispute/credit history, closure evidence and allowed data export status. |
| CR-BILL-016 | Suspension for non-payment/dispute должен быть scoped and explainable. | Commercial action не должен уничтожать data или unrelated services. | Suspension shows reason, scope, appeal, allowed export/recovery, unaffected services, support path and review trigger. |
| CR-BILL-017 | Billing/settlement/entitlement changes by agent требуют approval. | Money and access rights need strict guardrails. | Agent cannot alter invoice, settlement, credit, refund, entitlement or suspension without approval record and policy decision. |
| CR-BILL-018 | Currency/tax/regulatory metadata должны быть represented without promising universal tax automation. | Global commerce needs context, но universal tax/legal automation unrealistic. | Record carries jurisdiction/commercial metadata, manual-review status where needed and limitation statement. |
| CR-BILL-019 | Billing state должен быть visible to buyer, provider, actual provider, ISV and reseller with scoped views. | Каждая сторона требует trust без over-sharing. | Buyer sees charges/evidence; participants see relevant shares/evidence; sensitive details are scoped by role and policy. |
| CR-BILL-020 | Usage, entitlement and settlement freshness должны быть visible. | Delayed federation не должна выглядеть как final truth. | Records show fresh, delayed, stale, disputed, corrected, revoked or manual-review status with timestamp/source. |
| CR-BILL-021 | Billing должен support policy-based availability. | Some plans/offers cannot be sold, renewed or activated everywhere. | Offer availability considers commercial, jurisdiction, compliance, entitlement, provider-chain and budget policy. |
| CR-BILL-022 | Billing events должны быть part of audit and product knowledge graph. | Agents need context for support, disputes, migration and exit. | Billing event links order, policy, support, entitlement, service instance, usage and settlement context. |
| CR-BILL-023 | Billing capability должен publish conformance evidence. | Commerce must be certifiable before trust can scale. | Readiness report covers usage, invoice, credits/refunds, disputes, entitlements, suspension and settlement where applicable. |
| CR-BILL-024 | Commercial model changes должны follow continuous evolution loop. | Pricing and settlement changes can break promises and trust. | Change links signal, ADR if needed, affected users, migration/notice, validation, rollback/exception path and support script. |
| CR-BILL-025 | Usage gateway must maintain a decision ledger. | Billable events need evidence even when they are rejected, delayed, flushed or replayed. | Ledger records received, accepted, queued, broker-flushed, rejected, transform-rejected, quarantined, duplicate, delayed, shutdown-delayed, replayed, disputed and corrected events with reason, source, product/resource scope and timestamp. |
| CR-BILL-026 | Usage validation contract must be explicit. | Bad periods, units or amounts must not silently become charges. | Validation covers schema, units, period ordering, period overlap policy, amount boundaries, resource identity and version. |
| CR-BILL-027 | Billable usage idempotency must be mandatory. | Retries, queues and federation sync will duplicate events. | Event without payload-bound idempotency identity is rejected or quarantined before invoice impact; identity evidence is documented, credential-free and covered by duplicate/replay tests. |
| CR-BILL-028 | Usage ingestion must declare payload/rate limits and backpressure behavior. | Overload should be visible and bounded, not hidden data loss. | Gateway states size/rate limits, queue states, retry/dead-letter behavior, delay markers and operator/customer impact. |
| CR-BILL-029 | Authentication and token failures must be logged without credential material. | Billing investigation should not create a credential leak. | Failure evidence records outcome, actor/source class, scope and reason while redacting tokens, secrets and raw authorization headers. |
| CR-BILL-030 | Usage access state freshness must be visible. | Stale access cache can accept wrong billable events. | Gateway decision references active/stale/revoked/degraded sync state, source timestamp, last successful sync, source state and fail-open/fail-closed behavior. |
| CR-BILL-031 | Usage metadata must have size, shape and redaction rules. | Metadata helps disputes but can leak tenant data or overload ingestion. | Usage contract defines allowed metadata keys/classes, value classes, identity participation, max size, redaction boundary, retention and rejection/quarantine behavior. |
| CR-BILL-032 | Period overlap and correction policy must be explicit. | Period bugs create double charging and disputes. | Gateway validates period ordering, overlap behavior, correction version, replacement semantics and dispute trace. |
| CR-BILL-033 | Usage decision state taxonomy must be shared across API, queue and settlement. | Different pipeline layers must not disagree about event truth. | States include received, accepted, queued, broker-flushed, rejected, transform-rejected, duplicate, delayed, shutdown-delayed, quarantined, disputed, corrected, expired and replayed with stable reason codes. |
| CR-BILL-034 | Usage gateway must expose operator and customer impact of backpressure. | Overload affects invoices and trust. | Backpressure evidence shows queue status, delayed scope, retry guidance, freshness, affected offers/resources and customer/provider visibility. |
| CR-BILL-035 | Usage gateway conformance must include replay and duplicate tests. | Retries and federation sync are normal paths. | Test evidence covers duplicate submit, missing/stale idempotency, replay after queue recovery, stale access state, shutdown/backpressure delay, corrected event and disputed event. |
| CR-BILL-036 | Usage gateway must preserve source safety in diagnostics. | Billing debugging often touches sensitive context. | Diagnostic bundle redacts credentials, tenant data, internal topology and source-derived private context while preserving dispute evidence. |

## Party Views

- Buyer видит charges, usage evidence, entitlement, dispute/credit status,
  export/closure options and suspension consequences.
- Provider видит provider-local usage, invoices, disputes, credits and service
  health/commercial evidence relevant to its offers.
- Actual provider/federation participant видит scoped settlement share and
  operational evidence, not full customer commercial data by default.
- ISV/reseller видит relevant share, product usage evidence and dispute impact
  without extra customer data access.
- Agent видит only scoped billing context required for the approved task.

## Evidence

- Usage resource declaration for offer.
- Usage event sample with idempotency and product/order/resource scope.
- Usage gateway decision: accepted/rejected/quarantined/delayed/disputed/corrected.
- Usage gateway decision ledger and validation report.
- Usage payload/rate/backpressure/freshness evidence.
- Usage metadata/redaction and period-overlap validation evidence.
- Usage replay/duplicate/missing-identity/correction/dispute conformance tests.
- Usage queue flush, shutdown delay, replay/quarantine and stale-access fixtures.
- Usage diagnostic source-safety bundle.
- Billing preview before order/scale/migration.
- Invoice/credit/refund/dispute bundle.
- Settlement closure run, input manifest, reconciliation report and freeze
  decision.
- Participant share, disputed amount hold/release and closeout export evidence
  where Stage 5+ applies.
- Entitlement state record including offline/grace/degraded behavior.
- Provider-local invoice readiness evidence.
- Cross-participant settlement share record where Stage 5+ applies.
- Suspension/appeal/export/recovery evidence.
- Customer export/closure evidence.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/manual review, если:

- usage cannot trace to order, entitlement, invoice/credit/refund and policy
  context;
- commercial action changes invoice, credit, refund, settlement, entitlement or
  suspension without approval;
- suspension lacks scope, appeal, export/recovery path or unaffected service list;
- billing/settlement record would expose data beyond party scope;
- Stage 3/4 plan accidentally requires cross-participant settlement;
- tax/regulatory/jurisdiction metadata requires manual review;
- billing state would block customer exit or data export without explicit policy
  and appeal path;
- duplicate usage/settlement cannot be resolved with evidence;
- period closeout lacks closure run, reconciliation, dispute hold/release,
  participant-share lineage or closeout export evidence;
- disputed or late usage would settle without approval/manual review;
- billable usage lacks idempotency identity;
- usage metadata is unbounded or can carry sensitive data without redaction;
- period overlap/correction behavior is ambiguous;
- invalid, duplicate, over-limit or delayed usage would be silently accepted or
  dropped;
- queue/backpressure state hides customer/provider impact;
- authentication failure evidence would expose token or credential material.

## Non-Goals

- Не реализовывать payment processor внутри capability contract.
- Не давать tax/legal advice для каждой jurisdiction.
- Не обещать universal settlement across all currencies, regimes and countries.
- Не использовать billing as customer retention trap.
- Не делать offline entitlement центральным kill switch.
- Не включать federation/global settlement в Stage 3/4 readiness.
