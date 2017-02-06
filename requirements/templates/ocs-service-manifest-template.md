# OCS Service Manifest Template

Purpose: define a service as a CloudRING product contract that can move from
local development to private, provider, federation and global scopes without
copying old source structures.

This template is product-level. A future ADR may choose a concrete serialization
format. Field names below are semantic placeholders.

```yaml
manifest:
  standard_version: ocs-version
  manifest_maturity: draft | ready | preview | deprecated | blocked
  service:
    id: stable-service-id
    name: human-name
    purpose: product outcome
    owner: role-or-organization-boundary
    publisher: role-or-organization-boundary
    support_owner: role
    tenant_scope: single-tenant | multi-tenant | dedicated | shared | unknown
    lifecycle_state: draft | candidate | active | updating | suspended | retired
  users:
    - role
  product_promises:
    - what user can rely on
  non_goals:
    - what this service does not claim
  requirements:
    requirement_refs:
      - CR-...
    adr_refs:
      - ADR-...
    conformance_refs:
      - profile-id
  capability:
    required:
      - capability name
    optional:
      - capability name
    unsupported:
      - capability name with visible consequence
    extensions:
      - namespace, owner, compatibility impact
  profiles:
    - profile_id: local | private | provider | federation | global | edge
      status: supported | degraded | unsupported | blocked | unknown
      overrides:
        public_values:
          - name and purpose
        secret_references:
          - reference name, owner, scope
        generated_values:
          - name, generator, freshness
      policy:
        data_classes:
          - class name
        allowed_locations:
          - policy expression
        forbidden_locations:
          - policy expression
        required_approvals:
          - approval class
  components:
    - id: component-id
      role: api | worker | ui | database | cache | queue | storage | custom
      owner: role
      lifecycle: managed | external | manual-review | unsupported
      readiness:
        health: declared | not-applicable | unknown
        observability: declared | limited | missing
  dependencies:
    - id: dependency-id
      capability: capability name
      connection_contract:
        outputs:
          - output name and class
        secret_boundary: reference-only | brokered | not-required
        degraded_state: consequence
        fallback: supported | manual | none
        owner: role
  lifecycle_actions:
    - action: validate | publish | order | provision | update | suspend | resume | remove | export | migrate
      risk_class: read-only | safe-change | controlled-change | risky-change | destructive | emergency
      idempotency: required | not-applicable | explicit-repeat-consequence
      approval: none | owner | policy | dual-control
      result_shape: standard lifecycle result
  usage:
    resources:
      - id: usage-resource-id
        unit: product unit
        scope: service | instance | tenant | participant
        billing_relevance: billable | informational | non-commercial
        exclusions:
          - excluded condition
  health_observability:
    health: endpoint-or-contract-purpose
    readiness: endpoint-or-contract-purpose
    metrics:
      - metric purpose
    logs:
      - class, retention, redaction
    traces:
      - correlation purpose
    events:
      - lifecycle, audit or usage event
  policy_and_trust:
    placement_constraints:
      - policy constraint
    data_residency:
      - declared rule
    audit_requirements:
      - audit event class
    certification_state: dev | private-ready | public-ready | federation-ready | global-ready | blocked
    trust_state: trusted | degraded | disputed | revoked | unknown
  portability:
    status: automated | assisted | manual | export-only | blocked | non-portable | unknown
    exportable_data:
      - data class
    exportable_metadata:
      - metadata class
    restore_or_import_story: evidence reference or limitation
    compatible_targets:
      - target class
    known_limits:
      - limitation
  ui:
    embed_mode: none | standalone | host-controlled | both
    descriptor_ref: safe-reference
    scoped_context:
      - field and permission class
    allowed_actions:
      - action
    support_owner: role
  docs:
    overview: safe-reference
    api_contract: safe-reference
    architecture: safe-reference
    runbook: safe-reference
    faq: safe-reference
    known_limits: safe-reference
  generated_artifacts:
    - id: artifact-id
      source_of_truth: manifest-field-or-contract
      generator: generator identity
      target_profile: profile-id
      freshness: current | stale | unknown
      publish_boundary: publishable | local-only | ignored | restricted
      cleanup_rule: required | not-applicable | unknown
  evidence:
    conformance_report: safe-reference
    validation_summary: safe-reference
    source_safety: passed | warning | blocked | not-run
    evidence_owner: role
    review_trigger: date-or-condition
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
```

## Required Checks

| Check | Blocks If |
|---|---|
| Stable identity | Service lacks stable id, owner or support owner. |
| Secret boundary | Plain secret values appear in manifest, generated artifacts, logs or agent context. |
| Lifecycle result | Actions cannot produce standard result with state, evidence and next actions. |
| Dependencies | Dependency connection requires manual hidden setup. |
| Observability | Runnable service lacks health/readiness and supportable telemetry. |
| Policy | Placement/data movement can happen without policy decision. |
| Portability | Marketplace/order flow claims portability without evidence or limitation. |
| Generated artifacts | Derived files become source-of-truth or lack provenance/freshness. |
| Source safety | Manifest includes private source context, copied snippets or raw operational details. |
