# SCENARIO-STAGE2-002 - Private User Workload Policy

```yaml
id: SCENARIO-STAGE2-002
stage: STAGE-002
primary_role: user
secondary_roles:
  - admin
  - governance owner
  - AI agent
intent:
  user_goal: Create a basic private workload only when policy allows it.
  why_it_matters: Private self-service must be useful without bypassing ownership and policy.
  anti_lock_in_relevance: local-autonomy
preconditions:
  - presence-private-a is healthy
  - policy-profile-a is active
surfaces:
  - UI
  - API
  - CLI
  - Agent API
product_flow:
  - user requests workload
  - policy evaluates owner, quota, location and data class
  - allowed request provisions workload with audit
  - denied request explains reason and next action
expected_state_vocabulary:
  - allowed
  - denied
  - warning
  - manual_review_required
evidence:
  requirement_refs:
    - CR-STAGE2-003..006
    - CR-POLICY-001..020
  conformance_refs:
    - stage2-private-presence-ready
stop_condition_cases:
  - case: policy-denied
    expected_result: blocked
  - case: unapproved-agent-action
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: governance owner
  stop_if_unknown: true
```
