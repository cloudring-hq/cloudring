# Federation, Marketplace And Billing

CloudRING должен создавать экономику сервисов без превращения платформы в
централизованный замок.
Провайдеры, ISV, integrators, private cloud владельцы и edge-операторы должны
участвовать в общей сети через контракты, доверие, settlement и проверяемость.

## Федерация

| ID | Требование | Почему |
|---|---|---|
| CR-FED-001 | CloudRING должен поддерживать федерацию независимых провайдеров. | Это снижает зависимость от одного оператора и одной юрисдикции. |
| CR-FED-002 | Федерация должна работать через общий протокол синхронизации каталогов, условий, capability, availability и events. | Пользователь должен видеть сеть как единый рынок, а не набор кабинетов. |
| CR-FED-003 | Участник федерации должен иметь возможность быть public provider, private cloud, edge operator, ISV или reseller. | Экосистема не должна ограничиваться одним типом участника. |
| CR-FED-004 | Федерация должна поддерживать connected и partially disconnected режимы. | Edge и private-инсталляции не всегда имеют постоянную связь с центром. |
| CR-FED-005 | Пользователь должен выбирать сервис по требованиям: цена, локация, jurisdiction, latency, trust level, capability, SLA. | Пользователь покупает результат, а не имя провайдера. |
| CR-FED-006 | Платформа должна поддерживать cross-provider scenarios: DR, backup, replication, CDN, migration, burst capacity. | Реальная ценность федерации проявляется между провайдерами. |
| CR-FED-007 | Федерация должна поддерживать переносимость сервиса между presence, если сервисный контракт это допускает. | Это прямое средство против lock-in. |
| CR-FED-008 | CloudRING не должен требовать единого центрального доверенного оператора для всех действий. | Иначе federation станет централизованным cloud с новым именем. |
| CR-FED-009 | Федерация должна иметь governance: onboarding, certification, suspension, dispute handling, compatibility rules. | Открытая сеть без правил быстро теряет доверие. |
| CR-FED-010 | Federation events должны иметь audit trail и correlation IDs. | Cross-provider инциденты требуют расследования. |

## Marketplace

| ID | Требование | Почему |
|---|---|---|
| CR-FED-011 | CloudRING должен иметь marketplace/service store для инфраструктурных, platform, enterprise и ISV-сервисов. | Один поставщик не может развить все сервисы сам. |
| CR-FED-012 | Marketplace должен поддерживать публикацию сервиса через Open Cloud Standard и certification checks. | Каталог без совместимости не является платформой. |
| CR-FED-013 | Marketplace должен показывать совместимость сервиса с public/private/edge/disconnected режимами. | Клиенту важно знать, где сервис реально работает. |
| CR-FED-014 | Marketplace должен показывать условия: цена, SLA, support, jurisdiction, data handling, dependencies, license, maintenance. | Покупатель должен принимать informed decision. |
| CR-FED-015 | Marketplace должен поддерживать trial/dev/free сценарии для разработчиков и small users. | Adoption начинается с доступного входа. |
| CR-FED-016 | Marketplace должен поддерживать enterprise subscriptions, support contracts, maintenance and customizations. | Это коммерческая основа без lock-in. |
| CR-FED-017 | Marketplace должен поддерживать cross-licensing сервисов между провайдерами и ISV. | Провайдеры должны зарабатывать на сервисах друг друга. |
| CR-FED-018 | Marketplace должен поддерживать policy-based availability: сервис доступен только в допустимых регионах, средах и compliance-профилях. | Не все сервисы можно продавать везде. |

## Billing And Usage Metrics

| ID | Требование | Почему |
|---|---|---|
| CR-FED-019 | Каждый коммерческий сервис должен регистрировать измеримые ресурсы до приема usage. | Billing должен понимать, за что выставляется счет. |
| CR-FED-020 | Usage event должен содержать service/product identity, resource identity, instance/external id, unit, usage, period start/end и optional metadata. | Эти поля нужны для корректного учета потребления. |
| CR-FED-021 | Usage ingestion должен быть идемпотентным. | Повторная отправка не должна создавать двойное начисление. |
| CR-FED-022 | Usage ingestion должен иметь версии API и план миграции между ними. | Billing-контракты нельзя ломать одномоментно. |
| CR-FED-023 | Usage ingestion должен проверять права сервиса на отправку метрик конкретного продукта/ресурса. | Иначе один сервис сможет начислять потребление за другой. |
| CR-FED-024 | Access tokens/service credentials должны поддерживать scope по продуктам, ресурсам и средам. | Гранулярные права уменьшают blast radius. |
| CR-FED-025 | Токены доступа должны обновляться и отзыватьcя без перезапуска всей платформы. | Эксплуатация требует быстрой реакции на компрометацию. |
| CR-FED-026 | Billing pipeline должен поддерживать очереди, backpressure и ошибку "слишком много событий". | Ingestion не должен падать молча при перегрузке. |
| CR-FED-027 | Usage events должны трассироваться от API до очереди и settlement. | Споры по начислениям требуют доказуемости. |
| CR-FED-028 | Платформа должна поддерживать settlement между выбранным провайдером, фактическим исполнителем, ISV, reseller и CloudRING. | Федерация создает цепочки участников в одной покупке. |
| CR-FED-029 | Пользователь должен иметь единый счет/видимость, даже если сервис потреблялся у нескольких участников. | Удобство не должно теряться из-за federation complexity. |
| CR-FED-030 | После окончания лицензии базовая работоспособность private/edge-инсталляции не должна мгновенно отключаться; могут прекращаться updates, maintenance и support, кроме критичных исправлений совместимости. | Клиент не должен терять контроль над собственной инфраструктурой. |
| CR-FED-031 | Usage gateway должен иметь quarantine/replay path для failed usage. | Ошибка учета не должна становиться потерянным счетом или silent drop. |
| CR-FED-032 | Usage period and overlap policy должны быть part of billing contract. | Ambiguous periods create double billing and disputes. |
| CR-FED-033 | Backpressure должен быть visible to provider and affected customer context. | Перегрузка ingestion влияет на trust and invoice freshness. |
| CR-FED-034 | Billing attribution должен выводиться из offer/order/entitlement/provider/support context. | Hardcoded attribution ломает federation commerce and support chain. |
| CR-FED-035 | Usage diagnostics must be redacted and dispute-ready. | Billing investigation should preserve evidence without leaking credentials or tenant data. |
| CR-FED-036 | Offline entitlement behavior must be proven by simulation. | Private/edge promises must not depend on optimistic assumptions. |
