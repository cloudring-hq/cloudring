# Service Registry Catalog Publication Evidence

## Назначение

Service Registry Catalog Publication Evidence фиксирует требования к тому, как
CloudRING превращает service manifest, registry record and catalog card в
управляемую продуктовую правду.

Главный урок source slice: список файлов, статический asset endpoint, seed
таблица или локальный service manifest полезны как ранние сигналы, но не
доказывают готовность service catalog. CloudRING должен уметь доказать, кто
публикует service, зачем он доступен, в каком scope, какой version/readiness
обещан, какие артефакты и support boundaries стоят за записью, как запись
изменяется, снимается и синхронизируется без потери локального контроля.

Этот документ описывает what/why/evidence. Он не выбирает registry backend,
database schema, package format, object storage, orchestrator, UI framework or
search engine.

## Product Boundary

- Service registry record - canonical product identity of service or
  service version inside CloudRING.
- Catalog card - user-facing and agent-facing projection of registry record
  with compatibility, readiness, support, trust, portability and lifecycle
  consequences.
- Publication request - explicit owner action that asks to create, update,
  deprecate, suspend or remove a catalog-visible record.
- Publication event - auditable state transition with actor, reason, evidence,
  policy result and rollback/compensation expectation.
- Registry snapshot - immutable or replayable view of the registry at a
  known time/profile so agents can reproduce decisions.
- Local catalog cache - private/offline view used by presence without making
  a global service the owner of local lifecycle.
- Sync ledger - scoped record of imported/exported registry changes for
  private, provider, federation and global stages.

## Source-Derived Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| A service manifest was the local source of service information. | Manifest is an input to product truth, but publication needs validation, owner, scope and evidence. | `CR-CATREG-001..005`, `CR-CATREG-011` |
| Static assets were distributed through a registry-like service. | Asset distribution and catalog publication are different promises. | `CR-CATREG-008..010`, `CR-CATREG-022` |
| A minimal registry table stored service identity. | Name/namespace is a useful start, but not enough for support, readiness, compatibility or lifecycle. | `CR-CATREG-002`, `CR-CATREG-011..012` |
| Seeded service lists existed for platform-known services. | Seed/import is bootstrap evidence only until provenance, freshness, owner and policy are known. | `CR-CATREG-009`, `CR-CATREG-018` |
| Developer docs separated manifest, components and tasks. | Catalog publication must summarize dependencies and controlled automation without copying raw local runtime details. | `CR-CATREG-013..014`, `CR-CATREG-021` |
| The legacy platform bundle has no local git history in the provided source root. | Coverage must distinguish current-tree signals from unavailable history. | `CR-CATREG-027`, `CR-SRCOV-003` |
| The old implementation was marked as not maintained. | Registry/catalog truth must survive implementation replacement and source disappearance. | `CR-CATREG-028`, `CR-CATREG-032` |

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-CATREG-001 | Registry должен быть product control plane для service truth, а не только списком файлов, образов или YAML. | Catalog влияет на install, support, trust, portability and agent decisions. | Registry record has purpose, owner, scope, lifecycle state, evidence refs and policy status. |
| CR-CATREG-002 | Service identity должна быть stable, unique within scope and collision-safe. | Name collisions turn local convenience into marketplace/support ambiguity. | Identity includes service id, publisher/owner scope, version scope, namespace/collision policy and rename/deprecation path. |
| CR-CATREG-003 | Service manifest должен быть input, not authority by itself. | A local file can be stale, incomplete, unsafe or unsupported. | Publication validates manifest, records effective model, rejects unknown critical fields and links source-safe validation result. |
| CR-CATREG-004 | Registry record, catalog card, offer, install plan and service instance must remain separate entities. | Mixing them breaks audit, support, pricing, rollback and portability. | Each entity has its own id, lifecycle state, owner, evidence and relationships. |
| CR-CATREG-005 | Publication intent must be explicit. | A discovered service file should not silently become installable product. | Request names actor, owner, target audience, visibility, readiness target, reason and approval requirements. |
| CR-CATREG-006 | Registry lifecycle must include create, update, suspend, deprecate, unpublish and remove. | Store trust depends on controlled change, not only initial discovery. | Lifecycle events are auditable and expose affected cards, offers, installs, instances, entitlements and support state. |
| CR-CATREG-007 | Publication must produce plan before changing visibility or installability. | Publishing can create security, support, billing and lock-in consequences. | Plan shows evidence, policy result, compatibility impact, support impact, rollback/compensation and user-visible state changes. |
| CR-CATREG-008 | Registry snapshots must be reproducible. | Agents need to explain why a service was visible, hidden or blocked at decision time. | Snapshot records profile, time, source version, policy version, imported changes and stale/degraded state. |
| CR-CATREG-009 | Static asset distribution must not count as catalog readiness. | A reachable artifact endpoint does not prove product owner, support, compatibility or lifecycle. | Evidence separates asset availability from service publication readiness and links artifact trust separately. |
| CR-CATREG-010 | Seed/imported registry data must be provisional until verified. | Bootstrap lists often become outdated hidden truth. | Imported record shows provenance class, freshness, owner, policy status, validation status and review trigger. |
| CR-CATREG-011 | Registry schema must hold product fields beyond name. | A service list cannot drive private store decisions safely. | Required fields include owner, purpose, capability, version, compatibility, readiness, support, docs, portability and evidence refs. |
| CR-CATREG-012 | Namespace and scope rules must be visible before publication. | Private, provider and global catalogs need predictable collision handling. | Publication explains uniqueness scope, aliasing, conflict resolution, reserved names and migration path. |
| CR-CATREG-013 | Component, dependency and task summaries must be linked to OCS evidence. | Catalog consumers need consequences, not raw local runtime snippets. | Catalog record links dependency/deployment evidence and controlled automation evidence without exposing raw env, endpoints or commands. |
| CR-CATREG-014 | Publication evidence must link manifest, artifacts, docs, support and source safety. | Store users trust the whole product promise, not a single registry row. | Evidence refs cover manifest validation, artifact inventory, provenance/integrity, docs/runbook, support owner and source-safety scan. |
| CR-CATREG-015 | Registry must represent blocked, warning, degraded, private-only and install-ready states. | Absence from catalog is not enough explanation for humans or agents. | UI/API/CLI/Agent API expose state, reason, next action and owner for every non-ready state. |
| CR-CATREG-016 | Publication must be policy-aware by visibility and installability. | A service can be known but not safe or allowed for every presence. | Policy can allow, hide, block, warn, require approval or restrict by profile, scope, jurisdiction, trust or owner. |
| CR-CATREG-017 | Local/private catalog cache must preserve installed-service manageability offline. | Private presence autonomy is part of the anti-lock-in promise. | Installed service records, support state, entitlement status, update limits and lifecycle actions remain visible with degraded/sync status. |
| CR-CATREG-018 | Registry sync must have a scoped ledger. | Federation and private sync need audit without turning global registry into owner of local lifecycle. | Ledger records imported/exported changes, scope, actor, source, conflict decision, freshness and local ownership boundary. |
| CR-CATREG-019 | Search/index output must be derivative and explainable. | Ranking cannot become an opaque second source of truth. | Search result links canonical record, policy decision, ranking reason, freshness and hidden/blocked alternatives where relevant. |
| CR-CATREG-020 | Registry update must preserve previous support and rollback target. | Users need exact version and support context during incidents or rollback. | Updated record keeps previous versions, deprecation timeline, rollback/restore target, affected instances and support impact. |
| CR-CATREG-021 | Catalog evidence must redact secret, topology and private source context. | Publication artifacts often leak old environment assumptions. | Registry/card/evidence scan proves no raw source paths, endpoints, env dumps, credentials, tenant data or private names are retained. |
| CR-CATREG-022 | Local debug/build/deploy success must not imply publication readiness. | A developer proof can hide missing support, artifact trust, policy and offline behavior. | Readiness report separates local-ready, private-store-ready, provider-ready and federation-ready evidence. |
| CR-CATREG-023 | Minimal prototype registry records may exist only with explicit non-claims. | Early stages need learning without false marketplace promises. | Prototype record is marked candidate/dev-only with missing fields, blocked install state and next evidence needed. |
| CR-CATREG-024 | Registry must support private/internal publication without forcing public marketplace. | Private cloud users need internal service store before public commerce. | Visibility scope can be private/internal, provider-local, federation or global with separate gates and non-goals. |
| CR-CATREG-025 | Registry must include support-chain and escalation ownership. | Store install creates operational responsibility. | Record/card shows service owner, support owner, evidence owner, escalation owner and diagnostic bundle boundary. |
| CR-CATREG-026 | Unpublish/remove must protect installed users and audit history. | Removing a catalog item must not strand existing instances. | Plan shows affected installs, updates, support, entitlements, export/migration, retention and irreversible consequences. |
| CR-CATREG-027 | Source coverage status must be part of source-derived registry lessons. | Current-tree evidence is not the same as full history proof. | Pass record states current-tree/history availability, non-claims and whether deleted-path/ref coverage exists. |
| CR-CATREG-028 | Registry knowledge must survive implementation sunset. | CloudRING should be rebuildable even if old source trees disappear. | Product records and requirements store product meaning, evidence shape and migration constraints without depending on old code. |
| CR-CATREG-029 | Agents must be able to review publication without raw source access. | Solo founder plus agents needs repeatable, safe review loops. | Evidence template gives requirement refs, scenario refs, owners, blockers, allowed actions, forbidden actions and source-safety status. |
| CR-CATREG-030 | Publication conflicts must create manual-review bundles. | Ambiguous identity, owner, scope or evidence should not be guessed by automation. | Conflict record names conflicting fields, affected records, policy result, owner, options and safe next action. |
| CR-CATREG-031 | Registry/catalog events must be learning inputs. | Repeated publication failures should improve standards and templates. | Repeated blocker cluster links to requirement, ADR, conformance check, template/example update or owner-approved no-change rationale. |
| CR-CATREG-032 | Registry must not create a new lock-in point. | A central catalog can become as restrictive as a proprietary cloud. | Local owner can export records/evidence, operate installed services offline, sync with alternatives and exit a registry authority with audit. |

## Evidence Shape

Minimum evidence for a publication-ready registry/catalog record:

- registry identity and scope;
- publication intent and owner approval;
- manifest validation and effective product model;
- catalog card projection and policy visibility decision;
- artifact inventory and trust evidence;
- dependency/deployment and controlled automation evidence;
- support-chain and diagnostic boundary;
- portability/exit statement;
- lifecycle and sync ledger state;
- offline/private cache behavior where relevant;
- source-safety scan and explicit non-claims.

## Stop Conditions

Agent обязан остановиться и запросить owner/ADR/approval, если:

- service file, static asset, seed row or build result is treated as publication
  readiness;
- service identity, owner, support owner, visibility scope or collision policy
  is unknown;
- manifest validation, artifact trust, dependency evidence, docs/runbook or
  source-safety scan is missing;
- publication changes installability without plan, policy and rollback or
  compensation;
- catalog record leaks raw paths, endpoints, env values, credentials, tenant
  data, private names or source snippets;
- registry sync would transfer more scope than required or make a global owner
  authoritative over local lifecycle;
- unpublish/remove would strand installed users without support, migration,
  retention or audit plan;
- current-tree source evidence is claimed as full history coverage.

## Non-Goals

- Не выбирать registry backend, database, object storage, search engine or
  marketplace UI framework.
- Не делать global catalog обязательным для Stage 3 private store.
- Не обещать, что каждый discovered service можно публиковать.
- Не хранить raw source inventory, old service names, exact commands, paths,
  endpoints, credentials or copied snippets.
- Не заменять `CR-CATALOG-*`; этот документ добавляет reusable evidence shape
  for registry/publication proof.
