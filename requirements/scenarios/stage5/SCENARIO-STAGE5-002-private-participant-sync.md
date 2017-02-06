# SCENARIO-STAGE5-002 - Private Participant Sync

```yaml
id: SCENARIO-STAGE5-002
stage: STAGE-005
primary_role: admin
secondary_roles:
  - ISV
  - provider
  - AI agent
intent:
  user_goal: Join a private participant to federation with scoped catalog sync.
  why_it_matters: Federation should include private participants without forcing full disclosure.
  anti_lock_in_relevance: local-autonomy
preconditions:
  - participant-private-a has local ownership
  - provider-public-a is an independent participant
  - service-portable-a has federation-ready metadata candidate
surfaces:
  - UI
  - API
  - Agent API
  - federation report
product_flow:
  - admin selects metadata classes to share
  - policy checks what may sync
  - catalog and trust metadata sync with freshness state
  - disconnected mode marks stale data without stopping local services
expected_state_vocabulary:
  - active
  - delayed
  - stale
  - blocked
  - local-only
evidence:
  requirement_refs:
    - CR-STAGE5-001..026
    - CR-FEDNET-001..030
  conformance_refs:
    - stage5-federation-ready
stop_condition_cases:
  - case: policy-denied
    expected_result: blocked
  - case: stale-trust
    expected_result: warning
source_safety:
  sensitivity_class: operational
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: admin-private-a
  stop_if_unknown: true
```
