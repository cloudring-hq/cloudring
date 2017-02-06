# Source Pass 018 - UI Extension Runtime Certification

Source pass `SRC-PASS-018` deepens the UI validation and UI composition
prototype source classes from general UI contract signals into reusable UI
extension runtime certification evidence.

The pass is source-safe. It records product lessons about validation phase
semantics, field-level error lifecycle, dependent rules, stable error identity,
browser/runtime certification, accessibility/localization gaps, embedded UI host
authority, scoped context, lifecycle cleanup, publication proof and support
ownership without preserving raw source paths, private names, exact commands,
endpoints, credential values, regex bodies or copied source blocks.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-018` |
| Date | 2026-06-22 |
| Source classes | UI validation prototype; UI composition prototype |
| Source slice | Validation rules/forms/tests/config/history and embedded UI bootstrap/provider/build/history as product evidence |
| Coverage mode | Bounded current-tree product-signal pass plus local git-history shape; not runtime/browser execution, accessibility audit, vulnerability audit, dependency-license audit or full line-by-line audit |
| Agent work | Two read-only explorers reviewed validation-runtime and embedded-UI publication signals separately |
| Safety boundary | No raw source paths, private names, endpoints, network addresses, credential values, regex bodies, command dumps or copied source snippets |

## Source-Safe Slice Counts

| Category | UI validation slice | UI composition slice | Treatment |
|---|---:|---:|---|
| Current non-git files | 28 | 16 | Inventory only; not a full source-completion claim. |
| Rules/validation modules | 6 | 0 | Product signal for phase semantics, field state, dependent rules and stable error identity. |
| Form/UI runtime files | 4 | 2 | Product signal for user-visible error lifecycle, inline consequences and embedded app surface. |
| Tests/fixtures | 1 direct test, no fixture directory | 0 tests | Product signal for insufficient certification evidence. |
| Docs/config/build | 6 | 4 | Product signal for intended workflow, build/package metadata and certification limits. |
| Host/bootstrap/provider files | 0 | 5 | Product signal for host authority, scoped context and lifecycle boundary. |
| Dedicated typed contract files | 1 validation contract layer | 0 dedicated embed contract files | Product signal for contract gap and publication blockers. |

## Git History Shape

| Signal | UI validation slice | UI composition slice | Product Meaning |
|---|---:|---:|---|
| Local commit count | 9 | 32 | Small iterative prototypes, not release-grade history. |
| Tag count | 0 | 0 | Publication/release identity cannot be inferred from tags. |
| Deleted path count | 11 | 4 | Refactors occurred; certification must not depend on current tree alone. |
| High-level themes | validation module refactor, test setup, dependency update, form component evolution | template scaffold, provider refactor, type-shape changes, style/module support, dependency refresh | Product contract evolved and needs stable certification evidence before store readiness. |

## Product Signals Integrated

| Signal | Product Meaning | Requirement Outcome |
|---|---|---|
| Validation phases distinguish submit, blur/focus and reactive behavior. | User and agent outcomes depend on timing semantics. | `CR-UICERT-014`, `CR-UICERT-018` |
| Field-level state and inline errors are visible. | CloudRING needs per-field error lifecycle, not only global rejection. | `CR-UICERT-015`, `CR-UICERT-017` |
| Conditional/dependent rules appear. | Rule dependencies and short-circuit behavior must be certified. | `CR-UICERT-016`, `CR-UICERT-020` |
| Component-level tests exist but real-browser evidence is missing. | Store/provider readiness needs runtime/browser certification beyond unit/component tests. | `CR-UICERT-005`, `CR-UICERT-021`, `CR-UICERT-032` |
| Accessibility and localization are unproven. | Beautiful self-service requires focus/keyboard/assistive and message governance evidence. | `CR-UICERT-011..013` |
| Embedded UI bootstrap/provider boundary exists. | Host authority and scoped context are first-class product contracts. | `CR-UICERT-002..004`, `CR-UICERT-008` |
| Lifecycle cleanup, failure fallback and publication proof are missing. | Extension publication must block until runtime lifecycle and store evidence exist. | `CR-UICERT-006..007`, `CR-UICERT-022..024`, `CONF-STAGE3-012` |
| Shared frontend runtime/dependency churn appears in history. | Extension dependency and compatibility policy must be explicit. | `CR-UICERT-023`, `CR-UICERT-027` |
| No tags or release attestation exist. | Certification requires immutable artifact identity and provenance. | `CR-UICERT-022`, `CR-UICERT-029` |

## Integrated Outputs

| Output | Product Signal | File |
|---|---|---|
| UI extension runtime certification requirements | Turns validation/runtime/embed/publication lessons into readiness evidence gates. | [../38-ui-extension-runtime-certification.md](../38-ui-extension-runtime-certification.md) |
| Reusable evidence template | Gives agents a structured way to fill certification evidence without raw frontend source. | [../templates/ui-extension-runtime-certification-template.md](../templates/ui-extension-runtime-certification-template.md) |
| Synthetic evidence example | Shows source-safe warning-state proof and non-claims. | [../examples/ui-extension-runtime-certification-example.md](../examples/ui-extension-runtime-certification-example.md) |
| Stage 3 scenario | Adds private-store UI extension certification journey. | [../scenarios/stage3/SCENARIO-STAGE3-005-ui-extension-runtime-certification.md](../scenarios/stage3/SCENARIO-STAGE3-005-ui-extension-runtime-certification.md) |

## Requirement Updates Applied

- Added `CR-UICERT-001..032`.
- Added `CR-CONF-039`.
- Added `CR-CAPEVID-029`.
- Added `CR-SPECTPL-033`.
- Added `CR-SPECEX-021`.
- Added `WS-031`.
- Added `SCENARIO-STAGE3-005`.
- Added `CONF-STAGE3-012`.

## Non-Claims

- This pass does not execute a real browser or host shell.
- This pass does not certify accessibility, localization or mobile behavior.
- This pass does not prove provider/public marketplace publication readiness.
- This pass does not prove vulnerability absence, dependency safety or full
  secret-history coverage.
- This pass does not require any specific frontend framework, validation
  library, bundler or browser technology.
- This pass does not claim full line-by-line or all historical decision
  recovery for the selected slices.

## Stop Conditions

Future agents must stop if:

- UI extension evidence contains raw source, tenant data, endpoint values,
  credentials, private routes or copied config;
- local preview/build success is used as private/provider publication proof;
- scoped context, host authority, lifecycle cleanup or support owner is unknown;
- validation parity is claimed without stable error identity and rule/phase
  evidence;
- user-facing readiness is claimed without browser/runtime, accessibility or
  localization evidence;
- source pass claims full line-by-line or marketplace certification coverage
  from this bounded pass.

## Current Status

Completed as a bounded current-tree plus local history-shape UI extension
runtime certification source pass. Final validation summary is recorded below
after integration.

## Validation Summary

- Markdown files: 182.
- Requirement IDs: 1629 defined, 1629 referenced, 0 undefined, 0 unused.
- Stage IDs: 8 defined, 8 referenced, 0 undefined, 0 unused.
- Markdown links: 0 missing.
- Private marker scan outside review checklist: 0 matches.
- Strict secret scan outside review checklist: 0 matches.
- Conflict marker and trailing whitespace scan: 0 matches.
