# Base OS Image Readiness Evidence Template

Use this template when a stage, infrastructure profile, source pass or provider
catalog claims reusable base OS image, golden image, VM template or image
factory readiness.

```yaml
base_os_image_readiness_evidence:
  evidence_id: base-os-image-readiness-evidence-id
  date: YYYY-MM-DD
  owner: infrastructure-owner
  stage_refs:
    - STAGE-002
  profile_refs:
    - stage2-private-presence-ready
  requirement_refs:
    - CR-BASEIMG-001..032
    - CR-INFPROFILE-008
    - CR-CAPEVID-028
  scenario_refs:
    - SCENARIO-STAGE2-007

  scope:
    image_line_ref: base-image-line-id
    artifact_ref: immutable-artifact-id-or-pending
    target_profiles:
      - private
    claim_scope:
      proves:
        - product claim
      does_not_prove:
        - explicit non-claim

  product_identity:
    purpose_status: passed | warning | failed | blocked
    owner_status: passed | warning | failed | blocked
    os_support_window_status: passed | warning | failed | blocked
    backend_adapter_boundary_status: passed | warning | failed | blocked
    stage_scope_status: passed | warning | failed | blocked

  build_inputs:
    input_classification_status: passed | warning | failed | blocked
    profile_boundary_status: passed | warning | failed | blocked
    secret_adjacent_handling_status: passed | warning | failed | blocked
    dependency_provenance_status: passed | warning | failed | blocked
    source_safety_status: passed | warning | failed | not-run

  install_and_provisioning:
    unattended_install_status: passed | warning | failed | blocked
    disk_layout_status: passed | warning | failed | blocked
    account_access_policy_status: passed | warning | failed | blocked
    package_baseline_status: passed | warning | failed | blocked
    role_composition_status: passed | warning | failed | blocked
    idempotence_status: passed | warning | failed | blocked | not-reviewed

  guest_readiness:
    guest_initialization_status: passed | warning | failed | blocked
    guest_tooling_status: passed | warning | failed | blocked
    disk_expansion_status: passed | warning | failed | blocked | not-applicable
    network_access_status: passed | warning | failed | blocked
    console_diagnostics_status: passed | warning | failed | blocked | not-applicable
    crash_boot_diagnostics_status: passed | warning | failed | blocked | not-applicable

  cleanup_and_sealing:
    machine_identity_cleanup_status: passed | warning | failed | blocked
    temporary_access_cleanup_status: passed | warning | failed | blocked
    log_cache_cleanup_status: passed | warning | failed | blocked
    generated_file_cleanup_status: passed | warning | failed | blocked
    diagnostic_retention_status: passed | warning | failed | blocked | not-applicable
    residue_scan_status: passed | warning | failed | blocked | not-run

  artifact_and_lifecycle:
    immutable_identity_status: passed | warning | failed | blocked
    provenance_status: passed | warning | failed | blocked
    validation_layer_status: passed | warning | failed | blocked
    first_boot_smoke_status: passed | warning | failed | blocked | not-run
    catalog_promotion_status: passed | warning | failed | blocked | not-applicable
    rollback_deprecation_status: passed | warning | failed | blocked
    multi_family_roadmap_status: passed | warning | failed | blocked | not-applicable

  ci_and_operability:
    ci_validation_status: passed | warning | failed | blocked | not-applicable
    timing_reliability_status: passed | warning | failed | blocked | not-reviewed
    agent_boundary_status: passed | warning | failed | blocked
    approval_status: passed | warning | failed | blocked | manual_review_required

  source_safety:
    sensitivity_class: synthetic | source-derived | operational | secret-adjacent
    raw_value_absence_status: passed | warning | failed | blocked
    private_marker_scan_status: passed | warning | failed | blocked | not-run
    strict_secret_scan_status: passed | warning | failed | blocked | not-run
    raw_source_copy_status: passed | warning | failed | blocked | not-reviewed
    profile_disclosure_status: safe | redacted | excluded | blocked

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
      - draft missing image readiness questions
    forbidden_actions:
      - paste raw build profiles, endpoints, credentials, private locations or copied configs
      - promote image readiness without first-boot and cleanup evidence
    required_approvals:
      - infrastructure owner
      - security owner
```

## Rules

1. A built artifact is not ready until install, provisioning, cleanup, first
   boot and source-safety evidence are separated.
2. Unknown artifact identity, cleanup state, owner, dependency provenance or
   first-boot result is warning or blocker, never pass.
3. Keep the template independent of any one image builder, OS family,
   virtualization backend or provisioning tool.
4. Treat build profiles and generated evidence as secret-adjacent until reviewed.
