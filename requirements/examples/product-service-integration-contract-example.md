# Product Service Integration Contract Example

This is a source-safe synthetic example. It does not describe a real provider,
endpoint, token, tenant, source path or old implementation.

```yaml
integration_id: integration-usage-product-a
service_ref: service-a
product_identity:
  canonical_id: product-a
  alias_policy: explicit-aliases
  exact_match_required: true
  collision_review_status: passed
capability_target:
  capability: usage
  commercial_impact: billable
profile_scope:
  stage_refs:
    - STAGE-003
  profile_refs:
    - stage3-private-store-ready
  environment_profile: private
owner_refs:
  product_owner: service-owner
  capability_owner: usage-capability-owner
  support_owner: support-owner
  evidence_owner: integration-evidence-owner
requirement_refs:
  - CR-SVCINT-001..032
  - CR-BILLRUN-001..032
  - CR-CATREG-001..032

access_scope:
  credential_class: service-credential
  credential_storage: reference-only
  allowed_products:
    - product-a
  allowed_actions:
    - resource-registration
    - usage-submission
  forbidden_actions:
    - admin-override
    - settlement-close
  freshness:
    source: authoritative-access-state
    last_checked: synthetic-date
    stale_policy: fail-closed
  revocation:
    supported: true
    evidence_ref: evidence-access-revocation-a

resource_lifecycle:
  resources:
    - resource_id: usage-resource-a
      state: registered
      unit_policy: unit-catalog-a
      registration_evidence: evidence-resource-registration-a
      runtime_enforcement_status: warning
  unknown_resource_behavior: quarantine

contract_publication:
  human_onboarding_guide:
    status: passed
    freshness: current
    source_safety: passed
  machine_contract:
    status: passed
    version: integration-contract-v1
    compatibility: compatible
  generated_docs:
    source_of_truth: false
    freshness_status: warning
    generator_identity: api-doc-generator-class
    redaction_status: passed
  drift_check:
    docs_spec_runtime_status: warning
    known_differences:
      - resource-registration behavior is documented but runtime proof is incomplete

submission_semantics:
  result_meaning: accepted-for-processing
  event_identity:
    status: passed
    caller_supplied_supported: true
  idempotency:
    status: warning
    conflict_behavior: return-original
  batch:
    semantics: per-item
    max_safe_batch_note: use small retryable batches until per-item status is proven
  error_model:
    status: passed
    includes_retryability: true
    redaction_status: passed
  receipt:
    status: passed
    support_safe: true

fixtures:
  positive:
    - product-registered-resource-usage
  negative:
    - unauthorized-product
    - unknown-resource
    - stale-credential
    - invalid-period
    - duplicate-conflict
    - oversize-metadata
    - unsupported-version
    - unsafe-example-blocked
  fixture_source_safety: passed

handoff:
  support_boundary: product support owns payload meaning; capability support owns intake state
  diagnostic_bundle_boundary: redacted receipt and status references only
  onboarding_acceptance: warning
  decommission_plan:
    credential_revocation: passed
    resource_retirement: warning
    docs_deprecation: warning
source_safety:
  private_marker_scan: passed
  strict_secret_scan: passed
  copied_source_risk: passed
non_claims:
  - example does not prove downstream financial settlement
  - example does not prove production provider readiness
  - example does not prove full source or git-history coverage
```

## Review Notes

- The integration is useful but not fully ready because runtime resource
  enforcement and decommission evidence are warnings.
- The success state is intentionally limited to accepted-for-processing.
- Generated docs are evidence, not source of truth.
