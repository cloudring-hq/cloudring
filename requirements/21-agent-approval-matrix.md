# Agent Approval Matrix

AI-агенты являются полноценными операторами CloudRING, но не невидимыми
суперпользователями.
Каждое действие агента должно иметь класс риска, evidence и approval policy.

## Risk Classes

| Class | Примеры | Approval |
|---|---|---|
| `read-only` | Чтение docs, requirements, telemetry, audit, catalog, non-secret configs. | Разрешено в рамках scope агента. |
| `safe-change` | Создать draft requirement, запустить non-destructive validation, обновить docs, создать plan. | Разрешено, если есть validation и audit. |
| `controlled-change` | Изменить non-production config, запустить тестовый deployment, обновить marketplace draft. | Требуется policy approval или pre-approved runbook. |
| `risky-change` | Production/private config change, service upgrade, policy change, provider onboarding, billing rule change. | Требуется explicit approval владельца domain или change window. |
| `destructive` | Delete resource, rotate/revoke keys, suspend participant, purge data, irreversible migration. | Требуется human approval, backup/rollback evidence и dual control там, где применимо. |
| `emergency` | Security containment, stop billing leakage, isolate compromised service. | Может выполняться по emergency policy, но требует immediate audit and retrospective approval. |

## Evidence Requirements

| Class | Required Evidence |
|---|---|
| `read-only` | Goal, scope, accessed resources. |
| `safe-change` | Diff/summary, validation command/result. |
| `controlled-change` | Plan, expected impact, rollback/compensation, validation result. |
| `risky-change` | Plan, impact analysis, policy decision, approval record, rollback, monitoring window. |
| `destructive` | Owner confirmation, backup/export proof, irreversible warning, rollback impossibility note if any. |
| `emergency` | Trigger condition, action taken, containment evidence, follow-up incident/ADR/requirement. |

## Requirements

| ID | Требование | Почему |
|---|---|---|
| CR-APPROVAL-001 | Каждое агентское действие должно быть классифицировано по risk class до выполнения. | Нельзя управлять риском после действия. |
| CR-APPROVAL-002 | Агент не должен сам повышать свой risk class permission. | Иначе approval model бессмысленна. |
| CR-APPROVAL-003 | Risk class должен быть частью audit event. | Последующий review должен понимать контекст риска. |
| CR-APPROVAL-004 | Для risky/destructive действий агент должен сформировать plan и дождаться approval. | Человек или policy owner сохраняет контроль. |
| CR-APPROVAL-005 | Emergency actions должны быть ограничены заранее описанными сценариями. | Emergency не должен быть универсальным обходом governance. |
| CR-APPROVAL-006 | Агент должен использовать brokered secret access вместо прямого просмотра секрета. | Секреты не должны попадать в agent context без необходимости. |
| CR-APPROVAL-007 | Агент должен остановиться, если validation contradicts expected outcome. | Автономность не должна продолжать сломанную цепочку. |
| CR-APPROVAL-008 | Агент должен создавать follow-up requirement/ADR при повторяющейся нештатной ситуации. | Повторяющийся инцидент является источником требований. |

## Default Approval Matrix

| Actor | Read-only | Safe Change | Controlled Change | Risky Change | Destructive | Emergency |
|---|---|---|---|---|---|---|
| Personal agent | Yes | Yes | With pre-approved runbook | Human approval | Human approval | Only predefined |
| Service owner agent | Own service | Own docs/tests | Own non-prod | Owner approval | Owner + platform approval | Only service containment |
| Platform operator agent | Platform telemetry/docs | Platform docs/tests | Non-prod platform | Platform owner approval | Dual approval | Predefined security/SRE |
| Provider agent | Own presence | Own catalog draft | Own non-prod presence | Provider approval | Provider + affected owner approval | Own presence containment |
| Governance agent | Federation metadata | Draft findings | Certification draft | Governance approval | Multi-party approval | Trust compromise playbook |
| Support agent | Support evidence and redacted telemetry | Draft support summary/runbook update | Guided remediation in approved scope | Support owner approval | Support owner + affected owner approval | Incident containment playbook |
| Billing/settlement agent | Usage, invoice and settlement evidence | Draft correction or dispute summary | Non-production billing validation | Billing owner approval | Billing owner + affected owner approval | Stop active billing leakage playbook |
| Certification/marketplace agent | Service card, conformance and trust evidence | Draft certification finding | Marketplace candidate state in review | Certification owner approval | Governance + affected owner approval | Trust downgrade playbook |

## Stop Conditions

Агент обязан остановиться и запросить approval/новое решение, если:

1. Требуется доступ к секрету, которого нет в brokered capability.
2. План затрагивает данные клиента без явного policy allowance.
3. Действие меняет billing, settlement или invoices.
4. Действие может нарушить data residency или jurisdiction policy.
5. Validation показывает drift относительно expected state.
6. Требование или ADR противоречит плану.
7. Rollback невозможен, а approval не получен.
