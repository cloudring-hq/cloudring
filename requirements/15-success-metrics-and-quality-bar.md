# Success Metrics And Quality Bar

CloudRING должен оцениваться не количеством реализованных технологий, а тем,
насколько он снижает зависимость, упрощает доступ к cloud-технологиям и
позволяет участникам создавать ценность.

## North Star

Главная метрика:

> Пользователь может выбрать, запустить, оплатить, наблюдать, перенести или
> остановить cloud-сервис через единый self-service контракт без зависимости от
> одного провайдера, одной технологии и одной юрисдикции.

## Lock-In Metrics

| ID | Метрика | Целевой Смысл |
|---|---|---|
| CR-METRIC-001 | Service portability score | Доля сервисов, которые можно перенести между presence без ручного проекта миграции. |
| CR-METRIC-002 | Data export completeness | Доля сервисных данных и metadata, доступных для экспорта через стандартный контракт. |
| CR-METRIC-003 | Alternative provider availability | Сколько совместимых провайдеров/regions может принять сервис. |
| CR-METRIC-004 | Time to leave | Сколько времени требуется пользователю, чтобы прекратить использование сервиса и забрать данные. |
| CR-METRIC-005 | Contract dependency ratio | Какая часть интеграций идет через Open Cloud Standard, а не через proprietary API. |

## Self-Service Metrics

| ID | Метрика | Целевой Смысл |
|---|---|---|
| CR-METRIC-006 | Time to first service | Время от установки/регистрации до первого работающего сервиса. |
| CR-METRIC-007 | Self-service completion rate | Доля операций, выполненных без ручной поддержки. |
| CR-METRIC-008 | Guided remediation success | Доля типовых проблем, решенных пользователем/админом/агентом через подсказанный flow. |
| CR-METRIC-009 | Admin toil hours | Сколько ручных часов нужно на поддержку базовой инсталляции. |
| CR-METRIC-010 | Agent-operable runbook ratio | Доля runbooks, которые агент может безопасно выполнить или проверить. |

## Marketplace Metrics

| ID | Метрика | Целевой Смысл |
|---|---|---|
| CR-METRIC-011 | Service publication lead time | Время от submitted service до marketplace candidate. |
| CR-METRIC-012 | Certification pass rate | Доля сервисов, проходящих conformance/security checks без ручных исключений. |
| CR-METRIC-013 | Active ISV/provider services | Количество реально используемых сервисов от независимых участников. |
| CR-METRIC-014 | Cross-licensing revenue share | Доля выручки, проходящая через federation между участниками. |
| CR-METRIC-015 | Marketplace trust score | Композитный показатель качества: incidents, vulnerabilities, docs, SLA, user feedback. |

## Federation Metrics

| ID | Метрика | Целевой Смысл |
|---|---|---|
| CR-METRIC-016 | Federation participant count by type | Здоровье сети по public/private/edge/ISV/reseller ролям. |
| CR-METRIC-017 | Catalog sync freshness | Насколько актуальны предложения между участниками. |
| CR-METRIC-018 | Settlement accuracy | Доля settlement без dispute/correction. |
| CR-METRIC-019 | Cross-provider operation success | Успешность DR/backup/replication/migration между presence. |
| CR-METRIC-020 | Disconnected recovery time | Время восстановления синхронизации после offline периода. |

## Developer Experience Metrics

| ID | Метрика | Целевой Смысл |
|---|---|---|
| CR-METRIC-021 | Time to create service | Время от пустого каталога до service skeleton with docs/metrics/tasks. |
| CR-METRIC-022 | Local debug success rate | Доля сервисов, которые запускают зависимости и debug flow без ручных правок. |
| CR-METRIC-023 | Task portability score | Доля задач, одинаково работающих local и CI. |
| CR-METRIC-024 | Documentation completeness | Доля сервисов с overview/API/architecture/runbook/FAQ. |
| CR-METRIC-025 | Conformance feedback time | Время получения понятного отчета о несовместимости сервиса. |

## Security And Trust Metrics

| ID | Метрика | Целевой Смысл |
|---|---|---|
| CR-METRIC-026 | Secrets exposure incidents | Должно стремиться к нулю; секреты не должны попадать в docs/repo/artifacts. |
| CR-METRIC-027 | Policy decision coverage | Доля placement/lifecycle/billing действий с сохраненным policy decision. |
| CR-METRIC-028 | Audit completeness | Доля критичных действий с полным audit trail. |
| CR-METRIC-029 | Supply chain verification coverage | Доля артефактов с provenance, version, integrity check. |
| CR-METRIC-030 | Security remediation lead time | Время от finding до исправления/mitigation. |

## Evolution Metrics

| ID | Метрика | Почему |
|---|---|---|
| CR-METRIC-031 | Signal-to-learning conversion time | Сколько времени проходит от significant signal до requirement/ADR/runbook/conformance outcome. |
| CR-METRIC-032 | ADR closure and review rate | Насколько быстро архитектурные вопросы превращаются в явные решения или пересмотры. |
| CR-METRIC-033 | Conformance drift age | Сколько времени accepted requirement остается без validation path или со stale check. |
| CR-METRIC-034 | Technology refresh lead time | Сколько времени занимает безопасная замена устаревшей технологии без нарушения product contract. |
| CR-METRIC-035 | Repeated incident reduction | Снижается ли частота повторных инцидентов после learning follow-up. |
| CR-METRIC-036 | Agent proposal defect rate | Доля agent-generated proposals, отклоненных из-за missing scope, risk, evidence, validation, approval or anonymization. |
| CR-METRIC-037 | Repeated-fix conversion rate | Доля повторяющихся fix/theme clusters, которые стали requirement, ADR, runbook, conformance check, regression test or explicit no-change decision. |
| CR-METRIC-038 | Regression-after-fix coverage | Доля повторных failure modes, закрытых negative validation/conformance evidence, parity/bounded-runtime fixture or documented no-test rationale. |
| CR-METRIC-039 | Release and source-history evidence coverage | Доля readiness claims with release evidence plus source/history manifest with ref/tag/deleted-path/source-safety coverage. |
| CR-METRIC-040 | Restore/PITR drill freshness | Сколько критичных stateful capabilities have current restore/PITR evidence within declared freshness window. |
| CR-METRIC-041 | Failover drill freshness | Сколько HA/stateful capabilities have current failover drill evidence with endpoint ownership, RPO/RTO and split-brain prevention result. |
| CR-METRIC-042 | Stateful audit blocker rate | Доля stateful readiness audits that produce blocking findings, waived findings or unresolved evidence gaps. |
| CR-METRIC-043 | Source-safe evidence coverage | Доля operational evidence bundles classified/redacted before they enter requirements, conformance reports, agent context or marketplace/provider artifacts. |

## Product Design Quality Metrics

| ID | Metric | Meaning |
|---|---|---|
| CR-METRIC-044 | Task-intent completion rate | Доля ключевых flows, где роль завершает задачу из намерения, а не из знания внутренних сущностей. |
| CR-METRIC-045 | Consequence visibility before action | Доля high-impact actions, где cost, provider chain, jurisdiction, policy, trust, support and exit видны до подтверждения. |
| CR-METRIC-046 | Alternative explanation coverage | Доля рекомендаций/defaults, где видны альтернативы и объяснение why/why-not. |
| CR-METRIC-047 | Support-ready failure coverage | Доля failed/degraded/blocked flows, которые создают понятное объяснение, next action and evidence bundle. |
| CR-METRIC-048 | Jurisdiction and economics disclosure coverage | Доля marketplace/global decisions, где jurisdiction overlay and buyer/provider economic impact visible before order/change. |
| CR-METRIC-049 | Design regression learning rate | Доля повторяющихся UX/support confusion signals, превращенных в requirement, scenario, conformance check, runbook or explicit no-change decision. |
| CR-METRIC-050 | Human-agent parity coverage | Доля ключевых decisions, где UI/API/CLI/Agent API expose the same state, consequence, remediation and approval boundary. |

## Product Quality Bar

Capability можно считать готовой, если:

1. У нее есть requirement с why и acceptance criteria.
2. У нее есть domain owner/context.
3. Она доступна через UI/API/CLI или явно имеет причину исключения.
4. Она имеет observability: metrics, logs, traces или audit events.
5. Она имеет security model.
6. Она имеет failure states и remediation.
7. Она не привязана без необходимости к одному провайдеру или runtime.
8. Она документирована для человека и AI-агента.
9. Она имеет upgrade/compatibility story.
10. Она не добавляет lock-in, если цель capability - его снижать.

## Simplicity Quality Bar

Пользовательский поток считается простым, если:

1. Следующее действие очевидно без чтения внешней инструкции.
2. Риск и стоимость видны до подтверждения.
3. Ошибка объясняет причину и предлагает следующий шаг.
4. Сложность federation скрыта, но не замаскирована: детали доступны по запросу.
5. Поток можно выполнить повторно без неожиданных побочных эффектов.
6. Тот же поток можно выполнить через agent API.
7. Документация объясняет концепцию, а не только перечисляет команды.

## Продуктовый Анти-Критерий

Если новая capability:

- увеличивает зависимость от одного поставщика;
- требует ручной поддержки там, где возможен self-service;
- скрывает billing или placement;
- не имеет audit;
- не имеет понятного отказа;
- не может быть объяснена AI-агенту;
- ломает private/edge/local сценарии без причины;

то она не соответствует миссии CloudRING, даже если технически работает.
