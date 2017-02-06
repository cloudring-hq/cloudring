# ADR-0012 - Beautiful Simplicity Product Standard

---
id: ADR-0012
status: proposed
title: Beautiful Simplicity Product Standard
context: CloudRING должен оставаться понятным self-service продуктом, хотя внутри объединяет federation, marketplace, billing, policy, trust, private/edge и AI-operated operations.
decision: Простота и красота являются продуктовым архитектурным контрактом: каждый основной flow должен начинаться с намерения пользователя, показывать важные последствия до действия, раскрывать сложность постепенно и быть одинаково понятным человеку, API, CLI и AI-агенту.
---

## Контекст

CloudRING создается как cloud-of-clouds сеть. Это означает много участников,
юрисдикций, моделей доверия, тарифов, support chains, lifecycle states и
ограничений переносимости. Если эта сложность станет видимой как набор
внутренних сущностей, продукт будет сильным технически, но непригодным для
массового использования и обслуживания одним человеком с AI-агентами.

Простота в CloudRING не означает скрывать риски. Она означает:

- начинать с задачи пользователя, а не с внутреннего объекта платформы;
- показывать цену, риск, trust, jurisdiction, SLA и portability до решения;
- давать безопасные defaults, но объяснять, почему они выбраны;
- раскрывать детали по запросу, audit и agent API;
- делать ошибки и ограничения полезными, а не тупиковыми;
- сохранять одинаковую модель мира в UI, API, CLI, events и документации.

## Решение

CloudRING принимает Beautiful Simplicity Product Standard как обязательный
критерий для всех stages, marketplace offers, provider portals, admin flows,
agent operations and support flows.

Стандарт требует:

1. Intent-first flows.
   Пользователь начинает с намерения: заказать сервис, перенести workload,
   подключить provider, установить private cloud, опубликовать offer, восстановить
   сервис. Внутренние сущности появляются только когда они нужны для выбора.

2. Consequence-before-action.
   Перед подтверждением действия пользователь, администратор или агент видит
   стоимость, data location, jurisdiction, provider chain, trust state, SLA,
   portability limits, rollback and support owner.

3. Progressive disclosure.
   Первый экран показывает короткий осмысленный выбор. Детали policy decisions,
   compatibility, price formula, provider chain, data handling, rollback,
   evidence, raw events and audit доступны рядом, но не заменяют основной
   сценарий.

4. Safe defaults with explainability.
   Платформа может предлагать recommended placement, plan, update path or
   remediation, но обязана объяснить критерии выбора и показать альтернативы.

5. Human-agent symmetry.
   То, что видит человек, должно иметь machine-readable эквивалент для агента.
   То, что делает агент, должно иметь human-readable plan, risk, approval,
   validation and outcome summary.

6. One vocabulary.
   UI, API, CLI, events, support, billing and documentation используют одинаковые
   names, lifecycle states and risk labels.

7. Useful failure.
   Ошибка всегда объясняет cause, impact, safe next step, retry/remediation path
   and evidence bundle. Если self-service невозможен, создается support-ready
   package.

8. Measured simplicity.
   Простота проверяется task-based сценариями, а не мнением дизайнера или
   красотой отдельных экранов.

## Почему

CloudRING должен стать платформой, которую можно развивать одному человеку с
командой AI-агентов и использовать независимым провайдерам, private cloud
владельцам, разработчикам сервисов и покупателям. Без жесткого стандарта
простоты каждый новый слой federation будет добавлять когнитивный долг.

Этот ADR снижает риск того, что:

- power-user интерфейс станет единственным способом управления;
- AI-агенты будут действовать в другой терминологии, чем люди;
- marketplace начнет продавать сложность вместо результата;
- federation будет выглядеть как новая форма lock-in;
- ошибки и policy conflicts будут требовать ручной поддержки.

## Product Rules

| Rule | Требование | Acceptance |
|---|---|---|
| BS-001 | Основной flow начинается с пользовательского результата. | В flow нет обязательного первого шага, который требует знать внутренний bounded context. |
| BS-002 | Важные последствия видны до irreversible/risky action. | Confirmation показывает price/risk/policy/trust/support/rollback summary. |
| BS-003 | Recommended choice объясняется. | Recommendation includes why, alternatives and blocked options. |
| BS-004 | Состояния одинаковы в UI/API/CLI/events. | Same resource returns same lifecycle state and risk label in all interfaces. |
| BS-005 | Agent-readable output существует для каждого operator-critical screen. | Agent can obtain structured state, evidence and allowed actions without scraping UI. |
| BS-006 | Ошибка ведет к действию. | Error includes cause, impact, next step, retry/remediation and support bundle reference. |
| BS-007 | Пользователь может открыть evidence, но не обязан читать его для обычного happy path. | Summary is sufficient for safe decision; details are one action away. |
| BS-008 | Сложность governance/federation не скрывает ownership. | User sees provider chain, support owner and responsibility boundaries. |
| BS-009 | Стандартные сценарии завершаются без оператора. | User/admin/ISV/provider completes supported flow through UI/API/CLI/agent API. |
| BS-010 | Красота означает ясность, предсказуемость и уважение к вниманию. | Review rejects ornamental, noisy or misleading presentation of risk-critical information. |
| BS-011 | Service UI extensions must preserve common navigation, permissions, terminology, theme, lifecycle states and evidence rules. | Marketplace расширяет продукт, но не фрагментирует опыт. |

## Consequences

Положительные последствия:

- продуктовые решения получают общий quality bar;
- AI-агенты могут безопаснее действовать, потому что видят те же states and
  consequences, что человек;
- onboarding новых providers, ISV и admins становится воспроизводимым;
- пользователь доверяет federation, потому что ownership and risks не скрыты.

Trade-offs:

- каждая новая capability должна иметь experience acceptance criteria;
- нельзя выпускать API-only capability без human-readable product path, если она
  влияет на пользователя, деньги, данные, trust или SLA;
- internal model может быть сложнее, чем видимый flow, но эта сложность должна
  иметь explainability and evidence.
- service micro-UI and extensions cannot bypass common navigation, permissions,
  lifecycle vocabulary, approval and evidence rules.

## Anti-Patterns

Запрещенные продуктовые паттерны:

- "создай внутренний ресурс X", когда пользовательский результат понятен иначе;
- скрытая рекомендация без explanation and alternatives;
- глобальный marketplace, который маскирует provider ownership;
- warning fatigue: много предупреждений без приоритета и next step;
- attractive UI that masks irreversible consequences;
- ошибки без remediation;
- разные названия одного состояния в UI/API/CLI;
- агентские действия без human-readable plan and validation;
- "universal portability" как маркетинговое обещание без честного portability
  profile.

## Критерии Приемки

ADR-0012 считается примененным, когда:

- `CR-UX-001..021` используются как review checklist для новых flows;
- каждый stage имеет at least one user/admin/provider/agent acceptance scenario;
- risky action показывает consequence summary before approval;
- API/CLI/agent output exposes same lifecycle state as UI;
- standard flow can be completed without support for supported profiles;
- blocked/manual/non-standard path creates useful support-ready evidence;
- user can explain what will happen, where it will run, who owns/supports it,
  how to stop/rollback it and how to export/leave;
- conformance review может отклонить capability за нарушение product simplicity,
  даже если technical implementation работает.
