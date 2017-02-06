# Source Pass 001 - Legacy Platform Prototype

Source pass `SRC-PASS-001` covers the legacy platform prototype as a product
signal source for CloudRING. It focuses on high-signal documents, command
surfaces, service manifest/schema, generated artifacts, local runtime,
task/plugin model and sample services.

This file is intentionally source-safe: it records categories, signals,
requirements and limitations, not raw paths, private names, URLs, secrets,
source snippets or implementation commands.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-001` |
| Source class | Legacy platform prototype |
| Snapshot date | 2026-06-21 |
| Indexed files in source class | 241 |
| High-signal categories | Docs/ADR, command/runtime, manifest/spec/generator, samples/showcases, task/plugin, asset/bootstrap registry |
| Coverage mode | Targeted current-tree analysis with multi-agent slice review |
| Coverage claim | Strong product-signal coverage for high-signal categories; not full line-by-line audit |
| Inventory note | Canonical coverage manifest uses 241 significant files after refresh/normalization; an earlier pre-refresh snapshot recorded one additional inventory item. |

## Slice Coverage

| Slice | Coverage Status | Product Signal Focus | Requirement Areas |
|---|---|---|---|
| Docs, ADR and developer guidance | Completed targeted slice | Platform principles, ADR lessons, docs lifecycle, command documentation, service developer journey. | `CR-GOV-*`, `CR-OPS-*`, `CR-SERVICEFACTORY-*`, `CR-END2END-*` |
| Command and local runtime surfaces | Completed targeted slice | Lifecycle actions, command result semantics, debug split, runtime state, bootstrap, task execution. | `CR-SERVICEFACTORY-*`, `CR-OCSCONTRACT-*`, `CR-STAGE1-*` |
| Manifest, generated artifacts and sample services | Completed targeted slice | Manifest schema, components, generated artifacts, service template, registry/bootstrap, showcase services. | `CR-DOMAIN-*`, `CR-OCSCONTRACT-*`, `CR-CATALOG-*`, `CR-SRCOV-*` |

## Initial Product Signals

| Signal | Product Meaning | Current Coverage |
|---|---|---|
| Manifest-first service description | Service meaning must be declared before runtime artifacts. | Covered by OCS/domain/service-factory contracts. |
| Local runtime as developer product boundary | A developer should interact with product actions, not backend-specific commands. | Covered; pass checks for missing command states and evidence. |
| Debug dependencies separately from service process | Local development needs dependency runtime and external service debugger handoff. | Covered; pass checks for redacted env handoff and cleanup evidence. |
| Generated artifacts from contract | Runtime files are derived and disposable, not source-of-truth. | Covered; pass checks for inventory, provenance and regeneration boundaries. |
| Task library and plugin split | Repeatable tasks should be bounded; plugins are higher-trust extensions. | Covered; pass checks for scope/risk/permission clarity. |
| Docs as lifecycle | Docs/runbooks must be created, previewed and validated as part of service readiness. | Covered; pass checks support-usefulness and manifest linkage. |
| Retired/prototype material | Old experiments are source signals, not future requirements by default. | Partially covered; pass checks deprecation/retired-source handling. |

## Expected Evidence From Pass

- Source-safe slice summaries from docs/ADR, command/runtime and
  manifest/generator/sample analysis.
- Gap list mapped to requirement ranges or explicit already-covered decision.
- Required updates to coverage manifest, traceability or capability contracts.
- Limitations and non-claims.
- Validation after edits: CR IDs, links, private marker scan and secret-pattern
  scan.

## Stop Conditions

Agent must stop and request owner/review if:

- source-derived text would include private name, URL, IP, local path, secret
  value or exact source snippet;
- pass output claims full line-by-line source coverage;
- old implementation detail is promoted to mandatory future technology without
  product reason;
- command/runtime behavior changes product promises without requirement or ADR;
- generated artifact boundary remains ambiguous after review.

## Current Status

`SRC-PASS-001` targeted high-signal current-tree pass is completed. It provides
strong product-signal coverage for the requested source class, but it is not a
full line-by-line audit, not a runtime execution test and not a full git-history
audit.

## Validation Summary

Latest recorded aggregate validation: 2026-06-22 during `SRC-PASS-006`.
Scope: `requirements/` corpus. Result: CR/stage ID consistency, markdown links,
private-marker scan, strict secret-pattern scan and conflict/trailing-whitespace
checks passed after source-safe repairs. Raw match output is not retained in
this pass file.

## Integrated Slice Results

### Slice A - Docs, ADR And Developer Guidance

| Coverage | Result |
|---|---|
| Reviewed scope | 48 scoped Markdown documents across overview, role docs, ADRs, evolution notes, service-template guidance, build/task-image notes, service-developer command/component/extension/install/service docs, observability/database best practices, service boilerplate docs, showcase docs and plugin showcase docs. |
| Already covered signals | Manifest-first service contract, local runtime product boundary, debug split, paved-road template, task library, plugins, docs lifecycle, observability, components/dependencies and ADR/evolution loop. |
| Updates added | `CR-OPS-036` canonical UTC timestamps; `CR-OPS-037` database practice separation for schemas/extensions/migration tracking/runtime roles/maintenance roles. |
| Non-claims | No execution of legacy tools, no non-Markdown full audit, no raw source transfer. |

### Slice B - Command And Local Runtime Surfaces

| Coverage | Result |
|---|---|
| Reviewed scope | CLI/root/config, local runtime lifecycle, service factory/lifecycle, debug split, task execution, bootstrap/config distribution, plugin/library extension and e2e expectation surfaces. |
| Already covered signals | Command matrix, runtime profile/state model, preflight, debug split, task/plugin boundary, command maturity/correlation, bootstrap distribution, offline/private profile and source safety. |
| Updates added | `CR-SERVICEFACTORY-041` now includes manual/external state; `CONF-STAGE1-011` includes manual-external state; `CONF-STAGE1-014` requires command fixtures and negative cases instead of binary availability. |
| Non-claims | No legacy CLI execution, no full git-history analysis, no claim that e2e behavior was runtime-verified. |

### Slice C - Manifest, Generated Artifacts And Sample Services

| Coverage | Result |
|---|---|
| Reviewed scope | Manifest/spec schema, validation, env/profile helpers, deployment generator library, service boilerplate/template, generator service wrapper, asset/bootstrap registry, showcase services, retired/prototype signal and manifest-like configs. |
| Source-safe counts | 13 manifest/spec/validation/env files, 9 generator library files, 14 template files, 6 generator wrapper files, 6 registry files, 45 showcase files, 12 retired/prototype files, 19 manifest-like configs across the slice. |
| Already covered signals | Manifest-first contract, service/platform component distinction, dependency connection, generated artifact boundaries, service template, docs lifecycle, observability redaction, asset/bootstrap registry, retired/prototype handling. |
| Updates added | `CONF-STAGE1-016..019` for Stage 1 manifest fixture, generator fixtures, role-based support ownership in docs template, and local-generator-only readiness scope. |
| Non-claims | No build/test execution, no full secret scan, no git-history pass for this slice. |

## Pass Outcome

`SRC-PASS-001` confirms that the current requirements already capture the main
legacy platform prototype product lessons at a stronger product-contract level
than the prototype itself. The pass added targeted hardening requirements for:

- canonical time and database operational practice;
- manual/external local runtime state;
- stronger Stage 1 command fixtures and negative cases;
- Stage 1 manifest/generator/docs-template conformance fixtures;
- local generator evidence scoped only to local readiness.

Remaining work is not more wording for this pass; it is deeper proof work:
runtime execution, line-by-line source coverage where valuable, and git-history
passes for other source classes.
