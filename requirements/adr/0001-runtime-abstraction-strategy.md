# ADR-0001 - Runtime Abstraction Strategy

```yaml
id: ADR-0001
status: proposed
title: Runtime Abstraction Strategy
context: CloudRING должен работать в local, private, edge, public и federation сценариях, где доступные runtime и операционные ограничения различаются.
decision: Product contract CloudRING является runtime-neutral, а конкретные runtime подключаются через совместимые профили и adapters.
supersedes: []
requirements:
  - CR-ARCH-017..020
  - CR-DX-004..006
  - CR-INFRA-001..006
  - CR-CORE-007
```

## Контекст

CloudRING не должен превращать одну технологию запуска workload в новый lock-in.
Платформа должна позволять развивать local developer cloud, private cloud,
edge-узлы, публичные presence и federation без переписывания сервисного
контракта при смене runtime.

Опыт исходной архитектуры показывает, что разработчику нужна локальная среда,
близкая по поведению к production, но это не означает, что вся платформа должна
быть навсегда привязана к одному runtime. Важен переносимый lifecycle: создать,
проверить, запустить, наблюдать, обновить, остановить, экспортировать и
мигрировать сервис.

## Решение

CloudRING принимает runtime-neutral стратегию:

- обязательным является не конкретный runtime, а CloudRING capability contract;
- каждый runtime описывается как profile с явными возможностями, ограничениями,
  стоимостью, trust boundary и совместимостью;
- local runtime должен проверять тот же сервисный контракт, что private/public
  presence, даже если реализует его проще;
- platform core не должен знать внутренние детали runtime, кроме declared
  capabilities и lifecycle results;
- service manifest должен описывать потребности сервиса, а не инструкции под
  один runtime;
- runtime adapter может быть заменен без изменения пользовательского order flow,
  service manifest и marketplace listing;
- если сервис зависит от runtime-specific behavior, это должно быть видно как
  portability limitation до установки или покупки.

## Почему

CloudRING создается для снижения vendor, technology и jurisdiction lock-in.
Если первая реализация жестко привяжет продукт к одному runtime, платформа
решит часть старой проблемы и создаст новую. Runtime-neutral стратегия позволяет
начать с простого локального профиля, но сохранить путь к private, edge,
public и federation сценариям.

## Последствия

Положительные:

- сервисы проектируются вокруг переносимого контракта;
- local-first разработка не конфликтует с будущей federation;
- можно добавлять новые runtime без переписывания пользовательских сценариев;
- AI-агенты получают устойчивую модель рассуждения: capability важнее
  реализации.

Отрицательные:

- требуется строгая модель capability и conformance;
- runtime adapter становится самостоятельной зоной качества и безопасности;
- некоторые возможности придется явно объявлять как optional, а не считать
  доступными везде.

Follow-up:

- описать минимальный набор runtime capabilities для Stage 1;
- описать compatibility matrix для local, private, edge, public profiles;
- добавить conformance checks, которые доказывают, что adapter выполняет
  заявленный contract;
- связать runtime profiles с marketplace certification levels.

## Критерии Приемки

- Один и тот же service manifest проходит проверку в local profile и имеет
  понятный путь к private profile без изменения продуктового смысла сервиса.
- Runtime profile показывает supported, unsupported и degraded capabilities.
- Пользователь видит portability limitations до запуска сервиса.
- Замена runtime adapter не меняет пользовательский order/API/CLI flow.
- AI-агент может выбрать runtime profile по ограничениям сервиса, а не по
  внутренним именам технологий.

