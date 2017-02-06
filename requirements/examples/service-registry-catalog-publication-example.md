# Synthetic Service Registry Catalog Publication Example

This example follows
[../templates/service-registry-catalog-publication-template.md](../templates/service-registry-catalog-publication-template.md).
It uses synthetic objects only and does not prove a real implementation exists.

```yaml
service_registry_catalog_publication_evidence:
  evidence_id: registry-publication-stage3-a
  stage_scope: Stage 3
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
    registry_owner: store-owner-a
    service_owner: publisher-isv-a
    publisher_owner: publisher-isv-a
    support_owner: support-owner-a
    evidence_owner: evidence-owner-a
    approver: store-owner-a
  registry_record:
    record_id: service-portable-a-record
    service_identity_status: passed
    uniqueness_scope: private
    namespace_collision_status: passed
    lifecycle_state: warning
    visibility_scope: private-store
    publication_intent: publish a private-ready candidate for controlled install review
    source_manifest_status: passed
    effective_model_status: warning
  catalog_projection:
    card_status: warning
    capability_summary_status: passed
    compatibility_status: passed
    readiness_status: private-ready
    policy_visibility_status: approval-required
    search_index_status: warning
    freshness: current
  publication_plan:
    action: create
    actor_scope_status: passed
    consequence_summary_status: passed
    policy_result_status: warning
    approval_status: passed
    rollback_compensation_status: warning
    affected_users_instances_status: not-applicable
  evidence_links:
    manifest_validation_status: passed
    artifact_inventory_status: warning
    artifact_trust_status: warning
    dependency_deployment_evidence_status: passed
    controlled_automation_evidence_status: warning
    docs_runbook_status: passed
    support_chain_status: passed
    portability_exit_status: warning
  sync_and_cache:
    local_cache_status: passed
    offline_installed_service_status: warning
    sync_ledger_status: warning
    conflict_resolution_status: not-applicable
    global_authority_boundary_status: passed
  agent_safety:
    risk_class: controlled-change
    allowed_actions:
      - inspect registry evidence
      - draft missing artifact trust remediation
      - compare private store alternatives
    forbidden_actions:
      - mark static asset availability as publication readiness
      - expose raw manifest, paths, endpoints, env values or credentials
      - publish without owner approval
    remaining_gaps:
      - artifact trust is warning in this synthetic example
      - offline installed-service behavior needs stronger simulation
  source_coverage:
    source_mode: current-tree
    git_history_status: unavailable
    coverage_non_claims:
      - example does not prove source history coverage
      - example does not prove global marketplace publication
  source_safety:
    sensitivity_class: source-derived
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    raw_match_output_retained: false
  non_claims:
    - static asset distribution is not treated as catalog readiness
    - private-ready record does not imply provider or federation readiness
    - warning statuses are intentional to show honest readiness
```

## Non-Claims

- This example is not a final registry schema.
- This example does not include real paths, endpoints, service names,
  credentials, tenant data or source output.
- Warning statuses are valid when a Stage 3 record is visible only with
  approval and remediation.
