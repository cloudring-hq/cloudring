# Release Environment Promotion Evidence Template

Purpose: capture source-safe evidence that a release is a governed artifact
promotion with environment bundle, checks, approval and rollback, not only a
build, tag, CI job or local archive.

```yaml
release_environment_promotion_evidence:
  evidence_id: release-promotion-evidence-id
  stage_scope: Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 | Stage 6 | Stage 7
  profile_refs:
    - stage4-public-provider-ready
  requirement_refs:
    - CR-RELPROM-001..032
  scenario_refs:
    - SCENARIO-STAGE4-006
  workstream_refs:
    - WS-037
  owners:
    release_owner: role
    build_owner: role
    runtime_owner: role
    support_owner: role
    evidence_owner: role
    approver: role
  module:
    module_id: safe-module-id
    module_type: service | control-plane | task-image | ui-extension | base-image | connector | template | docs-package
    release_scope: local | private | provider | federation | global
    maturity: draft | candidate | promoted | blocked | deprecated | retired
  source_and_dependencies:
    source_revision_class: branch | tag | release-candidate | source-bundle | unknown
    source_coverage_status: current-tree | history-focused | sampled | complete | unknown
    lock_strategy: single-lock | multi-lock-explicit | checksum-only | exception | unknown
    toolchain_status: pinned | range | floating | exception | unknown
    mutable_input_exceptions:
      - exception-id-or-none
  checks:
    build_status: passed | warning | failed | blocked | skipped | unknown
    lint_status: passed | warning | failed | blocked | skipped | unknown
    unit_status: passed | warning | failed | blocked | skipped | unknown
    integration_status: passed | warning | failed | blocked | skipped | unknown
    e2e_status: passed | warning | failed | blocked | skipped | unknown
    smoke_status: passed | warning | failed | blocked | skipped | unknown
    first_boot_status: passed | warning | failed | blocked | skipped | not-applicable | unknown
    publication_status: passed | warning | failed | blocked | skipped | not-applicable | unknown
    confidence_non_claims:
      - explicit non-claim
  runner:
    runner_class: local | ci | private-runner | provider-runner | managed-cloudring-runner | external | unknown
    trust_boundary: safe-summary
    permissions_status: scoped | broad | unknown | blocked
    log_redaction_status: passed | warning | failed | not-reviewed
    secret_cleanup_status: passed | warning | failed | not-applicable | unknown
  artifact:
    artifact_id: immutable-safe-id
    artifact_type: image | binary | ui-bundle | package | vm-template | manifest | docs | other
    provenance_status: complete | partial | warning | blocked | unknown
    digest_or_immutable_id_status: present | missing | not-applicable | unknown
    registry_or_storage_scope: local | private | provider | federation | global | not-published
    source_safety_status: passed | warning | failed | blocked
  environment_bundle:
    target_environment: local | development | staging | production | private | provider | federation | global
    bundle_id: safe-bundle-id
    profile_status: complete | partial | missing | unknown
    parity_claim: exact | production-like | limited | not-claimed | unknown
    difference_summary:
      - safe-summary
    secret_reference_status: passed | warning | failed | blocked
    topology_redaction_status: passed | warning | failed | blocked
    policy_status: allow | warn | block | manual_review_required | unknown
  approval_and_promotion:
    approval_status: approved | rejected | pending | waived | missing | not-required
    approval_scope: safe-summary
    promotion_state: not-promoted | planned | promoted | failed | rolled-back | blocked
    promotion_target: safe-target-class
    activation_evidence_status: passed | warning | failed | blocked | unknown
  rollback_and_retention:
    rollback_status: ready | warning | impossible | missing | blocked | unknown
    previous_artifact_status: retained | missing | not-applicable | unknown
    alias_or_pointer_status: atomic | mutable-unsafe | not-applicable | unknown
    retention_status: policy-defined | warning | missing | unknown
    irreversible_warning_status: present | missing | not-applicable
  source_safety:
    sensitivity_class: source-derived | operational | secret-adjacent | topology-adjacent | financial-adjacent
    redaction_status: safe | warning | blocked | not-reviewed
    copy_risk_status: paraphrased | source-shaped | blocked | not-reviewed
    forbidden_content_result: passed | failed | not-run
    raw_match_output_retained: false
  non_claims:
    - explicit non-claim
```

## Rules

1. Do not treat build, tag, CI entrypoint, badge or local archive as promotion
   proof.
2. Redact encrypted payloads, topology values, secret-shaped names, raw logs,
   command lines and source-shaped snippets.
3. Mark staging-like, debug/pre-release and external-runner evidence honestly.
4. Require rollback/retention before provider/public/private impact promotion.
