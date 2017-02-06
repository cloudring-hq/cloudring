# ADR-0016 - Continuous Evolution Loop

---
id: ADR-0016
status: proposed
title: Continuous Evolution Loop
context: CloudRING должен не устаревать при смене технологий, юрисдикций, угроз, бизнес-моделей и операционного опыта, но не должен отдавать архитектурные решения неконтролируемой автономии.
decision: Все значимые сигналы развития проходят через проверяемый loop: signal -> triage -> requirement/ADR/runbook/conformance change -> implementation plan -> validation -> audit -> learning record.
---

## Контекст

CloudRING строится как долгоживущая cloud-of-clouds платформа. За время жизни
платформы будут меняться runtime, hardware, security practices, jurisdiction
rules, billing models, AI-agent capabilities, user expectations and marketplace
economics. Если платформа привязана к текущему поколению технологий или к памяти
одного человека, она неизбежно устареет.

При этом "саморазвивающаяся" платформа не должна означать, что агент может
молча менять продуктовый контракт, рисковать клиентскими данными, подменять
юридические решения или удалять историю. Обучение должно быть системным,
проверяемым, трассируемым и подчиненным product requirements.

## Решение

CloudRING принимает Continuous Evolution Loop как обязательный product and
governance contract.

Каждый значимый сигнал классифицируется:

- incident;
- support case;
- repeated manual operation;
- conformance failure;
- security finding;
- marketplace feedback;
- provider/ISV/customer feedback;
- jurisdiction or policy change;
- technology generation change;
- dependency deprecation;
- cost/performance anomaly;
- new source supplied by the founder or ecosystem.

После intake урок получает один из triage outcomes:

- no-change;
- implementation guidance/profile update;
- conformance update;
- requirement change;
- ADR or ADR update;
- runbook update;
- agent task template;
- explicit rejection/defer with reason.

Сигнал не считается "обучением", пока не привел к одному из проверяемых
артефактов:

- new or changed requirement;
- ADR or ADR update;
- runbook update;
- conformance check;
- agent task template;
- product flow change;
- metric or quality gate;
- explicit rejection with reason.

Generated artifacts имеют lifecycle status, owner, source signal and next review.
Закрытие evolution item допустимо только через accepted artifact, validation
passed, explicit rejection/defer reason or owner-approved exception.

AI-агенты могут находить сигналы, строить impact analysis, готовить drafts,
запускать non-destructive validation and propose safe changes. Risky,
destructive, financial, legal, data-moving and trust-affecting changes остаются
под approval policy из `ADR-0009` и `21-agent-approval-matrix.md`.

## Почему

Главная цель CloudRING - снижать provider, technology and jurisdiction lock-in.
Если требования и conformance не обновляются после реального опыта, сама
платформа становится новой устаревающей зависимостью. Если же изменения
происходят без traceability, пользователи и участники сети перестают доверять
результату.

Continuous Evolution Loop нужен, чтобы:

- сохранять опыт после исходных текстов, инцидентов и решений;
- обновлять технологии без потери продуктового контракта;
- превращать repeated toil в automation and self-service;
- улучшать conformance по мере роста marketplace;
- удерживать AI-автономию в проверяемых границах;
- сохранять human ownership over mission, policy and risk.

## Product Rules

| Rule | Требование | Acceptance |
|---|---|---|
| EL-001 | Каждый значимый signal получает classification, source, owner and freshness. | Signal backlog показывает тип, scope, urgency, affected requirements and privacy status. |
| EL-002 | Повторяющийся incident/toil создает follow-up artifact. | После threshold появляется requirement/ADR/runbook/conformance/task draft или rejected reason. |
| EL-003 | Technology refresh оценивается через product contract impact, а не через модность технологии. | Impact analysis показывает affected capabilities, contracts, users, migration and rollback. |
| EL-004 | Requirements остаются source-safe. | New source intake проходит anonymization, copyright-safe paraphrase and secret scan. |
| EL-005 | Conformance suite evolves with requirements. | Accepted requirement with testable behavior has a linked conformance check or explicit exception. |
| EL-006 | AI-generated proposals remain drafts until validation and approval rules pass. | Agent output has risk_class, evidence, validation, owner and approval state. |
| EL-007 | Deprecated technology has migration or containment story. | Deprecation record shows supported profiles, timeline, alternatives, customer impact and exit path. |
| EL-008 | Learning record is human-readable and machine-readable. | Human can review what changed and agent can query requirements/ADR/runbook links. |
| EL-009 | Rejected suggestions are stored with reason. | Future agents can avoid rediscovering the same false path. |
| EL-010 | Product simplicity is part of evolution. | Repeated confusion or support friction can create UX requirement/conformance follow-up. |
| EL-011 | Operational lesson is classified before changing artifacts. | Outcome is no-change, guidance/profile, conformance, requirement, ADR, runbook, agent task or rejection. |
| EL-012 | Conformance changes are versioned. | New/changed check has version, reason, affected profiles, compatibility impact and rollout/migration note. |
| EL-013 | Failed implementation cannot silently weaken conformance. | Relaxing a check requires ADR/conflict note, owner, reason and affected requirement. |
| EL-014 | Technology refresh asks whether product contract changed. | Review states requirement/ADR change or implementation guidance/profile update. |
| EL-015 | Evolution closure has observable outcome. | Item closes with accepted artifact, validation, rejection/defer reason or owner-approved exception. |

## Consequences

Положительные последствия:

- CloudRING получает институциональную память, независимую от одного исходного
  репозитория или поколения технологии;
- conformance становится живой защитой от regressions and lock-in;
- incidents and support не теряются как разовые события;
- AI-агенты получают безопасный способ улучшать платформу.

Trade-offs:

- больше изменений требуют triage and evidence;
- быстрый эксперимент нельзя автоматически превратить в accepted platform
  contract;
- нужно поддерживать freshness, ownership and status для requirements, ADR,
  runbooks and conformance checks;
- rejected decisions тоже занимают место, но уменьшают повторение ошибок.
- conformance rollouts need compatibility windows instead of instant global
  enforcement.

## Anti-Patterns

Запрещенные паттерны:

- менять product requirement только потому, что появилась новая технология;
- закрывать incident без requirement/runbook/conformance follow-up, если он
  повторяется;
- делать agent-generated proposal сразу accepted;
- хранить source snippets, private names, URLs, secrets or pilot context in
  learning records;
- использовать "AI decided" как объяснение архитектурного trade-off;
- создавать conformance exception без owner, reason and expiry/review;
- ослаблять conformance ради текущей реализации без ADR/conflict note;
- менять product requirement, когда изменился только adapter, profile or
  implementation guidance;
- удалять старое решение без superseding trail;
- считать зеленый тест доказательством, если он не покрывает product risk.

## Критерии Приемки

ADR-0016 считается примененным, когда:

- signal backlog supports incident/support/source/tech/security/policy/market
  signals;
- repeated incident can be traced to requirement/ADR/runbook/conformance change
  or explicit rejection;
- technology refresh has product contract impact analysis;
- accepted requirement has linked validation path or documented exception;
- conformance changes have version, reason, affected scope, compatibility impact
  and migration/deprecation note;
- failed conformance cannot be "fixed" by weakening the standard without
  ADR/conflict note;
- technology refresh review states whether product contract changes or only
  implementation guidance/profile changes;
- AI proposal contains scope, risk, evidence, validation, owner and approval;
- evolution item closure records accepted artifact, validation, rejection/defer
  reason or owner-approved exception;
- source-derived changes pass anonymization and copyright-safe paraphrase checks;
- conformance drift and stale decisions are visible in metrics;
- human owner can override, reject or defer evolution with recorded reason.
