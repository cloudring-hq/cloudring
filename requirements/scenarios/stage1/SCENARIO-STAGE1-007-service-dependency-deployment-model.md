# SCENARIO-STAGE1-007 - Service Dependency Deployment Model

```yaml
id: SCENARIO-STAGE1-007
stage: STAGE-001
primary_role: developer
secondary_roles:
  - service owner
  - support
  - AI agent
intent:
  user_goal: Describe a local service, its dependencies, generated runtime artifacts and redacted effective environment as one portable product contract.
  why_it_matters: Stage 1 must teach CloudRING what the service needs, not only how one local runtime starts it.
  anti_lock_in_relevance: portability
preconditions:
  - ocs-model-a defines service manifest, dependency contract and generated artifact kinds
  - service-portable-a has a draft service model
  - local-generator-a can create redacted local artifacts or report unsupported capability
surfaces:
  - CLI
  - API
  - Agent API
  - conformance report
product_flow:
  - developer declares service identity, profile and dependency capability classes
  - platform resolves effective local model and shows override consequences
  - generator creates traceable local artifacts and redacted env preview
  - agent reviews route, port, storage, state and local-only value warnings
  - service owner records dependency owners, support boundaries and non-claims
expected_state_vocabulary:
  - draft
  - model-ready
  - generated
  - local-ready
  - warning
  - blocked
evidence:
  requirement_refs:
    - CR-SVCDEPLOY-001..032
    - CR-LIFECMD-001..032
    - CR-OCSIM-001..036
    - CR-OCSCONTRACT-001..046
    - CR-STAGE1-001..025
  conformance_refs:
    - stage1-service-ready
stop_condition_cases:
  - case: local-fixture-credential-promoted
    expected_result: blocked
  - case: dependency-owner-unknown
    expected_result: blocked
  - case: generated-artifact-treated-as-source-of-truth
    expected_result: blocked
  - case: multiple-dependency-instances-without-conflict-report
    expected_result: blocked
  - case: unsupported-generator-capability
    expected_result: blocked
source_safety:
  sensitivity_class: source-derived
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: service owner
  stop_if_unknown: true
```
