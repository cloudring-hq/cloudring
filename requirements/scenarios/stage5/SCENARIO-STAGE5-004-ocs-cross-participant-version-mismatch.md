# SCENARIO-STAGE5-004 - OCS Cross-Participant Version Mismatch

```yaml
id: SCENARIO-STAGE5-004
stage: STAGE-005
primary_role: participant
secondary_roles:
  - provider
  - buyer
  - support
  - AI agent
intent:
  user_goal: Handle a cross-participant catalog sync where one participant advertises an older OCS model version.
  why_it_matters: Federation must remain interoperable while standards evolve.
  anti_lock_in_relevance: technology-refresh
preconditions:
  - provider-public-a publishes offer-public-a with current model evidence
  - provider-public-b publishes offer-public-b with older model evidence
surfaces:
  - federation sync report
  - catalog UI
  - API
  - Agent API
product_flow:
  - federation sync compares model versions and compatibility class
  - buyer sees available, warning or blocked status before order
  - support owner receives evidence for mismatch and migration path
  - agent may prepare compatibility review but cannot mark incompatible offer as ready
expected_state_vocabulary:
  - compatible
  - warning
  - stale
  - blocked
  - migration-required
evidence:
  requirement_refs:
    - CR-OCSIM-006
    - CR-OCSIM-013..015
    - CR-OCSIM-023..031
    - CR-FEDGOV-008..010
    - CR-STAGE5-001..026
  conformance_refs:
    - stage5-federation-ready
stop_condition_cases:
  - case: missing-model-version
    expected_result: blocked
  - case: stale-compatibility-review
    expected_result: warning
  - case: incompatible-offer-marked-ready
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: participant
  stop_if_unknown: true
```
