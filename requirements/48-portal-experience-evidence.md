# Portal Experience And Self-Service UI Evidence

Этот документ фиксирует продуктовые требования к доказательству готовности
портала CloudRING. Он не выбирает frontend framework, сборщик, дизайн-систему,
portal shell или конкретный runtime. Его задача - не дать пустой оболочке,
документационному landing page, локальной демо-сборке или смонтированному
компоненту выдать себя за готовый self-service портал.

`CR-PORTALUX-*` дополняет `CR-UX-*`, `CR-SELF-*`, `CR-UICERT-*`,
`CR-DESIGNQ-*`, `CR-AGOPS-*`, `CR-MKT-*`, release, support and billing
requirements. Эти семейства уже говорят, каким должен быть опыт, self-service,
embedded UI, marketplace, support и financial evidence. `CR-PORTALUX-*`
связывает их на уровне portal experience evidence: что пользователь, оператор,
провайдер, разработчик, support, governance owner и AI-агент реально могут
понять, сделать, проверить и передать дальше через единый продуктовый путь.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-PORTALUX-001 | Portal readiness must be an evidence gate, not a frontend build or navigation claim. | Портал является рабочим контуром доверия, а не только страницей или bundle. | Evidence states surface, stage, role coverage, owner, journeys, states, blockers, source-safety and explicit non-claims before portal readiness is claimed. |
| CR-PORTALUX-002 | Portal surface must have clear product identity. | Пользователь должен сразу понимать, где он находится и чем управляет. | Surface identity includes product area, role, environment/presence scope, tenant/customer scope where allowed, owner and support boundary. |
| CR-PORTALUX-003 | Portal must expose role entrypoints for promised actors. | Ролевая навигация без действий оставляет пользователя в справочнике. | Claimed roles have entrypoints for user, admin, developer/ISV, provider, support, governance and agent where stage scope promises them. |
| CR-PORTALUX-004 | Documentation surface and operational portal surface must be explicitly separated. | Docs help understand, but readiness requires doing, seeing state and receiving evidence. | Portal evidence marks which links are docs, which are actions, which are reports, and which docs-only surfaces are non-claims. |
| CR-PORTALUX-005 | Each role must have a first useful task path. | Self-service starts when a role can reach outcome, not when it can browse sections. | Evidence covers first task, prerequisites, current state, steps, success criteria, blocked state and handoff for each claimed role. |
| CR-PORTALUX-006 | The start screen must not be blank, placeholder-only or demo-only when readiness is claimed. | A blank portal creates false confidence and hides missing product work. | Portal proof includes non-empty role-aware state, meaningful empty state, next action and explicit demo/development labels where applicable. |
| CR-PORTALUX-007 | Navigation must be task-centric, not only component-centric or document-centric. | Users come with intent such as order, recover, publish, inspect, export or dispute. | Navigation maps intents to product actions, evidence views, reports, docs and support paths without forcing internal architecture knowledge. |
| CR-PORTALUX-008 | Search and discovery must work by intent, capability and constraint where claimed. | Cloud choice is driven by outcome, price, jurisdiction, support and trust, not by internal names. | Search/discovery evidence covers capability, service, region/presence, policy, trust, price/support and unsupported/no-match explanations for the stage. |
| CR-PORTALUX-009 | Portal actions must map to the shared UI/API/CLI/Agent API intent contract. | Parallel surfaces become dangerous when they describe different work. | Each visible action links to canonical intent, allowed surfaces, state transition, result object, evidence refs and unavailable-surface explanation. |
| CR-PORTALUX-010 | Portal states must use the shared lifecycle and readiness vocabulary. | Humans and agents need the same interpretation of ready, blocked, stale, degraded and disputed states. | State evidence maps visible labels to machine-readable state family, owner, cause, impact, freshness and next action. |
| CR-PORTALUX-011 | Consequences must be visible before action. | Cloud operations affect money, data, policy, SLA, support and exit options. | Before confirmation, portal shows cost/credit impact, policy/trust effect, data movement, support/SLA boundary, rollback/exit and required approval where relevant. |
| CR-PORTALUX-012 | Blocked and degraded portal states must explain a safe next step. | Self-service fails when refusal gives only a red status. | Blocked/degraded evidence includes reason, owner, affected constraint, remediation, alternative, approval path or no-compatible-option explanation. |
| CR-PORTALUX-013 | Empty, loading, validation, warning, error and success states must be evidence-backed. | Edge states are where users and agents lose trust. | Evidence covers visible message, machine-readable code/state, retry/safe action, support handoff, telemetry and source-safe diagnostic summary. |
| CR-PORTALUX-014 | High-impact actions must require reviewable confirmation. | Portal buttons can mutate infrastructure, money, access, trust or data residency. | Confirmation record includes actor, scope, consequence summary, approval class, expiry/revocation where needed, evidence refs and final result. |
| CR-PORTALUX-015 | Portal must produce support-ready handoff when a flow cannot finish safely. | A blocked journey should preserve context instead of starting support from zero. | Handoff links intent, current state, blocker, owner, affected user/service, diagnostics, billing/support refs, safe next actions and non-claims. |
| CR-PORTALUX-016 | Provider portal journeys must bind offers, orders, instances, support and billing views. | Public provider readiness is commercial and operational, not just catalog publication. | Provider/tenant evidence links offer, plan, order, entitlement, instance, usage/billing, support case, SLA and credit/dispute state with party-scoped views. |
| CR-PORTALUX-017 | Developer and ISV portal journeys must bind docs, manifest, workflow and certification evidence. | A service creator needs product readiness feedback, not scattered commands and prose. | Evidence shows template/manifest status, dependency/workflow checks, UI/runtime certification, publication blockers, docs links and support handoff. |
| CR-PORTALUX-018 | Admin portal journeys must bind health, capacity, policy, update and recovery evidence. | Private/provider operation needs one calm control surface for repeated work. | Admin evidence covers health, capacity, policy violations, update plan/apply/validate, backup/restore/failover freshness, incidents and guided remediation. |
| CR-PORTALUX-019 | Tenant/user portal journeys must bind instance, cost, SLA, provider chain and exit path. | Anti-lock-in is only real when the user can see and act on ownership and portability. | User evidence shows service state, owner/provider/presence, price forecast, SLA/support, dependencies, export/migration options and limitations. |
| CR-PORTALUX-020 | Agent portal view must be inspectable but non-executive by default. | AI agents should help understand and prepare without silently clicking risky actions. | Agent handoff defines readable evidence, draftable plans, forbidden executions, approval needs, source-safety and final evidence requirements. |
| CR-PORTALUX-021 | Portal modules must separate standalone, embedded, documentation and production modes. | Local demos and docs previews can hide host authority, policy and lifecycle gaps. | Evidence labels each mode, allowed claims, unsupported behavior, host/context assumptions and promotion blockers. |
| CR-PORTALUX-022 | Portal module/provider contract must declare intent, owner, host surface and allowed actions. | A mounted component is not a product surface unless the host understands what it is for. | Contract covers surface identity, role, owner, context, actions, required permissions, lifecycle, support owner, evidence refs and non-claims, while runtime certification remains in `CR-UICERT-*`. |
| CR-PORTALUX-023 | Portal bundle or embedded surface must have artifact identity and release provenance when shipped. | Users need to know which portal experience is active and supportable. | Evidence links immutable artifact identity, release/promotion state, rollback/retention, compatibility, source-safety and current support owner. |
| CR-PORTALUX-024 | Development/demo behavior must never be accepted as publication proof. | Dev integration conveniences can bypass production trust boundaries. | Readiness report states dev-only behavior, production behavior, forbidden dev carryover and required release/certification evidence. |
| CR-PORTALUX-025 | Documentation landing/navigation alone must not prove portal readiness. | A well-structured guide is valuable but cannot prove live self-service. | Conformance treats docs-only role cards, static links or command references as supporting evidence, not as operational portal proof. |
| CR-PORTALUX-026 | Onboarding must show progress, prerequisites and success evidence. | New users need to know what is ready, what is missing and how to finish. | Onboarding evidence includes role goal, prerequisites, progress state, next step, success metric, skipped/blocked reason and support/agent handoff. |
| CR-PORTALUX-027 | Accessibility, localization and responsive behavior must be evidence or explicit gaps. | Portal readiness includes people, devices and jurisdictions, not only happy-path desktop UI. | Evidence records supported locales/viewports/accessibility checks, known exceptions, owner, remediation and non-claims. |
| CR-PORTALUX-028 | Portal self-service completion must be measurable. | A portal that cannot measure completion cannot improve or prove usefulness. | Metrics cover started/completed/blocked flows, time to first value, support handoff, drop-off reasons, retry/recovery and source-safe aggregation. |
| CR-PORTALUX-029 | Portal views must be party-scoped and evidence-scoped. | Federation and provider commerce require different truths for tenant, provider, ISV, support and governance. | Evidence proves each actor sees allowed state, hidden state is justified, restricted evidence is redacted and over-sharing is blocked. |
| CR-PORTALUX-030 | Portal experience scenarios must include happy, blocked, degraded, support and agent paths. | A polished happy path cannot prove operational readiness. | Scenario evidence covers at least one role journey with success, no-match/blocked, degraded/error, support handoff and agent-readable review path. |
| CR-PORTALUX-031 | Source-derived portal requirements must remain technology-replaceable. | Portal lessons should survive frontend, runtime and docs tooling changes. | Requirements and examples use product contracts, synthetic objects and generic surface terms, not source-specific code, package names, commands or private paths. |
| CR-PORTALUX-032 | Portal evidence must state explicit non-claims. | It is easy to overclaim from a demo shell, docs site, screenshot or local build. | Evidence says what is not proven: live self-service, production release, accessibility, localization, embedded runtime, security, billing/support readiness or full source/history coverage unless separately shown. |

## Evidence Bundle

Minimum evidence bundle for portal experience readiness:

1. Portal surface identity, stage/profile scope, role coverage, owner and support
   boundary.
2. Role-to-intent journey map with first useful task, prerequisites, state
   vocabulary, success criteria, blocked/degraded/error behavior and handoff.
3. Cross-surface action mapping for UI, API, CLI and Agent API, including
   unavailable-surface explanations and shared result/evidence refs.
4. Consequence-before-action proof for cost, policy, trust, data movement,
   support/SLA, rollback/exit and approval.
5. Portal module/provider contract for standalone/embedded/docs/production
   modes, allowed actions, context, lifecycle and non-claims.
6. Support-ready, billing-aware and party-scoped evidence links where portal
   journeys touch provider, tenant, support, SLA, credit, dispute or settlement
   state.
7. Release/artifact identity for shipped portal bundles or embedded surfaces,
   plus source-safety result and explicit dev/demo limitations.
8. Accessibility, localization, responsive behavior, completion metrics and
   scenario coverage with happy, blocked, degraded, support and agent paths.

## Stop Conditions

Stop and require owner/review when:

- portal readiness is claimed from a blank screen, placeholder, local dev mode,
  static docs landing or screenshot alone;
- role entrypoints do not lead to first useful tasks with success/blocker
  criteria;
- visible actions lack shared UI/API/CLI/Agent API intent, result or evidence
  mapping;
- consequences for cost, policy, trust, support, SLA, data movement or exit are
  hidden before high-impact action;
- blocked/degraded/error states have no owner, reason, safe next step or
  support-ready handoff;
- a module is embedded without declared owner, host surface, context, allowed
  actions, lifecycle, support owner or non-claims;
- shipped portal assets have no artifact identity, release/promotion evidence,
  rollback/retention or source-safety result;
- party-scoped views leak restricted tenant, provider, financial, support or
  diagnostic evidence;
- agent review can execute risky portal actions without approval;
- evidence contains private names, endpoints, raw source snippets, exact
  commands/configuration, credentials, personal contacts or copied source shape.
