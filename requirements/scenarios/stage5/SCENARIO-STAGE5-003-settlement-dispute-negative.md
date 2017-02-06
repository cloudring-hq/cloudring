# SCENARIO-STAGE5-003 - Settlement Dispute Negative Path

```yaml
id: SCENARIO-STAGE5-003
stage: STAGE-005
primary_role: participant
secondary_roles:
  - buyer
  - provider
  - support
  - governance
  - AI agent
intent:
  user_goal: Resolve a cross-participant settlement dispute without blocking unrelated services.
  why_it_matters: Federation needs disagreement handling as a normal product flow.
  anti_lock_in_relevance: choice
preconditions:
  - provider-public-a and provider-public-b exchange settlement events
  - dispute-a references order-a and usage-resource-a
  - unrelated services exist for the same buyer
surfaces:
  - federation report
  - support UI
  - API
  - Agent API
product_flow:
  - participant opens dispute with signed usage and settlement evidence
  - buyer sees affected order, credit status and unaffected services
  - governance reviews policy and appeal scope
  - agent prepares evidence bundle and may not alter settlement without approval
expected_state_vocabulary:
  - active
  - disputed
  - under-review
  - credited
  - resolved
  - blocked
evidence:
  requirement_refs:
    - CR-DESIGNQ-007..008
    - CR-DESIGNQ-012
    - CR-DESIGNQ-017..018
    - CR-FEDGOV-019..021
    - CR-MKT-023..024
    - CR-STAGE5-001..022
  conformance_refs:
    - stage5-federation-ready
stop_condition_cases:
  - case: missing-signed-evidence
    expected_result: blocked
  - case: unrelated-service-blocked
    expected_result: blocked
  - case: unapproved-agent-action
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: governance owner
  stop_if_unknown: true
```
