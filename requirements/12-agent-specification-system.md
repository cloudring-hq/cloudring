# Agent Specification System

Этот документ задает формат, в котором требования и архитектурные решения должны
быть понятны AI-агентам.

## Requirement Object

Каждое требование должно быть самодостаточным.

```yaml
id: CR-DOMAIN-NNN
status: draft
title: Short product title
statement: What must be true
why: Product reason and experience behind the requirement
users:
  - role
scenarios:
  - scenario name
acceptance:
  - observable acceptance criterion
non_goals:
  - what this requirement does not imply
source_signals:
  - anonymized source signal
risks:
  - product or operational risk
links:
  - related requirement id
```

## Architecture Decision Object

```yaml
id: ADR-0000
status: proposed
title: Decision title
context: Why the decision is needed
decision: What we choose
consequences:
  positive:
    - expected benefit
  negative:
    - tradeoff
  follow_up:
    - future work
supersedes:
  - ADR-previous
requirements:
  - CR-...
```

## Agent Task Object

```yaml
id: TASK-0000
goal: Concrete outcome
mode: investigate | plan | implement | verify | operate
risk_class: read-only | safe-change | controlled-change | risky-change | destructive | emergency
scope:
  include:
    - files/domains
  exclude:
    - forbidden files/domains
inputs:
  - requirement ids
expected_outputs:
  - artifact or validation
template_refs:
  - template id or path
conformance_report_ref: optional-safe-reference
evidence_bundle_refs:
  - evidence-bundle-id
coverage_manifest_ref: optional-safe-reference
validation_summary_ref: optional-safe-reference
permissions:
  secrets: none | brokered | direct
  destructive_actions: false
validation:
  - command/check/review
rollback:
  - rollback or compensation
```

## Требования К Документам Для Агентов

| ID | Требование | Почему |
|---|---|---|
| CR-AGENT-001 | Каждый requirement должен иметь `why`. | Агент не сможет правильно заменить технологию без понимания причины. |
| CR-AGENT-002 | Каждый requirement должен иметь acceptance criteria. | Иначе агент не поймет, когда задача выполнена. |
| CR-AGENT-003 | Каждый architecture decision должен ссылаться на requirements. | Решение должно обслуживать продуктовую цель. |
| CR-AGENT-004 | Любой source-derived requirement должен иметь обезличенный source signal. | Нужна трассируемость без раскрытия внутреннего контекста. |
| CR-AGENT-005 | Агентские задачи должны явно указывать scope и non-scope. | Это снижает риск случайных изменений. |
| CR-AGENT-006 | Агентские задачи должны иметь validation и rollback/compensation. | Автономная работа должна быть проверяемой и обратимой. |
| CR-AGENT-007 | Для risky/destructive операций агент должен требовать явного policy approval. | Не все можно автоматизировать без контроля. |
| CR-AGENT-008 | Agent-readable документы должны быть совместимы с human-readable Markdown. | Люди и агенты должны работать с одной памятью. |
| CR-AGENT-009 | Агентские задачи должны указывать risk class из approval matrix. | Агент не должен сам решать уровень риска уже в момент выполнения. |
| CR-AGENT-010 | Агентские задачи должны ссылаться на expected templates, evidence bundles, conformance report or coverage manifest where relevant. | Свободная форма результата плохо проверяется и плохо наследуется следующим агентом. |
| CR-AGENT-011 | Агентский результат должен иметь source-safe output boundary. | Агент может случайно перенести приватный source context в требования или evidence. |

## Source Intake Workflow

Когда пользователь дает новый источник:

1. Зарегистрировать источник в `00-source-analysis.md`.
2. Определить тип: idea, codebase, docs, git history, incident, customer story,
   architecture, security, billing, operations.
3. Полностью прочитать источник или явно зафиксировать, что исключено и почему.
4. Извлечь product requirements: what, why, user, scenario, acceptance.
5. Удалить внутренние имена, секреты, URLs, IP, hostnames, direct copy.
6. Сопоставить с существующими requirements.
7. Добавить новые requirements или уточнить существующие.
8. Если источник меняет архитектурное решение, создать или обновить ADR.
9. Запустить checks на обезличивание и противоречия.

## Quality Bar

Спецификация считается хорошей, если:

- по ней можно реализовать capability без доступа к исходнику;
- она не копирует исходник;
- она объясняет причину решения;
- она допускает замену технологии;
- она имеет критерии приемки;
- она понятна человеку и AI-агенту;
- она не раскрывает пилотный контекст;
- она помогает сделать CloudRING проще, надежнее и красивее.
