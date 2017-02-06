# Synthetic Developer Workflow Scenario Evidence Example

This example follows
[../templates/developer-workflow-scenario-evidence-template.md](../templates/developer-workflow-scenario-evidence-template.md).
It uses synthetic objects only and does not prove a real implementation exists.

```yaml
developer_workflow_scenario_evidence:
  evidence_id: developer-workflow-stage1-a
  stage_scope: Stage 1
  profile_refs:
    - stage1-service-ready
  requirement_refs:
    - CR-WORKFLOW-001..032
    - CR-SERVICEFACTORY-053
  scenario_refs:
    - SCENARIO-STAGE1-009
  workstream_refs:
    - WS-036
  owners:
    workflow_owner: service-factory-owner-a
    service_owner: service-owner-a
    support_owner: support-owner-a
    evidence_owner: evidence-owner-a
    approver: service-owner-a
  workflow:
    workflow_id: local-service-loop-a
    primary_role: developer
    user_intent: create and debug a portable service candidate with docs and cleanup evidence
    capability_scope:
      - service-factory
      - local-runtime
    maturity: preview
    confidence: run-profile-backed
  prerequisites:
    bootstrap_status: warning
    runtime_profile_status: passed
    config_freshness: current
    required_tools_status: warning
    unsupported_states:
      - full managed start is preview in this synthetic example
  product_steps:
    - step_id: create
      intent: create service candidate from supported template
      surface: CLI
      source_signal_class: docs
      expected_state: draft
      structured_result_status: warning
      source_safety_status: passed
    - step_id: debug
      intent: run dependencies while service process is externally controlled
      surface: CLI
      source_signal_class: run-profile
      expected_state: debug-ready
      structured_result_status: warning
      source_safety_status: passed
    - step_id: docs
      intent: preview support docs locally
      surface: docs
      source_signal_class: docs
      expected_state: docs-ready
      structured_result_status: warning
      source_safety_status: passed
    - step_id: cleanup
      intent: remove local runtime resources without hiding retained state
      surface: CLI
      source_signal_class: docs
      expected_state: cleaned-up
      structured_result_status: warning
      source_safety_status: passed
  negative_cases:
    - case: thin-e2e-only
      expected_result: warning
      remediation_status: passed
    - case: unsupported-mode
      expected_result: blocked
      remediation_status: warning
    - case: unsafe-evidence
      expected_result: blocked
      remediation_status: passed
  cleanup_and_handoff:
    cleanup_status: warning
    retained_state_status: warning
    support_handoff_status: passed
    agent_allowed_actions:
      - inspect redacted workflow evidence
      - propose deeper e2e fixture
      - draft missing structured result contract
    agent_forbidden_actions:
      - expose raw run profile or local endpoint
      - publish personal contact placeholders
      - claim private/provider readiness from local workflow
  linked_evidence:
    lifecycle_command_status: warning
    dependency_deployment_status: passed
    controlled_automation_status: warning
    documentation_memory_status: passed
    bootstrap_activation_status: warning
  source_coverage:
    source_mode: current-tree
    e2e_scope: binary-availability
    coverage_non_claims:
      - example does not prove live local runtime execution
      - example does not prove production or private readiness
  source_safety:
    sensitivity_class: contact-adjacent
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    raw_match_output_retained: false
  non_claims:
    - thin e2e check is scoped to availability only
    - run-profile-backed evidence is not live-run-backed evidence
    - local workflow success does not imply provider readiness
```

## Non-Claims

- This example is not a final workflow schema.
- This example does not include real commands, paths, endpoints, credentials,
  personal contacts, tenant data or source output.
- Warning statuses are intentional to show honest readiness.
