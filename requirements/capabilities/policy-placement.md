# Capability Contract - Policy And Placement

## Назначение

Policy And Placement решает, можно ли выполнить CloudRING action, где его
разместить и какие ограничения/риски нужно показать до provisioning, migration,
replication, backup, support handoff, billing change, destructive action или
data movement. Этот слой защищает anti-lock-in на уровне jurisdiction, provider
chain, technology choice, trust, cost, capacity, portability и user intent.

Contract описывает продуктовые решения и evidence. Он не выбирает конкретный
policy engine, scheduler или legal interpretation.

## Продуктовая Граница

- Policy принимает решение до действия, а не объясняет нарушение после факта.
- Placement возвращает не только target, но и объяснение: почему allowed,
  preferred, degraded, blocked, approval-required, warning-visible или
  manual-review.
- Policy применима к human, service и agent actions одинаково, но high-impact
  agent actions требуют approval boundary.
- Local/private overlays могут добавлять правила, не форкая core decision shape.
- Marketplace/search/ranking не должен становиться скрытой коммерческой
  манипуляцией: blocked/preferred/degraded/non-portable choices объясняются.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-POLICY-001 | Policy decision должно происходить до provisioning, replication, migration, backup, support handoff или data movement. | Jurisdiction/data residency violation часто невозможно исправить после размещения. | Order/placement/migration plan хранит policy result до action и не запускает action без decision. |
| CR-POLICY-002 | Policy outcome должен использовать стандартные states. | Users, providers и agents должны одинаково понимать решение. | Outcome one of: allowed, blocked, warning-visible, approval-required, manual-review, alternative-proposed, not-applicable. |
| CR-POLICY-003 | Policy decision должен объяснять reason, affected constraint, impact и next action. | Self-service невозможен, если отказ выглядит как техническая ошибка. | Human/agent видит readable summary, structured output, evidence reference и remediation/alternative where relevant. |
| CR-POLICY-004 | Policy должен оценивать jurisdiction и data residency для workload, data, backup, logs, support access и provider chain. | Jurisdiction lock-in - самостоятельный риск, не сводимый к choice of cloud. | Placement rejects/requires approval when data location, support access or provider chain violates profile. |
| CR-POLICY-005 | Policy должен оценивать trust, certification state, freshness, degraded/disputed/revoked status. | Устаревший или деградировавший trust меняет безопасность продукта. | Offer/action availability changes when trust evidence is stale, degraded, disputed or revoked. |
| CR-POLICY-006 | Policy должен оценивать budget, commercial constraints и entitlement state. | Cloud self-service обязан показывать cost consequence before commitment. | Order/scale/migration показывает budget impact и блокирует/эскалирует over-budget или entitlement-violating action. |
| CR-POLICY-007 | Policy должен оценивать capacity, health, SLA и degraded capability state. | Placement не должен скрывать operational risk. | Recommendation marks target as preferred, allowed, degraded, blocked or approval-required with health/capacity reason. |
| CR-POLICY-008 | Policy должен оценивать portability и exit constraints до order. | Anti-lock-in нужно проверять при входе, а не только при выходе. | Buyer/agent видит portability class, exit limitations, export path and non-portable dependencies before confirmation. |
| CR-POLICY-009 | Policy должен различать hard requirement, preference, avoid и forbidden constraints. | Пользователь должен выбирать осознанно, не превращая предпочтения в ложные запреты. | Plan явно разделяет must-have, prefer, avoid, forbidden и показывает impact on options. |
| CR-POLICY-010 | Policy должен поддерживать local/private/jurisdiction overlays без fork core contracts. | Enterprises, regions и private presences нуждаются в локальных правилах. | Local profile adds constraints while preserving common outcome states, evidence and explanation shape. |
| CR-POLICY-011 | Policy должен поддерживать disconnected private/edge evaluation для local actions. | Local autonomy не должна зависеть от global connectivity. | Local presence evaluates cached/local policy, marks freshness/degraded state and limits only actions requiring external proof. |
| CR-POLICY-012 | Policy decision должен храниться рядом с action. | Audit, support и disputes должны объяснять, почему action был allowed или blocked. | Order/provision/migration/support/billing event links policy decision id, correlation id and evidence pointer. |
| CR-POLICY-013 | Policy должен предлагать alternatives, если blocking не финальный. | Self-service должен помогать безопасно продолжить работу. | Blocked/approval-required decision lists compatible alternatives or explains why none exist. |
| CR-POLICY-014 | Policy должен запускать approval для risky changes. | Destructive, financial, trust-changing и data-moving actions требуют owner judgment. | Risky/destructive/financial/trust/data-moving actions have approval record before execution. |
| CR-POLICY-015 | Policy должен быть testable through conformance profiles. | Policy без readiness evidence остается обещанием. | Profiles include scenarios for placement, data movement, cross-provider plan, agent action and local/disconnected mode. |
| CR-POLICY-016 | Policy должен быть explainable для человека и AI-agent. | Human-agent symmetry предотвращает скрытую автоматизацию. | Same decision is available as readable summary and structured output with the same meaning. |
| CR-POLICY-017 | Policy не должен быть скрытым commercial ranking engine. | Ranking bias может стать marketplace lock-in. | Marketplace ranking exposes policy, trust, cost, compatibility, jurisdiction and portability reasons for preferred/hidden offers. |
| CR-POLICY-018 | Policy exceptions должны быть scoped, owned и reviewed. | Exceptions незаметно превращаются в новый стандарт. | Exception includes owner, reason, scope, expiry/review trigger, affected users and compensating controls. |
| CR-POLICY-019 | Policy conflicts должны создавать ADR или explicit owner decision. | Конфликты между cost, jurisdiction, trust и availability нельзя решать привычкой implementation. | Conflict record links requirements, affected domains, rejected options, chosen trade-off and review date. |
| CR-POLICY-020 | Policy evolution должен следовать continuous evolution loop. | Regulations, threats, providers, pricing и product promises меняются. | Policy change links signal, impact analysis, validation, rollout/exception path and user-facing consequence. |

## Evidence

- Policy decision record before action.
- Placement recommendation with allowed/preferred/degraded/blocked reasons.
- Blocked, approval-required and alternative-proposed scenarios.
- Jurisdiction/data residency/provider-chain matrix.
- Trust downgrade availability change.
- Budget/entitlement impact preview.
- Cross-provider compatibility check.
- Local/disconnected policy evaluation record.
- Marketplace ranking explanation showing policy/commercial/trust reasons.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/ADR, если:

- policy outcome unknown for placement, data movement, billing, trust or
  destructive action;
- data movement может произойти before residency/provider-chain decision;
- placement hides source, owner, freshness, provider chain, jurisdiction, trust
  or price reason;
- cross-provider plan содержит unresolved policy conflict;
- platform claims ready while critical placement capability is degraded;
- recommendation cannot explain blocked/preferred/degraded/non-portable choices;
- exception lacks owner, scope, expiry/review trigger or compensating controls;
- agent пытается обойти approval for billing, suspension, data movement or
  destructive operation.

## Non-Goals

- Не давать legal advice для каждой jurisdiction.
- Не выбирать конкретный policy engine, scheduler или optimizer.
- Не обещать universal или bit-for-bit portability.
- Не гарантировать покрытие всех countries, providers или compliance regimes.
- Не скрывать placement, data residency, provider chain, billing или portability
  от пользователя.
- Не превращать global portal в единственного owner of lifecycle.
