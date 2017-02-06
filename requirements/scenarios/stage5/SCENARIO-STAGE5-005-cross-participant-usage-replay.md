# SCENARIO-STAGE5-005 - Cross-Participant Usage Replay

```yaml
id: SCENARIO-STAGE5-005
stage: STAGE-005
primary_role: participant
secondary_roles:
  - buyer
  - provider
  - support
  - governance
  - AI agent
intent:
  user_goal: Replay delayed or disputed usage across participants without duplicate charges or hidden settlement impact.
  why_it_matters: Federation needs settlement trust across independent owners, not only local billing acceptance.
  anti_lock_in_relevance: cross-provider commercial portability
preconditions:
  - provider-public-a and provider-public-b exchange scoped settlement metadata
  - settlement-a references order-a, entitlement-a and usage-resource-a
  - dispute-a can be opened without blocking unrelated services
surfaces:
  - Federation API
  - provider portal
  - buyer billing view
  - governance report
  - Agent API
product_flow:
  - participant detects delayed usage with known receipt and decision ledger state
  - agent prepares replay plan with idempotency, access freshness and participant share impact
  - governance verifies generated docs/config and release evidence before settlement freeze
  - provider replays or voids quarantined usage with approval where required
  - buyer sees corrected settlement/invoice/dispute state without duplicate charge
expected_state_vocabulary:
  - delayed
  - stale
  - replay-planned
  - replayed
  - duplicate
  - corrected
  - voided
  - disputed
  - settlement-frozen
evidence:
  requirement_refs:
    - CR-BILLRUN-001..032
    - CR-BILL-001..036
    - CR-FEDNET-001..030
    - CR-STAGE5-001..026
  conformance_refs:
    - stage5-federation-ready
  template_refs:
    - ../../templates/billing-runtime-evidence-template.md
stop_condition_cases:
  - case: settlement-freeze-without-usage-evidence-bundle
    expected_result: blocked
  - case: duplicate-replay-would-double-settle
    expected_result: blocked
  - case: participant-share-not-traceable-to-order-entitlement
    expected_result: blocked
  - case: dirty-release-state-used-as-settlement-proof
    expected_result: blocked
source_safety:
  sensitivity_class: synthetic
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: federation billing owner
  stop_if_unknown: true
```
