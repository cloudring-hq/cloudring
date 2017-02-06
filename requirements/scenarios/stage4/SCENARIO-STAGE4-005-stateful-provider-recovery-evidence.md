# SCENARIO-STAGE4-005 - Stateful Provider Recovery Evidence

```yaml
id: SCENARIO-STAGE4-005
stage: STAGE-004
primary_role: provider
secondary_roles:
  - tenant
  - support
  - governance
  - AI agent
intent:
  user_goal: Prove that a public provider can operate a stateful service with recovery, failover, support and evidence boundaries.
  why_it_matters: Tenants buy an operating promise, not a backup checkbox.
  anti_lock_in_relevance: provider exit, operational trust and support evidence portability
preconditions:
  - provider-public-a offers service-stateful-a
  - stateful-readiness evidence exists for the provider-local presence
  - support and SLA claims reference recovery freshness
surfaces:
  - UI
  - API
  - Agent API
  - support console
  - conformance report
product_flow:
  - provider reviews recovery evidence before marking offer provider-ready
  - tenant sees recovery freshness, limitations and support owner before order
  - support opens incident using source-safe recovery evidence
  - provider records remediation, waiver or blocking finding
  - billing/support owner links recovery impact to SLA or appeal path when relevant
expected_state_vocabulary:
  - provider-ready
  - limited
  - degraded
  - blocked
  - stale
  - waived
evidence:
  requirement_refs:
    - CR-STATEFULRUN-001..032
    - CR-OBSOPS-031..036
    - CR-INFPROFILE-031
    - CR-STAGE4-001..026
  conformance_refs:
    - stage4-public-provider-ready
  template_refs:
    - ../../templates/stateful-readiness-evidence-template.md
stop_condition_cases:
  - case: provider-sells-stateful-service-with-stale-restore-evidence
    expected_result: blocked
  - case: support-needs-raw-private-topology-to-diagnose
    expected_result: blocked
  - case: recovery-finding-waived-without-expiry
    expected_result: blocked
  - case: tenant-impact-hidden-from-service-card
    expected_result: blocked
  - case: recovery-limitation-visible-before-order
    expected_result: limited
source_safety:
  sensitivity_class: synthetic
  redaction_status: safe
  copy_risk_status: paraphrased
  forbidden_content_result: passed
  reviewer_or_owner: provider operations owner
  stop_if_unknown: true
```
