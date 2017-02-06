# Capability Contract - Service Factory And Local Runtime

## Назначение

Service Factory And Local Runtime превращает создание cloud service в paved road:
developer or AI-agent can create, run, debug, document, validate, package and
promote a service from local loop to private/provider/federation readiness. Этот
слой сохраняет опыт локальной платформы: service template, manifest, tasks,
docs, generated artifacts, runtime backend abstraction, plugins and validation
should be product capabilities, not tribal knowledge.

Contract описывает product workflow. Он не выбирает конкретный language,
framework, container runtime, build tool or documentation engine.

## Продуктовая Граница

- Service Factory создает service candidate with OCS contract, docs, tests,
  observability and tasks.
- Local Runtime запускает service and declared dependencies locally through
  replaceable runtime profile.
- Bootstrap Activation prepares trusted config/assets and local runtime profile
  before developer or agent lifecycle actions rely on them.
- Task Library gives safe repeatable automation.
- Plugin Surface extends CLI/API/Agent API under permissions and trust boundary.
- Generated Artifacts are derived and disposable.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SERVICEFACTORY-001 | Developer must create a service from a supported template. | Correct defaults reduce decisions and future toil. | Template creates OCS manifest, source structure, docs, runbook, tests, observability and local runtime profile. |
| CR-SERVICEFACTORY-002 | Template must be stage-aware. | Stage 1 service should not pretend to be Stage 4 provider product. | Template marks current stage, future-stage non-goals, required evidence and promotion path. |
| CR-SERVICEFACTORY-003 | Service name and identifiers must be validated for portability. | DNS, URLs, federation and runtime targets impose constraints. | Create flow rejects non-portable names with clear human/agent-readable reason. |
| CR-SERVICEFACTORY-004 | Local environment must support declared dependencies. | Real services rarely run alone. | Local run plan includes required databases, storage, messaging, identity, secrets, network and observability dependencies or explicit unsupported state. |
| CR-SERVICEFACTORY-005 | Local runtime profile must be replaceable. | Desktop/runtime technologies change and can become lock-in. | Same service contract can run on another compatible local profile or shows documented limitation. |
| CR-SERVICEFACTORY-006 | Platform must check local resource prerequisites before heavy actions. | Resource failures should be clear before workload starts. | Preflight reports CPU/memory/storage/network/runtime availability and safe next action. |
| CR-SERVICEFACTORY-007 | Start/stop/status/log/debug/doc/env must be standard product actions. | Developer and agent should not remember backend-specific commands. | Service exposes standard local lifecycle actions with known states and errors. |
| CR-SERVICEFACTORY-008 | Service start must prepare environment through contract, not manual agreement. | Environment drift breaks repeatability. | Environment is derived from manifest/profile, redacted for secrets and recorded as generated artifact. |
| CR-SERVICEFACTORY-009 | Generated local artifacts must live outside product source-of-truth. | Local state should not pollute service repo or future requirements. | Generated artifacts have location, regeneration method, cleanup policy and ignore/publish boundary. |
| CR-SERVICEFACTORY-010 | Platform-owned build recipe should be default where possible. | Common build path reduces divergence. | Service can build/package through standard recipe; custom recipe requires explicit reason and conformance impact. |
| CR-SERVICEFACTORY-011 | Custom build/deploy recipe must be an explicit architecture exception. | Flexibility is needed but should remain intentional. | Exception links owner, why, portability impact, validation and review date. |
| CR-SERVICEFACTORY-012 | Task library must support repeatable service operations. | Build, tests, migrations and maintenance should be agent-operable. | Task declares purpose, inputs, environment, timeout, risk, idempotency, validation and rollback/compensation. |
| CR-SERVICEFACTORY-013 | Task execution must be isolated and bounded. | Tasks can become arbitrary scripts with hidden side effects. | Task plan shows mounted scope, allowed environment, secret boundary, network/data access and audit record. |
| CR-SERVICEFACTORY-014 | Task output must be evidence-ready. | Agents need proof of what happened. | Task result records status, logs summary, artifacts, validation, warnings and next action. |
| CR-SERVICEFACTORY-015 | Documentation must be part of the service lifecycle. | Service without docs cannot be supported by agents. | Docs include overview, API, architecture, runbook, FAQ, development flow and support context. |
| CR-SERVICEFACTORY-016 | Documentation must run locally and be validated. | Docs need fast feedback and not rot. | Local docs preview/check is available and linked to service manifest/conformance. |
| CR-SERVICEFACTORY-017 | Observability conventions must exist from first commit. | Retrofitting health later is expensive. | Template includes health/readiness, metrics/logs/traces/events conventions or explicit non-runtime exception. |
| CR-SERVICEFACTORY-018 | Debug flow must handle service and dependencies separately. | Complex local stacks fail in different layers. | Debug view distinguishes service, dependency, platform runtime and network issues. |
| CR-SERVICEFACTORY-019 | Local runtime must support multi-service ingress or equivalent routing. | Parallel development needs stable access to multiple services. | Profile shows routes, conflicts, names, ports and resolution for local services. |
| CR-SERVICEFACTORY-020 | Library/template updates must be versioned and reviewable. | Paved road evolves; services cannot be broken silently. | Update plan shows template/library version, impact, migration, validation and rollback. |
| CR-SERVICEFACTORY-021 | Plugin surface must have packaging, permission and capability declaration. | Plugins are executable trust boundaries. | Plugin declares name, owner, inputs, outputs, permissions, service context access, version and support owner. |
| CR-SERVICEFACTORY-022 | Plugin execution must be audited and secret-safe. | Extensions should not bypass platform governance. | Plugin run records actor, scope, arguments summary, secret boundary, result and evidence. |
| CR-SERVICEFACTORY-023 | Task library must be preferred over plugins for simple automation. | Not every workflow should become executable extension. | Guidance distinguishes safe task, controlled task, plugin and core feature. |
| CR-SERVICEFACTORY-024 | Service factory must support candidate publication. | Marketplace starts before public sale. | Service candidate can generate conformance report, service card draft, docs bundle and readiness blockers. |
| CR-SERVICEFACTORY-025 | Service factory must support AI-agent contribution safely. | One human with agents should create and evolve services. | Agent can scaffold, validate, run tasks and draft docs within scoped permissions and approval policy. |
| CR-SERVICEFACTORY-026 | Service factory must preserve source safety. | Generated artifacts and source-derived memory can leak private context. | Outputs avoid secret values, local paths, private names and source snippets; redaction checks are part of validation. |
| CR-SERVICEFACTORY-027 | Deprecated factory/runtime path must have migration. | Old development platform should not trap services. | Deprecation record shows replacement, affected services, migration path, timeline and support state. |
| CR-SERVICEFACTORY-028 | Local success must not imply production readiness. | Developer loop and provider operation are different promises. | Report distinguishes local-ready, private-ready, public-ready, federation-ready and missing evidence. |
| CR-SERVICEFACTORY-029 | Local runtime profile must describe backend capabilities and unsupported states. | Replaceable runtime requires more than a name. | Profile declares supported workload types, storage/network/ingress/secrets/observability capabilities, limits, degraded states and unsupported states. |
| CR-SERVICEFACTORY-030 | Preflight must be reusable by humans, CI and agents. | The same readiness question appears in every surface. | Preflight returns human summary and structured result with checks, severity, evidence, remediation and safe next action. |
| CR-SERVICEFACTORY-031 | Local command matrix must define stable action semantics. | CLI/API/Agent API should not diverge. | create/debug/start/stop/status/log/env/doc/task commands have states, arguments, outputs, errors, idempotency and readiness meaning. |
| CR-SERVICEFACTORY-032 | Debug mode must explicitly split dependency runtime from service process. | Local development often needs dependencies running while the service is started by IDE or debugger. | Debug plan marks platform-managed dependencies, externally/debugger-managed service, routes, env, logs and cleanup. |
| CR-SERVICEFACTORY-033 | Task runner contract must prevent hidden arbitrary automation. | Portable tasks are powerful and risky. | Runner enforces unique task names, declared image/tooling, args, mounts, network, resources, timeout, secret boundary, risk and structured result. |
| CR-SERVICEFACTORY-034 | Generated artifact inventory must distinguish source-of-truth, derived and local-state files. | Agents must know what can be deleted or regenerated. | Inventory declares file category, owner, generator, freshness, ignore/publish boundary, cleanup rule and regeneration path. |
| CR-SERVICEFACTORY-035 | Documentation check must validate support usefulness, not only site startup. | Docs should help future agents operate the service. | Check covers overview, API, architecture, runbook, FAQ, development flow, known limits and link from service manifest. |
| CR-SERVICEFACTORY-036 | Plugin manifest must declare trust boundary before execution. | Binary extensions can do anything unless bounded. | Manifest declares owner, version, inputs/outputs, permissions, service context, network/data/secret access, audit and support owner. |
| CR-SERVICEFACTORY-037 | Plugin runs must produce reviewable audit evidence. | Extensions should not become invisible local root. | Run evidence records actor, plugin version, command, scope, argument summary, permissions used, result, artifacts and redaction status. |
| CR-SERVICEFACTORY-038 | Template/runtime/config distribution must be versioned and provenance-aware. | Paved-road updates can break every future service. | Registry record shows version, source, integrity/provenance, compatibility, migration, rollback and deprecation state. |
| CR-SERVICEFACTORY-039 | Factory updates must produce migration plans for existing services. | Services should not be stranded on old templates. | Update report lists affected services, changes, breaking/non-breaking impact, validation, rollback and manual steps. |
| CR-SERVICEFACTORY-040 | Factory outputs must be agent-readable as well as human-readable. | One human with agents needs structured proof. | Commands return structured status, evidence links, warnings, next actions and stable error codes alongside human text. |
| CR-SERVICEFACTORY-041 | Local runtime state model must be explicit. | Local runtime is a product boundary, not just a tool process. | Runtime/profile state distinguishes absent, starting, ready, degraded, blocked, stale, stopped, manual/external and unknown with owner, cause and next action. |
| CR-SERVICEFACTORY-042 | Runtime preflight must include route and port conflict checks. | Local multi-service development fails when access paths collide. | Preflight reports route, port, name, certificate/trust and ingress conflicts with safe remediation. |
| CR-SERVICEFACTORY-043 | Unsupported runtime capability must be visible before execution. | A service should not fail halfway because profile limitations were hidden. | Runtime profile marks supported, degraded, manual, blocked, unknown and unsupported capabilities with consequence. |
| CR-SERVICEFACTORY-044 | Cleanup must be a standard lifecycle action for local runtime and artifacts. | Local state leaks create drift, security risk and confusing retries. | Cleanup plan lists dependencies, generated artifacts, volumes/state, secrets references, retained evidence and irreversible warnings. |
| CR-SERVICEFACTORY-045 | Command result must include maturity flag. | Legacy/preview actions should not be mistaken for ready product behavior. | Result marks ready, preview, experimental, deprecated, unsupported or blocked and links to evidence/non-goal. |
| CR-SERVICEFACTORY-046 | Command result must be correlation-ready. | Logs, tasks, artifacts and support need one operation thread. | Result includes operation id, correlation id, started/finished time, actor, target service/profile, evidence links and retryability. |
| CR-SERVICEFACTORY-047 | Service env handoff for debug must be explicit and redacted. | Debugging outside platform should not leak secrets or break repeatability. | Debug report shows redacted env, secret references, dependency endpoints, routes, logs and cleanup instructions. |
| CR-SERVICEFACTORY-048 | Template/runtime/config distribution must support offline/private profiles. | Private adoption cannot depend on permanent central connectivity. | Distribution record shows cached version, freshness, trust evidence, allowed offline use, update limits and sync recovery. |
| CR-SERVICEFACTORY-049 | Task and plugin selection must be policy-guided. | Simple automation should not become overpowered executable extension. | Factory guidance marks operation as core feature, safe task, controlled task or plugin with reason, risk and approval need. |
| CR-SERVICEFACTORY-050 | Stage 1 service candidate must produce a single readiness bundle. | Agents need one evidence package for promotion. | Bundle includes manifest validation, field matrix, runtime profile, command matrix, docs check, tasks/plugins, artifact inventory, observability, security and next-stage gaps. |
| CR-SERVICEFACTORY-051 | Local runtime bootstrap must have activation evidence before service lifecycle commands rely on it. | A service command can look broken when the underlying runtime/config was never safely activated. | Stage 1 readiness links presence bootstrap activation evidence for trusted config, preflight, runtime provider matrix, diagnostics, rollback/cleanup and source safety. |
| CR-SERVICEFACTORY-052 | Task, plugin, dependency and boilerplate automation must have controlled automation evidence before it contributes to readiness. | Local executable automation can look like paved-road product while hiding arbitrary code, env leakage, mutation side effects or prototype-only behavior. | Stage 1 readiness links `CR-EXTAUTO-001..032`, automation kind, owner, task-vs-plugin rationale, artifact trust, scope, env/secret boundary, rollback/compensation, structured result, agent approval and production non-claims. |
| CR-SERVICEFACTORY-053 | Developer workflow scenario evidence must be part of Stage 1 service readiness. | Template output, docs, run profiles or a CLI binary do not prove a complete developer journey. | Stage 1 readiness links `CR-WORKFLOW-001..032`, role intent, prerequisites, step sequence, e2e scope, evidence confidence, negative fixtures, cleanup/handoff, source-safety and private/provider non-claims. |

## Evidence

- Generated service candidate summary.
- Template readiness and version record.
- Local runtime profile and preflight report.
- Runtime state model and unsupported/degraded/manual-external capability report.
- Route/port conflict and cleanup plan.
- Local lifecycle action logs and states.
- Local command matrix and structured output samples.
- Command result maturity/correlation samples.
- Command result examples for ready, blocked, unsupported, manual/external,
  preview and not-implemented outcomes.
- Debug split plan for dependencies and service process.
- Redacted debug environment handoff report.
- Generated artifact inventory and cleanup boundary.
- Task definition and task result evidence.
- Documentation preview/check result.
- Plugin capability/permission declaration and audit record.
- Template/runtime/config registry provenance and migration record.
- Offline/private distribution freshness and trust report.
- Stage 1 service candidate readiness bundle.
- Presence bootstrap activation evidence for local runtime profile.
- Controlled extension/task automation evidence for tasks, plugins, dependency
  updates and boilerplate generation.
- Developer workflow scenario evidence with thin-e2e scope, run-profile
  confidence, negative fixtures, cleanup and source-safety.
- Candidate conformance report.
- Deprecated factory/runtime migration record.

## Stage Guardrails

- Stage 1 requires service template, local runtime, docs, tasks, observability and
  local validation.
- Stage 2 adds private runtime/profile readiness and admin-operable local
  dependencies.
- Stage 3 adds private store candidate publication and install/update/remove
  readiness.
- Stage 4 adds provider-facing packaging, support and billing readiness.
- Stage 5/6 require federation/global publication only after OCS conformance,
  policy and trust checks.

## Stop Conditions

Agent обязан остановиться и запросить owner/ADR/approval, если:

- template produces service without manifest, docs, observability or tests;
- local runtime prerequisite check fails or is unknown;
- local runtime bootstrap artifact/config/preflight is unknown but lifecycle
  readiness is claimed;
- task/plugin/dependency/boilerplate automation lacks controlled automation
  evidence but is used as readiness proof;
- developer workflow readiness is claimed from scaffold output, docs, run
  profiles or binary availability without workflow scenario evidence;
- runtime profile hides unsupported capability or resource limit;
- runtime profile treats manual/external operation as failure instead of
  explicit state;
- route/port/certificate/trust conflict is known but not reported;
- cleanup would remove state without retained evidence or irreversible warning;
- task has unknown side effects, no idempotency or no validation;
- task runner cannot prove mounts, network, resources, timeout or secret
  boundary;
- generated artifact is about to be committed/published as source-of-truth;
- plugin has undeclared permissions or secret access;
- plugin execution lacks audit evidence;
- factory/template update lacks migration and rollback path;
- command output cannot be interpreted by an agent for risky action;
- command maturity is preview/experimental but presented as ready;
- debug env handoff exposes raw secret value;
- offline/private distribution trust or freshness is unknown;
- custom build path weakens portability without ADR;
- local success is presented as production/provider/federation readiness;
- outputs contain private source context, secret value or local path.

## Non-Goals

- Не выбирать programming language, framework, container runtime or docs engine.
- Не превращать service factory в forced monorepo.
- Не требовать one template for every service class.
- Не разрешать plugins/tasks bypass security and conformance.
- Не считать scaffolded service готовым продуктом без evidence.
