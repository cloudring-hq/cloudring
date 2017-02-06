# OCS Supporting Contract Templates

Purpose: define the reusable product-level shapes that make an OCS manifest
verifiable: field matrix, environment/profile precedence, validation code
catalog and generated artifact provenance.

These are semantic templates. They do not require a specific schema format,
language, runtime, orchestrator or UI framework.

## Manifest Field Matrix

```yaml
manifest_field_matrix:
  standard_version: ocs-version
  matrix_version: version
  fields:
    - path: semantic.field.path
      purpose: why this field exists
      owner: service-owner | platform | provider | policy | extension-owner
      status: required | optional | extension | deprecated | forbidden
      type: semantic type
      default:
        value_class: explicit | platform-default | profile-default | generated | none
        user_visible_consequence: consequence
      profile_behavior:
        local: required | optional | unsupported | generated | not-applicable
        private: required | optional | unsupported | generated | not-applicable
        provider: required | optional | unsupported | generated | not-applicable
        federation: required | optional | unsupported | generated | not-applicable
        global: required | optional | unsupported | generated | not-applicable
      validation:
        rule_id: stable-rule-id
        machine_code: stable-code
        severity: error | warning | info
        remediation: human-and-agent action
      compatibility:
        introduced_in: version
        deprecated_in: version-or-none
        breaking_change_if_removed: true | false
      source_safety:
        may_contain_secret: true | false
        may_contain_private_context: true | false
        redaction_required: true | false
```

## Environment And Profile Precedence

```yaml
environment_profile_precedence:
  service_id: synthetic-or-safe-id
  standard_version: ocs-version
  layers:
    - name: base
      purpose: common product contract
      may_contain_secret_values: false
    - name: profile
      purpose: local/private/provider/edge/global difference
      may_contain_secret_values: false
    - name: generated
      purpose: platform-derived values with provenance
      may_contain_secret_values: false
    - name: secret_binding
      purpose: brokered secret references only
      may_contain_secret_values: false
  precedence_rules:
    - higher layer overrides lower layer only for declared fields
    - unknown override field is rejected or namespaced as extension
    - secret reference can bind to field, but raw secret value cannot appear
  effective_config_evidence:
    safe_reference: evidence-bundle-id
    redaction_status: safe | warning | blocked
    defaulted_fields_visible: true | false
```

## Validation Code Catalog

```yaml
validation_code_catalog:
  catalog_version: version
  codes:
    - machine_code: OCS-CODE-000
      rule_id: stable-rule-id
      field_or_scope: field path or lifecycle scope
      severity: error | warning | info
      human_message_key: localization key
      agent_message: concise machine-readable cause
      remediation_hint: next action
      retryability: retryable | after-change | not-retryable | unknown
      parity:
        ui: same | exception
        api: same | exception
        cli: same | exception
        agent_api: same | exception
      compatibility:
        aliases:
          - older-code
        deprecated: true | false
```

## Generated Artifact Provenance

```yaml
generated_artifact_provenance:
  artifact_id: stable-artifact-id
  artifact_class: runtime-config | docs | image | api-spec | ui-bundle | report | other
  source_contract:
    manifest_identity: safe-manifest-identity
    standard_version: ocs-version
    field_matrix_version: version
    generator: generator identity
  target_profile: local | private | provider | federation | global | edge
  freshness:
    status: current | stale | unknown
    generated_at: date-or-build-identity
    review_trigger: date-or-condition
  boundary:
    source_of_truth: false
    publish_boundary: publishable | local-only | restricted | ignored
    cleanup_required: true | false
  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    reviewer_or_owner: role
    stop_if_unknown: true
```

## Stop Conditions

Agent must stop if:

- required fields have no owner, validation code or profile behavior;
- defaults are hidden from user/agent;
- precedence allows raw secret values or unknown override fields;
- validation codes differ across surfaces without explicit exception;
- generated artifact claims to be source-of-truth;
- artifact provenance lacks source contract, field matrix or freshness;
- source-safety status is unknown for publishable or agent-consumed artifact.
