# SCENARIO-STAGE1-001 - First Portable Service

```yaml
id: SCENARIO-STAGE1-001
stage: STAGE-001
primary_role: developer
secondary_roles:
  - AI agent
intent:
  user_goal: Create, run, observe, document and validate a portable service locally.
  why_it_matters: Stage 1 must be a finished Solo Developer Cloud product.
  anti_lock_in_relevance: technology-refresh
preconditions:
  - service template is available
  - local runtime profile is declared
  - no public provider dependency is required
surfaces:
  - UI
  - API
  - CLI
  - Agent API
product_flow:
  - create service-portable-a from template
  - validate OCS manifest and field matrix
  - start local dependencies through declared contract
  - inspect health, docs, logs, metrics and traces
  - run validate task and produce conformance report
expected_state_vocabulary:
  - draft
  - ready
  - degraded
  - blocked
  - unsupported
evidence:
  requirement_refs:
    - CR-STAGE1-001..025
    - CR-OCSCONTRACT-001..046
    - CR-SERVICEFACTORY-001..050
  conformance_refs:
    - stage1-service-ready
  scenario_objects:
    - service-portable-a
    - presence-local-a
stop_condition_cases:
  - case: unsafe-evidence
    expected_result: blocked
  - case: unapproved-agent-action
    expected_result: blocked
  - case: missing-owner
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: service owner
  stop_if_unknown: true
```
