# SCENARIO-STAGE7-001 - Source Signal Learning

```yaml
id: SCENARIO-STAGE7-001
stage: STAGE-007
primary_role: AI agent
secondary_roles:
  - governance owner
  - requirement owner
intent:
  user_goal: Turn a source or operational signal into safe requirements memory.
  why_it_matters: CloudRING must improve without leaking source context or weakening human ownership.
  anti_lock_in_relevance: technology-refresh
preconditions:
  - coverage-manifest-a exists or is created from template
  - source-safety gate is available
  - owner review is required for high-impact changes
surfaces:
  - Markdown
  - Agent API
  - conformance report
  - source coverage manifest
product_flow:
  - classify source signal by source class and coverage mode
  - extract product meaning as what/why/evidence without copying source
  - update requirement, ADR, runbook, template or no-change decision
  - record profile change if conformance changes
  - run validation summary and preserve non-claims
expected_state_vocabulary:
  - proposed
  - accepted
  - rejected
  - stale
  - blocked
  - complete
evidence:
  requirement_refs:
    - CR-STAGE7-001..039
    - CR-SRCOV-001..018
    - CR-SPECTPL-001..024
  conformance_refs:
    - stage7-self-evolving-ready
  scenario_objects:
    - coverage-manifest-a
    - evidence-bundle-a
stop_condition_cases:
  - case: unsafe-evidence
    expected_result: blocked
  - case: stale-evidence
    expected_result: warning
  - case: unapproved-agent-action
    expected_result: blocked
source_safety:
  sensitivity_class: source-derived
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: governance owner
  stop_if_unknown: true
```
