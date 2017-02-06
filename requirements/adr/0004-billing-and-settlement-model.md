# ADR-0004 - Billing And Settlement Model

```yaml
id: ADR-0004
status: proposed
title: Billing And Settlement Model
context: CloudRING должен поддерживать коммерческие cloud-сервисы, usage billing, invoices, credits, disputes и будущий settlement между участниками без превращения денег в новый lock-in.
decision: Billing строится вокруг проверяемых usage records, product-scoped entitlements, invoices, credits/disputes и staged settlement model: provider-local на Stage 4, cross-participant на Stage 5+.
supersedes: []
requirements:
  - CR-FED-019..030
  - CR-MKT-020..024
  - CR-SELF-003
  - CR-SELF-015
  - CR-METRIC-018
  - CR-METRIC-027..028
```

## Контекст

CloudRING должен позволить независимому провайдеру продавать облачные услуги и
позже участвовать в federation economy. Billing является доверительным ядром:
если usage, invoices, credits и disputes непроверяемы, пользователь не будет
доверять платформе, а провайдеры и ISV не смогут строить бизнес.

Billing также не должен становиться механизмом удержания. Пользователь должен
видеть, за что платит, когда начисление остановлено, как экспортировать данные,
как оспорить начисление и какие участники вовлечены.

## Решение

CloudRING использует staged billing model:

- базовые коммерческие сущности: order, subscription, entitlement, usage
  record, invoice, credit/refund, dispute, settlement share;
- Stage 4: provider-local billing для одного публичного provider presence,
  его tenants, services, plans, usage records, invoices, credits и support
  disputes, включая provider-local ISV/reseller share без обязательной
  federation sync;
- Stage 5+: cross-participant settlement между несколькими provider/private/ISV
  участниками federation как отдельный режим той же модели, а не скрытое
  требование Stage 4;
- usage record является первичным доказательством начисления и имеет product,
  resource, instance, unit, amount, period, identity, idempotency key, policy
  context и audit trail;
- service не может отправлять usage за продукт/ресурс вне своего scope;
- usage без product/resource authorization, period, unit или idempotency key
  отклоняется и аудитится;
- invoice должен быть объясним пользователю: service, plan, period, quantity,
  price, credits, taxes/fees profile, provider and support context;
- credit/refund/dispute не должен уничтожать audit trail;
- dispute содержит evidence bundle: order, policy decision, usage records,
  support timeline and correction history;
- billing stop semantics должны быть видны до remove, suspend, export или plan
  change;
- pricing, tax, legal invoice format и payment processing являются
  jurisdiction-specific extension points, но core contract должен сохранять
  auditability, transparency и portability.

## Почему

Экономика CloudRING должна конкурировать ценностью, а не непрозрачностью.
Проверяемый billing снижает споры, делает provider kit жизнеспособным и
готовит основу для federation settlement без преждевременного усложнения
Stage 4.

## Последствия

Положительные:

- провайдер может продавать услуги на Stage 4 без полной federation;
- пользователь получает понятную детализацию счета;
- будущий settlement получает чистые usage/invoice/evidence события;
- disputes решаются фактами, а не ручной перепиской.

Отрицательные:

- каждый коммерческий сервис должен заранее описать usage metrics;
- billing pipeline становится критичной частью trust model;
- локальный provider billing и будущий federation settlement должны быть
  разделены, но совместимы.

Follow-up:

- определить `stage4-provider-billing-ready` conformance checks;
- описать invoice/credit/dispute evidence bundle;
- связать billing stop semantics с remove/export flows;
- вынести cross-participant settlement details в Stage 5 ADR/federation spec.

## Критерии Приемки

- Usage record идемпотентен, scoped и имеет audit trail.
- Пользователь видит usage, invoice, credits, billing stop time и dispute path.
- Provider видит revenue, unpaid/failed billing states, disputes и correction
  history.
- Commercial service не публикуется без declared usage metrics или явного
  non-metered plan.
- Stage 4 может выставить provider-local invoice без multi-provider settlement.
- Stage 4 может учитывать provider-local ISV/reseller share без federation
  settlement.
- Stage 5 может использовать Stage 4 usage/invoice evidence как вход для
  cross-participant settlement.
