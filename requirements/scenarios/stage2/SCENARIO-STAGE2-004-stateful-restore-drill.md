# SCENARIO-STAGE2-004 - Stateful Restore Drill

```yaml
id: SCENARIO-STAGE2-004
stage: STAGE-002
primary_role: admin
secondary_roles:
  - support owner
  - AI agent
intent:
  user_goal: Prove that a private presence can restore a stateful service from a declared backup or archive.
  why_it_matters: Private cloud autonomy is false if local data cannot be recovered.
  anti_lock_in_relevance: local recovery and exit readiness
preconditions:
  - presence-private-a is installed
  - service-stateful-a declares stateful-readiness requirements
  - backup evidence exists but must not be treated as restore proof
surfaces:
  - UI
  - API
  - CLI
  - Agent API
  - conformance report
product_flow:
  - inspect stateful topology, node classes and failure domains
  - select backup or archive evidence with freshness and owner
  - review restore target and expected RPO
  - execute or attach controlled restore drill evidence
  - validate integrity and service smoke test
  - record blockers, warnings, non-claims and source-safety decision
expected_state_vocabulary:
  - ready
  - warning
  - stale
  - blocked
  - degraded
  - manual_review_required
evidence:
  requirement_refs:
    - CR-STATEFULRUN-001..032
    - CR-OPS-038..046
    - CR-OBSOPS-031..036
    - CR-STAGE2-001..026
  conformance_refs:
    - stage2-private-presence-ready
  template_refs:
    - ../../templates/stateful-readiness-evidence-template.md
stop_condition_cases:
  - case: backup-exists-without-restore-test
    expected_result: blocked
  - case: pitr-claimed-without-archive-continuity
    expected_result: blocked
  - case: restore-target-unknown
    expected_result: blocked
  - case: raw-operational-log-required-for-agent-review
    expected_result: blocked
  - case: stale-restore-evidence
    expected_result: warning
source_safety:
  sensitivity_class: synthetic
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: stateful operations owner
  stop_if_unknown: true
```
