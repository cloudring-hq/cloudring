# Source Pass 020 - Presence Bootstrap Activation Evidence

Source pass `SRC-PASS-020` deepens the legacy platform prototype source class
from lifecycle command/dependency evidence into presence bootstrap activation:
trusted config/assets, local provider startup, install/manual docs, asset
distribution, preflight, diagnostics, rollback and agent-safe activation.

This file is source-safe. It records categories, product signals, requirement
updates and limitations. It does not store raw source paths, private names,
URLs, tokens, env values, IPs, exact commands, copied docs or code snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-020` |
| Source class | Legacy platform prototype |
| Snapshot date | 2026-06-22 |
| Non-excluded files observed in source class | 258 current-tree files in platform slice |
| Main file categories | Platform docs, install/bootstrap/manual docs, ADRs, CLI command code, runtime provider bridge, asset registry service, generated/static bootstrap asset, service examples, command docs, local runtime/deployment helpers |
| Git history | No local `.git` for platform slice in current bundle; no history claim |
| Coverage mode | Current-tree product review plus two read-only agents launched for documentation and code/config cross-check |
| Coverage claim | Targeted source-derived product pass for bootstrap activation evidence; not full line-by-line, live runtime, installer, private cluster, vulnerability, secret or history audit |

## Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| Automatic bootstrap downloads a configuration artifact. | Future CloudRING needs trusted artifact identity, provenance, compatibility, atomic write and rollback evidence. | `CR-PRESBOOT-001..006`, `CR-PRESBOOT-023`, `CR-PRESBOOT-026` |
| Manual bootstrap exists as fallback. | Manual recovery path must produce the same validation/evidence as automatic flow. | `CR-PRESBOOT-013`, `CR-PRESBOOT-020..021` |
| Local provider choice was driven by multi-service routing and operational consistency. | Requirements should preserve the capability need without freezing one runtime technology. | `CR-PRESBOOT-008..010`, `CR-PRESBOOT-022`, `CR-INFPROFILE-001..031` |
| Some runtime providers do not need start/stop; others are unsupported. | Unsupported, unstartable and manual-external are product states, not generic errors. | `CR-PRESBOOT-015..017` |
| Asset registry serves bootstrap/config assets. | Bootstrap catalog must be a governed supply-chain surface, not raw storage. | `CR-PRESBOOT-003..004`, `CR-PRESBOOT-011..012`, `CR-PRESBOOT-026` |
| Config and environment surfaces include toolchain, proxy and runtime values. | Effective config/env is secret-adjacent and topology-adjacent by default. | `CR-PRESBOOT-005`, `CR-PRESBOOT-014`, `CR-PRESBOOT-025`, `CR-PRESBOOT-031` |
| Docs and command behavior show warnings, unsupported states and unstable flows. | Readiness must prove docs/contract alignment and avoid treating preview behavior as ready. | `CR-PRESBOOT-018`, `CR-PRESBOOT-028..030` |
| The source does not prove live private presence install. | Requirements must explicitly separate Stage 1 local bootstrap from Stage 2 private presence readiness. | `CR-PRESBOOT-002`, `CR-PRESBOOT-027`, `CR-PRESBOOT-031` |
| Install proof is weaker than activation proof. | Future CloudRING must record installer/tool provenance, compatibility, integrity and support-safe install status separately from config/runtime activation. | `CR-PRESBOOT-002..003`, `CR-PRESBOOT-020`, `CR-CONF-041` |
| Generated local artifacts are part of the developer loop. | Future CloudRING must classify generated artifacts, deterministic inputs, cache/user-state boundaries, overwrite risk and cleanup policy. | `CR-PRESBOOT-019..021`, `CR-SERVICEFACTORY-051` |

## Agent Cross-Check

Two read-only agents independently reviewed complementary slices:
documentation/install/bootstrap/ADR guidance and CLI/config/provider/asset
registry/generation behavior. They converged on the same product conclusion:
the source is an early bootstrap product signal, not a finished self-service
CloudRING activation guarantee.

Agent-confirmed additions retained in the requirement set:

- install evidence must include tool/source provenance, compatibility and
  integrity, not only binary availability;
- bootstrap must be reproducible, resumable and rollback-aware with checkpoints,
  safe retry, partial-state detection and concurrency lock;
- asset distribution must become a governed catalog with integrity, versioning,
  immutable references, fallback and offline/private modes;
- runtime provider choice must be represented as a capability matrix, not a
  future architecture mandate;
- generated artifacts need a manifest of created/overwritten/cache/user-state
  classes and deterministic source inputs;
- diagnostics must be structured and support-safe: preflight, postflight,
  component health, redacted logs and machine-readable next actions;
- Stage 1 local bootstrap must not be used as proof of Stage 2 private presence,
  enrollment, identity, policy, trust bundle or production readiness.

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Presence bootstrap activation requirements | Defines trusted activation workflow and evidence gates. | [../40-presence-bootstrap-activation-evidence.md](../40-presence-bootstrap-activation-evidence.md) |
| Presence bootstrap activation template | Adds reusable evidence shape for conformance reports. | [../templates/presence-bootstrap-activation-template.md](../templates/presence-bootstrap-activation-template.md) |
| Presence bootstrap activation example | Provides source-safe synthetic evidence record. | [../examples/presence-bootstrap-activation-example.md](../examples/presence-bootstrap-activation-example.md) |
| Stage 2 scenario | Adds admin/agent private presence activation journey. | [../scenarios/stage2/SCENARIO-STAGE2-008-presence-bootstrap-activation.md](../scenarios/stage2/SCENARIO-STAGE2-008-presence-bootstrap-activation.md) |

## Requirement Updates Applied

- Added `CR-PRESBOOT-001..032`.
- Added `CR-CONF-041`.
- Added `CR-CAPEVID-031`.
- Added `CR-SPECTPL-035`.
- Added `CR-SPECEX-023`.
- Added `WS-033`.
- Added `SCENARIO-STAGE2-008`.
- Updated README, acceptance, conformance, conformance template/example,
  templates/examples indexes, scenario index, capability map, workstream backlog,
  infrastructure and service-factory capability contracts, Stage 1/2 profiles,
  source coverage audit and traceability map.

## Non-Claims

This pass does not claim:

- live bootstrap execution or private cluster installation;
- final installer architecture;
- runtime provider choice for future CloudRING;
- vulnerability, dependency-license or secret absence;
- full line-by-line audit of all platform files;
- git history coverage for the platform slice;
- old commands/config formats should be reused.

## Stop Conditions

Future agents must stop if:

- binary install, config download or local runtime start is treated as private
  presence readiness;
- bootstrap artifact trust, version, compatibility or freshness is unknown;
- config/env evidence would expose raw private paths, endpoints, credentials,
  internal topology or copied source text;
- state-changing activation lacks dry-run, approval, rollback or cleanup;
- source pass tries to claim platform history without a local history store.

## Current Status

Completed as a bounded presence bootstrap activation evidence source pass.

Validation after integration:

- `markdown_count=193`.
- `cr_defined=1724`, `cr_referenced=1724`, `cr_undefined=0`,
  `cr_unused=0`.
- `stage_defined=8`, `stage_referenced=8`, `stage_undefined=0`,
  `stage_unused=0`.
- `links_missing=0`.
- Private-marker, strict secret and conflict/trailing-space scans returned no
  findings.
