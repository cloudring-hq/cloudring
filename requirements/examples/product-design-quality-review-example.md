# Synthetic Product Design Quality Review Example

This example follows
[../templates/product-design-quality-review-template.md](../templates/product-design-quality-review-template.md).
It is synthetic and source-safe. It demonstrates a Stage 6 jurisdiction and
provider-choice review without defining final UI, pricing formula or policy
engine implementation.

```yaml
design_quality_review:
  review_id: design-review-stage6-jurisdiction-a
  title: Buyer compares global offers with jurisdiction overlay
  stage: STAGE-006
  capability_refs:
    - Global Discovery And Network
    - Policy And Placement
    - Usage Billing And Credits
  scenario_refs:
    - SCENARIO-STAGE6-003
  requirement_refs:
    - CR-DESIGNQ-001..024
    - CR-UX-001..021
    - CR-MKT-001..040
    - CR-FEDGOV-011..021
  roles:
    primary: buyer
    secondary:
      - governance
      - provider
      - agent
  product_intent:
    role_goal: choose a compatible offer that satisfies data-location and budget constraints
    product_promise: compare choices without hiding provider, jurisdiction, trust, support or exit consequences
    anti_lock_in_relevance: jurisdiction
  surfaces_reviewed:
    - UI
    - API
    - CLI
    - Agent API
  consequence_before_action:
    price_or_cost: visible
    provider_chain: visible
    jurisdiction: visible
    policy_decision: warning
    trust_state: visible
    support_owner: visible
    exit_or_rollback: visible
    data_movement: visible
  choice_and_alternatives:
    recommended_option:
      id: offer-public-a
      reason: satisfies policy-profile-a with lower exit friction and current trust evidence
    alternatives:
      - id: offer-public-b
        status: manual-review
        why_not_recommended: jurisdiction class requires owner approval for data movement
      - id: offer-private-a
        status: available
        why_not_recommended: higher cost but stronger local-autonomy profile
    hidden_alternative_risk: none
  provider_economics:
    buyer_visible:
      - monthly plan estimate before order
      - credit path for SLA miss
    provider_visible:
      - settlement share and support obligation
      - dispute evidence requirement
    federation_visible:
      - signed order and settlement event references
    confidential_not_exposed:
      - unrelated provider internal cost model
    dispute_or_credit_path: visible
  jurisdiction_overlay:
    data_location: visible
    participant_jurisdiction_class: visible
    policy_overlay_refs:
      - policy-profile-a
    fallback_options:
      - choose offer-private-a
      - request manual approval for offer-public-b
    appeal_path: visible
  failure_and_recovery:
    negative_states_covered:
      - warning
      - manual-review
      - blocked
      - disputed
    user_explanation_quality: clear
    next_action_quality: self-service
    rollback_or_exit_path: visible
    evidence_bundle_refs:
      - evidence-bundle-design-a
  human_agent_parity:
    term_parity: passed
    state_parity: passed
    consequence_parity: passed
    remediation_parity: passed
    agent_allowed_actions:
      - compare offers
      - prepare approval request
      - generate evidence bundle
    agent_forbidden_actions:
      - approve jurisdiction exception
      - submit commercial order without human approval
    approval_boundary:
      - buyer-owner-approval
      - governance-policy-approval
  interaction_quality:
    information_hierarchy: clear
    stable_layout_or_schema: passed
    text_fit_and_readability: passed
    accessibility_baseline: warning
    progressive_disclosure: passed
    critical_information_hidden_by_decoration: false
  metrics:
    - CR-METRIC-044
    - CR-METRIC-045
    - CR-METRIC-046
    - CR-METRIC-048
    - CR-METRIC-050
  decision:
    status: warning
    owner: governance owner
    reviewer: product owner
    unresolved_gaps:
      - accessibility baseline needs implementation-specific proof
    stage7_learning_output: conformance-check
  validation_summary:
    requirement_link_check: passed
    scenario_link_check: passed
    private_marker_scan: passed
    strict_secret_scan: passed
  source_safety:
    sensitivity_class: public-template
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    reviewer_or_owner: product owner
    stop_if_unknown: true
    raw_source_snippets: false
    private_context: false
```

## Non-Claims

- This is not a final UX design.
- This is not a pricing or legal policy.
- This does not prove an implementation exists.
- The warning is intentional until accessibility and real surface parity are
  proven by implementation evidence.
