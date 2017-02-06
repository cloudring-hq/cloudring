# Conformance Report Template

Purpose: produce a readiness report that a human and AI-agent can review in the
same way. This template applies to stage profiles, capability profiles and
source-derived evidence updates.

```yaml
report:
  profile_id: stage-or-capability-profile
  profile_version: version
  report_id: stable-report-id
  generated_at: date-or-build-identity
  stage: stage-number-or-not-applicable
  scope:
    product_increment: name
    environment_profile: local | private | provider | federation | global | edge | source-memory
    service_or_presence: safe-identifier
    participants:
      - role-only-or-safe-identifier
  summary:
    decision: ready | ready-with-limitations | not-ready | blocked
    profile_status: passed | failed | blocked | warning | stale | manual_review_required | unknown
    current_product_promise:
      - promise
    future_stage_gaps:
      - non-blocking gap
    non_goals:
      - explicit non-goal
  owners:
    profile_owner: role
    evidence_owner: role
    exception_owner: role
    approver: role
  checks:
    - id: CONF-STAGEN-000
      title: check title
      criticality: hard-gate | warning-gate | informational | future-gap
      status: passed | failed | blocked | warning | skipped | waived | stale | not-applicable | degraded | manual_review_required | unknown
      blocker_class: ownership | secret-safety | policy | portability | billing | support | trust | source-coverage | other
      requirement_refs:
        - CR-...
      adr_refs:
        - ADR-...
      evidence_refs:
        - safe-reference
      evidence_bundle_ids:
        - evidence-bundle-id
      evidence_freshness: current | stale | unknown | contradicted
      evidence_owner: role
      future_stage_classification: required-now | accepted-non-goal | future-stage-gap | not-applicable
      waiver_ref: waiver-id-or-none
      source_safety_status: safe | warning | blocked | not-reviewed
      user_impact: concise impact
      agent_next_action: continue | collect-evidence | request-approval | create-ADR | stop
      notes: concise explanation
  evidence_bundles:
    - id: evidence-bundle-id
      type: product-flow | contract | operational | trust | policy | audit | economic | support | portability | experience | agent | source-coverage
      owner: role
      freshness: current | stale | unknown
      redaction_status: safe | warning | blocked | not-reviewed
      retention: keep-summary | keep-reference | restricted | delete-after-review
      links:
        - safe-reference
  design_quality_reviews:
    - review_id: design-review-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | manual_review_required
      visible_consequence_coverage: passed | warning | failed
      alternative_analysis: passed | warning | failed | not-applicable
      provider_economics: passed | warning | failed | not-applicable
      jurisdiction_overlay: passed | warning | failed | not-applicable
      human_agent_parity: passed | warning | failed
      unresolved_gaps:
        - gap
  ocs_information_model_evidence:
    - model_id: ocs-model-id
      model_version: version
      field_registry_version: version
      validation_catalog_version: version
      conformance_suite_version: version
      compatibility_review_ref: safe-reference
      status: passed | warning | failed | blocked | stale | not-applicable
      round_trip_status: passed | warning | failed | not-run | not-applicable
      unknown_field_policy_status: passed | warning | failed | not-applicable
      extension_lifecycle_status: passed | warning | failed | not-applicable
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  lifecycle_command_surface_evidence:
    - command_surface_id: lifecycle-command-surface-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      command_catalog_ref: safe-reference
      preflight_status: passed | warning | failed | not-applicable
      risk_approval_status: passed | warning | failed | not-applicable
      structured_result_status: passed | warning | failed
      cleanup_status: passed | warning | failed | not-applicable
      task_plugin_boundary_status: passed | warning | failed | not-applicable
      generated_artifact_status: passed | warning | failed | not-applicable
      support_evidence_status: passed | warning | failed
      unresolved_gaps:
        - gap
  service_dependency_deployment_evidence:
    - evidence_id: service-dependency-deployment-evidence-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      effective_model_status: passed | warning | failed | blocked
      dependency_graph_status: passed | warning | failed | blocked
      component_ownership_status: passed | warning | failed | blocked
      connection_output_status: passed | warning | failed | blocked
      generated_artifact_status: passed | warning | failed | blocked
      env_handoff_status: passed | warning | failed | blocked | not-applicable
      preflight_conflict_status: passed | warning | failed | blocked | not-applicable
      role_matrix_status: passed | warning | failed | blocked | not-applicable
      portability_status: passed | warning | failed | blocked | not-applicable
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  base_os_image_readiness_evidence:
    - evidence_id: base-os-image-readiness-evidence-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      image_identity_status: passed | warning | failed | blocked
      build_input_classification_status: passed | warning | failed | blocked
      unattended_install_status: passed | warning | failed | blocked
      provisioning_role_status: passed | warning | failed | blocked
      guest_readiness_status: passed | warning | failed | blocked
      cleanup_sealing_status: passed | warning | failed | blocked
      artifact_identity_status: passed | warning | failed | blocked
      first_boot_smoke_status: passed | warning | failed | blocked | not-run
      lifecycle_promotion_status: passed | warning | failed | blocked | not-applicable
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  ui_extension_runtime_certification_evidence:
    - evidence_id: ui-extension-runtime-certification-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      typed_embed_descriptor_status: passed | warning | failed | blocked
      host_authority_status: passed | warning | failed | blocked
      scoped_context_status: passed | warning | failed | blocked
      runtime_lifecycle_status: passed | warning | failed | blocked | not-run
      validation_phase_status: passed | warning | failed | blocked | not-applicable
      stable_error_identity_status: passed | warning | failed | blocked | not-applicable
      parity_matrix_status: passed | warning | failed | blocked | not-applicable
      browser_runtime_status: passed | warning | failed | blocked | not-run
      accessibility_localization_status: passed | warning | failed | blocked | not-run
      artifact_publication_status: passed | warning | failed | blocked
      support_owner_status: passed | warning | failed | blocked
      telemetry_redaction_status: passed | warning | failed | blocked | not-applicable
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  billing_runtime_evidence:
    - evidence_id: billing-runtime-evidence-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      usage_contract_status: passed | warning | failed | blocked
      receipt_status_status: passed | warning | failed | blocked
      idempotency_identity_status: passed | warning | failed | blocked
      backpressure_status: passed | warning | failed | blocked
      shutdown_drain_status: passed | warning | failed | blocked
      replay_quarantine_status: passed | warning | failed | blocked
      access_freshness_status: passed | warning | failed | blocked
      release_history_status: passed | warning | failed | blocked
      generated_docs_config_status: passed | warning | failed | blocked
      settlement_freeze_status: passed | warning | failed | blocked | not-applicable
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  settlement_closure_evidence:
    - evidence_id: settlement-closure-evidence-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      closure_run_status: passed | warning | failed | blocked
      input_manifest_status: passed | warning | failed | blocked
      reconciliation_status: passed | warning | failed | blocked
      settlement_freeze_status: passed | warning | failed | blocked | not-applicable
      invoice_credit_refund_trace_status: passed | warning | failed | blocked | not-applicable
      participant_share_status: passed | warning | failed | blocked | not-applicable
      dispute_hold_release_status: passed | warning | failed | blocked | not-applicable
      party_view_status: passed | warning | failed | blocked
      closeout_export_status: passed | warning | failed | blocked
      approval_override_status: passed | warning | failed | blocked | not-applicable
      release_history_status: passed | warning | failed | blocked
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  presence_bootstrap_activation_evidence:
    - evidence_id: presence-bootstrap-activation-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      activation_workflow_status: passed | warning | failed | blocked
      install_provenance_status: passed | warning | failed | blocked
      artifact_identity_status: passed | warning | failed | blocked
      distribution_channel_status: passed | warning | failed | blocked
      config_schema_profile_status: passed | warning | failed | blocked
      atomic_write_status: passed | warning | failed | blocked
      preflight_status: passed | warning | failed | blocked
      runtime_provider_matrix_status: passed | warning | failed | blocked
      diagnostics_status: passed | warning | failed | blocked
      smoke_readiness_status: passed | warning | failed | blocked | not-applicable
      generated_artifact_inventory_status: passed | warning | failed | blocked
      resumability_lock_status: passed | warning | failed | blocked
      rollback_cleanup_status: passed | warning | failed | blocked
      infrastructure_profile_status: passed | warning | failed | blocked | not-applicable
      agent_approval_status: passed | warning | failed | blocked | not-applicable
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  controlled_extension_task_automation_evidence:
    - evidence_id: controlled-automation-evidence-id
      scenario_refs:
        - SCENARIO-STAGE1-008
      status: passed | warning | failed | blocked | stale | not-applicable
      automation_kind_status: passed | warning | failed | blocked
      execution_class_status: passed | warning | failed | blocked
      owner_support_status: passed | warning | failed | blocked
      selection_rationale_status: passed | warning | failed | blocked
      artifact_identity_status: passed | warning | failed | blocked
      provenance_integrity_status: passed | warning | failed | blocked
      version_policy_status: passed | warning | failed | blocked
      execution_scope_status: passed | warning | failed | blocked
      env_secret_boundary_status: passed | warning | failed | blocked
      env_export_policy_status: passed | warning | failed | blocked
      argument_schema_status: passed | warning | failed | blocked
      runtime_budget_status: passed | warning | failed | blocked
      filesystem_network_policy_status: passed | warning | failed | blocked
      mutation_rollback_status: passed | warning | failed | blocked | not-applicable
      structured_result_status: passed | warning | failed | blocked
      managed_runner_boundary_status: passed | warning | failed | blocked
      agent_approval_status: passed | warning | failed | blocked | not-applicable
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  stateful_recovery_evidence:
    - evidence_id: stateful-readiness-evidence-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      topology_status: passed | warning | failed | blocked
      backup_archive_status: passed | warning | failed | blocked | stale
      restore_pitr_status: passed | warning | failed | blocked | not-applicable
      failover_status: passed | warning | failed | blocked | not-applicable
      endpoint_ownership_status: passed | warning | failed | blocked | not-applicable
      audit_findings_status: passed | warning | failed | blocked
      access_role_status: passed | warning | failed | blocked
      source_history_status: passed | warning | failed | blocked
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  secret_runtime_readiness_evidence:
    - evidence_id: secret-runtime-readiness-evidence-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      secret_reference_boundary_status: passed | warning | failed | blocked
      scope_binding_status: passed | warning | failed | blocked
      key_custody_status: passed | warning | failed | blocked
      public_certificate_status: passed | warning | failed | blocked | stale
      generation_condition_status: passed | warning | failed | blocked | stale
      install_delete_status: passed | warning | failed | blocked | not-applicable
      rbac_status: passed | warning | failed | blocked
      health_metrics_status: passed | warning | failed | blocked | not-applicable
      rotation_rebinding_status: passed | warning | failed | blocked | not-applicable
      degraded_fail_closed_status: passed | warning | failed | blocked
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  documentation_decision_memory_evidence:
    - evidence_id: documentation-decision-memory-evidence-id
      scenario_refs:
        - SCENARIO-STAGEN-000
      status: passed | warning | failed | blocked | stale | not-applicable
      docs_package_status: passed | warning | failed | blocked | not-applicable
      adr_or_no_adr_status: passed | warning | failed | blocked | not-applicable
      template_link_status: passed | warning | failed | blocked | not-applicable
      synthetic_example_status: passed | warning | failed | blocked | not-applicable
      source_pass_link_status: passed | warning | failed | blocked | not-applicable
      owner_freshness_status: passed | warning | failed | blocked
      feedback_triage_status: passed | warning | failed | blocked | not-applicable
      non_claim_status: passed | warning | failed | blocked
      source_safety_status: passed | warning | failed | not-run
      unresolved_gaps:
        - gap
  exceptions:
    - id: waiver-id
      status: proposed | approved | expired | revoked | superseded
      scope: affected profile/service/presence/capability
      reason: product reason
      risk: risk statement
      compensation: mitigation or customer/support plan
      approver: role
      review_trigger: date-or-condition
      expiry: date-or-condition
      linked_requirement: CR-...
      linked_adr: ADR-...
  agent_handoff:
    risk_class: read-only | safe-change | controlled-change | risky-change | destructive | emergency
    allowed_actions:
      - action
    forbidden_actions:
      - action
    required_approvals:
      - approval class
    validation_needed:
      - check
    remaining_gaps:
      - gap
  profile_change:
    profile_change_record_ref: safe-reference-or-none
    changed_checks:
      - check id
    compatibility_impact: none | minor | breaking | unknown
  validation_summary:
    cr_id_check: passed | failed | not-run
    stage_id_check: passed | failed | not-run
    link_check: passed | failed | not-run
    private_marker_scan: passed | failed | not-run
    strict_secret_scan: passed | failed | not-run
    copyright_safety_review: passed | warning | blocked | not-run
    raw_match_output_retained: false
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
```

## Report Rules

1. `unknown` evidence is never equivalent to `passed`.
2. Critical blockers cannot be waived by the same actor that failed the check.
3. Waiver must have scope, reason, risk, compensation, owner, approver and
   expiry/review trigger.
4. Future-stage gaps must not block current stage unless the current stage
   explicitly depends on them.
5. Source-safety failures block report publication until repaired.
6. Raw private scan matches, source snippets, credentials and tenant data are
   never stored inside the report.
