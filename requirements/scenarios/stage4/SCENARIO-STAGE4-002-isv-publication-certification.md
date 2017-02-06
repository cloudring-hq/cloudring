# SCENARIO-STAGE4-002 - ISV Publication Certification

```yaml
id: SCENARIO-STAGE4-002
stage: STAGE-004
primary_role: ISV
secondary_roles:
  - provider
  - governance owner
  - certification agent
intent:
  user_goal: Publish a provider-local public offer only after certification evidence passes.
  why_it_matters: Public provider kit must protect tenants and provider trust.
  anti_lock_in_relevance: choice
preconditions:
  - publisher-isv-a owns service-portable-a
  - provider-public-a accepts public offer candidates
surfaces:
  - UI
  - API
  - Agent API
  - marketplace review
product_flow:
  - ISV submits offer-public-a
  - certification agent checks manifest, artifact, docs, support and portability
  - provider approves public-ready state or returns actionable blockers
  - governance records waiver only with scope and expiry
expected_state_vocabulary:
  - candidate
  - public-ready
  - warning
  - blocked
  - waived
evidence:
  requirement_refs:
    - CR-STAGE4-001..026
    - CR-CATALOG-021..028
    - CR-SECSUPPLY-030..038
  conformance_refs:
    - stage4-public-provider-ready
stop_condition_cases:
  - case: unsafe-evidence
    expected_result: blocked
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
