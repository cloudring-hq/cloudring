# Secret Runtime Readiness Evidence Example

Synthetic example for
[../templates/secret-runtime-readiness-evidence-template.md](../templates/secret-runtime-readiness-evidence-template.md).

```yaml
secret_runtime_readiness_evidence:
  evidence_id: secret-runtime-readiness-private-a
  date: 2026-06-22
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
    presence_ref: presence-private-a
    service_refs:
      - service-workload-a
    capability_refs:
      - secret runtime
    applies_to:
      - encrypted declaration
      - brokered runtime access
      - rotation
      - evidence redaction
    claim_scope:
      proves:
        - secret values are not part of product memory or agent handoff
        - scope, owner, reconciliation state and key custody are represented as evidence
      does_not_prove:
        - live decryption succeeded
        - provider-grade production readiness
        - absence of all vulnerabilities
        - full source-history audit

  secret_reference_boundary:
    raw_value_absence_status: passed
    encrypted_data_classification_status: passed
    secret_reference_status: passed
    key_inventory_status: warning
    template_metadata_status: warning
    ordinary_config_separation_status: passed

  scope_and_tenancy:
    strict_scope_status: passed
    namespace_scope_status: warning
    cluster_scope_status: warning
    scope_weakening_approval_status: warning
    tenant_boundary_status: warning
    cross_scope_replay_status: warning

  key_and_certificate_custody:
    private_key_boundary_status: warning
    public_certificate_distribution_status: warning
    key_identity_fingerprint_status: warning
    validity_window_status: unknown
    rotation_rebinding_status: not-run
    multi_key_migration_status: not-applicable

  runtime_reconciliation:
    observed_generation_status: warning
    sync_condition_status: warning
    stale_state_status: warning
    error_redaction_status: passed
    unsupported_format_status: warning

  install_update_delete:
    crd_api_contract_status: warning
    schema_strictness_status: warning
    bundle_integrity_status: warning
    service_account_rbac_status: warning
    key_admin_separation_status: warning
    install_prerequisite_status: warning
    uninstall_retention_status: warning
    existing_secret_adoption_status: not-applicable
    deletion_cleanup_status: unknown

  operations_and_observability:
    health_readiness_status: warning
    metrics_redaction_status: warning
    dashboard_redaction_status: not-applicable
    degraded_mode_status: unknown
    fail_closed_status: warning
    agent_action_scope: read-only
    approval_status: not-applicable

  release_and_source_evidence:
    artifact_identity_status: warning
    provenance_status: warning
    validation_result_status: not-run
    source_coverage_status: warning
    history_coverage_status: not-applicable

  source_safety:
    sensitivity_class: synthetic
    redaction_status: passed
    private_marker_scan_status: passed
    strict_secret_scan_status: passed
    raw_source_copy_status: passed
    encrypted_material_disclosure_status: safe

  blockers: []
  warnings:
    - this is a source-safe evidence example and not a live runtime test
    - key validity, rotation and deletion cleanup are intentionally unknown in the synthetic example
    - namespace-wide or cluster-wide scope would require explicit approval evidence
  unresolved_gaps:
    - attach implementation-backed reconciliation report when runtime exists
    - attach rotation and rebinding evidence before claiming production readiness
    - attach install/uninstall retention report before claiming private presence readiness
  non_claims:
    - this example does not contain or prove secret values
    - this example does not certify a specific secret manager, controller, chart or cryptographic implementation
    - this example does not prove provider or federation readiness
  agent_handoff:
    allowed_actions:
      - review evidence
      - draft rotation plan
      - draft missing conformance fixture
    forbidden_actions:
      - retrieve raw secret values or private key material
      - paste encrypted blobs, raw grants, private paths or tenant data
      - claim provider-grade readiness from encrypted-at-rest evidence alone
    required_approvals:
      - secret runtime owner
```
