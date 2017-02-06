# Operations, Resilience And Observability

CloudRING должен быть управляемым одним человеком и AI-агентами, но при этом
достаточно зрелым для командной эксплуатации.

## Observability

| ID | Требование | Почему |
|---|---|---|
| CR-OPS-001 | Каждый сервис должен публиковать metrics endpoint в стандартизированном формате. | Платформа должна автоматически собирать состояние сервисов. |
| CR-OPS-002 | Каждый сервис должен поддерживать structured logs с correlation fields. | Логи должны быть пригодны для поиска и автоматического анализа. |
| CR-OPS-003 | Сервисы должны поддерживать distributed tracing для сетевых и долгих операций. | Без трассировки сложно понять, где потеряна latency или ошибка. |
| CR-OPS-004 | Trace context должен передаваться через API, очереди и межсервисные вызовы. | Cross-service операции должны иметь единую картину. |
| CR-OPS-005 | Метрики должны различать успешные и ошибочные операции. | Это база для SLO и alerting. |
| CR-OPS-006 | Платформа не должна дублировать метрики, которые можно надежно вывести из других метрик. | Лишние временные ряды повышают стоимость мониторинга. |
| CR-OPS-007 | Ошибка должна логироваться на правильном уровне, без многократного дублирования одной ошибки. | Дубли создают шум и ложные инциденты. |
| CR-OPS-008 | Платформа должна иметь golden signals для ключевых сервисов. | Нужен минимальный универсальный health baseline. |
| CR-OPS-036 | Operational, lifecycle, audit, billing, federation and incident records must use canonical UTC timestamps. | Cross-presence correlation breaks when time semantics are local or ambiguous. |

## Operations For AI Agents

| ID | Требование | Почему |
|---|---|---|
| CR-OPS-009 | Операционные команды должны быть идемпотентными или явно описывать последствия повторного запуска. | AI-агенты будут повторять операции при сбоях. |
| CR-OPS-010 | Каждая automation должна иметь dry-run/plan режим там, где возможны изменения инфраструктуры. | Агентам и людям нужно видеть последствия до применения. |
| CR-OPS-011 | Платформа должна хранить планы, результаты и артефакты аудита в структурированном виде. | История stateful-проекта показала ценность планов и логов аудита. |
| CR-OPS-012 | Операционные runbooks должны быть machine-readable настолько, насколько это возможно. | AI-агенты должны исполнять и проверять runbooks. |
| CR-OPS-013 | Операции должны иметь таймауты, retries и понятные failure states. | Бесконечные операции неприемлемы для автономной эксплуатации. |
| CR-OPS-014 | Платформа должна явно различать read-only audit, planned change и destructive action. | Это снижает риск ошибочных автоматизаций. |

## Reliability And Backpressure

| ID | Требование | Почему |
|---|---|---|
| CR-OPS-015 | Ingestion/gateway сервисы должны иметь backpressure и bounded queues. | При перегрузке сервис должен деградировать управляемо. |
| CR-OPS-016 | Очереди должны иметь controlled flush, shutdown и recovery semantics. | Потеря usage events или lifecycle events недопустима. |
| CR-OPS-017 | Повторная отправка события должна быть безопасной через idempotency key или deterministic id. | Сети и клиенты будут повторять запросы. |
| CR-OPS-018 | Сервис должен возвращать понятный результат при повторе уже обработанного события. | Retry не должен считаться ошибкой пользователя. |
| CR-OPS-019 | Платформа должна поддерживать graceful shutdown для сервисов с буферами и очередями. | Иначе данные теряются при обновлениях и рестартах. |
| CR-OPS-020 | Платформа должна поддерживать versioned rollouts и rollback. | Обновления в federation/private/edge не происходят одновременно. |

## Stateful Services

| ID | Требование | Почему |
|---|---|---|
| CR-OPS-021 | CloudRING должен иметь первый класс требований для stateful-сервисов. | Базы, DNS, storage и queues являются ядром облака. |
| CR-OPS-022 | Stateful-сервис должен поддерживать backup, restore, replication, failover и upgrade. | Запуск без восстановления не является production capability. |
| CR-OPS-023 | Backup должен иметь проверяемые restore-тесты. | Непроверенный backup не является backup. |
| CR-OPS-024 | Архивирование журналов изменений/WAL/event log должно поддерживаться для критичных баз данных. | Point-in-time recovery важен для данных. |
| CR-OPS-025 | Stateful-сервисы должны иметь audit-процедуры: ресурсы, диск, ошибки, fatal logs, replication lag, backup status. | Операционные проблемы видны в регулярных аудитах. |
| CR-OPS-026 | DNS/service discovery должен проектироваться как отказоустойчивый сервис. | Облачная платформа зависит от имен и маршрутизации. |
| CR-OPS-027 | Платформа должна поддерживать maintenance users/roles отдельно от runtime users/roles. | Миграции и приложение не должны иметь одинаковые права. |
| CR-OPS-028 | Database guidelines должны быть частью платформенной практики. | Единые правила схем, миграций и прав снижают production-риск. |
| CR-OPS-037 | Database practice must separate schemas, extensions, migration tracking, runtime roles and maintenance roles. | Stateful services need drift visibility and least privilege, not hidden operational coupling. |

## ADR And Change History

| ID | Требование | Почему |
|---|---|---|
| CR-OPS-029 | Значимые архитектурные решения должны фиксироваться в ADR. | Будущие агенты должны понимать не только что сделано, но и почему. |
| CR-OPS-030 | ADR должен иметь статус: proposed, accepted, superseded, deprecated. | История прототипа содержит решения, которые были заменены более зрелыми. |
| CR-OPS-031 | При изменении решения нужно ссылаться на superseded/superseding ADR. | Иначе теряется причинная цепочка. |
| CR-OPS-032 | Requirements должны ссылаться на source signals, но не копировать исходники. | Это сохраняет трассируемость без copyright-риска. |
| CR-OPS-033 | Gateway/ingestion evidence must include negative scenarios. | Очереди и ingestion ломаются не только на happy path. |
| CR-OPS-034 | Backpressure and queue recovery must be measured through explicit failure modes. | Silent accept/drop недопустим для billable and lifecycle events. |
| CR-OPS-035 | Operational churn must update docs/runbooks or record no-change rationale. | Повторные fixes без обновления operational memory создают toil. |
| CR-OPS-038 | Stateful topology must declare node classes, quorum and failure domains. | HA не доказывается количеством узлов; важно, какие узлы могут принимать запись, promoted, read-only, DR или manual-review. |
| CR-OPS-039 | Stateful failover must define write endpoint semantics and client impact. | Failover без понятного write path создает split-brain, stale writes and confusing recovery. |
| CR-OPS-040 | Stateful services must publish RPO/RTO and replication mode as product promises. | Async/sync replication, lag and acceptable data loss are user-facing risk. |
| CR-OPS-041 | Continuous backup must prove archive continuity, retention and freshness. | WAL/event archive без проверки непрерывности может не восстановить данные. |
| CR-OPS-042 | Restore/PITR drill evidence is mandatory for stateful readiness. | Backup job success is not recoverability. |
| CR-OPS-043 | Stateful audit runs must produce blocking pass/fail evidence. | Audit that ignores stale backup, failed replication, malformed artifact or unreachable target gives false confidence. |
| CR-OPS-044 | Stateful access roles must have lifecycle, owner, review and rotation. | Runtime, owner, admin, replication, rewind and monitoring roles carry different blast radius. |
| CR-OPS-045 | Stateful runbooks must declare reproducible dependency manifests. | Branch-only roles, manual refresh and missing dependency identity make operations impossible to replay safely. |
| CR-OPS-046 | Operational source artifacts must be redacted before entering requirements or agent context. | Logs, topology, IaC state, grants and encrypted material are useful evidence but unsafe memory. |
