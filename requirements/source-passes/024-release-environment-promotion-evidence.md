# SRC-PASS-024 - Release Environment Promotion Evidence

Source pass `SRC-PASS-024` extracts source-safe product lessons from release,
build, environment profile, dependency lock, CI/test and promotion signals across
the legacy source bundle.

The pass is intentionally product-level. It preserves what CloudRING must prove
and why, without copying old commands, config files, paths, endpoints, encrypted
payloads, dependency lists, commit subjects or private names.

## Coverage Manifest

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-024` |
| Source classes | Usage/billing gateway release signals, base-image factory release/profile signals, platform/tooling/frontend build and dependency signals |
| Source mode | Bounded current-tree review plus targeted history/tag-shape review where local history exists |
| Agent method | Three read-only agents analyzed independent slices; parent synthesized source-safe product requirements |
| High-signal categories | CI entrypoints, build/test/lint/integration scripts, container/build files, values/profile files, secret-shaped config classes, dependency manifests/lockfiles, toolchain hints, task-image Dockerfiles, frontend build/test configs, release tags/history shape |
| Coverage claim | Targeted source-derived product pass for release/environment promotion evidence; not full line-by-line, live deployment, vulnerability, license, dependency-security, production, secret or full history audit |

## Source-Safe Findings

| Source Signal | Product Lesson | Requirement Output |
|---|---|---|
| Build/test/lint/integration entrypoints existed but did not prove all checks ran for a specific release. | Release readiness needs executed check evidence, not only declared check entrypoints. | `CR-RELPROM-001..006` |
| Environment/profile bundles existed with different maturity and secret classes. | Promotion must prove bundle completeness, parity limits and secret policy across all environments. | `CR-RELPROM-007..013` |
| Release tags and badges existed in one slice, while another lacked immutable tag discipline. | Tags are version signals, not promotion or rollback proof. | `CR-RELPROM-014..016`, `CR-RELPROM-026` |
| Base image flow showed environment-specific builds and descriptive metadata. | CloudRING should promote immutable artifacts and require provenance-grade metadata. | `CR-RELPROM-017..018`, `CR-BASEIMG-*` |
| Task images and frontend modules had mixed lock/test/toolchain confidence. | Module boundary, lock strategy and local-vs-release evidence must be explicit. | `CR-RELPROM-019..025` |
| Manual/scheduled jobs and docs were visible but approval records were not product-grade. | Manual execution is not approval. | `CR-RELPROM-027..028` |
| Rollback/previous-artifact/last-known-good evidence was weak or absent. | Rollback must be planned and retained before tenant/provider-impacting promotion. | `CR-RELPROM-029..031` |
| Source slices are legacy and bounded. | Requirements must preserve lessons without production readiness or full-history claims. | `CR-RELPROM-032`, `CR-SRCOV-*` |

## Agent Cross-Check Summary

Three read-only agents independently converged on the same product conclusion:
release evidence must be an auditable chain, not a local build or historical tag.

Agent-confirmed additions retained in the requirement set:

- release evidence links build, test, integration, environment bundle,
  immutable artifact, promotion and rollback;
- environment bundles need explicit parity/difference statements;
- all environments, including development/test, require secret classification;
- encrypted payloads and topology-adjacent values are not safe evidence;
- tags, badges and manual triggers are useful signals but not promotion proof;
- base-image releases should be artifact-first, not rebuild-per-environment
  unless an exception proves equivalence;
- module boundary, lock strategy, toolchain and runner semantics must be part of
  release readiness;
- task image and frontend release evidence need their own confidence and
  publication boundaries;
- rollback, retention and post-promotion verification are first-class product
  evidence.

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Release environment promotion requirements | Defines evidence gates for artifact identity, environment bundle, checks, runner semantics, approval, rollback and source safety. | [../44-release-environment-promotion-evidence.md](../44-release-environment-promotion-evidence.md) |
| Release promotion template | Adds reusable promotion evidence shape for conformance reports. | [../templates/release-environment-promotion-evidence-template.md](../templates/release-environment-promotion-evidence-template.md) |
| Release promotion example | Provides source-safe synthetic promotion evidence record. | [../examples/release-environment-promotion-evidence-example.md](../examples/release-environment-promotion-evidence-example.md) |
| Stage 4 scenario | Adds provider release/promotion/rollback evidence journey. | [../scenarios/stage4/SCENARIO-STAGE4-006-release-environment-promotion.md](../scenarios/stage4/SCENARIO-STAGE4-006-release-environment-promotion.md) |

## Requirement Updates Applied

- Added `CR-RELPROM-001..032`.
- Added `CR-CONF-045`.
- Added `CR-CAPEVID-035`.
- Added `CR-SPECTPL-039`.
- Added `CR-SPECEX-027`.
- Added `WS-037`.
- Added `CONF-STAGE4-016`.
- Added `SCENARIO-STAGE4-006`.

## Non-Claims

This pass does not claim:

- live CI, build, deployment or rollback execution;
- production promotion occurred;
- signed releases, reproducible builds or vulnerability scans are present;
- dependency security, SBOM, license or supply-chain completeness;
- secret handling is safe end to end;
- full line-by-line source review;
- full all-refs/deleted-path history coverage for every source class;
- old commands, configs, runner details, environment files, dependency lists,
  tags, commit subjects or encrypted payloads should be reused.

## Stop Conditions

Future agents must stop if:

- build, tag, badge, CI entrypoint, manual job or local archive is treated as
  promotion readiness;
- production/provider/private release is claimed without artifact identity,
  environment bundle, approval and rollback evidence;
- encrypted payloads, raw secret/topology values, command lines, local paths,
  internal URLs, dependency lists or commit subjects enter requirements;
- staging-like evidence is claimed as production parity without difference
  record;
- mutable dependencies/base images/tool installs are promoted without exception;
- this bounded pass is used as vulnerability, license, production, secret or
  full-history audit proof.

## Validation

- Markdown corpus count after pass: 213 files.
- Requirement IDs: 1873 defined, 1873 referenced, 0 undefined, 0 unused.
- Stage IDs: 8 defined, 8 referenced, 0 undefined, 0 unused.
- Markdown links: 0 missing local targets.
- Private marker scan: clean for private organization names, source roots,
  network literals, private tool markers and encoding artifacts.
- Strict secret scan: clean for common key, token, password, private-key and
  bearer-token patterns.
- Conflict/trailing scan: clean for merge markers and trailing whitespace.

## Current Status

Completed as a bounded release environment promotion evidence source pass.
