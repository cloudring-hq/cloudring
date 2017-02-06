# Support Diagnostics Evidence Example

This is a source-safe synthetic example. It does not describe a real provider,
tenant, endpoint, source path, log stream, host, command or old implementation.

```yaml
support_diagnostics_evidence:
  evidence_id: support-diagnostics-provider-incident-a
  target:
    object_type: service
    object_ref: service-a
    profile_refs:
      - stage4-public-provider-ready
    stage_refs:
      - STAGE-004
  owners:
    support_owner: support-owner
    product_owner: service-owner
    platform_owner: platform-owner
    evidence_owner: evidence-owner
  requirement_refs:
    - CR-SUPDIAG-001..032
    - CR-BILLRUN-001..032
    - CR-STATEFULRUN-001..032
  conformance_refs:
    - CR-CONF-047
    - CR-CAPEVID-037
  scenario_refs:
    - SCENARIO-STAGE4-007

lifecycle_state:
  liveness:
    status: passed
    meaning: process-alive
  readiness:
    status: warning
    traffic_ready: false
    startup_gate: passed
    shutdown_gate: passed
  health_components:
    - component_ref: intake-component
      class: required
      status: warning
      freshness: current
    - component_ref: shared-observability
      class: shared-platform
      status: passed
      freshness: current
  drain:
    stop_admission_status: passed
    accepted_work_policy: drain
    timeout_policy: explicit

correlation:
  correlation_reference:
    status: passed
    scope: operation
  signal_matrix:
    logs: summary-only
    traces: linked
    metrics: summary-only
    event_receipts: linked
  primary_failure_story:
    status: passed
    symptom_summary: tenant-visible retries increased while new intake was paused
    affected_component: intake-component
    issue_classification: shared-platform
    recommended_next_action: keep service not-ready, drain accepted work, escalate shared dependency owner

operational_signals:
  error_taxonomy:
    status: passed
    classes:
      - authorization
      - validation
      - dependency
      - overload
      - duplicate-or-retry
      - internal
  retry_duplicate:
    status: passed
    duplicate_visible: true
    retention_window: explicit
  overload_backpressure:
    status: warning
    pressure_signal: last-known
    retry_guidance: present
  async_outcome:
    status: passed
    acceptance_not_final_truth: true

image_and_stateful:
  image:
    applicable: false
    boot_readiness_status: unknown
    seal_cleanup_status: unknown
    crash_diagnostics_policy: unknown
    omitted_artifact_classes: []
  stateful_operation:
    applicable: true
    operation_type: failover
    evidence_class: drill
    timeline_status: passed
    outcome_status: warning
    rollback_or_compensation_status: warning
    tenant_impact_summary: synthetic degraded read-only window with no raw topology

export_control:
  read_only_status: passed
  staged_disclosure:
    summary_level: restricted-support
    attachments_level: owner-approved
    escalation_reason: stateful timeline contains sensitive operational context
  approval:
    required: true
    status: warning
    approver_role: support-owner
  retention:
    policy: ticket-bound
    expiry: synthetic-date
    deletion_status: pending
  source_safety:
    private_marker_scan: passed
    strict_secret_scan: passed
    copied_source_risk: passed
    unsafe_attachment_status: warning

validation:
  diagnostics_contract_tests:
    readiness_health: passed
    correlation: passed
    error_taxonomy: passed
    retry_duplicate: passed
    overload_backpressure: warning
    drain_shutdown: passed
    redaction_export: warning
  non_claims:
    - example does not prove live provider root cause
    - example does not prove downstream billing settlement
    - example does not prove production restore or failover completion
    - example does not prove full source or git-history coverage
```

## Review Notes

- The diagnostic package is useful but not fully ready because overload
  freshness, stateful outcome and attachment approval are warnings.
- The package intentionally shows summary-level evidence first.
- No raw logs, commands, hostnames, network literals, source paths or tenant data
  are included.
