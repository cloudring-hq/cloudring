# Source Pass 011 - Platform Lifecycle Command Surface

This pass is a bounded current-tree source-slice pass over the legacy platform
prototype service lifecycle and deployment surfaces. It focuses on product
signals from documentation, manifest shape, command surfaces, task/plugin
boundaries, runtime/deployment generation and local evidence gaps.

It does not claim full line-by-line source coverage, git-history coverage,
runtime execution, vulnerability absence or final implementation readiness.
The selected source slice has no local git metadata available in this workspace,
so history coverage for this slice remains unproven.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | SRC-PASS-011 |
| Date | 2026-06-22 |
| Source Slice | Legacy platform prototype lifecycle/deployment contract surfaces: docs, manifest examples, command/task/plugin surfaces, validation, generators and local runtime helpers. |
| Coverage Mode | Targeted current-tree contract-surface pass, not full source/history audit. |
| Primary Output | Service lifecycle command surface evidence requirements and Stage 1 scenario. |
| Agent Support | Three read-only agents reviewed next-slice priority, product docs/narrative lessons and command/manifest/task/plugin/generator surface lessons. |
| Safety Boundary | No raw source paths, company names, endpoints, network addresses, credentials, commit subjects or copied source snippets. |

## Product Signals Integrated

| Signal | Requirement Outcome |
|---|---|
| Manifest-first source of truth was valuable but too narrow. | Lifecycle command surfaces must derive from OCS model and include evidence/support/policy/portability boundaries. |
| Create/scaffold flow produced starter files but not full product evidence. | Starter service must include manifest, docs/runbook, validation target, source-safety and conformance gaps. |
| Debug dependency flow was separate from full service start. | Debug dependencies, full start and unsupported/unimplemented actions must be distinct lifecycle states. |
| Environment/profile override existed but effective config evidence was implicit. | Effective configuration report and secret-adjacent export policy are required. |
| Tasks were portable but execution was broad and command-shaped. | Task operations need bounded inputs, mounts, network, risk, secret-safety, timeout and structured result. |
| Plugins were extension points with inherited environment. | Plugin lifecycle needs permissions, isolation, audit, support owner and revocation. |
| Generated runtime artifacts were derived. | Artifact provenance, freshness, source-of-truth boundary and cleanup/regeneration are mandatory. |
| E2E evidence was too shallow for readiness. | E2E command evidence must cover product journeys and negative cases, not executable presence only. |

## Integrated Outputs

| Output | Product Signal | File |
|---|---|---|
| Lifecycle command requirements | Turns command/task/plugin/generator lessons into product evidence gates. | [../31-service-lifecycle-command-surface-evidence.md](../31-service-lifecycle-command-surface-evidence.md) |
| Stage 1 scenario | Adds create/validate/debug/task/docs/cleanup journey evidence. | [../scenarios/stage1/SCENARIO-STAGE1-005-service-lifecycle-command-evidence.md](../scenarios/stage1/SCENARIO-STAGE1-005-service-lifecycle-command-evidence.md) |

## Requirement Updates Applied

- Added `CR-LIFECMD-001..032`.
- Added `SCENARIO-STAGE1-005`.
- Updated acceptance, README, scenario index, capability map, workstream backlog,
  conformance profile, traceability and completion audit.

## Non-Claims

- This pass does not prove the legacy source slice is production-ready.
- This pass does not preserve old CLI names, source paths or implementation
  structure as requirements.
- This pass does not claim source-history coverage for the selected slice.
- This pass does not execute runtime commands or verify live containers.

## Stop Conditions

Future agents must stop if:

- command/lifecycle claim lacks OCS/action/evidence reference;
- task/plugin execution would require raw secret, private path or copied source
  text;
- generated artifact lacks provenance/freshness/cleanup semantics;
- unsupported action is presented as ready;
- source pass tries to claim history coverage for this slice without git
  metadata or equivalent evidence.

## Current Status

Completed as a bounded current-tree contract-surface source pass. Final
validation summary is recorded below after structural and safety scans.

## Validation Summary

Final validation on 2026-06-22:

- `markdown_count=144`.
- `cr_defined=1379`, `cr_referenced=1379`, `cr_undefined=0`,
  `cr_unused=0`.
- `stage_defined=8`, `stage_referenced=8`, `stage_undefined=0`,
  `stage_unused=0`.
- `links_missing=0`.
- Private/source marker scan outside review checklist: `0` matches.
- Strict secret-pattern scan outside review checklist: `0` matches.
- Conflict marker and trailing whitespace scan: `0` matches.
