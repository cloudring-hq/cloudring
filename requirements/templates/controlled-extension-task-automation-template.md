# Controlled Extension And Task Automation Template

Purpose: capture source-safe evidence that a CloudRING task, plugin, dependency
mutation or boilerplate generation flow is governed, portable, trustable and
agent-safe.

```yaml
controlled_extension_task_automation_evidence:
  evidence_id: controlled-automation-evidence-id
  stage_scope: Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 | Stage 6 | Stage 7
  profile_refs:
    - stage1-service-ready
  requirement_refs:
    - CR-EXTAUTO-001..032
  scenario_refs:
    - SCENARIO-STAGE1-008
  workstream_refs:
    - WS-034
  owners:
    automation_owner: role
    security_owner: role
    service_owner: role
    evidence_owner: role
    approver: role
  automation_unit:
    unit_id: safe-id
    kind: core-action | safe-task | controlled-task | plugin | library-mutation | boilerplate-generation
    execution_class: local-developer | managed-runner | ci-like-validation | private-runner | provider-runner
    purpose: safe-summary
    stage_scope: stage-or-profile
    selection_rationale: why-core-task-plugin-or-library
    support_boundary: supported | preview | deprecated | blocked
  trust_and_distribution:
    artifact_ref: safe-reference
    artifact_version: version-or-safe-id
    immutable_identity_status: passed | warning | failed | blocked
    provenance_status: passed | warning | failed | blocked
    integrity_status: passed | warning | failed | blocked
    version_pin_status: passed | warning | failed | blocked
    catalog_status: passed | warning | failed | blocked
    offline_private_status: passed | warning | failed | blocked | not-applicable
    freshness: current | stale | unknown | contradicted
  execution_boundary:
    capability_scope_status: passed | warning | failed | blocked
    workspace_scope: safe-summary
    data_access_class: none | metadata | service-data | tenant-data | unknown
    network_access_class: none | local | private | public | unknown
    env_redaction_status: passed | warning | failed | blocked
    env_export_policy_status: passed | warning | failed | blocked
    secret_boundary_status: passed | warning | failed | blocked
    argument_schema_status: passed | warning | failed | blocked
    working_context_status: passed | warning | failed | blocked
    isolation_or_boundary_status: passed | warning | failed | blocked
    filesystem_network_policy_status: passed | warning | failed | blocked
    runtime_budget_status: passed | warning | failed | blocked
  mutation_and_rollback:
    dependency_mutation_status: passed | warning | failed | blocked | not-applicable
    boilerplate_generation_status: passed | warning | failed | blocked | not-applicable
    affected_file_classes:
      - class
    data_or_state_change_status: passed | warning | failed | blocked | not-applicable
    rollback_compensation_status: passed | warning | failed | blocked
    update_migration_status: passed | warning | failed | blocked | not-applicable
  results_and_conformance:
    structured_result_status: passed | warning | failed | blocked
    local_ci_private_parity_status: passed | warning | failed | blocked
    managed_runner_boundary_status: passed | warning | failed | blocked
    conformance_link_status: passed | warning | failed | blocked
    failure_learning_status: passed | warning | failed | blocked
    retained_artifacts:
      - safe-reference
  agent_safety:
    risk_class: read-only | safe-change | controlled-change | risky-change | destructive | emergency
    dry_run_status: passed | warning | failed | blocked
    approval_status: passed | warning | failed | blocked | not-applicable
    allowed_actions:
      - inspect evidence
      - propose remediation
    forbidden_actions:
      - run untrusted plugin
      - expose raw env, paths, endpoints or secrets
      - mutate dependencies without plan/apply/validate
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

1. Treat unknown plugin/task artifact trust as blocker for readiness.
2. Prefer task/core action evidence over plugin when scope is simple.
3. Do not store raw command output, local paths, private process details,
   endpoints, secrets or source snippets.
4. Mark scaffolded/generated services as candidates until validation evidence
   exists.
