# ADR-0009 - Agent Permission And Approval Model

```yaml
id: ADR-0009
status: proposed
title: Agent Permission And Approval Model
context: CloudRING должен обслуживаться человеком и AI-агентами, но агентская автономия не должна обходить ownership, policy, audit и safety boundaries.
decision: Все агентские действия классифицируются по risk class до выполнения и исполняются только в пределах approval policy.
supersedes: []
requirements:
  - CR-SELF-021..028
  - CR-ARCH-028..032
  - CR-AGENT-001..008
  - CR-APPROVAL-001..008
```

## Контекст

CloudRING задуман как платформа, которую можно развивать и обслуживать одному
основателю вместе с командами AI-агентов. Это требует агентской автономии, но
не допускает невидимого суперпользователя. Агент должен быть оператором с
понятными границами, evidence, audit и остановками.

Для Stage 1 это особенно важно: локальная среда кажется низкорисковой, но уже
содержит сервисные контракты, секреты разработки, dependencies, tasks и
артефакты готовности. Если агент привыкнет менять состояние без классификации
риска, та же привычка позже перенесется в private, provider и federation
сценарии.

## Решение

CloudRING использует risk-class модель из `21-agent-approval-matrix.md`.

Обязательные правила:

- каждое агентское действие получает risk class до выполнения;
- агент не может сам повысить свои permissions или обойти approval policy;
- агент может выполнять `read-only` и `safe-change` действия автономно только
  внутри выданного scope и при наличии validation/audit;
- `controlled-change` требует policy approval или заранее утвержденный runbook;
- `risky-change` и `destructive` требуют явного approval владельца domain или
  человека, с rollback/backup evidence там, где применимо;
- `emergency` действия допустимы только по заранее описанным сценариям и
  требуют немедленного audit и последующего review;
- доступ к секретам должен быть brokered, а не через раскрытие значения агенту;
- если validation противоречит expected outcome, агент обязан остановиться.

## Почему

CloudRING должен масштабировать способность одного человека строить облачного
провайдера, но не должен превращать автоматизацию в неконтролируемый риск.
Approval model сохраняет ownership, делает действия объяснимыми и позволяет
постепенно расширять автономию агентов без потери доверия.

## Последствия

Положительные:

- агентские действия становятся проверяемыми и воспроизводимыми;
- человек остается владельцем политики и рискованных решений;
- одна модель разрешений работает от Stage 1 до federation;
- audit trail становится источником обучения, требований и ADR.

Отрицательные:

- часть операций будет требовать больше ceremony даже в локальном профиле;
- нужно поддерживать risk taxonomy, runbooks и approval evidence;
- агенты должны уметь останавливаться, а не только выполнять.

Follow-up:

- связать каждый Stage 1 task с risk class;
- описать формат approval record и audit event;
- определить default scopes для service developer agent и platform operator
  agent;
- добавить conformance check, что agent task содержит permissions,
  validation и rollback/compensation.

## Критерии Приемки

- Каждый agent task содержит scope, permissions, risk class, validation и
  rollback/compensation.
- Агентские действия записываются в audit с risk class и результатом.
- Controlled/risky/destructive действия не выполняются без нужного approval.
- Агент не получает plaintext secrets, если доступ можно выполнить через
  brokered capability.
- Stop conditions из approval matrix являются обязательной частью agent runtime
  и runbook review.

