# Synthetic OCS Information Model Example

This example follows
[../templates/ocs-information-model-template.md](../templates/ocs-information-model-template.md).
It is synthetic and source-safe. It shows the semantic model shape for a Stage 1
service manifest baseline and one safe extension namespace.

```yaml
ocs_information_model:
  model_id: ocs-model-a
  model_version: ocs-model-0.1-example
  standard_version: ocs-0.1-example
  maturity: candidate
  owner: standard owner
  decision_refs:
    requirements:
      - CR-OCSIM-001..036
      - CR-OCSCONTRACT-001..046
    adr:
      - ADR-0002
    conformance:
      - stage1-service-ready
  supported_serializations:
    - name: structured-manifest-example
      status: draft
      round_trip_required: true
  artifact_kinds:
    - kind: service_manifest
      purpose: describe a service as a portable product contract
      owner: service owner
      maturity: ready
      required_sections:
        - service
        - profiles
        - lifecycle_actions
        - health_observability
        - docs
        - evidence
      allowed_references:
        - dependency_contract
        - profile
        - evidence_bundle
        - ui_descriptor
      publishability:
        default: publishable
        purpose: allow catalog and conformance review without private operational data
      validation_scope:
        - model
        - profile
        - policy
        - evidence
  reference_model:
    stable_identity:
      required_fields:
        - kind
        - id
        - model_version
        - owner
    missing_target_behavior: blocked
    version_pin_behavior: compatible-range
  field_registry:
    version: field-registry-0.1-example
    fields:
      - path: service.id
        artifact_kind: service_manifest
        purpose: stable service identity across catalog, support, billing and portability
        owner: service owner
        requiredness: required
        type_class: string
        allowed_values: []
        default:
          class: none
          source: none
          user_visible_consequence: missing identity blocks readiness
        profile_behavior:
          overridable: false
          allowed_profiles:
            - local
            - private
            - provider
            - federation
            - global
            - edge
          precedence: base
        compatibility:
          introduced_in: ocs-model-0.1-example
          deprecated_in: none
          compatibility_class: forbidden
          migration_required: false
        validation:
          code: OCS-ID-001
          severity: blocker
          owner: service owner
          retryability: after-change
          remediation: add stable service identity before validation can pass
        source_safety:
          publish_boundary: publishable
          secret_class: none
      - path: profiles.secret_references
        artifact_kind: service_manifest
        purpose: bind secret capabilities without storing raw secret values
        owner: security owner
        requiredness: conditional
        type_class: reference
        allowed_values: []
        default:
          class: none
          source: none
          user_visible_consequence: raw secret values are blocked
        profile_behavior:
          overridable: true
          allowed_profiles:
            - local
            - private
            - provider
            - federation
            - global
            - edge
          precedence: secret-binding
        compatibility:
          introduced_in: ocs-model-0.1-example
          deprecated_in: none
          compatibility_class: forbidden
          migration_required: false
        validation:
          code: OCS-SECRET-001
          severity: blocker
          owner: security owner
          retryability: after-change
          remediation: replace raw secret with scoped reference
        source_safety:
          publish_boundary: redacted
          secret_class: reference-only
  canonical_core_field_catalog:
    baseline_manifest_fields:
      - family: identity
        product_meaning: stable service identity and support ownership
        baseline_rule: required
        omission_consequence: blocker
        profile_behavior: applies-to-current-stage
      - family: observability
        product_meaning: health and support evidence for runnable service
        baseline_rule: conditional
        omission_consequence: blocker
        profile_behavior: applies-to-current-stage
      - family: portability
        product_meaning: honest export and migration limits
        baseline_rule: conditional
        omission_consequence: warning
        profile_behavior: applies-to-publication
  unknown_field_policy:
    default_behavior: extension-only
    extension_namespace_required: true
    evidence_required:
      - namespace owner
      - compatibility impact
      - validation result
  extension_registry:
    - namespace: ocs-extension-a
      owner: extension owner
      purpose: add domain-specific display metadata without changing baseline lifecycle
      lifecycle_state: active
      scope:
        - service_manifest
      ownership_transfer:
        allowed: true
        approval: governance
      mandatory_baseline_constraints:
        - identity cannot be weakened
        - secret handling cannot be weakened
        - policy and evidence cannot be bypassed
      compatibility_class: additive
      deprecation:
        path: none
        removal_rule: not-applicable
  validation_catalog:
    version: validation-catalog-0.1-example
    codes:
      - code: OCS-ID-001
        class: model
        field_or_scope: service.id
        message_key: service-id-required
        severity: blocker
        owner: service owner
        remediation: add stable service identity
        agent_action: stop
      - code: OCS-SECRET-001
        class: source-safety
        field_or_scope: profiles.secret_references
        message_key: raw-secret-not-allowed
        severity: blocker
        owner: security owner
        remediation: use scoped secret reference
        agent_action: stop
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
    suite_version: ocs-suite-0.1-example
    owner: conformance owner
    model_version_under_test: ocs-model-0.1-example
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
    requirement_link_check: passed
    round_trip_check: not-run
    unknown_field_policy_check: passed
    extension_baseline_check: passed
    private_marker_scan: passed
    strict_secret_scan: passed
  source_safety:
    sensitivity_class: public-template
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    reviewer_or_owner: standard owner
    stop_if_unknown: true
    raw_source_snippets: false
    private_context: false
```

## Non-Claims

- This example does not choose final serialization.
- This example does not prove parser implementation.
- This example does not replace real conformance execution.
- This example intentionally uses synthetic identifiers only.
