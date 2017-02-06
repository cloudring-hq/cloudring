# ADR-0013 - Local Entitlement And Offline Licensing

```yaml
id: ADR-0013
status: proposed
title: Local Entitlement And Offline Licensing
context: Stage 3 должен позволять private cloud устанавливать готовые сервисы, лицензировать дополнительные возможности и получать updates/support, не превращая лицензию в выключатель базовой работоспособности.
decision: CloudRING разделяет runtime entitlement, update entitlement, support entitlement и commercial settlement; private presence хранит локально проверяемое entitlement state с offline grace/degraded semantics.
supersedes: []
requirements:
  - CR-FED-014..018
  - CR-FED-030
  - CR-MKT-004..015
  - CR-SELF-017..020
  - CR-STAGE2-020..023
```

## Контекст

Private cloud владелец должен иметь возможность устанавливать готовые сервисы
как из app store, лицензировать дополнительные возможности, получать updates и
support. Но CloudRING не должен строить коммерческую модель на мгновенном
отключении уже установленной private-инфраструктуры. Иначе платформа создаст
новый lock-in: зависимость от внешней лицензии как от рубильника.

Stage 3 еще не является глобальным settlement или public provider commerce.
Нужна локальная entitlement model, которая работает в connected и offline
режимах, показывает права честно и готовит данные для будущей federation.

## Решение

CloudRING разделяет несколько типов entitlement:

- runtime entitlement: право продолжать базовое выполнение установленного
  сервиса в пределах локальной policy;
- update entitlement: право получать новые версии, security fixes,
  compatibility updates или feature updates;
- support entitlement: право получать поддержку, SLA, incident handoff и
  vendor/ISV assistance;
- feature entitlement: право использовать дополнительные возможности сервиса;
- publication entitlement: право публиковать сервис дальше в private store,
  provider offering или federation;
- settlement entitlement: будущий коммерческий расчет между участниками,
  который не должен быть обязательным для локальной private установки Stage 3.

Private presence должна иметь локально проверяемое entitlement state:

- источник entitlement;
- service/product identity;
- owner/project scope;
- validity period или perpetual terms;
- offline grace/degraded rules;
- update eligibility;
- support coverage;
- suspension/conflict state;
- update/support implications;
- audit history;
- user-visible consequences.

## Почему

CloudRING должен поддерживать коммерческую экосистему, но не должен удерживать
клиента через потерю контроля над собственной инфраструктурой. Разделение
runtime/update/support/settlement делает модель честной: сервис может
продолжать работать, даже если updates/support/новые features ограничены.

## Последствия

Положительные:

- private cloud сохраняет базовую работоспособность;
- ISV и поставщики могут продавать updates/support/features;
- offline installations имеют предсказуемое поведение;
- будущий settlement получает чистые входные события.

Отрицательные:

- карточка сервиса должна объяснять несколько entitlement states;
- ISV должен явно определить consequences окончания entitlement;
- нужны audit и dispute evidence для entitlement changes.

Follow-up:

- описать user-visible entitlement states для Stage 3;
- связать entitlement с update plan/apply/validate;
- определить offline grace semantics для disconnected private presence;
- подготовить входные события для будущего ADR-0004 billing/settlement.

## Критерии Приемки

- Service store показывает runtime/update/support/feature entitlement отдельно.
- Окончание update/support entitlement не отключает мгновенно уже установленную
  базовую работоспособность, если нет security/legal/policy причины.
- Offline private presence может показать current entitlement state и
  последствия отсутствия sync.
- Entitlement state явно различает active, grace, degraded, expired, suspended
  и conflict states.
- Install/update/remove flow показывает entitlement impact до действия.
- Entitlement changes создают audit events и пригодны для будущего settlement.
