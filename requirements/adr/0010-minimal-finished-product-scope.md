# ADR-0010 - Minimal Finished Product Scope

```yaml
id: ADR-0010
status: proposed
title: Minimal Finished Product Scope
context: CloudRING должен быть полезен на первом реализуемом этапе, но не должен пытаться сразу стать всей глобальной федерацией.
decision: Stage 1 является законченным Solo Developer Cloud для создания, проверки и локального запуска переносимых сервисов.
supersedes: []
requirements:
  - CR-PLAT-001..010
  - CR-INFRA-001..006
  - CR-DX-001..029
  - CR-OCS-001..032
  - CR-OPS-001..014
  - CR-APPROVAL-001..008
  - CR-METRIC-021..025
```

## Контекст

CloudRING имеет большую цель: open cloud/post-cloud платформа, marketplace,
private/public/edge presence и federation. Если первый этап попытается
реализовать всю цель сразу, он станет слишком широким. Если первый этап будет
только библиотекой или набором документов, он не докажет продуктовую ценность.

Первый законченный продукт должен быть маленьким, но настоящим: он должен
помогать создать переносимый сервис по стандарту CloudRING и сразу проверять
те принципы, на которых будет строиться вся платформа.

## Решение

Минимальный законченный продукт Stage 1 - Solo Developer Cloud.

Входит в Stage 1:

- onboarding разработчика и AI-агента в локальную среду;
- создание сервиса из template;
- service manifest по Open Cloud Standard;
- локальный запуск сервиса и его зависимостей через runtime profile;
- единый start/stop/status/debug loop;
- task library с одинаковым смыслом локально и в CI;
- docs preview для сервиса;
- базовые metrics, logs, traces и health/readiness;
- conformance checks для manifest, docs, observability и portability;
- понятный отчет о готовности сервиса к следующему stage.

Не входит в Stage 1:

- полноценный public cloud provider;
- federation network;
- marketplace commerce и settlement;
- production-grade multi-tenant private cloud;
- автоматическое управление реальными деньгами, юридическими обязательствами
  или критичной инфраструктурой;
- поддержка всех возможных runtime и классов workload.

## Почему

Stage 1 должен доказать самый важный корневой тезис CloudRING: сервис можно
создать не под конкретного провайдера, а под открытый переносимый контракт.
Если это работает для одиночного разработчика, дальше можно наращивать private
cloud, service store, provider kit и federation, не меняя смысл сервисов.

## Последствия

Положительные:

- первый продукт реалистичен для одиночного основателя с AI-агентами;
- ранняя ценность появляется до построения полной инфраструктуры;
- сервисный контракт проверяется с первого дня;
- будущие marketplace и federation получают совместимые сервисы заранее.

Отрицательные:

- Stage 1 не продает полноценное публичное облако;
- часть инфраструктурных решений остается ADR/backlog;
- пользователю нужно явно объяснить, что это developer cloud, а не production
  provider kit.

Follow-up:

- вести детальную спецификацию Stage 1 в `requirements/stages/01-solo-developer-cloud.md`;
- создать conformance profile `stage1-service-ready`;
- определить Stage 2 boundary для private cloud OS zone;
- не добавлять commerce/federation в Stage 1 без отдельного ADR.

## Критерии Приемки

- Разработчик создает новый переносимый сервис из template и запускает его
  локально через стандартный flow.
- Сервис имеет manifest, docs, health/readiness, metrics, logs и traces.
- Зависимости сервиса поднимаются и проверяются через declared dependencies.
- Task library выполняет build/validate/test/docs/observe/package локально и в
  CI с одинаковым смыслом.
- Conformance report показывает, какие требования Stage 1 выполнены, а какие
  блокируют переход к Stage 2/marketplace.
