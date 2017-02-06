# Stage 7 - Self-Evolving Platform

---
id: STAGE-007
status: draft
title: Self-Evolving Platform
goal: Сделать CloudRING платформой, которая системно превращает опыт, инциденты, новые источники, технологические изменения and ecosystem feedback в требования, ADR, runbooks, conformance checks and safe agent-operated improvements.
---

## Назначение

Stage 7 завершает текущую продуктовую лестницу CloudRING как платформы, которая
не устаревает вместе с конкретным поколением технологий. После Stage 6 CloudRING
имеет глобальную сеть, marketplace, trust, policy, settlement and portability.
Stage 7 добавляет системную способность учиться: сохранять опыт, находить drift,
обновлять контракты, улучшать self-service, безопасно использовать AI-агентов и
делать каждое повторяющееся событие источником улучшения.

Stage 7 не означает полностью автономную самопереписывающуюся систему. Человек
и владельцы domain остаются владельцами миссии, risk appetite, policy,
commercial terms, trust decisions and irreversible changes. AI-агенты помогают
видеть, предлагать, проверять и выполнять безопасные шаги, но не становятся
скрытым root-оператором.

## Product Promise

CloudRING становится living cloud platform: если меняется технология, появляется
новый источник, повторяется инцидент, меняется policy, растет marketplace или
пользователь путается в self-service flow, платформа не просто чинит симптом.
Она создает проверяемый след: что произошло, почему это важно, какое требование
или решение меняется, какие проверки добавлены, кто владеет риском и как
доказать, что следующий раз будет лучше.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-STAGE7-001 | Stage 7 должен реализовать continuous evolution loop from signal to validated learning record. | Платформа должна сохранять опыт, а не только реагировать. | Signal creates triage, linked artifact, validation result and audit/learning record. |
| CR-STAGE7-002 | Evolution loop должен следовать `ADR-0016`. | Self-evolving capability требует явного governance contract. | Signal -> triage -> requirement/ADR/runbook/conformance -> plan -> validation -> audit path is visible. |
| CR-STAGE7-003 | Signal intake должен поддерживать incidents, support cases, source materials, technology changes, security findings, conformance failures and ecosystem feedback. | Опыт приходит из разных каналов, а не только из production incidents. | Signal backlog shows type, source, scope, owner, affected domains, privacy and freshness. |
| CR-STAGE7-004 | New source intake must remain copyright-safe and anonymized. | Requirements должны пережить исчезновение исходников и не раскрывать пилотный контекст. | Source-derived update contains paraphrased product meaning, why, acceptance and no private names/secrets/URLs. |
| CR-STAGE7-005 | Repeated incidents and toil must create follow-up requirements, ADR, runbooks or conformance checks. | Повторение означает системный пробел. | Threshold breach opens linked follow-up or explicit rejection with reason. |
| CR-STAGE7-006 | Technology refresh must preserve product contract unless an ADR changes it. | Технологии меняются быстрее, чем миссия CloudRING. | Refresh analysis shows affected requirements, compatibility, migration, rollback and unchanged why. |
| CR-STAGE7-007 | Deprecated dependency or capability must have migration, containment or sunset story. | Устаревание нельзя переносить на пользователя внезапно. | Deprecation record shows scope, timeline, alternatives, customer impact, support and exit path. |
| CR-STAGE7-008 | Conformance checks must evolve with accepted requirements. | Требование без проверки легко забыть. | Accepted testable requirement links to conformance check, scenario or documented exception. |
| CR-STAGE7-009 | Conformance drift must be visible. | Зеленый статус устаревает, если проверки не покрывают новые риски. | Dashboard shows stale checks, uncovered requirements, expired exceptions and failing profiles. |
| CR-STAGE7-010 | Requirements, ADR, runbooks, incidents, metrics and agent tasks must be queryable as one knowledge graph. | AI-агенты должны понимать контекст решений. | User/agent can trace requirement -> ADR -> runbook -> check -> incident -> metric. |
| CR-STAGE7-011 | AI agents must propose changes with scope, why, risk class, evidence, validation and rollback/compensation. | Автономность без объяснения опасна. | Agent proposal is rejected by gate if any required field is missing. |
| CR-STAGE7-012 | AI agents may autonomously perform read-only and safe-change evolution tasks within policy. | Один человек с агентами должен масштабировать поддержку. | Agent can draft requirement/runbook/check and run non-destructive validation with audit. |
| CR-STAGE7-013 | Controlled/risky/destructive evolution tasks must require approval from the right owner. | Learning loop не должен обходить ownership. | Policy blocks unapproved production, billing, trust, data-moving or destructive change. |
| CR-STAGE7-014 | Emergency actions must create retrospective learning. | Emergency не должен быть обходом governance. | Emergency record creates incident review, follow-up artifact and approval/audit trail. |
| CR-STAGE7-015 | Product simplicity feedback must enter the same evolution loop. | Сложность является дефектом продукта. | Repeated confusion/support friction creates UX requirement, flow change or rejection reason. |
| CR-STAGE7-016 | Marketplace quality feedback must affect certification and conformance. | Ecosystem quality cannot rely on initial review only. | Incidents, vulnerabilities, docs, support and user feedback can update trust/certification state. |
| CR-STAGE7-017 | Federation and global governance changes must be scoped and reversible where possible. | Global network evolution can affect many participants. | Governance proposal shows affected participants, compatibility, appeal, rollback/transition and alternatives. |
| CR-STAGE7-018 | Policy and jurisdiction changes must create impact analysis before enforcement. | Compliance changes can break workloads or contracts. | Policy update shows affected services, regions, customers, deadlines and allowed mitigations. |
| CR-STAGE7-019 | Learning records must preserve rejected paths. | Future agents should not repeat known bad decisions. | Rejected proposal stores reason, evidence, date, owner and conditions for reconsideration. |
| CR-STAGE7-020 | Evolution loop must distinguish product gap, implementation bug, operational incident and one-off exception. | Не каждый сбой требует нового требования, и не каждое требование означает bug. | Triage has classification and resulting artifact type. |
| CR-STAGE7-021 | Customer-impacting evolution must expose communication and migration plan. | Улучшение не должно неожиданно ломать доверие. | Change plan includes affected users, notice, migration, support and rollback/compensation. |
| CR-STAGE7-022 | Experiments must be isolated from accepted product contracts. | Инновации нужны без разрушения стабильности. | Experimental capability has scope, expiry/review, compatibility label and exit path. |
| CR-STAGE7-023 | Ecosystem participants must be able to propose requirements and conformance improvements. | CloudRING grows as a network, not as a closed backlog. | Provider/ISV/customer proposal enters signal intake with attribution and review status. |
| CR-STAGE7-024 | Evolution metrics must measure learning quality and speed. | Self-evolving capability needs evidence, not slogans. | Dashboards include source conversion, ADR closure, conformance drift, refresh lead time and agent defect rate. |
| CR-STAGE7-025 | Agent-operated remediation must validate outcome before closing. | Автоматизация без проверки создает скрытый долг. | Remediation closes only with validation result, remaining risk and follow-up status. |
| CR-STAGE7-026 | Stage 7 must support safe rollback or compensation for evolution changes. | Ошибка улучшения не должна разрушать доверие. | Change record declares rollback, compensation or irreversible-warning with approval. |
| CR-STAGE7-027 | Requirements governance must detect stale decisions. | Старое правильное решение может стать новым lock-in. | ADR/requirement/runbook has review trigger by time, incident, dependency, policy or metric. |
| CR-STAGE7-028 | Learning loop must protect privacy and tenant boundaries. | Сигналы могут содержать sensitive operational data. | Learning record stores redacted/scoped evidence and avoids raw secrets or tenant data exposure. |
| CR-STAGE7-029 | Platform must support independent implementation replacement while preserving open contracts. | Это ядро защиты от technology lock-in. | Runtime/backend replacement plan passes contract, portability and conformance checks. |
| CR-STAGE7-030 | Stage 7 must provide `stage7-self-evolving-ready` conformance profile. | Self-evolving readiness must be testable. | Report covers signal intake, traceability, conformance drift, agent governance, refresh and learning records. |
| CR-STAGE7-031 | Stage 7 must not require global autonomy to be useful. | Private/edge/public participants need local learning too. | Local presence can run source/incident/runbook/conformance loop without always-online global coordination. |
| CR-STAGE7-032 | Human owner must remain accountable for mission, policy and major trade-offs. | Платформа должна усиливать человека, а не стирать ответственность. | Accepted high-impact change records owner, approval, rationale and residual risk. |
| CR-STAGE7-033 | Generated requirements, ADR, runbooks and conformance changes must have lifecycle status and owner. | Автоматически созданные артефакты не должны зависать без ответственности. | Artifact shows draft/proposed/accepted/rejected/superseded/deprecated state, owner, source signal and next review. |
| CR-STAGE7-034 | Evolution item closure must require an observable outcome. | Закрытый сигнал без результата превращает learning loop в иллюзию. | Item closes only with accepted artifact, validation passed, explicit rejection/defer reason or linked owner-approved exception. |
| CR-STAGE7-035 | Conformance evolution must be versioned and rolled out with compatibility impact. | Новая проверка не должна внезапно ломать участников сети. | Check change shows version, reason, affected profiles, migration/deprecation note and enforcement timeline. |
| CR-STAGE7-036 | Failed implementation must not weaken conformance without ADR or conflict note. | Стандарт защищает продукт от удобных shortcuts. | Attempt to relax check requires owner, reason, affected requirement and ADR/conflict reference. |
| CR-STAGE7-037 | Operational lesson must be classified before artifact creation. | Не каждый урок меняет requirement; иногда нужен runbook, guidance or no-change. | Triage class is no-change, implementation guidance, conformance update, requirement change, ADR, runbook or agent task. |
| CR-STAGE7-038 | Repeated fix clusters must trigger learning follow-up. | Repeated fixes reveal a product/system gap even when each fix is small. | Explicit threshold/window for repeated signals in a topic, source class, file category or release window creates requirement/runbook/conformance/test follow-up, fixture/no-test rationale or explicit rejected rationale with owner. |
| CR-STAGE7-039 | Source/history intake must include coverage manifest. | Agents must not overclaim complete analysis from sampled evidence. | Intake records current tree, refs/tags/deleted-path counts, dirty state, generated/vendor exclusions, sampled/history-focused limits and source-safety result. |

## Acceptance Scenarios

### Scenario A - Incident Becomes Lasting Improvement

Цель: доказать, что repeated incident превращается в проверяемое улучшение.

Критерии:

- incident has impact, scope, evidence and owner;
- repeated pattern triggers follow-up requirement/ADR/runbook/conformance draft;
- agent proposes safe plan with validation;
- owner accepts, rejects or defers with reason;
- closure includes status, owner and observable outcome;
- next conformance run proves coverage or shows explicit blocker.

### Scenario B - Technology Generation Refresh

Цель: доказать, что CloudRING может заменить technology layer без потери
product contract.

Критерии:

- refresh proposal states product reason, not only technology preference;
- affected requirements and ADR are listed;
- compatibility, migration, rollback and customer impact are visible;
- conformance validates old and new profiles where applicable;
- if product contract changes, ADR supersedes old decision.

### Scenario C - New Source Intake

Цель: доказать, что новый источник превращается в безопасную agent-readable
память.

Критерии:

- source is registered with type, scope and exclusions;
- analysis extracts what/why/user/scenario/acceptance, not copied text;
- private names, paths, URLs, IPs, secrets and pilot context are removed;
- changes link to existing requirements or create new ones;
- review checklist records anonymization and copyright-safety checks.

### Scenario D - Conformance Drift

Цель: доказать, что проверки не отстают от требований.

Критерии:

- accepted requirement without validation is visible as uncovered;
- stale check has freshness and owner;
- exception has reason, expiry/review and affected scope;
- new/changed check has version, compatibility impact and rollout/migration note;
- agent can propose new check or update;
- readiness report shows drift trend.

### Scenario E - Agent Remediation With Guardrails

Цель: доказать, что AI-агент улучшает систему без невидимой власти.

Критерии:

- agent reads requirements, ADR, runbooks, telemetry and approval matrix;
- plan includes risk_class, scope, actions, validation and rollback;
- approval gates block risky/destructive/data-moving/billing/trust changes;
- execution creates audit and learning record;
- validation failure stops the chain and creates follow-up.

### Scenario F - Ecosystem Proposal

Цель: доказать, что providers, ISV and customers могут развивать сеть без
ручного неформального процесса.

Критерии:

- proposal enters signal intake with proposer role and affected domains;
- conflict with existing requirements creates ADR or rejection reason;
- marketplace/conformance impact is visible;
- accepted proposal updates docs, requirements and checks;
- rejected proposal remains searchable for future agents.

## Agent Task Seeds

```yaml
id: TASK-STAGE7-001
goal: Проанализировать repeated incident и создать learning follow-up.
mode: plan
risk_class: safe-change
scope:
  include:
    - incident evidence
    - affected requirements and ADR
    - runbook and conformance gaps
    - proposed requirement/ADR/check draft
  exclude:
    - production change
    - destructive remediation
inputs:
  requirements:
    - CR-STAGE7-001
    - CR-STAGE7-005
    - CR-STAGE7-010
    - CR-STAGE7-011
    - CR-STAGE7-025
    - CR-STAGE7-033
    - CR-STAGE7-034
    - CR-STAGE7-037
    - CR-STAGE7-038
expected_output:
  - signal classification
  - linked artifacts
  - proposed change set
  - validation plan
  - owner decision needed
rollback:
  - mark proposal rejected/deferred with reason
```

```yaml
id: TASK-STAGE7-002
goal: Оценить technology refresh без разрушения product contract.
mode: plan
risk_class: safe-change
scope:
  include:
    - product reason
    - affected contracts
    - compatibility and migration
    - conformance impact
    - customer/provider/ISV impact
  exclude:
    - vendor-specific implementation plan
    - production migration
inputs:
  requirements:
    - CR-STAGE7-006
    - CR-STAGE7-007
    - CR-STAGE7-022
    - CR-STAGE7-029
expected_output:
  - impact analysis
  - unchanged why list
  - ADR needed/not needed decision
  - validation and rollback plan
rollback:
  - keep old technology profile and record rejected refresh reason
```

```yaml
id: TASK-STAGE7-003
goal: Описать conformance profile stage7-self-evolving-ready.
mode: plan
risk_class: safe-change
scope:
  include:
    - signal intake
    - traceability graph
    - conformance drift
    - AI governance
    - technology refresh
    - privacy/anonymization
    - local/global learning modes
  exclude:
    - autonomous production mutation
inputs:
  requirements:
    - CR-STAGE7-002
    - CR-STAGE7-008
    - CR-STAGE7-009
    - CR-STAGE7-024
    - CR-STAGE7-027
    - CR-STAGE7-028
    - CR-STAGE7-030
    - CR-STAGE7-031
    - CR-STAGE7-035
    - CR-STAGE7-036
expected_output:
  - readiness checklist
  - evidence model
  - drift report
  - blocked conditions
  - required owner decisions
rollback:
  - disputed check remains draft with linked reason
```

## Non-Goals

Stage 7 намеренно не является:

- fully autonomous self-modifying production system;
- replacement for human ownership of mission, policy, money, legal and trust
  decisions;
- permission for agents to bypass approval matrix;
- promise that every incident creates a new feature;
- automatic legal or regulatory decision engine;
- storage of raw source texts, secrets, private names or tenant data in
  requirements;
- reason to break existing contracts because a new technology looks better.

Stage 7 должен сделать CloudRING learning organization in product form: every
important experience can become safer contract, better conformance and less
manual toil.

## Readiness Gate

Stage 7 считается готовым, когда:

- signal intake supports incident/support/source/technology/security/policy/
  marketplace/customer/provider/ISV feedback;
- repeated incident produces linked requirement/ADR/runbook/conformance outcome
  or explicit rejection;
- repeated fix clusters produce follow-up or owner-approved no-change rationale;
- source/history intake includes coverage manifest and analysis limitations;
- technology refresh has product contract impact analysis and validation plan;
- requirements, ADR, runbooks, incidents, checks, metrics and agent tasks are
  traceable as one knowledge graph;
- generated artifacts have lifecycle status, owner and closure criteria;
- accepted testable requirements have validation path or documented exception;
- conformance changes are versioned and cannot be weakened without ADR/conflict
  trail;
- conformance drift, stale decisions and expired exceptions are visible;
- AI agents can draft and validate safe improvements but cannot bypass approval
  for risky/destructive/financial/trust/data-moving changes;
- local presence can run evolution loop without mandatory global connectivity;
- source-derived changes pass anonymization and copyright-safety checks;
- conformance report shows `stage7-self-evolving-ready` or concrete blockers.
