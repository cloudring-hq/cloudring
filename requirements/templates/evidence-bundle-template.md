# Evidence Bundle Template

Purpose: make evidence references reviewable. A conformance report should not
say only "see evidence"; it should identify what evidence proves, who owns it,
how fresh it is, what it excludes and whether it is safe for humans and agents.

```yaml
evidence_bundle:
  id: EVIDENCE-000
  title: short evidence title
  evidence_class: product-flow | contract | operational | trust | policy | audit | economic | support | portability | experience | agent | source-coverage
  scope:
    stage: STAGE-000 | not-applicable
    profile_id: profile-id-or-none
    service_or_capability: safe identifier
    environment_profile: local | private | provider | federation | global | edge | source-memory
  proves:
    - product claim or check
  does_not_prove:
    - explicit non-claim
  links:
    requirement_refs:
      - CR-...
    check_refs:
      - CONF-...
    adr_refs:
      - ADR-...
    scenario_refs:
      - SCENARIO-...
  safe_references:
    - reference id or relative safe path
  owner:
    evidence_owner: role
    reviewer: role
    approver: role-or-none
  freshness:
    status: current | stale | unknown | contradicted
    observed_at: date-or-build-identity
    review_trigger: date-or-condition
  validation:
    result: passed | failed | warning | blocked | not-run
    method: manual-review | automated-check | agent-review | external-attestation | other
    summary: concise source-safe summary
  limitations:
    - limitation
  retention:
    policy: keep-summary | keep-reference | restricted | delete-after-review
    reason: why
  handoff_consequence:
    if_passed: allowed next action
    if_failed: blocker or remediation
    if_stale: stale behavior
    if_unknown: warning or blocker
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
    raw_match_output_retained: false
```

## Stop Conditions

Agent must stop if:

- evidence has no owner or scope;
- evidence is stale/unknown but check would pass;
- evidence contains private context, secret values, tenant data or copied source;
- evidence cannot state what it does not prove;
- evidence supports data, money, trust or destructive lifecycle action without
  policy/approval link.
