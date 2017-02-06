# Source Pass 004 - UI Validation And Composition

Source pass `SRC-PASS-004` covers the UI validation and UI composition
prototypes as product signal sources for CloudRING self-service, UI/API/agent
parity, embedded service UI trust and marketplace-quality user experience.

This file is source-safe. It records categories, product signals, requirements
and limitations. It does not store raw source paths, private names, URLs,
tokens, env values, IPs, commit subjects or implementation snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-004` |
| Source classes | UI validation prototype; UI composition prototype |
| Snapshot date | 2026-06-22 |
| Indexed files in UI validation source class | 25 |
| Indexed files in UI composition source class | 13 |
| Tracked files in UI validation git repository | 28 |
| Tracked files in UI composition git repository | 16 |
| UI validation git commits | 9 |
| UI composition git commits | 32 |
| Git tags | 0 in both source classes |
| High-signal categories | Validation rule identity, error contract, event timing, test fixtures, UI embedding, typed context, lifecycle, theming, extension trust, support owner, history/release evidence |
| Coverage mode | Current-tree analysis plus git history/theme review |
| Coverage claim | Completed targeted product-signal and all-refs history/theme coverage; not full line-by-line vulnerability/secret audit |

## Slice Coverage

| Slice | Coverage Status | Product Signal Focus | Requirement Areas |
|---|---|---|---|
| UI validation contract | Completed targeted current-tree pass | Rule identity, typed errors, human/machine messages, timing, fixtures, UI/API/agent parity and safety budgets. | `CR-OCSCONTRACT-*`, `CR-SECSUPPLY-*`, `CR-CAPEVID-*` |
| UI composition and embedding contract | Completed targeted current-tree pass | Bootstrap/provider model, typed context, lifecycle, theming, permissions, sandbox/trust manifest and support owner. | `CR-OCSCONTRACT-*`, `CR-SECSUPPLY-*`, `CR-MKT-*`, `CR-UX-*` |
| History, release and source safety | Completed all-refs history/theme pass | Small histories, no-tag release gap, dependency/test evolution, static asset/source safety and repeated fix themes. | `CR-SRCOV-*`, `CR-STAGE7-*`, `CR-METRIC-*` |

## Initial Product Signals

| Signal | Product Meaning | Current Coverage |
|---|---|---|
| Validation rules as product contract | User input rules must be shared by UI, API and agents. | Covered; pass checks rule identity, messages, timing and parity gaps. |
| Negative fixtures and safety budgets | Unsafe validation can become denial of service or a policy bypass. | Covered; pass checks regex/size/runtime evidence. |
| Human-readable and machine-readable errors | Self-service and agents need the same actionable truth. | Covered; pass checks error taxonomy and localization/accessibility gaps. |
| Embedded service UI | Marketplace services need their own UI without breaking portal trust. | Covered; pass checks typed context, lifecycle and isolation evidence. |
| UI extension trust manifest | Raw embedded UI can bypass permissions, theme and validation. | Covered; pass checks install-time trust evidence. |
| Support ownership | UI extensions create support and incident responsibilities. | Covered; pass checks owner/escalation evidence. |
| Release and source safety | Frontend prototypes can hide private context in examples, assets, configs and lockfiles. | Covered via all-refs history/theme and source-safety class scan. |

## Expected Evidence From Pass

- Source-safe slice summaries for UI validation, UI composition and
  history/source-safety evolution.
- Gap list mapped to existing requirement ranges or new requirement updates.
- Updates to coverage manifest, traceability, capability contracts or
  conformance if needed.
- Explicit non-claims about vulnerability/secret/line-by-line/runtime coverage.
- Validation after edits: CR IDs, links, private marker scan and secret-pattern
  scan.

## Stop Conditions

Agent must stop and request owner/review if:

- source-derived output would include raw token, env value, endpoint, IP, local
  path, private name, exact source snippet or raw commit subject;
- validation can pass in UI while API/agent/server rejects or accepts a
  different truth without explicit exception;
- regex, size or runtime validation behavior is unbounded;
- embedded UI can bypass portal permissions, theme, navigation, lifecycle,
  validation or support ownership;
- UI extension trust evidence lacks signed origin/host, scoped context,
  isolation controls, support owner or publishable-build restriction;
- history coverage claims every decision without all-refs/deleted-path evidence;
- requirements would promote an old frontend framework instead of a replaceable
  UI/validation contract.

## Current Status

`SRC-PASS-004` is completed as targeted current-tree plus all-refs
history/theme analysis. It is sufficient to update CloudRING product
requirements for UI validation/composition, but it is not a full vulnerability,
secret-history, runtime, performance or line-by-line source audit.

## Validation Summary

Latest recorded aggregate validation: 2026-06-22 during `SRC-PASS-006`.
Scope: `requirements/` corpus. Result: CR/stage ID consistency, markdown links,
private-marker scan, strict secret-pattern scan and conflict/trailing-whitespace
checks passed after source-safe repairs. Raw match output is not retained in
this pass file.

## Integrated Slice Results

### UI Validation Contract

| Signal | Product Requirement Meaning | Integrated Requirement Updates |
|---|---|---|
| Declarative validation rules | Input rules are product contracts, not UI-only helpers. | `CR-DX-027`, `CR-OCSCONTRACT-018`, `CR-OCSCONTRACT-038`, `CR-CAPEVID-017`, `CONF-STAGE1-010` |
| Stable rule identity | A rule needs a durable rule id and machine code distinct from rendered text. | `CR-OCSCONTRACT-038`, `CR-OCSCONTRACT-045`, `CR-SECSUPPLY-036` |
| Timing and input state | Validation must distinguish reactive, blur, submit and state transitions such as pristine, dirty, touched, pending, submitted and blocked. | `CR-DX-028`, `CR-UX-004`, `CR-UX-013`, `CONF-STAGE1-014` |
| Human and machine error boundary | Users need cause/impact/next step while agents need code/path/params/remediation. | `CR-DX-029`, `CR-UX-007`, `CR-OCSCONTRACT-045` |
| Parity and safety | UI-only truth is not enough for security, billing or marketplace readiness. | `CR-SECSUPPLY-034`, `CR-SECSUPPLY-036`, `CR-CAPEVID-023` |
| Fixture depth | Happy-path snapshots do not prove edge behavior. | `CR-SECSUPPLY-036`, `CR-METRIC-038` |

Required validation evidence now includes stable rule id, machine code, field
path, timing trigger, params schema, severity, remediation, safety budget,
localization/accessibility binding where user-facing, and parity matrix across
UI, API, CLI and Agent API where the rule affects policy, security, billing or
service lifecycle.

### UI Composition And Embedding Contract

| Signal | Product Requirement Meaning | Integrated Requirement Updates |
|---|---|---|
| Standalone plus embedded mode | A service UI can run locally for development but must become host-controlled when embedded. | `CR-DX-025`, `CR-DX-026`, `CR-OCSCONTRACT-036` |
| Typed context | The portal must pass scoped context instead of global ambient power. | `CR-OCSCONTRACT-017`, `CR-SECSUPPLY-016`, `CR-CAPEVID-020` |
| Lifecycle | Mount-only evidence is insufficient; update, unmount, failure and cleanup must be explicit. | `CR-OCSCONTRACT-036`, `CR-CAPEVID-020` |
| Theme and route boundary | Embedded UI must preserve portal navigation, terminology, permissions and visual system. | `CR-UX-021`, `CR-OCSCONTRACT-017`, `CR-OCSCONTRACT-036` |
| Trust manifest | Install-time declaration is required before execution or embed. | `CR-SECSUPPLY-032`, `CR-CAPEVID-020`, `CONF-STAGE3-010` |
| Support owner | UI extension failures create support and incident responsibility. | `CR-OCSCONTRACT-036`, `CR-SECSUPPLY-032`, `CR-CAPEVID-020` |

Required extension evidence now includes embed descriptor, scoped context
schema, allowed actions, host authority boundary, route/navigation containment,
theme-token contract, lifecycle API, validation API, telemetry/redaction API,
support owner, isolation mode, signed or otherwise verified artifact origin,
allowed hosts and publishable-build restriction. Local build success alone is
prototype evidence, not store/provider readiness.

### History, Release And Source-Safety Coverage

| Metric | UI Validation Source Class | UI Composition Source Class |
|---|---:|---:|
| All-refs commits | 9 | 32 |
| Default-branch commits | 9 | 32 |
| Local branch refs | 1 | 1 |
| Remote refs | 2 | 2 |
| Non-default unique commit delta | 0 | 0 |
| Tags | 0 | 0 |
| Current tracked files | 28 | 16 |
| Ever-touched paths | 44 | 21 |
| Deleted paths | 11 | 4 |
| Dirty worktree entries | 0 | 0 |

History scan found small prototype histories with no release tags and no
release-document evidence. UI validation had a small test/fixture footprint but
no negative/parity/bounded-runtime evidence. UI composition had no current or
historical fixture coverage despite build/test script signals. Source-safety
scan found endpoint/host-like metadata classes in current/history material, but
did not find secret assignment, authorization credential, private key, local
path or IP
value classes. This is not a formal secret-history audit.

### Requirement Updates Applied

- Strengthened UI embedding contract in `CR-DX-025..026`,
  `CR-OCSCONTRACT-017`, `CR-OCSCONTRACT-036`, `CR-SECSUPPLY-016`,
  `CR-SECSUPPLY-032`, `CR-CAPEVID-020`, `CR-UX-021`,
  `CONF-STAGE3-010`.
- Strengthened validation contract in `CR-DX-027..029`,
  `CR-OCSCONTRACT-018`, `CR-OCSCONTRACT-038`, `CR-OCSCONTRACT-045`,
  `CR-SECSUPPLY-034`, `CR-SECSUPPLY-036`, `CR-CAPEVID-017`,
  `CONF-STAGE1-010`, `CONF-STAGE1-014`, `CONF-STAGE3-008`.
- Strengthened release/source-history discipline in `CR-SECSUPPLY-013`,
  `CR-SECSUPPLY-035`, `CR-CAPEVID-015`, `CR-CAPEVID-024`,
  `CR-STAGE7-038..039`, `CR-METRIC-038..039`,
  `26-source-coverage-and-completion-audit.md` and
  `98-legacy-source-traceability-map.md`.

### Non-Claims

- This pass does not claim full vulnerability audit, full secret-history audit,
  runtime behavior, dependency health, performance safety or marketplace
  publication readiness.
- This pass does not require a specific frontend framework, validation library,
  module federation mechanism, build tool or browser technology.
- This pass preserves the reusable product contract: typed embedding, scoped
  context, host-controlled lifecycle, stable validation identity, shared error
  semantics, parity, safety budgets, fixtures, source-safety and release
  evidence.
