# Service Registry Catalog Publication Template

Purpose: capture source-safe evidence that a CloudRING service registry record,
catalog card or publication operation is product-ready, lifecycle-aware and
safe for human and AI-agent review.

```yaml
service_registry_catalog_publication_evidence:
  evidence_id: registry-publication-evidence-id
  stage_scope: Stage 3 | Stage 4 | Stage 5 | Stage 6 | Stage 7
  profile_refs:
    - stage3-private-store-ready
  requirement_refs:
    - CR-CATREG-001..032
    - CR-CATALOG-029
  scenario_refs:
    - SCENARIO-STAGE3-006
  workstream_refs:
    - WS-035
  owners:
    registry_owner: role
    service_owner: role
    publisher_owner: role
    support_owner: role
    evidence_owner: role
    approver: role
  registry_record:
    record_id: safe-id
    service_identity_status: passed | warning | failed | blocked
    uniqueness_scope: local | private | provider | federation | global
    namespace_collision_status: passed | warning | failed | blocked
    lifecycle_state: candidate | visible | install-ready | warning | blocked | suspended | deprecated | unpublished | removed
    visibility_scope: private-internal | private-store | provider-local | federation | global
    publication_intent: safe-summary
    source_manifest_status: passed | warning | failed | blocked
    effective_model_status: passed | warning | failed | blocked
  catalog_projection:
    card_status: passed | warning | failed | blocked
    capability_summary_status: passed | warning | failed | blocked
    compatibility_status: passed | warning | failed | blocked
    readiness_status: candidate | dev-only | private-ready | public-ready | federation-ready | global-ready | blocked
    policy_visibility_status: allowed | hidden | blocked | warning | approval-required | manual-review
    search_index_status: passed | warning | failed | blocked
    freshness: current | stale | unknown | contradicted
  publication_plan:
    action: create | update | suspend | deprecate | unpublish | remove | import | sync
    actor_scope_status: passed | warning | failed | blocked
    consequence_summary_status: passed | warning | failed | blocked
    policy_result_status: passed | warning | failed | blocked
    approval_status: passed | warning | failed | blocked | not-applicable
    rollback_compensation_status: passed | warning | failed | blocked
    affected_users_instances_status: passed | warning | failed | blocked | not-applicable
  evidence_links:
    manifest_validation_status: passed | warning | failed | blocked
    artifact_inventory_status: passed | warning | failed | blocked
    artifact_trust_status: passed | warning | failed | blocked
    dependency_deployment_evidence_status: passed | warning | failed | blocked
    controlled_automation_evidence_status: passed | warning | failed | blocked | not-applicable
    docs_runbook_status: passed | warning | failed | blocked
    support_chain_status: passed | warning | failed | blocked
    portability_exit_status: passed | warning | failed | blocked
  sync_and_cache:
    local_cache_status: passed | warning | failed | blocked | not-applicable
    offline_installed_service_status: passed | warning | failed | blocked | not-applicable
    sync_ledger_status: passed | warning | failed | blocked | not-applicable
    conflict_resolution_status: passed | warning | failed | blocked | not-applicable
    global_authority_boundary_status: passed | warning | failed | blocked | not-applicable
  agent_safety:
    risk_class: read-only | safe-change | controlled-change | risky-change | destructive | emergency
    allowed_actions:
      - inspect registry evidence
      - propose publication remediation
    forbidden_actions:
      - publish from static asset or debug success alone
      - expose raw source paths, endpoints, env values or credentials
      - make global registry authoritative over local lifecycle
    remaining_gaps:
      - gap
  source_coverage:
    source_mode: current-tree | history-focused | sampled | complete | unknown
    git_history_status: available | unavailable | partial | not-reviewed
    coverage_non_claims:
      - explicit non-claim
  source_safety:
    sensitivity_class: source-derived | operational | secret-adjacent | topology-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    raw_match_output_retained: false
  non_claims:
    - explicit non-claim
```

## Rules

1. Treat registry rows, static assets and local manifest discovery as inputs,
   not publication proof.
2. Keep source references safe and generic; do not store old paths, service
   names, URLs, endpoints, commands, env output or snippets.
3. Mark current-tree-only evidence as current-tree-only.
4. Publication changes installability, support or visibility only after plan,
   policy and approval evidence is recorded.
