# Stateful Readiness Evidence Example

Synthetic example for
[../templates/stateful-readiness-evidence-template.md](../templates/stateful-readiness-evidence-template.md).

```yaml
stateful_readiness_evidence:
  evidence_id: stateful-readiness-example-a
  date: 2026-06-22
  owner: stateful-operations-owner
  stage_refs:
    - STAGE-002
  profile_refs:
    - stage2-private-presence-ready
  requirement_refs:
    - CR-STATEFULRUN-001..032
  scenario_refs:
    - SCENARIO-STAGE2-004
    - SCENARIO-STAGE2-005

  scope:
    presence_ref: presence-private-a
    service_refs:
      - service-stateful-a
    capability_refs:
      - stateful datastore
    applies_to:
      - backup
      - restore
      - PITR
      - failover

  topology:
    status: warning
    node_classes_status: passed
    failure_domain_status: warning
    quorum_or_consistency_status: warning
    endpoint_ownership_status: warning
    per_node_drift_status: warning

  backup_and_archive:
    backup_identity_status: passed
    backup_freshness_status: warning
    archive_continuity_status: warning
    retention_policy_status: passed
    backup_change_migration_status: warning

  restore_and_pitr:
    restore_target_status: passed
    restore_execution_status: warning
    integrity_check_status: warning
    service_smoke_test_status: warning
    pitr_status: warning
    observed_rpo_status: unknown

  failover:
    drill_status: warning
    endpoint_switch_status: warning
    split_brain_prevention_status: warning
    client_impact_status: unknown
    observed_rto_status: unknown
    rollback_or_compensation_status: warning

  operational_evidence:
    runbook_status: warning
    task_preflight_status: warning
    audit_bundle_status: warning
    critical_findings_status: unknown
    capacity_disk_status: warning
    log_summary_status: passed
    dependency_version_status: warning

  access_and_agent_controls:
    role_matrix_status: warning
    break_glass_status: warning
    agent_action_scope: read-only
    approval_status: not-applicable

  source_and_release_evidence:
    current_tree_status: warning
    history_coverage_status: warning
    deleted_path_theme_status: warning
    repeated_fix_learning_status: warning
    release_provenance_status: warning

  source_safety:
    sensitivity_class: synthetic
    redaction_status: passed
    private_marker_scan_status: passed
    raw_source_copy_status: passed
    topology_disclosure_status: safe

  blockers: []
  warnings:
    - restore and failover are represented as planned evidence, not executed proof
    - RPO and RTO are unknown in this synthetic example
    - history shows repeated audit, backup and HA learning themes that require fixtures
  unresolved_gaps:
    - implementation-backed restore drill evidence is not attached
    - implementation-backed failover drill evidence is not attached
  non_claims:
    - this example does not prove production recovery readiness
    - this example does not certify a specific database, HA or backup stack
  agent_handoff:
    allowed_actions:
      - review evidence
      - draft missing fixture backlog
    forbidden_actions:
      - mutate stateful data, endpoint, backup, restore, failover or access without approval
    required_approvals:
      - stateful operations owner
```
