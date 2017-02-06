# Product Stages And Finished Increments

CloudRING слишком велик, чтобы ждать "финальной версии".
Каждый этап должен быть законченным, полезным и расширяемым продуктом.

Правило: следующий этап добавляет слой, но не обесценивает предыдущий.

## Stage 0 - Requirements And Agent Memory

Назначение: создать живую память продукта.

Детальная спецификация: [stages/00-requirements-and-agent-memory.md](stages/00-requirements-and-agent-memory.md).

North Star slice:

- Доказано, что опыт из источников можно превратить в agent-readable
  требования без копирования исходников и пилотного контекста.
- Метрики: `CR-METRIC-010`, `CR-METRIC-027`, governance checklist completeness.

Готовый продукт этапа:

- Папка `requirements`.
- Source analysis.
- Product principles.
- Reference architecture.
- Agent-readable requirement format.
- Правила обезличивания и переноса опыта.

Критерии готовности:

- Новый источник можно добавить без переписывания всей структуры.
- AI-агент может понять миссию, домены и формат требований.
- В требованиях нет внутренних имен, секретов и копий исходников.

## Stage 1 - Solo Developer Cloud

Назначение: CloudRING как локальная платформа разработки сервисов.

Детальная спецификация: [stages/01-solo-developer-cloud.md](stages/01-solo-developer-cloud.md).

North Star slice:

- Разработчик может создать и отладить переносимый сервис через стандартный
  контракт без зависимости от ручных локальных инструкций.
- Метрики: `CR-METRIC-006`, `CR-METRIC-021`, `CR-METRIC-022`,
  `CR-METRIC-023`, `CR-METRIC-024`.

Готовый продукт этапа:

- CLI/API bootstrap.
- Presence bootstrap activation evidence.
- Service manifest.
- Service template.
- Local runtime.
- Component dependencies.
- Task library.
- Controlled extension/task automation evidence.
- Docs preview.
- Observability defaults.

Пользовательская ценность:

- Разработчик создает сервис, запускает зависимости, дебажит, выполняет tasks,
  смотрит docs и metrics без ручного разворачивания инфраструктуры.

Критерии готовности:

- Новый сервис создается из шаблона.
- Local runtime bootstrap имеет trusted activation evidence с preflight,
  rollback/cleanup и source-safe report.
- Task/plugin/dependency/boilerplate automation имеет controlled evidence и не
  выдается за production managed runner.
- Локальный debug работает для сервиса с базой, object storage, secrets и tracing.
- Tasks запускаются одинаково локально и в CI.
- Сервис имеет минимальные docs, metrics, logs и traces.

## Stage 2 - Private Cloud OS Zone

Назначение: самостоятельная инсталляция CloudRING на одном или нескольких
серверах.

Детальная спецификация: [stages/02-private-cloud-os-zone.md](stages/02-private-cloud-os-zone.md).

North Star slice:

- Владелец инфраструктуры получает базовое облако под своим контролем,
  с self-service и upgrade path без публичного провайдера.
- Метрики: `CR-METRIC-006`, `CR-METRIC-007`, `CR-METRIC-009`,
  `CR-METRIC-026`, `CR-METRIC-028`.

Готовый продукт этапа:

- Installer/distribution.
- Presence bootstrap activation and enrollment evidence.
- IAM and Resource Manager.
- Compute/network/storage basics.
- Monitoring and alerting.
- Update channel.
- Backup basics.
- Admin portal.
- Policy basics.

Пользовательская ценность:

- Владелец инфраструктуры получает работающую private cloud зону без покупки
  public cloud.

Критерии готовности:

- Инсталляция проходит на single-host и multi-node профиле.
- Private presence readiness подтверждается bootstrap/enrollment evidence, а не
  только наличием installer, config или локального runtime.
- Есть self-service создание базового workload.
- Есть мониторинг и управляемое обновление.
- Есть понятный путь восстановления после сбоя.

## Stage 3 - Service Store For Private Cloud

Назначение: подключение готовых сервисов в private-инсталляции.

Детальная спецификация: [stages/03-service-store-for-private-cloud.md](stages/03-service-store-for-private-cloud.md).

North Star slice:

- Private cloud получает app-store модель сервисов с лицензированием,
  совместимостью и updates/support без потери локального контроля.
- Метрики: `CR-METRIC-011`, `CR-METRIC-012`, `CR-METRIC-014`,
  `CR-METRIC-015`, `CR-METRIC-024`.

Готовый продукт этапа:

- Local marketplace/catalog.
- Service connector.
- Compatibility checks.
- License/subscription state.
- Offline/connected update modes.
- Enterprise extension hooks.

Пользовательская ценность:

- Private cloud владелец устанавливает готовые сервисы как из app store,
  лицензирует дополнительные и разрабатывает собственные.

Критерии готовности:

- Сервис публикуется в catalog.
- Сервис устанавливается через portal/API/CLI.
- Сервис проходит conformance checks.
- Лицензия/подписка влияет на updates/support, но не ломает уже установленную
  базовую работоспособность.

## Stage 4 - Public Cloud Provider Kit

Назначение: возможность построить публичного облачного провайдера.

Детальная спецификация: [stages/04-public-cloud-provider-kit.md](stages/04-public-cloud-provider-kit.md).

North Star slice:

- Независимый провайдер может запустить presence, продавать сервисы и принимать
  usage/billing через единый контракт.
- Метрики: `CR-METRIC-007`, `CR-METRIC-011`, `CR-METRIC-018`,
  `CR-METRIC-027`, `CR-METRIC-029`.

Готовый продукт этапа:

- Provider onboarding.
- Public plans and pricing.
- Tenant management.
- Billing and usage gateway.
- Support workflows.
- SLA/SLO.
- Marketplace publication.
- Provider operations portal.

Пользовательская ценность:

- Независимый провайдер запускает CloudRING presence и продает услуги.

Критерии готовности:

- Provider может опубликовать тарифы и регионы.
- Клиент может заказать сервис и получить счет.
- Usage events проходят через проверяемый pipeline.
- Provider видит capacity, incidents, revenue и support.

## Stage 5 - Federation Network

Назначение: соединение нескольких provider/private/edge presence.

Детальная спецификация: [stages/05-federation-network.md](stages/05-federation-network.md).

North Star slice:

- Пользователь видит и использует предложения нескольких участников, а
  federation выполняет catalog sync, policy, usage и settlement.
- Метрики: `CR-METRIC-003`, `CR-METRIC-016`, `CR-METRIC-017`,
  `CR-METRIC-018`, `CR-METRIC-019`.

Готовый продукт этапа:

- Participant registry.
- Federation catalog sync.
- Cross-cloud connect.
- Settlement.
- Trust and certification.
- Cross-provider observability.
- Migration/DR scenarios.

Пользовательская ценность:

- Клиент выбирает сервисы между провайдерами и юрисдикциями, переносит workload
  и использует DR/backup/replication между участниками.

Критерии готовности:

- Два независимых presence обмениваются catalog and usage metadata.
- Пользователь видит предложения из нескольких presence в одном portal.
- Settlement рассчитывает доли участников.
- Cross-provider DR/backup проходит policy checks.

## Stage 6 - Global CloudRING

Назначение: глобальная сеть облачных сервисов без единого lock-in центра.

Детальная спецификация: [stages/06-global-cloudring.md](stages/06-global-cloudring.md).

North Star slice:

- CloudRING доказывает cloud-of-clouds сценарий: выбор provider/jurisdiction,
  marketplace, migration/DR и settlement across independent participants.
- Метрики: `CR-METRIC-001`, `CR-METRIC-002`, `CR-METRIC-003`,
  `CR-METRIC-014`, `CR-METRIC-019`, `CR-METRIC-020`.

Готовый продукт этапа:

- Global portal/API.
- Multi-provider marketplace.
- Jurisdiction-aware placement.
- Global settlement.
- ISV cross-licensing.
- Edge/disconnected support.
- Agent-operated SRE and support.
- Governance and dispute resolution.

Пользовательская ценность:

- CloudRING становится сетью облаков, где пользователь выбирает сервис,
  провайдера, регион, trust model и цену без потери переносимости.

Критерии готовности:

- Участники разных типов подключаются через стандартизованный onboarding.
- Сервисы публикуются и продаются между участниками.
- Пользователь может мигрировать или реплицировать поддерживаемый сервис.
- Governance управляет качеством без превращения сети в закрытый монолит.

## Stage 7 - Self-Evolving Platform

Назначение: платформа, которая системно учится.

Детальная спецификация: [stages/07-self-evolving-platform.md](stages/07-self-evolving-platform.md).

North Star slice:

- Платформа превращает инциденты, новые источники и технологические изменения
  в требования, ADR, проверки и безопасные агентские операции.
- Метрики: `CR-METRIC-010`, `CR-METRIC-025`, `CR-METRIC-030`,
  agent follow-up requirement rate, ADR closure rate.

Готовый продукт этапа:

- Requirements feedback loop.
- Incident-to-ADR automation.
- AI conformance review.
- Autonomous remediation with approvals.
- Continuous compatibility testing.
- Technology refresh without contract breakage.

Пользовательская ценность:

- Платформа не устаревает вместе с технологическим поколением.

Критерии готовности:

- Замена runtime/backend не ломает service contracts.
- Инциденты создают требования и проверки.
- AI-агенты безопасно выполняют рутинную эксплуатацию.
- Человек остается владельцем смысла, политики и ключевых решений.
