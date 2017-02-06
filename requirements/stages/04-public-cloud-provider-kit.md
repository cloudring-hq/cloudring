# Stage 4 - Public Cloud Provider Kit

```yaml
id: STAGE-004
status: draft
title: Public Cloud Provider Kit
goal: Дать независимому оператору законченный продукт для запуска публичной CloudRING provider presence, продажи сервисов tenants и проверяемого provider-local billing/support.
primary_users:
  - public cloud provider operator
  - provider administrator
  - tenant administrator
  - service buyer
  - support operator
  - billing operator
  - AI operations agent
related_adr:
  - ADR-0004
  - ADR-0007
  - ADR-0009
  - ADR-0011
  - ADR-0013
  - ADR-0014
related_requirements:
  - CR-FED-003
  - CR-FED-014..030
  - CR-FEDGOV-001..004
  - CR-MKT-001..024
  - CR-SELF-001..006
  - CR-SELF-013..016
  - CR-METRIC-007
  - CR-METRIC-011
  - CR-METRIC-018
  - CR-METRIC-027..029
```

## Назначение

Stage 4 превращает CloudRING в набор для запуска публичного облачного
провайдера. Это первая стадия, где появляется внешний tenant, публичные offers,
plans/pricing, provider-local usage billing, invoices, SLA/support и provider
operations portal.

Stage 4 не является полной federation network: один provider может работать и
продавать услуги самостоятельно. Cross-provider catalog sync, settlement,
DR/migration между независимыми participants и multi-provider governance
остаются Stage 5.

## Product Promise

Provider проходит onboarding, публикует public presence, задает regions,
services, plans, pricing, SLA/support и policy constraints. Tenant находит
сервис, видит цену, регион, jurisdiction, trust/compliance, заказывает service
instance, наблюдает usage/cost/state, получает invoice и support path. Provider
видит capacity, incidents, revenue, support load, usage quality and policy
violations. Все критичные действия имеют audit, risk class и validation.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-STAGE4-001 | Stage 4 должен быть законченным public provider kit для одного provider presence. | Провайдер должен продавать услуги до federation network. | Provider может пройти readiness, опубликовать offer, принять tenant order, собрать usage и выставить provider-local invoice. |
| CR-STAGE4-002 | Provider onboarding должен следовать `ADR-0014`. | Публичная услуга требует identity, capacity, SLA, billing and support evidence. | Onboarding report показывает identity, lifecycle status candidate/active/blocked, presence profile, regions, services, billing readiness, support readiness and blockers. |
| CR-STAGE4-003 | Provider presence должен публиковать regions/locations, jurisdiction, capacity, capability, SLA/SLO and maintenance windows. | Buyer выбирает не только сервис, но и контекст риска. | Service card/order plan показывает эти attributes до заказа. |
| CR-STAGE4-004 | Public offers должны иметь plans, pricing, quotas, entitlement and support terms. | Публичная услуга должна быть покупаемым продуктом. | Tenant видит plan comparison, price basis, limits, support and change consequences до order. |
| CR-STAGE4-005 | Public offer должен иметь самостоятельный lifecycle и certification/public-ready state. | Provider может быть active, а конкретный offer blocked или limited. | Offer без public-ready certification публикуется только как beta/limited с warning and policy gate; offer state виден отдельно от provider state. |
| CR-STAGE4-006 | Tenant management должен быть first-class. | Public provider обслуживает внешних клиентов, а не только локальных администраторов. | Tenant имеет account/project/resource scopes, roles, budgets, policies and support context. |
| CR-STAGE4-007 | Tenant order flow должен быть policy-aware, price-aware and idempotent. | Ошибки заказа создают финансовый и compliance риск. | Повтор order не создает двойной service instance; plan показывает price, resources, data location, provider responsibility and policy decisions. |
| CR-STAGE4-008 | Provider-local billing должен следовать `ADR-0004`. | Непрозрачный счет разрушает доверие к cloud provider. | Orders, subscriptions, entitlements, usage records, invoices, credits/refunds and disputes имеют audit and user-visible explanation. |
| CR-STAGE4-009 | Commercial service должен объявить usage metrics или non-metered plan до публикации. | Billing не должен догадываться, за что начислять. | Publication gate блокирует offer без usage/pricing contract. |
| CR-STAGE4-010 | Usage gateway должен быть scoped, versioned, idempotent and backpressure-aware. | Usage pipeline является денежным и доверительным контуром. | Duplicate usage не создает двойное начисление; unauthorized usage rejected; overload returns controlled state. |
| CR-STAGE4-011 | Tenant должен видеть current usage, cost forecast, invoice history, credits and dispute path. | Пользователь должен контролировать стоимость. | Billing view показывает service, period, quantity, unit price, credits, provider context and billing stop semantics. |
| CR-STAGE4-012 | Provider operations portal должен показывать capacity, incidents, revenue, support, usage quality and policy violations. | Провайдер должен управлять услугой как бизнесом и операцией. | Provider dashboard имеет actionable views and exportable audit/evidence. |
| CR-STAGE4-013 | Support workflow должен знать provider, service, tenant, plan, SLA, usage and incident context. | Поддержка не должна начинаться с ручного сбора фактов. | Support request автоматически содержит evidence bundle and responsibility boundary. |
| CR-STAGE4-014 | SLA/SLO должны быть declared, observable and connected to incidents/credits. | SLA без измерения и последствий является обещанием без продукта. | Service instance показывает SLO state, incident timeline, credit eligibility and support status. |
| CR-STAGE4-015 | Provider должен иметь guided remediation and agent-operable runbooks. | Один человек с AI-агентами должен поддерживать provider presence. | Routine operations имеют runbook, risk class, validation and rollback/compensation. |
| CR-STAGE4-016 | Public provider security baseline должен включать tenant isolation, audit, supply chain and secret boundaries. | Публичный cloud повышает blast radius ошибок. | Public-ready gate проверяет isolation evidence, artifact verification, audit and secret handling. |
| CR-STAGE4-017 | Public offer должен показывать data residency and jurisdiction policy до заказа. | Jurisdiction lock нужно решать до provisioning. | Order отклоняется, если requested policy несовместима с provider/region/service. |
| CR-STAGE4-018 | Provider должен поддерживать scoped suspension states без уничтожения пользовательских данных. | Abuse, unpaid, security and compliance incidents требуют ограничения, но не потери контроля. | Suspension показывает reason, scope participant/presence/offer/capability/service version, allowed actions, export/recovery options and appeal/support path; unrelated services не блокируются. |
| CR-STAGE4-019 | Remove/cancel flow должен показывать export, billing stop time, retention and irreversible effects. | Отказ от сервиса не должен становиться скрытым lock-in. | Tenant принимает explicit decision по данным и видит final usage/invoice implications. |
| CR-STAGE4-020 | Provider offer должен быть federation-ready by design, но federation не обязательна. | Stage 4 должен готовить Stage 5 без преждевременного sync. | Catalog, usage, support and certification metadata имеют structure для future sync, но один provider работает автономно. |
| CR-STAGE4-021 | Public provider не должен требовать единого центрального CloudRING operator для повседневной работы. | Иначе CloudRING станет новым централизованным облаком. | Provider can operate local/public presence with local ownership, audit and provider-local billing. |
| CR-STAGE4-022 | Provider должен видеть quality metrics: self-service completion, usage accuracy, support load, incidents, revenue and policy coverage. | Провайдер должен улучшать услугу на основе данных. | Dashboard показывает CR-METRIC related provider view and trend. |
| CR-STAGE4-023 | AI-agent operations должны соблюдать approval matrix, особенно provider onboarding, billing rules, support, suspension, tenant and production changes. | Агент не должен быть невидимым суперпользователем публичного провайдера. | Agent task has risk_class, scope, expected impact, approval, validation, audit and rollback/compensation. |
| CR-STAGE4-024 | Stage 4 должен иметь conformance profile `stage4-public-provider-ready`. | Нужна объективная граница готовности. | Report показывает provider readiness, public offers, billing, support, SLA, operations and blockers. |
| CR-STAGE4-025 | Stage 4 не должен включать multi-provider settlement как обязательную функцию. | Cross-provider economy относится к Stage 5. | Provider-local invoice работает; cross-participant settlement marked future/federation-ready metadata. |
| CR-STAGE4-026 | Public provider kit должен поддерживать provider-owned services and certified external services. | Провайдеры должны развивать собственные услуги и подключать ISV. | Offer card показывает service owner, provider responsibility, support handoff and revenue/entitlement model. |

## Acceptance Scenarios

### Scenario A - Provider Onboarding

Цель: доказать, что независимый оператор может запустить public provider
presence.

Критерии:

- provider identity and ownership profile созданы;
- provider status candidate/active/blocked visible with blockers and evidence;
- presence profile публикует regions, capacity, jurisdiction, support and SLA;
- operations readiness показывает health, incidents, backup/recovery,
  security and support evidence;
- billing readiness показывает usage metrics, invoice profile and dispute flow;
- conformance report показывает `stage4-public-provider-ready` или blockers.

### Scenario B - Tenant Orders Public Service

Цель: доказать end-to-end self-service заказ публичной услуги.

Критерии:

- tenant выбирает service plan с price, SLA, region, jurisdiction and support
  terms;
- order plan проходит policy and budget checks;
- provisioning idempotent;
- tenant видит service instance, state, usage, cost forecast and support path.

### Scenario C - Usage To Invoice

Цель: доказать provider-local billing без multi-provider settlement.

Критерии:

- service publishes declared usage metric;
- usage record accepted once and duplicate ignored/linked;
- invoice объясняет service, period, quantity, unit, credits and provider;
- tenant может открыть dispute with evidence bundle;
- provider/ISV/reseller видят provider-local revenue/share and correction
  history, если share применяется без federation settlement.

### Scenario D - Incident, SLA And Credit

Цель: доказать связь operations и коммерческого обещания.

Критерии:

- incident has timeline, affected services, tenants and correlation IDs;
- SLO/SLA impact calculated or explicitly marked unknown with reason;
- credit eligibility visible to tenant/provider;
- support handoff has owner and status;
- post-incident follow-up can create requirement/ADR/runbook.

### Scenario E - Suspend Without Data Loss

Цель: доказать, что ограничение сервиса не уничтожает контроль клиента.

Критерии:

- suspension reason, scope and allowed actions visible;
- export/recovery actions remain available unless blocked by policy/security;
- billing stop/continue semantics visible;
- appeal/support path and audit trail preserved.

### Scenario F - Provider Agent Routine Operation

Цель: доказать, что provider kit поддерживается человеком с AI-агентами.

Критерии:

- агент читает requirements, ADR, provider telemetry and runbook;
- task has risk_class, expected impact, validation and rollback/compensation;
- billing, tenant, production and policy changes require approval;
- result saved as audit and human-readable summary.

## Agent Task Seeds

```yaml
id: TASK-STAGE4-001
goal: Описать conformance profile stage4-public-provider-ready.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/04-public-cloud-provider-kit.md
    - requirements/05-federation-marketplace-billing.md
    - requirements/17-acceptance-criteria.md
    - requirements/18-federation-governance.md
  exclude:
    - multi-provider settlement
    - federation event bus implementation
inputs:
  - CR-STAGE4-024
  - CR-FED-019..030
  - CR-SELF-013..016
expected_outputs:
  - readiness checks
  - provider evidence fields
  - blocking vs warning categories
permissions:
  secrets: none
  destructive_actions: false
validation:
  - every check maps to a requirement or ADR
rollback:
  - disputed checks become draft and link to ADR follow-up
```

```yaml
id: TASK-STAGE4-002
goal: Спроектировать provider-local usage-to-invoice product flow.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/04-public-cloud-provider-kit.md
    - requirements/adr/0004-billing-and-settlement-model.md
    - requirements/20-marketplace-journeys.md
  exclude:
    - payment processor integration
    - cross-provider settlement
inputs:
  - CR-STAGE4-008
  - CR-STAGE4-010
  - CR-STAGE4-011
expected_outputs:
  - user-visible billing states
  - usage evidence bundle
  - dispute and credit boundaries
permissions:
  secrets: none
  destructive_actions: false
validation:
  - flow covers usage, invoice, credit, dispute and billing stop semantics
rollback:
  - supersede via ADR if billing model changes
```

## Non-Goals

Stage 4 намеренно не является:

- multi-provider federation network;
- global marketplace across independent participants;
- cross-provider DR/migration;
- multi-party settlement;
- governance operator for the whole network;
- mandatory central SaaS control plane.

Stage 4 должен позволить одному provider presence быть полезным и коммерчески
работающим, сохраняя путь к Stage 5 federation.

## Readiness Gate

Stage 4 считается готовым, когда:

- provider onboarding работает как self-service readiness flow;
- provider offer публикует regions, services, plans, pricing, SLA/support and
  policy limitations;
- tenant order создает service instance through UI/API/CLI/Agent API;
- provider-local usage billing produces explainable invoice and dispute path;
- provider operations portal shows capacity, incidents, revenue, support,
  usage quality and policy violations;
- public-ready certification gates protect offers;
- support/SLA/credit flow has evidence and responsibility boundary;
- AI-agent routine operations follow approval matrix;
- conformance report shows `stage4-public-provider-ready` or concrete blockers.
