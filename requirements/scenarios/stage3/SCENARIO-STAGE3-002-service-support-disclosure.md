# SCENARIO-STAGE3-002 - Service Support Disclosure

```yaml
id: SCENARIO-STAGE3-002
stage: STAGE-003
primary_role: support
secondary_roles:
  - governance owner
  - admin
  - ISV
intent:
  user_goal: Verify that private store service card discloses support, trust and exit limits before install.
  why_it_matters: App-store simplicity must not hide operational responsibility.
  anti_lock_in_relevance: choice
preconditions:
  - service-portable-a is store candidate
  - support-owner-a is declared
surfaces:
  - UI
  - API
  - support report
product_flow:
  - admin reviews service card
  - support owner and escalation role are visible
  - trust and portability limits are visible before install
  - governance blocks install if owner or evidence is missing
expected_state_vocabulary:
  - candidate
  - install-ready
  - warning
  - blocked
evidence:
  requirement_refs:
    - CR-STAGE3-006..020
    - CR-MKT-001..040
  conformance_refs:
    - stage3-private-store-ready
stop_condition_cases:
  - case: missing-support-owner
    expected_result: blocked
  - case: unsupported-portability
    expected_result: warning
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: support owner
  stop_if_unknown: true
```
