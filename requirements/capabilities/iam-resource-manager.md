# Capability Contract - IAM And Resource Manager

## Назначение

IAM And Resource Manager - это слой ownership для CloudRING. Он отвечает на
вопросы: кто владеет ресурсом, кто может действовать, от чьего имени действует
человек, сервис или AI-agent, где проходит граница tenant/provider/federation,
какие quotas/budgets применяются, как подтверждается audit и почему private
presence сохраняет локальный контроль даже при деградации global/federation
слоя.

Этот contract описывает продуктовые обещания, а не конкретный identity provider,
runtime, протокол или database.

## Продуктовая Граница

- IAM управляет identity, roles, scopes, policies, approvals и audit decisions.
- Resource Manager управляет resource identity, owner, lifecycle, metadata,
  quotas, support/billing context и связями с policy/billing/support.
- Секреты не являются обычными атрибутами ресурсов: в product contracts,
  manifests, events и agent context допустимы только secret references или
  brokered capabilities без plaintext secret value.
- Agent identity всегда отдельна от human/service identity и не превращается в
  невидимого super-admin.
- Local/private/edge presence считается полноценной presence, а не демо-режимом:
  она должна иметь локальные identity, ownership, audit и emergency controls.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-IAM-001 | Каждый resource должен иметь стабильный identity, owner и lifecycle state. | Federation, billing, support и audit требуют устойчивых ссылок, которые переживают backend replacement. | Resource record показывает id, type, owner, scope, lifecycle state, policy context и audit links. |
| CR-IAM-002 | Organization, project/space, tenant, service account, human user и agent identity должны быть first-class сущностями. | Human и AI operations требуют явной accountability. | Любое действие можно атрибутировать human, service или agent identity с scope, delegated subject и reason. |
| CR-IAM-003 | Ownership должен быть отделен от runtime implementation. | Платформа должна переживать замену runtime/provider/backend без потери правды о владельце. | Замена runtime/backend не меняет resource identity, owner, billing/support context и audit history. |
| CR-IAM-004 | Resource hierarchy должна поддерживать local, private, provider, federation и global scopes. | CloudRING строится как сеть разных operating boundaries. | Одна модель описывает local dev service, private workload, provider tenant, marketplace order и federation participant. |
| CR-IAM-005 | Permission model должен выражать role, scope, action, resource, purpose и risk class. | Широкие разрешения создают скрытую root-власть и ломают агентные операции. | Access decision объясняет actor, delegated subject, action, resource, scope, purpose, risk class и outcome. |
| CR-IAM-006 | Agent identity не должна схлопываться в generic admin/root. | Агентам нужна bounded autonomy, а не невидимая власть. | Agent action записывает identity, delegated subject, granted scope, risk class, approval policy и audit event; агент не может повышать собственные permissions. |
| CR-IAM-007 | Cross-tenant и cross-participant access требует явной boundary declaration. | Support, federation, settlement и migration могут пересекать ownership boundaries. | Access plan показывает source tenant/participant, target, purpose, data scope, allowed operators и approval. |
| CR-IAM-008 | Quotas, limits и budgets должны привязываться к ownership context. | Resource и cost control являются частью cloud self-service. | User/admin/agent видит quota и budget impact до order, scale, migration или destructive action. |
| CR-IAM-009 | Resource tags/labels/attributes должны обслуживать billing, support, policy, lifecycle и cleanup сценарии. | Metadata нужна для operations, а не для декоративной классификации. | Tags/attributes используются для cost allocation, support ownership, policy selection, lifecycle cleanup и reporting. |
| CR-IAM-010 | Ownership transfer должен быть explicit и audited. | Services, tenants, teams, providers и projects меняются со временем. | Transfer record содержит old owner, new owner, reason, approval, affected resources, billing/support impact и rollback/appeal path where relevant. |
| CR-IAM-011 | Suspension не равна deletion. | Governance, billing dispute или security response не должны уничтожать данные без отдельного решения. | Suspended resource показывает reason, scope, allowed actions, appeal/remediation, export/recovery status и unaffected resources. |
| CR-IAM-012 | Resource deletion требует lifecycle, backup/export, billing, support и policy impact checks. | Deletion может уничтожить data, evidence, invoices и recovery path. | Delete plan показывает owner approval, retention/export/backup status, billing closeout, support handoff, rollback или irreversible warning. |
| CR-IAM-013 | Каждое permission decision должно быть auditable. | Trust, investigation, compliance и agent operations требуют объяснить, почему action allowed/denied. | Audit event содержит actor, delegated subject, resource, action, risk class, policy decision, reason, correlation id и evidence pointer. |
| CR-IAM-014 | IAM должен поддерживать disconnected/local operation для private/edge presence. | Local autonomy - часть anti-lock-in и условие private cloud readiness. | При global/federation outage local presence сохраняет lifecycle, audit, health, emergency control и evaluation of allowed local actions. |
| CR-IAM-015 | Identity federation не должна требовать единого global identity provider. | Identity dependency сама может стать lock-in. | Несколько identity sources могут маппиться в local ownership/audit без передачи ownership центральному провайдеру identity. |
| CR-IAM-016 | Service credentials должны быть scoped to product, resource, environment and purpose. | Product-scoped access снижает blast radius и упрощает audit. | Credential grant показывает service/product, resource, environment, expiration, allowed actions, owner и rotation/revocation status. |
| CR-IAM-017 | IAM evidence должно быть доступно conformance reports без раскрытия secrets. | Readiness нужна proof-based, но отчеты не должны утекать credentials. | Report содержит redacted permissions, scopes, owners, audit decisions и secret references, но не secret values. |
| CR-IAM-018 | IAM должен связываться с support и incident ownership. | Во время incident нужно быстро понять responsible parties и allowed operators. | Resource page/API показывает owner, support owner, escalation path, affected identities, active restrictions и next actions. |

## Evidence

- Resource ownership sample для local/private/provider/federation scope.
- Permission decision record с actor, delegated subject, purpose, risk class и
  outcome.
- Agent action audit, показывающий bounded autonomy и отсутствие self-escalation.
- Ownership transfer record с billing/support impact.
- Suspension/deletion plan с retention/export/appeal evidence.
- Quota/budget impact preview before order/scale/migration.
- Disconnected local authorization evidence для private/edge presence.
- Redacted conformance report, где secret values не раскрываются.

## Stop Conditions

Agent обязан остановиться и запросить owner/approval/ADR, если:

- resource owner, support owner или tenant boundary неизвестны;
- action меняет ownership, data access, billing scope, tenant boundary или
  provider/federation boundary без approval;
- permission decision не может объяснить allowed/denied reason;
- action требует secret value вместо secret reference или brokered capability;
- agent пытается повысить собственные permissions или risk class;
- delete/suspend/migration plan не содержит export, billing, support или appeal
  evidence;
- local/private presence теряет emergency control из-за недоступности global
  слоя;
- planned action противоречит requirement, policy decision, conformance gate или
  active ADR.

## Non-Goals

- Не выбирать конкретный identity provider, protocol или cryptographic stack.
- Не создавать единый global super-admin поверх всех presence.
- Не хранить secrets как обычные resource attributes.
- Не заменять legal ownership contracts.
- Не смешивать marketplace, billing, provisioning и resource entities в одну
  неразличимую модель.
- Не делать private/edge presence неполноценным режимом без локального
  ownership и audit.
