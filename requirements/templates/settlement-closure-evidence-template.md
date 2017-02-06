# Settlement Closure Evidence Template

Purpose: capture source-safe evidence that a provider-local or federated billing
period can be financially closed, disputed, corrected, exported and audited.

```yaml
settlement_closure_evidence:
  evidence_id: settlement-closure-evidence-id
  stage_scope: Stage 4 | Stage 5 | Stage 6
  profile_refs:
    - stage4-public-provider-ready
    - stage5-federation-ready
  requirement_refs:
    - CR-SETTLE-001..032
    - CR-BILLRUN-030..032
  scenario_refs:
    - SCENARIO-STAGE5-006
  workstream_refs:
    - WS-032
  owners:
    evidence_owner: role
    billing_owner: role
    settlement_owner: role
    dispute_owner: role
    approver: role
  closure_run:
    closure_id: safe-id
    status: draft | reconciling | blocked | manual-review | closed | reopened | adjusted | voided | disputed | partially-settled | settled
    scope: provider-local | federation | global
    period: safe-period-label
    parties:
      - role-only-or-safe-id
    offers_orders_resources:
      - safe-summary
    excluded_or_not_applicable:
      - item
  input_manifest:
    orders_entitlements_ref: safe-reference
    usage_receipt_status_ref: safe-reference
    decision_ledger_ref: safe-reference
    invoice_credit_refund_ref: safe-reference
    disputes_support_policy_ref: safe-reference
    release_history_ref: safe-reference
    generated_docs_config_safety_ref: safe-reference
    freshness: current | stale | unknown | contradicted
  reconciliation:
    pipeline_stage_comparison: passed | warning | failed | blocked
    counts_units_amounts_status: passed | warning | failed | blocked
    difference_taxonomy_status: passed | warning | failed | blocked
    unresolved_deltas:
      - reason-code-and-safe-summary
    late_usage_policy_status: passed | warning | failed | blocked
    correction_lineage_status: passed | warning | failed | blocked
  freeze_and_outputs:
    freeze_status: passed | warning | failed | blocked | not-run
    invoice_trace_status: passed | warning | failed | blocked
    credit_refund_trace_status: passed | warning | failed | blocked | not-applicable
    participant_share_status: passed | warning | failed | blocked | not-applicable
    currency_rounding_status: passed | warning | failed | blocked | not-applicable
    tax_regulatory_metadata_status: passed | warning | failed | blocked | manual_review_required | not-applicable
  disputes:
    open_disputes:
      - safe-dispute-id
    disputed_amount_status: passed | warning | failed | blocked | not-applicable
    hold_release_policy_status: passed | warning | failed | blocked | not-applicable
    evidence_bundle_status: passed | warning | failed | blocked
    decision_history_status: passed | warning | failed | blocked | not-applicable
  party_views_and_exit:
    buyer_view_status: passed | warning | failed | blocked
    provider_view_status: passed | warning | failed | blocked
    participant_view_status: passed | warning | failed | blocked | not-applicable
    agent_view_status: passed | warning | failed | blocked
    closeout_export_status: passed | warning | failed | blocked
    suspension_cancel_closeout_status: passed | warning | failed | blocked | not-applicable
  governance:
    approval_status: passed | warning | failed | blocked
    manual_override_status: passed | warning | failed | blocked | not-applicable
    release_compatibility_status: passed | warning | failed | blocked
    mixed_version_simulation_status: passed | warning | failed | blocked | not-applicable
    learning_loop_status: passed | warning | failed | blocked
  observability_and_retention:
    blast_radius_status: passed | warning | failed | blocked
    aging_and_blocker_metrics_status: passed | warning | failed | blocked
    retention_immutability_status: passed | warning | failed | blocked
  source_safety:
    sensitivity_class: source-derived | operational | economic | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    party_scope_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    raw_match_output_retained: false
  non_claims:
    - explicit non-claim
  agent_handoff:
    allowed_actions:
      - collect safe evidence
      - propose remediation
    forbidden_actions:
      - close or reopen money without approval
      - include raw source or tenant data
    required_approvals:
      - billing owner approval for close/reopen/credit/refund/settlement release
    remaining_gaps:
      - gap
```

## Rules

1. Treat `unknown` money evidence as blocker or manual review, never as pass.
2. Separate Stage 4 provider-local closure from Stage 5 cross-participant
   settlement.
3. Keep party views scoped and source-safe.
4. Do not store raw source paths, endpoints, credentials, tenant data, exact
   commands, copied docs or raw commit subjects.
