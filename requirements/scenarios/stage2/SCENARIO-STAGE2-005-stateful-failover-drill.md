# SCENARIO-STAGE2-005 - Stateful Failover Drill

```yaml
id: SCENARIO-STAGE2-005
stage: STAGE-002
primary_role: admin
secondary_roles:
  - support owner
  - AI agent
intent:
  user_goal: Prove that a stateful private presence can fail over without hidden endpoint or split-brain risk.
  why_it_matters: HA is a product promise only when clients and writes move safely.
  anti_lock_in_relevance: local autonomy and provider independence
preconditions:
  - presence-private-a has multi-node or declared HA stateful capability
  - service-stateful-a has topology and endpoint ownership evidence
  - agent has read-only review scope unless owner approves controlled drill action
surfaces:
  - UI
  - API
  - CLI
  - Agent API
  - conformance report
product_flow:
  - review node classes, quorum or consistency model and failure domains
  - verify write/read endpoint owner and service-discovery behavior
  - inspect split-brain prevention and rollback or compensation path
  - attach failover drill evidence with observed RTO and client impact
  - classify degraded, warning or blocked state for unresolved findings
expected_state_vocabulary:
  - ready
  - degraded
  - stale
  - blocked
  - manual_review_required
evidence:
  requirement_refs:
    - CR-STATEFULRUN-001..032
    - CR-INFPROFILE-031
    - CR-PORTX-014
    - CR-STAGE2-001..026
  conformance_refs:
    - stage2-private-presence-ready
  template_refs:
    - ../../templates/stateful-readiness-evidence-template.md
stop_condition_cases:
  - case: endpoint-owner-unknown
    expected_result: blocked
  - case: split-brain-prevention-unproven
    expected_result: blocked
  - case: observed-rto-missing-for-ha-claim
    expected_result: warning
  - case: agent-requests-unapproved-failover-mutation
    expected_result: blocked
  - case: degraded-readonly-service-visible-to-user
    expected_result: degraded
source_safety:
  sensitivity_class: synthetic
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: stateful operations owner
  stop_if_unknown: true
```
