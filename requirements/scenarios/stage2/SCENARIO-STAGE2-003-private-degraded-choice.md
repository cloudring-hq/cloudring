# SCENARIO-STAGE2-003 - Private Degraded Capability Choice

```yaml
id: SCENARIO-STAGE2-003
stage: STAGE-002
primary_role: admin
secondary_roles:
  - user
  - support
  - AI agent
intent:
  user_goal: Place a stateful workload only after understanding degraded local capability and recovery options.
  why_it_matters: Private presence must preserve autonomy without pretending that stale or degraded infrastructure is healthy.
  anti_lock_in_relevance: local-autonomy
preconditions:
  - presence-private-a is installed
  - service-stateful-a requests storage and backup capability
  - one capability profile has stale evidence
surfaces:
  - UI
  - API
  - CLI
  - Agent API
product_flow:
  - admin opens workload placement summary
  - product marks local capability as degraded and explains impact
  - user sees available local fallback and not-applicable federation options
  - agent can prepare evidence refresh but cannot override policy
expected_state_vocabulary:
  - ready
  - stale
  - degraded
  - warning
  - blocked
evidence:
  requirement_refs:
    - CR-DESIGNQ-004
    - CR-DESIGNQ-010..018
    - CR-STAGE2-001..026
    - CR-OPS-040..046
  conformance_refs:
    - stage2-private-presence-ready
stop_condition_cases:
  - case: stale-evidence
    expected_result: warning
  - case: missing-support-owner
    expected_result: blocked
  - case: unapproved-agent-action
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: admin
  stop_if_unknown: true
```
