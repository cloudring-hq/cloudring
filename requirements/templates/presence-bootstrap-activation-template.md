# Presence Bootstrap Activation Evidence Template

Purpose: capture source-safe evidence that a local or private CloudRING presence
can be bootstrapped through trusted assets, validated config, profile-aware
runtime activation, diagnostics, rollback/cleanup and agent-safe handoff.

```yaml
presence_bootstrap_activation_evidence:
  evidence_id: presence-bootstrap-evidence-id
  stage_scope: Stage 1 | Stage 2
  profile_refs:
    - stage1-service-ready
    - stage2-private-presence-ready
  requirement_refs:
    - CR-PRESBOOT-001..032
  scenario_refs:
    - SCENARIO-STAGE2-008
  workstream_refs:
    - WS-033
  owners:
    activation_owner: role
    infrastructure_owner: role
    security_owner: role
    evidence_owner: role
    approver: role
  activation:
    activation_id: safe-id
    target_profile: local | single-host-private | multi-node-private | edge | provider
    actor: user | admin | ai-agent | support
    status: not-started | preflighting | blocked | downloading | configured | starting-runtime | active | degraded | manual-external | rolling-back | failed | cleaned-up
    install_provenance_status: passed | warning | failed | blocked
    tool_compatibility_status: passed | warning | failed | blocked
    current_product_promise:
      - promise
    future_stage_non_goals:
      - non-goal
  artifact_and_distribution:
    bootstrap_artifact_ref: safe-reference
    artifact_version: version-or-safe-id
    provenance_status: passed | warning | failed | blocked
    integrity_status: passed | warning | failed | blocked
    compatibility_status: passed | warning | failed | blocked
    distribution_mode: connected | private-mirror | cached-offline | manual-import
    freshness: current | stale | unknown | contradicted
    downgrade_policy_status: passed | warning | failed | blocked | not-applicable
  config_and_preflight:
    config_schema_version: version-or-safe-id
    profile_resolution_status: passed | warning | failed | blocked
    atomic_write_status: passed | warning | failed | blocked
    previous_config_backup_status: passed | warning | failed | blocked | not-applicable
    resource_preflight_status: passed | warning | failed | blocked
    port_route_conflict_status: passed | warning | failed | blocked | not-applicable
    env_classification_status: passed | warning | failed | blocked
  runtime_presence:
    runtime_provider_state: supported | degraded | unsupported | blocked | manual-external | unstartable | unknown
    start_stop_status: passed | warning | failed | blocked | not-applicable
    ingress_routing_status: passed | warning | failed | blocked | not-applicable
    local_autonomy_status: passed | warning | failed | blocked | not-applicable
    infrastructure_profile_ref: safe-reference
    infrastructure_profile_status: passed | warning | failed | blocked
  diagnostics_and_operations:
    activation_report_status: passed | warning | failed | blocked
    doctor_report_status: passed | warning | failed | blocked
    smoke_readiness_status: passed | warning | failed | blocked | not-applicable
    generated_artifact_inventory_status: passed | warning | failed | blocked
    resumability_lock_status: passed | warning | failed | blocked
    rollback_cleanup_status: passed | warning | failed | blocked
    update_plan_status: passed | warning | failed | blocked | not-applicable
    docs_contract_status: passed | warning | failed | blocked
    fixture_status: passed | warning | failed | blocked
  agent_handoff:
    risk_class: read-only | safe-change | controlled-change | risky-change
    dry_run_status: passed | warning | failed | blocked
    approval_status: passed | warning | failed | blocked | not-applicable
    allowed_actions:
      - inspect evidence
      - propose remediation
    forbidden_actions:
      - overwrite config without backup
      - expose raw secrets, endpoints, topology or local paths
      - claim Stage 2 readiness from Stage 1 local bootstrap
    required_approvals:
      - owner approval for state-changing activation
    remaining_gaps:
      - gap
  source_safety:
    sensitivity_class: source-derived | operational | secret-adjacent | topology-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    raw_match_output_retained: false
  non_claims:
    - explicit non-claim
```

## Rules

1. Treat unknown artifact trust, config safety or runtime state as blocker or
   manual review, never as pass.
2. Keep Stage 1 local bootstrap and Stage 2 private presence activation separate.
3. Store evidence references and safe summaries, not raw configs, paths,
   endpoints, secrets, command output or copied docs.
