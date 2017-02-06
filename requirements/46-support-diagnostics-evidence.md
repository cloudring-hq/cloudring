# Support Diagnostics Evidence

## Назначение

Support Diagnostics Evidence фиксирует требования к тому, как CloudRING
формирует безопасный диагностический пакет для поддержки, операторов и
AI-агентов. Такой пакет нужен, чтобы один человек с агентами мог понять
состояние сервиса, образа, очереди, stateful-операции или provider-присутствия
без доступа к старым исходникам, приватным стендам и небезопасным логам.

Главный урок source-slice: observability signals сами по себе не равны
support-ready diagnostics. Health, logs, traces, metrics, generated API docs,
runtime manifest, debug flow, image cleanup and stateful audit signals полезны
только тогда, когда они собраны в источник правды: что произошло, где граница
ответственности, какие данные безопасны, какие сигналы отсутствуют, что можно
делать агенту, а что требует owner approval.

Этот документ описывает what/why/evidence. Он не выбирает observability stack,
log backend, tracing protocol, ticketing system, crash dump implementation,
orchestration runtime, database, queue, image builder or incident tool.

## Product Boundary

- Support diagnostics package - read-only evidence bundle for a specific
  service, image, operation, incident, release or provider state.
- Diagnostics identity - service/product/environment/profile/release identity
  that lets support reason about the right object without raw source context.
- Primary failure story - single support-safe summary that links symptoms,
  correlation references, affected components and next action.
- Signal matrix - declared mapping of health, readiness, logs, traces, metrics,
  events, queue pressure, drain state, image readiness and stateful audit signals.
- Redaction boundary - explicit rule for what is omitted, summarized, retained,
  attached or blocked from agent context.
- Staged disclosure - summary-first diagnostic flow where sensitive attachments
  require stronger approval.

## Source-Derived Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| Runtime used separate readiness/liveness and changed readiness during lifecycle. | Support must distinguish alive process, traffic-ready service and draining service. | `CR-SUPDIAG-004..006` |
| Requests carried correlation into logs/traces/downstream work. | One incident must be traceable across ingress, internal work and queued output. | `CR-SUPDIAG-007..009` |
| Retry, duplicate and queue pressure were partially observable. | Backpressure and idempotent duplicate success must not look like silent data loss. | `CR-SUPDIAG-011..014` |
| Generated docs and error schemas existed but did not form an operational runbook. | Integration docs must be linked to diagnostic semantics and non-claims. | `CR-SUPDIAG-015..018` |
| Platform docs treated logs, traces and metrics as complementary signals. | A support package needs cross-linked signal families, not one raw stream. | `CR-SUPDIAG-008`, `CR-SUPDIAG-019` |
| Runtime manifest and service docs described dependencies and local flows. | Diagnostics must classify service, local runtime, shared platform and provider issues. | `CR-SUPDIAG-003`, `CR-SUPDIAG-020..022` |
| Image factory cleaned logs and optional crash evidence before publication. | Image diagnostics must preserve seal/crash/boot meaning without shipping unsafe residue. | `CR-SUPDIAG-023..025` |
| Stateful recovery evidence used audit summaries rather than raw infrastructure dumps. | Restore/failover diagnostics need timelines, outcomes and blockers, not full private logs. | `CR-SUPDIAG-026..028` |
| Log export and support bundle shape were incomplete. | Readiness must warn or block when diagnostics surfaces are declared but not implemented. | `CR-SUPDIAG-029..032` |

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SUPDIAG-001 | Every supportable CloudRING capability must declare a Support Diagnostics Package. | Support readiness cannot be inferred from scattered logs, metrics, docs or probes. | Package links object type, owner, profile, stage, source of signals, redaction policy, retention policy, evidence refs, non-claims and stop conditions. |
| CR-SUPDIAG-002 | Diagnostics package must be read-only and side-effect free. | Collecting diagnostics during an incident must not change tenant state, queue state, billing state or recovery state. | Evidence records allowed read scopes, forbidden mutations, collection risk class, approval status and proof that diagnostic collection does not execute remediation. |
| CR-SUPDIAG-003 | Diagnostics identity must include stable service, environment, profile, release and owner context. | Support cannot reason safely from host location, local path, raw process name or human memory. | Package identifies target object, stage/profile scope, release/build marker, support owner, evidence owner and affected users using safe generic identifiers. |
| CR-SUPDIAG-004 | Liveness, readiness and health must have separate meanings. | A process can be alive while not ready, or degraded while still serving some traffic. | Evidence defines alive, ready, degraded, draining and unavailable states, with who consumes each state and what user consequence follows. |
| CR-SUPDIAG-005 | Readiness must become false before planned shutdown or unsafe traffic handling. | Rollout and maintenance should stop new work before accepted work is drained. | Lifecycle evidence shows startup readiness gate, shutdown readiness flip, drain boundary, timeout/unknown behavior and support-visible state. |
| CR-SUPDIAG-006 | Dependency health must not be hidden behind a single green status. | A generic health pass can mask broken queue, storage, identity, observability or shared platform dependency. | Component status matrix distinguishes service process, required dependencies, optional dependencies, shared platform services, stale checks and unknown checks. |
| CR-SUPDIAG-007 | Request and operation correlation must survive from entry to internal work and downstream output. | Support needs one handle to connect user symptoms, logs, traces, queued work and receipts. | Evidence proves correlation reference propagation across ingress, internal operation, emitted event/receipt and support-safe summary. |
| CR-SUPDIAG-008 | Logs, traces, metrics and event summaries must be cross-linkable. | One raw signal rarely explains failure causality or blast radius. | Signal matrix states which outcomes produce log summaries, trace/error markers, counters/events and support references, with gaps marked warning or blocked. |
| CR-SUPDIAG-009 | Diagnostics must preserve a single primary failure story. | Duplicate error reporting creates noise, conflicting tickets and misleading agent action. | Package names primary failure boundary, supporting signals, deduplication rule, affected component and recommended next action. |
| CR-SUPDIAG-010 | Error taxonomy must be stable, redacted and actionable. | Users, support and agents need deterministic remediation without internal details. | Error catalog distinguishes authorization, validation, parse/shape, dependency, overload, timeout, duplicate/retry and internal classes with retryability and owner. |
| CR-SUPDIAG-011 | Retry and idempotent duplicate outcomes must be visible. | A successful duplicate response can otherwise look like double processing or data loss. | Diagnostics show first-seen vs duplicate behavior, correlation reference, dedupe outcome, retention window, counters and support-safe explanation. |
| CR-SUPDIAG-012 | Queue saturation and backpressure must be first-class support states. | Overload should be treated differently from validation failure or broken dependency. | Package records overload class, affected intake path, current/last-known pressure signal, caller consequence, retry guidance and mitigation owner. |
| CR-SUPDIAG-013 | Drain and shutdown progress must be diagnostically visible for accepted work. | Rolling updates and terminations can lose accepted work if drain state is opaque. | Evidence shows stop-admission time, drain scope, pending-work policy, completion/timeout state, discarded/quarantined count class and non-claims. |
| CR-SUPDIAG-014 | Async acceptance must be separated from final outcome in diagnostics. | Accepted-for-processing is not proof of downstream delivery, billing, settlement or recovery completion. | Receipt/status summary separates received, validated, queued, processed, quarantined, failed, settled, restored or unknown states as appropriate. |
| CR-SUPDIAG-015 | Generated API docs must not be the support source of truth. | Generated docs can be stale, unsafe or missing operational consequences. | Support package links generated docs to machine contract, runtime evidence, freshness, drift result and source-safety status. |
| CR-SUPDIAG-016 | Diagnostic docs must explain required inputs, result states, error classes and duplicate behavior. | Most integration incidents come from misunderstood contract semantics. | Runbook or diagnostics guide covers safe required fields, profile scope, request identity, retry, duplicate, overload, error taxonomy and non-claims. |
| CR-SUPDIAG-017 | Runbook content must be separated from general product documentation. | Operational recovery steps should not be buried in architecture prose or feature docs. | Service docs package contains dedicated runbook/diagnostics section with owner, freshness, stage scope and linked evidence bundle. |
| CR-SUPDIAG-018 | Runtime manifest or equivalent contract must reconstruct diagnostic dependency context. | Support should not need source code to know required components and mode. | Manifest-derived summary lists declared dependencies, profile overrides, optional/required classification, local/shared/provider boundary and unknowns. |
| CR-SUPDIAG-019 | Diagnostics must classify issue location before recommending action. | Local service bug, local runtime issue, shared platform dependency and provider incident require different owners. | Triage classification is one of service, local-runtime, shared-platform, provider, customer-input, external-dependency, security-review or ambiguous, with evidence. |
| CR-SUPDIAG-020 | Diagnostic mode must be distinct from normal start/stop and repair actions. | Operators need a safe path for inspection that does not accidentally run or mutate production flow. | Tooling distinguishes normal lifecycle, diagnostic inspection, debug reproduction, remediation and rollback, each with risk class and approval. |
| CR-SUPDIAG-021 | Support owner and escalation path must be explicit for every diagnostics package. | A useful bundle still fails if no one owns the next decision. | Package records support owner, product owner, platform owner if applicable, evidence owner, escalation trigger and manual-review condition. |
| CR-SUPDIAG-022 | Diagnostics package must be readable by humans and AI agents. | The operating model depends on one human plus agents sharing the same safe evidence. | Summary uses stable fields, bounded vocabulary, requirement refs, scenario refs, source-safety status, recommended action and forbidden action list. |
| CR-SUPDIAG-023 | Image diagnostics must preserve boot/readiness/crash and seal outcome safely. | Base images can fail after publication while raw build residue must not leak. | Image evidence records boot readiness, guest initialization, crash evidence policy, seal/cleanup summary, omitted artifact classes and promotion identity. |
| CR-SUPDIAG-024 | Crash or deep diagnostics must be optional, scoped and approval-gated. | Deep dumps can contain secrets, tenant data or kernel/runtime internals. | Evidence states whether deep diagnostics are enabled, why, access scope, retention, redaction, approval and fallback summary when disabled. |
| CR-SUPDIAG-025 | Cleanup and redaction decisions must be visible as evidence, not hidden deletion. | Support needs to know what was intentionally removed and what cannot be inspected. | Package records removed/omitted evidence classes, reason, safety classification, impact on diagnosis and owner-approved exception if needed. |
| CR-SUPDIAG-026 | Stateful operation diagnostics must use timelines and audit summaries, not raw dumps by default. | Restore, PITR, failover and backup evidence can expose topology, grants and sensitive state. | Bundle contains operation timeline, target scope, outcome, rollback/failover state, blocker summary, tenant impact and redacted audit references. |
| CR-SUPDIAG-027 | Restore/failover diagnostics must separate drill evidence from production incident evidence. | A successful drill does not prove the exact production incident path. | Evidence marks drill, simulation, live incident, partial recovery or unknown, with freshness, deviations and non-claims. |
| CR-SUPDIAG-028 | Diagnostic export for high-impact operations must require owner approval and retention limit. | Support bundles can become sensitive long-lived archives. | Export record includes requester, approver, purpose, access level, expiry, deletion/retention state, attachment policy and revocation path. |
| CR-SUPDIAG-029 | Redaction must be default-deny for source, secret, topology and customer data. | Diagnostics are often the highest-risk leak surface. | Scan and review block raw credentials, secret-like values, private paths, host identifiers, network literals, tenant data, raw commands, source snippets and copied generated examples. |
| CR-SUPDIAG-030 | Diagnostics must use staged disclosure: summary first, attachments only when justified. | Agents should triage with minimal sensitive context and escalate only when needed. | Package separates public/support summary, restricted attachments, blocked artifacts, approval requirements and reason for each escalation. |
| CR-SUPDIAG-031 | Diagnostics readiness must be tested or explicitly marked as a gap. | A declared log/export/status surface can be present in docs but absent in implementation. | Evidence covers readiness/health, correlation, error taxonomy, duplicate/retry, overload, drain, redaction and export behavior, or marks each missing proof warning/blocked. |
| CR-SUPDIAG-032 | Source-derived diagnostics lessons must remain product abstractions. | CloudRING should preserve experience without cloning old source, commands or private context. | Requirements and evidence omit raw paths, endpoints, hostnames, IPs, credentials, command lines, package names, commit subjects, source snippets and generated docs text. |

## Evidence Shape

Minimum Support Diagnostics evidence:

```yaml
support_diagnostics_evidence:
  evidence_id: support-diagnostics-evidence-id
  profile_refs:
    - stage4-public-provider-ready
  scenario_refs:
    - SCENARIO-STAGE4-007
  requirement_refs:
    - CR-SUPDIAG-001..032
  target:
    object_type: service | image | stateful-operation | provider-operation | release
    identity_status: passed | warning | failed | blocked
    owner_status: passed | warning | failed | blocked
    stage_scope:
      - STAGE-004
  lifecycle_state:
    liveness_status: passed | warning | failed | blocked
    readiness_status: passed | warning | failed | blocked
    health_component_status: passed | warning | failed | blocked
    drain_status: passed | warning | failed | blocked
  correlation:
    request_correlation_status: passed | warning | failed | blocked
    logs_traces_metrics_link_status: passed | warning | failed | blocked
    primary_failure_story_status: passed | warning | failed | blocked
  operational_signals:
    error_taxonomy_status: passed | warning | failed | blocked
    retry_duplicate_status: passed | warning | failed | blocked
    overload_backpressure_status: passed | warning | failed | blocked
    async_outcome_status: passed | warning | failed | blocked
  dependency_context:
    manifest_derived_context_status: passed | warning | failed | blocked
    issue_classification: service | local-runtime | shared-platform | provider | customer-input | external-dependency | security-review | ambiguous
  image_and_stateful:
    image_boot_seal_status: passed | warning | failed | blocked | not-applicable
    deep_diagnostics_policy_status: passed | warning | failed | blocked | not-applicable
    stateful_timeline_status: passed | warning | failed | blocked | not-applicable
  export_control:
    read_only_status: passed | warning | failed | blocked
    redaction_status: passed | warning | failed | blocked
    staged_disclosure_status: passed | warning | failed | blocked
    approval_status: passed | warning | failed | blocked
    retention_status: passed | warning | failed | blocked
  validation:
    diagnostics_test_status: passed | warning | failed | blocked
    source_safety_status: passed | warning | failed | blocked
  non_claims:
    - does not prove production root cause unless linked incident evidence exists
    - does not prove downstream financial or recovery completion
```

## Stop Conditions

Agent must stop and request owner/review if:

- diagnostics collection would mutate runtime, tenant, billing, queue, recovery or
  release state;
- liveness, readiness, health and drain are collapsed into one ambiguous status;
- correlation cannot connect symptom, request, internal work and support-safe
  receipt/event reference;
- duplicate, retry, queue pressure or async acceptance is hidden behind generic
  success;
- generated docs or a declared log/status command are treated as support
  readiness without runtime evidence;
- support bundle contains raw source paths, private endpoints, host identifiers,
  network literals, credentials, tenant data, copied commands or source snippets;
- stateful or deep diagnostics export lacks owner approval, retention limit,
  staged disclosure or redaction result;
- local/debug observability is claimed as private/provider/federation readiness
  without stage-scoped evidence.

## Non-Goals

- Не выбирать конкретный monitoring, tracing, logging, crash dump, ticketing,
  image, orchestration or incident-management technology.
- Не заменять `CR-OBSOPS-*`, `CR-BILLRUN-*`, `CR-STATEFULRUN-*`,
  `CR-BASEIMG-*` or `CR-RELPROM-*`; this document defines the diagnostics
  package that makes those evidence families supportable.
- Не переносить старые logs, API docs, endpoint paths, commands, source snippets,
  package names, host identifiers or operational context.
- Не утверждать live runtime behavior, root cause, production readiness,
  financial settlement, restore completion, vulnerability absence, full
  line-by-line source coverage or full all-refs history coverage.
