# SCENARIO-STAGE4-009 - Provider Portal Experience Evidence

Проверить, что Stage 4 provider portal доказывает реальные self-service
пути для tenant, provider, support and agent, а не только наличие frontend
bundle, документационной landing page или embedded component.

```yaml
scenario_id: SCENARIO-STAGE4-009
stage: STAGE-004
role: provider-product-owner
secondary_roles:
  - tenant
  - support
  - governance
  - AI agent
user_goal: Prove that provider portal users can discover, inspect, act, stop safely and hand off support with source-safe evidence.
why_it_matters: Public provider readiness needs an operational product surface where consequences, states, owners and evidence are visible before action.
surfaces:
  - UI
  - API
  - CLI
  - Agent API
  - report
requirements:
  - CR-PORTALUX-001..032
  - CR-CAPEVID-039
  - CR-CONF-049
  - CR-SPECTPL-043
  - CR-SPECEX-031
workstreams:
  - WS-041
```

## Preconditions

- A synthetic provider portal evidence package exists.
- A synthetic catalog offer, order preview, support case and billing preview
  exist as source-safe objects.
- The portal surface declares standalone, embedded, documentation and
  production mode claims.
- UI extension/runtime certification and release promotion evidence are linked
  when embedded or shipped behavior is claimed.
- Agent access is review-only unless an explicit approval artifact is present.

## Flow

1. Provider owner opens the portal readiness report and confirms surface
   identity, owner, support boundary, stage scope and role coverage.
2. Tenant starts from an intent such as selecting a portable service, not from
   an internal component name.
3. Portal shows compatible offers with price estimate, provider/presence scope,
   support/SLA boundary, trust/policy summary and exit limitations.
4. Tenant requests an order preview and sees consequence-before-action evidence
   for cost, policy, data movement, support, rollback/exit and approval.
5. A policy warning blocks execution and portal creates a support-ready handoff
   with reason, owner, affected scope, safe next action and case link.
6. Support opens the case view and sees party-scoped context without restricted
   raw diagnostics, private source details or financial data beyond the support
   boundary.
7. Agent reviews the same evidence, drafts a remediation/approval plan and
   stops before executing order, credit, dispute or policy actions.
8. Provider owner reviews portal module contract and sees whether standalone,
   embedded and production modes are proven, blocked or non-claimed.
9. Conformance report records blockers, non-claims, source-safety result and
   next required evidence.

## Expected Evidence

- Portal experience evidence filled from
  [../../templates/portal-experience-evidence-template.md](../../templates/portal-experience-evidence-template.md).
- Synthetic example based on
  [../../examples/portal-experience-evidence-example.md](../../examples/portal-experience-evidence-example.md).
- Role-to-intent journey map for tenant, provider, support and agent.
- UI/API/CLI/Agent API action parity matrix.
- Blocked/degraded/error state evidence with machine-readable state/code,
  owner, next action and support handoff.
- Consequence-before-action evidence for order preview.
- Party-scoped views for tenant, provider, support and governance.
- Portal module contract with mode claims, owner, host surface, context,
  allowed/forbidden actions, lifecycle claims and non-claims.
- Source-safety and strict-secret scan summary.

## Stop Conditions

- Portal readiness is claimed from a blank/demo UI, docs landing or local build
  without role journeys.
- Tenant can confirm an order without visible cost, policy, support/SLA,
  trust, data movement or exit consequences.
- Blocked state lacks owner, reason, safe next action or support-ready handoff.
- Support view leaks restricted tenant, provider, diagnostic or financial
  evidence outside party scope.
- Agent can execute order, credit, dispute, policy or destructive action without
  approval.
- Portal module has no artifact identity, release evidence, host/context
  contract, lifecycle/non-claim record or source-safety result.

## Notes

This scenario proves portal experience evidence for Stage 4 provider readiness.
It does not prove global discovery, multi-provider federation, cross-participant
settlement, final visual design, vulnerability absence or full source/history
coverage.
