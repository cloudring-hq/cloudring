# Stateful Readiness Evidence Template

Use this template when a stage, service, presence or provider claims stateful
restore, PITR, failover, backup, migration or recovery readiness.

```yaml
stateful_readiness_evidence:
  evidence_id: stateful-readiness-evidence-id
  date: YYYY-MM-DD
  owner: stateful-operations-owner
  stage_refs:
    - STAGE-002
  profile_refs:
    - stage2-private-presence-ready
  requirement_refs:
    - CR-STATEFULRUN-001..032
  scenario_refs:
    - SCENARIO-STAGE2-004

  scope:
    presence_ref: presence-id
    service_refs:
      - service-id
    capability_refs:
      - stateful capability
    applies_to:
      - backup
      - restore
      - PITR
      - failover

  topology:
    status: passed | warning | failed | blocked | stale | unknown
    node_classes_status: passed | warning | failed | blocked
    failure_domain_status: passed | warning | failed | blocked
    quorum_or_consistency_status: passed | warning | failed | blocked | not-applicable
    endpoint_ownership_status: passed | warning | failed | blocked
    per_node_drift_status: passed | warning | failed | blocked

  backup_and_archive:
    backup_identity_status: passed | warning | failed | blocked
    backup_freshness_status: passed | warning | failed | blocked | stale
    archive_continuity_status: passed | warning | failed | blocked | not-applicable
    retention_policy_status: passed | warning | failed | blocked
    backup_change_migration_status: passed | warning | failed | blocked | not-applicable

  restore_and_pitr:
    restore_target_status: passed | warning | failed | blocked
    restore_execution_status: passed | warning | failed | blocked | not-run
    integrity_check_status: passed | warning | failed | blocked | not-run
    service_smoke_test_status: passed | warning | failed | blocked | not-run
    pitr_status: passed | warning | failed | blocked | not-applicable
    observed_rpo_status: passed | warning | failed | blocked | unknown

  failover:
    drill_status: passed | warning | failed | blocked | not-run | not-applicable
    endpoint_switch_status: passed | warning | failed | blocked | not-applicable
    split_brain_prevention_status: passed | warning | failed | blocked | not-applicable
    client_impact_status: passed | warning | failed | blocked | unknown
    observed_rto_status: passed | warning | failed | blocked | unknown
    rollback_or_compensation_status: passed | warning | failed | blocked

  operational_evidence:
    runbook_status: passed | warning | failed | blocked | stale
    task_preflight_status: passed | warning | failed | blocked | not-applicable
    audit_bundle_status: passed | warning | failed | blocked
    critical_findings_status: none | warning | blocker | waived | unknown
    capacity_disk_status: passed | warning | failed | blocked
    log_summary_status: passed | warning | failed | blocked
    dependency_version_status: passed | warning | failed | blocked

  access_and_agent_controls:
    role_matrix_status: passed | warning | failed | blocked
    break_glass_status: passed | warning | failed | blocked | not-applicable
    agent_action_scope: read-only | controlled-change | risky-change | emergency
    approval_status: passed | warning | failed | blocked | not-applicable

  source_and_release_evidence:
    current_tree_status: passed | warning | failed | blocked
    history_coverage_status: passed | warning | failed | blocked
    deleted_path_theme_status: passed | warning | failed | blocked
    repeated_fix_learning_status: passed | warning | failed | blocked
    release_provenance_status: passed | warning | failed | blocked

  source_safety:
    sensitivity_class: synthetic | operational | confidential | restricted
    redaction_status: passed | warning | failed | blocked
    private_marker_scan_status: passed | warning | failed | blocked
    raw_source_copy_status: passed | warning | failed | blocked
    topology_disclosure_status: safe | redacted | local-only | blocked

  blockers:
    - blocker
  warnings:
    - warning
  unresolved_gaps:
    - gap
  non_claims:
    - non-claim
  agent_handoff:
    allowed_actions:
      - review evidence
    forbidden_actions:
      - mutate stateful data, endpoint, backup, restore, failover or access without approval
    required_approvals:
      - stateful operations owner
```

## Rules

1. Treat unknown restore, PITR, failover or endpoint evidence as warning or
   blocker, never pass.
2. Do not paste raw inventories, logs, hostnames, addresses, Terraform state,
   grants, credentials, private source paths, source snippets or raw commit
   subjects.
3. Separate backup, restore, PITR and failover statuses.
4. State what the evidence does not prove.
