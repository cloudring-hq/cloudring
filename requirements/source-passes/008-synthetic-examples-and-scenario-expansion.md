# Source Pass 008 - Synthetic Examples And Scenario Expansion

Source pass `SRC-PASS-008` expands the requirements memory after
`SRC-PASS-007` by adding filled, source-safe examples for reusable templates and
additional role scenario fixtures.

This pass does not analyze new legacy source files. It improves the ability to
reimplement CloudRING without old source access by showing how the templates
from `SRC-PASS-007` should be filled with synthetic objects, evidence,
non-claims, role coverage and stop-condition cases.

This file is source-safe. It stores only synthetic/generic examples, requirement
links, non-claims and validation summaries. It does not store raw source paths,
private names, URLs, hostnames, network addresses, credentials, commit subjects
or implementation snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-008` |
| Scope | Synthetic examples and scenario corpus expansion |
| Snapshot date | 2026-06-22 |
| Requirements markdown files before pass | 104 |
| Source pass inputs | `SRC-PASS-007`, templates, scenario fixtures, conformance profiles |
| Coverage mode | Requirements-memory example completion |
| Coverage claim | Completed synthetic example layer and expanded role fixture coverage; not source/history audit |

## Integrated Outputs

| Output | Product Meaning | Files |
|---|---|---|
| Synthetic examples requirements | Defines why filled examples are required and what they must prove. | `28-synthetic-examples-and-fixtures.md` |
| OCS manifest example | Shows service-as-product manifest fields without choosing final schema format. | `examples/ocs-service-manifest-example.md` |
| OCS supporting contracts example | Shows field matrix, precedence, validation code catalog and artifact provenance. | `examples/ocs-supporting-contracts-example.md` |
| Conformance report example | Shows readiness report with checks, role coverage, evidence bundles, warnings and agent handoff. | `examples/conformance-report-example.md` |
| Evidence bundle examples | Shows what evidence proves, does not prove, freshness, owner, retention and source-safety. | `examples/evidence-bundle-examples.md` |
| Profile change example | Shows how conformance changes record compatibility, rollout and owner review. | `examples/profile-change-record-example.md` |
| Source coverage example | Shows classification closure vs full-audit non-claims. | `examples/source-coverage-manifest-example.md` |
| Expanded role fixtures | Adds source intake, user/support handoff, private policy, support disclosure, certification, participant sync, policy overlay and incident learning fixtures. | `scenarios/stage0..stage7` |

## Scenario Expansion Summary

| Stage | Added Fixture | Gap Reduced |
|---|---|---|
| Stage 0 | `SCENARIO-STAGE0-002` | Developer/source-intake role coverage. |
| Stage 1 | `SCENARIO-STAGE1-002` | User and support handoff role coverage. |
| Stage 2 | `SCENARIO-STAGE2-002` | User workload and governance/policy role coverage. |
| Stage 3 | `SCENARIO-STAGE3-002` | Support and governance disclosure coverage. |
| Stage 4 | `SCENARIO-STAGE4-002` | ISV and certification/governance coverage. |
| Stage 5 | `SCENARIO-STAGE5-002` | Private participant admin and ISV federation coverage. |
| Stage 6 | `SCENARIO-STAGE6-002` | Admin and policy overlay governance coverage. |
| Stage 7 | `SCENARIO-STAGE7-002` | Support/provider/developer incident-learning coverage. |

## Requirement Updates Applied

- Added `CR-SPECEX-001..012` for filled synthetic examples and fixtures.
- Updated acceptance summaries, README, traceability map and coverage audit.
- Expanded `scenarios/README.md` and `scenarios/role-coverage-matrix.md`.
- Added examples under `examples/` and linked them from the example index.

## Non-Claims

This pass does not claim:

- full source/history coverage;
- runtime execution of examples;
- final Open Cloud Standard schema format;
- production conformance readiness;
- legal/commercial completeness;
- real provider, tenant or source evidence.

## Stop Conditions

Agent must stop and request owner/ADR/review if:

- a synthetic example starts choosing final schema technology without ADR;
- an example uses real source/customer/provider/network/credential material;
- role coverage matrix marks a role as passed without a fixture or
  not-applicable reason;
- conformance example treats warning or unknown evidence as full pass;
- source coverage example is used to claim full source/history audit.

## Current Status

`SRC-PASS-008` is completed as a synthetic examples and scenario expansion
pass. Validation summary is recorded below.

## Validation Summary

Final validation after edits, 2026-06-22:

| Check | Result |
|---|---|
| Markdown files | 121 |
| CR IDs | 1273 defined, 1273 referenced, 0 undefined, 0 unused |
| Stage IDs | 8 defined, 8 referenced, 0 undefined, 0 unused |
| Markdown links | 0 missing |
| Private marker scan | Passed, no matches in publishable requirements corpus outside review checklist |
| Strict secret-pattern scan | Passed, no matches in publishable requirements corpus outside review checklist |
| Conflict/trailing-whitespace scan | Passed, no matches |

Raw match output is not stored in this pass file.
