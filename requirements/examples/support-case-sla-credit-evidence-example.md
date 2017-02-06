# Support Case SLA Credit Evidence Example

This is a source-safe synthetic example. It does not describe a real provider,
tenant, endpoint, source path, contact, log stream, invoice or old
implementation.

```yaml
support_case_sla_credit_evidence:
  evidence_id: support-case-sla-credit-provider-incident-a
  case:
    case_id: case-a
    case_type: incident
    profile_refs:
      - stage4-public-provider-ready
    stage_refs:
      - STAGE-004
  requirement_refs:
    - CR-SUPCASE-001..032
    - CR-SUPDIAG-001..032
    - CR-BILLRUN-001..032
    - CR-SETTLE-001..032
  conformance_refs:
    - CR-CONF-048
    - CR-CAPEVID-038
  scenario_refs:
    - SCENARIO-STAGE4-008

case_binding:
  requester:
    role: tenant
    safe_ref: tenant-a
  affected_object:
    offer_ref: offer-a
    order_ref: order-a
    instance_ref: instance-a
    plan_ref: plan-standard
    entitlement_ref: entitlement-a
    profile_ref: stage4-public-provider-ready
  binding_status: passed
  missing_bindings: []

ownership:
  first_line_owner: provider-support
  product_owner: service-owner
  platform_owner: platform-owner
  provider_owner: provider-owner
  isv_owner: not-applicable
  reseller_owner: not-applicable
  evidence_owner: support-evidence-owner
  escalation:
    status: passed
    trigger: severity
  support_boundary:
    classification: shared-platform
    current_owner: platform-owner
    handoff_history_status: passed

service_promise:
  service_card_support_status: passed
  support_scope_status: passed
  runbook_freshness_status: warning
  maintenance_policy_status: passed
  sla_policy:
    status: passed
    target: restoration-time
    measurement_window: synthetic-window
    excluded_states:
      - approved-maintenance
      - waiting-customer
  sla_clock:
    status: warning
    start_rule: explicit
    pause_rules:
      - waiting-customer
      - approved-maintenance
    stop_rule: explicit
    breach_decision: unknown
    approver_role: provider-owner

lifecycle:
  state: credit-review
  severity:
    status: passed
    impact_class: degraded
    escalation_deadline: synthetic-date
  customer_impact:
    status: passed
    summary: service remained available with degraded write throughput for a bounded window
    root_cause_claim: hypothesis
  communication:
    cadence_status: passed
    next_update_due: synthetic-date
    audience: tenant
    stale_status: current
  customer_input:
    required: false
    safe_input_needed: []
    sla_clock_effect: not-applicable

evidence_links:
  diagnostics:
    status: warning
    package_ref: support-diagnostics-provider-incident-a
    issue_classification: shared-platform
  billing_receipt:
    status: passed
    receipt_ref: usage-receipt-a
    accepted_not_final_truth: true
    duplicate_retry_status: passed
  settlement:
    status: warning
    closure_ref: settlement-closure-a
    disputed_amount_hold: active

credit_review:
  requested: true
  status: pending
  policy_status: passed
  eligible_reason: sla-breach
  calculation_evidence_status: warning
  amount_class: restricted
  decision:
    approver_role: provider-owner
    explanation_status: warning
    appeal_path_status: passed
  correction_lineage:
    status: warning
    preserves_settlement_audit: unknown

party_views:
  tenant_view_status: passed
  provider_view_status: passed
  isv_reseller_view_status: not-applicable
  finance_view_status: warning
  governance_view_status: passed
  restricted_attachments_status: owner-approved

source_safety:
  private_marker_scan: passed
  strict_secret_scan: passed
  raw_log_or_source_copy_risk: passed
  unsafe_contact_or_endpoint_status: passed

agent_handoff:
  allowed_actions:
    - draft next tenant update from approved summary
    - request missing settlement correction evidence
    - propose runbook freshness repair
  approval_required_actions:
    - approve credit
    - publish final breach decision
    - release disputed amount hold
  forbidden_actions:
    - change financial record without correction lineage
    - expose restricted diagnostic attachment
    - mark root cause confirmed from hypothesis
  learning_outcome:
    status: pending
    target: runbook
```

## Review Notes

- The case is not ready for final credit approval because SLA breach and
  correction lineage are still warnings.
- The tenant can still receive safe status updates, impact summary and appeal
  path.
- The example separates degraded support experience, diagnostic hypothesis,
  billing receipt and financial settlement.
