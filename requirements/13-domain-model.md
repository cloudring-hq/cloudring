# Domain Model

Этот документ описывает концептуальную модель CloudRING.
Она нужна, чтобы требования превращались в согласованную архитектуру, API,
данные, события и агентские задачи.

## Bounded Contexts

| Context | Назначение |
|---|---|
| Identity And Access | Пользователи, организации, роли, service accounts, agent identities, scopes. |
| Resource Management | Ресурсы, quotas, limits, ownership, tags, lifecycle state. |
| Service Catalog | Сервисы, capability, compatibility, versions, dependencies, documentation. |
| Marketplace | Offers, plans, prices, licenses, subscriptions, publication workflow. |
| Provisioning | Orders, service instances, workflows, connectors, placement, generated specs. |
| Infrastructure | Presence, regions, zones, capacity, compute, network, storage, runtime backends. |
| Federation | Participants, trust, catalog sync, event exchange, settlement routes. |
| Billing | Usage resources, usage events, invoices, settlement, revenue share, disputes. |
| Policy And Compliance | Jurisdiction, data residency, security baselines, approvals, constraints. |
| Observability | Metrics, logs, traces, alerts, SLO, incidents, audit. |
| Operations Knowledge | Requirements, ADR, runbooks, plans, validations, agent task records. |

## Core Entities

| Entity | Описание |
|---|---|
| Organization | Юридический/логический владелец пользователей, сервисов, ресурсов или provider presence. |
| User | Человек, выполняющий действия через portal/API/CLI. |
| Agent | AI-агент или automation identity с ограниченными правами и audit trail. |
| Participant | Любой субъект federation: public provider, private owner, edge operator, ISV, reseller, support partner or governance actor. |
| Provider | Participant, который предоставляет cloud presence, capacity, service runtime, public offer or commercial provider responsibility. |
| Owner | Субъект, который принимает продуктовую ответственность за ресурс, сервис, presence, evidence, exception or requirement. |
| Operator | Субъект, который выполняет operational действия по поручению owner and within policy/audit boundary. |
| Publisher | ISV, provider or internal team, публикующий service candidate, artifact, offer or update. |
| Presence | Конкретное место/инсталляция CloudRING: public, private, edge, local. |
| Region | Географическая или юридическая зона размещения. |
| Zone | Техническая зона внутри region/presence. |
| Service | Продуктовая сущность, публикуемая или используемая через CloudRING. |
| ServiceVersion | Версия сервиса с совместимостью, контрактом и артефактами. |
| ServiceCapability | Объявленная возможность сервиса. |
| ServiceConnector | Адаптер сервиса к Open Cloud Standard. |
| ServiceInstance | Конкретно заказанный и работающий экземпляр сервиса. |
| EnvironmentProfile | Набор environment overrides, secret references, generated values and policy constraints для local/private/provider/edge/disconnected контекста. |
| RuntimeProfile | Описание runtime backend capabilities, limits, unsupported/degraded states, ingress/routing and cleanup behavior. |
| DependencyConnection | Контракт подключения зависимости: outputs, readiness, fallback, owner, secret boundary and unsupported state. |
| GeneratedArtifact | Производный runtime/config/build/docs artifact with generator, freshness, source contract, publish/ignore boundary and cleanup rule. |
| TaskOperation | Повторяемая product operation for build, validation, docs, migration, maintenance or diagnostics with risk, scope and structured result. |
| PluginExtension | Executable extension surface with owner, permissions, provenance, audit and support boundary. |
| UIExtension | Embedded service UI descriptor with mount, route, permissions, theme, scoped context, telemetry and isolation. |
| ValidationRule | Human-readable and machine-readable rule with code, path, timing, severity, parity and safety limits. |
| CommandResult | Standard result object for UI/API/CLI/Agent API actions with state, operation id, evidence, warnings, next actions and maturity. |
| Resource | Единица инфраструктуры или продуктового потребления. |
| Component | Зависимость сервиса: database, storage, queue, secret store, network endpoint и т.д. |
| Offer | Коммерческое предложение сервиса в marketplace. |
| Plan | Тариф/пакет условий: цена, quotas, SLA, features. |
| Subscription | Право клиента использовать сервис или получать updates/support. |
| UsageResource | Зарегистрированный ресурс для billing. |
| UsageEvent | Событие потребления ресурса за период. |
| Invoice | Счет или начисление для клиента. |
| Settlement | Расчет долей между провайдерами, ISV, reseller и CloudRING. |
| Policy | Машинно-исполняемое ограничение или правило. |
| ComplianceProfile | Набор policy для рынка, клиента, отрасли или юрисдикции. |
| SecretReference | Ссылка на секрет без раскрытия значения. |
| AuditEvent | Неизменяемое событие действия или изменения состояния. |
| Incident | Операционная проблема с timeline, impact и remediation. |
| ADR | Архитектурное решение с контекстом и последствиями. |
| Requirement | Продуктовое требование с why и acceptance criteria. |
| Runbook | Процедура эксплуатации для человека и агента. |

## Canonical Role Terms

| Term | Product Boundary |
|---|---|
| Provider | Предоставляет capacity/service offer and accepts provider-facing support, billing or SLA responsibility for declared scope. |
| Participant | Участвует в federation, но не обязательно продает public cloud capacity. Private owner, edge operator, ISV and reseller are participants. |
| Owner | Имеет право принять риск, waiver, lifecycle decision, policy exception or customer promise. |
| Operator | Исполняет действие; operator не становится owner только потому, что выполняет runbook. |
| ISV / Publisher | Создает и публикует сервис; может не владеть presence, где сервис будет работать. |
| Reseller / Integrator | Продает, сопровождает or bundles offer, но его ответственность должна быть отделена от provider/operator/support owner. |

## State Families

CloudRING не должен сводить все состояния к `ready/failed`. Разные вопросы
имеют разные state families, и UI/API/CLI/Agent API должны показывать family,
owner, cause, user impact and next action.

| State Family | Examples | Product Meaning |
|---|---|---|
| Lifecycle state | draft, candidate, active, updating, suspended, retired | Где сущность находится в своем жизненном цикле. |
| Readiness/certification state | dev, private-ready, public-ready, federation-ready, global-ready, blocked | Какой продуктовый promise доказан conformance evidence. |
| Freshness state | current, stale, unknown, contradicted | Можно ли доверять evidence, sync, catalog or trust metadata right now. |
| Policy decision state | allowed, denied, warning, manual-review, waived | Что policy разрешила и на каких условиях. |
| Trust/suspension state | trusted, degraded, disputed, revoked, quarantined | Как сеть должна ограничить visibility, order, update, sync or support. |

## Key Relationships

| Relationship | Смысл |
|---|---|
| Organization owns Resource | Ресурс должен иметь владельца и billing context. |
| Participant may operate, publish or resell | Federation role must be explicit; one participant can have multiple scoped roles. |
| Provider operates Presence | Провайдер отвечает за конкретную инсталляцию/регион/зону. |
| Owner approves risk or exception | Approval authority follows ownership, not whoever runs the command. |
| Operator executes under Owner policy | Execution must keep audit, scope and compensation boundary. |
| Presence exposes Capability | Не каждая presence поддерживает все capability. |
| Service declares Capability | Сервис сообщает, что умеет и какие контракты выполняет. |
| ServiceVersion implements StandardVersion | Совместимость привязана к версии стандарта. |
| Service depends on Component | Зависимости должны быть declarative. |
| ServiceVersion declares EnvironmentProfile | Один сервис должен переноситься между профилями без копирования смысла. |
| Presence supports RuntimeProfile | Runtime capability принадлежит конкретной presence/profile и может быть заменена. |
| Component exposes DependencyConnection | Платформа должна знать, как подключить зависимость и как она деградирует. |
| Manifest generates GeneratedArtifact | Derived artifacts должны иметь provenance и не становиться source-of-truth. |
| Service exposes TaskOperation | Tasks являются product operations, а не скрытыми shell-командами. |
| PluginExtension extends ServiceFactory | Plugin должен иметь trust boundary и audit. |
| UIExtension extends Experience Surface | Embedded UI должен сохранять permissions, terminology, validation and support rules. |
| CommandResult records operation evidence | Human and agent surfaces должны видеть один outcome. |
| Offer references ServiceVersion | Marketplace продает конкретную совместимую версию или канал. |
| Plan defines price/SLA/quota | Коммерческие условия отделены от реализации сервиса. |
| Subscription grants entitlement | Доступ к сервису, updates и support должен быть формализован. |
| ServiceInstance emits UsageEvent | Billing основан на событиях потребления. |
| UsageEvent references UsageResource | Нельзя начислять неизвестный ресурс. |
| Policy constrains Placement | Placement должен учитывать jurisdiction, security и capacity. |
| Agent executes Task under Identity | Агентские действия должны быть управляемыми и проверяемыми. |
| Incident creates Requirement or ADR | Платформа учится через операционный опыт. |

## Domain Events

| Event | Когда Возникает |
|---|---|
| ParticipantRegistered | Новый provider/private/edge участник принят в federation. |
| PresenceConnected | Инсталляция подключилась к federation. |
| CapabilityPublished | Presence опубликовала доступную capability. |
| ServiceSubmitted | ISV или provider подал сервис на проверку. |
| ServiceCertified | Сервис прошел conformance/security checks. |
| OfferPublished | Marketplace offer стал доступен пользователям. |
| OrderCreated | Пользователь заказал сервис. |
| PlacementProposed | Платформа предложила место размещения. |
| PolicyDecisionMade | Policy engine разрешил или запретил действие. |
| ManifestValidated | Manifest/schema/profile validation закончилась с результатом и evidence. |
| RuntimeProfileChecked | Runtime preflight определил supported/degraded/blocked/unknown capabilities. |
| CommandCompleted | UI/API/CLI/Agent command завершилась structured result. |
| GeneratedArtifactProduced | Derived artifact создан или обновлен из source contract. |
| TaskOperationCompleted | Task завершилась с evidence, warnings and next actions. |
| PluginExtensionExecuted | Plugin execution зафиксирован с permissions and redaction status. |
| UIExtensionMounted | Service UI embedded через trust/permission descriptor. |
| ServiceProvisioningStarted | Начался lifecycle provisioning. |
| ServiceInstanceReady | Экземпляр сервиса готов. |
| ServiceInstanceChanged | Изменились параметры сервиса. |
| ServiceInstanceSuspended | Сервис остановлен или ограничен. |
| UsageResourceRegistered | Сервис зарегистрировал ресурс учета. |
| UsageEventAccepted | Usage event принят gateway. |
| UsageEventRejected | Usage event отклонен с понятной причиной. |
| InvoiceIssued | Сформировано начисление/счет. |
| SettlementCalculated | Рассчитаны доли участников. |
| IncidentOpened | Обнаружена проблема. |
| RemediationExecuted | Выполнено восстановление или изменение. |
| RequirementDiscovered | Новый урок превращен в требование. |
| ADRAccepted | Принято архитектурное решение. |
| StateFamilyChanged | Lifecycle, readiness, freshness, policy or trust state changed with owner, cause and impact. |

## Требования К Модели

| ID | Требование | Почему |
|---|---|---|
| CR-DOMAIN-001 | Все ключевые сущности должны иметь стабильные identifiers и lifecycle state. | Federation и audit требуют ссылочной устойчивости. |
| CR-DOMAIN-002 | Сущности billing, marketplace и provisioning не должны смешиваться в одну таблицу/модель. | У них разные жизненные циклы и разные владельцы. |
| CR-DOMAIN-003 | Все cross-context действия должны публиковать domain events. | Слабая связность нужна для federation и агентской автоматизации. |
| CR-DOMAIN-004 | Domain events должны быть идемпотентными или иметь deterministic identity. | Повторы неизбежны. |
| CR-DOMAIN-005 | Policy decisions должны сохраняться рядом с действием. | Нужно объяснять, почему placement/order/action был разрешен или запрещен. |
| CR-DOMAIN-006 | Secret values не должны быть частью domain events; допустимы только references. | Событийные логи широко распространяются. |
| CR-DOMAIN-007 | ServiceInstance должен быть отделен от ServiceVersion. | Один продукт имеет много работающих экземпляров и версий. |
| CR-DOMAIN-008 | Presence должна описывать и технические, и юридические attributes. | Placement зависит и от capacity, и от jurisdiction. |
| CR-DOMAIN-009 | Agent identity должна быть такой же полноценной сущностью, как user/service account. | Агентские действия должны иметь owner, permissions и audit. |
| CR-DOMAIN-010 | Requirements/ADR/runbooks должны быть частью knowledge domain, а не внешними заметками. | CloudRING должен сохранять и использовать собственную память. |
| CR-DOMAIN-011 | EnvironmentProfile должен быть отдельной сущностью. | Config, policy and secret binding меняются между local/private/provider/edge без изменения смысла сервиса. |
| CR-DOMAIN-012 | RuntimeProfile должен быть отделен от Presence and Service. | Runtime можно заменить, а service contract должен сохраняться. |
| CR-DOMAIN-013 | DependencyConnection должен быть first-class domain object. | Зависимость должна быть подключаемой и проверяемой, а не ручной инструкцией. |
| CR-DOMAIN-014 | GeneratedArtifact должен быть отделен от source-of-truth. | Derived local/runtime files не должны загрязнять продуктовый контракт. |
| CR-DOMAIN-015 | TaskOperation должен иметь product semantics. | Повторяемые действия нужны для agents, CI and support, но не должны быть произвольными скриптами. |
| CR-DOMAIN-016 | PluginExtension должен быть trust boundary. | Executable extensions требуют permissions, provenance, audit and support owner. |
| CR-DOMAIN-017 | UIExtension должен быть частью experience and security domain. | Embedded UI влияет на permissions, validation, telemetry and support. |
| CR-DOMAIN-018 | ValidationRule должен быть переиспользуемым между UI, API, CLI and Agent API. | Иначе разные поверхности принимают разные решения. |
| CR-DOMAIN-019 | CommandResult должен иметь единый доменный shape. | Human и agent должны одинаково понимать outcome, warnings, retryability and next actions. |
| CR-DOMAIN-020 | Control plane, runtime and generated artifact boundaries must remain explicit. | Смешивание этих слоев создает hidden lock-in and unsafe automation. |
