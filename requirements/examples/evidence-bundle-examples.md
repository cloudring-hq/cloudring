# Synthetic Evidence Bundle Examples

These examples follow
[../templates/evidence-bundle-template.md](../templates/evidence-bundle-template.md).

## Contract Evidence Bundle

```yaml
evidence_bundle:
  id: evidence-bundle-a
  title: Synthetic OCS Contract Evidence
  evidence_class: contract
  scope:
    stage: STAGE-001
    profile_id: stage1-service-ready
    service_or_capability: service-portable-a
    environment_profile: local
  proves:
    - manifest has stable service identity, owner and support owner
    - manifest uses secret references rather than raw secret values
    - generated artifact has provenance and is not source-of-truth
  does_not_prove:
    - runtime execution
    - production readiness
    - full source/history audit
  links:
    requirement_refs:
      - CR-OCSCONTRACT-001..046
      - CR-SPECTPL-019
    check_refs:
      - CONF-STAGE1-001
    adr_refs:
      - ADR-0002
    scenario_refs:
      - SCENARIO-STAGE1-001
  safe_references:
    - examples/ocs-service-manifest-example.md
    - examples/ocs-supporting-contracts-example.md
  owner:
    evidence_owner: org-owner-a
    reviewer: org-owner-a
    approver: org-owner-a
  freshness:
    status: current
    observed_at: synthetic-review-001
    review_trigger: manifest template change
  validation:
    result: passed
    method: manual-review
    summary: source-safe example review passed
  limitations:
    - no real service executed
    - no provider or private presence involved
  retention:
    policy: keep-summary
    reason: reusable product example
  handoff_consequence:
    if_passed: use as example for filling Stage 1 contract evidence
    if_failed: repair example before using template
    if_stale: re-review against latest template
    if_unknown: treat as warning or blocker depending on profile
  source_safety:
    sensitivity_class: public-template
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    reviewer_or_owner: org-owner-a
    stop_if_unknown: true
    raw_match_output_retained: false
```

## Source Coverage Evidence Bundle

```yaml
evidence_bundle:
  id: evidence-bundle-source-coverage-a
  title: Synthetic Source Coverage Evidence
  evidence_class: source-coverage
  scope:
    stage: STAGE-007
    profile_id: stage7-self-evolving-ready
    service_or_capability: requirements memory
    environment_profile: source-memory
  proves:
    - significant source inventory is classified by source class
    - common-noise exclusions are named by category
    - full source/history completion is not claimed
  does_not_prove:
    - every line reviewed
    - every deleted path reviewed
    - vulnerability or secret absence
  links:
    requirement_refs:
      - CR-SRCOV-001..018
      - CR-SPECTPL-009..010
      - CR-SPECEX-008
    check_refs:
      - CONF-STAGE7-011
    adr_refs:
      - ADR-0016
    scenario_refs:
      - SCENARIO-STAGE7-001
  safe_references:
    - examples/source-coverage-manifest-example.md
  owner:
    evidence_owner: org-owner-a
    reviewer: governance-owner-a
    approver: governance-owner-a
  freshness:
    status: current
    observed_at: synthetic-review-001
    review_trigger: source inventory or pass change
  validation:
    result: passed
    method: manual-review
    summary: example preserves non-claims and source safety
  limitations:
    - classification evidence is not full audit evidence
  retention:
    policy: keep-summary
    reason: future source-intake agents need the pattern
  handoff_consequence:
    if_passed: use as source coverage manifest example
    if_failed: block full-coverage claims
    if_stale: refresh inventory counts
    if_unknown: block completion claim
  source_safety:
    sensitivity_class: source-derived
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    reviewer_or_owner: governance-owner-a
    stop_if_unknown: true
    raw_match_output_retained: false
```
