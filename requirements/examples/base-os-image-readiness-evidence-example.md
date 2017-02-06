# Base OS Image Readiness Evidence Example

Synthetic example for
[../templates/base-os-image-readiness-evidence-template.md](../templates/base-os-image-readiness-evidence-template.md).

```yaml
base_os_image_readiness_evidence:
  evidence_id: base-os-image-private-a
  date: 2026-06-22
  owner: infrastructure-owner-a
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
    image_line_ref: base-linux-image-a
    artifact_ref: image-artifact-private-a-immutable-id
    target_profiles:
      - private
    claim_scope:
      proves:
        - base image evidence has product identity, cleanup and validation shape
        - private profile readiness gaps are visible
      does_not_prove:
        - provider marketplace publication
        - vulnerability absence
        - multi-backend certification
        - full source-history audit

  product_identity:
    purpose_status: passed
    owner_status: passed
    os_support_window_status: warning
    backend_adapter_boundary_status: warning
    stage_scope_status: passed

  build_inputs:
    input_classification_status: passed
    profile_boundary_status: warning
    secret_adjacent_handling_status: passed
    dependency_provenance_status: warning
    source_safety_status: passed

  install_and_provisioning:
    unattended_install_status: passed
    disk_layout_status: warning
    account_access_policy_status: warning
    package_baseline_status: warning
    role_composition_status: passed
    idempotence_status: warning

  guest_readiness:
    guest_initialization_status: passed
    guest_tooling_status: warning
    disk_expansion_status: warning
    network_access_status: warning
    console_diagnostics_status: passed
    crash_boot_diagnostics_status: warning

  cleanup_and_sealing:
    machine_identity_cleanup_status: warning
    temporary_access_cleanup_status: warning
    log_cache_cleanup_status: warning
    generated_file_cleanup_status: warning
    diagnostic_retention_status: warning
    residue_scan_status: not-run

  artifact_and_lifecycle:
    immutable_identity_status: passed
    provenance_status: warning
    validation_layer_status: warning
    first_boot_smoke_status: warning
    catalog_promotion_status: warning
    rollback_deprecation_status: warning
    multi_family_roadmap_status: warning

  ci_and_operability:
    ci_validation_status: warning
    timing_reliability_status: warning
    agent_boundary_status: passed
    approval_status: manual_review_required

  source_safety:
    sensitivity_class: synthetic
    raw_value_absence_status: passed
    private_marker_scan_status: passed
    strict_secret_scan_status: passed
    raw_source_copy_status: passed
    profile_disclosure_status: safe

  blockers: []
  warnings:
    - first-boot and residue evidence are represented but not implementation-backed
    - backend adapter portability is not yet proven
    - release lifecycle has no signed/tagged promotion record in this example
  unresolved_gaps:
    - attach current first-boot smoke result before private-ready claim
    - attach cleanup residue scan before catalog promotion
    - attach dependency provenance review before provider-ready claim
  non_claims:
    - this example does not certify a specific OS or virtualization backend
    - this example does not include raw build profiles or operational values
    - this example does not prove compliance or vulnerability absence
  agent_handoff:
    allowed_actions:
      - review redacted evidence
      - draft missing cleanup and first-boot questions
      - prepare conformance report warning summary
    forbidden_actions:
      - paste raw build profiles, endpoints, credentials, private locations or copied configs
      - promote image readiness without first-boot and cleanup evidence
    required_approvals:
      - infrastructure owner
      - security owner
```
