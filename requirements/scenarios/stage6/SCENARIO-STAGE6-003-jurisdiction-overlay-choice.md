# SCENARIO-STAGE6-003 - Jurisdiction Overlay Choice

```yaml
id: SCENARIO-STAGE6-003
stage: STAGE-006
primary_role: buyer
secondary_roles:
  - governance
  - provider
  - AI agent
intent:
  user_goal: Compare global offers by jurisdiction, policy, provider trust, cost, support and exit.
  why_it_matters: Global discovery must reduce provider and jurisdiction lock-in without becoming a hidden central owner.
  anti_lock_in_relevance: jurisdiction
preconditions:
  - offer-public-a, offer-public-b and offer-private-a are indexed
  - policy-profile-a defines data-location and approval rules
  - provider-public-a and provider-public-b have current trust metadata
surfaces:
  - global discovery UI
  - API
  - CLI
  - Agent API
product_flow:
  - buyer searches by task and jurisdiction constraint
  - global discovery shows recommended offer and alternatives
  - policy overlay marks one offer as manual-review and one as local fallback
  - agent can prepare approval request but cannot submit order
expected_state_vocabulary:
  - available
  - recommended
  - warning
  - manual-review
  - blocked
evidence:
  requirement_refs:
    - CR-DESIGNQ-001..024
    - CR-FEDGOV-011..021
    - CR-MKT-001..004
    - CR-MKT-025..028
    - CR-STAGE6-001..032
  conformance_refs:
    - stage6-global-ready
stop_condition_cases:
  - case: policy-denied
    expected_result: blocked
  - case: stale-trust
    expected_result: warning
  - case: hidden-jurisdiction-impact
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: governance owner
  stop_if_unknown: true
```
