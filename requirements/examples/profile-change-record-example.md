# Synthetic Profile Change Record Example

This example follows
[../templates/profile-change-record-template.md](../templates/profile-change-record-template.md).

```yaml
profile_change_record:
  id: PROFILE-CHANGE-001
  profile_id: stage1-service-ready
  from_version: 0.1
  to_version: 0.2-example
  change_type: add-check
  reason:
    source_signal: synthetic role coverage gap
    product_reason: stage readiness should include reusable role scenario evidence
  changed_checks:
    - check_id: CONF-STAGE1-020
      previous_meaning: role scenario coverage was implied by prose scenarios
      new_meaning: role scenario coverage matrix and fixtures are required evidence
      criticality_change: stronger
  affected_profiles:
    - stage1-service-ready
    - stage0-requirements-memory-ready
  affected_requirements:
    - CR-CONF-028
    - CR-CONF-029
    - CR-SPECTPL-022
  compatibility_impact:
    level: minor
    affected_users:
      - developer
      - AI agent
      - profile owner
    migration_or_rollout_note: add or link starter role scenario fixtures before claiming profile pass
  evidence:
    evidence_bundle_refs:
      - evidence-bundle-a
    validation_summary_ref: synthetic-validation-summary
  governance:
    owner: org-owner-a
    approver: governance-owner-a
    review_trigger: new role added to stage profile
    waiver_needed: false
  agent_handoff:
    allowed_actions:
      - add synthetic fixture
      - update role coverage matrix
      - run validation scans
    forbidden_actions:
      - weaken hard gate without ADR
      - mark future-expand as passed
    required_approvals:
      - profile owner approval for breaking change
  source_safety:
    sensitivity_class: public-template
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    reviewer_or_owner: governance-owner-a
    stop_if_unknown: true
```

## Non-Claims

- This example does not change the actual profile version.
- This example shows how a profile change should be recorded when it happens.
