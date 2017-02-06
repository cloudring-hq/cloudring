# SCENARIO-STAGE6-002 - Policy Overlay Governance

```yaml
id: SCENARIO-STAGE6-002
stage: STAGE-006
primary_role: admin
secondary_roles:
  - governance owner
  - provider
  - AI agent
intent:
  user_goal: Apply a policy overlay without forking the global standard.
  why_it_matters: Global network must handle jurisdictions and enterprises without central lock-in.
  anti_lock_in_relevance: jurisdiction
preconditions:
  - policy-profile-a exists
  - global discovery index has multiple offers
surfaces:
  - UI
  - API
  - Agent API
  - governance report
product_flow:
  - admin proposes local policy overlay
  - governance owner reviews conflict with global baseline
  - offer visibility changes to allowed, warning or blocked
  - agent records explanation and appeal path
expected_state_vocabulary:
  - allowed
  - policy-warning
  - blocked
  - appealed
  - superseded
evidence:
  requirement_refs:
    - CR-STAGE6-009
    - CR-STAGE6-018..019
    - CR-END2END-026
  conformance_refs:
    - stage6-global-ready
stop_condition_cases:
  - case: policy-denied
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
