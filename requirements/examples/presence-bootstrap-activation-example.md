# Synthetic Presence Bootstrap Activation Example

This example follows
[../templates/presence-bootstrap-activation-template.md](../templates/presence-bootstrap-activation-template.md).
It uses synthetic objects only and does not prove a real implementation exists.

```yaml
presence_bootstrap_activation_evidence:
  evidence_id: presence-bootstrap-single-host-a
  stage_scope: Stage 2
  profile_refs:
    - stage2-private-presence-ready
  requirement_refs:
    - CR-PRESBOOT-001..032
  scenario_refs:
    - SCENARIO-STAGE2-008
  workstream_refs:
    - WS-033
  owners:
    activation_owner: private-admin-a
    infrastructure_owner: infra-owner-a
    security_owner: security-owner-a
    evidence_owner: evidence-owner-a
    approver: private-admin-a
  activation:
    activation_id: activate-presence-a
    target_profile: single-host-private
    actor: ai-agent
    status: degraded
    install_provenance_status: warning
    tool_compatibility_status: passed
    current_product_promise:
      - admin can activate a local control surface with explicit limitations
    future_stage_non_goals:
      - public provider billing
      - cross-participant federation
  artifact_and_distribution:
    bootstrap_artifact_ref: bootstrap-bundle-a
    artifact_version: bootstrap-bundle-0.1-example
    provenance_status: warning
    integrity_status: warning
    compatibility_status: passed
    distribution_mode: cached-offline
    freshness: current
    downgrade_policy_status: warning
  config_and_preflight:
    config_schema_version: presence-config-0.1-example
    profile_resolution_status: passed
    atomic_write_status: warning
    previous_config_backup_status: warning
    resource_preflight_status: passed
    port_route_conflict_status: warning
    env_classification_status: passed
  runtime_presence:
    runtime_provider_state: degraded
    start_stop_status: warning
    ingress_routing_status: warning
    local_autonomy_status: passed
    infrastructure_profile_ref: infra-profile-single-host-a
    infrastructure_profile_status: warning
  diagnostics_and_operations:
    activation_report_status: passed
    doctor_report_status: warning
    smoke_readiness_status: warning
    generated_artifact_inventory_status: warning
    resumability_lock_status: warning
    rollback_cleanup_status: warning
    update_plan_status: warning
    docs_contract_status: warning
    fixture_status: warning
  agent_handoff:
    risk_class: controlled-change
    dry_run_status: passed
    approval_status: passed
    allowed_actions:
      - inspect evidence
      - collect missing route conflict proof
      - propose rollback checklist
    forbidden_actions:
      - mark private presence ready
      - overwrite config without backup
      - expose raw config, secret-adjacent env or local paths
    required_approvals:
      - private admin approval before activation apply
    remaining_gaps:
      - artifact signature is represented as warning in this synthetic example
      - rollback cleanup proof is not implementation-backed
  source_safety:
    sensitivity_class: secret-adjacent
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    raw_match_output_retained: false
  non_claims:
    - example does not prove a live private cloud installation
    - example does not choose final installer or runtime provider
    - degraded status is intentional and must not be treated as ready
```

## Non-Claims

- This example is not a final installer schema.
- This example does not include real configs, paths, endpoints, credentials or
  topology.
- Warning/degraded statuses are intentional to show honest readiness.
