# Secret Runtime Readiness Evidence Template

Use this template when a stage, service, presence, provider or source pass
claims encrypted secret or credential runtime readiness.

```yaml
secret_runtime_readiness_evidence:
  evidence_id: secret-runtime-readiness-evidence-id
  date: YYYY-MM-DD
  owner: secret-runtime-owner
  stage_refs:
    - STAGE-002
  profile_refs:
    - stage2-private-presence-ready
  requirement_refs:
    - CR-SECRETRUN-001..032
  scenario_refs:
    - SCENARIO-STAGE2-006

  scope:
    presence_ref: presence-id
    service_refs:
      - service-id
    capability_refs:
      - secret runtime
    applies_to:
      - encrypted declaration
      - brokered runtime access
      - rotation
      - evidence redaction
    claim_scope:
      proves:
        - product claim
      does_not_prove:
        - explicit non-claim

  secret_reference_boundary:
    raw_value_absence_status: passed | warning | failed | blocked
    encrypted_data_classification_status: passed | warning | failed | blocked
    secret_reference_status: passed | warning | failed | blocked
    key_inventory_status: passed | warning | failed | blocked | not-applicable
    template_metadata_status: passed | warning | failed | blocked | not-applicable
    ordinary_config_separation_status: passed | warning | failed | blocked

  scope_and_tenancy:
    strict_scope_status: passed | warning | failed | blocked | not-applicable
    namespace_scope_status: passed | warning | failed | blocked | not-applicable
    cluster_scope_status: passed | warning | failed | blocked | not-applicable
    scope_weakening_approval_status: passed | warning | failed | blocked | not-applicable
    tenant_boundary_status: passed | warning | failed | blocked | not-applicable
    cross_scope_replay_status: passed | warning | failed | blocked

  key_and_certificate_custody:
    private_key_boundary_status: passed | warning | failed | blocked
    public_certificate_distribution_status: passed | warning | failed | blocked | not-applicable
    key_identity_fingerprint_status: passed | warning | failed | blocked | not-applicable
    validity_window_status: passed | warning | failed | blocked | unknown
    rotation_rebinding_status: passed | warning | failed | blocked | not-run
    multi_key_migration_status: passed | warning | failed | blocked | not-applicable

  runtime_reconciliation:
    observed_generation_status: passed | warning | failed | blocked | not-applicable
    sync_condition_status: passed | warning | failed | blocked | unknown
    stale_state_status: passed | warning | failed | blocked | unknown
    error_redaction_status: passed | warning | failed | blocked
    unsupported_format_status: passed | warning | failed | blocked | not-applicable

  install_update_delete:
    crd_api_contract_status: passed | warning | failed | blocked | not-applicable
    schema_strictness_status: passed | warning | failed | blocked | unknown
    bundle_integrity_status: passed | warning | failed | blocked | not-applicable
    service_account_rbac_status: passed | warning | failed | blocked
    key_admin_separation_status: passed | warning | failed | blocked | not-applicable
    install_prerequisite_status: passed | warning | failed | blocked
    uninstall_retention_status: passed | warning | failed | blocked | unknown
    existing_secret_adoption_status: passed | warning | failed | blocked | not-applicable
    deletion_cleanup_status: passed | warning | failed | blocked | unknown

  operations_and_observability:
    health_readiness_status: passed | warning | failed | blocked
    metrics_redaction_status: passed | warning | failed | blocked | not-applicable
    dashboard_redaction_status: passed | warning | failed | blocked | not-applicable
    degraded_mode_status: passed | warning | failed | blocked | unknown
    fail_closed_status: passed | warning | failed | blocked
    agent_action_scope: read-only | safe-change | controlled-change | risky-change | emergency
    approval_status: passed | warning | failed | blocked | not-applicable

  release_and_source_evidence:
    artifact_identity_status: passed | warning | failed | blocked | not-applicable
    provenance_status: passed | warning | failed | blocked | not-applicable
    validation_result_status: passed | warning | failed | blocked | not-run
    source_coverage_status: passed | warning | failed | blocked
    history_coverage_status: passed | warning | failed | blocked | not-applicable

  source_safety:
    sensitivity_class: synthetic | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: passed | warning | failed | blocked
    private_marker_scan_status: passed | warning | failed | blocked | not-run
    strict_secret_scan_status: passed | warning | failed | blocked | not-run
    raw_source_copy_status: passed | warning | failed | blocked | not-reviewed
    encrypted_material_disclosure_status: safe | redacted | excluded | blocked

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
      - review evidence
      - draft rotation plan
    forbidden_actions:
      - retrieve raw secret values or private key material
      - paste encrypted blobs, raw grants, private paths or tenant data
      - claim provider-grade readiness from encrypted-at-rest evidence alone
    required_approvals:
      - secret runtime owner
```

## Rules

1. Treat unknown key custody, scope binding, generation status or source-safety
   as warning or blocker, never pass.
2. Do not paste secret values, encrypted blobs, private key material, topology,
   grants, raw source paths, commands or source snippets.
3. Separate encrypted declarations, public certificate distribution, private key
   custody and decrypted runtime output.
4. State what the evidence does not prove.
