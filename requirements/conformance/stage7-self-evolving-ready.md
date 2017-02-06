# Conformance Profile - Stage 7 Self-Evolving Ready

---
profile_id: stage7-self-evolving-ready
profile_version: 0.3
stage: 7
stage_file: ../stages/07-self-evolving-platform.md
change_note: SRC-PASS-006 added source/history coverage-manifest gate; SRC-PASS-014 added documentation decision-memory gate for self-evolving readiness.
---

## Purpose

Доказать, что Stage 7 делает CloudRING living platform: incidents, sources,
feedback, technology changes, conformance drift and agent findings become
requirements, ADR, runbooks, checks and safe improvements with human ownership.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE7-001 | Signal intake covers required source classes. | Platform learns from more than production incidents. | Signal backlog with incidents, support, source, technology, security, policy, marketplace and ecosystem feedback. | New significant signal has no intake path. |
| CONF-STAGE7-002 | Evolution loop follows `ADR-0016`. | Self-evolution needs governance contract. | Signal -> triage -> artifact -> plan -> validation -> audit path visible; repeated-fix clusters show threshold/window and owner decision. | Signal closes without outcome or reason. |
| CONF-STAGE7-003 | Triage class is explicit. | Not every lesson changes product contract. | Outcome is no-change, guidance/profile, conformance, requirement, ADR, runbook, agent task or rejection. | Agent changes requirement before classification. |
| CONF-STAGE7-004 | Generated artifacts have lifecycle owner. | Drafts need responsibility and review. | Artifact shows status, owner, source signal, next review and closure criteria. | Generated requirement/ADR/check has no owner/status. |
| CONF-STAGE7-005 | Conformance evolution is versioned. | Checks are product contracts. | New/changed check has version, reason, affected profiles, compatibility impact and rollout/migration note. | Check weakens standard silently. |
| CONF-STAGE7-006 | Technology refresh preserves product contract. | Technology change should not rewrite mission. | Impact analysis lists affected requirements, ADR, compatibility, migration, rollback and unchanged why. | Refresh changes user promise without ADR. |
| CONF-STAGE7-007 | AI proposals respect approval matrix. | Agent autonomy must stay bounded. | Proposal includes scope, risk_class, evidence, validation, rollback/compensation, approval and remaining gaps. | Agent executes risky/destructive/financial/trust/data-moving change without approval. |
| CONF-STAGE7-008 | Source-derived learning is safe. | Requirements must not carry private/copyright-sensitive material. | Source update is paraphrased, anonymized, secret-free and linked to source signal. | Raw source snippet, private name, path, URL, IP or secret appears in learning record. |
| CONF-STAGE7-009 | Knowledge graph traceability works. | Agents need context to avoid repeating mistakes. | Requirement -> ADR -> runbook -> check -> incident -> metric trace is queryable. | Critical decision only exists in memory or git history. |
| CONF-STAGE7-010 | Human owner remains accountable. | Platform should amplify humans, not erase responsibility. | High-impact accepted change records owner, approval, rationale and residual risk. | Major trade-off accepted by agent alone. |
| CONF-STAGE7-011 | Source/history coverage manifest exists for learning claims. | Self-evolution must not overclaim what was learned from sources or history. | Coverage manifest links source class, current tree/ref/tag/deleted-path scope, exclusions, source-safety classes, anonymization result, `CR-CAPEVID-024`, `CR-SRCOV-*` and `CR-STAGE7-039`. | Learning claims full source/history coverage without manifest or safety gate. |
| CONF-STAGE7-012 | Role scenario coverage matrix exists for self-evolution. | Self-evolving platform must prove owner/agent/governance learning journeys, not autonomous drift. | Scenario matrix links signal intake, triage, profile change, source-safety, human approval and no-change decision fixtures. | Stage 7 passes without reusable evolution role scenario evidence. |
| CONF-STAGE7-013 | Documentation decision-memory chain exists for accepted learning. | Self-evolution must preserve why a lesson changed the product, not only that a file was edited. | Accepted learning links requirement, ADR/no-ADR rationale, source pass or incident signal, template/example/scenario/conformance impact, owner, freshness, source-safety and non-claims. | Source or feedback lesson becomes docs/requirement/conformance change without traceable decision-memory evidence. |

## Required Report Outcome

`stage7-self-evolving-ready` is passed when CloudRING can improve from evidence
without unsafe autonomy, hidden source leakage or silent weakening of contracts.

## Profile Non-Goals

- Fully autonomous production mutation.
- Replacing human ownership of mission, money, legal, policy or trust decisions.
- Storing raw source texts, tenant data or secrets in learning records.
- Changing product contracts only because a technology is newer.
