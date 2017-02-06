# Synthetic Release Environment Promotion Evidence Example

This example follows
[../templates/release-environment-promotion-evidence-template.md](../templates/release-environment-promotion-evidence-template.md).
It uses synthetic objects only and does not prove a real implementation exists.

```yaml
release_environment_promotion_evidence:
  evidence_id: release-promotion-provider-a
  stage_scope: Stage 4
  profile_refs:
    - stage4-public-provider-ready
  requirement_refs:
    - CR-RELPROM-001..032
  scenario_refs:
    - SCENARIO-STAGE4-006
  workstream_refs:
    - WS-037
  owners:
    release_owner: release-owner-a
    build_owner: build-owner-a
    runtime_owner: runtime-owner-a
    support_owner: support-owner-a
    evidence_owner: evidence-owner-a
    approver: provider-owner-a
  module:
    module_id: metering-service-a
    module_type: service
    release_scope: provider
    maturity: candidate
  source_and_dependencies:
    source_revision_class: tag
    source_coverage_status: history-focused
    lock_strategy: single-lock
    toolchain_status: pinned
    mutable_input_exceptions: []
  checks:
    build_status: passed
    lint_status: passed
    unit_status: passed
    integration_status: warning
    e2e_status: skipped
    smoke_status: passed
    first_boot_status: not-applicable
    publication_status: warning
    confidence_non_claims:
      - integration proof is scoped to synthetic runner only
      - e2e was not run for this example
  runner:
    runner_class: managed-cloudring-runner
    trust_boundary: scoped build and test runner without direct production authority
    permissions_status: scoped
    log_redaction_status: passed
    secret_cleanup_status: passed
  artifact:
    artifact_id: artifact-digest-a
    artifact_type: image
    provenance_status: partial
    digest_or_immutable_id_status: present
    registry_or_storage_scope: provider
    source_safety_status: passed
  environment_bundle:
    target_environment: production
    bundle_id: provider-prod-bundle-a
    profile_status: complete
    parity_claim: production-like
    difference_summary:
      - staging bundle uses reduced capacity and synthetic credentials
    secret_reference_status: passed
    topology_redaction_status: passed
    policy_status: manual_review_required
  approval_and_promotion:
    approval_status: pending
    approval_scope: promote candidate to provider production scope
    promotion_state: planned
    promotion_target: provider-presence-a
    activation_evidence_status: unknown
  rollback_and_retention:
    rollback_status: warning
    previous_artifact_status: retained
    alias_or_pointer_status: atomic
    retention_status: policy-defined
    irreversible_warning_status: not-applicable
  source_safety:
    sensitivity_class: secret-adjacent
    redaction_status: safe
    copy_risk_status: paraphrased
    forbidden_content_result: passed
    raw_match_output_retained: false
  non_claims:
    - example does not prove production deployment
    - tag evidence is not promotion evidence
    - pending approval blocks final promotion claim
```

## Non-Claims

- This example is not a final release schema.
- This example does not include real commands, paths, endpoints, credentials,
  dependency lists, encrypted payloads or logs.
- This example does not prove signing, vulnerability scanning, license
  clearance or live deployment.
