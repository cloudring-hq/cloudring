# Synthetic Conformance Report Example

This example follows
[../templates/conformance-report-template.md](../templates/conformance-report-template.md).
It is a source-safe example for a Stage 1 style report.

```yaml
report:
  profile_id: stage1-service-ready
  profile_version: 0.2
  report_id: report-stage1-service-portable-a-example
  generated_at: synthetic-review-001
  stage: 1
  scope:
    product_increment: Solo Developer Cloud
    environment_profile: local
    service_or_presence: service-portable-a
    participants:
      - developer-a
      - agent-builder-a
  summary:
    decision: ready-with-limitations
    profile_status: warning
    current_product_promise:
      - developer can create, run, observe, document and validate service locally
    future_stage_gaps:
      - private-ready install needs Stage 3 service store evidence
      - provider billing is not part of Stage 1
    non_goals:
      - production HA
      - public provider tenant isolation
  role_coverage:
    user: warning
    admin: not-applicable
    developer_or_isv: passed
    provider: not-applicable
    support: warning
    governance: not-applicable
    ai_agent: passed
  scenario_refs:
    - SCENARIO-STAGE1-001
    - SCENARIO-STAGE1-003
  owners:
    profile_owner: org-owner-a
    evidence_owner: org-owner-a
    exception_owner: none
    approver: org-owner-a
  checks:
    - id: CONF-STAGE1-001
      title: Service manifest is valid and central
      criticality: hard-gate
      status: passed
      blocker_class: other
      requirement_refs:
        - CR-STAGE1-006
        - CR-OCSCONTRACT-001..046
      adr_refs:
        - ADR-0002
      evidence_refs:
        - ocs-service-manifest-example
      evidence_bundle_ids:
        - evidence-bundle-a
      evidence_freshness: current
      evidence_owner: org-owner-a
      future_stage_classification: required-now
      waiver_ref: none
      source_safety_status: safe
      user_impact: service cannot run without valid manifest
      agent_next_action: continue
      notes: synthetic manifest demonstrates service-as-product shape
    - id: CONF-STAGE1-020
      title: Role scenario coverage matrix exists
      criticality: warning-gate
      status: warning
      blocker_class: other
      requirement_refs:
        - CR-CONF-028
        - CR-SPECTPL-022
      adr_refs: []
      evidence_refs:
        - role-coverage-matrix
      evidence_bundle_ids:
        - evidence-bundle-a
      evidence_freshness: current
      evidence_owner: org-owner-a
      future_stage_classification: required-now
      waiver_ref: none
      source_safety_status: safe
      user_impact: starter coverage exists, but user/support fixtures need expansion
      agent_next_action: collect-evidence
      notes: future-expand roles are visible gaps, not passes
  evidence_bundles:
    - id: evidence-bundle-a
      type: contract
      owner: org-owner-a
      freshness: current
      redaction_status: safe
      retention: keep-summary
      links:
        - examples/ocs-service-manifest-example.md
  design_quality_reviews:
    - review_id: design-review-stage1-developer-a
      scenario_refs:
        - SCENARIO-STAGE1-003
      status: warning
      visible_consequence_coverage: passed
      alternative_analysis: warning
      provider_economics: not-applicable
      jurisdiction_overlay: not-applicable
      human_agent_parity: warning
      unresolved_gaps:
        - implementation-specific UI/API/CLI parity evidence is not available in this synthetic example
  ocs_information_model_evidence:
    - model_id: ocs-model-a
      model_version: ocs-model-0.1-example
      field_registry_version: field-registry-0.1-example
      validation_catalog_version: validation-catalog-0.1-example
      conformance_suite_version: ocs-suite-0.1-example
      compatibility_review_ref: compatibility-review-a
      status: warning
      round_trip_status: not-run
      unknown_field_policy_status: passed
      extension_lifecycle_status: passed
      source_safety_status: passed
      unresolved_gaps:
        - round-trip implementation evidence is not available in this synthetic example
  lifecycle_command_surface_evidence:
    - command_surface_id: lifecycle-command-stage1-a
      scenario_refs:
        - SCENARIO-STAGE1-005
      status: warning
      command_catalog_ref: service-lifecycle-command-surface-example
      preflight_status: warning
      risk_approval_status: warning
      structured_result_status: warning
      cleanup_status: warning
      task_plugin_boundary_status: warning
      generated_artifact_status: warning
      support_evidence_status: warning
      unresolved_gaps:
        - implementation-backed lifecycle command evidence is not available in this synthetic example
  service_dependency_deployment_evidence:
    - evidence_id: service-dependency-deployment-stage1-a
      scenario_refs:
        - SCENARIO-STAGE1-007
      status: warning
      effective_model_status: passed
      dependency_graph_status: warning
      component_ownership_status: warning
      connection_output_status: warning
      generated_artifact_status: passed
      env_handoff_status: warning
      preflight_conflict_status: warning
      role_matrix_status: warning
      portability_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed dependency conflict and portability evidence is not available in this synthetic example
  base_os_image_readiness_evidence:
    - evidence_id: base-os-image-stage2-a
      scenario_refs:
        - SCENARIO-STAGE2-007
      status: warning
      image_identity_status: passed
      build_input_classification_status: passed
      unattended_install_status: warning
      provisioning_role_status: warning
      guest_readiness_status: warning
      cleanup_sealing_status: warning
      artifact_identity_status: warning
      first_boot_smoke_status: warning
      lifecycle_promotion_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed first-boot, cleanup residue and artifact promotion evidence is not available in this synthetic example
  ui_extension_runtime_certification_evidence:
    - evidence_id: ui-extension-runtime-stage3-a
      scenario_refs:
        - SCENARIO-STAGE3-005
      status: warning
      typed_embed_descriptor_status: passed
      host_authority_status: warning
      scoped_context_status: warning
      runtime_lifecycle_status: warning
      validation_phase_status: passed
      stable_error_identity_status: warning
      parity_matrix_status: warning
      browser_runtime_status: warning
      accessibility_localization_status: warning
      artifact_publication_status: warning
      support_owner_status: passed
      telemetry_redaction_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed host-shell, accessibility, localization, parity and artifact provenance evidence is not available in this synthetic example
  billing_runtime_evidence:
    - evidence_id: billing-runtime-stage4-a
      scenario_refs:
        - SCENARIO-STAGE4-004
      status: warning
      usage_contract_status: warning
      receipt_status_status: warning
      idempotency_identity_status: warning
      backpressure_status: warning
      shutdown_drain_status: warning
      replay_quarantine_status: warning
      access_freshness_status: warning
      release_history_status: warning
      generated_docs_config_status: passed
      settlement_freeze_status: not-applicable
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed billing runtime evidence is not available in this Stage 1 synthetic example
  settlement_closure_evidence:
    - evidence_id: settlement-closure-stage5-a
      scenario_refs:
        - SCENARIO-STAGE5-006
      status: warning
      closure_run_status: warning
      input_manifest_status: warning
      reconciliation_status: warning
      settlement_freeze_status: not-applicable
      invoice_credit_refund_trace_status: warning
      participant_share_status: not-applicable
      dispute_hold_release_status: warning
      party_view_status: warning
      closeout_export_status: warning
      approval_override_status: warning
      release_history_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed settlement closure evidence is not available in this Stage 1 synthetic example
  presence_bootstrap_activation_evidence:
    - evidence_id: presence-bootstrap-stage2-a
      scenario_refs:
        - SCENARIO-STAGE2-008
      status: warning
      activation_workflow_status: warning
      install_provenance_status: warning
      artifact_identity_status: warning
      distribution_channel_status: warning
      config_schema_profile_status: passed
      atomic_write_status: warning
      preflight_status: warning
      runtime_provider_matrix_status: warning
      diagnostics_status: warning
      smoke_readiness_status: warning
      generated_artifact_inventory_status: warning
      resumability_lock_status: warning
      rollback_cleanup_status: warning
      infrastructure_profile_status: not-applicable
      agent_approval_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed bootstrap activation evidence is not available in this Stage 1 synthetic example
  controlled_extension_task_automation_evidence:
    - evidence_id: controlled-automation-stage1-a
      scenario_refs:
        - SCENARIO-STAGE1-008
      status: warning
      automation_kind_status: passed
      execution_class_status: warning
      owner_support_status: warning
      selection_rationale_status: passed
      artifact_identity_status: warning
      provenance_integrity_status: warning
      version_policy_status: warning
      execution_scope_status: warning
      env_secret_boundary_status: warning
      env_export_policy_status: warning
      argument_schema_status: warning
      runtime_budget_status: warning
      filesystem_network_policy_status: warning
      mutation_rollback_status: warning
      structured_result_status: warning
      managed_runner_boundary_status: warning
      agent_approval_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - local task/plugin automation is represented as warning until managed-runner evidence exists
  stateful_recovery_evidence:
    - evidence_id: stateful-readiness-stage2-a
      scenario_refs:
        - SCENARIO-STAGE2-004
        - SCENARIO-STAGE2-005
      status: warning
      topology_status: warning
      backup_archive_status: warning
      restore_pitr_status: warning
      failover_status: warning
      endpoint_ownership_status: warning
      audit_findings_status: warning
      access_role_status: warning
      source_history_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed restore and failover drills are not available in this synthetic example
  secret_runtime_readiness_evidence:
    - evidence_id: secret-runtime-readiness-stage2-a
      scenario_refs:
        - SCENARIO-STAGE2-006
      status: warning
      secret_reference_boundary_status: passed
      scope_binding_status: warning
      key_custody_status: warning
      public_certificate_status: warning
      generation_condition_status: warning
      install_delete_status: warning
      rbac_status: warning
      health_metrics_status: warning
      rotation_rebinding_status: warning
      degraded_fail_closed_status: warning
      source_safety_status: passed
      unresolved_gaps:
        - implementation-backed secret reconciliation and key rotation evidence is not available in this synthetic example
  documentation_decision_memory_evidence:
    - evidence_id: documentation-decision-memory-stage1-a
      scenario_refs:
        - SCENARIO-STAGE1-006
      status: warning
      docs_package_status: warning
      adr_or_no_adr_status: passed
      template_link_status: passed
      synthetic_example_status: passed
      source_pass_link_status: passed
      owner_freshness_status: passed
      feedback_triage_status: warning
      non_claim_status: passed
      source_safety_status: passed
      unresolved_gaps:
        - command reference validation is not implementation-backed in this synthetic example
        - offline docs export evidence is not attached
  exceptions: []
  agent_handoff:
    risk_class: safe-change
    allowed_actions:
      - add synthetic scenario fixture
      - strengthen requirements
      - run validation scans
    forbidden_actions:
      - claim production readiness
      - include raw source material
    required_approvals:
      - owner approval for weakening hard gate
    validation_needed:
      - CR ID consistency
      - link check
      - source-safety scan
    remaining_gaps:
      - more Stage 1 user and support scenario fixtures
  profile_change:
    profile_change_record_ref: none
    changed_checks: []
    compatibility_impact: none
  validation_summary:
    cr_id_check: passed
    stage_id_check: passed
    link_check: passed
    private_marker_scan: passed
    strict_secret_scan: passed
    copyright_safety_review: passed
    raw_match_output_retained: false
  source_safety:
    sensitivity_class: public-template
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    reviewer_or_owner: org-owner-a
    stop_if_unknown: true
```

## Non-Claims

- This report example does not prove an implementation exists.
- This report example does not replace real conformance execution.
- Warning status is intentional: starter fixture coverage is not full role
  coverage.
