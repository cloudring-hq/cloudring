# Stage 0 - Requirements And Agent Memory

---
id: STAGE-000
status: draft
title: Requirements And Agent Memory
goal: Создать живую, обезличенную, agent-readable память CloudRING, которая сохраняет продуктовый опыт из источников и позволяет строить платформу заново без копирования исходных текстов.
---

## Назначение

Stage 0 является фундаментом CloudRING: до реализации платформы должна
существовать безопасная и расширяемая память продукта. Она хранит миссию,
source analysis, requirements, ADR, domain model, stages, conformance profiles,
agent rules and review checks.

Stage 0 должен доказать, что опыт можно извлечь из источников полностью,
сохранить в product requirements, обезличить, сделать понятным AI-агентам и
подготовить к будущей реализации без зависимости от старых исходных текстов,
конкретной компании, конкретного runtime or private operational context.

## Product Promise

Если завтра исходные репозитории, заметки или PDF исчезнут, CloudRING все еще
можно будет проектировать и строить по `requirements`: что нужно сделать, для
кого, зачем, где границы, какие решения приняты, как проверять готовность и где
агент обязан остановиться.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-STAGE0-001 | Requirements folder должен быть главным product memory artifact. | Без памяти опыт снова растворится в коде и историях. | README explains purpose, structure, format and rules for agents. |
| CR-STAGE0-002 | Source analysis должен фиксировать scope, signals and exclusions. | Полнота анализа должна быть проверяема. | Each source has anonymized signal, extracted meaning and explicit exclusions if any. |
| CR-STAGE0-003 | Requirements must be written as what/why/user/acceptance, not implementation steps. | Технологии меняются, продуктовый смысл живет дольше. | New requirement can be understood without old source code. |
| CR-STAGE0-004 | Internal company names, pilot context, secrets, URLs, IPs and private paths must be excluded. | Requirements must be safe to reuse and share. | Forbidden scan returns no matches outside review checklist. |
| CR-STAGE0-005 | Source-derived content must be paraphrased and copyright-safe. | Память должна сохранять смысл, а не копии источников. | No long source excerpts; source signals are summarized product lessons. |
| CR-STAGE0-006 | Requirements must be in Russian and understandable by AI agents. | User requested Russian agent-readable specifications. | Documents use stable IDs, tables, clear why and acceptance criteria. |
| CR-STAGE0-007 | Architecture decisions must be separated into ADR files. | Trade-offs need durable context and consequences. | Current ADR list links decisions with requirements and follow-up. |
| CR-STAGE0-008 | Product stages must define finished increments. | CloudRING cannot wait for a final version to become useful. | Stage list shows purpose, value and readiness for every stage. |
| CR-STAGE0-009 | Conformance profiles must define evidence-based readiness. | "Готово" должно быть проверяемым. | Stage readiness profiles exist and link to gates, blockers and evidence. |
| CR-STAGE0-010 | Domain model must preserve key concepts and boundaries. | Agents need shared vocabulary before implementation. | Bounded contexts, entities, relationships and events are documented. |
| CR-STAGE0-011 | Agent task format must define scope, validation and rollback/compensation. | Multi-agent work must be safe and reviewable. | Agent specification includes task object and quality bar. |
| CR-STAGE0-012 | Approval matrix must define agent risk boundaries. | Agents must not become invisible superusers. | Risk classes and stop conditions exist for agent actions. |
| CR-STAGE0-013 | Product capability map must connect stages, capabilities and readiness. | Agents need an implementation-independent map of what to build. | Capability map links purpose, users, dependencies, stage and profile. |
| CR-STAGE0-014 | Agent workstream backlog must organize future work without choosing technologies. | Future implementation needs product workstreams, not vendor-specific instructions. | Workstreams link outcomes, requirements, ADR, conformance and stop conditions. |
| CR-STAGE0-015 | Requirements governance must define change, conflict and source intake rules. | Product memory must evolve without becoming chaotic. | Governance file defines statuses, conflict order, quality gates and review checklist. |
| CR-STAGE0-016 | Review checklist must include anonymization, links and ID checks. | Regression in requirements safety must be caught early. | Checklist commands exist for forbidden terms, secrets, links and ID consistency. |
| CR-STAGE0-017 | Traceability map must preserve legacy lessons without exposing legacy identity. | Future agents need why without unsafe source details. | Traceability map links anonymized source signals to requirement groups. |
| CR-STAGE0-018 | Stage 0 must be useful without implementation repository. | Requirements should outlive code. | A new agent can orient from README, stages, ADR, domain model and conformance only. |
| CR-STAGE0-019 | Stage 0 must not freeze technology choices. | The product must survive evolution. | Requirements focus on contracts, outcomes and evidence instead of mandatory stack. |
| CR-STAGE0-020 | Stage 0 must provide `stage0-requirements-memory-ready` readiness profile. | Product memory itself needs a readiness gate. | Conformance report can prove structure, safety, links, IDs and agent usability. |
| CR-STAGE0-021 | Stage 0 must include source coverage and completion audit. | Requirements memory must be honest about what is proven and what remains unproven. | Coverage manifest lists source classes, counts, methods, exclusions, limitations, current completion audit and next exhaustive passes. |

## Acceptance Scenarios

### Scenario A - New Agent Orientation

Цель: доказать, что AI-агент может понять CloudRING без внешнего контекста.

Критерии:

- agent reads README, vision, architecture, stages and domain model;
- agent can identify mission, roles, stage path and core trade-offs;
- agent can find relevant requirements by domain and stage;
- agent can name stop conditions before proposing work.

### Scenario B - New Source Intake

Цель: доказать, что новый источник можно добавить безопасно.

Критерии:

- source is registered with type, scope and exclusions;
- extracted content is paraphrased into what/why/user/acceptance;
- forbidden names, secrets, URLs, IPs and direct snippets are removed;
- changes link to requirements or ADR.

### Scenario C - Requirements Review

Цель: доказать, что Stage 0 can be audited.

Критерии:

- markdown links resolve;
- CR IDs are defined and referenced consistently;
- forbidden internal terms scan passes;
- secret scan shows only product-level secret-handling requirements;
- conformance profile reports blockers and next actions.

## Agent Task Seeds

```yaml
id: TASK-STAGE0-001
goal: Проверить readiness папки requirements как product memory.
mode: verify
risk_class: read-only
scope:
  include:
    - requirements README
    - source analysis
    - stages
    - ADR
    - conformance
    - governance
    - source coverage manifest
  exclude:
    - implementation source code
inputs:
  requirements:
    - CR-STAGE0-001
    - CR-STAGE0-004
    - CR-STAGE0-009
    - CR-STAGE0-016
    - CR-STAGE0-020
    - CR-STAGE0-021
expected_output:
  - readiness report
  - blockers
  - missing links or IDs
  - anonymization findings
  - coverage and completion-audit findings
rollback:
  - no mutation; create follow-up requirement if gap found
```

```yaml
id: TASK-STAGE0-002
goal: Принять новый источник в requirements без unsafe copying.
mode: plan
risk_class: safe-change
scope:
  include:
    - source registration
    - product lesson extraction
    - anonymization
    - requirement/ADR mapping
    - coverage manifest update
  exclude:
    - direct source copy
    - secret or private path persistence
inputs:
  requirements:
    - CR-STAGE0-002
    - CR-STAGE0-003
    - CR-STAGE0-004
    - CR-STAGE0-005
    - CR-GOV-001
    - CR-GOV-004
    - CR-GOV-023
    - CR-GOV-024
expected_output:
  - source analysis update
  - new or changed requirement draft
  - checks performed
  - coverage mode and exclusions
  - unresolved conflicts
rollback:
  - revert unsafe draft by superseding/rejected note, not by losing the lesson
```

## Non-Goals

Stage 0 intentionally does not include:

- implementation code;
- runtime selection;
- deployment scripts;
- product UI;
- provider operations;
- legal advice;
- copying old source text into requirements;
- exposing private operational names, URLs, IPs, credentials or pilot context.

Stage 0 is complete when the product memory is safe, navigable, extensible,
agent-readable and ready to guide Stage 1 implementation.

## Readiness Gate

Stage 0 считается готовым, когда:

- README explains structure and agent rules;
- source analysis and traceability map exist;
- product requirements have IDs, why and acceptance criteria;
- ADR, stages, domain model, conformance and governance are linked;
- forbidden internal terms and secret scans pass;
- markdown links resolve;
- single CR ID references are defined;
- review checklist can be run by an agent;
- conformance report shows `stage0-requirements-memory-ready` or concrete blockers.
