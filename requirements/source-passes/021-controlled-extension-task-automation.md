# Source Pass 021 - Controlled Extension And Task Automation

Source pass `SRC-PASS-021` deepens the legacy platform prototype source class
from bootstrap/dependency evidence into controlled extension and task
automation: tasks, plugins, dependency/library operations, task images and
boilerplate generation.

This file is source-safe. It records categories, product signals, requirement
updates and limitations. It does not store raw source paths, private names,
URLs, tokens, env values, IPs, exact commands, copied docs, commit subjects or
code snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-021` |
| Source class | Legacy platform prototype |
| Snapshot date | 2026-06-22 |
| Candidate files observed in bounded slice | 97 current-tree files matching plugin/task/lib/boilerplate/template/service-factory signals |
| Main file categories | Plugin docs and ADR, task command docs, task image docs, service manifest/task docs, CLI plugin/task/library command code, task runner code, library mutation code, service create/scaffold code, boilerplate service package, showcase task service |
| Git history | No local `.git` for platform slice in current bundle; no history claim |
| Coverage mode | Current-tree product review plus two read-only agents launched for documentation and code/config cross-check |
| Coverage claim | Targeted source-derived product pass for controlled automation evidence; not full line-by-line, live task/plugin execution, vulnerability, secret, dependency-license or history audit |

## Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| Tasks are positioned as portable service operations. | Future CloudRING needs task semantics, risk, inputs, env, isolation, result and local/CI/private parity evidence. | `CR-EXTAUTO-001`, `CR-EXTAUTO-010..015`, `CR-EXTAUTO-027` |
| Plugins exist for narrow private/specific automation. | Plugin must be an explicit exception with owner, purpose, permissions, trust and support boundary. | `CR-EXTAUTO-003..004`, `CR-EXTAUTO-016..018` |
| Plugin/task execution receives service context and env. | Env handoff is secret-adjacent and topology-adjacent; redaction and least privilege are product requirements. | `CR-EXTAUTO-007..009`, `CR-EXTAUTO-013`, `CR-SECSUPPLY-001..002` |
| Task images and plugin binaries are executable artifacts. | Artifact provenance, immutable identity, version pinning and catalog governance are readiness gates. | `CR-EXTAUTO-005..006`, `CR-EXTAUTO-015..017`, `CR-SECSUPPLY-009..015` |
| Library/dependency operations can mutate project state. | Dependency updates need plan/apply/validate, version policy, freshness, trust and rollback evidence. | `CR-EXTAUTO-020..021`, `CR-SERVICEFACTORY-020`, `CR-SECSUPPLY-013` |
| Boilerplate generation creates long-lived service starting point. | Scaffold must include product foundations but remain a candidate until validated. | `CR-EXTAUTO-022..024`, `CR-SERVICEFACTORY-001..003` |
| Docs warn parts of task library are changing. | Preview automation must not be treated as mature product behavior. | `CR-EXTAUTO-025`, `CR-SERVICEFACTORY-045` |
| Source does not prove safe production automation. | Requirements must separate local prototype execution from provider/private/federated readiness. | `CR-EXTAUTO-027`, `CR-EXTAUTO-032` |
| Local task/plugin flows execute from project context. | Local developer automation must not be treated as managed CI/private/provider runner evidence without explicit controls. | `CR-EXTAUTO-001`, `CR-EXTAUTO-014`, `CR-CONF-042` |
| Environment handoff reaches subprocesses, task containers and generated files. | Env export must be least-privilege, escaped, redacted and forbidden for raw real-secret exposure. | `CR-EXTAUTO-008..009`, `CR-SECSUPPLY-001..002`, `CR-SECSUPPLY-039` |
| Scaffold and richer boilerplate requirements are not equivalent. | Create/scaffold output must remain a candidate until template and conformance evidence prove readiness foundations. | `CR-EXTAUTO-022..024`, `CR-SERVICEFACTORY-052` |

## Agent Cross-Check

Two read-only agents independently reviewed complementary slices:
documentation/ADR/command guidance and CLI/config/task/plugin execution code.
They converged on the same product conclusion: task and plugin mechanisms are
useful portability/extensibility signals, but the source proves local developer
automation, not safe managed production automation.

Agent-confirmed additions retained in the requirement set:

- plugins are an exception mechanism for private/specific automation and must
  have owner, purpose, permissions, artifact trust, compatibility and disable
  policy before managed execution;
- task images are executable supply-chain artifacts and need immutable identity,
  provenance, scan/SBOM or approved exception, version policy, registry policy
  and rollback/deprecation evidence;
- service environment handoff is secret-adjacent and must define allowed/denied
  keys, redaction, shell/export safety, logging rules and real-secret stop
  conditions;
- local task execution must not be equated with sandboxed CI, private or
  provider runner execution without managed-runner evidence;
- dependency/library mutation must use plan/apply/validate with compatibility,
  trust/freshness, affected file classes and rollback;
- scaffold generation is not service readiness; richer template obligations
  such as docs, observability, build ownership and conformance must be proven;
- generated local env/compose/build artifacts are local developer artifacts and
  not production deployment contracts.

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Controlled automation requirements | Defines evidence gates for tasks, plugins, dependency mutations and boilerplate generation. | [../41-controlled-extension-and-task-automation-evidence.md](../41-controlled-extension-and-task-automation-evidence.md) |
| Controlled automation template | Adds reusable evidence shape for conformance reports. | [../templates/controlled-extension-task-automation-template.md](../templates/controlled-extension-task-automation-template.md) |
| Controlled automation example | Provides source-safe synthetic evidence record. | [../examples/controlled-extension-task-automation-example.md](../examples/controlled-extension-task-automation-example.md) |
| Stage 1 scenario | Adds developer/agent automation governance journey. | [../scenarios/stage1/SCENARIO-STAGE1-008-controlled-extension-task-automation.md](../scenarios/stage1/SCENARIO-STAGE1-008-controlled-extension-task-automation.md) |

## Requirement Updates Applied

- Added `CR-EXTAUTO-001..032`.
- Added `CR-CONF-042`.
- Added `CR-CAPEVID-032`.
- Added `CR-SPECTPL-036`.
- Added `CR-SPECEX-024`.
- Added `CR-SERVICEFACTORY-052`.
- Added `CR-SECSUPPLY-039`.
- Added `CR-AGOPS-031`.
- Added `WS-034`.
- Added `SCENARIO-STAGE1-008`.
- Updated README, acceptance, conformance, conformance template/example,
  templates/examples indexes, scenario index, capability map, workstream
  backlog, Service Factory, Security/Supply Chain and Agent Operations
  capability contracts.

## Non-Claims

This pass does not claim:

- live task/plugin execution;
- plugin runtime, task runner or template engine choice;
- safe production automation;
- vulnerability, secret, SBOM, license or dependency audit;
- full line-by-line review of all platform files;
- git history coverage for the platform slice;
- old commands, plugin examples or task image names should be reused.

## Stop Conditions

Future agents must stop if:

- task/plugin automation is run without owner, purpose, risk and evidence;
- plugin is used without exception rationale;
- artifact identity/provenance/version policy is unknown;
- service env, raw secrets, local paths or private topology would enter
  requirements, examples or agent context;
- dependency/library mutation lacks plan/apply/validate and rollback;
- scaffolded service is treated as ready product without validation;
- local task/plugin success is claimed as private/provider/federation readiness.

## Current Status

Completed as a bounded controlled extension and task automation source pass.

Validation after integration:

- `markdown_count=198`.
- `cr_defined=1763`, `cr_referenced=1763`, `cr_undefined=0`,
  `cr_unused=0`.
- `stage_defined=8`, `stage_referenced=8`, `stage_undefined=0`,
  `stage_unused=0`.
- `links_missing=0`.
- Private-marker, strict secret and conflict/trailing-space scans returned no
  findings.
