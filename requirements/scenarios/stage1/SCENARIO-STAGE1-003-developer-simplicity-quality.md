# SCENARIO-STAGE1-003 - Developer Simplicity Quality

```yaml
id: SCENARIO-STAGE1-003
stage: STAGE-001
primary_role: developer
secondary_roles:
  - service owner
  - AI agent
intent:
  user_goal: Create and validate the first portable service without learning internal platform topology first.
  why_it_matters: Stage 1 must make service creation feel like a product workflow, not a source archaeology task.
  anti_lock_in_relevance: portability
preconditions:
  - developer-a has local CloudRING tools
  - service-portable-a is not created yet
surfaces:
  - UI
  - CLI
  - Agent API
  - docs
product_flow:
  - developer chooses create portable service by goal and service type
  - product shows template consequences, default reason and unsupported limits
  - agent creates a dry-run plan and names files, checks and rollback
  - developer runs validation and receives support-ready failure output if blocked
expected_state_vocabulary:
  - draft
  - dry-run
  - validated
  - warning
  - blocked
evidence:
  requirement_refs:
    - CR-DESIGNQ-001..005
    - CR-DESIGNQ-013..018
    - CR-UX-001..021
    - CR-STAGE1-001..025
  conformance_refs:
    - stage1-service-ready
stop_condition_cases:
  - case: hidden-internal-dependency
    expected_result: blocked
  - case: inconsistent-ui-cli-agent-state
    expected_result: blocked
  - case: unsupported-portability
    expected_result: warning
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: service owner
  stop_if_unknown: true
```
