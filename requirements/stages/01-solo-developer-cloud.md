# Stage 1 - Solo Developer Cloud

```yaml
id: STAGE-001
status: draft
title: Solo Developer Cloud
goal: Дать одному разработчику и AI-агентам законченный локальный CloudRING-продукт для создания переносимых сервисов.
primary_users:
  - independent founder
  - service developer
  - platform developer
  - AI coding agent
  - AI verification agent
related_adr:
  - ADR-0001
  - ADR-0002
  - ADR-0009
  - ADR-0010
related_requirements:
  - CR-DX-001..029
  - CR-OCS-001..032
  - CR-PLAT-009..010
  - CR-OPS-001..014
  - CR-APPROVAL-001..008
  - CR-METRIC-021..025
  - CR-PRESBOOT-001..032
  - CR-EXTAUTO-001..032
```

## Назначение

Stage 1 превращает CloudRING из идеи и требований в первый законченный продукт:
локальную среду, где сервис создается, запускается, документируется,
наблюдается и проверяется по переносимому контракту.

Главный результат: завтра можно начать писать новый CloudRING service так, чтобы
его смысл, lifecycle, зависимости, observability, docs и portability были
понятны человеку, платформе и AI-агенту без доступа к старым исходникам.

## Product Promise

Разработчик открывает CloudRING, создает сервис из шаблона, описывает его
контракт, активирует локальную среду через доказуемый bootstrap, проверяет
dependencies, смотрит docs, metrics, logs и traces, запускает governed tasks or
extensions и получает conformance report. Вся эта работа происходит без ручного
знания внутренностей runtime и без привязки к будущему провайдеру.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-STAGE1-001 | Stage 1 должен быть самостоятельным продуктом, а не демо-скриптом. | Первый этап должен создавать реальную ежедневную ценность. | Разработчик может создать, запустить, проверить и сопровождать сервис без обращения к будущим Stage 2..6 возможностям. |
| CR-STAGE1-002 | Первым пользователем Stage 1 является одиночный основатель с AI-агентами. | CloudRING должен быть строимым малой командой и автоматизируемым с первого дня. | Все ключевые действия имеют CLI/API или agent-readable contract, а не только ручной UI flow. |
| CR-STAGE1-003 | Onboarding должен объяснять минимальный путь до первого работающего сервиса. | Сложный старт убивает adoption и делает платформу зависимой от носителей знания. | Новый пользователь проходит путь до первого health-сигнала сервиса по одной документированной последовательности. |
| CR-STAGE1-004 | Новый сервис создается из opinionated template. | Шаблон закрепляет качество, которое иначе будет забыто. | Template содержит manifest, source skeleton, docs, tests, observability conventions и task entrypoints. |
| CR-STAGE1-005 | Template должен быть заменяемым и версионируемым. | Один тип сервиса не покроет все будущие workload. | Пользователь видит template version, supported service type и migration notes. |
| CR-STAGE1-006 | Service manifest является центром Stage 1. | Без manifest сервис не станет переносимым объектом CloudRING. | Запуск workload в Stage 1 без валидного manifest невозможен; draft-заготовки без manifest не получают runtime execution и `stage1-service-ready` статус. |
| CR-STAGE1-007 | Manifest описывает потребности сервиса, а не инструкции конкретного runtime. | Runtime должен быть заменяемым. | В manifest есть dependencies, lifecycle, observability, policy и portability fields без локальных путей и секретов. |
| CR-STAGE1-008 | Local runtime profile должен объявлять свои возможности и ограничения. | Разработчик должен понимать, что именно проверено локально. | Conformance report показывает supported, degraded и unsupported capabilities local profile. |
| CR-STAGE1-009 | Локальная среда должна иметь единый start/stop/status/debug loop. | Разработчик и агент не должны помнить разрозненные команды компонентов. | Для сервиса и dependencies доступны предсказуемые операции состояния. |
| CR-STAGE1-010 | Dependencies должны подниматься из declared contract. | Ручная настройка зависимостей разрушает воспроизводимость. | Сервис с database, object storage, secret store и tracing запускается из manifest-driven flow. |
| CR-STAGE1-011 | Secret handling должен быть safe-by-default. | Первый этап не должен приучать хранить секреты в manifest или repository. | Manifest не принимает plaintext secrets; local secrets имеют отдельный brokered/dev-safe flow. |
| CR-STAGE1-012 | Observability должна появляться при создании сервиса, а не после инцидента. | Без metrics/logs/traces сервис нельзя поддерживать агентами. | Template и conformance требуют health/readiness, structured logs, metrics и trace context. |
| CR-STAGE1-013 | Docs являются частью service readiness. | Агент не сможет сопровождать сервис без объясненного контекста. | Сервис имеет overview, API/contract notes, runbook, FAQ и link на manifest. |
| CR-STAGE1-014 | Docs preview должен работать локально. | Документация должна проверяться в том же dev loop, что код. | Разработчик видит актуальные docs до публикации сервиса. |
| CR-STAGE1-015 | Task library должна быть первым классом продукта. | Повторяемые операции должны быть переносимыми, а не частными скриптами. | Минимум build, validate, test, docs, observe и package tasks имеют единый contract. |
| CR-STAGE1-016 | Tasks должны иметь одинаковый смысл локально и в CI. | Иначе проверка в CI не отражает реальный dev loop. | Один task definition запускается локально и в CI profile с одинаковым expected outcome. |
| CR-STAGE1-017 | Каждая изменяющая операция должна иметь risk class, plan/dry-run и approval boundary. | AI-агенты должны показывать намерение до изменения состояния и не обходить policy. | Для runtime/dependency/task operations есть risk class, explainable plan, validation и approval requirement по `ADR-0009`/`CR-APPROVAL-*`. |
| CR-STAGE1-018 | Ошибки должны быть понятны человеку и машиночитаемы агенту. | Агентам нужны коды, людям нужны причины и следующие действия. | Ошибка содержит code, message, category, suggested next step и related requirement или docs link. |
| CR-STAGE1-019 | Conformance report является главным артефактом готовности. | Нужен объективный мост от локального сервиса к будущим stages. | Report перечисляет passed, failed, skipped checks и portability limitations. |
| CR-STAGE1-020 | Stage 1 должен измерять developer success. | Без метрик невозможно понять, упрощает ли платформа работу. | Собираются или вручную фиксируются time to first service, local debug success, task portability, docs completeness и conformance feedback time. |
| CR-STAGE1-021 | Stage 1 не должен требовать публичного облака. | Первый продукт должен работать независимо от внешнего провайдера. | Все core flows Stage 1 доступны в local/offline-friendly profile с документированными исключениями. |
| CR-STAGE1-022 | Stage 1 должен готовить сервис к Stage 2, но не реализовывать Stage 2. | Граница продукта сохраняет фокус. | Report показывает private-readiness gaps, но не требует production multi-node установки. |
| CR-STAGE1-023 | Пользователь должен видеть, какие решения являются временными local assumptions. | Временное не должно незаметно стать архитектурой. | Local-only assumptions маркируются в report и docs. |
| CR-STAGE1-024 | AI-агент должен иметь безопасный scope для работы с сервисом. | Основатель должен масштабировать работу агентами без потери контроля. | Agent task object указывает include/exclude scope, permissions, risk class, approval requirement, validation и rollback/compensation. |
| CR-STAGE1-025 | Stage 1 должен поддерживать отказ от конкретного template/runtime без потери контракта. | Первая реализация не должна зацементировать случайный стек. | Альтернативный template или runtime profile может пройти тот же conformance baseline. |

## Acceptance Scenarios

### Scenario A - First Service

Цель: доказать, что новый пользователь может получить первый переносимый
CloudRING service.

Критерии:

- пользователь создает сервис из template;
- manifest проходит schema validation;
- local runtime bootstrap имеет trusted activation evidence и не заявляет
  Stage 2 private presence readiness;
- task/plugin/dependency/boilerplate automation имеет controlled automation
  evidence и не заявляет managed production readiness;
- сервис запускается локально;
- health/readiness доступны через стандартный flow;
- conformance report показывает минимальный `stage1-service-ready` статус.

### Scenario B - Service With Dependencies

Цель: доказать, что сервис не является одиночным hello-world.

Критерии:

- manifest объявляет representative dependency set: database, object storage,
  secret store и tracing/observability;
- local runtime поднимает dependencies через declared contract;
- сервис получает доступ к dependencies без plaintext secrets в manifest;
- failure одной dependency отражается в health/readiness и report.

### Scenario C - Local And CI Task Parity

Цель: доказать, что локальная проверка и CI говорят об одном и том же.

Критерии:

- task `validate` имеет один definition для local и CI profiles;
- task result machine-readable;
- failed task возвращает понятную причину и next action;
- artifacts проверки можно приложить к review или agent handoff.

### Scenario D - Docs And Observability Review

Цель: доказать, что сервис готов к сопровождению.

Критерии:

- docs preview открывается локально;
- docs связаны с manifest и runbook;
- metrics/logs/traces доступны в local profile;
- conformance report проверяет минимальный набор observability signals.

### Scenario E - Agent-Safe Contribution

Цель: доказать, что AI-агент может улучшать сервис в границах политики.

Критерии:

- агент получает задачу с scope, inputs, expected outputs и validation;
- агент не получает прямой доступ к секретам;
- изменяющая операция имеет risk class, plan/dry-run, validation и нужный
  approval по `ADR-0009`;
- результат проверяется conformance checks.

## Agent Safety Boundary

Stage 1 использует `ADR-0009` и `21-agent-approval-matrix.md` как обязательную
границу автономии.

До принятия более детальной runtime policy агент может автономно выполнять
только:

- `read-only` действия внутри выданного scope;
- `safe-change` действия, если есть validation, audit и rollback/compensation;
- `controlled-change` действия только через pre-approved runbook.

`risky-change`, `destructive` и `emergency` действия не входят в обычную
автономию Stage 1. Они требуют явного approval и отдельной записи в audit.

Агент не классифицирует действие как безопасное произвольно. Risk class должен
следовать из approval matrix, task definition или pre-approved runbook. Если
класс риска неясен, действие считается `controlled-change` или выше и требует
approval.

## Agent Task Seeds

```yaml
id: TASK-STAGE1-001
goal: Спроектировать минимальный service template для Stage 1.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/01-solo-developer-cloud.md
    - requirements/02-open-cloud-standard-service-contract.md
    - requirements/04-developer-experience.md
  exclude:
    - production provider billing
    - federation settlement
inputs:
  - CR-STAGE1-004
  - CR-STAGE1-006
  - CR-STAGE1-012
expected_outputs:
  - template capability list
  - manifest sections
  - conformance checks
permissions:
  secrets: none
  destructive_actions: false
validation:
  - every template element maps to a requirement
rollback:
  - supersede the plan through ADR or stage requirement update
```

```yaml
id: TASK-STAGE1-002
goal: Описать conformance profile stage1-service-ready.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/01-solo-developer-cloud.md
    - requirements/17-acceptance-criteria.md
  exclude:
    - runtime-specific implementation
inputs:
  - CR-STAGE1-019
  - CR-OCS-001..032
  - CR-DX-008..014
expected_outputs:
  - checklist of required checks
  - report fields
  - failure categories
permissions:
  secrets: none
  destructive_actions: false
validation:
  - each check has observable pass/fail evidence
rollback:
  - mark incompatible checks as draft and link to ADR follow-up
```

## Non-Goals

Stage 1 намеренно не является:

- публичным облачным провайдером;
- production private cloud инсталлятором;
- federation marketplace;
- billing/settlement системой;
- системой, которая обещает production HA;
- универсальной поддержкой всех runtime и типов workload.

Эти ограничения не уменьшают ценность Stage 1. Они защищают первый продукт от
расползания и сохраняют главный смысл: переносимый сервисный контракт,
который можно развивать дальше.

## Readiness Gate

Stage 1 считается готовым, когда:

- существует минимум один reference service, созданный из template;
- service manifest проходит validation;
- local runtime profile запускает сервис и dependencies;
- docs preview, health/readiness, metrics, logs и traces доступны через единый
  developer flow;
  - task library выполняет build/validate/test/docs/observe/package;
- conformance report показывает `stage1-service-ready`;
- агент может прочитать требования, выполнить safe task и предоставить
  проверяемый результат без доступа к секретам.
