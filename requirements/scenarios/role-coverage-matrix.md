# Role Coverage Matrix

This matrix is the first reusable role coverage baseline for stage readiness.
It is intentionally small but explicit. Future passes should add more fixtures
instead of replacing `not-applicable` or `future-expand` with implied coverage.

Status vocabulary:

- `fixture`: covered by a scenario fixture in this folder.
- `not-applicable`: role is outside current stage promise.
- `future-expand`: role matters, but current fixture is only a starter slice.
- `blocked`: missing fixture blocks readiness claim.

| Stage | User/Buyer | Admin | Developer/ISV | Provider | Support | Governance | AI Agent |
|---|---|---|---|---|---|---|---|
| Stage 0 | not-applicable | not-applicable | fixture | not-applicable | not-applicable | fixture | fixture |
| Stage 1 | fixture | not-applicable | fixture | not-applicable | fixture | fixture | fixture |
| Stage 2 | fixture | fixture | not-applicable | not-applicable | fixture | fixture | fixture |
| Stage 3 | fixture | fixture | fixture | not-applicable | fixture | fixture | fixture |
| Stage 4 | fixture | not-applicable | fixture | fixture | fixture | fixture | fixture |
| Stage 5 | fixture | fixture | fixture | fixture | fixture | fixture | fixture |
| Stage 6 | fixture | fixture | fixture | fixture | fixture | fixture | fixture |
| Stage 7 | not-applicable | not-applicable | fixture | fixture | fixture | fixture | fixture |

## Readiness Rule

For a stage readiness claim, every `future-expand` entry must be treated as a
visible gap unless the profile marks it `not-applicable` or a new scenario
fixture covers it. A profile must not treat `future-expand` as passed.

## Linked Requirements

- `CR-CONF-028`
- `CR-CONF-029`
- `CR-SPECTPL-022`
- `CR-DOCMEM-001..032`
- `CR-SECRETRUN-001..032`
- `CR-SVCDEPLOY-001..032`
- `CR-BASEIMG-001..032`
- `CR-UICERT-001..032`
- `CR-SETTLE-001..032`
- `CR-PRESBOOT-001..032`
- `CR-EXTAUTO-001..032`
- `CR-CATREG-001..032`
- `CR-WORKFLOW-001..032`
- `CR-RELPROM-001..032`
- `CR-SVCINT-001..032`
- `CR-SUPDIAG-001..032`
- `CR-SUPCASE-001..032`
- `CR-PORTALUX-001..032`
- `CR-REFSVC-001..032`
- `CR-STATEFULRUN-001..032`
- `CR-END2END-003`
- `CR-END2END-030`
