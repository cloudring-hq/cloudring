# ADR-0002 - Open Cloud Standard Schema Format

```yaml
id: ADR-0002
status: proposed
title: Open Cloud Standard Schema Format
context: Open Cloud Standard должен быть понятен людям, валидируем машинами и устойчив к смене runtime, языков и провайдеров.
decision: Стандарт описывается как versioned information model с human-readable Markdown narrative и machine-readable structured manifest.
supersedes: []
requirements:
  - CR-OCS-001..032
  - CR-AGENT-001..008
  - CR-DX-008..014
  - CR-OPS-029..032
```

## Контекст

CloudRING строится вокруг Open Cloud Standard: сервисный контракт должен быть
понятен разработчику, оператору, провайдеру, marketplace, conformance checks и
AI-агентам. Один только prose-документ не даст автоматической проверки. Один
только машинный manifest не сохранит продуктовый смысл, причины и границы.

Стандарт должен переживать смену технологий. Поэтому важна не привязка к одному
файловому формату, а стабильная информационная модель и правила версионирования.

## Решение

Open Cloud Standard должен иметь два согласованных слоя:

- normative human layer: Markdown-документация с назначением, why, ролями,
  scenarios, non-goals, responsibility boundaries и acceptance criteria;
- normative machine layer: structured manifest, который описывает capabilities,
  dependencies, lifecycle, policy, usage, observability, compatibility,
  portability и extension points.

Канонический стандарт задает информационную модель. Конкретная serialization
может меняться, если сохраняется обратимость, schema validation и compatibility
policy.

Обязательные правила:

- каждый manifest имеет version, kind, service identity и compatibility profile;
- extension fields разрешены только в явных namespace, чтобы не ломать ядро;
- breaking changes требуют новой версии стандарта и migration/deprecation plan;
- секреты, внутренние URLs, локальные пути и одноразовые runtime artifacts не
  являются частью service manifest;
- manifest должен генерировать проверяемые runtime intents, но не становиться
  ручной инструкцией конкретного runtime;
- documentation, manifest и conformance report должны ссылаться друг на друга.

## Почему

CloudRING должен обслуживаться человеком и командами AI-агентов. Агенту нужен
машинный контракт для проверки, генерации задач и conformance. Человеку нужен
контекст: зачем сервис существует, какие риски закрывает, кто за что отвечает и
где границы переносимости. Два слоя сохраняют и точность, и смысл.

## Последствия

Положительные:

- требования можно проверять автоматически;
- сервисы становятся сравнимыми в marketplace;
- AI-агенты могут генерировать и валидировать спецификации;
- продуктовый why не теряется в runtime artifacts.

Отрицательные:

- стандарт должен иметь дисциплину версий и совместимости;
- документация и manifest могут расходиться, если не будет автоматической
  проверки связности;
- потребуется отдельный conformance suite для каждого уровня зрелости.

Follow-up:

- описать минимальную schema для Stage 1 service manifest;
- определить набор обязательных и optional секций;
- описать compatibility rules между версиями стандарта;
- добавить template для service documentation, связанный с manifest.

## Критерии Приемки

- Новый сервис нельзя считать готовым без manifest, documentation и conformance
  report.
- Manifest валидируется до запуска workload.
- Documentation объясняет why и responsibility boundaries, а не только поля
  manifest.
- Агент может по manifest понять lifecycle, dependencies, observability, policy
  и portability limitations.
- Изменение стандарта имеет version, migration notes и статус совместимости.

