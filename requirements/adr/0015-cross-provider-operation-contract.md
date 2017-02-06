# ADR-0015 - Cross-Provider Operation Contract

```yaml
id: ADR-0015
status: proposed
title: Cross-Provider Operation Contract
context: Stage 5 должен доказать реальную ценность federation через backup, replication, migration, DR, burst capacity and support handoff между независимыми presence.
decision: Cross-provider operations are product contracts with declared source/target, policy, data scope, compatibility, risk class, plan, evidence, validation and rollback/compensation.
supersedes: []
requirements:
  - CR-FED-006..007
  - CR-FEDGOV-011..014
  - CR-OPS-021..028
  - CR-OPS-038..046
  - CR-OBSOPS-031..036
  - CR-INFPROFILE-031
  - CR-SELF-005..006
  - CR-APPROVAL-001..008
  - CR-METRIC-019..020
```

## Контекст

Федерация ценна не только тем, что показывает несколько providers в каталоге.
Главная продуктовая сила CloudRING - возможность переносить, резервировать,
реплицировать, восстанавливать и временно расширять workloads между
независимыми presence, не отдавая контроль одному оператору.

Такие операции затрагивают данные, стоимость, jurisdiction, security, SLA,
support ownership and rollback. Поэтому они не могут быть просто hidden
automation между API провайдеров.

## Решение

Каждая cross-provider operation должна иметь:

- operation type: backup, restore, replication, migration, DR, burst capacity,
  support handoff or validation drill;
- source presence, target presence and involved participants;
- service instance, owner, tenant and support responsibility;
- data/metadata/state scope and secret boundary;
- compatibility and portability profile;
- policy checks: jurisdiction, data residency, encryption, compliance, budget
  and allowed provider classes;
- expected impact: downtime, consistency, cost, support and SLA implications;
- risk class and approval boundary;
- plan, validation result, rollback/compensation or explicit irreversibility;
- evidence bundle and audit timeline.

Operation may be proposed by user, admin, provider, policy or AI-agent, but it
cannot bypass ownership, policy or approval requirements.

## Почему

Without cross-provider operation contract, CloudRING would show alternatives
but not actually reduce lock-in. The user must be able to move, protect and
recover services across participants with clear guarantees, limitations and
evidence.

## Последствия

Положительные:

- anti-lock-in becomes operational, not only catalog-level;
- policy and jurisdiction are checked before data moves;
- support and incident ownership remain visible;
- agents can plan and verify complex federation operations safely.

Отрицательные:

- not every service can be migrated or replicated;
- blocked/manual/non-standard portability must be an honest outcome, not a
  hidden failure;
- operations may need staged validation and explicit user approval;
- consistency and downtime trade-offs must be exposed honestly.

Follow-up:

- define minimal Stage 5 cross-provider scenario;
- connect operation evidence to settlement and support disputes;
- expose portability limitations in marketplace and service instance views;
- add rehearsal/drill requirements for DR and migration.

## Критерии Приемки

- Cross-provider operation cannot start without source, target, scope, policy
  result, risk class and validation plan.
- User sees data location, affected participants, cost/SLA impact and rollback
  story before approval.
- Operation evidence can support audit, support handoff, billing correction and
  dispute review.
- Failed operation leaves service in known state or provides compensation plan.
- A service without compatible portability profile is blocked or marked as
  requiring manual/non-standard migration.
- Cross-provider operation catalog never implies universal portability; it must
  show compatible, blocked, degraded and manual paths separately.
