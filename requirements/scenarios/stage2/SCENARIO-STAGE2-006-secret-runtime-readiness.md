# SCENARIO-STAGE2-006 - Secret Runtime Readiness

```yaml
id: SCENARIO-STAGE2-006
stage: STAGE-002
primary_role: admin
secondary_roles:
  - user
  - support
  - governance
  - AI agent
intent:
  user_goal: Prove that a private presence can use encrypted secret declarations without exposing values and without confusing encryption with runtime readiness.
  why_it_matters: Stage 2 contains real trust boundaries; a private cloud cannot be ready if credentials are hidden in source, logs, generated docs or agent context.
  anti_lock_in_relevance: local-autonomy-and-trust
preconditions:
  - presence-private-a is installed
  - workload-a needs a brokered credential reference
  - secret-runtime-readiness-private-a evidence record is available
surfaces:
  - API
  - CLI
  - Agent API
  - conformance report
  - redacted support bundle
product_flow:
  - admin registers an encrypted secret declaration with explicit scope and owner
  - runtime publishes safe status without exposing secret value or encrypted blob
  - user deploys workload only after policy confirms the reference is valid for the requested scope
  - support reviews failure evidence with redacted reason and next action
  - governance checks key custody, rotation gap, source-safety and non-claims before readiness is accepted
expected_state_vocabulary:
  - declared
  - bound
  - synced
  - failed
  - stale
  - degraded
  - blocked
  - rotated
evidence:
  requirement_refs:
    - CR-SECRETRUN-001..032
    - CR-SECSUPPLY-001..038
    - CR-CONF-036
    - CR-SPECTPL-030
    - CR-SPECEX-018
    - CR-STAGE2-001..026
  conformance_refs:
    - stage2-private-presence-ready
  template_refs:
    - secret-runtime-readiness-evidence-template
  example_refs:
    - secret-runtime-readiness-evidence-example
stop_condition_cases:
  - case: raw-secret-value-enters-report-or-agent-context
    expected_result: blocked
  - case: encrypted-at-rest-used-as-only-readiness-proof
    expected_result: blocked
  - case: scope-is-weakened-without-approval
    expected_result: blocked
  - case: observed-generation-or-sync-status-is-unknown
    expected_result: warning
  - case: key-rotation-state-is-stale
    expected_result: warning
  - case: runtime-fails-open-after-missing-key
    expected_result: blocked
source_safety:
  sensitivity_class: secret-adjacent
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: secret runtime owner
  stop_if_unknown: true
```
