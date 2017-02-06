# SCENARIO-STAGE4-003 - Provider Economics Transparency

```yaml
id: SCENARIO-STAGE4-003
stage: STAGE-004
primary_role: provider
secondary_roles:
  - buyer
  - billing agent
  - support
intent:
  user_goal: Publish and sell an offer only when price, entitlement, credit and support obligations are understandable.
  why_it_matters: A public provider presence must be commercially operable without opaque billing or dispute traps.
  anti_lock_in_relevance: economics
preconditions:
  - provider-public-a owns presence-provider-a
  - offer-public-a is certification-ready
  - order-a is not submitted yet
surfaces:
  - provider portal
  - buyer checkout
  - API
  - Agent API
product_flow:
  - provider reviews plan, settlement share, support duty and credit rules
  - buyer sees price estimate, SLA credit path, support owner and cancellation/export effect
  - billing agent validates usage and duplicate-charge guardrails
  - support case can bind order, entitlement and evidence without manual reconstruction
expected_state_vocabulary:
  - draft
  - public-ready
  - order-pending
  - active
  - disputed
  - credited
evidence:
  requirement_refs:
    - CR-DESIGNQ-004
    - CR-DESIGNQ-007..008
    - CR-DESIGNQ-012
    - CR-DESIGNQ-017..018
    - CR-MKT-020..024
    - CR-BILL-001..030
    - CR-STAGE4-001..026
  conformance_refs:
    - stage4-public-provider-ready
stop_condition_cases:
  - case: duplicate-billing-risk
    expected_result: blocked
  - case: missing-credit-path
    expected_result: blocked
  - case: missing-support-owner
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: provider
  stop_if_unknown: true
```
