# SCENARIO-STAGE3-006 - Service Registry Publication

```yaml
id: SCENARIO-STAGE3-006
stage: STAGE-003
primary_role: ISV
secondary_roles:
  - admin
  - support
  - governance
  - AI agent
intent:
  user_goal: Publish or update a private-store service record with product evidence.
  why_it_matters: Private store trust depends on registry truth, not only discovered manifests or static artifacts.
  anti_lock_in_relevance: choice
preconditions:
  - presence-private-a has private store enabled
  - publisher-isv-a owns service-portable-a
  - service-portable-a has source-safe manifest validation evidence
surfaces:
  - private store UI
  - API
  - CLI
  - Agent API
product_flow:
  - publisher opens publication request for a service candidate
  - registry validates identity, owner, scope, manifest and evidence links
  - catalog card preview shows capability, compatibility, support, portability and policy state
  - admin reviews plan before visibility or installability changes
  - agent prepares a safe publication evidence summary and stops before approval
expected_state_vocabulary:
  - candidate
  - visible
  - warning
  - approval-required
  - install-ready
  - blocked
  - deprecated
evidence:
  requirement_refs:
    - CR-CATREG-001..032
    - CR-CATALOG-001..029
    - CR-STAGE3-001..026
  conformance_refs:
    - stage3-private-store-ready
  template_refs:
    - requirements/templates/service-registry-catalog-publication-template.md
  scenario_objects:
    - presence-private-a
    - service-portable-a
    - publisher-isv-a
stop_condition_cases:
  - case: static-asset-treated-as-publication-proof
    expected_result: blocked
  - case: missing-support-owner
    expected_result: blocked
  - case: source-history-overclaimed
    expected_result: warning
  - case: namespace-collision-without-owner-decision
    expected_result: manual_review_required
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: store owner
  stop_if_unknown: true
```
