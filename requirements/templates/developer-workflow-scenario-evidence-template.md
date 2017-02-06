# Developer Workflow Scenario Evidence Template

Purpose: capture source-safe evidence that a CloudRING developer workflow is a
real role journey with preconditions, states, negative cases, cleanup and
agent-safe handoff, not only a CLI command or a thin e2e check.

```yaml
developer_workflow_scenario_evidence:
  evidence_id: developer-workflow-evidence-id
  stage_scope: Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 | Stage 6 | Stage 7
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
    workflow_owner: role
    service_owner: role
    support_owner: role
    evidence_owner: role
    approver: role
  workflow:
    workflow_id: safe-id
    primary_role: developer | service-owner | support | AI-agent
    user_intent: safe-summary
    capability_scope:
      - service-factory
      - local-runtime
    maturity: ready | preview | unstable | deprecated | unsupported | blocked
    confidence: docs-only | run-profile-backed | unit-fixture-backed | e2e-backed | live-run-backed | stale | unknown
  prerequisites:
    bootstrap_status: passed | warning | failed | blocked | not-applicable
    runtime_profile_status: passed | warning | failed | blocked
    config_freshness: current | stale | unknown | contradicted
    required_tools_status: passed | warning | failed | blocked
    unsupported_states:
      - safe-summary
  product_steps:
    - step_id: step-1
      intent: safe-summary
      surface: UI | API | CLI | Agent API | report | docs | IDE-profile | other
      source_signal_class: docs | run-profile | unit-fixture | generated-fixture | e2e | live-run | inferred
      expected_state: draft | validated | debug-ready | task-ready | docs-ready | cleaned-up | warning | blocked
      structured_result_status: passed | warning | failed | blocked
      source_safety_status: passed | warning | failed | blocked
  negative_cases:
    - case: invalid-identity | missing-manifest | missing-runtime | unsupported-mode | missing-task | docs-missing | unsafe-evidence | thin-e2e-only
      expected_result: blocked | warning | manual_review_required
      remediation_status: passed | warning | failed | blocked
  cleanup_and_handoff:
    cleanup_status: passed | warning | failed | blocked | not-applicable
    retained_state_status: passed | warning | failed | blocked | not-applicable
    support_handoff_status: passed | warning | failed | blocked
    agent_allowed_actions:
      - inspect evidence
      - propose remediation
    agent_forbidden_actions:
      - run untrusted task/plugin
      - expose raw env, endpoint, local path or personal contact
      - claim production readiness from local workflow
  linked_evidence:
    lifecycle_command_status: passed | warning | failed | blocked
    dependency_deployment_status: passed | warning | failed | blocked | not-applicable
    controlled_automation_status: passed | warning | failed | blocked | not-applicable
    documentation_memory_status: passed | warning | failed | blocked
    bootstrap_activation_status: passed | warning | failed | blocked | not-applicable
  source_coverage:
    source_mode: current-tree | history-focused | sampled | complete | unknown
    e2e_scope: binary-availability | command-behavior | role-journey | negative-case | live-runtime | not-run
    coverage_non_claims:
      - explicit non-claim
  source_safety:
    sensitivity_class: source-derived | operational | secret-adjacent | topology-adjacent | contact-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    raw_match_output_retained: false
  non_claims:
    - explicit non-claim
```

## Rules

1. Do not treat binary availability or command listing as full workflow proof.
2. Keep exact command lines, run profile paths, local endpoints, env values and
   personal contacts out of filled evidence.
3. Mark legacy/preview/unstable workflow states honestly.
4. Link task/plugin workflows to controlled automation evidence.
