# Conformance Profile - Stage 5 Federation Ready

---
profile_id: stage5-federation-ready
profile_version: 0.3
stage: 5
stage_file: ../stages/05-federation-network.md
change_note: SRC-PASS-019 added cross-participant settlement closure and dispute evidence.
---

## Purpose

Доказать, что Stage 5 соединяет несколько independent presence в настоящую
federation: catalog, trust, usage, settlement evidence, support handoff,
disputes and cross-provider operations work without global central lock-in.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE5-001 | At least two independent presence participate. | Federation cannot be proven with one participant. | Participant registry with roles, ownership, jurisdiction and lifecycle state. | All participants share same hidden control plane/owner. |
| CONF-STAGE5-002 | Federation sync follows scoped event/snapshot model. | Network must work without full trust. | Events/snapshots show scope, purpose, version, idempotency, policy result and audit. | Sync requires full infrastructure disclosure. |
| CONF-STAGE5-003 | Catalog shows multi-presence offers with ownership. | Choice must not hide responsibility. | Search result includes provider, region, jurisdiction, certification, price, support and portability. | Buyer cannot identify actual provider/support owner. |
| CONF-STAGE5-004 | Freshness/degraded/stale/disputed states are visible. | Disconnected federation must not create false confidence. | Offer/trust/usage/support freshness, usage-gateway access-sync state, queue-delay state and accepted/rejected/disputed status. | Stale data is presented as fresh. |
| CONF-STAGE5-005 | Usage and settlement evidence spans participants. | Federation economy requires verifiable shares. | Order, usage, invoice/credit, entitlement, duplicate/replay/correction/dispute evidence and participant share references. | Duplicate charges or untraceable shares. |
| CONF-STAGE5-011 | Cross-participant usage replay uses billing runtime evidence. | Federation settlement cannot trust local intake success without replay-safe evidence. | Scenario proves delayed/quarantined/replayed usage across participants with event identity, idempotency conflict handling, access freshness, participant share impact, release/history evidence and settlement freeze. | Replay can double-settle, hide participant impact or bypass dispute approval. |
| CONF-STAGE5-012 | Cross-participant settlement closure uses reconciliation and dispute hold/release evidence. | Participant shares and buyer invoices cannot be trusted if disputed or late usage settles silently. | Scenario proves closure run, input manifest, reconciliation report, frozen/held amounts, scoped participant views, dispute bundle, approval record, closeout export, release/history evidence and source safety. | Cross-participant period closes with unknown usage, over-shared evidence, missing participant-share lineage or unapproved disputed amount release. |
| CONF-STAGE5-006 | Support handoff and disputes are evidence-first. | Incidents cannot disappear between companies. | Ticket/dispute includes participant chain, SLA owner, events, policy decisions and correction history. | No owner for cross-participant support. |
| CONF-STAGE5-007 | Cross-provider operations follow portability and policy checks. | Anti-lock-in requires real movement with safety. | Backup/replication/migration/DR plan with policy, data scope, risk, validation and rollback. | Data moves before jurisdiction or portability check. |
| CONF-STAGE5-008 | Governance actions are scoped and non-destructive. | Trust action should not destroy customer control. | Suspension/revocation reason, scope, appeal, remediation and unaffected services. | Network-wide destructive action without scope or appeal. |
| CONF-STAGE5-009 | Stage 5 avoids global all-marketplace requirement. | Stage 5 proves federation slice, not worldwide scale. | Report lists global-scale gaps as Stage 6 non-blockers. | Profile requires worldwide catalog to pass Stage 5. |
| CONF-STAGE5-010 | Role scenario coverage matrix exists for federation. | Federation readiness must prove participant, buyer, support, governance and agent journeys across boundaries. | Scenario matrix links catalog sync, cross-participant order/usage, support handoff, dispute, suspension and cross-provider operation fixtures. | Stage 5 passes without reusable federation role scenario evidence. |

## Required Report Outcome

`stage5-federation-ready` is passed when independent participants cooperate
through contracts, evidence and policy while retaining local ownership.

## Profile Non-Goals

- Worldwide global marketplace coverage.
- Single global control plane.
- Universal portability for every service.
- Global legal/compliance governance for every jurisdiction.
