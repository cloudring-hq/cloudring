# SCENARIO-STAGE1-005 - Service Lifecycle Command Evidence

```yaml
id: SCENARIO-STAGE1-005
stage: STAGE-001
primary_role: developer
secondary_roles:
  - service owner
  - support
  - AI agent
intent:
  user_goal: Create, validate, debug, inspect, document, run a bounded task and clean up a local service with evidence.
  why_it_matters: Stage 1 must be a complete developer product loop, not only a manifest or executable.
  anti_lock_in_relevance: portability
preconditions:
  - ocs-model-a defines service_manifest and lifecycle action kinds
  - service-portable-a has a draft starter manifest
surfaces:
  - CLI
  - API
  - Agent API
  - conformance report
product_flow:
  - developer creates a service from a source-safe template
  - validator checks identity, manifest, docs, profiles and command contracts
  - agent prepares dry-run plan for debug dependencies and task execution
  - developer runs docs preview and support-safe evidence capture
  - cleanup result records removed and retained local resources
expected_state_vocabulary:
  - draft
  - validated
  - debug-ready
  - task-ready
  - cleaned-up
  - warning
  - blocked
evidence:
  requirement_refs:
    - CR-LIFECMD-001..032
    - CR-OCSIM-001..036
    - CR-OCSCONTRACT-001..046
    - CR-STAGE1-001..025
  conformance_refs:
    - stage1-service-ready
stop_condition_cases:
  - case: operation-has-unsafe-protected-value-interpolation
    expected_result: blocked
  - case: lifecycle-action-unstable-but-marked-ready
    expected_result: blocked
  - case: docs-preview-port-conflict
    expected_result: warning
  - case: cleanup-consequence-hidden
    expected_result: blocked
source_safety:
  sensitivity_class: public-template
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: service owner
  stop_if_unknown: true
```
