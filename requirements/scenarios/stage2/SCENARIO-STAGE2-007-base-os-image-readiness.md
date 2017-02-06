# SCENARIO-STAGE2-007 - Base OS Image Readiness

```yaml
id: SCENARIO-STAGE2-007
stage: STAGE-002
primary_role: admin
secondary_roles:
  - support
  - governance
  - AI agent
intent:
  user_goal: Prove that a private presence can create or accept a reusable base image without leaking build context and without confusing build success with cloud readiness.
  why_it_matters: Private CloudRING needs predictable VM/workload foundations; hidden image drift becomes security, support and lock-in debt.
  anti_lock_in_relevance: backend-neutral-image-supply
preconditions:
  - presence-private-a needs a reusable base image line
  - image builder evidence exists as source-safe summary
  - raw build profiles and private values are excluded from agent context
surfaces:
  - API
  - CLI
  - Agent API
  - conformance report
  - infrastructure capability profile
  - redacted support bundle
product_flow:
  - admin selects an image line and target private profile
  - system shows build input classes, artifact identity, supported profiles and non-claims before promotion
  - AI agent reviews redacted evidence for unattended install, provisioning, guest tooling, cleanup and first-boot status
  - support confirms console/diagnostic boundary and cleanup residue expectations
  - governance blocks promotion until source-safety, cleanup, provenance and first-boot evidence are current
expected_state_vocabulary:
  - draft
  - validating
  - built
  - sealed
  - smoke-tested
  - private-ready
  - provider-candidate
  - deprecated
  - blocked
evidence:
  requirement_refs:
    - CR-BASEIMG-001..032
    - CR-INFPROFILE-008
    - CR-SECSUPPLY-030..037
    - CR-CONF-038
    - CR-CAPEVID-028
    - CR-SPECTPL-032
    - CR-SPECEX-020
    - CR-STAGE2-001..026
  conformance_refs:
    - stage2-private-presence-ready
  template_refs:
    - base-os-image-readiness-evidence-template
  example_refs:
    - base-os-image-readiness-evidence-example
stop_condition_cases:
  - case: raw-build-profile-enters-report-or-agent-context
    expected_result: blocked
  - case: image-build-success-used-as-only-readiness-proof
    expected_result: blocked
  - case: cleanup-or-machine-identity-state-is-unknown
    expected_result: blocked
  - case: first-boot-smoke-result-is-missing
    expected_result: warning
  - case: backend-specific-image-is-marked-portable-without-adapter-gap
    expected_result: blocked
  - case: artifact-identity-is-mutable-before-catalog-placement
    expected_result: blocked
source_safety:
  sensitivity_class: secret-adjacent
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: infrastructure owner
  stop_if_unknown: true
```
