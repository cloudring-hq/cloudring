# Documentation Decision Memory Evidence Example

Synthetic example for
[../templates/documentation-decision-memory-template.md](../templates/documentation-decision-memory-template.md).

```yaml
documentation_decision_memory_evidence:
  evidence_id: documentation-decision-memory-stage1-a
  date: 2026-06-22
  owner: documentation-memory-owner
  stage_refs:
    - STAGE-001
  profile_refs:
    - stage1-service-ready
  requirement_refs:
    - CR-DOCMEM-001..032
  scenario_refs:
    - SCENARIO-STAGE1-006
  source_pass_refs:
    - SRC-PASS-014

  scope:
    artifact_kind: docs-package
    product_area: service factory and local runtime
    audience:
      - developer
      - service owner
      - support
      - AI agent
    stage_scope: local
    claim_scope:
      proves:
        - a developer and agent can find onboarding, lifecycle, manifest, task, command and support docs for a local service flow
        - the documentation chain links requirements, decision rationale, scenario and conformance evidence
      does_not_prove:
        - provider production readiness
        - live runtime execution
        - complete source-history audit

  documentation_package:
    navigation_status: warning
    onboarding_status: passed
    reference_status: warning
    lifecycle_workflow_status: passed
    service_docs_status: passed
    command_action_docs_status: warning
    task_docs_status: warning
    plugin_extension_docs_status: warning
    runbook_status: passed
    offline_export_status: warning

  decision_memory:
    requirement_link_status: passed
    adr_status: not-needed
    adr_refs: []
    no_adr_rationale: this synthetic example records evidence shape and does not change an architecture boundary
    template_link_status: passed
    synthetic_example_status: passed
    scenario_link_status: passed
    conformance_link_status: passed
    source_pass_link_status: passed
    supersession_status: current

  freshness_and_ownership:
    owner_status: passed
    freshness_status: current
    review_trigger: when Stage 1 command surface or service template changes
    stale_behavior: owner-review
    affected_roles:
      - developer
      - support
      - AI agent

  feedback_loop:
    source_signal_status: passed
    triage_status: requirement
    outcome_ref: CR-DOCMEM-001..032
    repeated_theme_status: warning

  source_safety:
    sensitivity_class: source-derived
    redaction_status: passed
    private_marker_scan_status: passed
    strict_secret_scan_status: passed
    raw_source_copy_status: passed
    private_endpoint_status: passed
    source_path_status: passed

  blockers: []
  warnings:
    - command and task reference examples are synthetic and need implementation-backed validation before claiming runtime parity
    - offline export is represented as a requirement and not as an executed packaging test
  unresolved_gaps:
    - attach implementation-backed docs publication report when Stage 1 docs tooling exists
    - link generated command reference validation once command registry is implemented
  non_claims:
    - this example does not prove every source document was reviewed line by line
    - this example does not reproduce any legacy documentation text
  agent_handoff:
    allowed_actions:
      - review evidence
      - add source-safe docs coverage gaps
      - draft conformance report entry
    forbidden_actions:
      - paste raw source text, private endpoint, exact command or secret-adjacent data
      - claim readiness outside stated scope
    required_approvals:
      - documentation memory owner
```
