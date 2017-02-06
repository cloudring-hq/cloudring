# SRC-PASS-025 Product Service Integration Contract

## Scope

Bounded cross-source pass for product-service integration contract evidence.

| Field | Value |
|---|---|
| Source classes | Usage gateway docs/API/access/queue signals; platform manifest/docs/registry/showcase signals |
| Coverage mode | Targeted current-tree review with read-only agent cross-checks |
| Agents | 3 read-only agents: API/docs contract, identity/access/resource lifecycle, platform/catalog/docs integration package |
| High-signal categories | Human onboarding docs, generated API docs, machine spec, scoped credential model, product/resource identity, usage submission, version drift, error/result semantics, local validation, service manifest and registry publication signals |
| Exclusions | Vendored dependencies, raw generated examples, endpoint paths, hostnames, tokens, source paths, commands, package/import names, commit subjects, dependency lists |
| Status | Completed as bounded product-service integration contract source pass |

## Source-Safety Boundary

This pass intentionally does not transfer:

- private organization or product names;
- hostnames, endpoint paths, URLs, IPs or local paths;
- token examples, credentials, secret-shaped values or encrypted payloads;
- source snippets, exact commands, package/import names or generated examples;
- commit subjects, raw docs prose or internal service taxonomy.

## Agent Findings

| Finding | Product Meaning | Requirement Output |
|---|---|---|
| Human guide and machine spec are both present but serve different purposes. | Integration package must include both onboarding narrative and machine contract. | `CR-SVCINT-001`, `CR-SVCINT-014..017` |
| Product identity is exact-match and used for authorization. | Identity format/case drift is product-breaking. | `CR-SVCINT-003..005` |
| Credentials are product-scoped, but validity and product authorization are different checks. | Access decision must expose validity, membership, profile and freshness separately. | `CR-SVCINT-004..007` |
| Resource registration is documented before usage, but runtime proof is incomplete in the slice. | Registration-before-usage must be enforced or readiness must be blocked/warned. | `CR-SVCINT-008..010` |
| Usage submission can be accepted before downstream truth is known. | Integration must distinguish accepted-for-processing from billing/settlement truth. | `CR-SVCINT-011`, `CR-SVCINT-023` |
| Request idempotency and event identity are separate. | Retry and reconciliation require distinct contracts and fixtures. | `CR-SVCINT-012..013`, `CR-SVCINT-025` |
| API generations and docs/spec/runtime behavior can differ. | Version migration and drift checks are publication gates. | `CR-SVCINT-018..019`, `CR-SVCINT-028` |
| Generated docs and examples can leak operational context. | Examples must be synthetic and generated docs must be source-safety gated. | `CR-SVCINT-017`, `CR-SVCINT-024`, `CR-SVCINT-028`, `CR-SVCINT-032` |
| Local tests and showcase patterns are thin evidence. | Local confidence must not be promoted to private/provider/federation readiness. | `CR-SVCINT-029..030` |

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Product service integration requirements | Defines integration package, identity, scoped access, resource lifecycle, docs/spec drift, fixtures, support and source-safety gates. | [../45-product-service-integration-contract-evidence.md](../45-product-service-integration-contract-evidence.md) |
| Integration contract template | Adds reusable product-service integration evidence shape. | [../templates/product-service-integration-contract-template.md](../templates/product-service-integration-contract-template.md) |
| Integration contract example | Provides source-safe synthetic integration evidence record. | [../examples/product-service-integration-contract-example.md](../examples/product-service-integration-contract-example.md) |
| Stage 3 scenario | Adds private-store product-service integration review journey. | [../scenarios/stage3/SCENARIO-STAGE3-007-product-service-integration-contract.md](../scenarios/stage3/SCENARIO-STAGE3-007-product-service-integration-contract.md) |

## Requirement Updates Applied

- Added `CR-SVCINT-001..032`.
- Added `CR-CONF-046`.
- Added `CR-CAPEVID-036`.
- Added `CR-SPECTPL-040`.
- Added `CR-SPECEX-028`.
- Added `WS-038`.
- Added `CONF-STAGE3-014`.
- Added `SCENARIO-STAGE3-007`.

## Non-Claims

This pass does not claim:

- live integration execution;
- downstream financial settlement correctness;
- production/provider readiness;
- full entitlement, tariff, invoice or dispute implementation;
- full API compatibility across all versions;
- full line-by-line source review;
- full all-refs/deleted-path git history coverage;
- old API docs, examples, paths, credentials, generated specs or commands should
  be reused.

## Stop Conditions

Future agents must stop if:

- integration readiness is claimed from API docs, generated spec, local test or
  token existence alone;
- product identity is ambiguous or normalized without explicit policy;
- credential scope/freshness is unknown but integration is marked ready;
- resource registration is documentation-only while billable usage readiness is
  claimed;
- success is treated as invoice, entitlement, settlement or downstream delivery
  truth;
- docs/spec/runtime drift is ignored;
- examples or evidence include private endpoints, credentials, tenant data,
  source snippets, local paths or copied commands;
- this bounded pass is used as production, settlement, security, vulnerability,
  license, full-source or full-history audit proof.

## Current Status

Completed as a bounded product service integration contract evidence source
pass. Final validation summary is recorded after integration.

## Validation

- Markdown corpus count after pass: 218 files.
- Requirement IDs: 1909 defined, 1909 referenced, 0 undefined, 0 unused.
- Stage IDs: 8 defined, 8 referenced, 0 undefined, 0 unused.
- Markdown links: 0 missing local targets.
- Private marker scan: clean for private organization names, source roots,
  network literals, private tool markers and encoding artifacts.
- Strict secret scan: clean for common key, token, password, private-key and
  bearer-token patterns.
- Conflict/trailing scan: clean for merge markers and trailing whitespace.
