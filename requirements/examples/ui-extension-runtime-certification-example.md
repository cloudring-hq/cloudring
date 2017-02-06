# UI Extension Runtime Certification Example

Synthetic example for
[../templates/ui-extension-runtime-certification-template.md](../templates/ui-extension-runtime-certification-template.md).

```yaml
ui_extension_runtime_certification:
  evidence_id: ui-extension-runtime-private-a
  date: 2026-06-22
  owner: service-owner-a
  stage_refs:
    - STAGE-003
  profile_refs:
    - stage3-private-store-ready
  requirement_refs:
    - CR-UICERT-001..032
    - CR-CAPEVID-029
  scenario_refs:
    - SCENARIO-STAGE3-005

  scope:
    service_ref: service-portable-a
    extension_ref: ui-extension-a
    host_surface: private-store
    publication_state: private-ready
    claim_scope:
      proves:
        - embedded UI contract is represented as certification evidence
        - validation runtime gaps are visible before store promotion
      does_not_prove:
        - provider-public publication
        - vulnerability absence
        - external accessibility audit
        - full source-history audit

  embed_contract:
    typed_descriptor_status: passed
    host_authority_status: passed
    scoped_context_status: warning
    permission_rationale_status: warning
    compatibility_matrix_status: warning

  runtime_lifecycle:
    host_shell_execution_status: warning
    mount_status: passed
    update_status: warning
    suspend_status: not-applicable
    unmount_cleanup_status: warning
    failure_fallback_status: warning
    route_navigation_status: warning

  experience_certification:
    theme_design_system_status: warning
    accessibility_status: warning
    focus_keyboard_status: warning
    responsive_status: warning
    localization_status: warning
    visual_regression_status: warning

  validation_runtime:
    phase_semantics_status: passed
    field_error_lifecycle_status: warning
    dependent_rule_status: warning
    stable_error_identity_status: warning
    parity_matrix_status: warning
    bounded_execution_status: warning
    fixture_depth_status: warning

  publication_and_trust:
    artifact_identity_status: warning
    provenance_status: warning
    dependency_shared_runtime_status: warning
    support_owner_status: passed
    telemetry_redaction_status: warning
    stage_gate_status: warning

  source_safety:
    sensitivity_class: synthetic
    raw_value_absence_status: passed
    private_marker_scan_status: passed
    strict_secret_scan_status: passed
    raw_source_copy_status: passed
    asset_context_review_status: passed

  blockers: []
  warnings:
    - private-ready claim needs real host-shell execution evidence
    - validation parity is represented but not implementation-backed
    - accessibility and localization are warning-state evidence only
  unresolved_gaps:
    - attach browser/runtime matrix before provider publication
    - attach stable machine-readable error catalog before policy-critical validation
    - attach immutable artifact identity and provenance before normal store install
  non_claims:
    - this example does not certify any specific frontend framework
    - this example does not include real tenant data or raw extension bundle
    - this example does not prove full accessibility compliance
  agent_handoff:
    allowed_actions:
      - review redacted evidence
      - draft missing certification questions
      - compare parity matrix
    forbidden_actions:
      - paste raw source, credentials, tenant data, private routes or endpoint values
      - mark extension private-ready from local preview alone
    required_approvals:
      - service owner
      - security owner
      - experience owner
```
