# ADR-0008 - Data Portability Contract

```yaml
id: ADR-0008
status: proposed
title: Data Portability Contract
context: CloudRING обещает снижать vendor lock-in, поэтому переносимость данных, metadata и state должна быть продуктовым контрактом, а не поздней миграционной утилитой.
decision: Каждый поддержанный класс сервиса объявляет portability profile: exportable data, metadata, state, secrets boundary, compatible targets, limitations и проверяемый restore/import path.
supersedes: []
requirements:
  - CR-CORE-006..008
  - CR-SELF-005
  - CR-FED-006..007
  - CR-OPS-021..028
  - CR-OPS-038..046
  - CR-OBSOPS-031..036
  - CR-INFPROFILE-031
  - CR-INFRA-029
```

## Контекст

CloudRING должен позволять пользователю уйти от провайдера, сменить
юрисдикцию, перенести workload в private cloud, восстановиться после сбоя или
реплицировать сервис между presence. Это невозможно, если данные и metadata
остаются в неописанном формате или требуют ручной экспертизы конкретной
реализации.

Переносимость не означает, что любой сервис можно мгновенно переместить куда
угодно. Она означает честный, проверяемый контракт: что можно экспортировать,
что нельзя, какие данные потеряют свойства, какие зависимости нужно создать на
целевой стороне и какие ограничения пользователь должен увидеть заранее.

## Решение

CloudRING вводит portability profile для сервисов и платформенных capability.

Portability profile должен описывать:

- какие пользовательские данные экспортируются;
- какие platform metadata нужны для восстановления сервиса;
- какой runtime/service state переносим, а какой создается заново;
- какие secret references остаются в исходной trust boundary;
- какие целевые profiles совместимы;
- какие потери, downtime, consistency limits или manual approvals возможны;
- как backup, restore, migration, upgrade, failover, export и import связаны с
  lifecycle сервиса;
- как проверить restore/import/failover до объявления операции успешной;
- какие audit events создаются при export, import, migration, backup, restore,
  failover и DR.

В Stage 2 portability contract является обязательным для базовых workloads,
backup/restore и upgrade path. В federation он станет основой cross-provider
migration, DR и provider exit.

## Почему

Если пользователь не может забрать данные и metadata, CloudRING не решает
vendor lock-in, а только меняет бренд зависимости. Portability contract делает
право ухода технически и продуктово проверяемым, а не маркетинговым обещанием.

## Последствия

Положительные:

- сервисы можно сравнивать по реальной переносимости;
- private cloud получает понятный backup/restore и upgrade path;
- marketplace может показывать portability score до покупки;
- AI-агенты могут планировать migration/DR по контракту, а не по догадкам.

Отрицательные:

- некоторые сервисы получат ограниченный portability profile;
- разработчикам придется описывать metadata/state явно;
- conformance должен проверять не только export, но и restore/import.

Follow-up:

- определить минимальные portability classes для Stage 2;
- добавить restore-test как acceptance для критичных stateful-сервисов;
- связать portability score с marketplace listing;
- описать user-facing предупреждения для неполной переносимости.

## Критерии Приемки

- Поддержанный сервис показывает portability profile до production/private
  установки.
- Export без restore/import проверки не считается достаточным доказательством
  переносимости.
- Secret values не экспортируются как часть данных без отдельного owner-approved
  flow.
- Backup/DR сценарий указывает target compatibility, policy constraints и
  проверку восстановления.
- Пользователь видит ограничения переносимости до заказа, установки или
  миграции сервиса.
