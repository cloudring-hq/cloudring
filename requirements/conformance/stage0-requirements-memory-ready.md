# Conformance Profile - Stage 0 Requirements Memory Ready

---
profile_id: stage0-requirements-memory-ready
profile_version: 0.1
stage: 0
stage_file: ../stages/00-requirements-and-agent-memory.md
---

## Purpose

Доказать, что requirements folder является безопасной, расширяемой,
agent-readable product memory for CloudRING before implementation starts.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE0-001 | README explains purpose, structure and agent rules. | New agent must orient without previous conversation. | README links core documents and ID prefixes. | Agent cannot find stage/ADR/governance/conformance entrypoints. |
| CONF-STAGE0-002 | Source analysis is anonymized and scoped. | Product memory must preserve lessons, not unsafe context. | Source analysis lists signals, scope and exclusions without private names/secrets. | Source analysis contains pilot identity, secrets, private URLs/IPs or direct copy. |
| CONF-STAGE0-003 | Requirements have stable IDs, why and acceptance. | Agents need testable product meaning. | CR IDs are defined and referenced consistently; requirements explain reason. | Requirement group lacks IDs or product why. |
| CONF-STAGE0-004 | ADR backlog and ADR files exist for key trade-offs. | Architecture choices need durable context. | ADR index links current decision files and related requirements. | Major trade-off exists only as prose without ADR. |
| CONF-STAGE0-005 | Stage ladder defines finished increments. | Each phase must be useful and extendable. | Stage 0-7 docs or stage index describe purpose, product value and readiness. | Stage path requires final platform before any useful product. |
| CONF-STAGE0-006 | Conformance framework and profiles exist. | Readiness must be evidence-based. | `22-conformance-readiness-profiles.md` and conformance profiles are linked. | No objective readiness profile for stages. |
| CONF-STAGE0-007 | Domain model and capability map preserve shared vocabulary. | Agents need common nouns before building. | Domain model and capability map link entities, capabilities and dependencies. | Same concept has conflicting names without decision. |
| CONF-STAGE0-008 | Agent governance exists. | Multi-agent work must be bounded. | Agent task format, approval matrix and stop conditions exist. | Agent can act without risk class, scope or validation. |
| CONF-STAGE0-009 | Safety scans pass. | Requirements must be shareable and reusable. | Forbidden-name/path/IP/secret scans pass, with product-level secret mentions only. | Private names, credentials, IPs or unsafe source snippets appear. |
| CONF-STAGE0-010 | Workstream backlog connects future work to requirements and conformance. | Future agents need product workstreams, not guesses. | Workstreams link outcome, stage, requirements, ADR, conformance and stop conditions. | Workstream cannot name user, outcome or readiness profile. |
| CONF-STAGE0-011 | Source coverage and completion audit exist. | New agents must know what was actually analyzed and what remains unproven. | Coverage manifest lists file/ref/history scope, exclusions, limitations, current completion audit and next exhaustive passes. | Requirements claim full source/history coverage without manifest evidence. |
| CONF-STAGE0-012 | Role scenario coverage matrix exists for requirements memory. | Founder, architect and agent must be able to continue the product safely. | Scenario matrix links Stage 0 fixtures for orientation, source intake, safety validation and agent handoff. | Requirements memory is structurally valid but no role can use it reproducibly. |

## Required Report Outcome

`stage0-requirements-memory-ready` is passed when the folder can guide a new
human or AI-agent through CloudRING mission, architecture, stages, trade-offs,
readiness gates and safe source intake without needing old source code.

## Profile Non-Goals

- Running CloudRING.
- Selecting implementation runtime.
- Creating deployment scripts.
- Certifying product features beyond requirements memory readiness.
