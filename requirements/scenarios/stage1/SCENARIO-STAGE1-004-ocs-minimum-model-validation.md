# SCENARIO-STAGE1-004 - OCS Minimum Model Validation

```yaml
id: SCENARIO-STAGE1-004
stage: STAGE-001
primary_role: developer
secondary_roles:
  - service owner
  - AI agent
intent:
  user_goal: Validate the smallest useful service manifest against the OCS information model.
  why_it_matters: Stage 1 needs a finished local product without waiting for every future cloud feature.
  anti_lock_in_relevance: portability
preconditions:
  - ocs-model-a defines service_manifest artifact kind
  - service-portable-a has a draft manifest
surfaces:
  - CLI
  - API
  - Agent API
  - conformance report
product_flow:
  - developer runs model validation before local service launch
  - validator checks identity, owner, profiles, lifecycle, observability, docs and evidence
  - agent receives stable validation codes and next actions
  - conformance report records model version and unresolved future-stage gaps
expected_state_vocabulary:
  - draft
  - validated
  - warning
  - blocked
evidence:
  requirement_refs:
    - CR-OCSIM-001..010
    - CR-OCSIM-016..018
    - CR-OCSCONTRACT-001..046
    - CR-STAGE1-001..025
  conformance_refs:
    - stage1-service-ready
stop_condition_cases:
  - case: missing-service-identity
    expected_result: blocked
  - case: unknown-field-without-extension
    expected_result: blocked
  - case: future-stage-field-missing
    expected_result: warning
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: service owner
  stop_if_unknown: true
```
