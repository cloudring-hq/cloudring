# SCENARIO-STAGE0-002 - Source Intake Review

```yaml
id: SCENARIO-STAGE0-002
stage: STAGE-000
primary_role: developer
secondary_roles:
  - AI agent
  - governance owner
intent:
  user_goal: Register a new source signal and decide whether it changes requirements.
  why_it_matters: CloudRING memory must grow safely from new experience.
  anti_lock_in_relevance: technology-refresh
preconditions:
  - source coverage manifest template exists
  - review checklist exists
surfaces:
  - Markdown
  - Agent API
product_flow:
  - classify source as idea, docs, code, history, incident or operation
  - record coverage mode and non-claims
  - extract product signal as what/why/evidence
  - update requirement or record no-change decision
expected_state_vocabulary:
  - proposed
  - accepted
  - rejected
  - blocked
evidence:
  requirement_refs:
    - CR-SRCOV-001..018
    - CR-AGENT-010..011
  conformance_refs:
    - stage0-requirements-memory-ready
stop_condition_cases:
  - case: unsafe-evidence
    expected_result: blocked
  - case: stale-evidence
    expected_result: warning
source_safety:
  sensitivity_class: source-derived
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: governance owner
  stop_if_unknown: true
```
