# SCENARIO-STAGE4-001 - Public Provider Order And Support

```yaml
id: SCENARIO-STAGE4-001
stage: STAGE-004
primary_role: provider
secondary_roles:
  - user
  - support owner
  - billing agent
  - AI agent
intent:
  user_goal: Provider publishes an offer, tenant orders it, usage and support evidence remain clear.
  why_it_matters: A public provider kit must sell and operate responsibly before federation.
  anti_lock_in_relevance: choice
preconditions:
  - provider-public-a has provider-local readiness
  - offer-public-a has certification and support owner
  - usage-resource-a has validation contract
surfaces:
  - UI
  - API
  - CLI
  - Agent API
  - support report
product_flow:
  - provider completes onboarding evidence
  - tenant reviews price, SLA, support, trust and exit limits
  - tenant orders offer-public-a and receives service instance
  - usage event is accepted or rejected with decision ledger
  - support-case-a links provider, support owner, incident evidence and credit path
expected_state_vocabulary:
  - candidate
  - public-ready
  - active
  - disputed
  - suspended
evidence:
  requirement_refs:
    - CR-STAGE4-001..026
    - CR-BILL-001..036
    - CR-OBSOPS-001..036
  conformance_refs:
    - stage4-public-provider-ready
  scenario_objects:
    - provider-public-a
    - offer-public-a
    - order-a
    - invoice-a
    - support-case-a
stop_condition_cases:
  - case: duplicate-billing-risk
    expected_result: blocked
  - case: missing-support-owner
    expected_result: blocked
  - case: unsafe-evidence
    expected_result: blocked
source_safety:
  sensitivity_class: operational
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: provider owner
  stop_if_unknown: true
```
