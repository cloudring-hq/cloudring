# Conformance Profile - Stage 6 Global Ready

---
profile_id: stage6-global-ready
aliases:
  - global-network-ready
profile_version: 0.2
stage: 6
stage_file: ../stages/06-global-cloudring.md
change_note: SRC-PASS-019 added global settlement closure evidence expectations.
---

## Purpose

Доказать, что Stage 6 превращает federation в global cloud-of-clouds product
surface: global discovery, multi-jurisdiction policy, distributed trust,
settlement, support, portability and governance work without creating a new
central lock-in.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE6-001 | Global portal/API is aggregator, not sole owner. | Global convenience must not become new lock-in. | Local presence keeps lifecycle, audit and emergency actions during global degradation. | Global portal outage stops existing local services. |
| CONF-STAGE6-011 | Global network includes multiple participant types and jurisdiction profiles. | Stage 6 is global network readiness, not just a larger Stage 5 demo. | At least three independent presence across multiple jurisdiction policy profiles and participant types. | Global readiness is claimed from a single jurisdiction or one participant type. |
| CONF-STAGE6-002 | Verified global discovery index exists. | Search needs trust without copying all control planes. | Offer metadata includes source participant, signature/attestation, freshness, policy availability and local owner. | Global catalog hides source/freshness/owner. |
| CONF-STAGE6-003 | Multi-jurisdiction policy gates risky action. | Data residency/compliance must be checked before action. | Order/placement/data movement returns allowed, blocked, warning, approval-required or manual-review with reason. | Data movement occurs before policy decision. |
| CONF-STAGE6-004 | Distributed trust supports multiple anchors, downgrade and rotation. | Single root trust can become lock-in. | Trust/certification downgrade affects marketplace availability without breaking unrelated local services. | One trust operator can silently control all actions. |
| CONF-STAGE6-005 | Marketplace ranking is explainable. | Hidden ranking can become commercial lock-in. | Buyer sees why offer is shown, blocked, degraded or preferred: price, latency, jurisdiction, trust, SLA, compatibility. | Ranking cannot explain blocked or preferred choices. |
| CONF-STAGE6-006 | Global settlement/dispute is evidence-first and closure-based. | Multi-party marketplace needs money trust across jurisdictions without hiding unresolved amounts. | Settlement links order, entitlement, usage, closure run, reconciliation, invoice/credit/refund, shares, currency/tax metadata, dispute hold/release, closeout export and party-scoped evidence. | Shares cannot be traced to closure evidence, disputed amounts settle silently or global view over-shares participant/customer data. |
| CONF-STAGE6-007 | Portability is honest and capability-based. | Universal portability must not be promised falsely. | Service shows automated, assisted, manual, export-only, blocked or non-portable status with reasons. | Marketplace implies migration where profile blocks it. |
| CONF-STAGE6-008 | Global support preserves one user experience. | User should not coordinate participants. | Ticket shows support owner, involved parties, SLA, handoff state, evidence and escalation. | User must manually chase provider chain. |
| CONF-STAGE6-009 | AI global operations respect approvals. | Global scale needs agents but not hidden authority. | Agent plan has options, policy, cost, risk, approval, rollback and validation. | Agent can bypass billing/suspension/data-movement approval. |
| CONF-STAGE6-010 | Product experience follows simplicity gate. | Global power must remain understandable. | Key flows pass `ADR-0012` checks: intent-first, consequence-before-action, human-agent symmetry. | Buyer cannot explain where service runs, who owns it or how to exit. |
| CONF-STAGE6-012 | Role scenario coverage matrix exists for global network. | Global readiness must prove buyer, provider, ISV, support, governance and agent journeys without central ownership takeover. | Scenario matrix links global discovery, policy overlay, trust downgrade, settlement/dispute, support and exit fixtures. | Stage 6 passes without reusable global role scenario evidence. |

## Required Report Outcome

`stage6-global-ready` / `global-network-ready` is passed when global choice,
policy, trust, settlement and support are usable without centralizing ownership
or promising impossible portability.

## Profile Non-Goals

- Guaranteed coverage of every country, provider or compliance regime.
- Universal or bit-for-bit portability for every service.
- Mandatory single root of trust.
- Stage 7 autonomous self-evolution.
