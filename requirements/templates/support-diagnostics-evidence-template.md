# Support Diagnostics Evidence Template

Use this template when a service, image, stateful operation, release or provider
presence needs a source-safe support diagnostics package for human and AI-agent
triage.

## Manifest

```yaml
support_diagnostics_evidence:
  evidence_id: support-diagnostics-evidence-id
  target:
    object_type: service | image | stateful-operation | provider-operation | release
    object_ref: synthetic-object-id
    profile_refs:
      - stage4-public-provider-ready
    stage_refs:
      - STAGE-004
  owners:
    support_owner: role
    product_owner: role
    platform_owner: role | not-applicable
    evidence_owner: role
  requirement_refs:
    - CR-SUPDIAG-001..032
  conformance_refs:
    - CR-CONF-047
    - CR-CAPEVID-037
  scenario_refs:
    - SCENARIO-STAGE4-007
```

## Lifecycle State

```yaml
lifecycle_state:
  liveness:
    status: passed | warning | failed | blocked | unknown
    meaning: process-alive | unknown
  readiness:
    status: passed | warning | failed | blocked | unknown
    traffic_ready: true | false | unknown
    startup_gate: passed | warning | failed | blocked | unknown
    shutdown_gate: passed | warning | failed | blocked | unknown
  health_components:
    - component_ref: component-a
      class: required | optional | shared-platform | external | unknown
      status: passed | warning | failed | blocked | unknown
      freshness: current | stale | unknown
  drain:
    stop_admission_status: passed | warning | failed | blocked | unknown
    accepted_work_policy: drain | quarantine | discard | unknown
    timeout_policy: explicit | unknown
```

## Correlation And Failure Story

```yaml
correlation:
  correlation_reference:
    status: passed | warning | failed | blocked | unknown
    scope: request | operation | event | incident | unknown
  signal_matrix:
    logs: summary-only | linked | missing | blocked
    traces: summary-only | linked | missing | blocked
    metrics: summary-only | linked | missing | blocked
    event_receipts: summary-only | linked | missing | blocked
  primary_failure_story:
    status: passed | warning | failed | blocked | unknown
    symptom_summary: summary
    affected_component: component-ref | unknown
    issue_classification: service | local-runtime | shared-platform | provider | customer-input | external-dependency | security-review | ambiguous
    recommended_next_action: action-summary
```

## Operational Signals

```yaml
operational_signals:
  error_taxonomy:
    status: passed | warning | failed | blocked | unknown
    classes:
      - authorization
      - validation
      - parse-or-shape
      - dependency
      - overload
      - timeout
      - duplicate-or-retry
      - internal
  retry_duplicate:
    status: passed | warning | failed | blocked | unknown
    duplicate_visible: true | false | unknown
    retention_window: explicit | unknown
  overload_backpressure:
    status: passed | warning | failed | blocked | unknown
    pressure_signal: current | last-known | missing | unknown
    retry_guidance: present | missing | unknown
  async_outcome:
    status: passed | warning | failed | blocked | unknown
    acceptance_not_final_truth: true | false | unknown
```

## Image And Stateful Signals

```yaml
image_and_stateful:
  image:
    applicable: true | false
    boot_readiness_status: passed | warning | failed | blocked | unknown
    seal_cleanup_status: passed | warning | failed | blocked | unknown
    crash_diagnostics_policy: enabled | disabled | approval-required | unknown
    omitted_artifact_classes:
      - class-summary
  stateful_operation:
    applicable: true | false
    operation_type: backup | restore | pitr | failover | audit | unknown
    evidence_class: drill | simulation | live-incident | partial-recovery | unknown
    timeline_status: passed | warning | failed | blocked | unknown
    outcome_status: passed | warning | failed | blocked | unknown
    rollback_or_compensation_status: passed | warning | failed | blocked | unknown
    tenant_impact_summary: summary
```

## Export Control

```yaml
export_control:
  read_only_status: passed | warning | failed | blocked | unknown
  staged_disclosure:
    summary_level: public-support | restricted-support | owner-only
    attachments_level: none | restricted | owner-approved | blocked
    escalation_reason: reason
  approval:
    required: true | false
    status: passed | warning | failed | blocked | unknown
    approver_role: role | not-applicable
  retention:
    policy: short-lived | ticket-bound | fixed-expiry | blocked | unknown
    expiry: synthetic-date | unknown
    deletion_status: pending | complete | not-applicable | unknown
  source_safety:
    private_marker_scan: passed | warning | failed | blocked
    strict_secret_scan: passed | warning | failed | blocked
    copied_source_risk: passed | warning | failed | blocked
    unsafe_attachment_status: passed | warning | failed | blocked
```

## Validation

```yaml
validation:
  diagnostics_contract_tests:
    readiness_health: passed | warning | failed | blocked | unknown
    correlation: passed | warning | failed | blocked | unknown
    error_taxonomy: passed | warning | failed | blocked | unknown
    retry_duplicate: passed | warning | failed | blocked | unknown
    overload_backpressure: passed | warning | failed | blocked | unknown
    drain_shutdown: passed | warning | failed | blocked | unknown
    redaction_export: passed | warning | failed | blocked | unknown
  non_claims:
    - non-claim
```

## Rules

1. Keep diagnostics collection read-only.
2. Prefer summary-level evidence before restricted attachments.
3. Mark missing or unimplemented diagnostics surfaces as warning or blocked.
4. Do not paste real paths, endpoints, hostnames, network literals, credentials,
   commands, source snippets, raw logs, generated examples or tenant data.
