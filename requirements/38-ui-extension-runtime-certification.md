# UI Extension Runtime Certification

Этот документ фиксирует продуктовые требования к сертификации UI extensions и
validation runtime в CloudRING. Он не выбирает frontend framework, validation
library, module format, browser engine или store implementation. Он задает,
что должно быть доказано, чтобы UI сервиса можно было безопасно встроить в
CloudRING portal/private store/provider surface, а validation rules были
одинаково понятны пользователю, API, CLI и AI-агентам.

`CR-UICERT-*` дополняет `CR-UX-*`, `CR-OCSCONTRACT-*`, `CR-SECSUPPLY-*` и
`CR-MKT-*`. Эти семейства уже говорят, что UI extension и validation contract
нужны. `CR-UICERT-*` добавляет reusable certification evidence: runtime
execution, browser/mobile behavior, accessibility, localization, error identity,
host authority, lifecycle cleanup, publication proof and explicit non-claims.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-UICERT-001 | UI extension certification must be a product gate, not a build success flag. | Store/provider publication changes user trust boundary. | Certification evidence states scope, profile, owner, runtime surface, validation status, blockers and non-claims before normal install or publication. |
| CR-UICERT-002 | UI extension must declare host authority and embedded authority separately. | Embedded UI must not take over portal permissions, navigation or lifecycle. | Evidence shows what the host controls, what the extension may request and which actions require explicit approval or scoped context. |
| CR-UICERT-003 | UI extension must have a typed embed descriptor. | Agents and host need stable contract instead of framework-specific wiring. | Descriptor covers mount target, inputs, outputs, context schema, capabilities, required permissions, route scope, theme scope, telemetry and support owner. |
| CR-UICERT-004 | Standalone development mode and embedded mode must be separated. | A local preview can hide host authority, policy, theme and lifecycle gaps. | Evidence marks standalone-only behavior, embedded-ready behavior, unsupported behavior and promotion blockers. |
| CR-UICERT-005 | Runtime certification must execute the extension in a representative host shell. | Unit/build checks do not prove real embedding. | Evidence includes host-shell run, mount result, scoped context use, visible state, error/fallback behavior and cleanup result. |
| CR-UICERT-006 | UI lifecycle must include mount, update, suspend, unmount and failure cleanup. | Extensions that only mount can leak state, listeners or stale authority. | Lifecycle evidence records each transition, allowed side effects, cleanup expectations, failure state and retry/rollback behavior. |
| CR-UICERT-007 | Extension failure must degrade locally and explain next action. | User should not lose the whole portal because one service UI fails. | Failure evidence shows fallback UI, support owner, affected scope, retry/disable path and agent-readable diagnostic summary. |
| CR-UICERT-008 | Context isolation must be explicit and testable. | Ambient global context is a policy and tenant-boundary risk. | Evidence proves extension receives only scoped context, cannot access forbidden host state and cannot expand authority without approval. |
| CR-UICERT-009 | Route, navigation and modal behavior must be host-contained. | Service UI must not fragment the CloudRING product experience. | Evidence verifies route scope, navigation ownership, back/close behavior, modal stacking and blocked host-navigation takeover. |
| CR-UICERT-010 | Theme and design-system compatibility must be certified. | App-store extensibility should feel coherent, not like unrelated control panels. | Evidence covers theme tokens or equivalent, typography/spacing constraints, dark/light or profile-specific modes, overflow behavior and visual regression status. |
| CR-UICERT-011 | Accessibility must be a hard certification dimension for user-facing UI. | Self-service fails when keyboard, screen reader or focus behavior is broken. | Evidence covers labels, error linkage, focus order, keyboard flow, contrast, landmark/semantic structure and known exceptions. |
| CR-UICERT-012 | Responsive/mobile behavior must be certified where the surface is available. | Admin/user flows may happen on constrained screens or embedded panels. | Evidence records supported viewport classes, overflow behavior, touch/keyboard limitations and unsupported cases. |
| CR-UICERT-013 | Localization and message governance must be explicit. | Hardcoded UI messages cannot serve many jurisdictions or support contexts. | Evidence records locale support, fallback behavior, message owner, translation freshness and unsupported languages. |
| CR-UICERT-014 | Validation phase semantics must be standardized. | Submit, blur, focus and reactive validation can produce different user outcomes. | Evidence defines phases, field states, submit-blocking behavior, stale/pending state and when errors are cleared or preserved. |
| CR-UICERT-015 | Field-level error lifecycle must be part of the contract. | Users and agents need to know why a field is blocked and how to fix it. | Evidence records field path, state, severity, message, code, remediation and visibility rules. |
| CR-UICERT-016 | Dependent validation rules must declare dependency graph and short-circuit behavior. | Conditional rules can silently change which errors appear. | Evidence shows rule dependencies, order, skip/stop behavior, affected fields and negative cases. |
| CR-UICERT-017 | Validation errors must have stable machine-readable identity. | Text changes should not break API/CLI/Agent parity or support automation. | Each error has stable code/id, field path, params schema, severity, human message, remediation and localization binding. |
| CR-UICERT-018 | UI/API/CLI/Agent validation parity must be proven for shared rules. | UI-only truth creates policy bypass and support confusion. | Certification links parity matrix, mismatch handling, accepted exceptions and authoritative source of each rule. |
| CR-UICERT-019 | Validation runtime must be bounded and safe. | Regex, large forms or repeated interactions can create latency or denial-of-service risk. | Evidence records input limits, rule count/size limits, timeout/performance budget, async/network policy and stress/negative results. |
| CR-UICERT-020 | Validation fixtures must cover happy, negative, edge and regression cases. | One component test cannot certify store/provider readiness. | Evidence includes representative fixtures for valid, invalid, dependent, localized, accessibility and agent-readable error cases. |
| CR-UICERT-021 | Real-browser or equivalent runtime evidence is required before certification. | Simulated component tests are useful but not enough for user-facing readiness. | Evidence states browser/runtime matrix, mobile/viewport scope, automation method, screenshots or equivalent proof and non-claims. |
| CR-UICERT-022 | Extension package must have provenance and immutable publication identity. | Store users need to know exactly what UI code is being installed. | Evidence records artifact identity, version, build provenance, dependency freshness, integrity/signing or equivalent verification and supersession. |
| CR-UICERT-023 | Publication certification must include compatibility matrix. | Host/runtime versions evolve, and extensions must not silently break. | Evidence lists supported host contract versions, unsupported versions, migration path, deprecation state and compatibility test status. |
| CR-UICERT-024 | Publication metadata must include owner, support and incident routing. | UI failures become product support events. | Store record has owner, support owner, escalation path, SLA/SLO relevance, evidence freshness and unknown-owner blocker. |
| CR-UICERT-025 | UI extension telemetry must be useful and redacted. | Support needs diagnostics without leaking tenant data or private context. | Evidence defines telemetry events, correlation, error categories, redaction/cardinality controls and forbidden payload classes. |
| CR-UICERT-026 | Extension permissions must be least-privilege and user-visible. | A UI extension can become an invisible authority escalation. | Certification lists permissions, rationale, user/admin visible consequences, approval class and denial behavior. |
| CR-UICERT-027 | Extension dependency/shared runtime policy must be explicit. | Shared frontend libraries can create version conflicts and supply-chain risk. | Evidence records shared runtime expectations, isolated dependencies, version conflicts, lock/freshness status and update policy. |
| CR-UICERT-028 | Agent review of UI certification must be bounded and non-executive by default. | AI agents should review evidence without gaining uncontrolled UI/runtime authority. | Handoff defines allowed review actions, forbidden raw context or secret retrieval, required approvals and validation needed. |
| CR-UICERT-029 | Certification states must be stage-aware. | Stage 1 local demo, Stage 3 private store and Stage 4 provider publication need different proof. | Evidence maps draft, local-ready, private-ready, provider-candidate, public-ready, deprecated and blocked states to required gates. |
| CR-UICERT-030 | UI certification must include source-safety treatment. | Frontend examples and bundles can leak private hosts, routes, tenant data or copied source. | Report records redaction, private-marker scan, strict-secret scan, copied-source check, asset review and forbidden-content result. |
| CR-UICERT-031 | Source-derived UI lessons must remain technology-replaceable. | Requirements must survive framework, validator and browser evolution. | Requirements and examples use product contracts, synthetic objects and generic runtime terms, not source-specific code or exact configuration. |
| CR-UICERT-032 | UI certification evidence must state explicit non-claims. | Build/test success can be mistaken for accessibility, security, publication or cross-browser proof. | Evidence says what is not proven: live browser run, accessibility, localization, provider publication, vulnerability absence, full history audit or external policy compliance unless separately shown. |

## Evidence Bundle

Minimum evidence bundle for UI extension/runtime certification:

1. UI extension identity, owner, support owner, stage/profile scope and
   publication state.
2. Typed embed descriptor, host authority boundary, scoped context and
   permission rationale.
3. Runtime host-shell execution evidence for mount/update/unmount/failure
   cleanup.
4. Validation phase/field/error contract with stable machine-readable identity.
5. Parity matrix across UI, API, CLI and Agent API where rules affect product
   decisions.
6. Accessibility, localization, responsive behavior and design-system
   compatibility evidence.
7. Browser/runtime matrix, bounded execution results and negative/regression
   fixtures.
8. Artifact provenance, immutable publication identity, dependency/shared
   runtime policy, telemetry redaction and source-safety scan.

## Stop Conditions

Stop and require owner/review when:

- an extension is published from standalone/local build evidence only;
- host authority, scoped context, permissions or lifecycle cleanup is unknown;
- validation rules affect policy/security/billing/lifecycle without parity
  evidence;
- error identity is only human text and has no stable code/path/remediation;
- browser/runtime, accessibility or localization evidence is absent while
  user-facing readiness is claimed;
- extension package lacks immutable identity, provenance or support owner;
- telemetry, examples or assets contain private context, endpoints, tenant data,
  credentials or copied source;
- source pass claims marketplace/provider readiness, vulnerability absence or
  full history coverage from prototype evidence alone.
