# Source Pass 012 - Billing Runtime Evidence And History

Source pass `SRC-PASS-012` deepens the usage metrics gateway source class from
general product-signal coverage into billing runtime evidence, release/history
and settlement trust requirements.

This file is source-safe. It records categories, product signals, requirement
updates and limitations. It does not store raw source paths, private names,
URLs, tokens, env values, IPs, commit subjects, code snippets or exact configs.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-012` |
| Source class | Usage metrics gateway prototype |
| Snapshot date | 2026-06-22 |
| Indexed files in source class | 55 |
| Tracked files in git repository | 58 |
| Current dirty entries | 1 |
| Git commits | 165 all-refs, 161 default-branch, 4 non-default-only |
| Git merges | 48 merge commits |
| Git non-merge commits | 117 |
| Git tags | 44 total, 16 annotated, 28 lightweight |
| Tag quality signals | debug/pre-release-like tags and duplicate tag target groups existed; raw tag names are not retained here |
| Ever-touched paths | 102 |
| Deleted paths | 39 |
| Deleted-path themes | tests/mocks/fixtures, runtime code, migration |
| High-signal categories | API/event contract, async receipt/status, idempotency, event identity, access freshness, queue/backpressure, generated docs/config safety, release/history evidence, settlement freeze |
| Coverage mode | Current-tree product review plus all-refs history/theme review with agent cross-check |
| Coverage claim | Deeper implementation-backed product-signal pass, not full line-by-line, vulnerability, secret, runtime or downstream settlement audit |

## Agent Work

Three read-only agents reviewed independent slices:

| Agent Slice | Product Focus | Output Used |
|---|---|---|
| API/event contract | Usage event identity, idempotency, batch semantics, period/unit/metadata, entitlement attribution. | `CR-BILLRUN-001..009`, `CR-BILLRUN-020..023` |
| Operations/runtime | Async acceptance, durable/volatile contract, backpressure, shutdown drain, quarantine, readiness, observability, docs/config safety. | `CR-BILLRUN-010..019`, `CR-BILLRUN-024` |
| History/release | Tags, deleted tests, repeated fixes, generated docs/config drift, migration compatibility, settlement evidence freeze. | `CR-BILLRUN-025..032` |

## Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| API success can mean async enqueue, not invoice truth. | Success receipt must be staged and auditable. | `CR-BILLRUN-001`, `CR-BILLRUN-008..010` |
| Usage registration, usage submission and commercial attribution are distinct. | Resource lifecycle and order/offer/entitlement context must be explicit. | `CR-BILLRUN-002..003`, `CR-BILLRUN-012`, `CR-BILLRUN-030` |
| Request idempotency and event identity are not the same. | Duplicate/replay conflict behavior must be payload-bound. | `CR-BILLRUN-004..006` |
| Batch processing can hide partial failure if not specified. | Billing requires atomic or per-item result contract. | `CR-BILLRUN-007`, `CR-BILLRUN-014` |
| Queue/backpressure/shutdown are commercial states. | Delayed or failed downstream delivery must be visible and replayable. | `CR-BILLRUN-011..013`, `CR-BILLRUN-017..018` |
| Access state can be stale. | Usage acceptance must state freshness and fail mode. | `CR-BILLRUN-015..016` |
| Generated docs/config are source-safety and commercial-promise surfaces. | Publication/settlement must block on freshness/redaction/drift checks. | `CR-BILLRUN-024`, `CR-BILLRUN-032` |
| Tag existence and current tree are weak billing release evidence. | Billing release readiness needs artifact/test/source/history manifest. | `CR-BILLRUN-025..026` |
| Repeated fixes and deleted tests are product memory. | Billing-critical fix clusters must become fixtures/checks/runbook/ADR outcomes. | `CR-BILLRUN-027..029` |
| Settlement needs frozen evidence. | No settlement without usage/order/entitlement/invoice/dispute/provenance bundle. | `CR-BILLRUN-030..031` |

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Billing runtime evidence requirements | Turns usage gateway runtime/history lessons into product evidence gates. | [../32-billing-runtime-evidence-and-settlement-trust.md](../32-billing-runtime-evidence-and-settlement-trust.md) |
| Billing runtime evidence template | Adds reusable evidence shape for readiness/conformance reports. | [../templates/billing-runtime-evidence-template.md](../templates/billing-runtime-evidence-template.md) |
| Billing runtime evidence example | Provides source-safe synthetic evidence record. | [../examples/billing-runtime-evidence-example.md](../examples/billing-runtime-evidence-example.md) |
| Stage 4 scenario | Adds provider-local billable ingestion/dispute evidence journey. | [../scenarios/stage4/SCENARIO-STAGE4-004-billing-runtime-ingestion-evidence.md](../scenarios/stage4/SCENARIO-STAGE4-004-billing-runtime-ingestion-evidence.md) |
| Stage 5 scenario | Adds cross-participant usage replay and settlement freeze journey. | [../scenarios/stage5/SCENARIO-STAGE5-005-cross-participant-usage-replay.md](../scenarios/stage5/SCENARIO-STAGE5-005-cross-participant-usage-replay.md) |

## Requirement Updates Applied

- Added `CR-BILLRUN-001..032`.
- Added `CR-CONF-033`.
- Added `CR-SPECTPL-027`.
- Added `CR-SPECEX-015`.
- Added `WS-025`.
- Added `SCENARIO-STAGE4-004` and `SCENARIO-STAGE5-005`.
- Updated README, acceptance, conformance, conformance template/example,
  templates/examples indexes, scenario index, capability map, workstream
  backlog, coverage audit and traceability map.

## Non-Claims

This pass does not claim:

- downstream settlement correctness;
- exact tariff/tax/payment processor behavior;
- runtime test execution or CI success;
- vulnerability or secret absence in the source repository;
- full line-by-line or full deleted-source audit;
- current dirty checkout is a release-ready state;
- old implementation technology should be reused.

## Stop Conditions

Future agents must stop if:

- billing readiness claims settlement from intake acceptance alone;
- release readiness uses tags without artifact/test/source-safety evidence;
- idempotency conflict can hide changed payload;
- generated docs/config drift contains unsafe examples or stale commercial
  promises;
- source pass tries to claim all billing history decisions from this targeted
  review;
- evidence would copy private paths, names, endpoints, credentials, tenant data,
  source snippets or raw commit subjects.

## Current Status

Completed as a bounded billing runtime evidence and history source pass.

## Validation Summary

- Markdown files: `150`.
- Requirement IDs: `1414` defined, `1414` referenced, `0` undefined, `0` unused.
- Stage IDs: `8` defined, `8` referenced, `0` undefined, `0` unused.
- Markdown links: `0` missing.
- Private marker scan outside review checklist: clean.
- Strict secret scan outside review checklist: clean.
- Conflict marker and trailing whitespace scan: clean.
