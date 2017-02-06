# Service Dependency Deployment Model Evidence

Этот документ фиксирует требования к product-level evidence for service
dependency and deployment model. Он не описывает, каким генератором или runtime
надо пользоваться. Он фиксирует, что CloudRING должен понимать о сервисе,
его зависимостях, профилях, generated artifacts and local/runtime boundaries,
чтобы сервис можно было переносить, поддерживать человеком с AI-агентами и
продвигать между stages без vendor lock-in.

## Requirements

| ID | Requirement | Why | Acceptance |
|---|---|---|---|
| CR-SVCDEPLOY-001 | Service dependency/deployment evidence must be separate from lifecycle command evidence. | Команда запуска может работать, но не доказывать, что dependency graph, profiles and generated artifacts are portable product contracts. | Readiness links a dedicated service dependency/deployment evidence bundle when service dependencies or generated runtime artifacts are claimed. |
| CR-SVCDEPLOY-002 | Service identity must be stable across source, generated artifacts and runtime profiles. | Anti-lock-in fails if service identity changes when generator, runtime or profile changes. | Evidence shows service id/name, namespace/scope, owner and profile refs before generation or promotion. |
| CR-SVCDEPLOY-003 | Profile resolution must produce an effective service model. | Base defaults and local/private/provider overrides can silently change behavior. | Evidence shows base values, profile overrides, generated values, omitted values, source of each value and visible consequences. |
| CR-SVCDEPLOY-004 | Profile overrides must be stage-aware and consequence-aware. | A local override can be safe in development and unsafe in private/provider operation. | Effective model marks local-only, private-ready, provider-ready, unsupported, degraded and future-stage values. |
| CR-SVCDEPLOY-005 | Dependencies must be modeled as product capabilities, not fixed technology names. | Technologies change; the product need is database, object storage, secret broker, messaging, tracing or task runtime capability. | Dependency contract records capability class, purpose, owner, state, portability class and allowed backend implementations. |
| CR-SVCDEPLOY-006 | Service-owned components and platform-owned components must be distinct. | Support and failure ownership differ when a component belongs to the service versus the platform presence. | Evidence separates service components, platform components, external dependencies, owner, support owner and lifecycle responsibility. |
| CR-SVCDEPLOY-007 | Dependency instance identity must be deterministic and collision-safe. | Multiple dependencies of the same class are normal; ambiguous names create wrong wiring and broken operations. | Each dependency instance has stable id, display name, role, profile scope and collision policy. |
| CR-SVCDEPLOY-008 | Dependency connection outputs must be typed, classified and redacted. | Generated connection settings can contain credentials, topology or local-only endpoints. | Output contract marks type, data class, secret boundary, publishability, redaction rule, owner and freshness. |
| CR-SVCDEPLOY-009 | Generated environment artifacts must be treated as secret-adjacent by default. | Env handoff often mixes safe config, topology and credentials. | Env artifact has classification, redacted preview, retention rule, publish boundary and scan status before agent handoff. |
| CR-SVCDEPLOY-010 | Demo or local fixture credentials must block promotion unless reclassified. | Prototype values are useful for local proof but dangerous as readiness evidence. | Promotion report rejects local/demo credentials or marks them replaced by brokered references with owner approval. |
| CR-SVCDEPLOY-011 | Local-only dependency behavior must not be presented as production readiness. | Local test components can hide HA, security, backup, support and policy gaps. | Readiness separates local fixture, private presence, provider presence and federation dependency claims. |
| CR-SVCDEPLOY-012 | Unsupported dependency or generator capability must fail before artifact generation. | Half-generated runtime files create support debt and false confidence. | Unsupported capability returns blocked/unsupported state with reason, affected profile, owner and safe next action. |
| CR-SVCDEPLOY-013 | Multiple dependency instances must include route, port, storage and state conflict evidence. | Same-class dependencies can collide even when their names differ. | Preflight reports route/port/storage/state conflicts, remediation options and unresolved blockers. |
| CR-SVCDEPLOY-014 | Generated artifacts must be disposable and traceable to source model. | Generated runtime files should never become the hidden source of truth. | Artifact inventory records source model id/version, generator id/version, target profile, freshness, checksum or equivalent identity, cleanup and regeneration rule. |
| CR-SVCDEPLOY-015 | Generator input and output contracts must be explicit. | Agents need to know what was requested and what was produced. | Evidence records request fields, selected profile, dependency lists, generated files, warnings, unsupported states and non-claims. |
| CR-SVCDEPLOY-016 | Generator mode must distinguish partial, complete, preview and unsupported output. | A partial local artifact is useful but cannot be sold as provider readiness. | Output marks generation mode, maturity, supported profiles and profile-specific blockers. |
| CR-SVCDEPLOY-017 | Dependency startup order must be represented as readiness dependency, not only runtime syntax. | Start order is not readiness; services need health and usable connection proof. | Dependency graph has edges, readiness condition, timeout/failure behavior and user/agent-visible state. |
| CR-SVCDEPLOY-018 | Runtime network exposure must be intentional and profile-scoped. | Default local ports and routes become security and support risks when promoted. | Evidence lists exposed routes/ports, purpose, profile, access boundary, conflict check and unsupported exposures. |
| CR-SVCDEPLOY-019 | Runtime artifact identity must be immutable before publication or provider use. | Mutable image names or generator defaults cannot prove what will run. | Publication requires artifact identity, provenance, source model link, validation result and approved exceptions. |
| CR-SVCDEPLOY-020 | Observability dependencies must be modeled as dependency outputs. | Hardcoded tracing/logging endpoints break portability and source-safety. | Observability output contract records endpoint reference, redaction class, profile scope and fallback when absent. |
| CR-SVCDEPLOY-021 | Data dependency roles must distinguish application, migration, maintenance and read-only access. | Operational safety requires different credentials and privileges for runtime and schema changes. | Data dependency evidence lists role classes, allowed actions, owner, rotation, audit and stop condition if roles are collapsed. |
| CR-SVCDEPLOY-022 | Task and migration actions must consume dependency references, not hidden strings. | Tasks become brittle and unsafe when they embed unresolved connection details. | Task evidence links dependency refs, required roles, redacted effective command, dry-run status and rollback/compensation. |
| CR-SVCDEPLOY-023 | Generated artifact output must be deterministic enough for review. | Agents and humans need meaningful diffs to approve changes. | Regeneration report shows stable ordering or normalized diff, changed files, added/removed dependency outputs and review status. |
| CR-SVCDEPLOY-024 | Empty or minimal service model must be accepted only as draft evidence. | Minimal services are useful for onboarding, but do not prove dependency/runtime maturity. | Conformance can mark minimal model as draft/local-ready with explicit missing dependency, observability, docs or support evidence. |
| CR-SVCDEPLOY-025 | Service examples must cover multiple dependency classes without freezing implementation choices. | Future agents need concrete scenarios, but examples must not become technology lock-in. | Synthetic examples include database-like, object-storage-like, secret-broker-like, messaging-like and observability-like capability classes as replaceable abstractions. |
| CR-SVCDEPLOY-026 | Dependency model evidence must include support ownership. | When a dependency fails, support must know whether service owner, platform owner or external provider acts. | Evidence records support owner, escalation path, evidence bundle, SLA/SLO relevance and unknown-owner blocker. |
| CR-SVCDEPLOY-027 | Dependency model evidence must include portability and exit story per dependency class. | A service can be portable overall while one dependency traps state or operations. | Each dependency records export/import/restore, replacement path, residual data, unsupported movement and accepted non-portability. |
| CR-SVCDEPLOY-028 | Dependency model readiness must be stage-aware. | Stage 1 local proof, Stage 2 private autonomy and Stage 4 provider offer need different evidence. | Evidence maps required-now, warning, future-stage gap, non-goal and not-applicable states per profile. |
| CR-SVCDEPLOY-029 | Conformance must require dependency/deployment evidence whenever dependencies or generated runtime artifacts are claimed. | Readiness from manifest presence or successful local start is too weak. | Readiness report links effective model, dependency graph, artifact inventory, env classification, preflight, source safety and non-claims. |
| CR-SVCDEPLOY-030 | Agent handoff must show safe generated diffs and forbidden material. | AI agents should help review/generate artifacts without receiving credentials or private topology. | Handoff includes allowed actions, redacted diff, forbidden raw values, approvals and validation needed. |
| CR-SVCDEPLOY-031 | Source-derived dependency lessons must remain source-safe. | Requirements must survive source disappearance without leaking old context or copied configs. | Pass output contains product abstractions, synthetic examples and scans; it excludes raw paths, private names, exact commands, endpoints, secrets and copied source blocks. |
| CR-SVCDEPLOY-032 | Dependency/deployment evidence must state explicit non-claims. | A generated local artifact is not a proof of live runtime, security, backup, provider readiness or full source coverage. | Evidence lists what it proves, what it does not prove, validation performed, gaps, owner and next review trigger. |

## Evidence Bundle

Minimum evidence bundle for dependency/deployment readiness:

1. Effective service model with profile resolution.
2. Dependency graph with capability classes, instances, owners and readiness
   edges.
3. Generated artifact inventory with source model, generator, target profile,
   freshness and cleanup/regeneration rules.
4. Secret-adjacent environment classification and redacted preview.
5. Route, port, storage and state conflict report.
6. Dependency role matrix for application, migration, maintenance and read-only
   access where relevant.
7. Portability/exit note per dependency class.
8. Source-safety scan and explicit non-claims.

## Stop Conditions

Stop and require owner/review when:

- a generated env/artifact contains raw credential, token, private endpoint or
  source-private path;
- a local fixture or demo value is used to claim private/provider readiness;
- dependency owner or support owner is unknown;
- generated runtime artifacts are treated as source of truth;
- unsupported generator/dependency capability is presented as ready;
- multiple dependency instances lack conflict evidence;
- dependency portability/exit is unknown but anti-lock-in is claimed.
