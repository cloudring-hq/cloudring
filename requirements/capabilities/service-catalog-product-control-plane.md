# Capability Contract - Service Catalog And Product Control Plane

## Назначение

Service Catalog And Product Control Plane превращает service в продуктовую
сущность CloudRING: описанную, versioned, совместимую с readiness profiles,
orderable, observable, supportable, billable, portable и управляемую lifecycle
operations. Его задача - отделить product meaning от runtime artifact, чтобы
service можно было переиспользовать в local/private/public/federation/global
контекстах без привязки к одному backend, marketplace или provider.

Contract описывает what/why/evidence. Он не выбирает package format, deployment
runtime, UI framework или registry implementation.

## Продуктовая Граница

- Service - продуктовая capability с owner, purpose, support model, lifecycle и
  compatibility profile.
- ServiceVersion - конкретная версия product promise и readiness evidence.
- Marketplace Offer - коммерческое/доступное предложение service/version в
  конкретном context, provider, region, jurisdiction и policy profile.
- Order/Install Plan - consequence-before-action план: price, policy,
  dependencies, data movement, approvals, rollback/exit.
- ServiceInstance - запущенный или установленный экземпляр с owner, state,
  resource links, billing/support context и lifecycle history.
- Support State - отдельная правда о support ownership, incidents, SLA,
  maintenance, suspension, dispute and handoff.
- Эти сущности связаны, но не сливаются: потеря различий ломает audit,
  settlement, support, portability и agent operations.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-CATALOG-001 | Service должен быть product entity, а не только runtime artifact. | Marketplace, billing, support, policy и portability работают с продуктовым смыслом. | Service has owner, purpose, description, capability, lifecycle, support context and compatibility profile. |
| CR-CATALOG-002 | ServiceVersion должен быть отделен от ServiceInstance. | Один product может иметь много versions и много running/installed instances. | Version and instance have separate IDs, lifecycle, readiness evidence, audit history and rollback/update context. |
| CR-CATALOG-003 | Service должен декларировать capabilities и compatibility profile. | Buyer, scheduler и agent должны понимать, где service можно безопасно использовать. | Catalog shows supported profiles, requirements, dependencies, limits, blockers, degraded modes and unsupported contexts. |
| CR-CATALOG-004 | Dependencies должны декларироваться через product contract. | Manual dependency instructions ломают repeatability и portability. | Dependencies are declared, validated before install/order and visible in impact/rollback/exit plan. |
| CR-CATALOG-005 | Service card должен показывать price, provider, actual provider where relevant, region, jurisdiction, trust, SLA, support, portability and freshness. | Buyer должен понимать consequence before purchase/install. | These fields are visible before confirmation across UI/API/CLI/Agent API. |
| CR-CATALOG-006 | Catalog должен различать dev, private-ready, public-ready, federation-ready and global-ready states. | Не каждый service безопасен во всех стадиях. | Certification/readiness state controls availability, warnings, approvals and non-goals for each stage. |
| CR-CATALOG-007 | Catalog availability должен быть policy-based. | Service нельзя одинаково продавать, устанавливать или предлагать во всех contexts. | Offer is allowed, hidden, blocked, warning-visible, approval-required or manual-review based on policy profile. |
| CR-CATALOG-008 | Catalog должен раскрывать data handling и responsibility boundaries. | User должен знать, где data, кто имеет support access и кто отвечает. | Service card lists data locations, support owner, participant/sub-processor boundary where relevant and operator responsibility. |
| CR-CATALOG-009 | Catalog должен включать documentation и runbook readiness. | Agents, support и solo operator нуждаются в operational context. | Service cannot be readiness-approved without docs/runbook or explicit limited scope with visible warning. |
| CR-CATALOG-010 | Catalog должен хранить lifecycle и audit events. | Support, migration, billing, dispute и incident investigation требуют history. | Service, offer, order and instance pages link create/change/suspend/update/remove/support events and correlation IDs. |
| CR-CATALOG-011 | Install/order должен produce plan before action. | Self-service требует consequence-before-action, а agent operations требуют проверяемый план. | Plan shows target, dependencies, policy decisions, price, data movement, approvals, rollback, exit and support impact. |
| CR-CATALOG-012 | Update/remove/rollback/suspend/resume должны быть explicit lifecycle operations. | App-store model не заканчивается initial install. | User/admin/agent can request operation with validation, policy check, audit, owner approval where needed and visible result state. |
| CR-CATALOG-013 | Stateful removal требует retention/export/backup/restore/billing/support decision. | Removing service может уничтожить data, evidence и commercial/support context. | Remove plan shows retention, export, latest backup/restore evidence, billing closeout, support handoff, rollback or irreversible warning. |
| CR-CATALOG-014 | Catalog должен поддерживать private/offline visibility for installed services. | Private cloud должен оставаться управляемым при disconnect. | Installed services remain visible with entitlement, support, update, lifecycle, health and limitation state offline. |
| CR-CATALOG-015 | Catalog должен поддерживать ISV/seller readiness feedback. | Ecosystem не масштабируется через opaque review. | Seller sees failed checks, next actions, certification blockers, limited-scope approval and appeal/review path. |
| CR-CATALOG-016 | Catalog должен поддерживать extension/plugin trust boundaries. | Store extensibility не должна обходить platform policy. | Connector/plugin permissions, signing/trust, data access, sandbox boundary and support owner are visible before enablement. |
| CR-CATALOG-017 | Catalog должен сохранять единый product vocabulary across UI/API/CLI/Agent API. | Human и agent должны разделять одну product reality. | Same states, lifecycle terms and entity names are used across interfaces and conformance evidence. |
| CR-CATALOG-018 | Catalog должен показывать alternatives и concentration risk. | Anti-lock-in требует видимого выбора, а не единственной скрытой дороги. | Buyer sees compatible alternatives, portability class, provider/technology concentration risk or reason none exist. |
| CR-CATALOG-019 | Catalog freshness и failure state должны быть visible in federation/global modes. | Stale offers create false confidence and hidden risk. | Offer shows fresh, stale, delayed, degraded, disputed, suspended, deprecated, limited, blocked or revoked status. |
| CR-CATALOG-020 | Catalog changes должны следовать conformance и evolution rules. | Marketplace quality должна улучшаться без хаоса и silent promise changes. | Certification/profile/offer changes have version, reason, owner, affected users, rollout/rollback path and validation evidence. |
| CR-CATALOG-021 | Provider/publisher readiness package must be required before publication. | Publication is an operational promise, not only a catalog card. | Package includes manifest validation, compatibility profile, docs/runbook/FAQ, observability, support owner, escalation/SLA owner where relevant, task declarations, known limitations, diagnostic boundary and readiness blockers. |
| CR-CATALOG-022 | Generated artifact inventory must be part of catalog readiness. | Store users need to know what will be installed, regenerated or ignored. | Catalog links source-of-truth, derived and local-state artifacts with version, owner, provenance, freshness, publish/ignore boundary and cleanup. |
| CR-CATALOG-023 | Artifact/image/template publication must require provenance and hardening evidence. | Marketplace trust depends on artifact proof. | Publication shows actual built artifact identity, digest or equivalent immutable identity, registration result, build/provenance, hardening, cleanup, boot/health/first-bootstrap validation, known limits and support diagnostics. |
| CR-CATALOG-024 | Service card must distinguish release identity from mutable marketing version. | Users and agents need exact support and rollback target. | Card shows service version, release channel, artifact identity, deprecation state, update path and rollback/restore target. |
| CR-CATALOG-025 | Publication must block secret/private context in generated outputs and examples. | Store artifacts often leak old environment assumptions. | Readiness scan proves docs, examples, generated specs, build profiles, CI/build diagnostics and artifacts contain only redacted/synthetic values and no private source context. |
| CR-CATALOG-026 | Support chain state must be catalog-linked. | A buyer needs support accountability before install and during incidents. | Service/offer/instance record shows support owner, SLA clock owner, escalation owner, evidence bundle owner, diagnostic bundle owner and credit/dispute handoff owner. |
| CR-CATALOG-027 | Local debug success must not count as publication readiness. | Developer proof is not provider/store proof. | Readiness report separates local-ready evidence from private-store, public-provider and federation evidence. |
| CR-CATALOG-028 | Offline/private installed-service readiness must be simulated. | Offline entitlement and local control cannot be assumed. | Simulation shows cached entitlement, allowed/blocked actions, deferred sync ledger, support/update limits and recovery behavior. |
| CR-CATALOG-029 | Catalog publication must link reusable service registry/catalog publication evidence. | Service store trust fails if catalog visibility is inferred from static assets, seed rows, local manifests or debug success. | Service/version/card publication links `CR-CATREG-001..032` evidence for registry identity, publication intent, lifecycle, policy visibility, manifest/effective model validation, artifact/dependency/support evidence, sync/cache, source coverage, source-safety and non-claims. |

## Actor Boundaries

- Buyer может search/order/install/remove только в рамках ownership, policy,
  entitlement and budget boundaries.
- Tenant admin может управлять catalog visibility, quotas, approvals and local
  overlays, но не переписывает readiness evidence.
- Provider/operator публикует offers, capacity, health, support and trust state.
- ISV/seller публикует service contract and readiness evidence, но не получает
  лишний customer data access.
- Agent может prepare plan, compare alternatives, validate readiness and execute
  approved operation; risky, destructive, financial, support-handoff and
  data-moving operations требуют approval.

## Evidence

- Service card snapshot before order.
- ServiceVersion and ServiceInstance records with separate lifecycle history.
- Compatibility/conformance report.
- Marketplace offer with freshness and policy availability decision.
- Install/order/update/remove plan with rollback/exit/support/billing impact.
- Documentation/runbook readiness evidence.
- Seller readiness feedback with blockers.
- Provider/publisher readiness package.
- Artifact inventory, provenance, hardening and boot/health evidence.
- Generated output source-safety scan.
- Support chain state record.
- Offline/private installed-service simulation.
- Service registry/catalog publication evidence.
- Plugin/connector trust boundary record.
- Offline installed-service view for private presence.

## Stage Guardrails

- Stage 3 private store может иметь local catalog, local entitlement visibility
  and install/update/remove lifecycle, но не должен требовать global marketplace.
- Stage 4 public provider readiness требует provider-local offer/order/billing
  consistency, но не требует cross-participant settlement.
- Stage 5 federation добавляет participant compatibility, cross-provider
  visibility and settlement readiness.
- Stage 6 global readiness требует freshness, dispute handling, multi-jurisdiction
  visibility and explainable global search/ranking.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/ADR, если:

- service lacks product contract, owner, compatibility profile or support model;
- publication lacks provider/publisher readiness package;
- artifact/image/template lacks provenance, hardening, cleanup, boot/health or
  support diagnostics evidence;
- generated docs/examples/artifacts contain secret/private context;
- service card hides price, provider/actual provider, jurisdiction, support,
  trust, freshness or portability;
- support owner, SLA clock owner or escalation owner is unknown;
- catalog, offer, order, instance and support state are indistinguishable;
- install/update/remove bypasses policy, entitlement, conformance or approval;
- stateful removal lacks retention/export/backup/billing/support decision;
- plugin/connector boundary, permissions or support owner are unknown;
- local debug success is used as store/publication readiness evidence;
- offline/private entitlement behavior has no simulation evidence;
- service registry/catalog visibility relies on static assets, seed rows,
  search entries, local manifests or debug/build success without publication
  evidence;
- early-stage plan accidentally requires global marketplace or cross-participant
  settlement;
- ranking/search cannot explain blocked, preferred, degraded or hidden offers.

## Non-Goals

- Не выбирать package format, registry, deployment runtime или UI framework.
- Не обещать portability for every service.
- Не заменять support contracts.
- Не делать global marketplace mandatory для private catalog.
- Не включать cross-participant settlement в Stage 3/4 readiness.
- Не скрывать provider chain, jurisdiction, trust or portability behind a single
  install button.
