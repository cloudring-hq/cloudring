# Service Dependency Deployment Evidence Example

Synthetic example for
[../templates/service-dependency-deployment-evidence-template.md](../templates/service-dependency-deployment-evidence-template.md).

```yaml
service_dependency_deployment_evidence:
  evidence_id: service-dependency-deployment-local-a
  date: 2026-06-22
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
    service_ref: service-portable-a
    source_model_ref: service-model-portable-a
    generator_ref: local-generator-a
    target_profiles:
      - local
    claim_scope:
      proves:
        - local dependency graph is represented as product evidence
        - generated artifacts are traceable and disposable
      does_not_prove:
        - provider-grade deployment readiness
        - live runtime success
        - backup or HA readiness
        - full source-history audit

  effective_service_model:
    identity_status: passed
    profile_resolution_status: passed
    override_consequence_status: warning
    minimal_model_status: draft
    stage_scope_status: passed

  dependency_graph:
    capability_class_status: passed
    instance_identity_status: passed
    service_component_status: passed
    platform_component_status: warning
    external_dependency_status: not-applicable
    startup_readiness_edge_status: warning
    owner_support_status: warning

  connection_outputs:
    output_type_status: passed
    data_classification_status: warning
    redaction_status: passed
    secret_reference_status: warning
    observability_output_status: warning
    role_matrix_status: warning

  generated_artifacts:
    artifact_inventory_status: passed
    source_model_link_status: passed
    generator_contract_status: warning
    generation_mode_status: warning
    deterministic_diff_status: warning
    cleanup_regeneration_status: passed

  runtime_preflight:
    unsupported_capability_status: passed
    route_port_conflict_status: warning
    storage_state_conflict_status: warning
    local_only_value_status: warning
    runtime_network_exposure_status: warning

  tasks_and_data_roles:
    task_dependency_ref_status: warning
    migration_role_status: warning
    maintenance_role_status: warning
    read_only_role_status: warning
    rollback_compensation_status: warning

  portability_and_stage:
    dependency_portability_status: warning
    exit_story_status: warning
    stage_awareness_status: passed
    promotion_gate_status: warning

  source_safety:
    sensitivity_class: synthetic
    raw_value_absence_status: passed
    private_marker_scan_status: passed
    strict_secret_scan_status: passed
    raw_source_copy_status: passed
    generated_artifact_disclosure_status: safe

  blockers: []
  warnings:
    - local generated artifacts are suitable for Stage 1 evidence only
    - dependency role separation and portability are not implementation-backed
    - route and state conflict checks are represented but not executed
  unresolved_gaps:
    - attach implementation-backed generator validation before private readiness
    - attach dependency owner/support matrix before marketplace publication
    - attach export/import or replacement evidence for each stateful dependency
  non_claims:
    - this example does not certify any specific runtime backend
    - this example does not include raw generated env files or credentials
    - this example does not prove live dependency health
  agent_handoff:
    allowed_actions:
      - review redacted generated diff
      - draft missing dependency owner matrix
      - draft portability questions for dependency classes
    forbidden_actions:
      - paste raw credentials, endpoints, private paths or copied source configs
      - claim provider readiness from local generated artifacts alone
    required_approvals:
      - service owner
      - dependency owner
```
