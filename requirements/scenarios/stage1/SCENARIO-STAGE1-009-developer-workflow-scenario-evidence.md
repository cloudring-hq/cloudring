# SCENARIO-STAGE1-009 - Developer Workflow Scenario Evidence

```yaml
id: SCENARIO-STAGE1-009
stage: STAGE-001
primary_role: developer
secondary_roles:
  - service owner
  - support
  - AI agent
intent:
  user_goal: Prove a complete local service workflow beyond binary availability.
  why_it_matters: Stage 1 must be a usable Solo Developer Cloud, not only installed tooling or disconnected docs.
  anti_lock_in_relevance: portability
preconditions:
  - presence-local-a has bootstrap evidence or a visible bootstrap warning
  - service-portable-a has a draft starter contract
  - workflow evidence template is available
surfaces:
  - CLI
  - API
  - Agent API
  - docs
  - conformance report
product_flow:
  - developer validates prerequisites and local runtime profile
  - developer creates or opens a service candidate with manifest and docs scaffold
  - agent reviews workflow steps and refuses thin e2e as full readiness
  - developer runs dependency debug path, env report, docs preview and one bounded task
  - cleanup evidence records removed resources, retained state and support handoff
expected_state_vocabulary:
  - draft
  - validated
  - debug-ready
  - docs-ready
  - task-ready
  - cleaned-up
  - warning
  - blocked
evidence:
  requirement_refs:
    - CR-WORKFLOW-001..032
    - CR-LIFECMD-001..032
    - CR-SERVICEFACTORY-001..053
    - CR-STAGE1-001..025
  conformance_refs:
    - stage1-service-ready
  template_refs:
    - requirements/templates/developer-workflow-scenario-evidence-template.md
  scenario_objects:
    - presence-local-a
    - service-portable-a
stop_condition_cases:
  - case: binary-availability-treated-as-full-workflow-proof
    expected_result: blocked
  - case: unstable-path-marked-ready
    expected_result: blocked
  - case: personal-contact-placeholder-in-docs
    expected_result: blocked
  - case: local-debug-success-claimed-as-provider-readiness
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: service owner
  stop_if_unknown: true
```
