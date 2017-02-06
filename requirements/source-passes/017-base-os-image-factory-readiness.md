# Source Pass 017 - Base OS Image Factory Readiness

Source pass `SRC-PASS-017` deepens the VM/image factory prototype from earlier
image publication and hardening signals into reusable base OS image factory
readiness evidence.

The pass is source-safe. It records product lessons about base image identity,
unattended install, provisioning composition, guest readiness, cleanup/sealing,
artifact provenance, profile boundaries, CI validation and promotion gates
without preserving raw source paths, private profile names, exact commands,
endpoints, credential values, network addresses or copied source blocks.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-017` |
| Date | 2026-06-22 |
| Source class | VM/image factory prototype |
| Source slice | Base OS image builder current tree, provisioning roles, unattended install material, cleanup, build profiles, CI wrapper and safe git-history shape |
| Coverage mode | Bounded current-tree product-signal pass plus local git-history shape; not live image build, boot execution, vulnerability audit, dependency-license audit, full deleted-path audit or full line-by-line audit |
| Agent work | One focused read-only explorer reviewed the base OS image factory/provisioning slice; main pass cross-checked current non-git file counts and repository history shape |
| Safety boundary | No raw source paths, private names, endpoints, network addresses, credential values, profile values, command dumps or copied source snippets |

## Source-Safe Slice Counts

| Category | Count | Treatment |
|---|---:|---|
| Current non-git files | 22 | Inventory only; not a full source-completion claim. |
| Image build definition | 1 | Product signal for governed image line, build inputs, backend adapter boundary and artifact lifecycle. |
| Unattended install material | 1 | Product signal for install choices, disk/account/package policy and source-safe answer-file summary. |
| Provisioning entrypoints | 3 | Product signal for role composition, idempotence expectations and build/provision separation. |
| Provisioning role files | 7 | Product signal for guest readiness, package baseline, guest tooling, diagnostics and cleanup dependencies. |
| Cleanup script | 1 | Product signal for sealing, residue removal and support-safe diagnostic retention. |
| Build wrapper and README | 2 | Product signal for operator workflow, validation wrapper, profile handling and local vs promotion boundary. |
| Variable/profile files | 4 | Secret-adjacent product signal only; values and profile names are excluded. |
| CI/dotfile support | 2 | Product signal for validate/build automation limits and source-safety hygiene. |
| Additional config descriptor | 1 | Treated as source-safe inventory only; no raw content transferred. |

## Git History Shape

| Signal | Value | Product Meaning |
|---|---:|---|
| Local commit count | 35 | Iterative image factory work exists, especially around boot/provisioning reliability. |
| Tag count | 0 | Release/promotion identity cannot be inferred from tags and must be explicit evidence. |
| Recent history themes | n/a | Boot timing, guest initialization, serial/console diagnostics, crash diagnostics, provisioning role refactor, package/install changes and validation wrapper updates. |
| History non-claim | n/a | This pass does not claim every historical decision, deleted file or secret-class event was audited. |

## Product Signals Integrated

| Signal | Product Meaning | Requirement Outcome |
|---|---|---|
| The slice represents a reusable image factory rather than a single manual VM install. | CloudRING needs base images as governed infrastructure capability. | `CR-BASEIMG-001`, `CR-BASEIMG-019..020`, `CR-INFPROFILE-008` |
| Build profiles and environment variables are present. | Inputs must be classified and separated from product contract to avoid private-context leakage. | `CR-BASEIMG-003..005`, `CR-BASEIMG-028`, `CR-CONF-038` |
| Unattended install and provisioning roles exist. | Install choices and role effects must become auditable evidence, not copied implementation details. | `CR-BASEIMG-006..016` |
| Guest initialization, disk growth, guest tooling and console/diagnostic signals appear. | First boot and supportability are product requirements for a cloud provider. | `CR-BASEIMG-007`, `CR-BASEIMG-009..012`, `CR-BASEIMG-021..023` |
| Cleanup/sealing is a distinct step. | Promotion requires residue and machine-identity evidence before reuse. | `CR-BASEIMG-017..018`, `CR-SECSUPPLY-030..037` |
| CI/wrapper material validates or automates parts of the flow. | Automation evidence must be useful but limited; it does not equal full image readiness. | `CR-BASEIMG-021`, `CR-BASEIMG-024`, `CR-BASEIMG-029` |
| No tags are present in local history. | Image release/promotion identity needs a product-level lifecycle gate. | `CR-BASEIMG-019`, `CR-BASEIMG-025..027` |
| The slice is one base OS/image line. | A first image line is useful, but multi-family portability must be explicit. | `CR-BASEIMG-030`, `CR-BASEIMG-032` |

## Integrated Outputs

| Output | Product Signal | File |
|---|---|---|
| Base OS image factory requirements | Turns build/provision/cleanup/history lessons into readiness evidence gates. | [../37-base-os-image-factory-readiness.md](../37-base-os-image-factory-readiness.md) |
| Reusable evidence template | Gives agents a structured way to fill image readiness evidence without raw build profiles. | [../templates/base-os-image-readiness-evidence-template.md](../templates/base-os-image-readiness-evidence-template.md) |
| Synthetic evidence example | Shows source-safe warning-state proof and non-claims. | [../examples/base-os-image-readiness-evidence-example.md](../examples/base-os-image-readiness-evidence-example.md) |
| Stage 2 scenario | Adds private-presence base image readiness journey. | [../scenarios/stage2/SCENARIO-STAGE2-007-base-os-image-readiness.md](../scenarios/stage2/SCENARIO-STAGE2-007-base-os-image-readiness.md) |

## Requirement Updates Applied

- Added `CR-BASEIMG-001..032`.
- Added `CR-CONF-038`.
- Added `CR-CAPEVID-028`.
- Added `CR-SPECTPL-032`.
- Added `CR-SPECEX-020`.
- Added `WS-030`.
- Added `SCENARIO-STAGE2-007`.
- Added `CONF-STAGE2-014`.

## Non-Claims

- This pass does not execute an image build.
- This pass does not boot a generated image or certify first-boot behavior.
- This pass does not prove production hardening, compliance or vulnerability
  absence.
- This pass does not certify a specific OS, image builder, provisioning tool,
  virtualization backend or provider environment.
- This pass does not claim full all-refs/deleted-path source-history coverage.
- This pass does not transfer raw build profiles, private values, endpoints,
  credentials, network addresses or copied source config.

## Stop Conditions

Future agents must stop if:

- image evidence contains raw profile values, endpoints, credentials, private
  locations or copied source configuration;
- build success is used as readiness without cleanup, first-boot, artifact
  identity and source-safety evidence;
- a backend-specific image is presented as portable without adapter limitations;
- cleanup/sealing state, dependency provenance, owner or rollback path is
  unknown but promotion is requested;
- source pass claims full line-by-line or complete history coverage from this
  bounded pass.

## Current Status

Completed as a bounded current-tree plus local history-shape base OS image
factory readiness source pass. Final validation summary is recorded below after
integration.

## Validation Summary

- Markdown files: 177.
- Requirement IDs: 1593 defined, 1593 referenced, 0 undefined, 0 unused.
- Stage IDs: 8 defined, 8 referenced, 0 undefined, 0 unused.
- Markdown links: 0 missing.
- Private marker scan outside review checklist: 0 matches.
- Strict secret scan outside review checklist: 0 matches.
- Conflict marker and trailing whitespace scan: 0 matches.
