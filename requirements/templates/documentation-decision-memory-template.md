# Documentation Decision Memory Evidence Template

Use this template when documentation, ADR, source-pass learning or developer
guidance is used as evidence for a CloudRING product decision.

```yaml
documentation_decision_memory_evidence:
  evidence_id: documentation-decision-memory-evidence-id
  date: YYYY-MM-DD
  owner: documentation-memory-owner
  stage_refs:
    - STAGE-000
  profile_refs:
    - stage0-requirements-memory-ready
  requirement_refs:
    - CR-DOCMEM-001..032
  scenario_refs:
    - SCENARIO-STAGE1-006
  source_pass_refs:
    - SRC-PASS-000

  scope:
    artifact_kind: docs-package | ADR | source-pass | runbook | command-reference | practice-guide | feedback-record
    product_area: capability-or-stage
    audience:
      - developer
      - support
      - AI agent
    stage_scope: local | private | provider | federation | global | self-evolving | source-memory
    claim_scope:
      proves:
        - product claim
      does_not_prove:
        - explicit non-claim

  documentation_package:
    navigation_status: passed | warning | failed | blocked | not-applicable
    onboarding_status: passed | warning | failed | blocked | not-applicable
    reference_status: passed | warning | failed | blocked | not-applicable
    lifecycle_workflow_status: passed | warning | failed | blocked | not-applicable
    service_docs_status: passed | warning | failed | blocked | not-applicable
    command_action_docs_status: passed | warning | failed | blocked | not-applicable
    task_docs_status: passed | warning | failed | blocked | not-applicable
    plugin_extension_docs_status: passed | warning | failed | blocked | not-applicable
    runbook_status: passed | warning | failed | blocked | not-applicable
    offline_export_status: passed | warning | failed | blocked | not-applicable

  decision_memory:
    requirement_link_status: passed | warning | failed | blocked
    adr_status: linked | not-needed | needed-blocker | missing
    adr_refs:
      - ADR-0000
    no_adr_rationale: reason-or-none
    template_link_status: passed | warning | failed | blocked | not-applicable
    synthetic_example_status: passed | warning | failed | blocked | not-applicable
    scenario_link_status: passed | warning | failed | blocked | not-applicable
    conformance_link_status: passed | warning | failed | blocked | not-applicable
    source_pass_link_status: passed | warning | failed | blocked | not-applicable
    supersession_status: current | superseded | deprecated | unknown

  freshness_and_ownership:
    owner_status: passed | warning | failed | blocked
    freshness_status: current | stale | unknown | contradicted
    review_trigger: date-or-condition
    stale_behavior: warn | block | remove-claim | owner-review
    affected_roles:
      - role

  feedback_loop:
    source_signal_status: passed | warning | failed | blocked | not-applicable
    triage_status: no-change | docs | requirement | ADR | runbook | conformance | scenario | rejected | unknown
    outcome_ref: safe-reference-or-none
    repeated_theme_status: none | warning | blocker | unknown

  source_safety:
    sensitivity_class: public-template | source-derived | operational | tenant-data | secret-adjacent
    redaction_status: passed | warning | failed | blocked
    private_marker_scan_status: passed | warning | failed | blocked | not-run
    strict_secret_scan_status: passed | warning | failed | blocked | not-run
    raw_source_copy_status: passed | warning | failed | blocked | not-reviewed
    private_endpoint_status: passed | warning | failed | blocked | not-reviewed
    source_path_status: passed | warning | failed | blocked | not-reviewed

  blockers:
    - blocker
  warnings:
    - warning
  unresolved_gaps:
    - gap
  non_claims:
    - non-claim
  agent_handoff:
    allowed_actions:
      - review evidence
      - draft source-safe docs improvement
    forbidden_actions:
      - paste raw source text, private endpoint, exact command or secret-adjacent data
      - claim readiness outside stated scope
    required_approvals:
      - documentation memory owner
```

## Rules

1. Treat missing ADR/no-ADR rationale, missing owner or missing source-safety
   review as warning or blocker, never as passed.
2. Store product meaning and decision links, not raw legacy docs or exact old
   operational commands.
3. State the stage and role scope of each claim.
4. If documentation is used as readiness evidence, link the conformance gate
   that consumes it.
