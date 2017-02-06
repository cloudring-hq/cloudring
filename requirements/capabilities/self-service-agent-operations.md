# Capability Contract - Self-Service And Agent Operations

## Назначение

Self-Service And Agent Operations задает продуктовый стандарт: пользователь,
администратор, provider, ISV/developer и AI-agent должны выполнять сложные
облачные действия как ясный поток: понять intent, увидеть consequences,
получить plan, проверить policy/cost/risk, выполнить или запросить approval,
увидеть validation, rollback/compensation and evidence.

CloudRING должен быть управляемым одним человеком с агентами, но без скрытой
root-власти, магии и непроверяемых automation shortcuts.

## Продуктовая Граница

- Self-service surface exists across UI/API/CLI/Agent API with the same product
  vocabulary and lifecycle truth.
- Agent operation is a first-class audited action with identity, scope, risk
  class, plan, validation and approval policy.
- Every meaningful flow answers: what will change, where, who owns it, what it
  costs, which data/secrets/policies are affected, how success is verified and
  how to stop/rollback/exit.
- Human and agent must see the same product reality, with different affordances
  but not different truth.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-AGOPS-001 | Every self-service flow must start from user intent, not internal implementation. | Users buy outcomes, not infrastructure internals. | Flow names task, service/capability outcome, owner, target context and expected result. |
| CR-AGOPS-002 | Self-service must expose consequence-before-action. | Cloud actions affect money, data, trust and availability. | Before confirmation, user/agent sees cost, policy, jurisdiction, data/secrets, support, SLA, portability and rollback/exit impact. |
| CR-AGOPS-003 | UI/API/CLI/Agent API must share one lifecycle vocabulary. | Agents and humans need the same product truth. | Same states and action names appear across surfaces for service, order, instance, support, billing and operations. |
| CR-AGOPS-004 | User must be able to find, compare, order, change, suspend, remove and export services. | Self-service cloud should not become ticket queue. | Supported service lifecycle actions are available or explicitly blocked with reason and alternative. |
| CR-AGOPS-005 | Admin must self-service install, upgrade, configure and recover presence. | One human with agents must run platform. | Admin flow shows health, capacity, policy violations, upgrade plan, backup/restore and guided remediation. |
| CR-AGOPS-006 | Provider must self-service onboard and operate presence. | CloudRING network cannot scale through manual onboarding. | Provider flow covers certification, capacity/pricing/SLA publication, tenant readiness, support and billing evidence. |
| CR-AGOPS-007 | ISV/developer must self-service publish and improve services. | Ecosystem growth needs low-friction productization. | Developer flow covers template/start, contract validation, conformance, docs, commercial plans, certification feedback and usage/support feedback. |
| CR-AGOPS-008 | Agent identity must be explicit and separate from human/service identity. | Agents must not act as anonymous root. | Agent action records actor, delegated subject, scope, risk class, permissions, approval and audit event. |
| CR-AGOPS-009 | Agent operation must be represented as goal, plan, actions, validations and rollback/compensation. | Autonomous work must be reviewable. | Operation record stores goal, context read, plan, expected impact, executed actions, validation and final summary. |
| CR-AGOPS-010 | Agent must classify risk before action. | Risk cannot be governed after execution. | Every agent action is read-only, safe-change, controlled-change, risky-change, destructive or emergency before execution. |
| CR-AGOPS-011 | Agent cannot self-escalate permissions or risk class. | Approval model would be meaningless. | Permission/risk escalation requires external owner/policy approval and audit. |
| CR-AGOPS-012 | Risky/destructive/financial/trust/data-moving actions require approval. | These actions can harm users or platform trust. | Agent blocks execution until approval record exists; plan remains available for review. |
| CR-AGOPS-013 | Dry-run/simulation must exist for infrastructure and lifecycle changes where possible. | Users need consequences before applying change. | Plan mode shows target diff/impact, policy, cost, risk, validation and rollback without applying action. |
| CR-AGOPS-014 | Agent must read product memory before acting. | Agents should not repeat known mistakes. | Plan references relevant requirements, ADR, runbooks, conformance, policy and current state; absence is a stop condition. |
| CR-AGOPS-015 | Agent context must be bounded and secret-safe. | Helpful autonomy should not leak credentials or tenant data. | Agent receives scoped redacted context and brokered capabilities; raw secrets require explicit exceptional flow. |
| CR-AGOPS-016 | Self-service must show explainable blocked/degraded states. | Denial should help the user proceed safely. | Blocked/degraded action shows reason, affected constraint, owner, alternative, approval path or no-compatible-option explanation. |
| CR-AGOPS-017 | Self-service must support guided remediation. | One human cannot manually diagnose every failure. | Health/problem view proposes runbook, evidence, safe checks, agent-assisted plan and escalation path. |
| CR-AGOPS-018 | Agent must stop when validation contradicts expected outcome. | Autonomy should not push through broken chains. | Operation state becomes blocked/needs-review with evidence and recommended next step. |
| CR-AGOPS-019 | Agent must leave final evidence. | Trust comes from trace, not claims. | Final record says what changed, why, checks run, results, risks, rollback state and follow-up requirements/ADR. |
| CR-AGOPS-020 | Emergency agent actions must be predefined and retrospective. | Emergency cannot be universal governance bypass. | Emergency action references trigger, scope, playbook, containment evidence, immediate audit and retrospective approval/learning. |
| CR-AGOPS-021 | Multi-agent work must have ownership and merge/review boundaries. | Parallel agents can conflict or duplicate work. | Workstream defines agent roles, write scopes, evidence, handoff, review gate and conflict handling. |
| CR-AGOPS-022 | Self-service must support disconnected private/edge operation. | Local control must survive global outage. | Local UI/API/Agent API keeps allowed lifecycle, health, backup/export, incident and emergency flows with freshness/degraded state. |
| CR-AGOPS-023 | Product flows must be beautiful in the sense of simple, calm and consequence-clear. | A powerful platform fails if complexity leaks to users. | Flow avoids unnecessary internal concepts and presents intent, consequence, action and evidence in a compact user-readable path. |
| CR-AGOPS-024 | Self-service actions must be idempotent or explain repeat behavior. | Users and agents retry failed actions. | Action record has operation id/idempotency or explicit duplicate/partial-apply handling. |
| CR-AGOPS-025 | Agent-discovered lessons must update product memory. | Platform must not age into repeated toil. | Repeated failure/incident/ambiguity creates requirement, ADR, runbook, conformance check or explicit no-change rationale. |
| CR-AGOPS-026 | Self-service must preserve party-scoped visibility. | Buyer, provider, ISV and governance need different views without false truth. | Each actor sees relevant state/evidence/actions without over-sharing tenant, commercial or internal topology data. |
| CR-AGOPS-027 | Approval record must include actor, approver, scope, risk, expiry/review, evidence, revocation path and dual-control where needed. | Approval without scope and expiry becomes theater. | Approval artifact is specific, current, owner-backed, reviewable and revocable. |
| CR-AGOPS-028 | Agent plans must respect stage guardrails and future-stage non-goals. | Agents should not turn Stage 6/7 ambitions into blockers for Stage 2/4. | Plan names target stage, required capabilities, explicit non-goals and refuses future-stage dependency as readiness blocker unless ADR accepts it. |
| CR-AGOPS-029 | Manual-review or support-ready bundle is required when self-service cannot finish safely. | A blocked flow should leave the next human/agent with context, not confusion. | Bundle includes intent, current state, blocker, owner, evidence, affected users, policy/approval need, safe next actions and customer-facing status. |
| CR-AGOPS-030 | Risky flows must prove rollback/compensation through evidence or rehearsal where feasible. | Rollback promise should be tested before high-impact automation. | Plan links rollback rehearsal/proof, compensation path or explicit irreversible warning with approval. |
| CR-AGOPS-031 | Agent-run task/plugin/dependency/boilerplate automation must use controlled automation plan and evidence. | An agent that can run local tasks or plugins can mutate code, data, dependencies and trust boundaries. | Agent plan links `CR-EXTAUTO-001..032`, risk class, dry-run, approval, redacted context, forbidden outputs, managed-runner/local-only boundary, validation, rollback/compensation and final evidence. |

## Evidence

- User/admin/provider/ISV journey sample with consequence-before-action.
- Agent operation record with identity, scope, risk, plan, validation and final
  evidence.
- Approval record for risky/destructive/financial/trust/data-moving action.
- Approval artifact with scope, expiry/review and revocation path.
- Dry-run plan for infrastructure/lifecycle change.
- Guided remediation flow.
- Disconnected private/edge self-service evidence.
- Multi-agent workstream record with ownership and review gate.
- Stage guardrail check and future-stage non-goal evidence.
- Manual-review/support-ready bundle.
- Rollback/compensation proof or rehearsal.
- Controlled extension/task automation plan and evidence for agent-run tasks,
  plugins, dependency mutations and boilerplate generation.
- Product memory update from repeated incident or agent-discovered lesson.

## Actor Boundaries

- User can manage own services, exports, billing views and support within owner,
  policy and entitlement scope.
- Admin can manage presence, policy, capacity, upgrades, identity and recovery
  within local/private/provider scope.
- Provider can onboard presence, publish offers, operate support/SLA and see
  scoped billing/quality evidence.
- ISV/developer can publish service candidates, see readiness feedback and manage
  own service lifecycle.
- Agent can investigate, plan, validate and execute only within assigned scope,
  risk class and approval policy.

## Stage Guardrails

- Stage 1 needs developer/local service self-service and safe agent planning.
- Stage 2 needs admin private presence self-service and local agent operations.
- Stage 3 adds private store lifecycle flows.
- Stage 4 adds provider onboarding, tenant operations, support and billing flows.
- Stage 5 adds federation/cross-provider operations with approvals.
- Stage 6 adds global discovery and network self-service without central owner
  takeover.
- Stage 7 adds continuous learning loop from operations back to requirements.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/ADR, если:

- action has no explicit owner, target scope or risk class;
- product memory, policy or conformance needed for action is missing;
- plan touches data, secrets, billing, trust, tenant boundary, jurisdiction or
  destructive lifecycle without approval;
- approval is stale, broad, ownerless or lacks revocation/review path;
- validation contradicts expected outcome or current state is stale/unknown;
- rollback/compensation is missing for risky action;
- agent-run task/plugin/dependency/boilerplate automation lacks controlled
  automation evidence or tries to use local-only execution as managed readiness;
- plan requires future-stage capability as a blocker without accepted ADR;
- self-service flow fails without manual-review/support-ready bundle;
- agent would need raw secret instead of brokered capability;
- multi-agent work has overlapping write scope without coordination;
- blocked/degraded action cannot explain reason or next step.

## Non-Goals

- Не проектировать конкретный UI framework, chatbot, CLI or orchestration tool.
- Не превращать agents в hidden super-users.
- Не заменять человеческое approval там, где оно является product promise.
- Не скрывать complexity ценой потери evidence.
- Не делать global self-service owner of local/private lifecycle.
