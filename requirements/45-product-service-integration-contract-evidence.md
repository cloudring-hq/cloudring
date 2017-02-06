# Product Service Integration Contract Evidence

## Назначение

Product Service Integration Contract Evidence фиксирует требования к тому, как
внешний или внутренний продуктовый сервис подключается к общим возможностям
CloudRING: catalog, identity, scoped access, usage, documentation, support,
validation and lifecycle.

Главный урок source-slice: интеграция сервиса не равна одному API вызову, одному
токену, одному swagger-файлу или одному локальному тесту. Готовая интеграция
должна быть доказуемой цепочкой: product identity, environment/profile scope,
service credential, registered usage resources, versioned API contract,
human-readable onboarding, machine-readable specification, safe examples,
negative fixtures, support-safe receipts, publication boundary and source-safety.

Этот документ описывает what/why/evidence. Он не выбирает API gateway,
authentication mechanism, database, message broker, schema format, portal,
programming language or billing backend.

## Product Boundary

- Product service integration package - reusable evidence bundle that shows how
  one service connects to one or more shared CloudRING capabilities.
- Product identity - canonical service/product code used for catalog, access,
  usage, support and audit correlation.
- Integration profile - local/private/provider/federation/global environment
  scope where docs, credentials, resources and API contract are coherent.
- Human onboarding guide - task-oriented process documentation for service
  owners and support teams.
- Machine contract - versioned request/result/error/state specification that
  agents and validators can check.
- Safe integration fixture - synthetic positive and negative example that proves
  behavior without leaking real endpoints, tokens, paths, tenants or source text.

## Source-Derived Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| Human integration guide and generated API specification both existed. | Onboarding narrative and machine contract are complementary evidence, not replacements for each other. | `CR-SVCINT-001`, `CR-SVCINT-014..017` |
| Product-scoped credentials were used before usage submission. | Access must be scoped to product identity and profile, not broad platform authority. | `CR-SVCINT-004..007` |
| Resource registration was documented before usage reporting. | Billable resources need lifecycle proof before consumption can be accepted as meaningful. | `CR-SVCINT-008..010` |
| Usage intake accepted structured batches and periods. | Submission needs event identity, batch semantics, period policy and support-safe receipt. | `CR-SVCINT-011..013`, `CR-SVCINT-020..023` |
| API generations and docs/code details could drift. | Integration readiness must block on version and docs/spec/code consistency. | `CR-SVCINT-018..019`, `CR-SVCINT-028` |
| Examples and generated docs contained unsafe operational context. | Integration examples must be synthetic and generated docs must be scanned before publication. | `CR-SVCINT-024..027`, `CR-SVCINT-031` |
| Local tests and build tasks existed but were thin. | Local/dev confidence is useful but cannot prove provider or financial readiness alone. | `CR-SVCINT-029..030`, `CR-SVCINT-032` |

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SVCINT-001 | Every shared-capability integration must have a Product Service Integration Package. | API docs alone cannot prove identity, access, resource lifecycle, support and source-safety. | Package links manifest, product identity, capability target, profile, credentials class, resource lifecycle, API contract, docs, fixtures, support owner, evidence refs and non-claims. |
| CR-SVCINT-002 | Integration package must declare capability purpose and commercial consequence. | A service owner must know whether integration affects billing, entitlement, catalog, support, audit or only telemetry. | Package states capability type, user-visible outcome, commercial impact, data class, stage scope and stop-if-unknown behavior. |
| CR-SVCINT-003 | Product identity must be canonical, exact and collision-reviewed. | Case, alias or format drift can authorize or bill the wrong product. | Evidence records canonical product id, alias policy, exact-match rule, rename/deprecation path, collision result and support-visible identity. |
| CR-SVCINT-004 | Service credentials must be explicitly scoped to product, capability and profile. | Broad credentials create commercial and operational blast radius. | Credential evidence records allowed product identities, capability actions, profile scope, owner, expiry/review, revocation path and redacted decision result. |
| CR-SVCINT-005 | Credential validity and product authorization must be separate checks. | A valid credential can still be unauthorized for a particular product or resource. | Access decision records validity, product membership, capability action, resource scope, freshness and fail mode separately. |
| CR-SVCINT-006 | Access freshness must be visible to the caller and support owner. | Cached or stale access can accept revoked usage or reject valid integration. | Evidence shows access source, last sync/freshness, stale policy, degraded behavior and affected product/resource scope. |
| CR-SVCINT-007 | Integration must distinguish service credential from user/admin identity. | Product-service automation should not inherit human admin power. | Package states actor type, allowed automated actions, forbidden actions, required approval and audit correlation. |
| CR-SVCINT-008 | Usage resources must be registered before billable usage submission. | Billing cannot interpret unknown resources safely. | Integration evidence links resource registration state, unit policy, lifecycle state, owner, visibility and behavior for unknown or retired resource usage. |
| CR-SVCINT-009 | Registration-before-usage must be runtime-enforced or explicitly blocked. | Documentation-only lifecycle rules create false integration readiness. | Readiness fails or warns if intake cannot prove registered-resource existence for the declared profile, with mitigation and owner decision. |
| CR-SVCINT-010 | Resource identity must be stable and versionable. | Changing resource codes or units silently breaks billing, support and reconciliation. | Resource record includes stable id, display name, unit set, compatibility version, retirement path and tariff/entitlement binding status where applicable. |
| CR-SVCINT-011 | Usage submission must be described as accepted-for-processing, not final commercial truth. | A successful intake response does not prove invoice, entitlement or settlement outcome. | Result model separates received, validated, accepted, queued, published, settled, rejected, quarantined and disputed states or links to billing runtime evidence. |
| CR-SVCINT-012 | Event identity and request idempotency must be separate integration concepts. | One request can contain many events, and retries can cross request boundaries. | Contract defines event id, request idempotency key or equivalent, duplicate behavior, conflict behavior, retention and replay evidence. |
| CR-SVCINT-013 | Batch semantics must be explicit and support-safe. | Partial failure hidden behind batch success creates disputes and missing charges. | Contract states atomic or per-item behavior, maximum safe batch guidance, partial-failure state, retryability and receipt fields. |
| CR-SVCINT-014 | Human onboarding guide must be task-oriented and profile-aware. | Service teams need process context, not only schema fields. | Guide covers prerequisites, profile selection, product identity, credential request, resource registration, usage submission, retry, support and decommission. |
| CR-SVCINT-015 | Machine contract must be versioned and validation-ready. | Agents and SDKs need stable request/result/error semantics. | Contract includes version, compatibility, deprecation, required fields, result shape, error catalog, examples, profile constraints and source-safety status. |
| CR-SVCINT-016 | Human docs and machine contract must reference the same product truth. | Drift between guide, generated spec and runtime creates integration failures. | Evidence links guide version, machine contract version, generated-doc source, freshness, drift check and owner decision. |
| CR-SVCINT-017 | Integration examples must be synthetic and safe by default. | Real examples often leak tokens, endpoints, tenant data or old service names. | Examples use generic product/resource/event ids, no real endpoints, no credentials, no raw source snippets and include positive and negative fixtures. |
| CR-SVCINT-018 | API generation changes must have compatibility and migration evidence. | Product services may lag behind platform versions. | Integration package records active, legacy, deprecated and blocked API boundaries, migration window, behavior differences and rollback/deprecation consequence. |
| CR-SVCINT-019 | Docs/spec/runtime disagreement must be a readiness blocker or warning. | A published guide can promise behavior the runtime does not prove. | Drift report records affected fields, result/error differences, severity, owner, allowed profile and next fix before publication. |
| CR-SVCINT-020 | Error envelope must be stable, redacted and actionable across versions. | Service owners and agents need safe remediation without internal details. | Error model includes stable code, field/path, retryability, owner, correlation reference, user/support message and redacted diagnostic boundary. |
| CR-SVCINT-021 | Period and unit policy must be part of integration contract. | Overlap, timezone and unit drift cause billing disputes. | Contract defines period ordering, overlap policy, time normalization, unit catalog, conversion/unsupported behavior and negative fixtures. |
| CR-SVCINT-022 | Metadata must be bounded, classified and source-safe. | Metadata can leak tenant data or destabilize event identity. | Contract defines allowed metadata classes, size/count limits, identity participation, redaction, retention, rejection and quarantine behavior. |
| CR-SVCINT-023 | Support-safe receipt must be returned or linked for high-impact integrations. | Support needs a handle without raw payload or credentials. | Receipt includes operation/event refs or redacted hashes, counts, status reference, timestamps, version, warnings, retryability and retention class. |
| CR-SVCINT-024 | Generated docs must not be the source of truth. | Generated files can be stale, unsafe or incomplete. | Evidence records source contract, generator identity, generated artifact identity, freshness, stale behavior and source-safety scan. |
| CR-SVCINT-025 | Integration package must include negative fixtures. | Readiness must prove safe refusal as well as happy path. | Fixtures cover unauthorized product, unknown resource, stale credential, invalid period, duplicate/conflict, oversize metadata, unsupported API version and unsafe evidence. |
| CR-SVCINT-026 | Integration must publish support and ownership boundaries. | Failed integration crosses service owner, platform capability owner and support. | Package names product owner, capability owner, support owner, evidence owner, escalation path and diagnostic bundle boundary. |
| CR-SVCINT-027 | Onboarding acceptance evidence must be explicit. | "Docs exist" does not prove a product service can safely connect. | Evidence shows product registration, credential scope, resource lifecycle, contract validation, fixture result, support receipt and unresolved blockers. |
| CR-SVCINT-028 | Integration publication must be gated by source-safety review. | API docs and examples are common leak surfaces. | Publication blocks on scans for private names, hostnames, paths, credentials, tenant data, raw source snippets, copied commands and unsafe generated examples. |
| CR-SVCINT-029 | Local/dev integration confidence must be stage-scoped. | Local smoke tests are useful but not provider or financial readiness proof. | Report states local-only, private-ready, provider-ready or federation-ready confidence, with required additional evidence per stage. |
| CR-SVCINT-030 | Thin integration tests must not be overclaimed. | Minimal tests can miss access freshness, resource lifecycle, batch and replay behavior. | Evidence states test scope, covered positive/negative cases, missing behaviors, confidence level and next fixture backlog. |
| CR-SVCINT-031 | Decommission must revoke or retire integration safely. | Product service exit should not leave credentials, resource codes or docs active. | Offboarding evidence covers credential revocation, resource retirement, docs/deprecation, pending usage, support handoff, retention and audit. |
| CR-SVCINT-032 | Source-derived integration lessons must preserve product meaning without old context. | The goal is reimplementation, not cloning old API docs or examples. | Requirements and evidence paraphrase product contracts, record non-claims and omit raw endpoints, paths, tokens, commands, source snippets, dependency names and private identifiers. |

## Evidence Shape

Minimum Product Service Integration Contract evidence:

```yaml
product_service_integration_evidence:
  evidence_id: product-service-integration-evidence-id
  profile_refs:
    - stage3-private-store-ready
  scenario_refs:
    - SCENARIO-STAGE3-007
  requirement_refs:
    - CR-SVCINT-001..032
  product_identity:
    canonical_status: passed | warning | failed | blocked
    alias_policy_status: passed | warning | failed | blocked
    collision_review_status: passed | warning | failed | blocked
  access_scope:
    credential_scope_status: passed | warning | failed | blocked
    product_authorization_status: passed | warning | failed | blocked
    freshness_status: passed | warning | failed | blocked
  resource_lifecycle:
    registration_status: passed | warning | failed | blocked
    runtime_enforcement_status: passed | warning | failed | blocked
    unit_period_policy_status: passed | warning | failed | blocked
  contract_publication:
    human_guide_status: passed | warning | failed | blocked
    machine_contract_status: passed | warning | failed | blocked
    docs_spec_runtime_drift_status: passed | warning | failed | blocked
    api_version_status: passed | warning | failed | blocked
  submission_semantics:
    receipt_status: passed | warning | failed | blocked
    idempotency_status: passed | warning | failed | blocked
    batch_status: passed | warning | failed | blocked
    error_model_status: passed | warning | failed | blocked
  fixtures:
    positive_fixture_status: passed | warning | failed | blocked
    negative_fixture_status: passed | warning | failed | blocked
    source_safety_status: passed | warning | failed | blocked
  handoff:
    support_owner_status: passed | warning | failed | blocked
    onboarding_acceptance_status: passed | warning | failed | blocked
    decommission_status: passed | warning | failed | blocked
  non_claims:
    - does not prove downstream financial settlement
    - does not prove provider production readiness
```

## Stop Conditions

Agent must stop and request owner/review if:

- product identity is ambiguous, case-normalized without policy or collision
  unreviewed;
- service credential is broad, ownerless, stale or not scoped to product,
  capability and profile;
- usage can be submitted for unregistered resources while readiness is claimed;
- docs, generated spec and runtime behavior disagree without warning/blocker;
- success response is treated as invoice, entitlement, settlement or downstream
  delivery truth;
- request idempotency hides event identity conflict or changed payload;
- batch success can hide item drops without per-item evidence or explicit
  limitation;
- examples, generated docs or evidence include private endpoints, paths,
  credentials, tenant data, raw source snippets or copied operational commands;
- local/dev tests are promoted as private/provider/federation readiness without
  stage-scoped evidence.

## Non-Goals

- Не выбирать конкретный API protocol, authentication implementation, API
  gateway, database, queue, SDK or billing engine.
- Не заменять `CR-BILLRUN-*`, `CR-SETTLE-*`, `CR-CATREG-*` or
  `CR-RELPROM-*`; this document defines the integration package that connects
  those evidence families.
- Не переносить старые API docs, examples, endpoint paths, command lines,
  source snippets, internal package names or private operational context.
- Не утверждать production readiness, financial settlement correctness, live
  delivery, full line-by-line source audit or full all-refs history coverage.
