# UI Extension Runtime Certification Template

Use this template when a service, store, provider offer, source pass or
conformance report claims UI extension readiness, embedded UI publication,
validation runtime parity or private/provider store certification.

```yaml
ui_extension_runtime_certification:
  evidence_id: ui-extension-runtime-certification-id
  date: YYYY-MM-DD
  owner: service-or-extension-owner
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
    service_ref: service-id
    extension_ref: ui-extension-id
    host_surface: portal | private-store | provider-console | global-discovery | local-preview
    publication_state: draft | local-ready | private-ready | provider-candidate | public-ready | deprecated | blocked
    claim_scope:
      proves:
        - product claim
      does_not_prove:
        - explicit non-claim

  embed_contract:
    typed_descriptor_status: passed | warning | failed | blocked
    host_authority_status: passed | warning | failed | blocked
    scoped_context_status: passed | warning | failed | blocked
    permission_rationale_status: passed | warning | failed | blocked
    compatibility_matrix_status: passed | warning | failed | blocked | not-applicable

  runtime_lifecycle:
    host_shell_execution_status: passed | warning | failed | blocked | not-run
    mount_status: passed | warning | failed | blocked
    update_status: passed | warning | failed | blocked | not-applicable
    suspend_status: passed | warning | failed | blocked | not-applicable
    unmount_cleanup_status: passed | warning | failed | blocked | not-run
    failure_fallback_status: passed | warning | failed | blocked
    route_navigation_status: passed | warning | failed | blocked

  experience_certification:
    theme_design_system_status: passed | warning | failed | blocked
    accessibility_status: passed | warning | failed | blocked | not-run
    focus_keyboard_status: passed | warning | failed | blocked | not-run
    responsive_status: passed | warning | failed | blocked | not-run
    localization_status: passed | warning | failed | blocked | not-applicable
    visual_regression_status: passed | warning | failed | blocked | not-run

  validation_runtime:
    phase_semantics_status: passed | warning | failed | blocked | not-applicable
    field_error_lifecycle_status: passed | warning | failed | blocked | not-applicable
    dependent_rule_status: passed | warning | failed | blocked | not-applicable
    stable_error_identity_status: passed | warning | failed | blocked | not-applicable
    parity_matrix_status: passed | warning | failed | blocked | not-applicable
    bounded_execution_status: passed | warning | failed | blocked | not-applicable
    fixture_depth_status: passed | warning | failed | blocked | not-applicable

  publication_and_trust:
    artifact_identity_status: passed | warning | failed | blocked
    provenance_status: passed | warning | failed | blocked
    dependency_shared_runtime_status: passed | warning | failed | blocked
    support_owner_status: passed | warning | failed | blocked
    telemetry_redaction_status: passed | warning | failed | blocked | not-applicable
    stage_gate_status: passed | warning | failed | blocked

  source_safety:
    sensitivity_class: synthetic | source-derived | operational | tenant-data | secret-adjacent
    raw_value_absence_status: passed | warning | failed | blocked
    private_marker_scan_status: passed | warning | failed | blocked | not-run
    strict_secret_scan_status: passed | warning | failed | blocked | not-run
    raw_source_copy_status: passed | warning | failed | blocked | not-reviewed
    asset_context_review_status: passed | warning | failed | blocked | not-reviewed

  blockers:
    - blocker
  warnings:
    - warning
  unresolved_gaps:
    - gap
  non_claims:
    - non-claim
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

## Rules

1. Local preview/build success is draft or local-ready evidence only.
2. Missing host authority, scoped context, lifecycle cleanup, support owner or
   artifact identity is a blocker for private/provider publication.
3. Missing browser, accessibility, localization or parity evidence is a warning
   or blocker according to the user-facing claim.
4. Keep the template independent of any one frontend framework, validation
   library, browser tool, packaging tool or store implementation.
