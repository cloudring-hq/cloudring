# Capability Contract - Open Cloud Standard

## Назначение

Open Cloud Standard - общий язык CloudRING для services, connectors,
marketplace, private store, provider presence, federation and AI-agents. Он
делает service не набором runtime-файлов, а переносимым продуктовым контрактом:
identity, capability, environments, dependencies, lifecycle, usage, health,
policy, portability, UI, docs, support and evidence.

Contract описывает what/why/evidence. Он не выбирает schema format, programming
language, runtime, orchestrator, API gateway or UI framework.

## Продуктовая Граница

- Service Manifest описывает продуктовый смысл сервиса и machine-readable
  contract.
- Capability Contract описывает, что сервис умеет и какие обязательства
  выполняет.
- Lifecycle Contract описывает allowed operations and states.
- Connector Contract позволяет existing service подключиться к CloudRING без
  переписывания всей реализации.
- Extension Contract позволяет расширять стандарт без изменения ядра.
- Standard Validation доказывает, что contract пригоден для humans, agents,
  conformance and marketplace.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-OCSCONTRACT-001 | Open Cloud Standard должен быть versioned product contract. | Federation and marketplace cannot rely on informal conventions. | Standard version, compatibility policy, deprecation policy and migration guidance are visible. |
| CR-OCSCONTRACT-002 | Service Manifest must declare stable service identity and ownership scope. | Service identity connects catalog, billing, support, audit and portability. | Manifest shows service id/name, owner, tenant/scope model, lifecycle state and support context. |
| CR-OCSCONTRACT-003 | Manifest must distinguish product service, component, dependency and runtime artifact. | Collapsing these concepts creates lock-in and operational confusion. | Contract shows service, components, dependencies and generated artifacts as separate entities. |
| CR-OCSCONTRACT-004 | Standard must declare mandatory and optional capabilities separately. | Ecosystem needs a low barrier without losing safety. | Conformance report identifies required, optional, unsupported and extension capabilities. |
| CR-OCSCONTRACT-005 | Manifest must support environment profiles and overrides. | One service must move across local, private, edge, provider and federation contexts. | Profiles show local/staging/production/private/edge/disconnected settings and non-secret overrides. |
| CR-OCSCONTRACT-006 | Manifest must never contain plaintext secrets. | Config and secret lifecycles have different risk. | Manifest uses secret references, brokered capabilities or explicit secret-binding requirements. |
| CR-OCSCONTRACT-007 | Dependencies must be declared as contracts, not instructions. | Manual dependency setup breaks repeatability and agent operations. | Dependencies include capability, version/compatibility, required policy, lifecycle and fallback/unsupported state. |
| CR-OCSCONTRACT-008 | Service lifecycle must be a standard state machine. | Marketplace, agents and providers need the same meaning for actions. | Lifecycle states and actions cover validate, publish, order, provision, update, suspend, resume, remove, export and migrate where applicable. |
| CR-OCSCONTRACT-009 | Lifecycle operations must be idempotent or describe repeat consequences. | Networks and agents retry. | Operation record includes idempotency/operation id or explicit duplicate behavior. |
| CR-OCSCONTRACT-010 | Usage resources must be declared before commercial publication. | Billing cannot be trusted without product-scoped usage. | Manifest lists usage resources, units, measurement scope, exclusions and non-commercial status where relevant. |
| CR-OCSCONTRACT-011 | Health/readiness/observability contract must be mandatory for runnable services. | Platform should manage services, not guess state. | Manifest declares health/readiness, metrics/logs/traces/events, retention expectations and redaction boundary. |
| CR-OCSCONTRACT-012 | Error semantics must be machine-readable and human-readable. | Users need clear errors; agents need actionable codes. | Standard error shape includes code, message, retryability, owner, user impact and evidence pointer where relevant. |
| CR-OCSCONTRACT-013 | Policy and placement requirements must be part of the service contract. | Jurisdiction, data residency and trust are product constraints. | Manifest declares data classes, allowed/forbidden locations, encryption/audit needs, provider class and approval needs. |
| CR-OCSCONTRACT-014 | Responsibility boundaries must be explicit. | Federation incidents cross organizations. | Contract identifies service owner, provider/operator, ISV, customer duties, support owner and escalation path. |
| CR-OCSCONTRACT-015 | Portability profile must be part of the service contract. | Anti-lock-in must be known before order. | Contract declares exportable data, metadata, state, compatible targets, limitations and restore/import evidence. |
| CR-OCSCONTRACT-016 | Service documentation must be linked to contract and lifecycle. | Docs must not become a forgotten site. | Manifest links overview, API, architecture, runbook, FAQ, support guide and conformance notes. |
| CR-OCSCONTRACT-017 | UI extension must use a typed embedding contract. | Marketplace services need UI without breaking portal trust. | UI declaration includes mount point, scoped context schema, inputs/outputs, allowed actions, route scope, locale/theme, validation API, telemetry API, permissions, isolation and support owner without raw credentials. |
| CR-OCSCONTRACT-018 | Validation rules must be both user-friendly and agent-readable. | Bad inputs should be caught before API calls. | Form/API validation distinguishes reactive, blur, submit or equivalent timing and returns readable message, stable rule identity, structured code, field/path and remediation hint. |
| CR-OCSCONTRACT-019 | Generated runtime artifacts must be derived and disposable. | Derived files should not become source-of-truth or local-state leakage. | Contract states which artifacts are generated, where they live, how they are regenerated and what must not be committed/published. |
| CR-OCSCONTRACT-020 | Service Connector must adapt external service to OCS without hiding limitations. | Existing services must join ecosystem safely. | Connector declares implemented capabilities, missing capabilities, mapping, validation, support owner and risk/limitations. |
| CR-OCSCONTRACT-021 | Connector must pass sandbox validation before marketplace/federation publication. | Connector is a trust boundary. | Validation evidence covers lifecycle, usage, health, error semantics, permissions and secret handling. |
| CR-OCSCONTRACT-022 | Extensions must be namespaced, versioned and compatibility-declared. | Innovation should not fork the standard silently. | Extension declares owner, purpose, mandatory/optional status, compatibility impact, conformance checks and deprecation path. |
| CR-OCSCONTRACT-023 | Standard must support service components with roles. | Stateful and composite services need more than one process. | Manifest can declare component roles such as primary/replica/cache/worker/api/ui or domain-specific equivalents without forcing implementation. |
| CR-OCSCONTRACT-024 | Standard must support service tasks as product operations. | Build, maintenance, migration and diagnostics should be repeatable. | Task declares purpose, inputs, environment, risk, idempotency, timeout, validation, rollback/compensation and allowed actor. |
| CR-OCSCONTRACT-025 | Standard must define conformance report shape. | Certification should be automatable and reviewable. | Report includes passed/failed checks, evidence, exceptions, non-goals, owner, freshness and next actions. |
| CR-OCSCONTRACT-026 | Standard must support backward-compatible evolution. | Services and providers cannot migrate instantly. | Change record shows version, breaking/non-breaking impact, migration window, deprecation path and affected users. |
| CR-OCSCONTRACT-027 | Standard must preserve human readability. | Founders, operators and auditors must understand the contract. | Contract can be reviewed without running implementation-specific tooling. |
| CR-OCSCONTRACT-028 | Standard must preserve machine actionability. | Agents need structured inputs for validation and planning. | Contract can drive validation, plan generation, conformance, catalog card and lifecycle operation. |
| CR-OCSCONTRACT-029 | Standard must be source-safe. | Requirements must not leak old implementation or pilot context. | Generated specs and reports contain generic product concepts, no private names, no source snippets and no secret values. |
| CR-OCSCONTRACT-030 | Standard must support local-to-global promotion. | A service should grow from local dev to private/public/federation without rewriting meaning. | Promotion path shows required evidence for each stage and explicit blockers/non-goals. |
| CR-OCSCONTRACT-031 | Service manifest schema must define required, optional and extension fields. | Agents need to know what is mandatory and what is safe extension. | Schema summary shows field purpose, type, default, allowed values, compatibility rule, deprecation rule and validation error code. |
| CR-OCSCONTRACT-032 | Environment profile precedence and secret binding must be explicit. | Local, private and provider settings must not drift or leak secrets. | Contract defines base/profile/override precedence, generated values, secret references, redaction behavior and forbidden raw-secret fields. |
| CR-OCSCONTRACT-033 | Dependency connection contract must be machine-readable. | A declared dependency is useful only if the platform knows how to connect and fail safely. | Dependency record declares type, role, instance name, connection outputs, readiness, fallback/degraded/unsupported state and owner. |
| CR-OCSCONTRACT-034 | Lifecycle action result must have a standard shape. | Humans and agents need the same interpretation of command outcomes. | Result includes state, operation id, idempotency/retryability, evidence links, warnings, error code, owner and next allowed actions. |
| CR-OCSCONTRACT-035 | Task must be modeled as a standard operation, not an arbitrary script. | Maintenance, migration and diagnostics need product semantics. | Task declares purpose, inputs, scope, mounts/data access, network access, resource limits, timeout, risk, validation and structured result. |
| CR-OCSCONTRACT-036 | UI embed descriptor must define trust, UX and support boundaries. | Embedded service UI must feel integrated without becoming a policy bypass. | Descriptor covers standalone vs host-controlled embed mode, mount/update/unmount/failure cleanup, route/navigation authority, inputs/outputs, permissions, theme contract, isolation, telemetry/redaction, validation and support owner. |
| CR-OCSCONTRACT-037 | Generated artifact provenance must be part of the standard. | Derived runtime files should be reproducible and disposable. | Artifact inventory records generator, source contract version, target profile, location, publish/ignore boundary, cleanup and regeneration command. |
| CR-OCSCONTRACT-038 | Validation and error objects must be shared across UI, API, CLI and Agent API where relevant. | Different surfaces should not disagree about what is valid. | Rule exposes stable rule id, human message key/template, machine code, field/path, timing trigger, params schema, severity, remediation, safety budget and UI/API/CLI/Agent parity status. |
| CR-OCSCONTRACT-039 | Manifest field matrix must be mandatory for each standard version. | Docs, parsers and generators drift when fields are implicit. | Matrix lists field path, owner, required/optional/extension status, type, default, profile behavior, validation code and deprecation state. |
| CR-OCSCONTRACT-040 | Unknown manifest fields must have explicit policy. | Silently ignored fields create false readiness and unsafe automation. | Validator rejects unknown mandatory-context fields or records accepted extension namespace with owner and compatibility impact. |
| CR-OCSCONTRACT-041 | Manifest defaults must be visible and reproducible. | Hidden defaults become lock-in and migration risk. | Validation report shows defaulted fields, source of default, profile override and user/agent-visible consequence. |
| CR-OCSCONTRACT-042 | Manifest maturity must be declared separately from implementation maturity. | A contract may exist while an action is experimental or unsupported. | Manifest/action report marks ready, preview, experimental, deprecated, unsupported or blocked with evidence and user-facing consequence. |
| CR-OCSCONTRACT-043 | Profile precedence must be testable. | Environment overrides are a common source of drift. | Conformance includes base/profile/local/secret/generated precedence examples and redacted effective configuration evidence. |
| CR-OCSCONTRACT-044 | Generated artifacts must reference the manifest field matrix they were derived from. | Derived files need traceability to avoid stale runtime state. | Artifact evidence includes source standard version, manifest digest/equivalent identity, field-matrix version, generator and freshness. |
| CR-OCSCONTRACT-045 | Validation code catalog must be stable and documented. | Agents and UIs need reliable remediation logic. | Catalog separates machine code from rendered message and records locale key, accessibility binding, severity, field/path, owner, remediation hint, alias/collision policy and compatibility/deprecation context. |
| CR-OCSCONTRACT-046 | Standard extensions must not weaken mandatory validation. | Extension freedom must not bypass compatibility or safety. | Extension validation runs after mandatory baseline and cannot override secret, identity, lifecycle, policy, billing, security or evidence requirements without owner-approved ADR exception. |

## Evidence

- Versioned standard document or schema summary.
- Service manifest sample without secret values.
- Manifest field matrix with required/optional/extension/deprecation policy.
- Unknown-field policy and validation code catalog.
- Manifest maturity/defaults/profile precedence report.
- Environment precedence and secret-binding validation report.
- Lifecycle operation contract and idempotency evidence.
- Lifecycle action result sample with evidence and next actions.
- Usage/health/error/observability declaration.
- Dependency connection contract and degraded/unsupported state sample.
- Task operation contract and structured result sample.
- Connector sandbox validation report.
- UI extension contract, typed context, lifecycle and validation rules.
- Generated artifact provenance inventory.
- Generated artifact source matrix/freshness evidence.
- Portability profile and restore/import evidence.
- Conformance report with exceptions/non-goals.
- Standard change/deprecation record.

## Stop Conditions

Agent обязан остановиться и запросить owner/ADR/approval, если:

- service has no manifest or stable identity;
- manifest schema has ambiguous required/optional/extension/deprecation rules;
- manifest has unknown ignored fields or undocumented defaults;
- manifest contains plaintext secret or private source context;
- environment/profile override could leak raw secret or hide generated value;
- profile precedence cannot be tested or explained;
- lifecycle operation lacks idempotency/repeat behavior;
- lifecycle result cannot be parsed by an agent;
- service is published without usage, health, responsibility or portability
  declaration where applicable;
- dependency requires manual setup without declared connection/degraded state;
- task has undeclared scope, risk, resource limit or structured result;
- connector hides unsupported capabilities;
- UI extension boundary, lifecycle, scoped context or permissions are unknown;
- validation returns different code/path/severity/remediation across required
  UI/API/CLI/Agent surfaces without explicit exception;
- extension breaks mandatory contract but claims compatibility;
- generated artifact becomes source-of-truth;
- generated artifact lacks source manifest/field matrix/freshness evidence;
- standard change breaks existing services without migration/deprecation path.

## Non-Goals

- Не выбирать конкретный schema format, protocol, runtime, language or UI
  framework.
- Не требовать одинаковую сложность от every service.
- Не обещать universal portability.
- Не превращать connector в способ bypass policy, secrets or conformance.
- Не копировать legacy source contracts verbatim.
