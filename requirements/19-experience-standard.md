# Experience Standard

CloudRING должен ощущаться простым, цельным и красивым, несмотря на сложность
federation, marketplace, billing, policy и инфраструктуры.

Красота здесь означает ясность, предсказуемость, отсутствие лишнего,
уважение к пользователю и видимость важных последствий до действия.

## Experience Principles

| ID | Требование | Почему |
|---|---|---|
| CR-UX-001 | Каждый основной flow должен начинаться с намерения пользователя, а не с внутренней сущности платформы. | Пользователь хочет "запустить сервис", а не "создать набор ресурсов". |
| CR-UX-002 | Сложные решения placement/federation должны показываться как понятный выбор с деталями по запросу. | Скрывать сложность нельзя, но нельзя и перекладывать ее всю на пользователя. |
| CR-UX-003 | Цена, jurisdiction, provider chain, SLA и trust profile должны быть видны до подтверждения заказа. | Это ключевые параметры выбора cloud-сервиса. |
| CR-UX-004 | Ошибка должна объяснять причину, влияние, следующий шаг and validation state. | Self-service ломается, если ошибка требует оператора. |
| CR-UX-005 | Любой irreversible/risky action должен иметь explicit confirmation и evidence. | Пользователь должен понимать последствия. |
| CR-UX-006 | UI, API и CLI должны использовать одинаковые термины и lifecycle states. | Иначе документация и агентские действия расходятся. |
| CR-UX-007 | Agent-readable output должен быть доступен рядом с human-readable output and include code/path/params/remediation where relevant. | Агент и человек должны работать с одной реальностью. |
| CR-UX-008 | Главный экран каждой роли должен показывать следующие полезные действия, health, risk and cost summary, а не внутреннюю карту всех подсистем. | Пользователь должен понимать, что делать сейчас, без чтения архитектуры. |
| CR-UX-009 | Сложный flow должен иметь progressive disclosure: summary, explanation, details and raw evidence. | Мощность платформы нужна без перегрузки пользователя. |
| CR-UX-010 | Recommendation должен иметь объяснение "почему", альтернативы и причины блокировок. | Рекомендация без объяснения становится скрытым lock-in. |
| CR-UX-011 | Defaults должны быть безопасными, обратимыми где возможно и честными по cost/policy/trust impact. | Хороший default помогает, но не должен прятать последствия. |
| CR-UX-012 | Resource page должен показывать owner, provider, region, jurisdiction, cost, SLA, dependencies, health and next actions. | Управление облаком требует контекста, а не списка разрозненных объектов. |
| CR-UX-013 | Empty, loading, validation, degraded and error states должны вести к self-service next step. | Нестандартное состояние не должно сразу требовать оператора. |
| CR-UX-014 | UI/API/CLI должны явно различать ready, provisioning, degraded, blocked, stale, disputed and retired states. | Federation создает состояния, которые нельзя смешивать без потери доверия. |
| CR-UX-015 | AI-generated action plan должен быть human-readable and show risk, scope, approval, rollback and validation. | Человек остается владельцем смысла и риска. |
| CR-UX-016 | Перед покупкой или изменением пользователь видит price, lock-in impact, data movement, support owner and exit path. | Self-service должен помогать принимать informed decision. |
| CR-UX-017 | Красота продукта должна измеряться ясностью, предсказуемостью и отсутствием лишнего, а не декоративностью. | Cloud management должен быть спокойным рабочим инструментом. |
| CR-UX-018 | Поддерживаемый standard flow должен завершаться без обращения в support. | Иначе self-service существует только на словах. |
| CR-UX-019 | Если flow не может завершиться self-service, он должен создать support-ready evidence bundle. | Поддержка должна начинаться с контекста, а не с повторного сбора фактов. |
| CR-UX-020 | Experience conformance должен проверяться task-based сценариями для пользователя, администратора, developer, provider, ISV, support, governance and agent, включая validation correction, embedded UI, support handoff and policy/trust flows. | Простота проверяется выполнением работы, а не статическим экраном. |
| CR-UX-021 | Service UI extensions должны сохранять общую навигацию, permissions, terminology, visual system, lifecycle states, theme containment and evidence rules. | App-store расширяемость не должна превращать CloudRING в набор несвязанных панелей. |

## Canonical Flow 1 - User Orders A Service

Цель: пользователь выбирает и запускает сервис.

Acceptance:

1. Пользователь находит сервис через search/filter по capability, price,
   provider, region, jurisdiction и trust profile.
2. Карточка сервиса показывает compatibility, dependencies, support, export
   story, data handling и estimated price.
3. Перед заказом пользователь видит placement proposal и policy decisions.
4. После подтверждения пользователь видит provisioning timeline.
5. После готовности пользователь получает endpoint/credentials через безопасный
   механизм, docs, monitoring и billing preview.
6. Весь flow доступен через UI/API/CLI/agent API.

## Canonical Flow 2 - Admin Installs Private Cloud

Цель: администратор запускает private CloudRING.

Acceptance:

1. Installer проверяет ресурсы, network, storage и prerequisites.
2. Admin выбирает профиль: single-host, multi-node, connected, disconnected.
3. Платформа объясняет, какие capability будут доступны.
4. Установка создает initial admin, policy baseline, audit и update channel.
5. После установки admin видит health, capacity, alerts, next recommended steps.
6. Ошибки установки имеют remediation и safe retry.

## Canonical Flow 3 - ISV Publishes A Service

Цель: разработчик публикует сервис в marketplace.

Acceptance:

1. ISV создает service skeleton или подключает existing service через connector.
2. Manifest проходит validation.
3. Conformance checks показывают missing lifecycle, usage, docs, security,
   compatibility и UI requirements.
4. ISV задает plans, supported profiles, support terms и pricing.
5. Certification result объясняет, какие marketplace levels доступны.
6. После публикации ISV видит installs, usage, revenue, incidents и feedback.

## Canonical Flow 4 - Provider Joins Federation

Цель: новый провайдер подключает presence к сети.

Acceptance:

1. Provider создает participant identity.
2. Presence проходит technical and trust onboarding.
3. Provider публикует capability, regions, capacity, pricing inputs и support.
4. Conformance определяет уровень участия.
5. Catalog sync делает предложения видимыми допустимым пользователям.
6. Provider видит settlement, incidents и quality score.

## Canonical Flow 5 - User Migrates Or Exports

Цель: пользователь снижает lock-in на практике.

Acceptance:

1. Пользователь видит portability score и ограничения сервиса.
2. Платформа предлагает export или migration targets.
3. Policy engine проверяет jurisdiction/data/security.
4. Migration/export plan показывает downtime, cost, data scope и rollback.
5. После выполнения пользователь получает validation report.
6. Billing прекращается или меняется предсказуемо.

## Canonical Flow 6 - Agent Remediates Incident

Цель: AI-агент помогает восстановить сервис.

Acceptance:

1. Агент получает incident context, telemetry, runbook и permissions.
2. Агент классифицирует risk class.
3. Агент строит plan и dry-run, если нужно.
4. Агент выполняет только разрешенные шаги.
5. Агент валидирует outcome.
6. Агент записывает summary, evidence и follow-up requirements/ADR.

## Canonical Flow 7 - Buyer Evaluates Trust

Цель: пользователь понимает, кому доверяет.

Acceptance:

1. Сервис показывает provider, ISV, reseller, data locations и sub-processors.
2. Trust profile показывает certification, audit, incidents, vulnerabilities и
   support quality.
3. Пользователь может сравнить альтернативных provider/region.
4. Policy conflicts объясняются до покупки.
5. Доверительная информация доступна через API для agent evaluation.
