# Conformance Profile - Stage 1 Service Ready

---
profile_id: stage1-service-ready
profile_version: 0.7
stage: 1
stage_file: ../stages/01-solo-developer-cloud.md
change_note: SRC-PASS-029 added reference service portfolio evidence gate.
---

## Purpose

Доказать, что Stage 1 является законченным Solo Developer Cloud: разработчик
может создать переносимый сервис, запустить его локально, увидеть docs,
observability, tasks and conformance report без ручной сборки инфраструктуры.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE1-000 | Versioned service template exists. | Developer старт должен быть воспроизводимым и обновляемым. | Template version, supported runtime profile and generated skeleton evidence. | Service can only be created by ad hoc manual copy. |
| CONF-STAGE1-001 | Service manifest is valid and central. | Без manifest нет переносимого сервиса. | Manifest/capability/lifecycle contract evidence linked to `CR-STAGE1-006`. | Runtime starts service without valid manifest. |
| CONF-STAGE1-002 | Local runtime executes declared dependencies. | Local dev должен быть близок к production contract. | Service with database/object storage/secret store/observability dependency reaches ready state. | Dependency is configured manually outside contract. |
| CONF-STAGE1-003 | Secrets are safe-by-default. | Первый stage не должен закрепить небезопасные привычки. | No plaintext secrets in manifest/repo; brokered/dev-safe secret flow evidence. | Secret value appears in manifest, logs, report or agent context. |
| CONF-STAGE1-004 | Health/readiness/metrics/logs/traces exist. | Сервис должен быть поддерживаемым агентами. | Standard health/readiness, metrics, structured logs and trace context evidence. | No observable readiness signal. |
| CONF-STAGE1-005 | Docs and runbook are part of readiness. | Агент не сможет сопровождать сервис без контекста. | Overview, API/contract notes, runbook, FAQ and manifest link. | Service is runnable but undocumented. |
| CONF-STAGE1-006 | Task library works local and CI-style with machine-readable outcome. | Automation should not be environment-specific. | Same task definition runs validation/build/test/docs/observe/package flow and returns structured outcome. | Task requires hidden local manual step or unparseable output. |
| CONF-STAGE1-007 | Portability limitations are explicit. | Stage 1 must prepare future stages without pretending to be them. | Report shows private-readiness gaps and runtime/template portability. | Template/runtime is hard lock-in without alternative path. |
| CONF-STAGE1-008 | Developer success metrics are captured. | Product must prove it reduces friction. | Time to first service, local debug success, task portability, docs completeness and feedback time. | No way to know whether Stage 1 helps developer. |
| CONF-STAGE1-009 | Agent task seeds are safe and scoped. | One human with agents needs safe delegation from day one. | Stage 1 tasks show scope, risk_class, validation and rollback/compensation. | Agent task lacks risk class or validation. |
| CONF-STAGE1-010 | Manifest field matrix and unknown-field policy are enforced. | A service contract with silently ignored fields is unsafe for agents. | Validation report shows required/optional/extension fields, defaults, unknown-field decisions, profile precedence, field-level rule identity, timing/default/secret precedence and stable error codes. | Runtime starts from manifest with unknown ignored fields or ambiguous defaults. |
| CONF-STAGE1-011 | Local runtime profile has state and unsupported capability model. | Local runtime is the first product boundary. | Profile reports absent/starting/ready/degraded/blocked/stale/stopped/manual-external/unknown states, limits, unsupported features, route conflicts and cleanup. | Runtime limitation is discovered only after service start. |
| CONF-STAGE1-012 | Generated artifact inventory is complete and redacted. | Derived artifacts must not become product truth or leak local context. | Inventory marks source-of-truth, derived and local-state artifacts with generator, freshness, publish/ignore boundary, redaction and cleanup. | Generated artifact is committed/published as source-of-truth or contains secret/local context. |
| CONF-STAGE1-013 | Task and plugin boundaries are declared. | Stage 1 automation must be safe before it scales. | Tasks/plugins show owner, tooling, args, mounts, network, resources, timeout, secret boundary, risk, audit and structured result. | Task/plugin is an arbitrary command with unknown side effects. |
| CONF-STAGE1-014 | Command result contract works across UI/API/CLI/Agent API. | One human and agents need parseable outcomes. | Command fixtures cover create/start/stop/status/log/env/doc/debug/task/bootstrap plus blocked, unsupported, no-manifest, no-task, docs-missing and invalid-input cases; results include state, operation id, maturity, retryability, evidence, warnings, code/path/severity/remediation and next actions. | Binary availability or unstructured logs are treated as lifecycle readiness. |
| CONF-STAGE1-015 | Debug split and env handoff are secret-safe. | Local debug often runs service process outside the runtime. | Debug report distinguishes platform-managed dependencies, external service process, redacted env, dependency endpoints, routes, logs and cleanup. | Debug handoff exposes raw secret or hides dependency ownership. |
| CONF-STAGE1-016 | OCS manifest fixture covers the full Stage 1 service contract. | Stage 1 needs a reimplementation-ready manifest example without copying legacy source. | Fixture covers identity, scope, base/profile env precedence, component type/name/role/enabled/ownership, tasks, docs links, generated artifacts, unknown-field policy and secret references. | Manifest fixture omits identity/scope/env/component/task/docs/artifact/secret-reference behavior. |
| CONF-STAGE1-017 | Generator conformance fixtures prove derived artifact boundaries. | Generated files are useful only if their source and limits are visible. | Fixtures cover visible defaults, implicit platform components, generated env/artifact provenance, route/port conflicts and redacted debug handoff. | Generated artifact lacks provenance, conflict behavior or redaction evidence. |
| CONF-STAGE1-018 | Docs template fixture uses role-based support ownership. | Templates must not preserve personal-contact or private-context placeholders. | Docs fixture includes overview/API/architecture/runbook/FAQ with support owner role, escalation role and known limits. | Docs template contains personal/private placeholders or lacks support role. |
| CONF-STAGE1-019 | Local generator evidence is scoped to local readiness only. | Local generated runtime files must not imply private/public/federation readiness. | Stage 1 report marks local generator as local evidence and any non-local generator as preview, unsupported or blocked with maturity state. | Local generator is used as proof of private/public/federation readiness. |
| CONF-STAGE1-020 | Role scenario coverage matrix exists for Solo Developer Cloud. | Stage 1 must prove developer and agent journeys, not only command availability. | Scenario matrix links developer, service owner and AI-agent fixtures for create, run, observe, document, validate and safe contribution flows. | Stage 1 passes without reusable developer/agent scenario evidence. |
| CONF-STAGE1-021 | Documentation decision-memory evidence supports service handoff. | Stage 1 docs must let a future developer, support owner or agent recreate the product flow without hidden old source knowledge. | Report links docs package, ADR/no-ADR rationale, documentation decision-memory evidence, `SCENARIO-STAGE1-006`, `CR-DOCMEM-001..032`, source-safety result, owner, freshness and non-claims. | Service flow depends on undocumented decisions, raw source context, private examples or ownerless stale docs. |
| CONF-STAGE1-022 | Service dependency/deployment model evidence is reusable and source-safe. | Stage 1 dependency readiness must prove the service model and generated artifacts, not only a local start command. | Report links `CR-SVCDEPLOY-001..032`, `SCENARIO-STAGE1-007`, effective model, dependency graph, component ownership, generated artifact inventory, env classification, conflict preflight, portability gaps, source-safety and non-claims. | Local fixture values, generated env files, unsupported generator capability or ownerless dependencies are treated as readiness proof. |
| CONF-STAGE1-023 | Local bootstrap activation evidence exists for the developer runtime. | Developer loop cannot depend on hidden manual setup or unsafe config download. | Report links `CR-PRESBOOT-001..032`, trusted bootstrap asset/config evidence, preflight, runtime provider matrix, diagnostics, rollback/cleanup, source-safety and explicit Stage 2 non-claim. | Binary availability, config download or local runtime start is treated as complete private presence readiness. |
| CONF-STAGE1-024 | Controlled extension/task automation evidence is reusable and source-safe. | Stage 1 tasks, plugins, dependency updates and scaffolding can otherwise bypass policy, leak env values or imply production automation. | Report links `CR-EXTAUTO-001..032`, `SCENARIO-STAGE1-008`, automation kind, task-vs-plugin rationale, artifact trust, version policy, scope, env/secret boundary, argument schema, runtime budget, mutation/rollback, structured result, agent approval, source-safety and explicit production non-claim. | Local task/plugin execution, generated env/build files, dependency update or scaffold output is treated as safe CI/private/provider automation without managed-runner evidence. |
| CONF-STAGE1-025 | Developer workflow scenario evidence is reusable and source-safe. | Stage 1 must not treat binary availability, docs, run profiles or showcase examples as proof of a complete Solo Developer Cloud workflow. | Report links `CR-WORKFLOW-001..032`, `SCENARIO-STAGE1-009`, role intent, prerequisites, workflow steps, expected states, e2e scope, evidence confidence, negative fixtures, cleanup/handoff, lifecycle/dependency/automation/docs links, source-safety and explicit private/provider non-claims. | Stage 1 passes while e2e only proves binary availability, unstable path is marked ready, docs contain personal/private placeholders, cleanup is unknown or local workflow success is claimed as private/provider readiness. |
| CONF-STAGE1-026 | Reference service portfolio evidence is reusable and source-safe. | Stage 1 must not treat one sample, generated scaffold, local start or showcase fragment as proof that the service factory is ready. | Report links `CR-REFSVC-001..032`, `SCENARIO-STAGE1-010`, archetype registry, portfolio coverage matrix, service purpose/stage/non-goals, first useful behavior, contract source-of-truth, run-mode boundaries, dependency ownership, docs/template readiness, observability semantics, task/data/object/secret evidence, fixtures, support handoff, portability lessons, source-safety and explicit private/provider/public non-claims. | Stage 1 passes while required archetypes are missing, docs remain placeholders, demo values are treated as evidence, task semantics are unknown, support handoff is missing or reference service success is claimed as provider/public readiness. |

## Required Report Outcome

`stage1-service-ready` is passed when all hard gates pass, warnings are scoped,
and report names next-stage gaps without requiring Stage 2 capabilities.

## Profile Non-Goals

- Production multi-node private cloud.
- Public provider billing or tenant isolation.
- Federation sync.
- Global marketplace publication.
