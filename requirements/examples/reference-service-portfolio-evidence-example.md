# Reference Service Portfolio Evidence Example

This synthetic example shows how to review a reference service portfolio without
using old source files, private names, endpoints, exact commands, raw config or
real credentials.

```yaml
template_id: reference-service-portfolio-evidence
template_version: 0.1
example_id: refsvc-portfolio-example-001
requirement_refs:
  - CR-REFSVC-001..032
  - CR-CAPEVID-040
  - CR-SPECTPL-044
  - CR-SPECEX-032
scenario_refs:
  - SCENARIO-STAGE1-010
workstream_refs:
  - WS-042
conformance_refs:
  - CR-CONF-050

portfolio:
  evidence_id: refsvc-portfolio-2026-001
  name: synthetic-reference-service-portfolio
  stage_scope: Stage 1
  readiness_claim: blocked
  owner: service-factory-owner
  support_owner: platform-support-owner
  source_safety_class: public-synthetic
  freshness:
    reviewed_at: 2026-06-22
    stale_after_days: 90
    review_trigger:
      - service template changed
      - reference archetype added

archetype_registry:
  - archetype: minimal-runtime
    required_for_stage: true
    covered_by:
      - svc-synthetic-minimal-a
    claim_level: executable
    missing_or_gap: null
    non_claims:
      - production deployment is not proven
  - archetype: documented-service
    required_for_stage: true
    covered_by:
      - svc-synthetic-documented-a
    claim_level: docs-only
    missing_or_gap: runbook and API pages still need filled product content
    non_claims:
      - docs scaffold is not docs readiness
  - archetype: observable-service
    required_for_stage: true
    covered_by:
      - svc-synthetic-observable-a
    claim_level: executable
    missing_or_gap: null
    non_claims:
      - support SLA is not proven
  - archetype: task-data-service
    required_for_stage: true
    covered_by:
      - svc-synthetic-task-data-a
    claim_level: task
    missing_or_gap: duplicate task behavior is partial
    non_claims:
      - production migration policy is not proven
  - archetype: object-artifact-service
    required_for_stage: true
    covered_by:
      - svc-synthetic-object-a
    claim_level: integration
    missing_or_gap: retention policy is not yet proven
    non_claims:
      - provider object storage readiness is not proven
  - archetype: secret-store-service
    required_for_stage: true
    covered_by:
      - svc-synthetic-secret-a
    claim_level: integration
    missing_or_gap: rotation drill is blocked
    non_claims:
      - production credential runtime readiness is not proven

service_entries:
  - service_id: svc-synthetic-observable-a
    archetypes:
      - observable-service
    audience:
      - developer
      - service owner
      - support
      - AI agent
    product_purpose: prove one request can be understood through logs, metrics, traces and error summary
    stage_scope: Stage 1
    readiness_claim: candidate
    non_goals:
      - production deployment is not proven
      - public provider publication is not proven
    canonical_contract_ref: contract-synthetic-observable-a
    capability_refs:
      - CR-WORKFLOW-001..032
      - CR-SVCDEPLOY-001..032
      - CR-SUPDIAG-001..032
    conformance_refs:
      - stage1-service-ready
    run_modes:
      platform_supported: partial
      direct_debug: supported-for-debug
      generated_artifact_boundary: derived
      cleanup_expected: true
    first_useful_behavior:
      intent: calculate a synthetic result and emit a correlated outcome
      input_class: synthetic request
      expected_result: result plus observable correlation summary
      success_state: lifecycle.ready
      failure_state: lifecycle.blocked
    dependency_evidence:
      - dependency_kind: observability-stack
        purpose: correlate one request across service signals
        owner: observability-owner
        lifecycle_expectation: use-only in Stage 1
        failure_expectation: service stays usable but readiness warning appears
        portability_note: replaceable through observability capability contract
    docs_evidence:
      overview: filled
      interface_contract: filled
      architecture: partial
      runbook: partial
      faq: placeholder
      support_boundary: filled
      freshness: current
    observability_evidence:
      structured_logs: proven
      metrics: proven
      traces: partial
      error_reporting: partial
      correlation_story: one synthetic operation can be followed from request to support summary
      metric_cardinality_risk: low
    task_evidence:
      task_classes: []
      completion_semantics: not-applicable
      retry_semantics: not-applicable
      duplicate_semantics: not-applicable
      result_object_ref: not-applicable
    data_and_artifact_evidence:
      schema_ownership: not-applicable
      migration_change_tracking: not-applicable
      object_lifecycle: not-applicable
      synthetic_artifact_refs: []
    secret_evidence:
      managed_reference: not-applicable
      raw_values_absent: true
      rotation_or_degraded_expectation: not-applicable
    fixtures:
      positive:
        - fixture-observable-success-001
      negative:
        - fixture-observable-backend-unavailable-001
    support_handoff:
      diagnostic_summary_ref: diag-synthetic-observable-001
      owner: platform-support-owner
      safe_next_actions:
        - inspect redacted correlation summary
        - compare metric success and failure counts
    source_safety:
      private_marker_scan: pass
      strict_secret_scan: pass
      copied_source_shape_review: pass

coverage_matrix:
  rows_reviewed: 6
  archetypes_covered: 6
  required_archetype_gaps:
    - documented service has placeholder FAQ
    - secret-store service lacks rotation drill
    - object-artifact service lacks retention proof
  composed_behavior_coverage: partial

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
    - service-factory-owner-readiness-approval
  final_evidence_required:
    - portfolio summary
    - coverage matrix
    - blocker list
    - source-safety result

blockers:
  - docs scaffold still contains placeholder sections
  - secret rotation evidence is missing
  - catalog publication evidence is not linked

non_claims:
  - production deployment is not proven
  - provider catalog publication is not proven
  - portal readiness is not proven
  - security vulnerability absence is not proven
  - full source/history coverage is not proven
```
