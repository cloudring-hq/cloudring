# ADR-0003 - Federation Event Bus And Sync Model

```yaml
id: ADR-0003
status: proposed
title: Federation Event Bus And Sync Model
context: CloudRING должен соединять независимые public, private, edge, ISV и reseller participants без полного доверия, постоянной связи и единого центрального оператора.
decision: Federation sync строится вокруг scoped, signed, idempotent domain events and snapshots with purpose-bound data sharing, delayed sync, conflict handling and audit evidence.
supersedes: []
requirements:
  - CR-FED-001..010
  - CR-FED-019..030
  - CR-FEDGOV-001..024
  - CR-ARCH-021..024
  - CR-SEC-001..006
  - CR-METRIC-016..020
```

## Контекст

Stage 5 впервые соединяет несколько независимых presence в одну сеть. Каждый
participant сохраняет ownership, policy, trust boundary и локальную автономию,
но должен обмениваться достаточными metadata для каталога, placement, support,
usage, settlement, certification, suspension, disputes и cross-provider
operations.

Федерация не может предполагать постоянную связь, полный доступ к внутренней
инфраструктуре участника или единый trusted operator для всех решений. При
этом пользователь должен видеть сеть как цельный продукт: предложения,
ограничения, price/trust/compliance, usage, support and recovery должны быть
понятны без ручной интеграции между участниками.

## Решение

CloudRING использует federation sync model:

- federation exchange состоит из domain events, periodic snapshots and signed
  metadata documents;
- каждый event имеет identity, issuer, subject, purpose, scope, version,
  idempotency key, causation/correlation id, timestamp, policy result and audit
  reference;
- participant делится только metadata, нужными для заявленной цели: catalog,
  placement, usage, settlement, support, audit, trust or dispute;
- catalog, certification, trust, usage, support and settlement streams могут
  иметь разные freshness, visibility and retention rules;
- disconnected participant may queue events and publish delayed sync after
  reconnect;
- stale offers, delayed usage, pending support states and outdated trust
  metadata must be visible as freshness/degraded states, not silently treated
  as current;
- replay and duplicate delivery must be safe;
- conflict handling must make local committed state, remote accepted state and
  disputed state visible, including accepted/rejected event outcomes;
- sensitive operational data must be summarized, redacted or purpose-scoped
  before federation exchange;
- governance can suspend participant, presence, offer, capability or service
  version without deleting customer data.

## Почему

CloudRING должен быть cloud-of-clouds, а не централизованным провайдером под
новым именем. Federation sync дает участникам возможность сотрудничать без
слияния control planes и без раскрытия всей внутренней инфраструктуры.

## Последствия

Положительные:

- участники могут подключаться к сети без полного доверия друг к другу;
- private/edge presence сохраняют автономию при временной потере связи;
- usage/settlement/support disputes имеют evidence;
- AI-агенты могут анализировать события и конфликты через единый контракт.

Отрицательные:

- требуется строгая модель событий, версий и конфликтов;
- пользовательский опыт должен объяснять local, remote, synced and disputed
  states;
- не все metadata можно синхронизировать мгновенно или полностью.

Follow-up:

- определить minimal Stage 5 event families;
- описать freshness/retention classes для catalog, usage, support and trust;
- связать federation sync с cross-provider operation contract;
- подготовить Stage 6 global network discovery and scale requirements.

## Критерии Приемки

- Два независимых presence могут обменяться catalog, trust/certification and
  usage metadata без ручной интеграции.
- Event replay не создает двойной catalog entry, usage charge or settlement
  share.
- Disconnected presence can reconnect and sync delayed events with visible
  gaps, conflicts and audit evidence.
- Stale catalog/trust/support/usage data is marked with freshness state before
  buyer/admin/agent decisions.
- Пользователь/администратор видит, какие metadata переданы участникам и для
  какой purpose.
- Suspension or dispute state propagates without deleting customer data or
  blocking unrelated services.
