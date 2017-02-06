# Stage 5 - Federation Network

```yaml
id: STAGE-005
status: draft
title: Federation Network
goal: Соединить несколько независимых CloudRING presence в проверяемую сеть catalog, trust, usage, settlement evidence and cross-provider operations without central lock-in.
primary_users:
  - public cloud provider
  - private cloud participant
  - edge operator
  - ISV / seller
  - reseller / integrator
  - federation governance operator
  - service buyer
  - AI federation agent
related_adr:
  - ADR-0003
  - ADR-0004
  - ADR-0007
  - ADR-0008
  - ADR-0009
  - ADR-0011
  - ADR-0014
  - ADR-0015
related_requirements:
  - CR-FED-001..030
  - CR-FEDGOV-001..024
  - CR-SETTLE-001..032
  - CR-ARCH-021..024
  - CR-MKT-001..028
  - CR-SEC-001..006
  - CR-SELF-001..006
  - CR-METRIC-016..020
```

## Назначение

Stage 5 превращает отдельные CloudRING presence в федеративную сеть. На этом
этапе минимум два независимых участника могут обмениваться catalog, trust,
certification, usage, support and settlement evidence, а пользователь может
выбирать сервисы и выполнять хотя бы один cross-provider сценарий с policy,
audit and recovery evidence.

Stage 5 еще не является глобальной сетью CloudRING для всех участников мира.
Global portal at planet scale, universal marketplace discovery, broad
jurisdiction catalog, global dispute institutions and self-evolving global
governance остаются Stage 6/7. Stage 5 доказывает федерацию как работающий
продуктовый slice между несколькими participants.

## Product Promise

Пользователь видит предложения нескольких независимых presence в одном
CloudRING experience, сравнивает price, region, jurisdiction, trust, SLA and
portability, заказывает service where allowed, получает usage visibility,
support context and settlement evidence, and can run cross-provider backup,
replication, migration or DR if the service contract supports it.

Provider/private/edge participants сохраняют local ownership and policy, но
синхронизируют только нужные metadata для catalog, placement, usage, settlement,
support and governance.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-STAGE5-001 | Stage 5 должен соединять минимум два независимых presence. | Федерация невозможна без реального multi-participant сценария. | Два presence обмениваются catalog, trust/certification and usage metadata через federation sync. |
| CR-STAGE5-002 | Participant onboarding должен поддерживать public provider, private cloud, edge, ISV and reseller roles. | Экосистема не должна ограничиваться одним типом участника. | Participant profile показывает role, identity, jurisdiction, support channels, capabilities and lifecycle state. |
| CR-STAGE5-003 | Federation sync должен следовать `ADR-0003`. | Сеть должна работать без полного доверия и ручных интеграций. | Events/snapshots имеют scope, purpose, version, idempotency key, policy result and audit reference. |
| CR-STAGE5-004 | Federation должна поддерживать connected and delayed/disconnected sync modes. | Private/edge не всегда online. | Delayed events sync after reconnect with gaps, conflicts and duplicate-safe behavior visible. |
| CR-STAGE5-005 | Federation must mark stale offers, trust, usage and support states. | Disconnected recovery must not create false confidence. | Buyer/admin/agent sees freshness, degraded, accepted/rejected and disputed states before action. |
| CR-STAGE5-006 | Catalog sync должен показывать offers из нескольких presence without hiding ownership. | Пользователь должен видеть выбор, но не терять прозрачность. | Search results show provider, region, jurisdiction, certification, price, support and portability. |
| CR-STAGE5-007 | Federation marketplace availability должна быть policy-based. | Не все сервисы можно продавать везде. | Offer hidden, blocked or warning-visible according to data residency, compliance, trust and participant policy. |
| CR-STAGE5-008 | Trust and certification state должны синхронизироваться как first-class metadata. | Открытая сеть без качества теряет доверие. | Certification downgrade affects availability and is visible to buyer/admin/agent. |
| CR-STAGE5-009 | Participant data sharing должен быть purpose-scoped. | Федерация не должна требовать раскрытия всей инфраструктуры. | User/admin can see what metadata is shared for catalog, billing, support, audit or dispute. |
| CR-STAGE5-010 | Usage and settlement evidence должны поддерживать cross-participant flow. | Federation economy requires verifiable revenue share. | Usage events can be traced to provider/ISV/reseller shares without duplicate charges and with visible disputed/held amount state. |
| CR-STAGE5-011 | Settlement в Stage 5 должен быть cross-participant, но основан на Stage 4 billing and settlement closure evidence. | Нельзя строить federation settlement без проверяемого usage/invoice/closure ядра. | Settlement record references usage, order, entitlement, invoice/credit, provider-local closure, reconciliation and participant shares. |
| CR-STAGE5-012 | Buyer должен иметь единый usage/billing/support view across involved participants. | Federation complexity не должна становиться проблемой пользователя. | User sees provider chain, responsible parties, usage, invoice/settlement status and support owner. |
| CR-STAGE5-013 | Support handoff должен работать между participants. | Инциденты не должны теряться на границе компаний. | Support request includes participant chain, SLA/support ownership, evidence bundle and handoff state. |
| CR-STAGE5-014 | Federation disputes должны иметь evidence bundle. | Независимые участники будут спорить о usage, SLA, policy and settlement. | Dispute includes events, signatures, policy decisions, usage records, support timeline and correction history. |
| CR-STAGE5-015 | Suspension/revocation must be scoped and non-destructive. | Security/governance action should not destroy customer control. | Suspension reason, scope, appeal path, remediation and unaffected services are visible. |
| CR-STAGE5-016 | Cross-provider operations должны следовать `ADR-0015`. | Настоящее снижение lock-in требует переносимых операций, не только каталога. | Backup/replication/migration/DR plan shows source, target, data scope, policy, risk, validation and rollback. |
| CR-STAGE5-017 | Cross-provider operation must check portability before action. | Не каждый сервис можно мигрировать безопасно. | Operation is compatible, blocked, degraded or marked manual/non-standard based on portability profile. |
| CR-STAGE5-018 | Data residency and jurisdiction policy must be checked before cross-provider data movement. | Исправлять нарушение после перемещения может быть невозможно. | Operation plan rejects or requires approval when target violates policy. |
| CR-STAGE5-019 | Federation must expose alternatives without forcing migration. | Выбор снижает lock-in, но пользователь сохраняет контроль. | Marketplace shows compatible alternatives and migration/replication options with limitations. |
| CR-STAGE5-020 | Federation operations must have agent-safe boundaries. | Cross-provider changes affect data, money and trust. | AI task includes risk_class, scope, participants, approval, validation, audit and rollback/compensation. |
| CR-STAGE5-021 | Cross-provider observability must preserve correlation without over-sharing internals. | Инциденты требуют трассировки, но participants keep boundaries. | User/support sees correlation IDs and status while sensitive topology is redacted or scoped. |
| CR-STAGE5-022 | Federation governance must support participant lifecycle. | Участников нужно подключать, блокировать и выводить из сети управляемо. | Participant states candidate/active/suspended/retired/revoked have consequences and remediation path. |
| CR-STAGE5-023 | Stage 5 must provide conformance profile `stage5-federation-ready`. | Нужна объективная граница готовности сети. | Report shows participant readiness, sync, catalog, settlement evidence, trust, disputes and cross-provider operation checks. |
| CR-STAGE5-024 | Stage 5 не должен требовать global single control plane. | Иначе CloudRING становится централизованным cloud. | Each presence retains local ownership, local control plane and local audit while participating in sync. |
| CR-STAGE5-025 | Stage 5 не должен включать глобальный all-marketplace scale как обязательное условие. | Это Stage 6; Stage 5 доказывает сеть на ограниченном наборе участников. | Minimum readiness requires two or more independent presence, not worldwide catalog coverage. |
| CR-STAGE5-026 | Federation must improve after incidents. | Сеть должна учиться, а не только синхронизироваться. | Repeated federation incident creates requirement/ADR/runbook/conformance follow-up. |

## Acceptance Scenarios

### Scenario A - Two Presence Catalog Sync

Цель: доказать базовую federation network.

Критерии:

- два независимых presence have participant identity and lifecycle state;
- catalog metadata syncs with provider, region, price, certification and policy;
- duplicate/replay does not create duplicate offers;
- user/admin can see source participant and data sharing purpose.

### Scenario B - Cross-Participant Order And Usage Evidence

Цель: доказать federation commercial flow without hiding participants.

Критерии:

- buyer sees provider/ISV/reseller chain before order;
- usage event traces to service/product/resource and participant shares;
- settlement evidence references order, usage, entitlement and invoice/credit;
- dispute can be opened with evidence bundle.

### Scenario C - Disconnected Participant Recovery

Цель: доказать delayed sync.

Критерии:

- participant queues permitted events while disconnected;
- local allowed workloads continue;
- reconnect sync shows gaps, stale data, conflicts and accepted/rejected events;
- no duplicate usage/settlement entries are created.

### Scenario D - Cross-Provider DR Or Migration

Цель: доказать operational anti-lock-in.

Критерии:

- source and target presence selected with policy and compatibility checks;
- plan shows data/metadata/state scope, cost, SLA and rollback/compensation;
- operation outcome is compatible, blocked, degraded or manual/non-standard, not
  falsely promised as universally portable;
- operation produces validation evidence;
- failure leaves known state or compensation plan.

### Scenario E - Suspension And Dispute

Цель: доказать governance without destruction.

Критерии:

- suspension scope is participant/presence/offer/capability/service version;
- reason, appeal path and remediation are visible;
- unrelated services remain available;
- dispute has evidence bundle and correction history.

### Scenario F - Federation Agent Review

Цель: доказать agent-operable federation without unsafe autonomy.

Критерии:

- agent reads requirements, ADR, federation events, policy and telemetry;
- task includes participants, risk_class, approval, validation and rollback;
- billing/settlement/suspension/cross-provider data movement require approval;
- result is stored as audit and human-readable summary.

### Scenario G - Cross-Participant Settlement Closure

Цель: доказать, что disputed federation money is held, explained and resolved
through evidence before settlement.

Критерии:

- closure run links order, entitlement, usage status, invoice draft, participant
  share and dispute evidence;
- reconciliation separates undisputed, disputed, late, corrected and manual
  review amounts;
- buyer/provider/participant/support/governance/agent views are scoped;
- disputed participant share cannot be released by an agent without approval;
- closeout export preserves commercial exit evidence without raw private data.

## Agent Task Seeds

```yaml
id: TASK-STAGE5-001
goal: Описать conformance profile stage5-federation-ready.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/05-federation-network.md
    - requirements/18-federation-governance.md
    - requirements/05-federation-marketplace-billing.md
    - requirements/17-acceptance-criteria.md
  exclude:
    - global Stage 6 portal scale
    - implementation-specific event broker
inputs:
  - CR-STAGE5-023
  - CR-FED-001..030
  - CR-FEDGOV-001..024
expected_outputs:
  - readiness checks
  - federation evidence fields
  - blocking vs warning categories
permissions:
  secrets: none
  destructive_actions: false
validation:
  - every check maps to a requirement or ADR
rollback:
  - disputed checks become draft and link to ADR follow-up
```

```yaml
id: TASK-STAGE5-002
goal: Спроектировать product flow для cross-provider DR/migration operation.
mode: plan
risk_class: safe-change
scope:
  include:
    - requirements/stages/05-federation-network.md
    - requirements/adr/0015-cross-provider-operation-contract.md
    - requirements/adr/0008-data-portability-contract.md
    - requirements/21-agent-approval-matrix.md
  exclude:
    - provider-specific migration commands
inputs:
  - CR-STAGE5-016
  - CR-STAGE5-017
  - CR-STAGE5-018
expected_outputs:
  - user-visible flow states
  - required evidence bundle
  - approval and rollback boundaries
permissions:
  secrets: none
  destructive_actions: false
validation:
  - flow covers policy, portability, evidence and failure states
rollback:
  - supersede via ADR if cross-provider operation model changes
```

## Non-Goals

Stage 5 намеренно не является:

- global CloudRING network at worldwide scale;
- universal public portal for every participant;
- global legal/compliance governance for every jurisdiction;
- mandatory central operator;
- full self-evolving platform;
- guarantee that every service is portable everywhere.

Stage 5 должен доказать, что independent participants can cooperate through
contracts, evidence and policy while retaining local ownership.

## Readiness Gate

Stage 5 считается готовым, когда:

- минимум два независимых presence подключены как participants;
- federation sync exchanges catalog, trust/certification and usage metadata;
- user can compare offers across participants with policy/trust transparency;
- provider/ISV/reseller settlement closure and dispute evidence exists for at
  least one flow;
- support handoff and dispute evidence bundle exist;
- disconnected/delayed sync behavior is demonstrated;
- at least one cross-provider backup/replication/migration/DR scenario is
  planned, policy-checked and validated or explicitly blocked by portability;
- federation governance can suspend scoped entity without data destruction;
- AI federation tasks follow approval matrix;
- conformance report shows `stage5-federation-ready` or concrete blockers.
