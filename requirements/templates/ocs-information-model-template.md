# OCS Information Model Template

Purpose: define a versioned product information model for Open Cloud Standard
without choosing a final serialization format. Fill this template when creating
or changing an OCS model version.

```yaml
ocs_information_model:
  model_id: ocs-model-id
  model_version: version
  standard_version: ocs-version
  maturity: draft | candidate | ready | deprecated | blocked
  owner: standard owner role
  decision_refs:
    requirements:
      - CR-OCSIM-001..036
    adr:
      - ADR-0002
    conformance:
      - profile-id
  supported_serializations:
    - name: serialization-name
      status: draft | supported | deprecated | blocked
      round_trip_required: true
  artifact_kinds:
    - kind: service_manifest
      purpose: product purpose
      owner: role
      maturity: draft | ready | deprecated | blocked
      required_sections:
        - section
      allowed_references:
        - target kind
      publishability:
        default: publishable | restricted | local-only | redacted
        purpose: why shared or restricted
      validation_scope:
        - model
        - profile
        - policy
        - extension
        - evidence
  reference_model:
    stable_identity:
      required_fields:
        - kind
        - id
        - model_version
        - owner
    missing_target_behavior: blocked | warning | stale | not-applicable
    version_pin_behavior: exact | compatible-range | latest-with-review
  field_registry:
    version: field-registry-version
    fields:
      - path: artifact.field.path
        artifact_kind: service_manifest
        purpose: why this field exists
        owner: role
        requiredness: required | optional | conditional | extension | deprecated | forbidden
        type_class: string | enum | number | boolean | object | array | reference | policy-expression | evidence-ref
        allowed_values:
          - value
        default:
          class: none | platform-default | profile-default | generated | owner-selected
          source: source of default
          user_visible_consequence: consequence or none
        profile_behavior:
          overridable: true | false
          allowed_profiles:
            - local
            - private
            - provider
            - federation
            - global
            - edge
          precedence: base | profile | owner-override | generated | secret-binding
        compatibility:
          introduced_in: version
          deprecated_in: version-or-none
          compatibility_class: additive | profile-scoped | default-changing | deprecated | breaking | forbidden
          migration_required: true | false
        validation:
          code: OCS-CODE-000
          severity: info | warning | blocker
          owner: role
          retryability: retryable | after-change | not-retryable | unknown
          remediation: user or agent next action
        source_safety:
          publish_boundary: publishable | restricted | local-only | redacted
          secret_class: none | reference-only | secret-adjacent | forbidden-raw
  canonical_core_field_catalog:
    baseline_manifest_fields:
      - family: identity | purpose | profiles | components | dependencies | lifecycle | usage | observability | policy-trust | portability | ui | docs | evidence | source-safety
        product_meaning: why this family exists
        baseline_rule: required | conditional | optional | extension-only | forbidden
        omission_consequence: blocker | warning | not-applicable
        profile_behavior: applies-to-current-stage | applies-to-publication | applies-to-commercial-use | applies-to-federation | applies-to-global
  unknown_field_policy:
    default_behavior: reject | quarantine | extension-only
    extension_namespace_required: true
    evidence_required:
      - namespace owner
      - compatibility impact
      - validation result
  extension_registry:
    - namespace: extension-name
      owner: role
      purpose: why it exists
      lifecycle_state: proposed | active | deprecated | retired | revoked
      scope:
        - artifact kind
      ownership_transfer:
        allowed: true | false
        approval: owner | governance | not-applicable
      mandatory_baseline_constraints:
        - identity cannot be weakened
        - secret handling cannot be weakened
        - policy and evidence cannot be bypassed
      compatibility_class: additive | profile-scoped | default-changing | deprecated | breaking | forbidden
      deprecation:
        path: replacement or none
        removal_rule: migration-required | block-new-use | not-applicable
  validation_catalog:
    version: validation-catalog-version
    codes:
      - code: OCS-CODE-000
        class: model | profile | policy | extension | evidence | source-safety
        field_or_scope: path or scope
        message_key: stable-message-key
        severity: info | warning | blocker
        owner: role
        remediation: next action
        agent_action: continue | collect-evidence | request-approval | stop
  effective_model_report:
    required: true
    includes:
      - defaults
      - profile overrides
      - generated values
      - secret references
      - redacted publishability
      - compatibility decision
  conformance_suite:
    suite_version: ocs-suite-version
    owner: conformance owner role
    model_version_under_test: version
    test_groups:
      - model-header
      - core-field-catalog
      - profile-precedence
      - unknown-fields
      - extension-lifecycle
      - validation-codes
      - effective-model-report
      - generated-artifacts
      - round-trip
      - source-safety
    pass_evidence_required:
      - conformance report
      - validation summary
      - source-safety scan
  model_change_governance:
    schema_governance_record_required: true
    change_record_required_for:
      - default-changing
      - deprecated
      - breaking
      - forbidden
    required_fields:
      - affected kinds
      - affected profiles
      - migration path
      - conformance impact
      - owner approval
      - source-safety review
  validation_summary:
    requirement_link_check: passed | failed | not-run
    round_trip_check: passed | failed | not-run
    unknown_field_policy_check: passed | failed | not-run
    extension_baseline_check: passed | failed | not-run
    private_marker_scan: passed | failed | not-run
    strict_secret_scan: passed | failed | not-run
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
    raw_source_snippets: false
    private_context: false
```

## Stop Conditions

Agent must stop if:

- model version, artifact kind or field registry version is missing;
- an artifact kind has no owner, purpose or validation scope;
- a field has no requiredness, validation code or compatibility class;
- unknown fields are silently accepted;
- an extension can override mandatory identity, secret, policy, billing, trust,
  support, portability or evidence rules;
- default-changing or breaking change has no model change record;
- model artifact includes real source, endpoint, network, provider/customer or
  secret material.
