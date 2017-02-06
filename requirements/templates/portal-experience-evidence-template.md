# Portal Experience Evidence Template

Use this template when a stage/profile, product capability, release or source
pass claims that a portal or self-service UI surface is ready. Fill it with
synthetic or source-safe references only.

```yaml
template_id: portal-experience-evidence
template_version: 0.1
requirement_refs:
  - CR-PORTALUX-001..032
  - CR-CAPEVID-039
  - CR-SPECTPL-043
stage_refs:
  - STAGE-004
scenario_refs:
  - SCENARIO-STAGE4-009
workstream_refs:
  - WS-041
conformance_refs:
  - CR-CONF-049

surface:
  evidence_id: portal-exp-YYYY-NNN
  name: synthetic-provider-portal
  stage_scope: Stage 4
  readiness_claim: candidate | blocked | ready | deprecated
  mode:
    standalone: supported | unsupported | docs-only | demo-only
    embedded: supported | unsupported | not-applicable
    production: supported | unsupported | blocked
  owner: product-owner-class
  support_owner: support-owner-class
  source_safety_class: public-synthetic | redacted-internal | restricted

role_coverage:
  - role: tenant | admin | provider | developer | support | governance | agent
    first_useful_task: short intent
    entrypoint: source-safe label
    success_criteria:
      - observable user outcome
    blocker_criteria:
      - condition that stops readiness
    non_claims:
      - what this role coverage does not prove

journey_map:
  intent: order-service | inspect-instance | publish-offer | recover-service | export-data | open-support-case
  prerequisites:
    - prerequisite with owner/status
  steps:
    - order: 1
      human_visible_state: summary label
      machine_state: state-family.code
      allowed_surfaces:
        - UI
        - API
        - CLI
        - Agent API
      consequence_summary:
        cost: known | estimated | not-applicable | unknown
        policy: allowed | denied | warning | unknown
        trust: known | warning | unknown
        support: known | unknown
        exit_path: available | limited | blocked | unknown
      evidence_refs:
        - source-safe evidence id
      stop_if_unknown:
        - field or owner that blocks readiness

action_parity:
  - action: canonical-intent-name
    ui_available: true
    api_available: true
    cli_available: true
    agent_api_available: review-only | executable-with-approval | unavailable
    result_object_ref: source-safe result schema id
    unavailable_surface_reason: null

state_and_error_model:
  states:
    - human_label: Ready
      machine_state: lifecycle.ready
      owner: owner-class
      freshness: current | stale | unknown
      next_action: source-safe action label
  errors:
    - code: PORTAL_SYNTHETIC_ERROR
      field_or_surface: journey.step
      user_message: source-safe summary
      remediation: source-safe next step
      support_handoff: supported | not-required | missing

support_and_billing_links:
  offer_ref: source-safe offer id or not-applicable
  order_ref: source-safe order id or not-applicable
  instance_ref: source-safe instance id or not-applicable
  support_case_ref: source-safe case id or not-applicable
  diagnostics_ref: source-safe diagnostic id or not-applicable
  billing_ref: source-safe billing id or not-applicable
  settlement_ref: source-safe settlement id or not-applicable
  party_scoped_views:
    tenant_view: allowed fields summary
    provider_view: allowed fields summary
    support_view: allowed fields summary
    governance_view: allowed fields summary

portal_module_contract:
  module_identity: source-safe module id
  artifact_identity: immutable artifact id or blocked
  release_promotion_ref: release evidence id or blocked
  host_surface: source-safe host label
  context_scope: tenant | provider | service | support | governance | none
  allowed_actions:
    - action label
  forbidden_actions:
    - action label
  lifecycle_claims:
    mount: proven | not-proven | not-applicable
    update: proven | not-proven | not-applicable
    unmount: proven | not-proven | not-applicable
    failure_fallback: proven | not-proven | not-applicable
  related_ui_certification_ref: UI certification evidence id or not-applicable

quality_and_access:
  accessibility: proven | partial | blocked | not-claimed
  localization: proven | partial | blocked | not-claimed
  responsive_behavior: proven | partial | blocked | not-claimed
  completion_metrics:
    started_count: synthetic-or-aggregated
    completed_count: synthetic-or-aggregated
    blocked_count: synthetic-or-aggregated
    dropoff_reasons:
      - source-safe reason

agent_handoff:
  allowed_agent_actions:
    - inspect-evidence
    - draft-plan
  forbidden_agent_actions:
    - execute-high-impact-action-without-approval
  required_approvals:
    - approval class if execution is requested
  final_evidence_required:
    - summary
    - validation result
    - remaining risks

validation_summary:
  role_journeys_reviewed: 0
  happy_paths_reviewed: 0
  blocked_paths_reviewed: 0
  degraded_paths_reviewed: 0
  support_handoffs_reviewed: 0
  agent_paths_reviewed: 0
  private_marker_scan: pass | fail | not-run
  strict_secret_scan: pass | fail | not-run
  copied_source_shape_review: pass | fail | not-run

blockers:
  - blocker id, owner, reason, next step

non_claims:
  - live production portal readiness is not proven unless release evidence is linked
  - docs-only navigation is not operational self-service proof
  - embedded runtime certification is not proven unless UI certification evidence is linked
```

Reviewers must stop if required fields need raw source snippets, private
operational names, endpoints, exact commands, secrets or copied source shape.
