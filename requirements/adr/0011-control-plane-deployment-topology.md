# ADR-0011 - Control Plane Deployment Topology

```yaml
id: ADR-0011
status: proposed
title: Control Plane Deployment Topology
context: CloudRING должен поддерживать local, private, edge, public provider и global federation без превращения одного control plane в новый lock-in центр.
decision: Control plane делится на локально автономные presence control planes и federation/global coordination planes, связанные через явные sync, policy и ownership contracts.
supersedes: []
requirements:
  - CR-ARCH-005..008
  - CR-ARCH-021..024
  - CR-INFRA-006
  - CR-INFRA-012..016
  - CR-SELF-007..012
```

## Контекст

Control plane управляет сервисами, ресурсами, lifecycle, policy, audit и
self-service. Если он существует только как централизованный SaaS, private и
edge сценарии теряют автономию. Если каждый участник полностью изолирован,
CloudRING не станет сетью облаков.

Нужна топология, где private cloud может работать самостоятельно, public
provider может продавать услуги, edge может переживать потерю связи, а global
federation может синхронизировать каталоги, доверие, usage и policy без
присвоения владения локальной инфраструктурой.

## Решение

CloudRING использует разделенную topology:

- Presence Control Plane управляет локальными ресурсами, сервисами, policy,
  audit, health, users, upgrades и emergency actions конкретной presence;
- Presence Control Plane хранит локальную lifecycle history, recovery context и
  policy decisions, чтобы владелец зоны мог расследовать и восстанавливать
  систему без обязательного внешнего сервиса;
- Federation Coordination Plane синхронизирует catalog metadata, participant
  identity, trust state, compatibility, usage envelopes и settlement inputs;
- Global/Network Portal может агрегировать выбор и видимость, но не должен быть
  единственным владельцем lifecycle локальной presence;
- private и edge presence должны иметь autonomous mode для критичных функций;
- sync между planes должен быть идемпотентным, проверяемым и ограниченным
  scopes;
- ownership ресурса, данных и billing events должен быть ясен в каждом sync
  event;
- потеря связи с federation не должна останавливать локальные разрешенные
  workloads, но может ограничивать publication, updates, settlement или внешние
  orders.

## Почему

CloudRING строится как cloud-of-clouds, а не как новый централизованный
монолит. Разделенная topology позволяет начать с private cloud зоны и позже
подключить ее к marketplace/federation, не переписывая локальный контроль и не
лишая владельца инфраструктуры автономии.

## Последствия

Положительные:

- private и edge получают реальную автономию;
- federation может расти без полного доверия между участниками;
- пользователь видит, где принимается решение и кто владеет ресурсом;
- сбой global coordination не уничтожает локальный control plane.

Отрицательные:

- требуется строгая модель sync и конфликтов;
- UI должен объяснять локальный и глобальный контекст без перегруза;
- часть операций будет иметь разные статусы local committed и federation synced.

Follow-up:

- описать Stage 2 local-only и federation-ready modes;
- определить минимальный набор events для presence sync;
- добавить conflict/disconnected semantics в federation ADR;
- связать topology с incident, audit и upgrade flows.

## Критерии Приемки

- Stage 2 private presence может выполнять локальные user/admin operations без
  обязательного подключения к global/federation plane.
- Local ownership, lifecycle history, policy decisions и recovery evidence
  остаются доступными владельцу private presence.
- Пользователь и администратор видят, какие действия локальны, какие требуют
  внешней синхронизации, а какие недоступны offline.
- Sync events имеют identity, owner, scope, idempotency key, policy result и
  audit trail.
- Потеря связи не ломает уже разрешенные локальные workloads.
- Подключение к federation является расширением presence, а не миграцией в
  другой продукт.
