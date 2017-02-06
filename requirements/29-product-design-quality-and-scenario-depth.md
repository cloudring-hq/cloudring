# Product Design Quality And Scenario Depth

Этот документ превращает "простую и красивую платформу" в проверяемое
продуктовое требование. Для CloudRING design quality означает не декор, а
способность роли быстро понять задачу, последствия, альтернативы, владельца
поддержки, экономику, jurisdiction impact и путь выхода до того, как действие
изменит деньги, данные, доверие или доступность.

Quality review is a conformance artifact. It must be readable by a human and an
AI agent, source-safe and independent of a particular frontend, runtime,
framework or provider implementation.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-DESIGNQ-001 | Product design quality must be treated as readiness evidence, not optional polish. | Cloud provider can be technically correct and still unusable or unsafe for one human plus agents. | Readiness report can link a product design quality review for each user-impacting capability. |
| CR-DESIGNQ-002 | Each primary flow must be verified through a task-based fixture. | Static screens do not prove that a role can finish work. | Fixture names role, intent, trigger, consequence before action, success, failure and evidence. |
| CR-DESIGNQ-003 | Flow entry points must start from role intent and outcome. | Users buy outcomes such as service, recovery, support or exit, not internal platform objects. | First visible decision can be phrased as the role's goal without naming internal subsystem first. |
| CR-DESIGNQ-004 | Before any meaningful action, the product must show cost, provider chain, jurisdiction, policy decision, trust state, support owner and exit or rollback path where relevant. | Hidden consequences create lock-in, billing disputes and unsafe automation. | Review marks each consequence as visible, not-applicable or blocking. |
| CR-DESIGNQ-005 | Recommendations and defaults must explain why this choice is suggested and why alternatives are worse or blocked. | An opaque recommendation becomes hidden vendor lock-in. | Review includes recommended option, at least one alternative and explanation for blocked alternatives when they exist. |
| CR-DESIGNQ-006 | Marketplace and service-store decisions must support comparison, substitution and portability warnings. | App-store convenience must not hide dependency traps. | Service card or decision fixture includes compatible alternatives, portability score or explicit non-portability warning. |
| CR-DESIGNQ-007 | Provider economics must be understandable before commercial commitment. | A federated cloud breaks if buyers and providers cannot reason about money, credits and obligations. | Review covers buyer price, provider-visible revenue/fee/settlement impact, credit/refund path and dispute evidence. |
| CR-DESIGNQ-008 | Provider economics must not expose irrelevant private commercial internals. | Transparency should explain the transaction without leaking unrelated business data. | Review separates buyer-visible, provider-visible, federation-visible and confidential fields. |
| CR-DESIGNQ-009 | Jurisdiction overlay must be a first-class product choice. | Anti-lock-in includes legal and data-residency mobility, not only technology portability. | Review shows data location, participant jurisdiction class, policy decision, fallback and appeal path. |
| CR-DESIGNQ-010 | Policy-denied and jurisdiction-denied paths must offer safe alternatives or explicit no-safe-alternative result. | A denial without next step pushes users to manual exceptions. | Blocked scenario includes explanation, alternative search, approval path or stop reason. |
| CR-DESIGNQ-011 | Degraded, disconnected and stale states must keep local autonomy visible. | Private/edge operation is a core anti-lock-in promise. | Review shows what remains available locally, what is blocked and how evidence freshness is restored. |
| CR-DESIGNQ-012 | Support handoff must be visible before and after failure. | Cross-provider support fails when users cannot see owner, SLA and evidence. | Flow shows support owner, SLA clock, escalation state and evidence bundle link. |
| CR-DESIGNQ-013 | Human UI, API, CLI and Agent API must expose the same product facts for the same decision. | One human plus agents cannot operate from inconsistent realities. | Review compares surfaces for terms, state, consequence, error and evidence parity. |
| CR-DESIGNQ-014 | No surface may introduce a product promise that is absent from the shared contract. | UI-only promises become support debt and automation traps. | Review links visible action to requirement, scenario, OCS, policy or conformance reference. |
| CR-DESIGNQ-015 | Interaction quality must prefer calm density, stable layout, readable hierarchy and predictable controls over decorative spectacle. | Cloud operations require scanning, comparison and repeated action. | Review checks no critical text is hidden, unstable, overflowing, decorative-only or disconnected from action. |
| CR-DESIGNQ-016 | Complexity must be progressively disclosed. | CloudRING must expose power without forcing every user to understand every layer first. | Flow has summary, consequence, explanation, details and raw evidence levels where relevant. |
| CR-DESIGNQ-017 | Money, data movement, policy exception, trust downgrade, destructive lifecycle and cross-provider action must require explicit consent or approval boundary. | These actions carry durable risk. | Review records risk class, approver, confirmation text meaning and rollback or compensation story. |
| CR-DESIGNQ-018 | Negative paths must be as designed as happy paths. | Real readiness is proven when the product refuses safely. | Scenario set covers warning, blocked, manual-review, disputed, stale, degraded and rollback/exit states where relevant. |
| CR-DESIGNQ-019 | Every design quality review must name owner, reviewer and unresolved gaps. | Anonymous quality feedback does not become product memory. | Review has owner, reviewer, decision, gap list, next action and Stage 7 learning link. |
| CR-DESIGNQ-020 | Design regressions must feed the learning loop. | Repeating UX/support pain should become requirement, check, runbook or explicit no-change decision. | Review can produce requirement update, conformance check, scenario fixture, runbook or no-change rationale. |
| CR-DESIGNQ-021 | Quality evidence must be source-safe and synthetic by default. | The requirements memory must remain shareable and reimplementable. | Reviews and examples do not contain real customers, providers, endpoints, source paths, code snippets or secrets. |
| CR-DESIGNQ-022 | Product quality must be measured with explicit metrics. | Quality that is not measured will regress under implementation pressure. | Review links relevant `CR-METRIC-044..050` metrics or states why they are not-applicable. |
| CR-DESIGNQ-023 | Portfolio/global views must compare providers, jurisdictions and economics without becoming the hidden owner of all lifecycle actions. | Global discovery must reduce lock-in without creating a new central lock-in. | Review distinguishes discovery/recommendation owner from lifecycle/support/settlement owners. |
| CR-DESIGNQ-024 | A stage cannot claim product experience readiness with only happy-path scenarios. | Cloud platforms fail through ambiguous edge cases. | Stage evidence includes at least one deeper negative or tradeoff scenario for the stage scope. |

## Review Model

| Review Area | Must Prove | Typical Evidence |
|---|---|---|
| Intent | Role can start from a real goal. | Task fixture, service/store/provider journey, support case. |
| Consequence | User sees cost, policy, provider, trust, support and exit impact before action. | Decision summary, API/CLI/Agent output, conformance report. |
| Choice | User can compare options and understand defaults. | Alternative matrix, blocked alternative explanation, portability warning. |
| Economics | Buyer/provider/federation money states are understandable and auditable. | Order, usage, credit, settlement and dispute evidence. |
| Jurisdiction | Data and participant constraints are visible and enforceable. | Policy decision, data-location disclosure, appeal or fallback path. |
| Failure | Product refuses safely and gives next step. | Negative scenario, support bundle, rollback/exit path. |
| Parity | Human and agent surfaces share the same facts. | Surface parity checklist and agent-readable output. |
| Source Safety | Review can be kept in requirements without leaking old context. | Source-safety block and validation summary. |

## Required Artifacts

- [templates/product-design-quality-review-template.md](templates/product-design-quality-review-template.md)
- [examples/product-design-quality-review-example.md](examples/product-design-quality-review-example.md)
- [scenarios/role-coverage-matrix.md](scenarios/role-coverage-matrix.md)
- [scenarios/stage6/SCENARIO-STAGE6-003-jurisdiction-overlay-choice.md](scenarios/stage6/SCENARIO-STAGE6-003-jurisdiction-overlay-choice.md)

## Stop Conditions

Agent must stop and request owner review when:

- a flow changes money, data, trust, policy or destructive lifecycle without
  visible consequence and approval boundary;
- the design review cannot identify support owner, rollback/exit or evidence
  for a failure path;
- an alternative is hidden even though portability, jurisdiction or cost differ;
- a recommendation cannot explain why it is recommended;
- UI/API/CLI/Agent API disagree about state or consequences;
- review text would include real provider, customer, endpoint, source path,
  copied source structure, credential or private context.

## Non-Goals

This document does not define visual branding, final UI components, legal terms,
pricing formulas, provider margin policy or implementation architecture. It
defines product-quality evidence that future implementations must satisfy.
