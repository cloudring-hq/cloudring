# Role Scenario Fixture Template

Purpose: define a product scenario in a way that proves CloudRING is usable by
real roles, not only internally coherent. A scenario fixture should be filled
before a capability is called finished for a stage.

```yaml
scenario:
  id: SCENARIO-STAGEN-ROLE-000
  title: short user-intent title
  stage: STAGE-000
  capability_refs:
    - capability cluster
  role:
    primary: user | admin | developer | ISV | provider | support | governance | agent
    secondary:
      - role
  intent:
    user_goal: what the role wants to achieve
    why_it_matters: product reason
    anti_lock_in_relevance: choice | portability | local-autonomy | jurisdiction | technology-refresh | not-applicable
  preconditions:
    - state that must already be true
  trigger:
    - event or action that starts the scenario
  product_flow:
    - step: visible action or decision
      surface: UI | API | CLI | Agent API | report | marketplace | support | other
      expected_state: state family and state
      user_visible_consequence: cost, risk, policy, trust, support or exit impact
      evidence_expected:
        - evidence type
  consequence_before_action:
    price_or_cost: visible | not-applicable | missing
    policy_decision: allowed | denied | warning | manual-review | not-applicable | unknown
    provider_chain: visible | not-applicable | missing
    trust_state: visible | not-applicable | missing
    support_owner: visible | not-applicable | missing
    exit_or_rollback: visible | not-applicable | missing
  success_criteria:
    - observable outcome
  failure_states:
    - state: blocked | degraded | stale | disputed | suspended | unknown
      user_explanation: what user/agent sees
      next_action: retry | choose-alternative | request-approval | contact-support | stop
  stop_condition_cases:
    - case: policy-denied | missing-owner | stale-trust | stale-evidence | unapproved-agent-action | unsupported-portability | duplicate-billing-risk | unsafe-evidence | missing-support-owner
      expected_result: blocked | warning | manual-review | not-applicable
      evidence_expected:
        - evidence type
  evidence:
    requirement_refs:
      - CR-...
    adr_refs:
      - ADR-...
    conformance_refs:
      - profile-id
    metrics:
      - CR-METRIC-...
    audit_events:
      - event class
  agent_boundary:
    risk_class: read-only | safe-change | controlled-change | risky-change | destructive | emergency
    allowed_actions:
      - action
    forbidden_actions:
      - action
    required_approvals:
      - approval class
    validation:
      - check
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
    raw_source_snippets: false
    private_context: false
  non_goals:
    - future-stage or out-of-scope promise
```

## Minimum Role Coverage

| Stage | Required Scenario Coverage |
|---|---|
| Stage 0 | Founder/architect/agent can orient, validate safety and continue source intake. |
| Stage 1 | Developer and agent can create, run, observe, document and validate a service locally. |
| Stage 2 | Admin and agent can install, operate, recover and upgrade a private presence. |
| Stage 3 | Admin/user/ISV/agent can find, verify, install, update and remove service store items. |
| Stage 4 | Provider/tenant/support/agent can onboard, order, bill, operate and handle incidents. |
| Stage 5 | Participants/user/support/governance/agent can sync catalog, settle usage, dispute and run cross-provider operation. |
| Stage 6 | Buyer/provider/ISV/governance/agent can use global discovery, policy, trust, settlement, support and exit without central ownership takeover. |
| Stage 7 | Owner/agent can turn signals into requirements, ADR, runbooks, checks or explicit no-change decisions. |

## Stop Conditions

Agent must stop if:

- scenario cannot name primary role and user intent;
- success requires a future-stage capability without non-goal treatment;
- data movement, money, trust, policy or destructive lifecycle action lacks
  approval boundary;
- user cannot see consequence before action;
- exit, support owner or portability limitation is hidden where relevant;
- scenario fixture would include raw source text, private names, credentials,
  tenant data or internal operational details.
