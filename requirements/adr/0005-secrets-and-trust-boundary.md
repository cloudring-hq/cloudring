# ADR-0005 - Secrets And Trust Boundary

```yaml
id: ADR-0005
status: proposed
title: Secrets And Trust Boundary
context: CloudRING должен работать в local, private, edge, provider и federation средах, где секреты, ключи и доверенные зоны принадлежат разным владельцам.
decision: Секреты управляются через scoped secret capabilities, brokered access, encrypted-at-rest declarations и audit, а не через прямое хранение значений в спецификациях.
supersedes: []
requirements:
  - CR-SEC-007..012
  - CR-SEC-013..018
  - CR-SELF-021..028
  - CR-INFRA-025
  - CR-APPROVAL-006
```

## Контекст

CloudRING должен позволять одному человеку и AI-агентам обслуживать облачную
платформу без превращения секретов в скрытый источник lock-in и риска. В
private, edge и federation сценариях секреты могут принадлежать владельцу
инфраструктуры, сервису, tenant, провайдеру или участнику federation. Эти
границы нельзя смешивать.

Секреты не должны попадать в service manifest, документацию, templates,
generated files, agent context или публичные артефакты. При этом платформа
должна оставаться воспроизводимой: backup, DR, upgrades и GitOps-подобные
потоки не должны требовать ручного копирования секретов.

## Решение

CloudRING использует trust-boundary модель:

- секрет всегда имеет owner, scope, environment, allowed capabilities и audit
  policy;
- конфигурация и секрет являются разными продуктовыми сущностями: конфигурацию
  можно показывать и версионировать шире, секрет требует отдельного trust
  boundary;
- спецификации описывают потребность в секрете, но не значение секрета;
- доступ к секрету выполняется через brokered capability, которая возвращает
  только то, что нужно конкретному workload или операции;
- encrypted declarations могут храниться в репозитории или backup только если
  расшифровка возможна в доверенной целевой среде;
- rotation, revocation и expiration являются частью lifecycle секрета;
- AI-агенты не получают plaintext secret, если задачу можно выполнить через
  brokered operation;
- если безопасный brokered access отсутствует, агент обязан остановиться и
  запросить approval/новое решение вместо обхода через просмотр значения;
- secret boundary должен быть виден в conformance report, audit и incident
  timeline;
- при переносе сервиса секреты не экспортируются как данные сервиса без явного
  owner-approved flow.

## Почему

Vendor lock-in часто прячется не только в API, но и в способе хранения ключей,
учетных записей, сертификатов и bootstrap-доступов. Если CloudRING не задаст
модель доверия с первого private cloud этапа, дальнейшая federation унаследует
опасные практики. Цель - сделать секреты переносимыми по контракту, но не
раскрываемыми по содержимому.

## Последствия

Положительные:

- private cloud может быть воспроизводимым без раскрытия секретов;
- агентская эксплуатация становится безопаснее;
- переносимость сервисов не требует копирования чувствительных значений;
- audit отвечает, кто и почему использовал brokered secret capability.

Отрицательные:

- простые dev-сценарии получают больше явных правил;
- понадобится UX для объяснения secret scopes и trust boundaries;
- не все внешние сервисы смогут быть перенесены без ручного owner approval.

Follow-up:

- описать минимальный secret readiness gate для Stage 2;
- определить, какие операции считаются brokered secret access;
- добавить secret exposure checks в conformance;
- связать secret rotation с incident и maintenance flows.

## Критерии Приемки

- Service manifest и Stage 2 инсталляционные спецификации не содержат plaintext
  secrets.
- Config values и secret references различаются в UI/API/audit и не смешиваются
  в export, logs, plans или generated artifacts.
- Каждый secret reference имеет owner, scope, environment и allowed capability.
- Агентская задача с secret access проходит через `CR-APPROVAL-006` и audit.
- Rotation/revocation имеют проверяемый lifecycle и не требуют переписывания
  сервисного контракта.
- Backup/restore private presence сохраняет возможность восстановить
  зашифрованные declarations без раскрытия секретов вне trust boundary.
