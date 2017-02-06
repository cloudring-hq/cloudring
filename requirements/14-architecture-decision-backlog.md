# Architecture Decision Backlog

Этот документ фиксирует решения, которые нужно принять как ADR.
Он не заменяет ADR, а задает очередь вопросов, без которых реализация может
закрепить случайные технологические решения.

## Текущие ADR-Файлы

- [ADR-0001 - Runtime Abstraction Strategy](adr/0001-runtime-abstraction-strategy.md)
- [ADR-0002 - Open Cloud Standard Schema Format](adr/0002-open-cloud-standard-schema-format.md)
- [ADR-0003 - Federation Event Bus And Sync Model](adr/0003-federation-event-bus-and-sync-model.md)
- [ADR-0004 - Billing And Settlement Model](adr/0004-billing-and-settlement-model.md)
- [ADR-0005 - Secrets And Trust Boundary](adr/0005-secrets-and-trust-boundary.md)
- [ADR-0006 - Plugin Security Model](adr/0006-plugin-security-model.md)
- [ADR-0007 - Marketplace Certification Levels](adr/0007-marketplace-certification-levels.md)
- [ADR-0008 - Data Portability Contract](adr/0008-data-portability-contract.md)
- [ADR-0009 - Agent Permission And Approval Model](adr/0009-agent-permission-and-approval-model.md)
- [ADR-0010 - Minimal Finished Product Scope](adr/0010-minimal-finished-product-scope.md)
- [ADR-0011 - Control Plane Deployment Topology](adr/0011-control-plane-deployment-topology.md)
- [ADR-0012 - Beautiful Simplicity Product Standard](adr/0012-beautiful-simplicity-product-standard.md)
- [ADR-0013 - Local Entitlement And Offline Licensing](adr/0013-local-entitlement-and-offline-licensing.md)
- [ADR-0014 - Provider Offer And Onboarding](adr/0014-provider-offer-and-onboarding.md)
- [ADR-0015 - Cross-Provider Operation Contract](adr/0015-cross-provider-operation-contract.md)
- [ADR-0016 - Continuous Evolution Loop](adr/0016-continuous-evolution-loop.md)

## ADR Readiness Semantics

Все текущие ADR-файлы имеют status `proposed`. Это допустимо для Stage 0
requirements memory, но stage-readiness report не должен трактовать proposed ADR
как already accepted architecture without qualification.

Правило для агентов:

- если stage gate зависит от proposed ADR, conformance report должен пометить
  это как `proposed_dependency`;
- если proposed dependency влияет на data, money, trust, policy, destructive
  lifecycle or cross-provider operation, readiness status становится `blocked`
  или требует scoped waiver;
- если implementation вынужден выбрать решение до принятия ADR, выбор должен
  быть обратимым, documented as temporary и связан с follow-up owner/review;
- accepted implementation не должен прятать ADR trade-off в коде, конфигурации
  или runbook.

Priority proposed dependencies before production/public/federation claims:

| ADR | Blocking Meaning |
|---|---|
| ADR-0001 | Runtime/backend abstraction cannot freeze accidental implementation lock-in. |
| ADR-0002 | Open Cloud Standard schema must be stable enough for service publication. |
| ADR-0005 | Secrets/trust boundary must be settled before private/public operations. |
| ADR-0008 | Data portability contract must be settled before anti-lock-in claims. |
| ADR-0009 | Agent approval must be settled before agent-operated lifecycle actions. |
| ADR-0011 | Control-plane topology must be settled before federation/global ownership claims. |
| ADR-0015 | Cross-provider operation contract must be settled before DR/migration/replication readiness. |

## ADR Candidates From SRC-PASS-006

These are backlog candidates, not created ADR files yet. They exist so agents
do not implement unresolved architecture implicitly.

| Candidate | Decision Needed | Related Requirements |
|---|---|---|
| ADR-0017 - Cross-Presence Identity And Tenant Model | How identity, tenant portfolio, local ownership and audit boundaries work across presences without centralizing all state. | `CR-DOMAIN-001..020`, `CR-END2END-001`, `CR-END2END-005..007`, `CR-STAGE6-003` |
| ADR-0018 - Lifecycle And State Taxonomy | Canonical state families for lifecycle, readiness, freshness, policy, trust, suspension and revocation. | `CR-END2END-028`, `CR-CONF-003`, `CR-DOMAIN-001`, `CR-STAGE5-022`, `CR-STAGE6-008` |
| ADR-0019 - Global Discovery And Ranking Governance | How global search/ranking/index freshness, policy availability and provider alternatives are explained without becoming central ownership. | `CR-END2END-025`, `CR-STAGE6-001`, `CR-STAGE6-031`, `CR-POLICY-001..020` |
| ADR-0020 - Jurisdiction Policy Overlay Precedence | How enterprise, local, regional and global policy overlays combine, conflict and appeal. | `CR-END2END-012`, `CR-END2END-026`, `CR-STAGE6-009`, `CR-STAGE6-019` |
| ADR-0021 - Distributed Trust Anchor Rotation And Downgrade | How multiple trust anchors, rotation, downgrade propagation and scoped revocation work without mandatory single root. | `CR-STAGE6-032`, `CR-FEDNET-001..030`, `CR-FEDGOV-001..024` |
| ADR-0022 - Cross-Domain Event Envelope | Shared event envelope for lifecycle, billing, federation, operations, policy and evidence correlation. | `CR-END2END-022`, `CR-DOMAIN-003..004`, `CR-FED-001..036`, `CR-BILL-001..036` |
| ADR-0023 - Scoped Suspension, Revocation And Appeal | How governance restricts participants/offers/capabilities/services while preserving customer control, appeal and remediation. | `CR-STAGE5-015`, `CR-STAGE6-018`, `CR-FEDNET-001..030`, `CR-END2END-029` |

## ADR-0001 - Runtime Abstraction Strategy

Статус: proposed; draft file:
[adr/0001-runtime-abstraction-strategy.md](adr/0001-runtime-abstraction-strategy.md).

Вопрос: CloudRING является Kubernetes-first, multi-runtime или runtime-neutral?

Почему важно:

- local, private, edge и public scenarios имеют разные ограничения;
- legacy-прототип показал пользу близости local runtime к production;
- один runtime не должен становиться новым lock-in.

Связанные требования:

- `CR-ARCH-017..020`
- `CR-DX-004..006`
- `CR-INFRA-001..006`

## ADR-0002 - Open Cloud Standard Schema Format

Статус: proposed; draft file:
[adr/0002-open-cloud-standard-schema-format.md](adr/0002-open-cloud-standard-schema-format.md).

Вопрос: в каком формате описывать service manifest, capability schema,
lifecycle API и compatibility profile?

Почему важно:

- формат должен быть human-readable и machine-readable;
- агенты должны валидировать и генерировать спецификации;
- стандарт должен версионироваться.

Связанные требования:

- `CR-OCS-001..027`
- `CR-AGENT-001..008`

## ADR-0003 - Federation Event Bus And Sync Model

Статус: proposed; draft file:
[adr/0003-federation-event-bus-and-sync-model.md](adr/0003-federation-event-bus-and-sync-model.md).

Вопрос: как участники federation обмениваются каталогами, событиями, usage,
settlement и trust state?

Почему важно:

- сеть должна работать без полного доверия;
- edge/private могут быть disconnected;
- события должны быть идемпотентными.

Связанные требования:

- `CR-FED-001..010`
- `CR-ARCH-021..024`
- `CR-DOMAIN-003..004`

## ADR-0004 - Billing And Settlement Model

Статус: proposed; draft file:
[adr/0004-billing-and-settlement-model.md](adr/0004-billing-and-settlement-model.md).

Вопрос: какая модель usage, invoices, settlement, refunds, disputes и revenue
share должна быть базовой?

Почему важно:

- billing является доверительным ядром marketplace;
- usage gateway должен быть точным и проверяемым;
- федерация создает цепочки участников.

Связанные требования:

- `CR-FED-019..030`
- `CR-DOMAIN-001..008`

## ADR-0005 - Secrets And Trust Boundary

Статус: proposed; draft file:
[adr/0005-secrets-and-trust-boundary.md](adr/0005-secrets-and-trust-boundary.md).

Вопрос: какие secret stores, encrypted GitOps flows, brokered secret access и
rotation policies являются базовыми?

Почему важно:

- legacy-источники показали риск секретов в конфигурациях;
- agents должны работать без прямого доступа к секретам;
- private/edge/disconnected имеют разные trust boundaries.

Связанные требования:

- `CR-SEC-007..012`
- `CR-SELF-028`
- `CR-DOMAIN-006`

## ADR-0006 - Plugin Security Model

Статус: proposed; draft file:
[adr/0006-plugin-security-model.md](adr/0006-plugin-security-model.md).

Вопрос: как подписывать, изолировать, разрешать и аудитить плагины?

Почему важно:

- плагины нужны для расширяемости;
- executable plugin является trust boundary;
- enterprise/private сценарии будут приносить специфичную автоматизацию.

Связанные требования:

- `CR-DX-020..024`
- `CR-SEC-025..027`

## ADR-0007 - Marketplace Certification Levels

Статус: proposed; draft file:
[adr/0007-marketplace-certification-levels.md](adr/0007-marketplace-certification-levels.md).

Вопрос: какие уровни сертификации сервиса нужны: dev, private-ready,
public-ready, federation-ready, edge-ready, compliance-ready?

Почему важно:

- marketplace должен быть безопасным;
- не каждый сервис можно запускать везде;
- ISV должен понимать путь публикации.

Связанные требования:

- `CR-FED-011..018`
- `CR-OCS-014..016`
- `CR-SELF-017..020`

## ADR-0008 - Data Portability Contract

Статус: proposed; draft file:
[adr/0008-data-portability-contract.md](adr/0008-data-portability-contract.md).

Вопрос: какие данные, metadata и state обязан экспортировать сервис для
portability и migration?

Почему важно:

- vendor lock-in часто находится в данных и metadata;
- не все сервисы одинаково мигрируемы;
- пользователь должен видеть ограничения до покупки.

Связанные требования:

- `CR-CORE-006..008`
- `CR-SELF-005`
- `CR-FED-006..007`

## ADR-0009 - Agent Permission And Approval Model

Статус: proposed; draft file:
[adr/0009-agent-permission-and-approval-model.md](adr/0009-agent-permission-and-approval-model.md).

Вопрос: какие действия AI-агент может выполнять самостоятельно, какие требуют
policy approval, а какие требуют человека?

Почему важно:

- платформа должна обслуживаться человеком с агентами;
- автономия без границ опасна;
- действия агентов должны быть объяснимыми и проверяемыми.

Связанные требования:

- `CR-SELF-021..028`
- `CR-ARCH-028..032`
- `CR-AGENT-001..008`

## ADR-0010 - Minimal Finished Product Scope

Статус: proposed; draft file:
[adr/0010-minimal-finished-product-scope.md](adr/0010-minimal-finished-product-scope.md).

Вопрос: какой минимальный набор capability делает Stage 1 CloudRING
законченным Solo Developer Cloud и не расползается в Stage 2?

Почему важно:

- платформа должна быть полезной на каждом этапе;
- слишком широкий MVP не будет построен;
- слишком узкий MVP не докажет продуктовую идею.

Связанные требования:

- `11-product-stages-and-finished-increments.md`
- `CR-PLAT-001..010`
- `CR-DX-001..029`
- `CR-OCS-001..032`
- `CR-OPS-001..014`
- `CR-INFRA-001..006`
- `CR-APPROVAL-001..008`

## ADR-0011 - Control Plane Deployment Topology

Статус: proposed; draft file:
[adr/0011-control-plane-deployment-topology.md](adr/0011-control-plane-deployment-topology.md).

Вопрос: где живет control plane для local, private, public provider и global
federation?

Почему важно:

- control plane не должен стать single point of lock-in;
- disconnected private/edge сценарии требуют автономии;
- global portal должен согласовываться с локальным ownership.

Связанные требования:

- `CR-ARCH-005..008`
- `CR-ARCH-021..024`
- `CR-INFRA-012..016`

## ADR-0012 - Beautiful Simplicity Product Standard

Статус: proposed; draft file:
[adr/0012-beautiful-simplicity-product-standard.md](adr/0012-beautiful-simplicity-product-standard.md).

Вопрос: какие UX/product rules делают CloudRING простым и прекрасным несмотря
на сложность federation?

Почему важно:

- сложность платформы нельзя перекладывать на пользователя;
- self-service должен быть понятным и надежным;
- хорошая архитектура должна проявляться в ясном опыте.

Связанные требования:

- `CR-ARCH-001..004`
- `CR-SELF-001..020`
- `CR-UX-001..021`

## ADR-0013 - Local Entitlement And Offline Licensing

Статус: proposed; draft file:
[adr/0013-local-entitlement-and-offline-licensing.md](adr/0013-local-entitlement-and-offline-licensing.md).

Вопрос: как private store должен управлять runtime, update, support и feature
entitlements без превращения лицензии в выключатель локальной инфраструктуры?

Почему важно:

- private cloud должен сохранять базовую работоспособность;
- ISV и поставщики должны иметь коммерческую модель updates/support/features;
- disconnected private presence требует локально проверяемого entitlement state.

Связанные требования:

- `CR-FED-014..018`
- `CR-FED-030`
- `CR-MKT-004..015`
- `CR-SELF-017..020`

## ADR-0014 - Provider Offer And Onboarding

Статус: proposed; draft file:
[adr/0014-provider-offer-and-onboarding.md](adr/0014-provider-offer-and-onboarding.md).

Вопрос: как независимый оператор должен запускать public provider presence,
публиковать offer, принимать tenants и доказывать readiness без ручной
интеграции с ядром CloudRING?

Почему важно:

- CloudRING должен позволять создавать публичных облачных провайдеров;
- provider offer должен быть продуктовым контрактом, а не скрытой
  инфраструктурой;
- Stage 4 должен готовить federation, но работать как самостоятельный provider.

Связанные требования:

- `CR-SELF-013..016`
- `CR-FED-003`
- `CR-FED-014..030`
- `CR-FEDGOV-001..004`

## ADR-0015 - Cross-Provider Operation Contract

Статус: proposed; draft file:
[adr/0015-cross-provider-operation-contract.md](adr/0015-cross-provider-operation-contract.md).

Вопрос: как CloudRING должен выполнять backup, replication, migration, DR,
burst capacity and support handoff между независимыми presence без скрытого
provider lock-in?

Почему важно:

- настоящая federation должна позволять переносить и защищать workloads;
- cross-provider операции затрагивают данные, деньги, SLA, jurisdiction and
  support ownership;
- AI-агенты должны планировать такие операции только через policy, evidence and
  approval.

Связанные требования:

- `CR-FED-006..007`
- `CR-SELF-005..006`
- `CR-OPS-021..028`
- `CR-OPS-038..046`
- `CR-OBSOPS-031..036`
- `CR-INFPROFILE-031`
- `CR-APPROVAL-001..008`

## ADR-0016 - Continuous Evolution Loop

Статус: proposed; draft file:
[adr/0016-continuous-evolution-loop.md](adr/0016-continuous-evolution-loop.md).

Вопрос: как CloudRING должен превращать incidents, support, source intake,
technology changes, conformance drift and ecosystem feedback в требования, ADR,
runbooks, conformance checks and safe agent-operated improvements?

Почему важно:

- платформа должна не устаревать вместе с технологическим поколением;
- repeated incidents and toil должны уменьшаться, а не становиться нормой;
- AI-агенты должны улучшать систему без обхода ownership, policy and approval;
- новая память не должна раскрывать исходные тексты, пилотный контекст или
  секреты.

Связанные требования:

- `CR-ARCH-029..032`
- `CR-SELF-023..028`
- `CR-GOV-011..022`
- `CR-METRIC-031..043`
- `CR-STAGE7-001..039`
