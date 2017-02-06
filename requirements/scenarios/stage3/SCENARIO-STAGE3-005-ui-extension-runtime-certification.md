# SCENARIO-STAGE3-005 - UI Extension Runtime Certification

```yaml
id: SCENARIO-STAGE3-005
stage: STAGE-003
primary_role: ISV
secondary_roles:
  - admin
  - user
  - support
  - governance
  - AI agent
intent:
  user_goal: Certify that a service UI extension can be installed from the private store without breaking host trust, validation parity, accessibility or supportability.
  why_it_matters: Store services need their own UI, but embedded UI is executable user experience and must not bypass policy or fragment CloudRING.
  anti_lock_in_relevance: portable-ui-extension-contract
preconditions:
  - service-portable-a has a candidate UI extension
  - private store supports certification states
  - raw source, tenant data and private runtime values are excluded from agent context
surfaces:
  - portal
  - private store
  - API
  - CLI
  - Agent API
  - conformance report
product_flow:
  - ISV submits UI extension descriptor and validation contract evidence
  - store checks host authority, scoped context, permissions, artifact identity and support owner
  - runtime certification executes representative host-shell mount and failure cleanup
  - user-facing review checks accessibility, localization, responsive behavior and design-system containment
  - validation review compares phase semantics, error identity and parity across UI/API/CLI/Agent API
  - governance blocks promotion until source-safety and publication evidence are current
expected_state_vocabulary:
  - draft
  - local-ready
  - certification-running
  - private-ready
  - provider-candidate
  - warning
  - blocked
  - deprecated
evidence:
  requirement_refs:
    - CR-UICERT-001..032
    - CR-OCSCONTRACT-017
    - CR-OCSCONTRACT-018
    - CR-SECSUPPLY-016
    - CR-SECSUPPLY-032
    - CR-CONF-039
    - CR-CAPEVID-029
    - CR-SPECTPL-033
    - CR-SPECEX-021
    - CR-STAGE3-001..026
  conformance_refs:
    - stage3-private-store-ready
  template_refs:
    - ui-extension-runtime-certification-template
  example_refs:
    - ui-extension-runtime-certification-example
stop_condition_cases:
  - case: extension-published-from-local-preview-only
    expected_result: blocked
  - case: scoped-context-or-permissions-unknown
    expected_result: blocked
  - case: validation-error-has-no-stable-machine-id
    expected_result: warning
  - case: browser-runtime-evidence-missing
    expected_result: warning
  - case: accessibility-evidence-missing-for-user-facing-ui
    expected_result: warning
  - case: artifact-identity-or-support-owner-missing
    expected_result: blocked
source_safety:
  sensitivity_class: source-derived
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: experience owner
  stop_if_unknown: true
```
