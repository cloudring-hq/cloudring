# Stage 3 - Service Store For Private Cloud

```yaml
id: STAGE-003
status: draft
title: Service Store For Private Cloud
goal: Дать private cloud владельцу app-store модель установки, обновления, лицензирования и сопровождения готовых сервисов без потери локального контроля.
primary_users:
  - private cloud administrator
  - service buyer
  - internal service developer
  - ISV / seller
  - platform operator
  - AI verification agent
related_adr:
  - ADR-0002
  - ADR-0005
  - ADR-0006
  - ADR-0007
  - ADR-0008
  - ADR-0009
  - ADR-0011
  - ADR-0013
related_requirements:
  - CR-FED-011..018
  - CR-FED-030
  - CR-MKT-001..028
  - CR-CATALOG-001..029
  - CR-CATREG-001..032
  - CR-OCS-014..032
  - CR-SELF-017..020
  - CR-DX-020..029
  - CR-STAGE2-020..023
```

## Назначение

Stage 3 добавляет к private cloud зоне локальный service store: возможность
находить, проверять, устанавливать, обновлять, удалять и сопровождать готовые
сервисы как продукты. Это app-store слой для private-инсталляции, но еще не
глобальный публичный marketplace, не provider kit и не settlement network.

Главный результат: private cloud владелец может использовать готовые сервисы,
лицензировать дополнительные возможности, устанавливать внутренние сервисы и
готовить свои сервисы к будущей публикации в сеть CloudRING, сохраняя локальный
контроль, policy и переносимость.

## Product Promise

Администратор открывает service store в private presence, видит совместимые
сервисы, trust/certification/portability/support/update information, получает
install plan, проходит policy checks, устанавливает сервис, наблюдает instance
state, обновляет через plan/apply/validate, удаляет с export/retention options
и передает routine checks AI-агенту. Seller/ISV видит conformance failures и
понятный путь к `private-ready`.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-STAGE3-001 | Stage 3 должен быть локальным service store для private presence, а не публичным marketplace. | Private cloud должен получить ценность до federation commerce. | Сервисы ищутся, проверяются, устанавливаются и обновляются внутри private presence без обязательного settlement. |
| CR-STAGE3-002 | Service store должен использовать Open Cloud Standard как входной контракт. | Каталог без стандарта не дает переносимости. | Service candidate без manifest, compatibility profile и conformance report не получает install-ready статус. |
| CR-STAGE3-003 | Service card должна показывать capability, dependencies, certification, trust, portability, support, update и entitlement state. | Покупатель должен понимать риск до установки. | Buyer/admin видит эти поля до install plan. |
| CR-STAGE3-004 | Поиск должен фильтровать по task/capability, compatibility, policy, portability, support и certification. | Private администратор выбирает результат и ограничения, а не бренд. | Search не предлагает сервисы, запрещенные policy, без явного warning/override path, если override допустим. |
| CR-STAGE3-005 | Install plan должен быть policy-aware и идемпотентным. | Установка сервиса меняет ресурсы, безопасность и ответственность. | Повтор install request не создает дубликаты; plan показывает resources, dependencies, policies, permissions и rollback/compensation. |
| CR-STAGE3-006 | Сервис нельзя установить без compatibility match с текущей presence. | Несовместимый сервис разрушает доверие к store. | Incompatible service получает visible blocker и remediation/alternative suggestions. |
| CR-STAGE3-007 | `private-ready` certification является минимальным уровнем для обычной установки в Stage 3. | Private cloud не должен принимать непроверенные сервисы как production-ready. | Dev-only сервис можно установить только в explicit dev/test scope с warning и audit. |
| CR-STAGE3-008 | Certification должен быть install/update gate, а не только бейджем. | Store должен защищать пользователя, а не просто информировать. | Install/update блокируется, если certification level ниже policy threshold или новая версия снижает уровень без approval. |
| CR-STAGE3-009 | Service Connector должен проходить sandbox/validation до публикации в локальный store. | Connector является границей доверия. | Validation report показывает implemented capabilities, missing capabilities, security findings и limitations. |
| CR-STAGE3-010 | Plugin/extension установка должна следовать `ADR-0006`. | Плагин может расширить платформу и повлиять на безопасность. | Plugin listing показывает permissions, risk class, publisher, compatibility, trust state и disable/revoke path. |
| CR-STAGE3-011 | Entitlement должен следовать `ADR-0013`. | Лицензия не должна быть скрытым выключателем локального облака. | Runtime/update/support/feature entitlements видны отдельно до install/update/remove. |
| CR-STAGE3-012 | Stage 3 должен поддерживать connected и offline/deferred update modes. | Private cloud может иметь ограниченную связь. | Store показывает update eligibility, pin/defer state, какие updates требуют sync, и какие риски есть при задержке. |
| CR-STAGE3-013 | Update должен проходить через changelog, impact, compatibility и rollback/compensation review. | Сервисное обновление может сломать workload. | Update plan показывает affected instances, downtime risk, data migration, entitlement impact, pin/defer options и validation. |
| CR-STAGE3-014 | Remove должен показывать export, data retention, dependency impact и irreversible effects. | Удаление не должно становиться скрытым lock-in. | Пользователь не может удалить stateful service без explicit export/retention decision или documented non-exportable limitation. |
| CR-STAGE3-015 | Store должен поддерживать internal/private services. | Компании и владельцы private cloud будут развивать собственные сервисы. | Internal service проходит те же manifest, security, observability и docs checks, но может иметь private-only visibility. |
| CR-STAGE3-016 | Seller/ISV publication workflow должен быть self-service. | Экосистема не масштабируется ручной сертификацией. | Seller получает readiness report, failed checks и next actions без ручного запроса к оператору. |
| CR-STAGE3-017 | Support ownership должен быть частью installed service instance. | Пользователь не должен вручную объяснять цепочку ответственности. | Support request видит service, version, plan, entitlement, owner, SLA/support state, logs/timeline context и responsibility boundary. |
| CR-STAGE3-018 | Store должен показывать alternatives и substitutes там, где они совместимы. | Это прямой механизм против lock-in. | Service card показывает compatible alternatives или объясняет, почему их нет. |
| CR-STAGE3-019 | Portability statement обязателен для install-ready сервиса. | Пользователь должен понимать выход до входа. | Service card показывает export/import/backup/restore story или visible limitation. |
| CR-STAGE3-020 | Store должен иметь trust score, но не заменять им certification. | Один агрегат не должен скрывать конкретные риски. | Trust score раскрывается в составляющие: certification, incidents, security response, docs, support, portability. |
| CR-STAGE3-021 | Store actions должны быть доступны через UI/API/CLI/Agent API. | Self-service и агенты должны работать с одним продуктовым flow. | Search, install plan, apply, update, remove, support и certification report имеют machine-readable representation. |
| CR-STAGE3-022 | AI-агент может выполнять store verification, но не bypass policy/approval. | Автоматизация должна ускорять проверку, а не снижать безопасность. | Agent task имеет risk_class, scope, validation, rollback/compensation и audit. |
| CR-STAGE3-023 | Stage 3 должен иметь conformance profile `stage3-private-store-ready`. | Нужна объективная граница готовности. | Report показывает catalog readiness, certification coverage, install/update/remove checks, entitlement state и blockers. |
| CR-STAGE3-024 | Stage 3 не должен включать global settlement or cross-participant settlement как обязательную функцию. | Provider-local billing относится к Stage 4, а cross-participant settlement относится к Stage 5. | Store может фиксировать entitlement/usage-ready metadata, но не требует public-provider billing или multi-party settlement. |
| CR-STAGE3-025 | Store должен сохранять локальную работоспособность установленных сервисов при недоступности внешнего каталога. | Private cloud не должен ломаться из-за потери связи. | Installed services, local catalog cache, entitlement state и support evidence остаются видимыми offline. |
| CR-STAGE3-026 | Store должен поддерживать service deprecation и migration path. | Старые версии нельзя бросать без пути выхода. | Deprecated service показывает replacement, timeline, export/migration plan и support impact. |

## Acceptance Scenarios

### Scenario A - Install Private-Ready Service

Цель: доказать app-store установку сервиса в private cloud.

Критерии:

- service card показывает certification, compatibility, entitlement,
  portability, dependencies и support terms;
- install plan проходит policy and compatibility checks;
- install создает service instance без дубликатов при повторе;
- instance имеет docs, health, logs/metrics/traces и available actions;
- conformance report фиксирует install evidence.

### Scenario B - Publish Internal Service

Цель: доказать, что private owner может развивать собственные сервисы.

Критерии:

- internal service candidate проходит manifest validation;
- security/observability/docs checks возвращают readiness report;
- visibility ограничена private scope;
- failed checks имеют actionable remediation;
- сервис можно установить как private-only item после прохождения gates.

### Scenario C - Update With Entitlement And Rollback

Цель: доказать безопасное обновление service store item.

Критерии:

- update plan показывает changelog, impact, compatibility, entitlement,
  pin/defer options и rollback/compensation;
- risky/destructive steps требуют approval;
- validation выполняется после update;
- при failure пользователь видит recovery path и support handoff.

### Scenario D - Remove Without Lock-In

Цель: доказать, что удаление не прячет удержание пользователя.

Критерии:

- remove plan показывает data retention, export options, backup and dependency
  impact;
- stateful сервис требует explicit decision по данным;
- billing/entitlement stop semantics видны пользователю;
- irreversible effects требуют explicit approval.

### Scenario E - Offline Store Continuity

Цель: доказать, что private store не ломает автономию private presence.

Критерии:

- installed services остаются видимыми и управляемыми без внешнего каталога;
- local entitlement state показывает current/degraded/grace behavior;
- новые external installs помечаются как unavailable/deferred, если требуют
  sync;
- audit сохраняет deferred sync events.

### Scenario F - Agent Verification

Цель: доказать, что AI-агент помогает store без обхода policy.

Критерии:

- агент читает service manifest, ADR, certification report, policy и health;
- агент формирует verification summary с risk class;
- агент не устанавливает plugin/service с controlled/risky permissions без
  approval;
- результат сохраняется в audit и human-readable summary.

### Scenario G - Publish Catalog Record

Цель: доказать, что service становится видимым в private store через governed
registry publication, а не через случайно найденный manifest, seed row or asset.

Критерии:

- publication request показывает owner, support owner, visibility scope,
  identity/collision policy and readiness target;
- manifest validation, artifact trust, dependency/deployment evidence, docs,
  support and source-safety scan linked before visibility changes;
- static asset availability or local debug success is not enough for
  install-ready status;
- publish/update/deprecate/remove actions produce audit, rollback or
  compensation, and affected-user impact;
- local/private cache and sync ledger preserve installed-service management
  without giving global registry ownership over local lifecycle.

## Agent Task Seeds

```yaml
id: TASK-STAGE3-001
goal: Описать conformance profile stage3-private-store-ready.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/03-service-store-for-private-cloud.md
    - requirements/20-marketplace-journeys.md
    - requirements/17-acceptance-criteria.md
  exclude:
    - global settlement
    - public provider onboarding
inputs:
  - CR-STAGE3-023
  - CR-MKT-001..019
  - CR-FED-011..018
expected_outputs:
  - readiness checks
  - report fields
  - certification gates
permissions:
  secrets: none
  destructive_actions: false
validation:
  - every check maps to a requirement or ADR
rollback:
  - disputed checks become draft and link to ADR follow-up
```

```yaml
id: TASK-STAGE3-002
goal: Спроектировать product flow install/update/remove для private store.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/03-service-store-for-private-cloud.md
    - requirements/adr/0013-local-entitlement-and-offline-licensing.md
    - requirements/adr/0007-marketplace-certification-levels.md
  exclude:
    - payment processing
    - multi-party settlement
inputs:
  - CR-STAGE3-005
  - CR-STAGE3-011
  - CR-STAGE3-013
  - CR-STAGE3-014
expected_outputs:
  - user-visible states
  - required evidence
  - policy/approval boundaries
permissions:
  secrets: none
  destructive_actions: false
validation:
  - flow covers install, update, remove and offline continuity
rollback:
  - supersede via ADR if entitlement model changes
```

## Non-Goals

Stage 3 намеренно не является:

- публичным provider kit;
- глобальной federation network;
- multi-party settlement системой;
- полноценным payment processing;
- заменой governance для federation;
- универсальной сертификацией всех рынков и регуляторных режимов.

Stage 3 должен сделать private cloud богаче и ближе к app-store опыту, но
сохранить локальный контроль и подготовить сервисы к будущим Stage 4/5.

## Readiness Gate

Stage 3 считается готовым, когда:

- private presence имеет local service store;
- service registry/catalog publication имеет identity, owner, lifecycle,
  policy visibility, sync/cache and source-safe publication evidence;
- сервисы имеют cards, compatibility, certification, portability, entitlement и
  support/update state;
- install/update/remove работают через plan/apply/validate;
- `private-ready` certification проверяет manifest, dependencies, security,
  observability, docs и portability statement;
- plugin/extension flow соответствует `ADR-0006`;
- entitlement/offline licensing соответствует `ADR-0013`;
- installed services продолжают быть управляемыми при недоступности внешнего
  каталога;
- agent verification проходит approval matrix;
- conformance report показывает `stage3-private-store-ready` или конкретные
  blockers.
