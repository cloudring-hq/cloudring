# Source Pass 002 - Usage Gateway

Source pass `SRC-PASS-002` covers the usage gateway prototype as a product
signal source for CloudRING billing, entitlement, federation and operational
trust.

This file is source-safe. It records categories, product signals, requirements
and limitations. It does not store raw source paths, private names, URLs,
tokens, env values, IPs, commit subjects or implementation snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-002` |
| Source class | Usage metrics gateway prototype |
| Snapshot date | 2026-06-22 |
| Indexed files in source class | 55 |
| Tracked files in git repository | 58 |
| Git commits | 165 |
| Git tags | 44 |
| High-signal categories | API/usage contract, scoped access, queue/backpressure, config/security, observability, tests/release history |
| Coverage mode | Current-tree analysis plus git history/theme review |
| Coverage claim | Completed targeted product-signal and history/theme coverage, not full line-by-line vulnerability/secret audit |

## Slice Coverage

| Slice | Coverage Status | Product Signal Focus | Requirement Areas |
|---|---|---|---|
| API and usage contract | Completed targeted current-tree coverage | Usage resources, versioned contract shape, period semantics, product/resource scope, metadata and error states. | `CR-BILL-*`, `CR-FED-*`, `CR-CAPEVID-021` |
| Ops, security and config | Completed targeted current-tree coverage | Scoped access, credential freshness, redaction, queue/backpressure, diagnostics, config/secret hygiene. | `CR-SECSUPPLY-*`, `CR-OPS-*`, `CR-BILL-*` |
| History, release and test evolution | Completed all-refs theme coverage | Tag discipline, repeated fixes, validation/test evolution, release evidence, source/history coverage. | `CR-STAGE7-*`, `CR-METRIC-*`, `CR-SRCOV-*` |

## Initial Product Signals

| Signal | Product Meaning | Current Coverage |
|---|---|---|
| Usage resource registration before events | Billing must know measurable product value before usage is accepted. | Covered by billing/federation requirements; pass checks evidence gaps. |
| Product-scoped usage access | One service must not submit usage for unrelated products/resources. | Covered; pass checks freshness and degraded-state evidence. |
| Idempotency and deterministic usage identity | Retries and sync replay must not double-charge. | Covered; pass checks duplicate/replay fixture gaps. |
| Period and overlap policy | Ambiguous windows create disputes and wrong invoices. | Covered; pass checks validation and correction semantics. |
| Queue/backpressure and quarantine | Overload or invalid events must be visible and recoverable. | Covered; pass checks negative scenarios and customer/provider impact. |
| Redacted diagnostics | Billing support needs evidence without exposing credentials or tenant/private context. | Covered; pass checks diagnostic evidence shape. |
| Release/test history | Provider readiness needs release evidence and regression coverage. | Covered in principle; pass checks history-specific gaps. |

## Expected Evidence From Pass

- Source-safe slice summaries for API/usage, ops/security/config and
  history/release/test evolution.
- Gap list mapped to existing requirement ranges or new requirement updates.
- Updates to coverage manifest, traceability and conformance if needed.
- Explicit non-claims about vulnerability/secret/line-by-line coverage.
- Validation after edits: CR IDs, links, private marker scan and secret-pattern
  scan.

## Stop Conditions

Agent must stop and request owner/review if:

- source-derived output would include raw token, env value, endpoint, IP, local
  path, private name, exact source snippet or raw commit subject;
- usage event can be accepted/dropped/duplicated without decision evidence;
- billing attribution is hardcoded outside order/offer/entitlement context;
- queue/backpressure state hides customer/provider impact;
- history coverage claims every decision without all-refs/deleted-path evidence;
- requirements would promote an old implementation choice instead of product
  contract.

## Current Status

`SRC-PASS-002` completed a targeted current-tree and all-refs history/theme
review on 2026-06-22. It is sufficient to preserve product signals and
requirement gaps, but it is not proof of runtime readiness, vulnerability
absence, secret absence, exact downstream settlement behavior or full
line-by-line source coverage.

## Validation Summary

Latest recorded aggregate validation: 2026-06-22 during `SRC-PASS-006`.
Scope: `requirements/` corpus. Result: CR/stage ID consistency, markdown links,
private-marker scan, strict secret-pattern scan and conflict/trailing-whitespace
checks passed after source-safe repairs. Raw match output is not retained in
this pass file.

## Integrated Slice Results

### API And Usage Contract

The source signal treats the usage gateway as a billing trust boundary, not as
an ordinary ingestion helper. A product-ready CloudRING implementation must
separate these concerns:

- usage resource declaration before events, so invoices refer to measurable
  product value;
- versioned usage event contracts with product, resource, instance, period,
  unit, amount, source and idempotency identity;
- shared accepted/rejected/duplicate/delayed/quarantined/corrected state
  semantics across API, queue, ledger and settlement;
- explicit period ordering, overlap, correction and dispute behavior;
- metadata identity, size and redaction rules for both keys and values;
- product/resource/environment/action scope checks, not only coarse product
  allow/deny;
- token-safe auth failure evidence;
- negative fixtures for schema drift, missing identity, duplicate replay,
  period overlap, metadata limit/redaction and queue overflow.

The current requirement set already captures the product direction in
`CR-BILL-001..036`, `CR-FED-019..036` and `CR-CAPEVID-021`. This pass tightened
evidence expectations rather than adding a new capability family.

### Ops, Security And Config

The operational signal is that a usage gateway is trustworthy only when its
readiness includes dependencies and queues, not just a listening endpoint.
CloudRING must preserve:

- access decision freshness with last successful sync, source state,
  active/stale/revoked/degraded status and fail-open/fail-closed behavior;
- bounded ingress, queue delay visibility, broker-flush state, replay/quarantine
  and customer/provider impact during backpressure;
- graceful shutdown evidence that pending billable work is flushed, delayed,
  quarantined or replayable with a visible decision;
- redaction coverage for auth failures, generated docs/specs, CI diagnostics,
  development profiles and token-derived operational keys;
- readiness that reports access-sync and queue-health state, not only process
  liveness;
- billing attribution through order, offer, entitlement and invoice context,
  not static deployment context alone.

These signals refine `CR-BILL-025`, `CR-BILL-027`, `CR-BILL-030`,
`CR-BILL-031`, `CR-BILL-033`, `CR-BILL-035`, `CR-SECSUPPLY-006`,
`CR-SECSUPPLY-008`, `CR-SECSUPPLY-028`, `CR-SECSUPPLY-033`,
`CONF-STAGE4-011`, `CONF-STAGE5-004` and `CONF-STAGE5-005`.

### History, Release And Test Evolution

History review covered all local refs at theme level. The repository had 165
commits, 161 commits reachable from the default branch, 48 merge commits, 117
non-merge commits, 4 commits reachable only from non-default refs, 44 tags, 16
annotated tags and 28 lightweight tags. Tag quality was uneven: pre-release or
debug-like tags and duplicate tag targets existed as release-discipline signals.
The current tracked tree had 58 files; all-history path review found 102
ever-touched path names and 39 deleted-path names.

The strongest repeated-change clusters were API contract, tests/mocks,
usage/access, deployment/config, dependencies, generated API docs and later
queue/backpressure. Product meaning:

- release readiness must include immutable artifact/provenance, tag/ref
  discipline, validation result, owner, known exceptions and rollback or
  deprecation note;
- repeated fix clusters must become regression, negative fixture, conformance
  check, requirement/runbook update or explicit owner-approved no-change
  decision;
- generated docs, config and integration-validation outputs are source-safety
  surfaces and must be scanned for credential-shaped, endpoint-shaped,
  address-shaped and private-context-shaped material;
- history-themed analysis can preserve lessons, but it must not claim all
  decisions were recovered without line-by-line deleted-path review.

### Requirement Updates Made

- Strengthened billable-event decision ledger, idempotency, metadata, access
  freshness, state taxonomy and replay/duplicate evidence.
- Strengthened security requirements for credential freshness, generated
  artifact redaction, config classifiers, source/history hygiene and release
  evidence.
- Strengthened Stage 4 and Stage 5 conformance gates for usage gateway negative
  fixtures, queue/shutdown/replay, stale access, backpressure and cross-participant
  evidence.
- Updated source coverage manifest to mark this pass complete as targeted
  current-tree plus history/theme coverage.

### Non-Claims

This pass does not claim:

- every source line or deleted path was audited;
- runtime tests, external integrations or CI artifacts were executed;
- the source is free of vulnerabilities or secrets;
- old implementation technologies should be reused;
- provider-local billing proves federation settlement;
- static deployment attribution is enough for mature commercial attribution.
