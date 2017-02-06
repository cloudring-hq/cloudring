# Marketplace Journeys

Marketplace CloudRING должен работать как app store для cloud-сервисов:
найти, понять, установить, оплатить, обновить, поддержать, удалить и перенести.

Он не должен быть статическим каталогом ссылок.

## Buyer Journey

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-001 | Buyer должен искать сервисы по задаче, capability, provider, region, jurisdiction, price, SLA, compliance и compatibility. | Покупатель выбирает результат и ограничения, а не внутреннюю технологию. |
| CR-MKT-002 | Карточка сервиса должна показывать trust score, certification level, support terms, export story, dependencies и known limitations. | Покупатель должен понимать риск до установки. |
| CR-MKT-003 | Marketplace должен показывать альтернативы и compatible substitutes. | Это прямой механизм против lock-in. |
| CR-MKT-004 | Перед установкой buyer должен видеть install plan: resources, price, provider chain, data location и policy decisions. | Установка сервиса - финансовое и compliance действие. |
| CR-MKT-005 | После установки marketplace должен показывать instance state, usage, docs, support и available actions. | Marketplace отвечает за lifecycle, а не только за продажу. |

## Seller / ISV Journey

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-006 | Seller должен публиковать сервис через submission workflow с conformance report. | Публикация должна быть масштабируемой и прозрачной. |
| CR-MKT-007 | Seller должен задавать plans, pricing model, support model, compatibility profiles и license/update policy. | Сервис продается как продукт. |
| CR-MKT-008 | Seller должен видеть failed checks с actionable remediation. | Certification не должна быть черным ящиком. |
| CR-MKT-009 | Seller должен получать feedback: installs, usage, revenue, churn, incidents, reviews. | Улучшение сервиса требует данных. |
| CR-MKT-010 | Seller должен поддерживать deprecation и migration path для старых версий. | Marketplace не должен бросать пользователей старых версий. |

## Install / Update / Remove

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-011 | Install должен быть policy-aware и идемпотентным. | Повтор установки или сбой сети не должны создавать хаос. |
| CR-MKT-012 | Update должен показывать changelog, impact, downtime, compatibility and rollback plan. | Обновления cloud-сервисов рискованны. |
| CR-MKT-013 | Remove должен показывать data retention, export options, billing stop time и irreversible effects. | Удаление не должно становиться скрытым lock-in. |
| CR-MKT-014 | Marketplace должен поддерживать staged rollout для обновлений. | Массовое обновление без контроля опасно. |
| CR-MKT-015 | Marketplace должен поддерживать pinning версии сервиса там, где это допустимо. | Enterprise/private клиенты не всегда могут обновляться сразу. |

## Reviews, Trust And Quality

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-016 | Marketplace должен поддерживать verified reviews от реальных пользователей/администраторов. | Trust score должен учитывать опыт использования. |
| CR-MKT-017 | Reviews должны быть отделены от support incidents и SLA metrics, но связаны с ними. | Эмоциональный отзыв и операционное качество - разные сигналы. |
| CR-MKT-018 | Trust score должен учитывать certification, incident history, vulnerability response, docs completeness, support quality и portability. | Качество cloud-сервиса многомерно. |
| CR-MKT-019 | Сервис с критичным security или compatibility issue должен получать marketplace warning или suspension. | Пользователи должны быть защищены. |

## Refunds, Disputes And Support Handoff

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-020 | Marketplace должен поддерживать refund/credit request flow. | Billing disputes неизбежны. |
| CR-MKT-021 | Support request должен автоматически знать provider, ISV, reseller, service instance, plan, usage and incident context. | Пользователь не должен объяснять цепочку участников вручную. |
| CR-MKT-022 | Support handoff между CloudRING, provider и ISV должен иметь SLA and ownership state. | Иначе поддержка теряется между участниками. |
| CR-MKT-023 | Dispute должен сохранять evidence bundle: order, policy, usage, settlement, logs, support timeline. | Спор должен решаться фактами. |
| CR-MKT-024 | Refund/credit не должен нарушать settlement audit trail. | Деньги в federation требуют проверяемости. |

## Marketplace Anti-Lock-In Rules

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-025 | Marketplace должен маркировать сервисы без export/migration path. | Пользователь должен видеть lock-in риск до покупки. |
| CR-MKT-026 | Marketplace должен поощрять compatible alternatives и open contracts. | Экосистема должна конкурировать ценностью, а не удержанием. |
| CR-MKT-027 | Marketplace не должен скрывать provider-specific dependencies. | Lock-in часто появляется через незаметные зависимости. |
| CR-MKT-028 | Marketplace должен позволять пользователю фильтровать сервисы по portability/trust/compliance. | Выбор должен отражать стратегию клиента. |

## Artifact / Image Publication Journey

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-029 | Marketplace publication должен требовать actual built artifact immutable release identity, digest/equivalent identity and registration result. | Нельзя поддерживать и откатывать неизвестный artifact or mutable location. |
| CR-MKT-030 | Artifact/image/template должен иметь build provenance and integrity evidence. | Store trust строится на проверяемом происхождении. |
| CR-MKT-031 | Publication должен требовать hardening, pre/post cleanup and final credential-residue evidence. | Runtime artifact не должен нести build credentials, bootstrap access, debug state or unsafe defaults. |
| CR-MKT-032 | Artifact должен пройти boot/health/first-bootstrap validation before publication. | Установочный пакет без проверки запуска и первичной настройки не является продуктом. |
| CR-MKT-033 | Publication должен register final inventory handoff with artifact identity, registration response, support owner, known limits and rollback/deprecation target. | Marketplace, support and agent operations need exact artifacts, versions, docs and diagnostics. |
| CR-MKT-034 | Artifact deprecation and update story must be visible. | Пользователь должен понимать maintenance, rollback and migration future. |
| CR-MKT-035 | Publication diagnostics must be support-safe with profile state, approval, scope, redaction, retention and audit. | Troubleshooting package должен помогать support без утечки secrets/tenant/source context. |
| CR-MKT-036 | Artifact card must disclose portability limitations. | Пользователь должен видеть lock-in risk before install/order. |

## Support Chain State

| ID | Требование | Почему |
|---|---|---|
| CR-MKT-037 | Support case must have explicit lifecycle states. | Поддержка не должна теряться между участниками. |
| CR-MKT-038 | Support case must bind service instance, version, plan, entitlement and provider chain. | Пользователь не должен вручную восстанавливать context. |
| CR-MKT-039 | SLA clock and escalation owner must be explicit. | Cross-provider support needs accountability. |
| CR-MKT-040 | Credit/dispute handoff must preserve support evidence. | Commercial correction должна опираться на факты инцидента. |
