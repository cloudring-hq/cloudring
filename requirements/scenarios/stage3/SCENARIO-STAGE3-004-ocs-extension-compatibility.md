# SCENARIO-STAGE3-004 - OCS Extension Compatibility

```yaml
id: SCENARIO-STAGE3-004
stage: STAGE-003
primary_role: ISV
secondary_roles:
  - admin
  - governance
  - AI agent
intent:
  user_goal: Publish a private-store service with a namespaced extension without weakening OCS baseline compatibility.
  why_it_matters: App-store extensibility should encourage innovation without creating hidden forks.
  anti_lock_in_relevance: choice
preconditions:
  - service-portable-a passes baseline service_manifest validation
  - ocs-extension-a is declared as additive
surfaces:
  - private store review
  - API
  - Agent API
product_flow:
  - ISV submits manifest with extension namespace
  - store validates mandatory baseline before extension checks
  - admin sees whether extension affects portability, support or policy
  - agent blocks publication if extension hides unsupported behavior
expected_state_vocabulary:
  - candidate
  - extension-valid
  - warning
  - blocked
  - private-ready
evidence:
  requirement_refs:
    - CR-OCSIM-010..015
    - CR-OCSIM-022
    - CR-OCSIM-026..036
    - CR-MKT-001..019
    - CR-STAGE3-001..026
  conformance_refs:
    - stage3-private-store-ready
stop_condition_cases:
  - case: unknown-field-without-extension
    expected_result: blocked
  - case: extension-weakens-secret-boundary
    expected_result: blocked
  - case: extension-adds-visible-limitation
    expected_result: warning
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: governance owner
  stop_if_unknown: true
```
