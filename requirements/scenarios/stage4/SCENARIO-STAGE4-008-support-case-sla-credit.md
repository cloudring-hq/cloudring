# SCENARIO-STAGE4-008 - Support Case SLA Credit Evidence

---
id: SCENARIO-STAGE4-008
stage: 4
title: Provider Support Case With SLA And Credit Review
roles:
  - provider
  - tenant
  - support
  - finance
  - governance
  - AI-agent
capabilities:
  - support-case-sla-credit-evidence
  - support-diagnostics-evidence
  - billing-runtime-evidence
  - settlement-closure-evidence
  - public-provider-kit
---

## Intent

A tenant opens a support case for a provider service incident and asks whether
an SLA credit applies. CloudRING must show the support owner, service promise,
SLA clock, diagnostics link, billing receipt, dispute hold, party-scoped views,
agent boundaries and non-claims without exposing private operational or
financial data.

## Preconditions

- Tenant has an active order, service instance, plan and entitlement.
- Service card declares support scope, support owner, SLA/SLO policy presence
  and credit/refund policy presence.
- Support diagnostics evidence is available or explicitly marked as missing.
- Billing receipt/status evidence exists if the case affects billed usage.
- Financial adjustment requires approval and settlement correction lineage.

## Happy Path

1. Tenant opens a case from the affected service instance.
2. CloudRING binds the case to offer, order, instance, plan, entitlement,
   support owner and profile scope.
3. Support classifies severity and ownership boundary using bounded vocabulary.
4. CloudRING links a read-only support diagnostics package and separates
   customer impact from root-cause claim.
5. SLA clock starts, pauses or remains not-applicable according to declared
   policy.
6. Tenant receives safe impact summary, next update deadline and required input
   status.
7. Billing evidence is linked as accepted-for-processing receipt/status, not
   invoice or settlement truth.
8. Credit review enters pending state with policy basis, approver, calculation
   evidence and dispute hold.
9. AI-agent drafts allowed updates and next-evidence requests, but cannot approve
   credit, publish breach decision or mutate financial records.
10. Closure records decision, appeal path, settlement correction lineage and
    learning target.

## Negative Cases

| Case | Expected Behavior |
|---|---|
| Service card has no support owner or escalation owner. | Case is blocked for provider support readiness; tenant receives explicit unavailable-owner limitation. |
| SLA is claimed but measurement window or clock rules are missing. | SLA breach decision is blocked; support can continue without promising credit. |
| Diagnostics package is missing or unsafe. | Technical root cause remains non-claim; case uses safe impact summary and requests evidence repair. |
| Usage receipt is treated as final invoice truth. | Financial decision is blocked until billing/runtime and settlement evidence are linked. |
| Credit is approved without calculation evidence or correction lineage. | Credit action is blocked and requires finance/provider approval. |
| Disputed amount would settle silently. | Settlement closeout is blocked until hold/release evidence exists. |
| Case attachment contains raw logs, endpoints, paths, host identifiers, credentials, commands or tenant-private data. | Attachment is blocked for redaction and cannot enter agent context. |
| AI-agent attempts remediation, public status update or financial adjustment without approval. | Action is denied and added to case audit as forbidden. |

## Evidence

- `CR-SUPCASE-001..032`
- `CR-SUPDIAG-001..032`
- `CR-BILLRUN-001..032`
- `CR-SETTLE-001..032`
- `CR-CONF-048`
- `CR-CAPEVID-038`
- `WS-040`
- Support case SLA credit evidence bundle.
- Party-scoped support and financial decision record.

## Stop Conditions

Agent must stop if:

- support owner, escalation owner or support boundary is unknown;
- paid support case lacks offer/order/instance/plan/entitlement binding;
- SLA or credit is inferred from diagnostics, usage intake or maintenance note;
- disputed amount could settle without hold/release and correction lineage;
- private/source/secret/topology/customer/finance data would enter agent
  context;
- requested agent action mutates tenant, service, public status or financial
  state without approval.

## Non-Claims

- This scenario does not choose a ticketing, billing, legal or incident tool.
- This scenario does not prove root cause, actual SLA breach, actual credit
  amount, tax/accounting correctness, final settlement or production readiness
  unless linked evidence explicitly covers them.
