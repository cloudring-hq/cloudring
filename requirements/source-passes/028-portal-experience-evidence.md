# Source Pass 028 - Portal Experience Evidence

Source pass `SRC-PASS-028` converts the portal, documentation navigation and
minimal frontend composition signals into product requirements for CloudRING
portal experience evidence. The pass is intentionally bounded: it does not
claim a complete UI audit, a final design, production frontend readiness, live
browser certification or full source/history coverage.

## Scope

| Dimension | Value |
|---|---|
| Source classes | Legacy platform prototype; UI composition prototype; UI validation prototype |
| Source slice | Documentation navigation/landing, role-oriented developer docs and minimal portal/frontend provider shell |
| Source-safe method | Paraphrased product lessons only; no raw code, commands, private paths, endpoints, dependency lists, commit subjects or company names |
| Agent work | Three read-only explorers reviewed frontend/provider signals, documentation/landing signals and existing requirements integration separately |

## Key Lessons

| Signal | Product Meaning | Requirement Treatment |
|---|---|---|
| Documentation navigation is role-oriented and useful as an entrypoint. | A docs surface can guide learning, but it is not the same as operational self-service. | `CR-PORTALUX-004`, `CR-PORTALUX-025`, `CR-SPECTPL-043` |
| Landing page links roles to content, not live tasks. | Role entrypoints need first useful tasks, state, progress and evidence. | `CR-PORTALUX-003..007`, `SCENARIO-STAGE4-009` |
| Developer guidance is command and manifest oriented. | Product portal should translate this knowledge into intent, readiness, blocker and handoff views. | `CR-PORTALUX-017`, `CR-PORTALUX-026`, `CR-CAPEVID-039` |
| Minimal frontend shell has separate local and provider-style entrypoints. | Standalone, embedded, docs and production modes must be explicit evidence dimensions. | `CR-PORTALUX-021..024`, `CR-UICERT-001..032` |
| Minimal frontend screen has no product journey. | Blank, placeholder or demo-only surfaces must stop portal readiness claims. | `CR-PORTALUX-001`, `CR-PORTALUX-006`, `CR-PORTALUX-032` |
| Provider-style frontend export has integration intent but weak product contract. | Host surface, owner, context, allowed actions, lifecycle, support owner and non-claims must be declared. | `CR-PORTALUX-022`, `CR-CAPEVID-039` |
| Import/startup path appears narrow and predictable in the reviewed slice. | Portal modules should avoid hidden side effects and leave lifecycle authority to the host. | `CR-PORTALUX-021..023`, `CR-UICERT-006` |
| Existing requirements already cover UX, self-service, embedded UI, support, billing and release. | New work must be a cross-surface evidence gate, not a duplicate UX/UI/support/billing spec. | `CR-PORTALUX-001..032`, `CR-CONF-049` |

## Added Requirements And Artifacts

| Artifact | Purpose |
|---|---|
| [../48-portal-experience-evidence.md](../48-portal-experience-evidence.md) | Adds `CR-PORTALUX-001..032` for portal experience and self-service UI evidence. |
| [../templates/portal-experience-evidence-template.md](../templates/portal-experience-evidence-template.md) | Adds reusable portal evidence template. |
| [../examples/portal-experience-evidence-example.md](../examples/portal-experience-evidence-example.md) | Adds source-safe synthetic filled example. |
| [../scenarios/stage4/SCENARIO-STAGE4-009-provider-portal-experience-evidence.md](../scenarios/stage4/SCENARIO-STAGE4-009-provider-portal-experience-evidence.md) | Adds Stage 4 provider portal evidence scenario. |

## ID Changes

- Added `CR-PORTALUX-001..032`.
- Added `CR-CONF-049`.
- Added `CR-CAPEVID-039`.
- Added `CR-SPECTPL-043`.
- Added `CR-SPECEX-031`.
- Added `WS-041`.
- Added `CONF-STAGE4-019`.
- Added `SCENARIO-STAGE4-009`.

## Non-Claims

This pass does not prove:

- production portal implementation;
- final visual design or design-system choice;
- live browser/runtime certification;
- accessibility or localization completion;
- provider billing, support, SLA or credit correctness beyond linked evidence;
- global marketplace, federation or cross-participant settlement readiness;
- security vulnerability absence;
- full line-by-line or all-history source coverage.

## Source-Safety Notes

- Requirements use product concepts and synthetic examples only.
- Old frontend/runtime tooling, exact commands, source paths, endpoints,
  package names and private operational names are intentionally not preserved.
- A private-marker scan and strict-secret scan must pass after integration.
