# Billing Runtime Evidence Example

Synthetic example for [../templates/billing-runtime-evidence-template.md](../templates/billing-runtime-evidence-template.md).

```yaml
billing_runtime_evidence:
  evidence_id: billing-runtime-example-a
  date: 2026-06-22
  owner: billing-runtime-owner
  stage_refs:
    - STAGE-004
  profile_refs:
    - stage4-public-provider-ready
  requirement_refs:
    - CR-BILLRUN-001..032
  scenario_refs:
    - SCENARIO-STAGE4-004

  scope:
    provider_or_presence_ref: provider-public-a
    service_refs:
      - service-portable-a
    offer_refs:
      - offer-a
    applies_to:
      - provider-local billing

  usage_contract:
    version: usage-contract-v1
    attribution_status: warning
    resource_lifecycle_status: passed
    unit_period_policy_status: passed
    correction_policy_status: warning
    metadata_policy_status: passed

  intake_result_model:
    receipt_status: passed
    async_status_transitions: warning
    batch_semantics: per-item
    error_envelope_status: passed
    volatile_acceptance_status: volatile-documented

  idempotency_and_identity:
    event_identity_status: passed
    request_idempotency_status: warning
    conflict_detection_status: warning
    replay_duplicate_fixture_status: warning

  operations:
    readiness_status: warning
    access_freshness_status: passed
    backpressure_status: warning
    shutdown_drain_status: warning
    replay_quarantine_status: warning
    observability_status: passed

  release_history:
    release_evidence_status: warning
    history_coverage_status: warning
    repeated_fix_learning_status: warning
    generated_docs_config_status: passed
    test_fixture_backlog_status: warning
    migration_compatibility_status: warning

  settlement_freeze:
    provider_local_status: warning
    cross_participant_status: not-applicable
    dispute_support_status: passed
    party_scope_status: passed

  source_safety:
    redaction_status: passed
    private_marker_scan_status: passed
    raw_source_copy_status: passed

  blockers: []
  warnings:
    - implementation-backed durable outbox evidence is not attached in this synthetic example
    - duplicate idempotency conflict fixture is represented as a planned evidence item
  unresolved_gaps:
    - mixed-version replay simulation is not available in this synthetic example
  non_claims:
    - this example does not prove downstream settlement correctness
    - this example does not certify a production deployment
  agent_handoff:
    allowed_actions:
      - review evidence
      - draft missing fixture backlog
    forbidden_actions:
      - alter invoice, entitlement, settlement, correction or dispute without approval
    required_approvals:
      - billing owner
```
