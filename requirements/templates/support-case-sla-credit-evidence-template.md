# Support Case SLA Credit Evidence Template

Use this template when a provider, marketplace offer, service instance,
incident, dispute or customer support request needs a source-safe support case
with SLA and credit/refund decision evidence.

## Manifest

```yaml
support_case_sla_credit_evidence:
  evidence_id: support-case-sla-credit-evidence-id
  case:
    case_id: support-case-id
    case_type: incident | request | dispute | credit-review | maintenance-impact | unknown
    profile_refs:
      - stage4-public-provider-ready
    stage_refs:
      - STAGE-004
  requirement_refs:
    - CR-SUPCASE-001..032
  conformance_refs:
    - CR-CONF-048
    - CR-CAPEVID-038
  scenario_refs:
    - SCENARIO-STAGE4-008
```

## Case Binding

```yaml
case_binding:
  requester:
    role: tenant | provider | ISV | reseller | support | finance | governance | AI-agent
    safe_ref: requester-ref
  affected_object:
    offer_ref: offer-a | unknown | not-applicable
    order_ref: order-a | unknown | not-applicable
    instance_ref: instance-a | unknown | not-applicable
    plan_ref: plan-a | unknown | not-applicable
    entitlement_ref: entitlement-a | unknown | not-applicable
    profile_ref: stage4-public-provider-ready | unknown
  binding_status: passed | warning | failed | blocked | unknown
  missing_bindings:
    - binding-name
```

## Ownership And Support Boundary

```yaml
ownership:
  first_line_owner: role
  product_owner: role | not-applicable
  platform_owner: role | not-applicable
  provider_owner: role | not-applicable
  isv_owner: role | not-applicable
  reseller_owner: role | not-applicable
  evidence_owner: role
  escalation:
    status: passed | warning | failed | blocked | unknown
    trigger: severity | stale-update | blocked-evidence | financial-review | security-review | unknown
  support_boundary:
    classification: customer-input | service | local-runtime | shared-platform | provider | ISV | reseller | external-dependency | security-review | ambiguous
    current_owner: role
    handoff_history_status: passed | warning | failed | blocked | unknown
```

## Promise And SLA Clock

```yaml
service_promise:
  service_card_support_status: passed | warning | failed | blocked | unknown
  support_scope_status: passed | warning | failed | blocked | unknown
  runbook_freshness_status: passed | warning | failed | blocked | unknown
  maintenance_policy_status: passed | warning | failed | blocked | not-applicable | unknown
  sla_policy:
    status: passed | warning | failed | blocked | not-applicable | unknown
    target: availability | response-time | restoration-time | custom | not-applicable
    measurement_window: synthetic-window | unknown | not-applicable
    excluded_states:
      - excluded-state
  sla_clock:
    status: passed | warning | failed | blocked | not-applicable | unknown
    start_rule: explicit | unknown | not-applicable
    pause_rules:
      - waiting-customer
      - approved-maintenance
    stop_rule: explicit | unknown | not-applicable
    breach_decision: breached | not-breached | excluded | unknown | not-applicable
    approver_role: role | not-applicable
```

## Lifecycle And Communication

```yaml
lifecycle:
  state: opened | triaged | waiting-customer | waiting-provider | waiting-ISV | in-remediation | workaround | resolved | credit-review | disputed | closed | learning | blocked
  severity:
    status: passed | warning | failed | blocked | unknown
    impact_class: no-impact | degraded | unavailable | data-risk | financial-risk | unknown
    escalation_deadline: synthetic-date | unknown
  customer_impact:
    status: passed | warning | failed | blocked | unknown
    summary: source-safe impact summary
    root_cause_claim: confirmed | hypothesis | unknown | not-claimed
  communication:
    cadence_status: passed | warning | failed | blocked | unknown
    next_update_due: synthetic-date | unknown
    audience: tenant | provider | ISV | support | governance | finance | mixed
    stale_status: current | stale | unknown
  customer_input:
    required: true | false
    safe_input_needed:
      - input-summary
    sla_clock_effect: pauses | does-not-pause | unknown | not-applicable
```

## Evidence Links

```yaml
evidence_links:
  diagnostics:
    status: passed | warning | failed | blocked | not-applicable | unknown
    package_ref: support-diagnostics-evidence-id | not-applicable | unknown
    issue_classification: service | local-runtime | shared-platform | provider | customer-input | external-dependency | security-review | ambiguous | unknown
  billing_receipt:
    status: passed | warning | failed | blocked | not-applicable | unknown
    receipt_ref: usage-receipt-ref | not-applicable | unknown
    accepted_not_final_truth: true | false | unknown | not-applicable
    duplicate_retry_status: passed | warning | failed | blocked | not-applicable | unknown
  settlement:
    status: passed | warning | failed | blocked | not-applicable | unknown
    closure_ref: settlement-closure-ref | not-applicable | unknown
    disputed_amount_hold: active | released | none | unknown | not-applicable
```

## Credit Or Refund Review

```yaml
credit_review:
  requested: true | false
  status: not-requested | pending | approved | denied | partial | disputed | blocked
  policy_status: passed | warning | failed | blocked | not-applicable | unknown
  eligible_reason: sla-breach | goodwill | billing-error | duplicate-usage | maintenance-impact | not-eligible | unknown
  calculation_evidence_status: passed | warning | failed | blocked | not-applicable | unknown
  amount_class: none | small | medium | large | restricted | unknown
  decision:
    approver_role: role | not-applicable
    explanation_status: passed | warning | failed | blocked | unknown
    appeal_path_status: passed | warning | failed | blocked | not-applicable | unknown
  correction_lineage:
    status: passed | warning | failed | blocked | not-applicable | unknown
    preserves_settlement_audit: true | false | unknown | not-applicable
```

## Party Views And Source Safety

```yaml
party_views:
  tenant_view_status: passed | warning | failed | blocked | unknown
  provider_view_status: passed | warning | failed | blocked | unknown
  isv_reseller_view_status: passed | warning | failed | blocked | not-applicable | unknown
  finance_view_status: passed | warning | failed | blocked | not-applicable | unknown
  governance_view_status: passed | warning | failed | blocked | unknown
  restricted_attachments_status: none | owner-approved | blocked | unknown

source_safety:
  private_marker_scan: passed | warning | failed | blocked
  strict_secret_scan: passed | warning | failed | blocked
  raw_log_or_source_copy_risk: passed | warning | failed | blocked
  unsafe_contact_or_endpoint_status: passed | warning | failed | blocked
```

## Agent Handoff

```yaml
agent_handoff:
  allowed_actions:
    - read evidence summary
    - draft customer update
    - propose next diagnostic check
  approval_required_actions:
    - remediation action
    - credit/refund decision
    - public status update
  forbidden_actions:
    - mutate tenant state without approval
    - alter financial record without correction lineage
    - expose restricted attachments
  learning_outcome:
    status: pending | completed | no-change-approved | blocked
    target: requirement | ADR | runbook | scenario | conformance | none
```

## Rules

1. Treat support case evidence as a decision record, not a raw ticket dump.
2. Do not infer SLA breach, credit approval or final settlement from diagnostics
   or intake receipt alone.
3. Use party-scoped summaries before restricted attachments.
4. Mark missing support owner, SLA policy, credit policy, settlement lineage or
   source-safety as warning or blocked.
5. Do not paste real names, source paths, endpoints, network literals,
   credentials, contacts, commands, raw logs, invoice details or source snippets.
