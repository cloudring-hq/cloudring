# Synthetic Controlled Extension And Task Automation Example

This example follows
[../templates/controlled-extension-task-automation-template.md](../templates/controlled-extension-task-automation-template.md).
It uses synthetic objects only and does not prove a real implementation exists.

```yaml
controlled_extension_task_automation_evidence:
  evidence_id: controlled-task-plugin-stage1-a
  stage_scope: Stage 1
  profile_refs:
    - stage1-service-ready
  requirement_refs:
    - CR-EXTAUTO-001..032
  scenario_refs:
    - SCENARIO-STAGE1-008
  workstream_refs:
    - WS-034
  owners:
    automation_owner: service-owner-a
    security_owner: security-owner-a
    service_owner: service-owner-a
    evidence_owner: evidence-owner-a
    approver: service-owner-a
  automation_unit:
    unit_id: local-migration-task-a
    kind: controlled-task
    execution_class: local-developer
    purpose: run a service-owned local schema migration in a portable developer loop
    stage_scope: Stage 1 local profile
    selection_rationale: task is sufficient; plugin is not required
    support_boundary: preview
  trust_and_distribution:
    artifact_ref: task-image-a
    artifact_version: task-image-0.1-example
    immutable_identity_status: warning
    provenance_status: warning
    integrity_status: warning
    version_pin_status: passed
    catalog_status: warning
    offline_private_status: warning
    freshness: current
  execution_boundary:
    capability_scope_status: passed
    workspace_scope: generated local service workspace only
    data_access_class: service-data
    network_access_class: local
    env_redaction_status: passed
    env_export_policy_status: warning
    secret_boundary_status: warning
    argument_schema_status: warning
    working_context_status: passed
    isolation_or_boundary_status: warning
    filesystem_network_policy_status: warning
    runtime_budget_status: warning
  mutation_and_rollback:
    dependency_mutation_status: not-applicable
    boilerplate_generation_status: not-applicable
    affected_file_classes:
      - local database state
      - redacted task log summary
    data_or_state_change_status: warning
    rollback_compensation_status: warning
    update_migration_status: not-applicable
  results_and_conformance:
    structured_result_status: warning
    local_ci_private_parity_status: warning
    managed_runner_boundary_status: warning
    conformance_link_status: warning
    failure_learning_status: passed
    retained_artifacts:
      - redacted-task-result-a
  agent_safety:
    risk_class: controlled-change
    dry_run_status: warning
    approval_status: passed
    allowed_actions:
      - inspect redacted evidence
      - propose safer argument schema
      - draft rollback checklist
    forbidden_actions:
      - run plugin alternative without exception rationale
      - expose raw env or local database endpoint
      - mark provider readiness from local task result
    remaining_gaps:
      - task image integrity is warning in this synthetic example
      - rollback proof is not implementation-backed
  source_safety:
    sensitivity_class: secret-adjacent
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    raw_match_output_retained: false
  non_claims:
    - example does not prove production automation readiness
    - example does not choose final task runner or plugin runtime
    - local task success does not imply private/provider readiness
```

## Non-Claims

- This example is not a final task/plugin schema.
- This example does not include real commands, paths, endpoints, credentials or
  source output.
- Warning statuses are intentional to show honest readiness.
