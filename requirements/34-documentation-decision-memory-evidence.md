# Documentation And Decision Memory Evidence

Этот документ фиксирует требования к документации и decision memory как к
продуктовому слою CloudRING. Его цель - сохранить не тексты старых
документов, а воспроизводимую память: зачем принято решение, кого оно
защищает, какой сценарий оно закрывает, каким evidence это подтверждается и
где проходит граница non-claim.

`CR-DOCMEM-*` не заменяет `CR-DX-*`, `CR-GOV-*`, `CR-CONF-*`,
`CR-SPECTPL-*` или `CR-SPECEX-*`. Это связующий контракт между ними:
требование, ADR/no-ADR rationale, шаблон, синтетический пример, scenario,
conformance gate, source-pass reference, владелец, свежесть и source-safety
должны складываться в одну цепочку, которую новый агент сможет восстановить
без доступа к старому исходному дереву.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-DOCMEM-001 | CloudRING must treat product documentation as an operating contract, not as a passive wiki. | Один человек с агентами сможет развивать платформу только если документация управляет действиями, проверками и handoff. | Docs link to requirements, ADR, scenarios, conformance profiles, owners, freshness and evidence. |
| CR-DOCMEM-002 | Documentation must be organized by audience, task and stage. | Разработчик, оператор, провайдер, support, governance owner and agent ищут разные ответы. | Navigation separates onboarding, reference, operations, governance and source-memory tasks without forcing cross-reading unrelated sections. |
| CR-DOCMEM-003 | Each documented entry point must state the user intent and product promise before mechanisms. | Иначе docs становятся пересказом реализации и стареют вместе с технологией. | Entry pages explain role, goal, supported stage, expected outcome and explicit non-goals. |
| CR-DOCMEM-004 | Onboarding docs must distinguish automated path, manual fallback, prerequisites, supported states and stop conditions. | Local developer friction should be diagnosable without hidden tribal knowledge. | Setup evidence shows happy path, fallback path, supported/unsupported local states, known blockers and owner. |
| CR-DOCMEM-005 | Service lifecycle documentation must cover create, validate, run, observe, document and cleanup as separate product workflows. | A runnable service is not enough; agents need the lifecycle shape and safety boundaries. | Docs link lifecycle steps to manifest, command/action contract, expected state vocabulary and support evidence. |
| CR-DOCMEM-006 | The service manifest contract must be documented as the source of service product truth. | Reimplementation depends on metadata, dependencies, tasks, docs and support semantics, not old generated files. | Manifest docs explain required concepts, examples, validation meaning, secret-reference boundary and portability limits. |
| CR-DOCMEM-007 | Command/action references must be grouped by task area and generated or validated against the actual command surface. | Command docs drift quickly when they are hand-written lists. | Reference includes purpose, inputs, outputs, risk, evidence, failure states and validation status for each command/action group. |
| CR-DOCMEM-008 | Task and task-library documentation must treat operational jobs as first-class product capabilities. | Reusable tasks carry side effects, approvals and evidence expectations. | Task docs describe intent, inputs, outputs, side effects, risk class, owner, timeout/resource boundary and structured result. |
| CR-DOCMEM-009 | Plugin and extension documentation must state trust boundary before usage. | Extension points are executable or embeddable authority boundaries, not just developer convenience. | Plugin docs include interface purpose, permissions, isolation, argument shape, audit, failure cleanup and forbidden actions. |
| CR-DOCMEM-010 | Service templates must include a minimum documentation package. | A generated service without docs cannot be supported or handed to agents. | Template output includes overview, API/contract notes, architecture, runbook, FAQ, known limits, support owner and manifest link. |
| CR-DOCMEM-011 | Showcase and example services must be manifest-backed pattern carriers. | Examples are how developers learn supported integration patterns without reading platform internals. | Each example states what pattern it proves, which requirements it illustrates, what it does not prove and whether docs depth is full or lightweight. |
| CR-DOCMEM-012 | Documentation examples must be synthetic or explicitly sanitized. | Examples are frequently copied by agents and must not carry old private context. | Private marker, endpoint, secret, raw-path, tenant-data and source-copy checks pass before publication. |
| CR-DOCMEM-013 | Best-practice documents must be classified as normative, advisory or exploratory. | Guidance becomes harmful when agents cannot tell whether it is a readiness gate. | Each practice links to conformance when normative, or states advisory/exploratory status and review trigger. |
| CR-DOCMEM-014 | Operational practice docs must translate into runbook, evidence or conformance updates when they describe readiness-critical behavior. | Observability, backup, incident and support lessons should not remain untestable prose. | Practice docs identify required evidence artifact, owner, freshness and stop condition when the behavior is stage-critical. |
| CR-DOCMEM-015 | Architecture decisions must preserve product rationale, not only chosen technology. | Technologies will change; the reason and trade-off must survive. | ADR records context, decision, alternatives, consequences, affected requirements, conformance impact and replacement conditions. |
| CR-DOCMEM-016 | ADR status, supersession and compatibility impact must be explicit. | Agents must not implement an obsolete or partially replaced decision. | ADR has status, supersedes/superseded-by, compatibility class, migration/rollback note and review trigger. |
| CR-DOCMEM-017 | Major documentation-backed decisions must link to requirements, scenarios and conformance. | A decision is not reusable memory until it can be validated. | Decision record links at least one `CR-*`, scenario or explicit scenario gap, conformance gate or explicit no-conformance rationale. |
| CR-DOCMEM-018 | A missing ADR must be an explicit no-ADR rationale, not silence. | Some changes need only docs or runbooks, but the reason must be reviewable. | Decision-memory artifact records `adr_status: linked | not-needed | needed-blocker` with reason and owner. |
| CR-DOCMEM-019 | Technology choices in docs must be expressed as replaceable profiles. | The platform must avoid lock-in to a local runtime, build tool, plugin mechanism or deployment substrate. | Docs separate product promise from current profile, supported alternatives, limitations and migration trigger. |
| CR-DOCMEM-020 | Platform-owned build, packaging and generated-artifact guidance must be versioned. | Service repositories should not each invent hidden build contracts. | Docs show source-of-truth, generated artifact boundary, platform-owned recipe version, freshness and support path. |
| CR-DOCMEM-021 | Platform time, identity, naming and observability conventions must be recorded as cross-cutting decisions. | Inconsistent conventions create hard-to-debug distributed behavior. | Convention docs link to affected requirements, lifecycle actions, evidence format and migration policy. |
| CR-DOCMEM-022 | Feedback from developers, operators, support and agents must enter a triage loop. | Feedback files and plans decay unless they produce a tracked outcome. | Feedback item resolves as requirement, ADR, docs/runbook, conformance, scenario, no-change rationale or rejected-with-reason. |
| CR-DOCMEM-023 | Documentation freshness and ownership must be visible. | Stale docs can create false readiness claims. | Critical docs and decision-memory artifacts have owner, last review, freshness state, review trigger and stale behavior. |
| CR-DOCMEM-024 | Documentation must be usable in private, disconnected and source-missing modes where the stage promise requires it. | CloudRING should not depend on one old repository, one hosted docs portal or one jurisdiction. | Docs package can be exported with requirements, templates, examples and safe evidence references for offline review. |
| CR-DOCMEM-025 | Support and agent handoff docs must state allowed actions, forbidden actions and evidence needed. | Agents need a safe continuation boundary, not just narrative context. | Handoff includes risk class, approvals, validation needed, non-claims, remaining gaps and escalation role. |
| CR-DOCMEM-026 | Documentation completeness must be a readiness blocker for critical flows. | A critical flow that only works through hidden knowledge is not product-ready. | Conformance marks missing docs/runbook/decision-memory evidence as blocker or scoped warning according to criticality. |
| CR-DOCMEM-027 | Documentation publication evidence must include navigation, links and source-safety results. | A docs portal can look complete while links are broken or unsafe examples leak. | Publication report includes nav coverage, link check, private marker scan, strict secret scan, source-copy review and broken-link blockers. |
| CR-DOCMEM-028 | Visual assets and diagrams must have safe provenance and accessible meaning. | Diagrams often reveal topology or private names and can become unreviewed source memory. | Asset record states purpose, source/provenance, redaction state, alt text or text summary, owner and replacement trigger. |
| CR-DOCMEM-029 | Terminology must be consistent across docs, requirements, ADR, scenarios and conformance. | Agents fail when the same concept has unrelated names in different artifacts. | Glossary or term mapping links product terms, aliases, deprecated terms and compatibility notes. |
| CR-DOCMEM-030 | Decision-memory evidence must be a reusable artifact with canonical links. | Scattered prose cannot prove that a requirement is reimplementation-ready. | Artifact links requirement refs, ADR/no-ADR rationale, template, synthetic example, scenario, conformance gate, source pass, owner, freshness and non-claims. |
| CR-DOCMEM-031 | Source passes must become product memory without copying source shape. | The goal is to keep the experience and why, not private source text or old implementation. | Source-derived decision-memory artifact records source class, method, counts, product lessons, outputs, limitations and validation summary without raw paths or snippets. |
| CR-DOCMEM-032 | Decision-memory claims must be party-scoped and non-claim explicit. | A docs-backed lesson may prove local developer readiness but not provider, federation or production readiness. | Evidence states scope, stage, affected roles, what is proven, what is not proven and which future evidence is needed. |

## Evidence Contract

Documentation and decision-memory evidence is complete only when the chain is
closed:

1. Product requirement or source-derived lesson exists.
2. ADR is linked or a no-ADR rationale is recorded.
3. Reusable template exists or not-needed rationale is recorded.
4. Synthetic example exists or gap is tracked.
5. Scenario fixture validates the role journey or gap is tracked.
6. Conformance gate names the evidence and stop condition.
7. Source pass or coverage reference records scope and non-claims.
8. Owner, freshness and source-safety status are visible.

## Source-Safety Rules

- Do not copy raw documentation text, commands, source paths, private endpoints,
  hostnames, tenant data, commit subjects, screenshots with private context or
  implementation-specific secrets.
- Keep old technology names as replaceable profiles only when the product
  reason requires them.
- Prefer synthetic examples and role names.
- If source meaning is unclear because of encoding damage, mark the requirement
  as inferred from structure and require owner review.
