# Portal Experience Evidence Example

This synthetic example shows how a provider portal readiness review can be
filled without using old source files, private names, endpoints or exact
commands.

```yaml
template_id: portal-experience-evidence
template_version: 0.1
example_id: portal-exp-example-001
requirement_refs:
  - CR-PORTALUX-001..032
  - CR-CAPEVID-039
  - CR-SPECTPL-043
  - CR-SPECEX-031
scenario_refs:
  - SCENARIO-STAGE4-009
workstream_refs:
  - WS-041
conformance_refs:
  - CR-CONF-049

surface:
  evidence_id: portal-exp-2026-001
  name: synthetic-provider-portal
  stage_scope: Stage 4
  readiness_claim: blocked
  mode:
    standalone: supported
    embedded: supported
    production: blocked
  owner: provider-product-owner
  support_owner: provider-support-owner
  source_safety_class: public-synthetic

role_coverage:
  - role: tenant
    first_useful_task: choose a portable service offer and inspect consequences before order
    entrypoint: service-catalog
    success_criteria:
      - tenant sees price estimate, support owner, SLA promise, provider scope and exit path before confirmation
    blocker_criteria:
      - offer lacks support boundary or exit limitation
    non_claims:
      - payment settlement is not proven by this journey
  - role: provider
    first_useful_task: publish a candidate offer with visible support and readiness blockers
    entrypoint: provider-offers
    success_criteria:
      - provider sees publication state, missing evidence and next actions
    blocker_criteria:
      - publication depends on a demo-only portal module
    non_claims:
      - multi-provider federation sync is not proven
  - role: agent
    first_useful_task: review portal evidence and draft a safe remediation plan
    entrypoint: evidence-review
    success_criteria:
      - agent can read redacted state and propose next steps without executing high-impact actions
    blocker_criteria:
      - agent is allowed to approve or execute order/credit actions without owner approval
    non_claims:
      - autonomous execution is not proven

journey_map:
  intent: order-service
  prerequisites:
    - catalog record is active
    - support owner is assigned
    - price estimate is fresh
  steps:
    - order: 1
      human_visible_state: Compare compatible offers
      machine_state: discovery.ready
      allowed_surfaces:
        - UI
        - API
        - Agent API
      consequence_summary:
        cost: estimated
        policy: allowed
        trust: known
        support: known
        exit_path: limited
      evidence_refs:
        - catalog-card-evidence-001
      stop_if_unknown:
        - provider support owner
    - order: 2
      human_visible_state: Confirm order consequences
      machine_state: order.awaiting-confirmation
      allowed_surfaces:
        - UI
        - API
        - CLI
        - Agent API
      consequence_summary:
        cost: estimated
        policy: warning
        trust: known
        support: known
        exit_path: limited
      evidence_refs:
        - order-preview-evidence-001
      stop_if_unknown:
        - rollback or cancellation path
    - order: 3
      human_visible_state: Support handoff because policy warning needs owner review
      machine_state: order.blocked.policy-review
      allowed_surfaces:
        - UI
        - API
        - Agent API
      consequence_summary:
        cost: estimated
        policy: warning
        trust: known
        support: known
        exit_path: limited
      evidence_refs:
        - support-handoff-evidence-001
      stop_if_unknown:
        - approval owner

action_parity:
  - action: catalog.offer.compare
    ui_available: true
    api_available: true
    cli_available: false
    agent_api_available: review-only
    result_object_ref: catalog-offer-comparison-result
    unavailable_surface_reason: CLI comparison is a future-stage convenience, not a Stage 4 blocker.
  - action: order.preview
    ui_available: true
    api_available: true
    cli_available: true
    agent_api_available: review-only
    result_object_ref: order-preview-result
    unavailable_surface_reason: null

state_and_error_model:
  states:
    - human_label: Blocked by policy review
      machine_state: policy.blocked.review-required
      owner: governance-owner
      freshness: current
      next_action: request scoped approval
  errors:
    - code: PORTAL_POLICY_REVIEW_REQUIRED
      field_or_surface: order.confirmation
      user_message: Order requires review before execution.
      remediation: Request approval or choose a different offer.
      support_handoff: supported

support_and_billing_links:
  offer_ref: offer-synthetic-portable-a
  order_ref: order-preview-synthetic-001
  instance_ref: not-applicable
  support_case_ref: case-synthetic-001
  diagnostics_ref: not-applicable
  billing_ref: billing-preview-synthetic-001
  settlement_ref: not-applicable
  party_scoped_views:
    tenant_view: price estimate, support owner, SLA label, policy warning and case status
    provider_view: offer readiness, blocked order count, support queue and evidence freshness
    support_view: case context, customer impact, policy warning and safe next actions
    governance_view: approval request, policy reason, affected scope and expiry

portal_module_contract:
  module_identity: portal-module-provider-ordering
  artifact_identity: blocked-until-release-promotion
  release_promotion_ref: blocked
  host_surface: provider-portal-shell
  context_scope: tenant
  allowed_actions:
    - catalog.offer.compare
    - order.preview
    - support.case.create
  forbidden_actions:
    - order.execute-without-approval
    - credit.issue-without-review
  lifecycle_claims:
    mount: proven
    update: partial
    unmount: not-proven
    failure_fallback: proven
  related_ui_certification_ref: ui-cert-synthetic-001

quality_and_access:
  accessibility: partial
  localization: not-claimed
  responsive_behavior: partial
  completion_metrics:
    started_count: synthetic-12
    completed_count: synthetic-7
    blocked_count: synthetic-5
    dropoff_reasons:
      - policy review required
      - exit path limitation unclear

agent_handoff:
  allowed_agent_actions:
    - inspect-evidence
    - draft-remediation-plan
    - prepare-approval-request
  forbidden_agent_actions:
    - execute-order
    - issue-credit
    - approve-policy-exception
  required_approvals:
    - order-execution-approval
    - policy-exception-approval
  final_evidence_required:
    - action summary
    - validation result
    - remaining risk list

validation_summary:
  role_journeys_reviewed: 3
  happy_paths_reviewed: 1
  blocked_paths_reviewed: 1
  degraded_paths_reviewed: 1
  support_handoffs_reviewed: 1
  agent_paths_reviewed: 1
  private_marker_scan: pass
  strict_secret_scan: pass
  copied_source_shape_review: pass

blockers:
  - production release promotion is missing
  - localization evidence is not claimed
  - unmount lifecycle cleanup is not proven

non_claims:
  - production portal readiness is not proven
  - global marketplace readiness is not proven
  - multi-party settlement is not proven
  - security vulnerability absence is not proven
```
