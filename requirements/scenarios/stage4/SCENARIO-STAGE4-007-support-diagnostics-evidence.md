# SCENARIO-STAGE4-007 - Support Diagnostics Evidence

---
id: SCENARIO-STAGE4-007
stage: 4
title: Provider Support Diagnostic Package For Tenant Incident
roles:
  - provider
  - tenant
  - support
  - governance
  - AI-agent
capabilities:
  - support-diagnostics-evidence
  - observability-and-operations
  - public-provider-kit
  - stateful-recovery-evidence
---

## Intent

Provider support receives a tenant-impacting incident. CloudRING must produce a
safe diagnostic package that explains identity, readiness, correlation, primary
failure story, issue location, export controls and non-claims without exposing
private operational context.

## Preconditions

- A provider-visible service or operation has a support owner.
- Runtime signals exist for at least health/readiness, correlation and one
  observability signal family.
- Source-safety and retention policy are available for support evidence.
- High-impact attachments require explicit owner approval.

## Happy Path

1. Support opens a diagnostic request for a synthetic incident.
2. CloudRING builds a read-only support package with service/profile/release
   identity and support owner.
3. CloudRING separates liveness, readiness, health, drain and dependency states.
4. Logs, traces, metrics and event summaries are linked through a safe
   correlation reference.
5. Primary failure story identifies whether the issue is service, local runtime,
   shared platform, provider, customer input, external dependency or ambiguous.
6. Redaction scan removes unsafe source, secret, topology and customer material.
7. Restricted attachments remain blocked until owner approval and retention are
   explicit.
8. Support and AI-agent receive the summary, allowed actions, forbidden actions
   and non-claims.

## Negative Cases

| Case | Expected Behavior |
|---|---|
| Diagnostics export would mutate service, queue, billing, recovery or release state. | Export is blocked; only existing read-only evidence may be summarized. |
| Health is green but dependency state is unknown. | Package is warning or blocked; readiness cannot be inferred from generic health. |
| Duplicate/retry success hides whether work was already accepted. | Package marks retry/idempotency evidence missing and blocks commercial or recovery conclusion. |
| Raw logs, endpoints, paths, host identifiers, network literals, credentials or commands appear in bundle. | Package is blocked for redaction/source-safety repair. |
| Stateful operation evidence requires raw topology dump. | Summary-only audit timeline is produced; attachments require owner approval and retention. |
| Declared log/status surface is unimplemented. | Readiness is warning or blocked; generated docs cannot prove support diagnostics. |

## Evidence

- `CR-SUPDIAG-001..032`
- `CR-CONF-047`
- `CR-CAPEVID-037`
- `WS-039`
- Support diagnostics evidence bundle.
- Source-safe incident summary and export-control record.

## Stop Conditions

Agent must stop if:

- support diagnostics collection is not read-only;
- liveness/readiness/health/drain meanings are ambiguous;
- correlation cannot connect symptom, internal work and safe support reference;
- raw source/private/secret/topology/customer data would enter agent context;
- high-impact attachment export lacks owner approval or retention policy;
- local/debug-only signals are claimed as provider readiness.

## Non-Claims

- This scenario does not choose a specific observability, logging, tracing,
  ticketing or incident-management technology.
- This scenario does not prove root cause, live provider repair, financial
  settlement, restore completion, vulnerability absence or full source/history
  coverage unless linked evidence explicitly covers them.
