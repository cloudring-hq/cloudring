# Product Design Quality Review Template

Purpose: prove that a CloudRING flow is understandable, safe, comparable and
operable by a real role and by AI agents. Use this template before a capability
claims product experience readiness.

```yaml
design_quality_review:
  review_id: design-review-000
  title: short task-based review name
  stage: STAGE-000
  capability_refs:
    - capability cluster
  scenario_refs:
    - SCENARIO-STAGEN-000
  requirement_refs:
    - CR-DESIGNQ-001..024
    - CR-UX-001..021
  roles:
    primary: user | admin | developer | ISV | provider | support | governance | agent
    secondary:
      - role
  product_intent:
    role_goal: what the role wants to accomplish
    product_promise: what CloudRING promises for this flow
    anti_lock_in_relevance: choice | portability | local-autonomy | jurisdiction | economics | support | not-applicable
  surfaces_reviewed:
    - UI
    - API
    - CLI
    - Agent API
  consequence_before_action:
    price_or_cost: visible | not-applicable | missing
    provider_chain: visible | not-applicable | missing
    jurisdiction: visible | not-applicable | missing
    policy_decision: allowed | denied | warning | manual-review | not-applicable | unknown
    trust_state: visible | not-applicable | missing
    support_owner: visible | not-applicable | missing
    exit_or_rollback: visible | not-applicable | missing
    data_movement: visible | not-applicable | missing
  choice_and_alternatives:
    recommended_option:
      id: synthetic-option-id
      reason: why this is recommended
    alternatives:
      - id: synthetic-option-id
        status: available | blocked | warning | manual-review
        why_not_recommended: explanation
    hidden_alternative_risk: none | warning | blocker
  provider_economics:
    buyer_visible:
      - price, entitlement or credit fact
    provider_visible:
      - revenue, fee, settlement or obligation fact
    federation_visible:
      - settlement, dispute or audit fact
    confidential_not_exposed:
      - internal fact intentionally not shown
    dispute_or_credit_path: visible | missing | not-applicable
  jurisdiction_overlay:
    data_location: visible | missing | not-applicable
    participant_jurisdiction_class: visible | missing | not-applicable
    policy_overlay_refs:
      - policy id
    fallback_options:
      - option or none
    appeal_path: visible | missing | not-applicable
  failure_and_recovery:
    negative_states_covered:
      - blocked
      - warning
      - manual-review
      - stale
      - degraded
      - disputed
    user_explanation_quality: clear | partial | blocker
    next_action_quality: self-service | support-ready | blocked
    rollback_or_exit_path: visible | missing | not-applicable
    evidence_bundle_refs:
      - evidence id
  human_agent_parity:
    term_parity: passed | warning | failed
    state_parity: passed | warning | failed
    consequence_parity: passed | warning | failed
    remediation_parity: passed | warning | failed
    agent_allowed_actions:
      - action
    agent_forbidden_actions:
      - action
    approval_boundary:
      - approval class
  interaction_quality:
    information_hierarchy: clear | partial | blocker
    stable_layout_or_schema: passed | warning | failed | not-applicable
    text_fit_and_readability: passed | warning | failed | not-applicable
    accessibility_baseline: passed | warning | failed | not-applicable
    progressive_disclosure: passed | warning | failed
    critical_information_hidden_by_decoration: false
  metrics:
    - CR-METRIC-044
    - CR-METRIC-045
  decision:
    status: passed | warning | failed | blocked | manual_review_required
    owner: role or owner id
    reviewer: role or owner id
    unresolved_gaps:
      - gap
    stage7_learning_output: requirement | conformance-check | scenario | runbook | no-change | not-applicable
  validation_summary:
    requirement_link_check: passed | failed | not-run
    scenario_link_check: passed | failed | not-run
    private_marker_scan: passed | failed | not-run
    strict_secret_scan: passed | failed | not-run
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
    raw_source_snippets: false
    private_context: false
```

## Stop Conditions

Agent must stop if:

- consequence before action has missing money, data, jurisdiction, trust,
  support or exit fields for a high-impact flow;
- recommendation has no alternative analysis;
- policy or jurisdiction denial has no safe next action or explicit stop result;
- provider economics review exposes unrelated confidential internals;
- human and agent surfaces disagree about state or allowed action;
- review would include real customer/provider/source material.
