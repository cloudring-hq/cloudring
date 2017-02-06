# Capability Contract - Infrastructure Capability Profiles

## Назначение

Infrastructure Capability Profiles описывают инфраструктуру CloudRING как
заменяемые продуктовые capabilities: compute, network, storage, backup,
observability, image/template supply, private/edge presence and cross-cloud
connectivity. Цель - не привязать CloudRING к одному backend, гипервизору,
runtime, public provider или hardware class, а дать пользователю и агенту
понятный contract: что площадка умеет, где ограничения, как это проверено и
какой exit path есть.

Contract описывает product outcome and evidence. Он не выбирает конкретную
виртуализацию, orchestrator, network stack, storage engine или hardware vendor.

## Продуктовая Граница

- Infrastructure profile - machine-readable product description of a presence
  capability: capacity, limits, health, locality, jurisdiction, lifecycle,
  maintenance, support, portability and conformance.
- Presence может быть local, single-host, private, edge, public provider,
  federation participant или global-facing provider.
- Infrastructure profile не равен implementation inventory: пользователь должен
  видеть product capabilities and constraints, а не внутреннюю topology.
- Backend replacement must preserve resource ownership, policy, billing/support
  context and user-visible service promise.
- Edge/private/disconnected modes are first-class, not reduced public cloud.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-INFPROFILE-001 | Каждая presence должна публиковать versioned infrastructure capability profile. | Placement, conformance, support and agents need a shared truth about infrastructure. | Profile lists version, capability class, scope, capacity, limits, health, lifecycle, jurisdiction, support owner and evidence freshness. |
| CR-INFPROFILE-002 | Capability profile must separate product capability from backend implementation. | Backend technology will change; product promise must survive. | User/agent sees compute/network/storage/backup capabilities and limitations; backend swap does not require rewriting service/order contract unless limitation is declared. |
| CR-INFPROFILE-003 | Compute capability must declare workload classes and constraints. | Workloads differ by latency, isolation, performance, lifecycle and cost needs. | Profile shows supported workload classes, quotas, scaling limits, isolation level, maintenance expectations and unsupported cases. |
| CR-INFPROFILE-004 | Network capability must declare connectivity, routing, exposure and policy boundaries. | Network is a common hidden lock-in and compliance risk. | Profile shows private/public/cross-cloud connectivity, ingress/egress boundaries, latency class, encryption expectation and jurisdiction-relevant routing notes. |
| CR-INFPROFILE-005 | Storage capability must declare persistence, replication, backup, restore and locality promises. | Data lock-in usually lives in storage and state. | Profile shows durability class, location, backup/restore support, export path, consistency limits and unsupported operations. |
| CR-INFPROFILE-006 | Backup capability must include restore evidence, not only backup existence. | Unverified backup is not a product capability. | Readiness evidence includes latest restore test or explicit limited-scope warning. |
| CR-INFPROFILE-007 | Observability capability must be declared for platform and hosted services. | One human with agents needs trustworthy health context. | Profile shows metrics/logs/traces/events support, retention limits, redaction boundary and agent-readable health endpoints. |
| CR-INFPROFILE-008 | Image/template supply must be a governed capability. | Reproducible hosts/images reduce drift and incident recovery time. | Image/template profile shows version, purpose, supported environments, immutable artifact identity, dependency/base image freshness, hardening state, cleanup status, bootstrap readiness, diagnostic boundary and rollback/deprecation path. |
| CR-INFPROFILE-009 | Single-host profile must be supported as learning/dev/small scenario with clear limits. | Small start should not be a dead end. | Single-host readiness shows included capabilities, excluded production promises and upgrade path to multi-node/private profile. |
| CR-INFPROFILE-010 | Multi-node private profile must prove autonomy and production readiness. | Private cloud must be a finished product, not managed demo. | Profile shows local control plane, IAM/RM, policy, monitoring, backup/recovery, upgrade path and emergency control. |
| CR-INFPROFILE-011 | Edge profile must declare connected and disconnected behavior. | Edge has latency, resource and connectivity constraints. | Profile shows local control capabilities, delayed sync, cache/freshness state, allowed local actions and sync limitations. |
| CR-INFPROFILE-012 | Infrastructure profile must expose capacity, reservation, saturation and failure-domain state. | Placement should not hide overload or partial failure. | Capacity shows free, used, reserved, saturated, degraded, blocked or unknown state with timestamp, forecast and affected failure domain/capability. |
| CR-INFPROFILE-013 | Infrastructure changes must use plan/apply/validate lifecycle. | Infrastructure mutation is risky and must be explainable. | Upgrade/scale/reconfigure plan shows impact, policy, affected services, rollback/compensation and validation evidence. |
| CR-INFPROFILE-014 | Maintenance windows and disruption expectations must be visible. | Users and agents need to plan around downtime and SLA risk. | Profile/action plan shows expected downtime, no-downtime claim, affected users, communication and rollback path. |
| CR-INFPROFILE-015 | Provider/hardware/runtime-specific dependencies must be marked. | Hidden dependencies become technology lock-in. | Profile marks portable, replaceable, provider-specific, hardware-specific and manual-migration dependencies. |
| CR-INFPROFILE-016 | Infrastructure profile must support policy-based placement. | Region, jurisdiction, trust, cost and data residency are infrastructure facts. | Placement policy can evaluate profile attributes before provisioning or data movement. |
| CR-INFPROFILE-017 | Cross-cloud connectivity must be explicit and policy-aware. | Federation without transparent connectivity can leak data or create surprise cost. | Profile shows available routes, participants, encryption expectation, latency/cost class, jurisdiction constraints and blocked routes. |
| CR-INFPROFILE-018 | Infrastructure must provide emergency access boundaries. | Recovery sometimes needs low-level access, but it must be governed. | Profile shows emergency control options, approval class, audit requirements and secrets boundary without exposing credentials. |
| CR-INFPROFILE-019 | Infrastructure events must be auditable and tied to resources. | Support, billing, compliance and agents need evidence. | Provision/change/failure/recovery events link resource, owner, policy decision, actor and correlation id. |
| CR-INFPROFILE-020 | Infrastructure profile must support customer exit and provider exit. | Anti-lock-in fails if infrastructure cannot be left. | Profile describes export, backup restore, migration target compatibility, dependency loss and closure evidence. |
| CR-INFPROFILE-021 | Private subscriptions/entitlements must not disable basic local operation. | Commercial model must not become a local kill switch. | Expired/degraded entitlement preserves local control, export, backup, emergency operations and clear support/update limits. |
| CR-INFPROFILE-022 | Conformance evidence must be profile-specific and stage-aware. | One readiness label cannot cover all infrastructure contexts. | Stage 2/4/5/6 readiness reports reference relevant capability profile checks and explicit non-goals. |
| CR-INFPROFILE-023 | Agent-readable infrastructure state must be bounded and non-secret. | Agents need state, not unrestricted access. | Agent context includes redacted health/capacity/config summaries and brokered actions, not raw secrets or uncontrolled shell access. |
| CR-INFPROFILE-024 | Infrastructure evolution must not break existing product promises silently. | Backend replacement and platform upgrades can degrade users. | Significant profile change links affected services, user impact, migration/rollback path, ADR if needed and validation evidence. |
| CR-INFPROFILE-025 | Profile capability states must include supported, degraded, unsupported, blocked and manual-review/manual-migration where relevant. | Honest readiness is better than false compatibility. | Capability matrix is visible in UI/API/CLI/Agent API and degraded critical capability cannot be shown as ready. |
| CR-INFPROFILE-026 | Profile health must link capability, dependency, freshness, incidents and next action. | Health without cause/action is weak operational evidence. | Health view shows state, dependency, stale/degraded reason, incident link, owner and recommended next action. |
| CR-INFPROFILE-027 | Federation publication must share scoped metadata, not full infrastructure truth. | Federation should not require over-disclosure of internal topology. | Published profile metadata has purpose, scope, owner, freshness, policy decision and redaction boundary. |
| CR-INFPROFILE-028 | Backend deprecation must include migration, rollback/compensation and alternative profile. | Old backend must not become a trap. | Deprecation record links affected profiles, services, users, timeline, exit path, alternative profile and validation evidence. |
| CR-INFPROFILE-029 | Profile lifecycle must be versioned, supersedable and compatibility-aware. | Agents and providers need to know which promises changed. | Profile change shows previous/new version, compatibility impact, superseded profile, affected users and rollout/rollback path. |
| CR-INFPROFILE-030 | Agents must inspect, plan, dry-run and validate infrastructure profile changes within approval boundaries. | One human with agents needs safe infrastructure operations. | Agent audit shows scope, risk class, preflight/dry-run, validation result and approval where needed. |
| CR-INFPROFILE-031 | Stateful infrastructure profile must declare topology and endpoint ownership. | Databases, DNS, queues and storage need stronger proof than generic compute health. | Profile shows node classes, quorum/failure domains, write/read endpoint ownership, replication mode, RPO/RTO, backup/restore evidence, failover drill freshness and unsupported/manual-review states. |
| CR-INFPROFILE-032 | Presence activation must update the infrastructure capability profile. | Bootstrap success must become product state, not remain a local command result. | Activation evidence updates profile version, capability states, capacity, degraded/unsupported flags, local autonomy, diagnostics, rollback and conformance refs. |

## Evidence

- Presence capability profile snapshot.
- Presence bootstrap activation evidence and profile update record.
- Versioned profile lifecycle and capability state matrix.
- Capacity/degraded state report.
- Backup and restore evidence.
- Stateful topology, endpoint ownership and failover drill evidence.
- Single-host to multi-node upgrade path evidence.
- Private/edge disconnected operation evidence.
- Image/template readiness and cleanup report.
- Base OS image factory readiness evidence.
- Cross-cloud connectivity policy decision.
- Scoped federation metadata publication record.
- Infrastructure change plan/apply/validate record.
- Backend deprecation and alternative profile evidence.
- Customer/provider exit evidence.

## Stage Guardrails

- Stage 1 may use local runtime profiles, but must not pretend to be production
  private/public infrastructure.
- Stage 2 requires autonomous private presence profile with local control,
  backup/recovery and policy-aware infrastructure.
- Stage 4 requires provider-local infrastructure profile with tenant-facing
  capacity, support and billing evidence.
- Stage 5 adds cross-presence connectivity and federation-compatible profile
  exchange.
- Stage 6 requires global discovery to compare profiles without centralizing
  ownership of infrastructure.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/ADR, если:

- infrastructure profile lacks owner, scope, capability class or freshness;
- presence activation is claimed without trusted artifact/config/preflight,
  diagnostics, rollback or profile update evidence;
- degraded/unsupported/manual capability is presented as fully ready;
- plan depends on hidden backend/provider-specific behavior not declared in
  profile;
- federation exchange requires full internal topology rather than scoped metadata;
- data movement or cross-cloud route lacks policy decision;
- backup exists but restore evidence is missing for production/stateful scope;
- stateful profile lacks node classes, endpoint ownership, RPO/RTO or failover
  drill evidence;
- local/private emergency control would be lost;
- capacity/degraded state is unknown for critical placement;
- change plan cannot explain impact, rollback/compensation or validation;
- backend deprecation has no alternative profile, exit path or validation;
- agent would need raw secret or uncontrolled privileged access.

## Non-Goals

- Не выбирать конкретный runtime, hypervisor, orchestrator, network stack,
  storage engine or hardware vendor.
- Не обещать одинаковые capabilities for every presence.
- Не превращать private/edge в урезанную копию public cloud.
- Не раскрывать internal topology больше, чем нужно для trust, policy and
  support.
- Не считать backup готовым без проверяемого restore path.
