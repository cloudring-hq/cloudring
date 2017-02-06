# Reference Service Portfolio Evidence Template

Use this template when a stage/profile, source pass, service factory, showcase
suite or provider package claims that a portfolio of reference services is
ready. Fill it with synthetic or source-safe references only.

```yaml
template_id: reference-service-portfolio-evidence
template_version: 0.1
requirement_refs:
  - CR-REFSVC-001..032
  - CR-CAPEVID-040
  - CR-SPECTPL-044
stage_refs:
  - STAGE-001
scenario_refs:
  - SCENARIO-STAGE1-010
workstream_refs:
  - WS-042
conformance_refs:
  - CR-CONF-050

portfolio:
  evidence_id: refsvc-portfolio-YYYY-NNN
  name: synthetic-reference-service-portfolio
  stage_scope: Stage 1
  readiness_claim: candidate | blocked | ready | deprecated
  owner: service-factory-owner-class
  support_owner: support-owner-class
  source_safety_class: public-synthetic | redacted-internal | restricted
  freshness:
    reviewed_at: YYYY-MM-DD
    stale_after_days: 90
    review_trigger:
      - service template changed
      - dependency archetype changed

archetype_registry:
  - archetype: minimal-runtime | documented-service | observable-service | task-data-service | object-artifact-service | secret-store-service | template-baseline
    required_for_stage: true
    covered_by:
      - synthetic service id
    claim_level: docs-only | executable | integration | task | release-candidate | production
    missing_or_gap: null
    non_claims:
      - unsupported claim

service_entries:
  - service_id: svc-synthetic-observable-a
    archetypes:
      - observable-service
    audience:
      - developer
      - service owner
      - support
      - AI agent
    product_purpose: show one coherent observable service behavior
    stage_scope: Stage 1
    readiness_claim: blocked | candidate | ready
    non_goals:
      - production deployment is not proven
    canonical_contract_ref: source-safe manifest/contract id
    capability_refs:
      - CR-WORKFLOW-001..032
      - CR-SVCDEPLOY-001..032
    conformance_refs:
      - stage1-service-ready
    run_modes:
      platform_supported: proven | partial | blocked | not-claimed
      direct_debug: supported-for-debug | unsupported | not-claimed
      generated_artifact_boundary: source-of-truth | derived | local-state
      cleanup_expected: true
    first_useful_behavior:
      intent: source-safe behavior
      input_class: synthetic request/event/task
      expected_result: observable product result
      success_state: lifecycle.ready
      failure_state: lifecycle.blocked
    dependency_evidence:
      - dependency_kind: relational-data-store | object-artifact-store | secret-store | observability-stack | none
        purpose: short purpose
        owner: owner-class
        lifecycle_expectation: create/use/update/delete or not-applicable
        failure_expectation: blocked/degraded behavior
        portability_note: replaceable via capability contract
    docs_evidence:
      overview: filled | placeholder | not-applicable
      interface_contract: filled | placeholder | not-applicable
      architecture: filled | placeholder | not-applicable
      runbook: filled | placeholder | not-applicable
      faq: filled | placeholder | not-applicable
      support_boundary: filled | placeholder | not-applicable
      freshness: current | stale | unknown
    observability_evidence:
      structured_logs: proven | partial | blocked | not-claimed
      metrics: proven | partial | blocked | not-claimed
      traces: proven | partial | blocked | not-claimed
      error_reporting: proven | partial | blocked | not-claimed
      correlation_story: source-safe summary
      metric_cardinality_risk: low | warning | blocked | unknown
    task_evidence:
      task_classes:
        - operational
        - domain
      completion_semantics: proven | partial | blocked | not-applicable
      retry_semantics: proven | partial | blocked | not-applicable
      duplicate_semantics: proven | partial | blocked | not-applicable
      result_object_ref: source-safe result schema id
    data_and_artifact_evidence:
      schema_ownership: proven | partial | blocked | not-applicable
      migration_change_tracking: proven | partial | blocked | not-applicable
      object_lifecycle: proven | partial | blocked | not-applicable
      synthetic_artifact_refs:
        - artifact-synthetic-001
    secret_evidence:
      managed_reference: proven | partial | blocked | not-applicable
      raw_values_absent: true
      rotation_or_degraded_expectation: proven | partial | blocked | not-applicable
    fixtures:
      positive:
        - source-safe fixture id
      negative:
        - source-safe fixture id
    support_handoff:
      diagnostic_summary_ref: source-safe diagnostic id
      owner: support-owner-class
      safe_next_actions:
        - inspect redacted diagnostics
    source_safety:
      private_marker_scan: pass | fail | not-run
      strict_secret_scan: pass | fail | not-run
      copied_source_shape_review: pass | fail | not-run

coverage_matrix:
  rows_reviewed: 0
  archetypes_covered: 0
  required_archetype_gaps:
    - gap id and owner
  composed_behavior_coverage: proven | partial | blocked | not-claimed

agent_handoff:
  allowed_agent_actions:
    - inspect-evidence
    - draft-gap-plan
    - compare-archetype-coverage
  forbidden_agent_actions:
    - run raw commands from old source
    - expose raw environment values
    - claim production readiness without linked release/support/catalog evidence
  required_approvals:
    - owner approval for readiness escalation
  final_evidence_required:
    - portfolio summary
    - coverage matrix
    - blocker list
    - source-safety result

blockers:
  - blocker id, owner, reason, next step

non_claims:
  - production deployment is not proven unless release evidence is linked
  - provider catalog publication is not proven unless catalog evidence is linked
  - portal or UI readiness is not proven unless portal/UI evidence is linked
```

Reviewers must stop if required fields need raw source snippets, private names,
source paths, endpoints, exact commands, raw configuration values, credentials
or copied source shape.
