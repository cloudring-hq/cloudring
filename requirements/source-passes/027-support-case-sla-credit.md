# SRC-PASS-027 Support Case SLA Credit Evidence

## Scope

Bounded cross-source pass for support case, SLA and credit/refund evidence.

| Field | Value |
|---|---|
| Source classes | Platform docs/service boilerplate/runbook/manifest/registry/showcase signals; provider/marketplace support-adjacent docs; usage gateway intake and billing evidence signals |
| Coverage mode | Targeted current-tree review with three read-only agent cross-checks |
| Agents | 3 read-only agents: platform docs/runbook/support metadata, provider/marketplace support signals, usage gateway billing/dispute/credit evidence boundary |
| High-signal categories | Support owner placeholders, service card support disclosure gap, runbook boundary, local-vs-provider support boundary, component ownership, maintenance/update readiness, observability as support input, usage receipt/status/idempotency/period evidence, credit/SLA workflow absence |
| Exclusions | Vendored dependencies, raw docs prose, private names, source paths, endpoint paths, hostnames, IPs, contacts, exact commands, package/import names, code snippets, commit subjects, generated examples, raw logs, invoice data, token values |
| Status | Completed as bounded support case/SLA/credit evidence source pass |

## Source-Safety Boundary

This pass intentionally does not transfer:

- private organization, provider, tenant, product or person names;
- hostnames, URLs, endpoint paths, IPs, local paths or contact handles;
- credentials, token examples, secret-shaped values or encrypted payloads;
- source snippets, exact commands, dependency/package names or generated docs;
- raw logs, invoice details, internal support text or commit subjects.

## Agent Findings

| Finding | Product Meaning | Requirement Output |
|---|---|---|
| Service boilerplate and docs include support owner/contact/card placeholders, but no complete standardized support operating model. | Support owner and service-card disclosure must become product evidence, not informal README text. | `CR-SUPCASE-001..004`, `CR-SUPCASE-026` |
| Manifest/schema and catalog examples identify services and components, but support/SLA metadata is absent or indirect. | Provider readiness must not infer support scope, SLA or credit policy from manifest presence. | `CR-SUPCASE-002..003`, `CR-SUPCASE-027`, `CR-SUPCASE-031` |
| Runbook and command docs support local lifecycle and diagnostics, but do not define support handoff, escalation or commercial terms. | Support cases must distinguish local troubleshooting, support diagnostics, escalation and paid-provider commitments. | `CR-SUPCASE-005..007`, `CR-SUPCASE-011`, `CR-SUPCASE-016` |
| Component docs separate service-owned and platform-owned dependencies. | Case ownership boundary must identify customer, service, platform, provider, ISV, reseller or external dependency. | `CR-SUPCASE-004..006`, `CR-SUPCASE-024` |
| Observability and maintenance practices exist as operational readiness inputs but not as SLA/SLO proof. | SLA clock and breach decision need explicit policy, measurement, exclusions and approval. | `CR-SUPCASE-008..010`, `CR-SUPCASE-012..013` |
| Usage gateway confirms intake, idempotency, periods and queue/error semantics, but not downstream invoice, settlement, credit or refund outcome. | Support case can link billing receipt/status evidence while preserving financial non-claims. | `CR-SUPCASE-018..022` |
| Explicit credit/refund/SLA state machine was not found in the reviewed source slice. | CloudRING needs a new support case/SLA/credit evidence layer and must block overclaimed readiness. | `CR-SUPCASE-019..023`, `CR-SUPCASE-027..032` |

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Support case SLA credit requirements | Defines support case object, ownership, support boundary, SLA clock, customer impact, communication, diagnostics link, billing/settlement link, credit/refund review, party views, agent boundaries and non-claims. | [../47-support-case-sla-credit-evidence.md](../47-support-case-sla-credit-evidence.md) |
| Support case SLA credit template | Adds reusable case/SLA/credit evidence shape. | [../templates/support-case-sla-credit-evidence-template.md](../templates/support-case-sla-credit-evidence-template.md) |
| Support case SLA credit example | Provides source-safe synthetic case with pending credit review. | [../examples/support-case-sla-credit-evidence-example.md](../examples/support-case-sla-credit-evidence-example.md) |
| Stage 4 scenario | Adds provider support case with SLA and credit review journey. | [../scenarios/stage4/SCENARIO-STAGE4-008-support-case-sla-credit.md](../scenarios/stage4/SCENARIO-STAGE4-008-support-case-sla-credit.md) |

## Requirement Updates Applied

- Added `CR-SUPCASE-001..032`.
- Added `CR-CONF-048`.
- Added `CR-CAPEVID-038`.
- Added `CR-SPECTPL-042`.
- Added `CR-SPECEX-030`.
- Added `WS-040`.
- Added `CONF-STAGE4-018`.
- Added `SCENARIO-STAGE4-008`.

## Non-Claims

This pass does not claim:

- live support case execution;
- production support process completeness;
- real SLA/SLO policy or legal interpretation;
- actual credit/refund calculation;
- actual invoice, settlement, tax or accounting correctness;
- downstream financial implementation exists;
- complete ticketing, status page or customer communication system exists;
- production root cause or remediation readiness;
- vulnerability, compliance or dependency-license clearance;
- full line-by-line source review;
- full all-refs/deleted-path git history coverage.

## Stop Conditions

Future agents must stop if:

- support/SLA/credit readiness is inferred from docs, manifests, diagnostics,
  usage intake, generated API docs or local command surfaces alone;
- support case lacks support owner, escalation owner, affected offer/order/
  instance/plan/entitlement binding or party-scoped views;
- SLA claim lacks measurement window, clock rules, excluded states, maintenance
  treatment, evidence source and approver;
- credit/refund claim lacks policy, calculation evidence, approval, dispute
  hold/release or settlement correction lineage;
- raw logs, endpoint paths, hostnames, network literals, credentials, contact
  details, source paths, copied commands, source snippets, invoice details or
  tenant data enter requirements or agent context;
- this bounded pass is used as legal, finance, production, root-cause,
  vulnerability, license, full-source or full-history proof.

## Current Status

Completed as a bounded support case/SLA/credit evidence source pass. Final
validation summary is recorded after integration.

## Validation

- Markdown corpus count after pass: 228 files.
- Requirement IDs: 1981 defined, 1981 referenced, 0 undefined, 0 unused.
- Stage IDs: 8 defined, 8 referenced, 0 undefined, 0 unused.
- Markdown links: 0 missing local targets.
- Private marker scan: clean for private organization names, source roots,
  network literals, private tool markers and encoding artifacts.
- Strict secret scan: clean for common key, token, password, private-key and
  bearer-token patterns.
- Conflict/trailing scan: clean for merge markers and trailing whitespace.
