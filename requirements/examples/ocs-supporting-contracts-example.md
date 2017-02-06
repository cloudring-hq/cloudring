# Synthetic OCS Supporting Contracts Example

This filled example complements
[ocs-service-manifest-example.md](ocs-service-manifest-example.md) and follows
[../templates/ocs-supporting-contract-templates.md](../templates/ocs-supporting-contract-templates.md).

## Manifest Field Matrix Example

```yaml
manifest_field_matrix:
  standard_version: ocs-0.1-example
  matrix_version: matrix-0.1-example
  fields:
    - path: service.id
      purpose: stable service identity across catalog, lifecycle and evidence
      owner: service-owner
      status: required
      type: stable identifier
      default:
        value_class: none
        user_visible_consequence: service cannot be validated without identity
      profile_behavior:
        local: required
        private: required
        provider: required
        federation: required
        global: required
      validation:
        rule_id: ocs-service-id-required
        machine_code: OCS-ID-001
        severity: error
        remediation: choose stable service id before runtime execution
      compatibility:
        introduced_in: ocs-0.1-example
        deprecated_in: none
        breaking_change_if_removed: true
      source_safety:
        may_contain_secret: false
        may_contain_private_context: false
        redaction_required: false
    - path: profiles.secret_references
      purpose: bind secrets by reference without raw value transfer
      owner: platform
      status: required when service needs secrets
      type: list of secret references
      default:
        value_class: none
        user_visible_consequence: service starts only when brokered binding is available
      profile_behavior:
        local: optional
        private: required
        provider: required
        federation: required
        global: required
      validation:
        rule_id: ocs-secret-reference-only
        machine_code: OCS-SEC-001
        severity: error
        remediation: replace raw value with brokered secret reference
      compatibility:
        introduced_in: ocs-0.1-example
        deprecated_in: none
        breaking_change_if_removed: true
      source_safety:
        may_contain_secret: false
        may_contain_private_context: true
        redaction_required: true
```

## Environment And Profile Precedence Example

```yaml
environment_profile_precedence:
  service_id: service-portable-a
  standard_version: ocs-0.1-example
  layers:
    - name: base
      purpose: common product contract
      may_contain_secret_values: false
    - name: profile
      purpose: private/local/provider differences
      may_contain_secret_values: false
    - name: generated
      purpose: platform-derived runtime values with provenance
      may_contain_secret_values: false
    - name: secret_binding
      purpose: brokered secret references only
      may_contain_secret_values: false
  precedence_rules:
    - profile may override only declared profile fields
    - generated values must reference source manifest and matrix version
    - secret binding may bind reference but never expose raw value
    - unknown fields are rejected unless namespaced extension is declared
  effective_config_evidence:
    safe_reference: evidence-bundle-a
    redaction_status: safe
    defaulted_fields_visible: true
```

## Validation Code Catalog Example

```yaml
validation_code_catalog:
  catalog_version: validation-0.1-example
  codes:
    - machine_code: OCS-ID-001
      rule_id: ocs-service-id-required
      field_or_scope: service.id
      severity: error
      human_message_key: service.id.required
      agent_message: service identity is missing
      remediation_hint: add stable service id before validation can pass
      retryability: after-change
      parity:
        ui: same
        api: same
        cli: same
        agent_api: same
      compatibility:
        aliases: []
        deprecated: false
    - machine_code: OCS-SEC-001
      rule_id: ocs-secret-reference-only
      field_or_scope: profiles.secret_references
      severity: error
      human_message_key: secret.reference.required
      agent_message: raw secret material is not allowed in manifest
      remediation_hint: use brokered secret reference
      retryability: after-change
      parity:
        ui: same
        api: same
        cli: same
        agent_api: same
      compatibility:
        aliases: []
        deprecated: false
```

## Generated Artifact Provenance Example

```yaml
generated_artifact_provenance:
  artifact_id: local-runtime-config
  artifact_class: runtime-config
  source_contract:
    manifest_identity: service-portable-a
    standard_version: ocs-0.1-example
    field_matrix_version: matrix-0.1-example
    generator: synthetic generator
  target_profile: local
  freshness:
    status: current
    generated_at: synthetic-build-001
    review_trigger: manifest or matrix change
  boundary:
    source_of_truth: false
    publish_boundary: local-only
    cleanup_required: true
  source_safety:
    sensitivity_class: public-template
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    reviewer_or_owner: org-owner-a
    stop_if_unknown: true
```

## Non-Claims

- This example does not prescribe final validation engine.
- This example does not require a specific manifest serialization.
- This example does not include real generated files.
