# SCENARIO-STAGE4-004 - Billing Runtime Ingestion Evidence

```yaml
id: SCENARIO-STAGE4-004
stage: STAGE-004
primary_role: provider
secondary_roles:
  - buyer
  - support
  - billing agent
  - AI agent
intent:
  user_goal: Accept billable usage only when receipt, async state, idempotency, access freshness and dispute evidence are clear.
  why_it_matters: Stage 4 public provider billing must be trusted before federation settlement exists.
  anti_lock_in_relevance: commercial exit and evidence portability
preconditions:
  - provider-public-a offers service-portable-a
  - offer-a declares usage-resource-a
  - entitlement-a is active for order-a
surfaces:
  - API
  - UI
  - Agent API
  - conformance report
product_flow:
  - service submits usage for order-a and usage-resource-a
  - usage gateway returns support-safe receipt with event identity and async status
  - billing agent verifies access freshness and request/event idempotency
  - provider sees queue/backpressure/readiness state before claiming billing readiness
  - support opens a dispute using receipt, decision ledger and invoice evidence
expected_state_vocabulary:
  - received
  - validated
  - accepted
  - enqueued
  - published
  - rejected
  - quarantined
  - corrected
  - disputed
  - settled
evidence:
  requirement_refs:
    - CR-BILLRUN-001..032
    - CR-BILL-001..036
    - CR-FED-019..036
    - CR-STAGE4-001..026
  conformance_refs:
    - stage4-public-provider-ready
  template_refs:
    - ../../templates/billing-runtime-evidence-template.md
stop_condition_cases:
  - case: success-response-without-durable-or-volatile-contract
    expected_result: blocked
  - case: reused-idempotency-key-with-different-payload
    expected_result: blocked
  - case: partial-batch-drop-after-success
    expected_result: blocked
  - case: queue-saturated-without-retry-guidance
    expected_result: blocked
  - case: generated-docs-contain-unsafe-runtime-example
    expected_result: blocked
source_safety:
  sensitivity_class: synthetic
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: billing owner
  stop_if_unknown: true
```
