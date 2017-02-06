# CloudRING Requirements

Эта папка хранит продуктовые требования к CloudRING.
Ее цель - сохранить опыт из исходных материалов так, чтобы CloudRING можно было
реализовать заново без зависимости от старых исходных текстов, конкретных
технологий, конкретного провайдера или конкретной юрисдикции.

Требования написаны по-русски и рассчитаны на AI-агентов.
Они описывают, что платформа должна уметь, для кого это нужно, какую проблему
закрывает и почему это важно.
Они намеренно не являются инструкцией "как именно реализовать".

## Принципы Папки

1. Сохранять смысл, а не копировать текст источников.
2. Не переносить внутренние имена компаний, стендов, IP-адреса, URL, токены,
   секреты, приватные ключи, учетные записи и точные операционные команды.
3. Фиксировать продуктовую причину каждого важного решения.
4. Считать технологии заменяемыми, а контракт, сценарий и ожидаемый результат -
   устойчивыми.
5. Писать требования так, чтобы одиночный основатель и команда AI-агентов могли
   строить, проверять, эксплуатировать и развивать платформу.
6. При добавлении нового источника расширять требования, а не переписывать их
   под конкретную реализацию источника.

## Структура

- [00-source-analysis.md](00-source-analysis.md) - какие источники разобраны,
  что из них извлечено и какие материалы исключены из прямого переноса.
- [01-product-vision-and-principles.md](01-product-vision-and-principles.md) -
  стратегические требования и неизменные принципы CloudRING.
- [02-open-cloud-standard-service-contract.md](02-open-cloud-standard-service-contract.md) -
  требования к Open Cloud Standard, Service Connector и сервисному контракту.
- [03-platform-capabilities-and-lifecycle.md](03-platform-capabilities-and-lifecycle.md) -
  базовые возможности платформы и жизненный цикл сервисов.
- [04-developer-experience.md](04-developer-experience.md) - требования к
  разработке, локальной отладке, шаблонам сервисов, задачам и документации.
- [05-federation-marketplace-billing.md](05-federation-marketplace-billing.md) -
  федерация, marketplace, роли участников, биллинг и revenue sharing.
- [06-security-trust-compliance.md](06-security-trust-compliance.md) -
  безопасность, доверие, секреты, аудит, прозрачность и юрисдикционные риски.
- [07-operations-resilience-observability.md](07-operations-resilience-observability.md) -
  эксплуатация, наблюдаемость, надежность, stateful-сервисы и backup/DR.
- [08-private-edge-infrastructure.md](08-private-edge-infrastructure.md) -
  private cloud, edge, bare metal, VM-шаблоны, disconnected/connected режимы.
- [09-reference-architecture.md](09-reference-architecture.md) - целевая
  архитектура CloudRING как cloud-of-clouds сети.
- [10-self-service-and-ai-operations.md](10-self-service-and-ai-operations.md) -
  self-service модель для пользователя, администратора, провайдера и AI-агентов.
- [11-product-stages-and-finished-increments.md](11-product-stages-and-finished-increments.md) -
  этапы развития, где каждый этап является законченным продуктом.
- [12-agent-specification-system.md](12-agent-specification-system.md) -
  формат требований, архитектурных решений и задач для AI-агентов.
- [13-domain-model.md](13-domain-model.md) - концептуальная модель сущностей,
  событий и bounded contexts CloudRING.
- [14-architecture-decision-backlog.md](14-architecture-decision-backlog.md) -
  начальный backlog ADR, которые нужно принять перед реализацией ключевых
  слоев.
- [adr/](adr/) - отдельные Architecture Decision Records, где backlog
  превращается в проверяемые решения с последствиями и критериями приемки.
- [15-success-metrics-and-quality-bar.md](15-success-metrics-and-quality-bar.md) -
  измеримые критерии того, что CloudRING действительно решает lock-in и
  остается простым self-service продуктом.
- [16-requirements-governance.md](16-requirements-governance.md) - правила
  долгосрочного управления требованиями, конфликтами, статусами и источниками.
- [17-acceptance-criteria.md](17-acceptance-criteria.md) - проверяемые
  критерии приемки для ключевых групп требований.
- [18-federation-governance.md](18-federation-governance.md) - минимальная
  спецификация управления федерацией CloudRING.
- [19-experience-standard.md](19-experience-standard.md) - продуктовый
  стандарт простоты, красоты и эталонных self-service flow.
- [20-marketplace-journeys.md](20-marketplace-journeys.md) - app-store
  механика marketplace: buyer/seller journey, install/update/remove, reviews,
  refunds, support.
- [21-agent-approval-matrix.md](21-agent-approval-matrix.md) - матрица
  разрешений, доказательств и approval для AI-агентов.
- [22-conformance-readiness-profiles.md](22-conformance-readiness-profiles.md) -
  общий стандарт readiness/conformance profiles для проверки готовности stages.
- [23-product-capability-map.md](23-product-capability-map.md) - карта
  продуктовых capability, stages, dependencies and readiness profiles.
- [24-agent-workstream-backlog.md](24-agent-workstream-backlog.md) - backlog
  agent-readable product workstreams для будущей реализации CloudRING.
- [25-end-to-end-cloudring-architecture-spec.md](25-end-to-end-cloudring-architecture-spec.md) -
  сквозная продуктовая архитектурная спецификация cloud-of-clouds платформы:
  роли, presences, marketplace, provider loop, federation, trust, exit,
  operations and learning loops.
- [26-source-coverage-and-completion-audit.md](26-source-coverage-and-completion-audit.md) -
  coverage manifest and completion audit для source intake: что разобрано,
  что было targeted/sampled/history-focused, какие ограничения есть и какие
  exhaustive passes нужны дальше.
- [27-agent-readable-specification-templates.md](27-agent-readable-specification-templates.md) -
  product-level templates для OCS manifest, conformance report, role scenario
  fixture and source coverage manifest.
- [28-synthetic-examples-and-fixtures.md](28-synthetic-examples-and-fixtures.md) -
  заполненные synthetic examples для templates and scenario fixtures without old
  source context.
- [29-product-design-quality-and-scenario-depth.md](29-product-design-quality-and-scenario-depth.md) -
  product design quality gates, deeper negative scenarios, provider economics
  and jurisdiction overlays for task-based readiness evidence.
- [30-open-cloud-standard-information-model-and-schema-governance.md](30-open-cloud-standard-information-model-and-schema-governance.md) -
  OCS semantic information model, schema governance, canonical field catalog,
  extension lifecycle and versioned conformance suite.
- [31-service-lifecycle-command-surface-evidence.md](31-service-lifecycle-command-surface-evidence.md) -
  service lifecycle command, task, plugin, generated artifact and local runtime
  evidence requirements from implementation-backed source-slice review.
- [32-billing-runtime-evidence-and-settlement-trust.md](32-billing-runtime-evidence-and-settlement-trust.md) -
  billing runtime evidence, usage receipt/status, replay, release history and
  settlement freeze requirements from implementation-backed source-slice review.
- [33-stateful-restore-failover-readiness.md](33-stateful-restore-failover-readiness.md) -
  stateful restore, PITR, failover, audit bundle, topology and source-safe
  recovery evidence requirements from implementation-backed source-slice review.
- [34-documentation-decision-memory-evidence.md](34-documentation-decision-memory-evidence.md) -
  documentation, ADR, feedback, source-pass and decision-memory evidence
  requirements for reimplementation-ready product knowledge without old source
  access.
- [35-secret-runtime-readiness-evidence.md](35-secret-runtime-readiness-evidence.md) -
  encrypted secret, key custody, scope binding, reconciliation, install/delete
  and source-safe credential runtime readiness evidence requirements.
- [36-service-dependency-deployment-model-evidence.md](36-service-dependency-deployment-model-evidence.md) -
  service dependency graph, profile resolution, generated artifact, env handoff,
  component ownership and deployment model evidence requirements.
- [37-base-os-image-factory-readiness.md](37-base-os-image-factory-readiness.md) -
  base OS image factory, build input classification, unattended install,
  provisioning, guest readiness, cleanup/sealing, artifact lifecycle and
  source-safe promotion evidence requirements.
- [38-ui-extension-runtime-certification.md](38-ui-extension-runtime-certification.md) -
  UI extension runtime certification, validation parity, browser/accessibility,
  host authority, lifecycle cleanup, publication and source-safe evidence
  requirements.
- [39-settlement-closure-and-dispute-evidence.md](39-settlement-closure-and-dispute-evidence.md) -
  settlement closure, reconciliation, dispute, correction, participant share,
  closeout export and source-safe financial evidence requirements.
- [40-presence-bootstrap-activation-evidence.md](40-presence-bootstrap-activation-evidence.md) -
  presence bootstrap activation, trusted asset/config distribution, preflight,
  runtime provider matrix, diagnostics, rollback and agent-safe evidence
  requirements.
- [41-controlled-extension-and-task-automation-evidence.md](41-controlled-extension-and-task-automation-evidence.md) -
  controlled task, plugin, dependency mutation and boilerplate automation
  evidence requirements.
- [42-service-registry-catalog-publication-evidence.md](42-service-registry-catalog-publication-evidence.md) -
  service registry, catalog card, publication lifecycle, sync/cache and
  source-safe publication evidence requirements.
- [43-developer-workflow-scenario-evidence.md](43-developer-workflow-scenario-evidence.md) -
  developer workflow, thin e2e, run-profile, fixture, negative-case and
  source-safe scenario evidence requirements.
- [44-release-environment-promotion-evidence.md](44-release-environment-promotion-evidence.md) -
  release, environment bundle, artifact identity, runner, approval, rollback
  and source-safe promotion evidence requirements.
- [45-product-service-integration-contract-evidence.md](45-product-service-integration-contract-evidence.md) -
  product service integration package, product identity, scoped access, resource
  lifecycle, docs/spec drift, fixtures, support and source-safe onboarding
  evidence requirements.
- [46-support-diagnostics-evidence.md](46-support-diagnostics-evidence.md) -
  support diagnostics package, lifecycle state, correlation, primary failure
  story, error taxonomy, backpressure, image/stateful signals, redaction,
  retention and agent-safe evidence requirements.
- [47-support-case-sla-credit-evidence.md](47-support-case-sla-credit-evidence.md) -
  support case object, support ownership, SLA clock, customer impact,
  diagnostics and billing links, credit/refund review, party-scoped views and
  agent-safe support evidence requirements.
- [48-portal-experience-evidence.md](48-portal-experience-evidence.md) -
  portal/self-service UI evidence for role journeys, consequence-before-action,
  mode claims, action parity, support handoff, party-scoped views and agent-safe
  review.
- [49-reference-service-portfolio-evidence.md](49-reference-service-portfolio-evidence.md) -
  reference service portfolio evidence for archetype coverage, first useful
  behavior, docs/template readiness, observability, task/data, object artifact,
  secret-store, support handoff and source-safe non-claims.
- [templates/](templates/) - reusable agent-readable templates для будущих
  service contracts, OCS information models, readiness reports, role scenarios,
  product design quality reviews and source intake.
- [examples/](examples/) - filled synthetic examples for OCS, conformance,
  OCS information model, evidence bundles, profile changes, product design
  quality and source coverage.
- [scenarios/](scenarios/) - synthetic role scenario fixtures and role coverage
  matrix for stage readiness.
- [source-passes/](source-passes/) - source-safe результаты bounded source
  passes, которые постепенно закрывают coverage gaps из completion audit.
- [capabilities/](capabilities/) - detailed product capability contracts для
  базовых доменов IAM, policy, catalog и billing.
- [stages/](stages/) - подробные спецификации законченных продуктовых этапов,
  начиная с Solo Developer Cloud.
- [conformance/](conformance/) - stage readiness profiles, которые задают
  evidence, blockers and report shape для AI-agent review.
- [99-review-checklist.md](99-review-checklist.md) - команды и checklist для
  ревью требований перед каждой итерацией.
- [98-legacy-source-traceability-map.md](98-legacy-source-traceability-map.md) -
  карта того, как выводы команды агентов по legacy-источникам перенесены в
  требования.

## Формат Требований

Каждое требование имеет ID:

- `CR-CORE-*` - стратегия и принципы.
- `CR-OCS-*` - Open Cloud Standard и сервисный контракт.
- `CR-PLAT-*` - платформенные capability и lifecycle.
- `CR-DX-*` - developer experience.
- `CR-FED-*` - федерация, marketplace и экономика.
- `CR-SEC-*` - безопасность, доверие и compliance.
- `CR-OPS-*` - эксплуатация, надежность и observability.
- `CR-INFRA-*` - private/edge/infrastructure.
- `CR-ARCH-*` - reference architecture.
- `CR-SELF-*` - self-service and AI operations.
- `CR-AGENT-*` - требования к agent-readable спецификациям.
- `CR-DOMAIN-*` - domain model.
- `CR-METRIC-*` - success metrics and quality bar.
- `CR-GOV-*` - governance требований.
- `CR-UX-*` - experience standard.
- `CR-MKT-*` - marketplace journeys.
- `CR-APPROVAL-*` - approval matrix for agents.
- `CR-CONF-*` - conformance/readiness profiles and evidence model.
- `CR-CAPEVID-*` - cross-stage capability evidence matrix.
- `CR-CAP-*` - product capability map.
- `CR-WORK-*` - agent-readable product workstream backlog.
- `CR-END2END-*` - сквозная end-to-end архитектурная спецификация CloudRING.
- `CR-SRCOV-*` - source coverage manifest and completion audit.
- `CR-SPECTPL-*` - agent-readable specification templates and evidence shapes.
- `CR-SPECEX-*` - filled synthetic examples and fixtures for templates/scenarios.
- `CR-DESIGNQ-*` - product design quality, scenario depth and task-based
  experience readiness.
- `CR-OCSCONTRACT-*` - capability contract для Open Cloud Standard.
- `CR-OCSIM-*` - Open Cloud Standard information model and schema governance.
- `CR-LIFECMD-*` - service lifecycle command surface evidence.
- `CR-BILLRUN-*` - billing runtime evidence and settlement trust.
- `CR-SETTLE-*` - settlement closure, reconciliation and dispute evidence.
- `CR-PRESBOOT-*` - presence bootstrap activation and trusted install evidence.
- `CR-EXTAUTO-*` - controlled extension, task, dependency and boilerplate
  automation evidence.
- `CR-CATREG-*` - service registry, catalog publication and private store
  publication evidence.
- `CR-WORKFLOW-*` - developer workflow, scenario, e2e and run-profile evidence.
- `CR-RELPROM-*` - release, environment promotion, artifact, runner, approval
  and rollback evidence.
- `CR-SVCINT-*` - product service integration package, scoped access, resource
  lifecycle, docs/spec drift, fixtures and source-safe onboarding evidence.
- `CR-SUPDIAG-*` - support diagnostics package, correlation, lifecycle state,
  error taxonomy, redaction, retention and agent-safe support evidence.
- `CR-SUPCASE-*` - support case, SLA clock, credit/refund review,
  communication, party-scoped views and agent-safe case evidence.
- `CR-PORTALUX-*` - portal experience, self-service UI, role journey,
  consequence-before-action and portal readiness evidence.
- `CR-REFSVC-*` - reference service portfolio, archetype coverage, golden
  service evidence, docs/template readiness, observability, task/data and
  source-safe showcase non-claims.
- `CR-STATEFULRUN-*` - stateful restore, PITR, failover and recovery evidence.
- `CR-DOCMEM-*` - documentation, ADR and decision-memory evidence.
- `CR-SECRETRUN-*` - encrypted secret and credential runtime readiness evidence.
- `CR-SVCDEPLOY-*` - service dependency and deployment model evidence.
- `CR-BASEIMG-*` - base OS image factory and reusable image readiness evidence.
- `CR-UICERT-*` - UI extension runtime certification and validation parity evidence.
- `CR-SERVICEFACTORY-*` - capability contract для Service Factory and Local Runtime.
- `CR-SECSUPPLY-*` - capability contract для Security, Secrets and Supply Chain.
- `CR-FEDNET-*` - capability contract для Federation and Global Trust Network.
- `CR-IAM-*` - capability contract для IAM and Resource Manager.
- `CR-POLICY-*` - capability contract для Policy and Placement.
- `CR-CATALOG-*` - capability contract для Service Catalog and Product Control Plane.
- `CR-BILL-*` - capability contract для Billing, Entitlements and Settlement.
- `CR-INFPROFILE-*` - capability contract для Infrastructure Capability Profiles.
- `CR-OBSOPS-*` - capability contract для Observability, Support and Operations.
- `CR-PORTX-*` - capability contract для Portability, Exit and Cross-Provider Operations.
- `CR-AGOPS-*` - capability contract для Self-Service and Agent Operations.
- `CR-STAGE0-*` - детальные требования Stage 0 Requirements And Agent Memory.
- `CR-STAGE1-*` - детальные требования Stage 1 Solo Developer Cloud.
- `CR-STAGE2-*` - детальные требования Stage 2 Private Cloud OS Zone.
- `CR-STAGE3-*` - детальные требования Stage 3 Service Store For Private Cloud.
- `CR-STAGE4-*` - детальные требования Stage 4 Public Cloud Provider Kit.
- `CR-STAGE5-*` - детальные требования Stage 5 Federation Network.
- `CR-STAGE6-*` - детальные требования Stage 6 Global CloudRING.
- `CR-STAGE7-*` - детальные требования Stage 7 Self-Evolving Platform.
- `ADR-*` - архитектурные решения, связывающие требования с выбранными
  продуктовыми trade-offs.

Статусы ADR:

- `proposed` - решение описано как draft и может использоваться для планирования,
  но перед production-реализацией требует review.
- `accepted` - решение принято как текущая архитектурная граница.
- `superseded` - решение заменено новым ADR.
- `deprecated` - решение сохраняется для истории, но не должно использоваться
  для новых реализаций.

Рекомендуемый формат для новых требований:

```text
ID: CR-DOMAIN-001
Статус: draft | accepted | superseded
Требование: что должно быть возможно.
Почему: продуктовая причина.
Пользователи: роли, для кого это важно.
Критерии приемки: как понять, что требование выполнено.
Источник: краткое обезличенное указание источника опыта.
```

## Правила Для AI-Агентов

Перед проектированием или реализацией CloudRING агент должен:

1. Найти требования нужного домена.
2. Проверить, не противоречит ли решение принципам из
   `01-product-vision-and-principles.md`.
3. Отделить обязательный контракт от конкретной технологии реализации.
4. Добавить новые требования, если найденный источник содержит опыт, которого
   еще нет в этой папке.
5. Не использовать исходные тексты как шаблон для копирования; использовать
   только извлеченные продуктовые требования и причины.

## Главная Идея

CloudRING должен стать открытой распределенной cloud/post-cloud платформой,
которая снижает vendor lock-in, technology lock-in и jurisdiction lock-in.
Она должна позволить строить облачного провайдера одному человеку и командам
AI-агентов, подключать провайдеров, частные облака, edge-площадки,
разработчиков и независимых поставщиков сервисов через общий стандарт,
федерацию, marketplace, прозрачный биллинг и переносимый lifecycle.

CloudRING должен быть простым, цельным и красивым в использовании:
сложность federation, billing, policy, инфраструктуры и эксплуатации должна
быть скрыта за ясными self-service сценариями, понятными пользователю,
администратору и AI-агенту.
