# SCENARIO-STAGE1-010 - Reference Service Portfolio Evidence

```yaml
id: SCENARIO-STAGE1-010
stage: STAGE-001
primary_role: developer
secondary_roles:
  - service owner
  - support
  - governance
  - AI agent
intent:
  user_goal: Prove that Stage 1 has a source-safe portfolio of reference services, not only one runnable sample.
  why_it_matters: Solo Developer Cloud must teach the right product patterns from day one and stop demo examples from becoming false readiness claims.
  anti_lock_in_relevance: portability
preconditions:
  - reference service portfolio evidence template is available
  - at least one service contract or service entry exists for review
  - conformance profile can distinguish candidate, blocked and ready states
surfaces:
  - docs
  - service contract
  - conformance report
  - Agent API
  - support handoff
product_flow:
  - developer opens the reference service portfolio evidence report
  - service owner verifies archetype registry and coverage matrix
  - agent checks that each service declares purpose, audience, stage scope and non-goals
  - developer reviews first useful behavior, run-mode boundary and dependency ownership for each archetype
  - support reviews diagnostic summary, runbook state and failure fixtures
  - governance blocks readiness when docs-only, debug-only, integration, release, catalog or production claims are mixed
  - agent produces source-safe gap plan without raw commands, raw environment values or copied source shape
expected_state_vocabulary:
  - draft
  - candidate
  - covered
  - partial
  - blocked
  - stale
  - ready
  - non-claim
evidence:
  requirement_refs:
    - CR-REFSVC-001..032
    - CR-WORKFLOW-001..032
    - CR-SVCDEPLOY-001..032
    - CR-DOCMEM-001..032
    - CR-SUPDIAG-001..032
    - CR-STAGE1-001..025
  conformance_refs:
    - stage1-service-ready
    - CR-CONF-050
  template_refs:
    - requirements/templates/reference-service-portfolio-evidence-template.md
  example_refs:
    - requirements/examples/reference-service-portfolio-evidence-example.md
  scenario_objects:
    - refsvc-portfolio-synthetic-a
    - service-portable-a
stop_condition_cases:
  - case: one-sample-treated-as-full-portfolio
    expected_result: blocked
  - case: docs-scaffold-treated-as-docs-readiness
    expected_result: blocked
  - case: demo-secret-or-local-endpoint-treated-as-production-evidence
    expected_result: blocked
  - case: job-case-lacks-completion-or-failure-semantics
    expected_result: blocked
  - case: reference-service-claimed-as-provider-publication-without-release-or-catalog-evidence
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: service owner
  stop_if_unknown: true
```
