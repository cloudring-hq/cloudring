# Product Service Integration Contract Template

Use this template when a product service connects to shared CloudRING
capabilities such as catalog, identity, scoped access, usage, support,
documentation or agent-operated lifecycle.

## Identity

```yaml
integration_id: product-service-integration-id
service_ref: service-id
product_identity:
  canonical_id: synthetic-product-id
  alias_policy: none | explicit-aliases | migration-only
  exact_match_required: true
  collision_review_status: passed | warning | failed | blocked
capability_target:
  capability: catalog | usage | entitlement | support | audit | other
  commercial_impact: none | informational | billable | entitlement | settlement
profile_scope:
  stage_refs:
    - STAGE-003
  profile_refs:
    - stage3-private-store-ready
  environment_profile: local | private | provider | federation | global
owner_refs:
  product_owner: role
  capability_owner: role
  support_owner: role
  evidence_owner: role
requirement_refs:
  - CR-SVCINT-001..032
```

## Access Scope

```yaml
access_scope:
  credential_class: service-credential
  credential_storage: reference-only
  allowed_products:
    - synthetic-product-id
  allowed_actions:
    - resource-registration
    - usage-submission
  forbidden_actions:
    - admin-override
    - settlement-close
  freshness:
    source: authoritative-access-state
    last_checked: synthetic-date
    stale_policy: fail-closed | warning | blocked
  revocation:
    supported: true | false | unknown
    evidence_ref: evidence-id
```

## Resource Lifecycle

```yaml
resource_lifecycle:
  resources:
    - resource_id: usage-resource-a
      state: candidate | registered | retired | blocked
      unit_policy: unit-catalog-ref
      registration_evidence: evidence-id
      runtime_enforcement_status: passed | warning | failed | blocked
  unknown_resource_behavior: reject | quarantine | warning | unknown
```

## Contract Publication

```yaml
contract_publication:
  human_onboarding_guide:
    status: passed | warning | failed | blocked
    freshness: current | stale | unknown
    source_safety: passed | warning | failed | blocked
  machine_contract:
    status: passed | warning | failed | blocked
    version: integration-contract-version
    compatibility: compatible | migration-required | deprecated | blocked
  generated_docs:
    source_of_truth: false
    freshness_status: passed | warning | failed | blocked
    generator_identity: generator-id-or-class
    redaction_status: passed | warning | failed | blocked
  drift_check:
    docs_spec_runtime_status: passed | warning | failed | blocked
    known_differences:
      - difference
```

## Submission Semantics

```yaml
submission_semantics:
  result_meaning: accepted-for-processing | final-truth | blocked
  event_identity:
    status: passed | warning | failed | blocked
    caller_supplied_supported: true | false | unknown
  idempotency:
    status: passed | warning | failed | blocked
    conflict_behavior: reject | quarantine | return-original | unknown
  batch:
    semantics: atomic | per-item | unclear | blocked
    max_safe_batch_note: note
  error_model:
    status: passed | warning | failed | blocked
    includes_retryability: true | false | unknown
    redaction_status: passed | warning | failed | blocked
  receipt:
    status: passed | warning | failed | blocked
    support_safe: true | false | unknown
```

## Fixtures

```yaml
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
  fixture_source_safety: passed | warning | failed | blocked
```

## Handoff

```yaml
handoff:
  support_boundary: summary
  diagnostic_bundle_boundary: redacted-summary-only
  onboarding_acceptance: passed | warning | failed | blocked
  decommission_plan:
    credential_revocation: passed | warning | failed | blocked
    resource_retirement: passed | warning | failed | blocked
    docs_deprecation: passed | warning | failed | blocked
source_safety:
  private_marker_scan: passed | warning | failed | blocked
  strict_secret_scan: passed | warning | failed | blocked
  copied_source_risk: passed | warning | failed | blocked
non_claims:
  - non-claim
```

## Rules

1. Treat success as accepted-for-processing unless downstream evidence proves
   stronger truth.
2. Do not paste real endpoint paths, hostnames, credentials, product codes,
   resource codes, commands, source snippets or generated examples.
3. Mark docs/spec/runtime drift as warning or blocker.
4. Keep local/dev confidence separate from private/provider/federation
   readiness.
