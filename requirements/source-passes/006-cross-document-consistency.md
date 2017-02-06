# Source Pass 006 - Cross-Document Consistency

Source pass `SRC-PASS-006` covers the consistency of the current CloudRING
requirements memory after `SRC-PASS-001..005`. It is not a new legacy source
slice. It checks whether the accumulated product requirements remain coherent,
traceable, source-safe, stage-aware and implementable by AI agents without
access to the original source tree.

This file is source-safe. It records categories, findings, requirement updates
and limitations. It does not store raw source paths, private names, URLs,
tokens, env values, IPs, hostnames, commit subjects or implementation snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-006` |
| Scope | Cross-document requirements consistency |
| Snapshot date | 2026-06-22 |
| Markdown files in requirements before pass | 82 |
| Source pass inputs | `SRC-PASS-001`, `SRC-PASS-002`, `SRC-PASS-003`, `SRC-PASS-004`, `SRC-PASS-005` |
| High-signal categories | Stale range summaries, cross-stage evidence drift, ADR coverage, conformance gaps, term consistency, source-safety gates, completion overclaim risk |
| Coverage mode | Requirements-memory consistency review |
| Coverage claim | Completed cross-document consistency review; not proof of full source/history or semantic completeness |

## Review Slices

| Slice | Coverage Status | Product Signal Focus | Requirement Areas |
|---|---|---|---|
| Product architecture and ADR consistency | Completed in this pass | Cloud-of-clouds architecture, stages, domain model, ADR queue, canonical vocabulary and unresolved trade-offs. | `CR-ARCH-*`, `CR-END2END-*`, `CR-DOMAIN-*`, ADR files |
| Conformance, acceptance and evidence coverage | Completed in this pass | Stale ID ranges, acceptance summaries, stage gates, capability evidence matrix, metrics and proof shape. | `CR-CONF-*`, `CR-CAPEVID-*`, stage profiles, `17-acceptance-criteria.md` |
| Source coverage and traceability consistency | Completed in this pass | Source-pass statuses, coverage manifest, traceability map, review checklist, non-claims and source-safety gates. | `CR-SRCOV-*`, `CR-SECSUPPLY-*`, `98-legacy-source-traceability-map.md` |

## Initial Findings

| Finding | Product Meaning | Planned Treatment |
|---|---|---|
| Acceptance summaries lag new requirement IDs | Agents may miss newly added requirements if summary ranges remain old. | Update acceptance ranges and summaries for security, infrastructure, observability and operations. |
| Cross-document pass needs explicit non-claim | A consistency scan must not be mistaken for full source completion. | Record `SRC-PASS-006` as requirements-memory consistency review only. |
| ADR backlog can drift from expanded source-derived requirements | New stateful and source-safety requirements may require ADR coverage or explicit linkage. | Review ADR backlog and add candidates/links if needed. |
| Conformance profiles can lag capability contracts | New evidence requirements need stage-aware gates or future-gap records. | Review and update stage profiles/evidence matrix where needed. |

## Expected Evidence From Pass

- Read-only agent review results for architecture/ADR, conformance/evidence and
  source coverage/traceability.
- Stale range and stale status fixes.
- Cross-document conflict, ambiguity, duplicate and ADR-candidate list.
- Updates to acceptance/conformance/source coverage documents if needed.
- Explicit non-claims about semantic completeness and source completeness.
- Validation after edits: CR IDs, links, private marker scan and secret-pattern
  scan.

## Stop Conditions

Agent must stop and request owner/ADR/review if:

- two requirements make incompatible product promises and neither has ADR or
  stage/context boundary;
- acceptance summary omits recently added requirement IDs;
- conformance claims readiness without evidence for a requirement class;
- stage profile depends on a future-stage capability without non-goal or
  future-gap treatment;
- traceability or coverage manifest claims more source/history coverage than
  current evidence proves;
- consistency fix would include private name, URL, IP, local path, source
  snippet, commit subject or secret-like value.

## Current Status

`SRC-PASS-006` is completed as a requirements-memory consistency pass. It does
not claim new legacy source coverage, full line-by-line audit or complete
semantic proof of all CloudRING requirements.

## Integrated Review Results

| Review Area | Finding Integrated | Requirement Memory Update |
|---|---|---|
| Control-plane vocabulary | `Control Plane` was overloaded across product, presence, federation and global discovery contexts. | `09-reference-architecture.md` now defines Product Control Plane, Presence Control Plane, Federation Coordination Plane and Global Discovery Index; `CR-ARCH-006..008` were clarified. |
| Surface parity | UI/API/CLI/Agent API parity was inconsistent between architecture and stages. | `CR-ARCH-001`, `CR-END2END-007` and stage acceptance now distinguish shared intent contract from stage-specific surface availability. |
| Catalog/store/marketplace taxonomy | Service catalog, private store, public marketplace, federated marketplace and global discovery were easy to confuse. | `23-product-capability-map.md` and `CR-END2END-009` now define stage-aware taxonomy and commerce boundaries. |
| Domain roles and states | Provider/participant/owner/operator/publisher roles and state families needed a canonical model. | `13-domain-model.md` now distinguishes Participant, Provider, Owner, Operator, Publisher and state families for lifecycle, readiness, freshness, policy and trust/suspension. |
| ADR dependency semantics | Proposed ADRs were used as stage gates without explicit readiness semantics. | `14-architecture-decision-backlog.md` now defines proposed dependency handling and adds ADR candidates for identity/tenant model, state taxonomy, discovery governance, policy overlay precedence, trust anchor rotation, event envelope and scoped suspension/appeal. |
| Stage 2/4 stateful evidence | New stateful restore/failover/audit requirements were not fully enforced by profiles and matrix. | `stage2-private-presence-ready.md`, `stage4-public-provider-ready.md` and `conformance/capability-evidence-matrix.md` now gate stateful/HA claims on topology, endpoint ownership, restore/PITR, failover freshness, normalized audit bundle and source-safe evidence. |
| Stage 7 coverage manifest | Self-evolving readiness referenced source learning but lacked explicit coverage-manifest gate. | `stage7-self-evolving-ready.md` now adds `CONF-STAGE7-011` for source/history coverage manifest linked to `CR-STAGE7-039`, `CR-CAPEVID-024` and `CR-SRCOV-*`. |
| Metrics gap | Operational recovery quality lacked dedicated measures. | `15-success-metrics-and-quality-bar.md` now adds `CR-METRIC-040..043` for restore/PITR freshness, failover freshness, stateful audit blocker rate and source-safe evidence coverage; acceptance ranges were updated. |
| Source-pass validation summaries | Completed source passes required validation but did not record safe validation summaries. | `source-passes/001..005` now include safe validation-summary sections; `SRC-PASS-001` source count was reconciled to canonical coverage manifest. |
| Traceability freshness | Legacy traceability map lagged later pass outputs. | `98-legacy-source-traceability-map.md` now expands service-factory, UI validation/composition, stateful operations and source-safety rows and records `SRC-PASS-006` as non-legacy-source consistency pass. |
| Source-safety scope | Review checklist stored literal forbidden markers and did not distinguish checked requirements corpus from workspace notes. | `99-review-checklist.md` now uses redacted private-marker classes, local ignored denylist rule file and explicit publishable-corpus scope. |

## Validation Summary

Final validation after edits, 2026-06-22:

| Check | Result |
|---|---|
| Markdown files | 83 |
| CR IDs | 1233 defined, 1233 referenced, 0 undefined, 0 unused |
| Stage IDs | 8 defined, 8 referenced, 0 undefined, 0 unused |
| Markdown links | 0 missing |
| Private marker scan | Passed, no matches in publishable requirements corpus outside review checklist |
| Strict secret-pattern scan | Passed, no matches in publishable requirements corpus outside review checklist |
| Conflict/trailing-whitespace scan | Passed, no matches |

Raw match output is not stored in this pass file.
