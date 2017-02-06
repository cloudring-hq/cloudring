# Service Dependency Deployment Evidence Template

Use this template when a service, stage or source pass claims dependency model,
generated deployment artifact or local dependency runtime readiness.

```yaml
service_dependency_deployment_evidence:
  evidence_id: service-dependency-deployment-evidence-id
  date: YYYY-MM-DD
  owner: service-owner
  stage_refs:
    - STAGE-001
  profile_refs:
    - stage1-service-ready
  requirement_refs:
    - CR-SVCDEPLOY-001..032
  scenario_refs:
    - SCENARIO-STAGE1-007

  scope:
    service_ref: service-id
    source_model_ref: service-model-id
    generator_ref: generator-id
    target_profiles:
      - local
    claim_scope:
      proves:
        - product claim
      does_not_prove:
        - explicit non-claim

  effective_service_model:
    identity_status: passed | warning | failed | blocked
    profile_resolution_status: passed | warning | failed | blocked
    override_consequence_status: passed | warning | failed | blocked
    minimal_model_status: draft | passed | warning | failed | blocked
    stage_scope_status: passed | warning | failed | blocked

  dependency_graph:
    capability_class_status: passed | warning | failed | blocked
    instance_identity_status: passed | warning | failed | blocked
    service_component_status: passed | warning | failed | blocked | not-applicable
    platform_component_status: passed | warning | failed | blocked | not-applicable
    external_dependency_status: passed | warning | failed | blocked | not-applicable
    startup_readiness_edge_status: passed | warning | failed | blocked | not-applicable
    owner_support_status: passed | warning | failed | blocked

  connection_outputs:
    output_type_status: passed | warning | failed | blocked
    data_classification_status: passed | warning | failed | blocked
    redaction_status: passed | warning | failed | blocked
    secret_reference_status: passed | warning | failed | blocked | not-applicable
    observability_output_status: passed | warning | failed | blocked | not-applicable
    role_matrix_status: passed | warning | failed | blocked | not-applicable

  generated_artifacts:
    artifact_inventory_status: passed | warning | failed | blocked
    source_model_link_status: passed | warning | failed | blocked
    generator_contract_status: passed | warning | failed | blocked
    generation_mode_status: passed | warning | failed | blocked
    deterministic_diff_status: passed | warning | failed | blocked | not-applicable
    cleanup_regeneration_status: passed | warning | failed | blocked

  runtime_preflight:
    unsupported_capability_status: passed | warning | failed | blocked
    route_port_conflict_status: passed | warning | failed | blocked | not-applicable
    storage_state_conflict_status: passed | warning | failed | blocked | not-applicable
    local_only_value_status: passed | warning | failed | blocked | not-applicable
    runtime_network_exposure_status: passed | warning | failed | blocked | not-applicable

  tasks_and_data_roles:
    task_dependency_ref_status: passed | warning | failed | blocked | not-applicable
    migration_role_status: passed | warning | failed | blocked | not-applicable
    maintenance_role_status: passed | warning | failed | blocked | not-applicable
    read_only_role_status: passed | warning | failed | blocked | not-applicable
    rollback_compensation_status: passed | warning | failed | blocked | not-applicable

  portability_and_stage:
    dependency_portability_status: passed | warning | failed | blocked | not-applicable
    exit_story_status: passed | warning | failed | blocked | not-applicable
    stage_awareness_status: passed | warning | failed | blocked
    promotion_gate_status: passed | warning | failed | blocked | not-applicable

  source_safety:
    sensitivity_class: synthetic | source-derived | operational | tenant-data | secret-adjacent
    raw_value_absence_status: passed | warning | failed | blocked
    private_marker_scan_status: passed | warning | failed | blocked | not-run
    strict_secret_scan_status: passed | warning | failed | blocked | not-run
    raw_source_copy_status: passed | warning | failed | blocked | not-reviewed
    generated_artifact_disclosure_status: safe | redacted | excluded | blocked

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
      - review redacted generated diff
      - draft missing dependency evidence
    forbidden_actions:
      - paste raw credentials, endpoints, private paths or copied source configs
      - claim provider readiness from local generated artifacts alone
    required_approvals:
      - service owner
      - dependency owner
```

## Rules

1. Generated runtime artifacts are evidence outputs, not source of truth.
2. Unknown dependency owner, support owner, secret boundary or portability story
   is warning or blocker, never pass.
3. Local fixture values must be excluded or replaced before private/provider
   readiness.
4. Keep the template independent of any one runtime, generator, language or
   dependency implementation.
