# Developer Workflow Scenario Evidence

## Назначение

Developer Workflow Scenario Evidence фиксирует требования к тому, как CloudRING
доказывает, что developer/service-owner/AI-agent могут пройти законченный
локальный продуктовый путь: install/bootstrap, create, validate, debug/run,
inspect, document, run bounded tasks, handle known unsupported states and clean
up with evidence.

Главный урок source slice: наличие CLI, README, IDE run profiles, showcase
services or thin e2e check is useful, but not enough. Product readiness starts
when workflow evidence proves role intent, preconditions, actions, expected
state, negative cases, source-safety and non-claims in one reproducible bundle.

Этот документ описывает what/why/evidence. Он не выбирает CLI syntax, IDE,
test framework, container runtime, docs engine, language or shell.

## Product Boundary

- Workflow scenario - reusable role journey from intent to validated outcome.
- Workflow evidence bundle - source-safe proof that the journey can be reviewed
  by humans and agents without raw logs, private paths, endpoints or commands.
- Run profile - developer convenience signal; not readiness proof unless linked
  to workflow contract and source-safety.
- E2E check - executable evidence; its claim is limited by what it actually
  covers.
- Showcase pattern - sanitized example of a supported integration pattern, not
  production proof.
- Negative fixture - explicit stop/degraded/unsupported case that prevents
  false readiness.
- Workflow confidence - documented strength of evidence: docs-only,
  run-profile-backed, fixture-backed, e2e-backed, live-run-backed or stale.

## Source-Derived Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| E2E evidence checked binary availability only. | Tool presence is not product journey readiness. | `CR-WORKFLOW-001`, `CR-WORKFLOW-006`, `CR-WORKFLOW-028` |
| Docs and run profiles covered create/debug/stop/env/docs/task/plugin flows. | Developer workflow exists as product intent and must become scenario evidence. | `CR-WORKFLOW-002..005`, `CR-WORKFLOW-011..019` |
| One documented lifecycle path was explicitly marked unstable while debug was preferred. | Unsupported and preferred paths must be visible readiness states. | `CR-WORKFLOW-007`, `CR-WORKFLOW-021` |
| Log viewing was scoped away from debug mode. | Workflow evidence must record mode boundaries. | `CR-WORKFLOW-020`, `CR-WORKFLOW-022` |
| Task and plugin examples inherited service context and arguments. | Workflow evidence must link to controlled automation and plugin trust boundaries. | `CR-WORKFLOW-016..017` |
| Service template requirements included observability and docs scaffold. | Template readiness must be workflow-proven, not only generated. | `CR-WORKFLOW-008..010`, `CR-SERVICEFACTORY-053` |
| Tests and fixtures covered env precedence and invalid names. | Negative fixtures should become reusable validation evidence with stable remediation. | `CR-WORKFLOW-012`, `CR-WORKFLOW-023..025` |
| Showcase docs included raw local access details and placeholder contacts. | Examples must be synthetic, role-based and contact/secret safe before publication. | `CR-WORKFLOW-026..027`, `CR-WORKFLOW-030` |
| Project state was legacy/not maintained. | Evidence must preserve lessons without claiming current support. | `CR-WORKFLOW-031..032` |

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-WORKFLOW-001 | Workflow readiness must prove role journey, not binary availability. | A tool can exist while the product flow is unusable. | Evidence covers role, intent, preconditions, action sequence, expected states, validation, cleanup and non-claims. |
| CR-WORKFLOW-002 | Each developer workflow must start from user intent. | Developers and agents need a task outcome, not a list of commands. | Scenario states goal, role, stage, capability, expected result and anti-lock-in relevance. |
| CR-WORKFLOW-003 | Workflow evidence must include prerequisites and bootstrap state. | Failures before the first action often look like product bugs. | Evidence links bootstrap activation, local runtime profile, required tools, config freshness and supported/unsupported setup states. |
| CR-WORKFLOW-004 | Workflow steps must share one lifecycle vocabulary across CLI/API/Agent API. | Run profiles, docs and tests should not describe different realities. | Step names map to command/action contract, expected state and structured result vocabulary. |
| CR-WORKFLOW-005 | Workflow evidence must include setup and teardown. | Local state leaks create repeated failures and false success. | Scenario records generated artifacts, runtime resources, retained data, cleanup result, orphan detection and irreversible warnings. |
| CR-WORKFLOW-006 | E2E scope must be stated precisely. | A tiny check should not become a broad readiness claim. | Evidence says whether it proves availability, command behavior, full journey, negative case or live runtime outcome. |
| CR-WORKFLOW-007 | Preferred, unstable, unsupported and deprecated paths must be explicit. | Users need the safe road, agents need stop conditions. | Workflow marks path maturity and blocks readiness if an unstable path is treated as default-ready. |
| CR-WORKFLOW-008 | Service template workflow must prove product foundations. | A scaffold can look complete while missing operability. | Evidence covers manifest, docs, runbook, tests, observability, support role and conformance gaps. |
| CR-WORKFLOW-009 | Template documentation must use role-based ownership, not personal placeholders. | Copied contacts become stale or unsafe source memory. | Docs fixtures use roles such as service owner/support owner/escalation owner and pass source-safety scan. |
| CR-WORKFLOW-010 | Showcase examples must declare what pattern they prove and what they do not prove. | Examples are learning tools, not production certification. | Each example links pattern, requirements, scope, non-claims, sanitized values and source-safety status. |
| CR-WORKFLOW-011 | Local debug workflow must distinguish dependency runtime from service process. | Debugging often runs the service outside platform control. | Evidence shows platform-managed dependencies, externally started service process, redacted env, logs, routes and cleanup. |
| CR-WORKFLOW-012 | Environment/profile workflow must prove precedence and redaction. | Env handoff is secret/topology-adjacent and easy to misread. | Fixtures show base/profile override behavior, effective report, redacted secret refs and forbidden raw-value output. |
| CR-WORKFLOW-013 | Component inspection workflow must classify service and platform components. | Developers need dependency truth without reading generated files. | Evidence lists component role, owner, access class, redaction, support boundary and unsupported states. |
| CR-WORKFLOW-014 | Documentation preview workflow must be checked as support evidence. | A docs server starting is not enough. | Evidence covers docs presence, navigation, runbook usefulness, renderer profile, source safety and graceful shutdown. |
| CR-WORKFLOW-015 | Log/status workflow must state runtime mode coverage. | Debug-mode and platform-managed logs can differ. | Evidence marks log source, supported modes, retention, redaction, gaps and support handoff. |
| CR-WORKFLOW-016 | Task workflow must link to controlled automation evidence. | Migration/seed/lint tasks can mutate state or expose env. | Scenario links task purpose, args, work context, risk, idempotency, result and `CR-EXTAUTO-*` evidence. |
| CR-WORKFLOW-017 | Plugin workflow must link to extension trust evidence. | Plugin examples can normalize broad executable authority. | Scenario links owner, permissions, service context, argument forwarding, audit, revocation and source-safety status. |
| CR-WORKFLOW-018 | Migration and seed workflows must be first-class repeatable scenarios. | Stateful setup should not remain bespoke local commands. | Evidence covers target component, data/state impact, idempotency, rollback/compensation and validation. |
| CR-WORKFLOW-019 | Workflow evidence must include human and agent handoff. | One founder with agents needs continuation without tribal memory. | Evidence states allowed actions, forbidden actions, approvals, validation needed, remaining gaps and next owner. |
| CR-WORKFLOW-020 | Mode boundaries must be tested or documented. | Users should not apply an action to the wrong runtime mode. | Negative fixture covers unsupported log/debug/start/stop/env/task/doc combinations where relevant. |
| CR-WORKFLOW-021 | Known unstable path must create warning or blocker, not silent pass. | Product honesty is part of readiness. | Readiness report marks unstable path, recommended alternative, owner and review trigger. |
| CR-WORKFLOW-022 | Workflow result must be structured and support-ready. | Screenshots or raw logs are weak for agents and support. | Result includes status, operation id, state transition, evidence refs, warning/error codes, remediation and support owner. |
| CR-WORKFLOW-023 | Negative fixtures must cover invalid identity and missing prerequisites. | Safe refusal proves product maturity. | Fixtures include invalid name/identity, missing manifest/config/runtime/task/docs and expected blocker/warning behavior. |
| CR-WORKFLOW-024 | Validation fixture confidence must be recorded. | Unit fixtures, docs and e2e tests prove different things. | Evidence labels docs-only, unit-fixture, generated-fixture, e2e, live-run, stale or unknown confidence. |
| CR-WORKFLOW-025 | Workflow evidence must preserve stable error identity and remediation. | Agents need machine-readable recovery, not prose errors. | Error includes code, field/path, severity, retryability, owner and remediation. |
| CR-WORKFLOW-026 | Workflow artifacts must be source-safe before entering requirements or examples. | Run configs, docs and examples can leak local paths, endpoints, contacts or secrets. | Evidence scan classifies and redacts paths, URLs, network values, env values, credentials, personal contacts and source-shaped snippets. |
| CR-WORKFLOW-027 | Personal contact data must not be part of reusable template or example evidence. | People and channels change and may be private. | Published fixtures use roles and safe escalation classes instead of names, handles, phones or emails. |
| CR-WORKFLOW-028 | Thin e2e evidence must be allowed but scoped. | Early projects need small checks without false confidence. | Report can include thin checks only with explicit non-claim and next deeper scenario/e2e needed. |
| CR-WORKFLOW-029 | Workflow evidence must support offline/private review. | Local/private development should survive missing source or hosted docs. | Evidence bundle is exportable with templates/examples and safe references, not raw source paths. |
| CR-WORKFLOW-030 | Workflow examples must use synthetic objects and sanitized values. | Agents copy examples; unsafe values become future leaks. | Examples use synthetic service/component/provider identities and generic safe values. |
| CR-WORKFLOW-031 | Legacy workflow source must not be treated as current support status. | Old implementations can be useful and unsupported at the same time. | Source pass records legacy status, current-tree/history limits and no-current-support non-claim. |
| CR-WORKFLOW-032 | Workflow lessons must update requirements without copying old command shape. | The goal is product memory, not command archaeology. | Requirement output describes intent, evidence and stop conditions with no exact commands, paths or raw snippets. |

## Evidence Shape

Minimum evidence for workflow readiness:

- role and intent;
- stage and capability scope;
- prerequisite/bootstrap/runtime state;
- step sequence and expected state vocabulary;
- source of truth for each step: doc, run profile, fixture, e2e, live run;
- structured result and support handoff;
- negative fixtures and stop cases;
- source-safety scan;
- confidence and non-claims.

## Stop Conditions

Agent обязан остановиться и запросить owner/ADR/approval, если:

- e2e binary availability is treated as full workflow readiness;
- docs/run profiles/showcase examples contain raw paths, endpoints, env values,
  credentials, personal contacts or source-shaped snippets;
- unstable/unsupported path is presented as ready;
- workflow lacks cleanup, support owner, negative cases or source-safety status;
- task/plugin workflow is used without controlled automation or trust evidence;
- local workflow success is claimed as private/provider/federation readiness;
- source-derived workflow evidence claims current support or full history without
  coverage proof.

## Non-Goals

- Не выбирать final CLI syntax, test framework, IDE, shell, runtime or docs
  renderer.
- Не превращать old run profiles into product API.
- Не требовать full live e2e for every early-stage flow, если scope честно
  ограничен.
- Не хранить raw run configs, paths, endpoints, contacts, command output or
  source snippets.
