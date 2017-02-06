# SCENARIO-STAGE5-001 - Federated Operation And Dispute

```yaml
id: SCENARIO-STAGE5-001
stage: STAGE-005
primary_role: buyer
secondary_roles:
  - provider
  - participant
  - support owner
  - governance owner
  - AI agent
intent:
  user_goal: Compare offers across participants, run a policy-safe cross-provider operation and handle a dispute.
  why_it_matters: Federation must create real choice without central ownership or hidden responsibility.
  anti_lock_in_relevance: portability
preconditions:
  - provider-public-a and presence-provider-b are independent participants
  - service-stateful-a has portability profile
  - settlement-a has evidence contract
surfaces:
  - UI
  - API
  - Agent API
  - support report
  - federation report
product_flow:
  - buyer compares offers with provider chain, trust and jurisdiction attributes
  - cross-provider operation plan checks policy, data scope and compatibility
  - agent proposes action but requires approval for data movement
  - operation produces validation or explicit blocked result
  - dispute-a links usage, settlement, support and correction evidence
expected_state_vocabulary:
  - fresh
  - stale
  - allowed
  - manual_review_required
  - disputed
  - blocked
evidence:
  requirement_refs:
    - CR-STAGE5-001..026
    - CR-FEDNET-001..030
    - CR-PORTX-001..033
  conformance_refs:
    - stage5-federation-ready
  scenario_objects:
    - provider-public-a
    - presence-provider-b
    - migration-target-a
    - settlement-a
    - dispute-a
stop_condition_cases:
  - case: policy-denied
    expected_result: blocked
  - case: stale-trust
    expected_result: manual-review
  - case: unapproved-agent-action
    expected_result: blocked
  - case: unsupported-portability
    expected_result: blocked
source_safety:
  sensitivity_class: operational
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: federation governance owner
  stop_if_unknown: true
```
