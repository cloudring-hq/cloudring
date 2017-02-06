# Profile Change Record Template

Purpose: record changes to conformance profiles so readiness does not drift or
weaken silently as CloudRING evolves.

```yaml
profile_change_record:
  id: PROFILE-CHANGE-000
  profile_id: profile-id
  from_version: version
  to_version: version
  change_type: add-check | strengthen-check | weaken-check | clarify | deprecate | split-profile | merge-profile
  reason:
    source_signal: anonymized signal or not-applicable
    product_reason: why change is needed
  changed_checks:
    - check_id: CONF-STAGEN-000
      previous_meaning: concise source-safe summary
      new_meaning: concise source-safe summary
      criticality_change: none | weaker | stronger | unknown
  affected_profiles:
    - profile-id
  affected_requirements:
    - CR-...
  compatibility_impact:
    level: none | minor | breaking | unknown
    affected_users:
      - role
    migration_or_rollout_note: how participants adapt
  evidence:
    evidence_bundle_refs:
      - evidence-bundle-id
    validation_summary_ref: safe-reference
  governance:
    owner: role
    approver: role
    review_trigger: date-or-condition
    waiver_needed: true | false
  agent_handoff:
    allowed_actions:
      - action
    forbidden_actions:
      - action
    required_approvals:
      - approval class
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
```

## Stop Conditions

Agent must stop if:

- profile change weakens a hard gate without ADR or owner approval;
- affected profiles/users are unknown;
- compatibility impact is hidden;
- rollout/migration note is missing for breaking change;
- change is source-derived but source-safety review is not passed;
- conformance report claims readiness against a changed profile without
  referencing the change record.
