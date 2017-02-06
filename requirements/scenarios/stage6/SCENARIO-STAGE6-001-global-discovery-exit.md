# SCENARIO-STAGE6-001 - Global Discovery And Exit

```yaml
id: SCENARIO-STAGE6-001
stage: STAGE-006
primary_role: buyer
secondary_roles:
  - provider
  - ISV
  - support owner
  - governance owner
  - AI agent
intent:
  user_goal: Use global discovery to choose a service and retain a visible exit path.
  why_it_matters: Global convenience must not become a new central lock-in.
  anti_lock_in_relevance: jurisdiction
preconditions:
  - global discovery index has offers from multiple participants
  - policy-profile-a is active
  - trust-profile-a has freshness state
surfaces:
  - UI
  - API
  - Agent API
  - marketplace
  - governance report
product_flow:
  - buyer searches globally and sees ranking explanation
  - policy overlay marks allowed, warning or blocked offers
  - trust downgrade changes visibility without stopping unrelated local services
  - buyer reviews provider chain, support owner, settlement and portability
  - exit plan shows export, residual-data closure and compatible targets
expected_state_vocabulary:
  - globally-visible
  - policy-warning
  - blocked
  - stale
  - degraded
  - exit-ready
evidence:
  requirement_refs:
    - CR-STAGE6-001..032
    - CR-END2END-001..032
    - CR-POLICY-001..020
  conformance_refs:
    - stage6-global-ready
  scenario_objects:
    - user-buyer-a
    - policy-profile-a
    - trust-profile-a
    - migration-target-a
stop_condition_cases:
  - case: policy-denied
    expected_result: blocked
  - case: stale-trust
    expected_result: warning
  - case: unsupported-portability
    expected_result: warning
  - case: missing-support-owner
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: governance owner
  stop_if_unknown: true
```
