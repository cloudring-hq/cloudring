# Agent-Readable Specification Templates

Этот документ задает product-level templates для CloudRING specifications.
Они нужны, чтобы будущие AI-агенты могли создавать service contracts,
conformance reports, scenario fixtures and source coverage manifests без
доступа к старым исходникам и без переноса приватного контекста.

Templates здесь не являются implementation schemas. Они фиксируют обязательные
смысловые поля: что доказывается, для кого, почему, где граница, какие evidence
нужны, какие blockers останавливают работу и какие действия разрешены агенту.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SPECTPL-001 | CloudRING must maintain agent-readable templates for recurring specification artifacts. | Без шаблонов агенты будут каждый раз заново изобретать форму доказательств. | `templates/` contains OCS manifest, conformance report, role scenario and source coverage manifest templates. |
| CR-SPECTPL-002 | Templates must preserve product meaning and avoid implementation lock-in. | Шаблон должен пережить смену runtime, schema format, language or provider. | Template fields describe identity, purpose, scope, evidence and limits, not framework-specific commands. |
| CR-SPECTPL-003 | OCS manifest template must express service-as-product. | Сервис должен быть reimplementation-ready без старых source files. | Template covers identity, ownership, users, lifecycle, dependencies, usage, health, policy, portability, UI, docs, support and evidence. |
| CR-SPECTPL-004 | OCS manifest template must separate source-of-truth from generated artifacts. | Derived runtime files must not become hidden product contract. | Template has explicit generated artifact inventory, provenance, publish/ignore boundary and freshness. |
| CR-SPECTPL-005 | Conformance report template must distinguish current blockers, warnings, waivers, stale evidence and future-stage gaps. | "Готово" должно быть проверяемым и честным. | Report template includes status taxonomy, blocker class, evidence freshness, exceptions, owners and next actions. |
| CR-SPECTPL-006 | Conformance report template must be safe for human and agent handoff. | Следующий агент должен понимать, что можно делать дальше. | Template includes allowed actions, forbidden actions, required approvals, validation needed and remaining gaps. |
| CR-SPECTPL-007 | Role scenario fixture must start from user intent, not system internals. | CloudRING is a product experience, not a bundle of backend components. | Scenario fixture includes role, stage, intent, trigger, preconditions, flow, evidence, failure states and stop conditions. |
| CR-SPECTPL-008 | Role scenario fixture must cover policy, cost, trust, support and exit where relevant. | Anti-lock-in and self-service fail when consequences are hidden. | Scenario fixture has consequence-before-action section and explicit exit/rollback/compensation story. |
| CR-SPECTPL-009 | Source coverage manifest template must prevent overclaiming. | Passing scans is not proof of full source/history analysis. | Template records source class, file/ref counts, exclusions, method, coverage mode, non-claims and next bounded pass. |
| CR-SPECTPL-010 | Source coverage manifest template must include source-safety treatment. | Source-derived memory must not leak private context or copied source shape. | Template includes anonymization, secret-class handling, copyright-safety, redaction and validation summary. |
| CR-SPECTPL-011 | Templates must use stable requirement, ADR, stage, workstream and profile references. | Agents need graph links, not prose-only memory. | Each template has fields for requirement_refs, adr_refs, stage_refs, workstream_refs and conformance_refs where relevant. |
| CR-SPECTPL-012 | Templates must include non-goals and unsupported states. | Honest limits are a product feature. | Each template can express non-goals, unsupported/degraded/blocked states and future-stage dependencies. |
| CR-SPECTPL-013 | Templates must be composable across stages. | Stage 1 evidence should promote into Stage 2..6 without rewriting meaning. | Template fields support local, private, provider, federation, global and self-evolving scopes. |
| CR-SPECTPL-014 | Templates must keep human-readable Markdown as the source review surface. | Humans and agents must share one memory. | Template files are Markdown with structured blocks, tables and examples. |
| CR-SPECTPL-015 | Templates must not require old source tree access. | The requirements folder must survive source disappearance. | A new agent can fill templates from requirements, ADR, stage docs and conformance profiles alone. |
| CR-SPECTPL-016 | Templates must expose evidence freshness and owner. | Stale or ownerless evidence creates false readiness. | Every critical evidence item has owner, freshness, review trigger and stale behavior. |
| CR-SPECTPL-017 | Templates must treat waivers as scoped product risks. | Exceptions should not silently become standards. | Waiver fields include scope, reason, risk, compensation, approver, expiry/review and linked requirement/ADR. |
| CR-SPECTPL-018 | Templates must define validation summary without storing raw unsafe match output. | Validation needs reproducibility without leaking sensitive strings. | Template records check names, scope and pass/fail counts, not raw private matches or source snippets. |
| CR-SPECTPL-019 | Evidence bundle template must be a standalone contract. | `evidence_refs` without structure cannot prove readiness. | Template defines evidence id, class, scope, safe reference, owner, freshness, redaction/source-safety, validation result, limitations and review trigger. |
| CR-SPECTPL-020 | OCS supporting templates must cover field matrix, precedence, validation catalog and generated artifact provenance. | A manifest example is not enough to reimplement the standard safely. | Template family includes manifest field matrix, environment/profile precedence, validation code catalog and generated artifact provenance examples. |
| CR-SPECTPL-021 | Profile change record template must govern conformance evolution. | Self-evolving conformance must not weaken checks silently. | Template records changed checks, reason, affected profiles, compatibility impact, rollout/migration note, owner, evidence and review trigger. |
| CR-SPECTPL-022 | Role scenario corpus must include safe synthetic fixtures. | Scenario validation should not require real source data or private customer context. | `scenarios/` contains synthetic catalog, role coverage matrix and stage scenario fixtures. |
| CR-SPECTPL-023 | Agent task and workstream outputs must reference template/evidence artifacts. | Free-form agent output is hard to audit and continue. | Agent/workstream objects can reference template version, conformance report, evidence bundles, coverage manifest and validation summary. |
| CR-SPECTPL-024 | Every reusable template must include machine-checkable source-safety block. | Source safety must be a field, not only a principle. | Template records sensitivity class, redaction status, copy-risk status, forbidden-content result, owner/reviewer decision and stop-if-unknown behavior. |
| CR-SPECTPL-025 | Product design quality review must have a reusable template. | Design quality should be comparable across stages and agents instead of subjective review prose. | Template covers role intent, consequences, alternatives, provider economics, jurisdiction overlay, failure handling, human-agent parity, metrics, owner, decision and source-safety. |
| CR-SPECTPL-026 | OCS information model must have a reusable template. | Schema governance needs durable artifact shape, not scattered prose. | Template covers model version, artifact kinds, field registry, core field catalog, unknown fields, extensions, validation catalog, conformance suite, change governance and source-safety. |
| CR-SPECTPL-027 | Billing runtime evidence must have a reusable template. | Money-flow readiness should not be recreated as prose after every usage or settlement review. | Template covers receipt/status, event identity, idempotency conflict, batch semantics, durable/volatile intake, backpressure, shutdown drain, quarantine/replay, access freshness, release history, settlement freeze and source-safety. |
| CR-SPECTPL-028 | Stateful recovery readiness must have a reusable template. | Restore and failover proof should not be rebuilt as one-off runbook prose. | Template covers topology, backup/archive, restore, PITR, failover, audit findings, capacity, access roles, agent controls, history coverage and source-safety. |
| CR-SPECTPL-029 | Documentation decision memory must have a reusable template. | Docs and ADR lessons should not remain scattered prose that future agents cannot validate or safely reuse. | Template covers docs package, ADR/no-ADR rationale, source-pass links, feedback triage, owner, freshness, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-030 | Secret runtime readiness must have a reusable template. | Credential runtime proof should not be inferred from encryption, source code or one-off operational prose. | Template covers secret reference boundary, scope binding, key/certificate custody, reconciliation status, install/delete behavior, RBAC, health/metrics, rotation/degraded behavior, release evidence, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-031 | Service dependency/deployment model evidence must have a reusable template. | Dependency graph, profile resolution and generated artifact proof should not be recreated as prose after every service generator review. | Template covers effective service model, dependency graph, connection outputs, generated artifacts, preflight, data roles, portability, stage scope, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-032 | Base OS image readiness evidence must have a reusable template. | Image factory readiness should not be recreated as prose after every build, profile or promotion review. | Template covers image identity, build input classification, install/provision summary, guest readiness, cleanup/sealing, artifact lifecycle, first-boot smoke, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-033 | UI extension runtime certification evidence must have a reusable template. | Embedded UI and validation runtime proof should not be recreated as prose after every store/provider publication review. | Template covers typed embed descriptor, host authority, lifecycle, validation phases, parity, browser/runtime proof, accessibility/localization, artifact identity, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-034 | Settlement closure evidence must have a reusable template. | Financial closeout, dispute and participant-share proof should not be recreated as one-off finance prose. | Template covers closure run, input manifest, reconciliation, freeze, invoice/credit/refund trace, participant shares, dispute hold/release, closeout export, approvals, release/history, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-035 | Presence bootstrap activation evidence must have a reusable template. | Install/bootstrap proof should not be recreated as ad hoc command notes after every local/private activation review. | Template covers activation workflow, artifact identity, distribution mode, config schema, preflight, runtime provider matrix, diagnostics, rollback/cleanup, infrastructure profile, agent approval, source-safety, blockers, non-claims and handoff. |
| CR-SPECTPL-036 | Controlled extension and task automation evidence must have a reusable template. | Task, plugin, dependency and boilerplate automation should not be reviewed from raw commands or local logs. | Template covers automation kind, owner, selection rationale, artifact trust, version policy, execution scope, env/secret boundary, mutation/rollback, structured result, conformance link, agent approval, source-safety, blockers, non-claims and handoff. |
| CR-SPECTPL-037 | Service registry/catalog publication evidence must have a reusable template. | Publication proof should not be inferred from static files, seed rows, manifests or local debug logs. | Template covers registry identity, visibility, lifecycle, publication plan, policy result, evidence links, sync/cache, source coverage, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-038 | Developer workflow scenario evidence must have a reusable template. | Workflow readiness should not be inferred from binary availability, run profiles, docs or showcase examples. | Template covers role intent, prerequisites, product steps, negative cases, cleanup, handoff, linked evidence, e2e scope, confidence, source-safety, blockers and non-claims. |
| CR-SPECTPL-039 | Release environment promotion evidence must have a reusable template. | Release readiness should not be inferred from build success, CI entrypoints, tags, badges or local archives. | Template covers module identity, dependency/toolchain evidence, checks, runner semantics, immutable artifact, environment bundle, approval, promotion, rollback, retention, source-safety, blockers and non-claims. |
| CR-SPECTPL-040 | Product service integration contract evidence must have a reusable template. | Integration readiness should not be inferred from API docs, generated specs, token existence or local tests alone. | Template covers product identity, scoped access, resource lifecycle, docs/spec/runtime drift, submission semantics, fixtures, support handoff, decommission, source-safety, blockers and non-claims. |
| CR-SPECTPL-041 | Support diagnostics evidence must have a reusable template. | Support readiness should not be inferred from scattered logs, probes, generated docs or unimplemented export surfaces. | Template covers target identity, lifecycle state, correlation, primary failure story, operational signals, image/stateful diagnostics, export control, redaction, retention, validation, blockers and non-claims. |
| CR-SPECTPL-042 | Support case/SLA/credit evidence must have a reusable template. | Provider support, SLA and credit decisions should not be reconstructed from free-form tickets, diagnostics or billing receipts. | Template covers case binding, support ownership, support boundary, service promise, SLA clock, lifecycle/communication, diagnostics/billing/settlement links, credit/refund review, party views, source-safety, agent handoff, blockers and non-claims. |
| CR-SPECTPL-043 | Portal experience evidence must have a reusable template. | Provider portal and self-service UI readiness should not be inferred from docs navigation, blank shells, screenshots or local builds. | Template covers surface identity, role journeys, action parity, shared states, consequences, mode claims, support/billing links, party-scoped views, module contract, metrics, source-safety, blockers, non-claims and agent handoff. |
| CR-SPECTPL-044 | Reference service portfolio evidence must have a reusable template. | Golden-service, showcase and boilerplate readiness should not be inferred from one sample, docs scaffold, local start or integration demo. | Template covers portfolio identity, archetype registry, service entries, first useful behavior, contract/run-mode boundary, dependency ownership, docs/template readiness, observability, task/data/object/secret evidence, fixtures, support handoff, source-safety, blockers, non-claims and agent handoff. |

## Template Index

- [templates/ocs-service-manifest-template.md](templates/ocs-service-manifest-template.md)
- [templates/ocs-supporting-contract-templates.md](templates/ocs-supporting-contract-templates.md)
- [templates/conformance-report-template.md](templates/conformance-report-template.md)
- [templates/evidence-bundle-template.md](templates/evidence-bundle-template.md)
- [templates/profile-change-record-template.md](templates/profile-change-record-template.md)
- [templates/role-scenario-fixture-template.md](templates/role-scenario-fixture-template.md)
- [templates/source-coverage-manifest-template.md](templates/source-coverage-manifest-template.md)
- [templates/product-design-quality-review-template.md](templates/product-design-quality-review-template.md)
- [templates/ocs-information-model-template.md](templates/ocs-information-model-template.md)
- [templates/billing-runtime-evidence-template.md](templates/billing-runtime-evidence-template.md)
- [templates/stateful-readiness-evidence-template.md](templates/stateful-readiness-evidence-template.md)
- [templates/documentation-decision-memory-template.md](templates/documentation-decision-memory-template.md)
- [templates/secret-runtime-readiness-evidence-template.md](templates/secret-runtime-readiness-evidence-template.md)
- [templates/service-dependency-deployment-evidence-template.md](templates/service-dependency-deployment-evidence-template.md)
- [templates/base-os-image-readiness-evidence-template.md](templates/base-os-image-readiness-evidence-template.md)
- [templates/ui-extension-runtime-certification-template.md](templates/ui-extension-runtime-certification-template.md)
- [templates/settlement-closure-evidence-template.md](templates/settlement-closure-evidence-template.md)
- [templates/presence-bootstrap-activation-template.md](templates/presence-bootstrap-activation-template.md)
- [templates/controlled-extension-task-automation-template.md](templates/controlled-extension-task-automation-template.md)
- [templates/service-registry-catalog-publication-template.md](templates/service-registry-catalog-publication-template.md)
- [templates/developer-workflow-scenario-evidence-template.md](templates/developer-workflow-scenario-evidence-template.md)
- [templates/release-environment-promotion-evidence-template.md](templates/release-environment-promotion-evidence-template.md)
- [templates/product-service-integration-contract-template.md](templates/product-service-integration-contract-template.md)
- [templates/support-diagnostics-evidence-template.md](templates/support-diagnostics-evidence-template.md)
- [templates/support-case-sla-credit-evidence-template.md](templates/support-case-sla-credit-evidence-template.md)
- [templates/portal-experience-evidence-template.md](templates/portal-experience-evidence-template.md)
- [templates/reference-service-portfolio-evidence-template.md](templates/reference-service-portfolio-evidence-template.md)

## Usage Rules

1. Use templates as evidence contracts, not as implementation schemas.
2. Keep examples generic and source-safe.
3. Link every filled template to requirements, ADR, stage and conformance
   profile where possible.
4. Mark unknown evidence as `unknown`, `warning` or `blocked`; never as passed.
5. Record non-goals and future-stage gaps explicitly.
6. Stop if filling a template would require raw source snippets, private names,
   credentials, internal locations, hostnames, tenant data or exact operational
   commands.

## Non-Goals

These templates are not:

- code generation formats;
- final Open Cloud Standard schema choice;
- deployment instructions;
- legal contracts;
- permission to bypass ADR, policy or owner approval;
- a place to store raw source inventory or private operational details.
