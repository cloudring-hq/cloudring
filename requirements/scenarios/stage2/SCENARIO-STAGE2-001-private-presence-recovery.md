# SCENARIO-STAGE2-001 - Private Presence Recovery

```yaml
id: SCENARIO-STAGE2-001
stage: STAGE-002
primary_role: admin
secondary_roles:
  - support owner
  - AI agent
intent:
  user_goal: Operate a private presence and prove stateful recovery readiness.
  why_it_matters: Private cloud value depends on local autonomy and recoverability.
  anti_lock_in_relevance: local-autonomy
preconditions:
  - presence-private-a is installed
  - service-stateful-a declares backup and restore requirements
  - agent has read-only or controlled-change scope
surfaces:
  - UI
  - API
  - CLI
  - Agent API
product_flow:
  - inspect private presence health and capability matrix
  - review topology and endpoint ownership for stateful capability
  - run restore/failover readiness evidence review
  - confirm source-safe operational evidence bundle
  - produce stage2-private-presence-ready report
expected_state_vocabulary:
  - ready
  - degraded
  - stale
  - blocked
  - manual_review_required
evidence:
  requirement_refs:
    - CR-STAGE2-001..026
    - CR-OPS-038..046
    - CR-OBSOPS-031..036
  conformance_refs:
    - stage2-private-presence-ready
  scenario_objects:
    - presence-private-a
    - service-stateful-a
    - evidence-bundle-a
stop_condition_cases:
  - case: stale-evidence
    expected_result: blocked
  - case: unsafe-evidence
    expected_result: blocked
  - case: unapproved-agent-action
    expected_result: blocked
  - case: unsupported-portability
    expected_result: warning
source_safety:
  sensitivity_class: operational
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: support owner
  stop_if_unknown: true
```
