# Source Pass 023 - Developer Workflow Scenario Evidence

Source pass `SRC-PASS-023` deepens the legacy platform prototype source class
from command/dependency/bootstrap/automation evidence into developer workflow
and scenario evidence.

This file is source-safe. It records categories, product signals, requirement
updates and limitations. It does not store raw source paths, private names,
URLs, tokens, env values, IPs, exact commands, copied docs, commit subjects,
service names, personal contacts or code snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-023` |
| Source class | Legacy platform prototype |
| Snapshot date | 2026-06-22 |
| Candidate files observed in bounded slice | Current-tree files matching e2e specs, run profiles, command docs, service template docs, showcase docs/manifests, validation tests and service spec fixtures |
| Main file categories | Thin e2e check, developer run profiles, service lifecycle docs, task/plugin docs, bootstrap/manual setup docs, service template requirements, showcase readmes, parser/validation fixtures, generated-deployment tests |
| Git history | No local `.git` for the provided platform source root; no history claim |
| Coverage mode | Current-tree product review plus two completed read-only agents for docs/run-profile and code/fixture cross-check |
| Coverage claim | Targeted source-derived product pass for developer workflow scenario evidence; not full line-by-line, live local runtime execution, full e2e suite, vulnerability, secret, dependency-license or history audit |

## Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| E2E checked tool availability only. | Binary presence is useful but must not count as full workflow readiness. | `CR-WORKFLOW-001`, `CR-WORKFLOW-006`, `CR-WORKFLOW-028` |
| Docs and run profiles describe developer lifecycle actions. | Workflow should become reusable scenario evidence with role intent and states. | `CR-WORKFLOW-002..005`, `CR-WORKFLOW-011..019` |
| One start path was explicitly unstable while debug path was preferred. | Readiness must represent maturity, preferred path and unsupported states. | `CR-WORKFLOW-007`, `CR-WORKFLOW-020..021` |
| Service env and generated deployment fixtures contain local/topology/secret-like classes. | Workflow evidence must redact and classify generated outputs before reuse. | `CR-WORKFLOW-012`, `CR-WORKFLOW-026`, `CR-SECSUPPLY-039` |
| Template docs included service observability and docs requirements. | Scaffold readiness must be proven through workflow scenario, not only files. | `CR-WORKFLOW-008..010`, `CR-SERVICEFACTORY-053` |
| Validation fixtures covered invalid identity cases. | Negative cases should become reusable stop-condition fixtures with stable remediation. | `CR-WORKFLOW-023..025` |
| Showcase docs carried local access details and contact-like placeholders. | Examples must be synthetic, role-based and source-safe before publication. | `CR-WORKFLOW-026..030` |
| Legacy project status is not current support evidence. | Requirements should preserve lessons while retaining explicit non-claims. | `CR-WORKFLOW-031..032` |

## Agent Cross-Check

Two read-only agents independently reviewed complementary slices:
docs/e2e/run-profile signals and code/test-fixture/showcase signals. They
converged on the same product conclusion: workflow intent is broad and valuable,
but executable coverage is thin and must be scoped precisely.

Agent-confirmed additions retained in the requirement set:

- local service lifecycle is product intent: create, debug, stop, logs,
  component inspection, env export, docs preview, tasks and plugins;
- e2e availability check proves only tool presence;
- unstable/preview paths must not be treated as readiness;
- tasks and plugins need workflow evidence plus controlled automation/trust
  boundaries;
- showcase services are pattern carriers, not production proof;
- docs and run profiles must be sanitized and generalized before becoming
  CloudRING requirements.
- manifest-first workflow includes environment overlay precedence, component
  declarations and task definitions, but fixtures must state what behavior they
  actually verify;
- service scaffold creation is a real product path, but scaffold generation does
  not by itself prove docs rendering, lifecycle behavior or boilerplate
  completeness;
- validation fixtures cover some invalid identity classes, while broader
  documented naming expectations require explicit gap tracking until enforced;
- generated deployment/task fixtures can contain local endpoint and secret-like
  classes, so reusable evidence must redact and classify them.

## Outputs

| Output | Product Signal | File |
|---|---|---|
| Developer workflow scenario requirements | Defines evidence gates for role journeys, thin e2e scope, run-profile evidence, negative fixtures, cleanup and source-safety. | [../43-developer-workflow-scenario-evidence.md](../43-developer-workflow-scenario-evidence.md) |
| Developer workflow template | Adds reusable workflow evidence shape for conformance reports. | [../templates/developer-workflow-scenario-evidence-template.md](../templates/developer-workflow-scenario-evidence-template.md) |
| Developer workflow example | Provides source-safe synthetic evidence record. | [../examples/developer-workflow-scenario-evidence-example.md](../examples/developer-workflow-scenario-evidence-example.md) |
| Stage 1 scenario | Adds developer/service-owner/agent workflow evidence journey. | [../scenarios/stage1/SCENARIO-STAGE1-009-developer-workflow-scenario-evidence.md](../scenarios/stage1/SCENARIO-STAGE1-009-developer-workflow-scenario-evidence.md) |

## Requirement Updates Applied

- Added `CR-WORKFLOW-001..032`.
- Added `CR-CONF-044`.
- Added `CR-CAPEVID-034`.
- Added `CR-SPECTPL-038`.
- Added `CR-SPECEX-026`.
- Added `CR-SERVICEFACTORY-053`.
- Added `WS-036`.
- Added `SCENARIO-STAGE1-009`.
- Updated README, acceptance, conformance, capability evidence matrix,
  conformance profile, templates/examples indexes, scenario index, capability
  map, workstream backlog, Service Factory capability contract, source coverage
  audit and traceability map.

## Non-Claims

This pass does not claim:

- live local runtime execution;
- full e2e coverage beyond observed thin availability check;
- final CLI/API/Agent API shape;
- production/private/provider/federation readiness;
- safe task/plugin execution beyond controlled evidence requirements;
- vulnerability, secret, SBOM, license or dependency audit;
- full line-by-line review of all platform files;
- git history coverage for the platform slice;
- old commands, run profiles, service names, endpoints, contact placeholders or
  configs should be reused.

## Stop Conditions

Future agents must stop if:

- binary availability, command docs, run profiles or showcase examples are used
  as full workflow readiness;
- unstable/unsupported flow is marked ready;
- workflow evidence includes raw source paths, commands, local endpoints, env
  values, credentials, personal contacts, tenant data or source snippets;
- task/plugin workflow lacks controlled automation or trust evidence;
- local workflow success is claimed as private/provider/federation readiness;
- current-tree review is claimed as full history/source completion.

## Validation

- Markdown corpus count after pass: 208 files.
- Requirement IDs: 1837 defined, 1837 referenced, 0 undefined, 0 unused.
- Stage IDs: 8 defined, 8 referenced, 0 undefined, 0 unused.
- Markdown links: 0 missing local targets.
- Private marker scan: clean for provider/company names, local source paths,
  IP-like literals, known private-source tokens and mojibake markers.
- Strict secret scan: clean for high-confidence key/token/private-key patterns.
- Conflict/trailing scan: clean for merge markers and trailing whitespace.

## Current Status

Completed as a bounded developer workflow scenario evidence source pass.
