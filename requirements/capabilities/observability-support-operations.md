# Capability Contract - Observability Support And Operations

## Назначение

Observability Support And Operations делает CloudRING управляемым одним
человеком с AI-агентами и зрелым для командной эксплуатации. Capability должна
давать единую правду о health, incidents, SLO/SLA, capacity, maintenance,
support ownership, remediation, credits and learning loops across local, private,
public, federated and global contexts.

Contract описывает product operations, not a specific monitoring stack, ticket
system, tracing library or incident tool.

## Продуктовая Граница

- Observability отвечает за health, metrics, logs, traces, events, golden
  signals, capacity and freshness.
- Operations отвечает за plan/apply/validate, rollout/rollback, maintenance,
  idempotency, backpressure, known failure states and runbooks.
- Support отвечает за support ownership, incidents, SLA/SLO, escalation,
  customer communication, credits/refunds evidence and post-incident learning.
- Agent operations can propose, investigate, remediate and validate only within
  risk/approval boundaries.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-OBSOPS-001 | Every service and platform capability must publish health in a standard product shape. | Users and agents need a common health language. | Health shows status, affected capability, scope, freshness, owner, user impact and next actions. |
| CR-OBSOPS-002 | Metrics/logs/traces/events must carry correlation context. | Incidents cross services, queues, providers and agents. | Support view can connect user action, service instance, resource, policy, billing and infrastructure events. |
| CR-OBSOPS-003 | Observability must separate signal, symptom, incident and root cause. | Automated remediation should not confuse noise with truth. | Incident record distinguishes trigger, observed impact, suspected cause, confirmed cause and remediation. |
| CR-OBSOPS-004 | Golden signals must exist for core platform and service classes. | A minimal health baseline is required for readiness. | Capability profile declares latency/traffic/errors/saturation or equivalent signals and user-facing health summary. |
| CR-OBSOPS-005 | Logs and traces must avoid leaking secrets and sensitive tenant data. | Observability must not become a data leak. | Redaction boundary and sensitive-field policy are part of readiness evidence. |
| CR-OBSOPS-006 | Capacity must be visible as product state. | Placement and support depend on capacity reality. | Capacity view shows available/constrained/degraded/blocked/unknown with reason, timestamp and affected offers. |
| CR-OBSOPS-007 | Alerting must be actionable and tied to ownership. | One human with agents cannot survive noisy alerts. | Alert includes owner, affected users, severity, evidence, suggested runbook and suppression/deduplication context. |
| CR-OBSOPS-008 | Incident lifecycle must be explicit. | Support quality depends on repeatable flow. | Incident states include detected, triaged, mitigated, resolved, learning-open and closed with timestamps and owner. |
| CR-OBSOPS-009 | Incident impact must be customer/service/offer aware. | Cloud incidents affect contracts, not only machines. | Incident links service instances, tenants, offers, SLA/SLO, provider chain, billing/credit impact and support owner. |
| CR-OBSOPS-010 | SLA/SLO must be product promises with SLI, target, window, owner and consequence. | Credits and trust require measurable commitments. | SLA/SLO view shows indicator, target, measurement window, owner, exclusions, current burn/violation, evidence and customer impact. |
| CR-OBSOPS-011 | Support request must prefill context. | User should not manually explain the provider chain. | Support case knows service instance, owner, provider/ISV/reseller where relevant, plan, usage, policy, incident and logs summary. |
| CR-OBSOPS-012 | Support handoff must preserve ownership and SLA state. | Federation can lose users between participants. | Handoff record shows from/to owner, reason, SLA clock, evidence shared, data scope and customer-visible state. |
| CR-OBSOPS-013 | Maintenance must be planned, visible and auditable. | Platform changes are product events. | Maintenance notice/record shows affected services, downtime risk, owner, approvals, rollback and validation. |
| CR-OBSOPS-014 | Rollouts and rollbacks must be versioned and observable. | Updates across private/federated contexts are not instantaneous. | Release state shows version, wave, affected users, validation, rollback path and known issues. |
| CR-OBSOPS-015 | Operational actions must be idempotent or declare repeat consequences. | Agents and networks retry. | Runbook/action shows idempotency key/operation id or explicit duplicate behavior. |
| CR-OBSOPS-016 | Queues/gateways must expose backpressure and recovery semantics. | Data loss in lifecycle/usage/support events breaks trust. | Component health shows queue depth, delay, drop policy, retry state, flush/shutdown behavior and recovery evidence. |
| CR-OBSOPS-017 | Stateful services must have operational readiness evidence. | Databases, storage, DNS and queues are cloud foundations. | Readiness covers backup, restore, replication/failover where applicable, upgrade, audit checks and known limitations. |
| CR-OBSOPS-018 | Remediation must use plan/apply/validate for risky operations. | Fixes can be more dangerous than incidents. | Remediation plan shows scope, risk class, policy, approval, expected outcome, rollback/compensation and validation. |
| CR-OBSOPS-019 | Agent investigation must be supported through bounded context. | Agents need enough evidence without excessive access. | Agent receives redacted telemetry, audit, runbook and state summaries, not raw secrets or unrestricted tenant data. |
| CR-OBSOPS-020 | Emergency operations must be predefined and retrospective. | Emergency cannot become governance bypass. | Emergency action references playbook, trigger, actor, scope, containment evidence and retrospective follow-up. |
| CR-OBSOPS-021 | Credits/refunds must link to incident/SLA/support evidence. | Commercial trust depends on operational proof. | Credit/refund request can reference incident timeline, SLA decision, customer impact and settlement context where relevant. |
| CR-OBSOPS-022 | Public status must be honest but scoped. | Users need trust; providers need protectable detail boundaries. | Status page/API shows impact, affected capabilities, regions/jurisdictions where relevant, freshness and remediation state without leaking internal topology. |
| CR-OBSOPS-023 | Post-incident learning must feed requirements/ADR/runbooks/conformance. | Repeated incidents should reduce future toil. | Closed incident either links no-change rationale or creates requirement, ADR, runbook update, conformance check or backlog item. |
| CR-OBSOPS-024 | Operations must support disconnected/private mode. | Private/edge must remain manageable without global portal. | Local presence keeps health, incident, audit, backup/restore and emergency operations locally and syncs allowed summaries later. |
| CR-OBSOPS-025 | Observability retention and export must be explicit. | Investigations, disputes and exit require historical evidence. | Retention policy shows windows, exportability, redaction and party-scoped access. |
| CR-OBSOPS-026 | Operations quality must be measured. | The platform should become easier to operate over time. | Metrics include incident frequency, MTTA/MTTR, alert noise, restore success, automation success, rollback rate and repeated toil signals. |
| CR-OBSOPS-027 | Service, presence, offer, support and billing impact must share one operational state model. | Humans and agents need one product truth during incidents. | Operational state links health, capacity, incidents, support owner, SLA/SLO and billing/credit impact without contradictions. |
| CR-OBSOPS-028 | Runbooks must be agent-readable with preconditions, risk, validation and rollback. | Agents need safe execution boundaries. | Routine operation has preconditions, required evidence, risk class, plan/apply/validate path, rollback/compensation or explicit non-goal. |
| CR-OBSOPS-029 | Recovery evidence must be recurring and freshness-scored. | Old restore proof can create false confidence. | Recovery view shows latest drill/restore, RPO/RTO result, scope, failures, exceptions, freshness and next due date. |
| CR-OBSOPS-030 | Capacity operations must include forecast, saturation, reservation and remediation. | Capacity incidents are product failures, not only resource metrics. | Capacity dashboard shows risk, reservations, forecast, saturation, affected offers and safe human/agent actions. |
| CR-OBSOPS-031 | Stateful audit must produce a normalized evidence bundle. | Raw logs and snapshots are useful for investigation but weak for readiness. | Bundle includes run identity, dependency manifest, sanitized target count, disk/resource summary, replication/failover state, backup freshness, log-class summary, final pass/fail and remediation owner. |
| CR-OBSOPS-032 | Stateful failover drills must be recurring and customer-impact aware. | HA promises fail at the client/write endpoint boundary. | Drill evidence shows node class, failure domain, write/read routing, client reconnect behavior, DNS/service-discovery impact, observed RTO/RPO and rollback or compensation. |
| CR-OBSOPS-033 | Operational runbooks must declare dependency and inventory identity. | A runbook that depends on mutable external roles cannot be trusted by agents. | Runbook evidence includes tool version, dependency lock or approved exception, inventory digest/equivalent identity, expected artifacts and validation gates. |
| CR-OBSOPS-034 | Audit artifacts must become structured operational reports. | Operators need trends, blockers and actions, not folders of raw evidence. | Report summarizes pass/fail, backup age, archive continuity, replication state, disk/resource deltas, top error classes, owner and next actions with links to redacted artifacts. |
| CR-OBSOPS-035 | Audit validation failures must be non-ignorable. | Skipped or unparsable evidence can hide broken recovery. | Stale backup, missing backup metadata, failed replication check, unreachable target, malformed artifact or skipped critical check blocks readiness unless a scoped waiver exists. |
| CR-OBSOPS-036 | Operational evidence retention must be source-safe and party-scoped. | Evidence is needed for support and disputes but can leak topology or credentials. | Retention policy classifies logs, snapshots, grants, IaC state and generated artifacts with redaction, access scope, exportability and deletion/retention windows. |

## Evidence

- Health/status snapshot with owner and user impact.
- Unified operational state record.
- Correlated incident timeline.
- SLA/SLO evidence bundle.
- Support case with prefilled service/provider/usage/context.
- Maintenance/change plan and validation result.
- Agent-readable runbook with preconditions and rollback.
- Rollout/rollback record.
- Stateful restore/failover evidence with freshness score.
- Stateful audit evidence bundle and normalized operational report.
- Capacity forecast/saturation/remediation evidence.
- Emergency action and retrospective record.
- Post-incident requirement/ADR/runbook/conformance update.
- Local/private disconnected operations evidence.

## Stage Guardrails

- Stage 1 needs service-level observability and agent-readable validation.
- Stage 2 needs local/private health, backup/recovery and emergency operations.
- Stage 4 needs provider support, SLA/SLO, maintenance and credit evidence.
- Stage 5 needs cross-participant support handoff and scoped evidence sharing.
- Stage 6 needs global status, incident/trust propagation and dispute-ready
  operational evidence.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/ADR, если:

- incident/support/alert has no owner or affected scope;
- operational states contradict each other across service, presence, offer or
  support views;
- telemetry required for decision is stale, missing or contradictory;
- SLA/SLO has no owner, measurement window or evidence;
- remediation could affect data, billing, trust, tenant boundary or SLA without
  approval;
- support handoff would lose SLA clock, evidence or customer-visible owner;
- emergency action is not covered by predefined policy;
- runbook depends on undocumented human judgment for routine operation;
- logs/traces would expose secrets or sensitive tenant data;
- restore/failover is claimed without current validation evidence;
- stateful audit report ignores stale backup, failed replication, malformed
  artifact or missing restore evidence;
- operational evidence exposes raw topology, grants, logs, IaC state or
  encrypted material outside a redacted evidence boundary;
- repeated incident closes without learning record or explicit no-change reason.

## Non-Goals

- Не выбирать monitoring, logging, tracing, incident or ticketing product.
- Не раскрывать internal topology beyond trust/support need.
- Не обещать zero incidents.
- Не разрешать agents выполнять risky remediation без approval.
- Не считать observability готовой, если она не помогает пользователю понять
  impact and next action.
