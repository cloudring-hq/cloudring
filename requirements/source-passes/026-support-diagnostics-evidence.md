# SRC-PASS-026 Support Diagnostics Evidence

## Scope

Bounded cross-source pass for support diagnostics evidence.

| Field | Value |
|---|---|
| Source classes | Usage gateway runtime/observability signals; platform docs/reference observable service/lifecycle docs; image factory diagnostics and cleanup signals; stateful recovery evidence links |
| Coverage mode | Targeted current-tree review with read-only agent cross-checks |
| Agents | 3 read-only agents: usage gateway diagnostics, platform observable service/docs, image/stateful diagnostic boundary |
| High-signal categories | Readiness/liveness, metrics/logs/traces, request correlation, retry/idempotency, queue pressure, drain/shutdown, error taxonomy, runtime manifest/dependency context, runbook boundary, image boot/crash/seal evidence, stateful audit summaries, redaction/retention gaps |
| Exclusions | Vendored dependencies, raw logs, endpoint paths, hostnames, IPs, token values, source paths, exact command lines, package/import names, commit subjects, generated examples, encrypted payloads |
| Status | Completed as bounded support diagnostics evidence source pass |

## Source-Safety Boundary

This pass intentionally does not transfer:

- private organization or product names;
- hostnames, endpoint paths, URLs, IPs or local paths;
- credentials, token examples, secret-shaped values, encrypted payloads or raw
  diagnostic exports;
- source snippets, exact commands, package/import names or generated examples;
- commit subjects, raw docs prose, raw logs, topology dumps or internal runtime
  identifiers.

## Agent Findings

| Finding | Product Meaning | Requirement Output |
|---|---|---|
| Runtime signals distinguish alive, ready and shutdown/drain behavior but not full support status. | Diagnostics must separate lifecycle states and avoid overclaiming generic health. | `CR-SUPDIAG-004..006`, `CR-SUPDIAG-013` |
| Request correlation flows through logs/traces/downstream work in the reviewed gateway slice. | Support needs one safe reference across symptom, request, work item and receipt. | `CR-SUPDIAG-007..009` |
| Duplicate retry and queue pressure are observable in parts of the gateway but lack a full support dashboard. | Backpressure and idempotent duplicate success must be explicit diagnostic states. | `CR-SUPDIAG-011..014` |
| Platform docs/showcase treat logs, traces and metrics as complementary signals. | Support package needs cross-linked signal families and a primary failure story. | `CR-SUPDIAG-008..010`, `CR-SUPDIAG-019` |
| Runtime manifest/docs describe dependencies, local flows and runbook boundaries. | Diagnostics must classify service, local runtime, shared platform and provider issue location. | `CR-SUPDIAG-016..022` |
| Image factory cleanup/sealing removes traces before publication and deep crash diagnostics are optional. | Image diagnostics need boot/seal/crash policy evidence without unsafe residue. | `CR-SUPDIAG-023..025` |
| Stateful recovery evidence should summarize timelines and outcomes rather than export raw infrastructure logs. | High-impact operations need owner-approved, retention-bound, staged diagnostics. | `CR-SUPDIAG-026..030` |
| Declared support/log surfaces and tests are incomplete in reviewed slices. | Diagnostics readiness must be tested or marked warning/blocked, not inferred from docs. | `CR-SUPDIAG-031..032` |

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Support diagnostics requirements | Defines read-only support diagnostics package, identity, lifecycle states, correlation, error taxonomy, backpressure, image/stateful signals, redaction, retention and non-claims. | [../46-support-diagnostics-evidence.md](../46-support-diagnostics-evidence.md) |
| Support diagnostics template | Adds reusable support diagnostics evidence shape. | [../templates/support-diagnostics-evidence-template.md](../templates/support-diagnostics-evidence-template.md) |
| Support diagnostics example | Provides source-safe synthetic diagnostic package. | [../examples/support-diagnostics-evidence-example.md](../examples/support-diagnostics-evidence-example.md) |
| Stage 4 scenario | Adds provider incident diagnostic package journey. | [../scenarios/stage4/SCENARIO-STAGE4-007-support-diagnostics-evidence.md](../scenarios/stage4/SCENARIO-STAGE4-007-support-diagnostics-evidence.md) |

## Requirement Updates Applied

- Added `CR-SUPDIAG-001..032`.
- Added `CR-CONF-047`.
- Added `CR-CAPEVID-037`.
- Added `CR-SPECTPL-041`.
- Added `CR-SPECEX-029`.
- Added `WS-039`.
- Added `CONF-STAGE4-017`.
- Added `SCENARIO-STAGE4-007`.

## Non-Claims

This pass does not claim:

- live diagnostics bundle execution;
- production root-cause identification;
- complete health/status endpoint implementation;
- complete log export implementation;
- production provider repair readiness;
- downstream financial settlement or restore/failover completion;
- vulnerability, compliance or dependency-license clearance;
- full line-by-line source review;
- full all-refs/deleted-path git history coverage;
- old logs, docs, commands, endpoint paths, source snippets or operational
  context should be reused.

## Stop Conditions

Future agents must stop if:

- diagnostics collection mutates runtime, billing, queue, recovery, release or
  tenant state;
- health/readiness/drain meanings are collapsed into one status;
- support package lacks target identity, owner, source-safety, retention or
  staged disclosure;
- duplicate/retry, queue pressure or async acceptance is hidden behind generic
  success;
- generated docs, log command or local observability are treated as provider
  support readiness without evidence;
- raw logs, private endpoints, hostnames, IPs, credentials, source paths, copied
  commands, topology dumps or tenant data enter requirements or agent context;
- this bounded pass is used as root-cause, production, security, vulnerability,
  license, full-source or full-history proof.

## Current Status

Completed as a bounded support diagnostics evidence source pass. Final
validation summary is recorded after integration.

## Validation

- Markdown corpus count after pass: 223 files.
- Requirement IDs: 1945 defined, 1945 referenced, 0 undefined, 0 unused.
- Stage IDs: 8 defined, 8 referenced, 0 undefined, 0 unused.
- Markdown links: 0 missing local targets.
- Private marker scan: clean for private organization names, source roots,
  network literals, private tool markers and encoding artifacts.
- Strict secret scan: clean for common key, token, password, private-key and
  bearer-token patterns.
- Conflict/trailing scan: clean for merge markers and trailing whitespace.
