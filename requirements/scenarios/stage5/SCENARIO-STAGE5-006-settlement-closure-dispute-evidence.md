# SCENARIO-STAGE5-006 - Settlement Closure Dispute Evidence

## Purpose

Проверить, что Stage 5 federation может закрыть расчетный период между
участниками только после reconciliation, scoped party views, dispute hold/release
policy and source-safe evidence. Scenario intentionally includes a disputed
amount so agents prove safe refusal before settlement.

## Roles

| Role | Goal |
|---|---|
| Buyer | Понять invoice, disputed amount, export and appeal path. |
| Provider | Закрыть provider-local period and expose participant impact. |
| Federation participant | Проверить свою share without seeing unrelated buyer data. |
| Support | Resolve dispute with evidence bundle. |
| Governance | Approve or block close/reopen/manual override. |
| AI agent | Collect evidence and propose next action without financial authority. |

## Preconditions

- `SCENARIO-STAGE4-004` produced billing runtime evidence for usage receipt,
  status, idempotency, replay/quarantine and provider-local settlement freeze.
- At least two independent participants exist in `stage5-federation-ready`.
- Synthetic order, entitlement, usage and participant share objects exist.
- One late usage event or correction creates a disputed participant share.

## Happy Path

1. Provider starts closure run for a period and scope.
2. Closure input manifest links order, entitlement, usage status, decision
   ledger, invoice draft, participant shares, support policy and release evidence.
3. Reconciliation compares intake, accepted, published, invoiced and share
   outputs.
4. Undisputed amounts are marked closeable; disputed amount is held.
5. Buyer, provider and participant see scoped views of the same closure state.
6. Support opens dispute bundle with evidence and decision deadline.
7. Governance approves only the undisputed settlement path.
8. AI agent records remaining gaps and refuses to mark disputed share as settled.

## Stop-Condition Cases

| Case | Expected Product Behavior |
|---|---|
| Usage state is unknown, delayed or quarantined. | Closure blocks or enters manual review; no silent settlement. |
| Late usage arrives after cutoff. | Policy applies backfill, adjustment, rejection or dispute with visible impact. |
| Correction has no lineage. | Credit/refund/participant adjustment is blocked. |
| Participant view exposes unrelated buyer data. | Evidence publication is blocked for party-scope repair. |
| Generated docs/config contain unsafe or stale commercial examples. | Closure blocks or warns according to severity before freeze. |
| Agent tries to release disputed amount. | Agent must stop and request approval. |

## Evidence

- Settlement closure evidence bundle using
  [../../templates/settlement-closure-evidence-template.md](../../templates/settlement-closure-evidence-template.md).
- Billing runtime evidence from `SCENARIO-STAGE4-004`.
- Dispute evidence bundle with safe summary.
- Party-view review for buyer, provider, participant, support, governance and
  AI-agent roles.
- Source-safety validation summary.

## Requirement References

- `CR-SETTLE-001..032`
- `CR-BILLRUN-030..032`
- `CR-BILL-009..014`
- `CR-FEDNET-019`
- `CR-FEDNET-029`
- `CR-CONF-040`
- `CR-CAPEVID-030`

## Non-Claims

- This scenario does not require Stage 6 global settlement.
- This scenario does not choose a payment processor, accounting system or tax
  engine.
- This scenario does not use real provider, customer, endpoint, source or tenant
  data.
