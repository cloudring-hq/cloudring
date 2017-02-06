# ADR-0014 - Provider Offer And Onboarding

```yaml
id: ADR-0014
status: proposed
title: Provider Offer And Onboarding
context: CloudRING должен позволить независимому оператору запустить публичную provider presence, опубликовать услуги и обслуживать tenants через единый контракт.
decision: Public provider onboarding описывается как product readiness flow: provider identity, presence profile, capacity, regions, pricing plans, SLA/support, compliance posture, billing readiness и operations evidence.
supersedes: []
requirements:
  - CR-SELF-013..016
  - CR-FED-003
  - CR-FED-014..018
  - CR-FED-019..030
  - CR-FEDGOV-001..004
  - CR-MKT-001..005
```

## Контекст

CloudRING должен дать возможность запускать облачного провайдера не только
крупным централизованным игрокам. Но публичная услуга отличается от private
presence: появляются external tenants, публичные plans/pricing, SLA/support,
billing, abuse/risk handling, jurisdiction promises и операционная
ответственность.

Stage 4 должен сделать одного provider presence жизнеспособным как публичный
cloud provider. Federation между несколькими providers остается следующим
слоем.

## Решение

Provider onboarding должен быть self-service readiness flow:

- provider identity and ownership profile;
- provider/presence/offer lifecycle states: draft, candidate, active, blocked,
  suspended, deprecated, retired, revoked;
- public presence profile: regions, zones/locations, jurisdiction, compliance
  posture, supported capability, capacity and availability attributes;
- offer catalog: services, plans, pricing model, quotas, trial/free options,
  support terms, SLA/SLO and maintenance windows;
- tenant onboarding: account, project/resource scope, policy, budget, access
  and support context;
- operations readiness: health, capacity, incident, change, backup/recovery,
  security and support evidence;
- billing readiness: usage metrics, invoice profile, credits/disputes,
  provider-local revenue view;
- publication gate: public-ready certification, supply chain verification,
  policy and trust metadata.

Provider onboarding and offer publication are separate gates: provider may be
active while a specific offer is blocked, and an offer may be public-ready
without being federation-ready.

Suspension scope must be explicit: participant, presence, offer, capability or
service version. Suspension must not destroy customer data or block unrelated
services.

Provider offer should be visible as a product contract, not as hidden
infrastructure detail.

## Почему

CloudRING сможет стать сетью облаков только если отдельный provider может
запуститься и продавать услуги самостоятельно. Provider onboarding превращает
операционную сложность в проверяемый self-service путь и не требует ручного
консалтинга на каждый запуск.

## Последствия

Положительные:

- независимый provider получает понятный путь запуска;
- пользователь видит price, SLA, region, jurisdiction and provider
  responsibility до заказа;
- Stage 4 создает доказуемую основу для Stage 5 federation;
- provider operations становятся agent-operable.

Отрицательные:

- provider readiness требует больше evidence, чем private store;
- public offer меняет риск-профиль: tenant isolation, billing and support
  становятся обязательными;
- ошибки в публичном offer сильнее влияют на trust score.

Follow-up:

- описать `stage4-public-provider-ready` conformance profile;
- связать provider offer с billing ADR-0004;
- определить support/SLA handoff для provider-local services;
- подготовить federation onboarding delta для Stage 5.

## Критерии Приемки

- Provider может пройти readiness flow без ручного изменения ядра платформы.
- Provider/presence/offer state has buyer/provider-visible consequences and
  remediation path.
- Provider offer показывает regions, price, SLA/SLO, support, jurisdiction,
  capacity, compatibility and policy limitations.
- Provider onboarding and service/offer publication are independently visible
  and auditable.
- Tenant может заказать сервис через UI/API/CLI/Agent API и получить service
  instance, usage visibility and support context.
- Public offer не публикуется без public-ready certification или explicit
  limited/beta status.
- Suspension scope is visible and does not destroy customer data or unrelated
  services.
- Provider operations portal показывает capacity, incidents, revenue, support,
  usage and policy violations.
