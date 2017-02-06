# Billing Runtime Evidence Template

Use this template when a stage, service, provider or federation participant
claims billable usage readiness.

```yaml
billing_runtime_evidence:
  evidence_id: billing-runtime-evidence-id
  date: YYYY-MM-DD
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
    provider_or_presence_ref: provider-or-presence-id
    service_refs:
      - service-id
    offer_refs:
      - offer-id
    applies_to:
      - provider-local billing
      - federation settlement

  usage_contract:
    version: usage-contract-version
    attribution_status: passed | warning | failed | blocked
    resource_lifecycle_status: passed | warning | failed | blocked
    unit_period_policy_status: passed | warning | failed | blocked
    correction_policy_status: passed | warning | failed | blocked
    metadata_policy_status: passed | warning | failed | blocked

  intake_result_model:
    receipt_status: passed | warning | failed | blocked
    async_status_transitions: passed | warning | failed | blocked
    batch_semantics: atomic | per-item | blocked | unknown
    error_envelope_status: passed | warning | failed | blocked
    volatile_acceptance_status: durable | volatile-documented | failed | blocked

  idempotency_and_identity:
    event_identity_status: passed | warning | failed | blocked
    request_idempotency_status: passed | warning | failed | blocked
    conflict_detection_status: passed | warning | failed | blocked
    replay_duplicate_fixture_status: passed | warning | failed | blocked

  operations:
    readiness_status: passed | warning | failed | blocked
    access_freshness_status: passed | warning | failed | blocked
    backpressure_status: passed | warning | failed | blocked
    shutdown_drain_status: passed | warning | failed | blocked
    replay_quarantine_status: passed | warning | failed | blocked
    observability_status: passed | warning | failed | blocked

  release_history:
    release_evidence_status: passed | warning | failed | blocked
    history_coverage_status: passed | warning | failed | blocked
    repeated_fix_learning_status: passed | warning | failed | blocked
    generated_docs_config_status: passed | warning | failed | blocked
    test_fixture_backlog_status: passed | warning | failed | blocked
    migration_compatibility_status: passed | warning | failed | blocked

  settlement_freeze:
    provider_local_status: passed | warning | failed | blocked | not-applicable
    cross_participant_status: passed | warning | failed | blocked | not-applicable
    dispute_support_status: passed | warning | failed | blocked
    party_scope_status: passed | warning | failed | blocked

  source_safety:
    redaction_status: passed | warning | failed | blocked
    private_marker_scan_status: passed | warning | failed | blocked
    raw_source_copy_status: passed | warning | failed | blocked

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
      - alter invoice, entitlement, settlement, correction or dispute without approval
    required_approvals:
      - billing owner
```

## Rules

1. Treat unknown billing evidence as warning or blocker, never pass.
2. Do not paste payloads, credentials, tenant data, internal hosts, source paths,
   source snippets or raw commit subjects.
3. Separate provider-local billing from cross-participant settlement.
4. Do not claim settlement correctness from intake evidence alone.
