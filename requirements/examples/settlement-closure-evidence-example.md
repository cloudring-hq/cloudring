# Synthetic Settlement Closure Evidence Example

This example follows
[../templates/settlement-closure-evidence-template.md](../templates/settlement-closure-evidence-template.md).
It uses synthetic objects only and does not prove a real implementation exists.

```yaml
settlement_closure_evidence:
  evidence_id: settlement-closure-q2-a
  stage_scope: Stage 5
  profile_refs:
    - stage5-federation-ready
  requirement_refs:
    - CR-SETTLE-001..032
    - CR-BILLRUN-030..032
  scenario_refs:
    - SCENARIO-STAGE5-006
  workstream_refs:
    - WS-032
  owners:
    evidence_owner: settlement-owner-a
    billing_owner: provider-finance-a
    settlement_owner: federation-settlement-a
    dispute_owner: support-owner-a
    approver: governance-owner-a
  closure_run:
    closure_id: close-federation-q2-a
    status: disputed
    scope: federation
    period: synthetic-quarter-a
    parties:
      - buyer-a
      - provider-a
      - participant-b
      - isv-c
    offers_orders_resources:
      - analytics-service-a usage resources for order-a
    excluded_or_not_applicable:
      - global tax automation is not part of this example
  input_manifest:
    orders_entitlements_ref: synthetic-order-entitlement-a
    usage_receipt_status_ref: billing-runtime-stage4-a
    decision_ledger_ref: decision-ledger-summary-a
    invoice_credit_refund_ref: invoice-draft-a
    disputes_support_policy_ref: dispute-bundle-a
    release_history_ref: release-evidence-a
    generated_docs_config_safety_ref: docs-config-safety-a
    freshness: current
  reconciliation:
    pipeline_stage_comparison: warning
    counts_units_amounts_status: warning
    difference_taxonomy_status: passed
    unresolved_deltas:
      - late-usage-under-review affects one participant share
    late_usage_policy_status: passed
    correction_lineage_status: warning
  freeze_and_outputs:
    freeze_status: blocked
    invoice_trace_status: passed
    credit_refund_trace_status: warning
    participant_share_status: warning
    currency_rounding_status: passed
    tax_regulatory_metadata_status: manual_review_required
  disputes:
    open_disputes:
      - dispute-a
    disputed_amount_status: passed
    hold_release_policy_status: passed
    evidence_bundle_status: passed
    decision_history_status: warning
  party_views_and_exit:
    buyer_view_status: passed
    provider_view_status: passed
    participant_view_status: passed
    agent_view_status: passed
    closeout_export_status: warning
    suspension_cancel_closeout_status: not-applicable
  governance:
    approval_status: warning
    manual_override_status: not-applicable
    release_compatibility_status: warning
    mixed_version_simulation_status: warning
    learning_loop_status: warning
  observability_and_retention:
    blast_radius_status: passed
    aging_and_blocker_metrics_status: warning
    retention_immutability_status: passed
  source_safety:
    sensitivity_class: economic
    redaction_status: safe
    party_scope_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    raw_match_output_retained: false
  non_claims:
    - example does not prove real settlement rail integration
    - example does not provide tax or legal advice
    - example intentionally leaves disputed closure blocked
  agent_handoff:
    allowed_actions:
      - collect missing correction lineage evidence
      - propose dispute decision checklist
      - update synthetic scenario if a new blocker appears
    forbidden_actions:
      - mark closure as settled
      - release disputed participant share
      - include raw source, tenant or credential data
    required_approvals:
      - governance owner approval before closing disputed period
    remaining_gaps:
      - closeout export needs implementation-backed proof
      - mixed-version replay simulation is only represented as warning
```

## Non-Claims

- This example is not an accounting, tax or payment processor design.
- This example does not claim downstream settlement exists in analyzed source.
- Warning and blocked statuses are intentional to show safe refusal.
