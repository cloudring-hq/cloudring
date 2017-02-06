# Stage 2 - Private Cloud OS Zone

```yaml
id: STAGE-002
status: draft
title: Private Cloud OS Zone
goal: Дать владельцу инфраструктуры автономную CloudRING presence, которая предоставляет базовые облачные capability под локальным контролем и готова к будущему подключению marketplace/federation.
primary_users:
  - infrastructure owner
  - private cloud administrator
  - platform operator
  - service owner
  - AI operations agent
related_adr:
  - ADR-0001
  - ADR-0005
  - ADR-0008
  - ADR-0009
  - ADR-0011
related_requirements:
  - CR-PLAT-001..010
  - CR-INFRA-001..011
  - CR-PRESBOOT-001..032
  - CR-SEC-001..024
  - CR-SELF-007..012
  - CR-OPS-009..028
  - CR-APPROVAL-001..008
```

## Назначение

Stage 2 превращает CloudRING в самостоятельную private cloud зону. Это уже не
только среда разработки сервисов, а минимально законченная облачная presence,
которую владелец инфраструктуры может установить, администрировать, обновлять,
наблюдать, восстанавливать и использовать для self-service workloads без
обязательного публичного провайдера.

Главный результат: у пользователя появляется облачная зона под своим контролем,
с IAM, Resource Manager, базовыми compute/network/storage capability, policy,
observability, backup/restore, update path и agent-safe operations.

## Product Promise

Администратор разворачивает CloudRING на своей инфраструктуре, получает единый
portal/API/CLI, видит health и capacity, создает базовый workload через
self-service, управляет policy и updates через plan/apply/validate flow,
проверяет backup/restore и может подключить AI-агента для безопасной routine
эксплуатации. Все это не требует покупки public cloud и не ломает путь к
будущей federation.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-STAGE2-001 | Stage 2 должен быть самостоятельной private cloud presence, а не расширенным dev profile. | Владелец инфраструктуры должен получить готовую ценность до marketplace/federation. | Инсталляция предоставляет локальный portal/API/CLI, admin health view, bootstrap activation evidence и self-service создание базового workload. |
| CR-STAGE2-002 | Stage 2 должен поддерживать single-host и multi-node profiles с понятной границей готовности. | Малый старт нужен для adoption, multi-node нужен для production/private сценариев. | Пользователь видит, какие capability доступны, degraded или unsupported в каждом profile. |
| CR-STAGE2-003 | Переход от single-host к multi-node должен быть upgrade path, а не миграцией в другой продукт. | Малый старт не должен становиться тупиком. | Есть documented readiness gate и preserved identity/resource model при расширении. |
| CR-STAGE2-004 | Presence Control Plane должен быть локально автономным для критичных функций. | Private cloud не должен зависеть от внешнего SaaS для базовой работы. | При отсутствии внешней связи разрешенные локальные workloads продолжают работать и управляться. |
| CR-STAGE2-005 | Control plane должен явно различать local-only, federation-ready и federation-connected режимы. | Пользователь должен понимать степень внешней зависимости. | UI/API показывают режим presence и ограничения доступных действий. |
| CR-STAGE2-006 | Все основные Stage 2 действия должны быть доступны через UI, API, CLI и Agent API. | Self-service и агентская эксплуатация не должны зависеть от одного интерфейса. | Install, health, capacity, policy, workload lifecycle, backup/recovery и update plan/apply/validate имеют product flow во всех основных интерфейсах или documented исключение. |
| CR-STAGE2-007 | IAM и Resource Manager являются обязательными capability Stage 2. | Без identity, ownership и resource accounting это не облачная платформа. | Workload, policy, audit и capacity привязаны к owner/project/resource model. |
| CR-STAGE2-008 | Compute capability должен быть backend-neutral. | Разные private-инфраструктуры используют разные способы запуска workload. | Пользователь заказывает workload через единый contract, а backend profile показывает ограничения. |
| CR-STAGE2-009 | Network capability должен включать адресацию, ingress, service discovery и policy boundaries. | Workload должен быть доступен и изолирован. | Созданный workload имеет предсказуемый endpoint, network policy и audit-visible connectivity. |
| CR-STAGE2-010 | Storage capability должен включать block/object/backup profiles или явные ограничения. | Stateful workloads и restore невозможны без storage contract. | Storage profile показывает durability, backup support, quota и portability limitations. |
| CR-STAGE2-011 | Monitoring, logs, alerts и audit должны быть доступны из коробки. | Один человек с агентами должен видеть состояние платформы. | Admin health view показывает capacity, incidents, alerts, policy violations и recent changes. |
| CR-STAGE2-012 | Update flow должен быть plan/apply/validate. | Обновление private cloud без плана опасно. | Перед изменением показываются affected services, risk class, rollback/compensation и validation checks. |
| CR-STAGE2-013 | Backup/restore должен быть обязательным readiness gate для stateful capability. | Непроверенный backup не является backup. | Есть restore-test evidence для критичных stateful components и понятное RPO/RTO ожидание. |
| CR-STAGE2-014 | Secret management должен следовать `ADR-0005`. | Private cloud содержит реальные trust boundaries. | Manifest, installer specs и generated files не содержат plaintext secrets; secret references имеют owner/scope/environment. |
| CR-STAGE2-015 | Data portability должен следовать `ADR-0008`. | Private cloud должен решать lock-in, а не создавать локальный тупик. | Поддержанный workload имеет export/restore/import story или явное documented limitation. |
| CR-STAGE2-016 | Policy engine должен участвовать в placement до provisioning. | Data residency, budgets, allowed services и security baselines нельзя проверять после факта. | Запрос workload отклоняется до создания ресурсов, если нарушает policy. |
| CR-STAGE2-017 | Admin self-service должен отвечать на вопросы health, capacity, updates, policy и recovery. | Платформа должна обслуживаться малой командой. | Администратор видит guided remediation и может передать safe tasks агенту. |
| CR-STAGE2-018 | AI operations agent должен работать только в рамках approval matrix. | Автономность не должна превращаться в неконтролируемый root-доступ. | Agent tasks имеют risk_class, scope, validation, rollback/compensation и audit. |
| CR-STAGE2-019 | Stage 2 должен иметь conformance profile `stage2-private-presence-ready`. | Нужна объективная граница готовности. | Report показывает installed capabilities, degraded areas, failed checks, risk items и next-stage readiness. |
| CR-STAGE2-020 | Stage 2 должен быть federation-ready без обязательной federation. | Private presence должна сохранять путь к cloud-of-clouds. | Catalog/policy/usage/audit metadata имеют структуру, пригодную для будущего sync, но не требуют внешнего подключения. |
| CR-STAGE2-021 | Пользователь должен видеть ownership и responsibility boundaries. | Private cloud смешивает роли платформы, владельца инфраструктуры и сервисов. | Portal/API показывают owner, operator, service responsibility и support boundary для каждого ресурса. |
| CR-STAGE2-022 | Stage 2 не должен включать marketplace commerce как обязательную функцию. | Иначе второй этап расползется в Stage 3/4. | Установка базовых workloads работает без catalog commerce, settlement и revenue sharing. |
| CR-STAGE2-023 | Stage 2 должен поддерживать local service installation только как controlled/private package flow. | До marketplace нужна безопасная установка внутренних сервисов. | Сервис проходит manifest/security/observability checks до установки в private presence. |
| CR-STAGE2-024 | Capacity management должен быть понятен человеку и агенту. | Private ресурсы конечны и должны планироваться. | Admin видит free/used/reserved capacity, saturation risks и suggested remediation. |
| CR-STAGE2-025 | Инциденты должны порождать knowledge artifacts. | Платформа должна учиться на опыте эксплуатации. | Повторяющийся incident создает requirement/ADR/runbook follow-up. |
| CR-STAGE2-026 | Stage 2 должен иметь graceful degradation model. | Private-инфраструктура не всегда идеальна. | Деградация capability отражается в health, placement decisions, user actions и conformance report. |

## Acceptance Scenarios

### Scenario A - Install Private Presence

Цель: доказать, что владелец инфраструктуры получает автономную облачную зону.

Критерии:

- presence проходит initial readiness checks;
- bootstrap activation evidence proves trusted assets, preflight, profile,
  diagnostics and rollback/cleanup;
- portal/API/CLI доступны локальному администратору;
- IAM/Resource Manager создает owner/project/resource scope;
- admin health view показывает capacity, alerts, policy и update status;
- conformance report фиксирует `stage2-private-presence-ready` или конкретные
  blockers.

### Scenario B - Self-Service Basic Workload

Цель: доказать, что Stage 2 предоставляет облачную услугу, а не только control
plane.

Критерии:

- пользователь создает базовый workload через self-service flow;
- placement проходит policy check до provisioning;
- workload получает compute, network endpoint, storage profile и observability;
- пользователь видит owner, status, cost/showback inputs и recovery actions.

### Scenario C - Update With Plan And Validation

Цель: доказать, что private cloud обновляется безопасно.

Критерии:

- update plan показывает affected capabilities, services и risk class;
- risky/destructive операции требуют approval по `ADR-0009`;
- после apply выполняется validation;
- при failure есть rollback/compensation или явное объяснение невозможности.

### Scenario D - Backup, Restore And Portability

Цель: доказать, что данные не становятся новым lock-in.

Критерии:

- stateful workload имеет backup policy;
- restore-test выполнен и привязан к evidence;
- portability profile показывает exportable data, metadata, compatible target и
  limitations;
- secret values не экспортируются без owner-approved flow.

### Scenario E - Disconnected Autonomy

Цель: доказать, что private presence не зависит от внешней сети для базовой
работы.

Критерии:

- разрешенные локальные workloads продолжают работать без federation/global
  connectivity;
- локальные admin operations сохраняют audit trail;
- действия, требующие внешнего sync, явно помечаются как unavailable/deferred;
- восстановление связи синхронизирует pending events без дубликатов.

### Scenario F - Agent-Operated Routine Maintenance

Цель: доказать, что один человек с AI-агентами может поддерживать Stage 2.

Критерии:

- агент читает requirements, ADR, health и runbook перед действием;
- задача имеет risk_class, scope, validation и rollback/compensation;
- агент выполняет read-only/safe-change routine без прямого доступа к секретам;
- результат сохраняется как audit и human-readable summary.

## Agent Task Seeds

```yaml
id: TASK-STAGE2-001
goal: Описать conformance profile stage2-private-presence-ready.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/02-private-cloud-os-zone.md
    - requirements/03-platform-capabilities-and-lifecycle.md
    - requirements/08-private-edge-infrastructure.md
    - requirements/17-acceptance-criteria.md
  exclude:
    - marketplace settlement
    - public provider billing
inputs:
  - CR-STAGE2-019
  - CR-INFRA-001..011
  - CR-SELF-007..012
expected_outputs:
  - readiness checks
  - report fields
  - blocking vs warning categories
permissions:
  secrets: none
  destructive_actions: false
validation:
  - every check maps to a requirement or ADR
rollback:
  - mark disputed checks as draft and link to ADR follow-up
```

```yaml
id: TASK-STAGE2-002
goal: Спроектировать product flow для update plan/apply/validate.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/02-private-cloud-os-zone.md
    - requirements/21-agent-approval-matrix.md
    - requirements/07-operations-resilience-observability.md
  exclude:
    - runtime-specific commands
inputs:
  - CR-STAGE2-012
  - CR-OPS-009..014
  - CR-APPROVAL-001..008
expected_outputs:
  - user-visible flow states
  - required evidence
  - approval boundaries
permissions:
  secrets: none
  destructive_actions: false
validation:
  - flow answers all self-service quality questions
rollback:
  - supersede via ADR if update topology changes
```

## Non-Goals

Stage 2 намеренно не является:

- federation network;
- public provider kit;
- paid marketplace;
- global settlement system;
- универсальной edge-платформой;
- полной заменой всех enterprise integrations;
- обещанием production HA для любого single-host сценария.

Stage 2 должен быть честной private cloud зоной: полезной самой по себе,
готовой к расширению, но не маскирующей будущие stages под ранний MVP.

## Readiness Gate

Stage 2 считается готовым, когда:

- presence устанавливается и проходит readiness checks;
- IAM/Resource Manager, compute, network, storage, monitoring, policy и audit
  доступны как базовые capability;
- self-service создает базовый workload;
- admin видит health, capacity, alerts, upgrades и recovery actions;
- update работает через plan/apply/validate;
- backup/restore проверен для stateful capability;
- secret handling соответствует `ADR-0005`;
- portability profile соответствует `ADR-0008`;
- control plane topology соответствует `ADR-0011`;
- agent routine maintenance проходит через approval matrix;
- conformance report показывает `stage2-private-presence-ready` или конкретные
  blockers.
