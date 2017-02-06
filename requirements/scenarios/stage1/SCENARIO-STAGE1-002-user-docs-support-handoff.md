# SCENARIO-STAGE1-002 - User Docs And Support Handoff

```yaml
id: SCENARIO-STAGE1-002
stage: STAGE-001
primary_role: user
secondary_roles:
  - support owner
  - AI agent
intent:
  user_goal: Understand a local service failure and produce support-ready evidence.
  why_it_matters: Stage 1 must be supportable by one human and agents.
  anti_lock_in_relevance: technology-refresh
preconditions:
  - service-portable-a has docs and runbook
  - local validation produced structured result
surfaces:
  - UI
  - CLI
  - Agent API
  - docs
product_flow:
  - user opens docs and known limits
  - failed validation shows human message and machine code
  - agent collects redacted evidence bundle
  - support owner receives next-action summary
expected_state_vocabulary:
  - failed
  - warning
  - blocked
  - ready
evidence:
  requirement_refs:
    - CR-STAGE1-012..019
    - CR-UX-019..020
  conformance_refs:
    - stage1-service-ready
stop_condition_cases:
  - case: missing-support-owner
    expected_result: blocked
  - case: unsafe-evidence
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: support owner
  stop_if_unknown: true
```
