# Source Pass 029 - Reference Service Portfolio Evidence

Source pass `SRC-PASS-029` converts service showcase, boilerplate, docs,
observability practice, data practice and deployment-generator signals into
product requirements for CloudRING reference service portfolio evidence. The
pass is intentionally bounded: it does not claim live runtime execution,
production template readiness, provider publication, vulnerability absence,
dependency/license review or full source/history coverage.

## Scope

| Dimension | Value |
|---|---|
| Source classes | Legacy platform prototype |
| Source slice | Reference/showcase services, service boilerplate, docs scaffold, observability guidance, data practice guidance and generated local deployment patterns |
| Source-safe method | Paraphrased product lessons only; no raw code, commands, private paths, endpoints, dependency lists, commit subjects, credentials, local values or company names |
| Agent work | Three read-only explorers reviewed showcase archetypes, boilerplate/docs/readiness evidence and existing requirements integration separately |

## Key Lessons

| Signal | Product Meaning | Requirement Treatment |
|---|---|---|
| Showcase services cover multiple archetypes rather than one sample. | Reference evidence must prove a portfolio: minimal runtime, documented service, observable service, task/data service, object artifact integration and secret-store integration. | `CR-REFSVC-001..004`, `CR-REFSVC-024..025` |
| Some examples are executable while others are docs or scaffold oriented. | Docs-only, executable, integration, task, release and production claims must be separated. | `CR-REFSVC-005`, `CR-REFSVC-020..021`, `CR-CONF-050` |
| Manifest/service contract appears as the stable product entrypoint while direct/debug paths are useful for development. | The portfolio must keep contract source-of-truth separate from debug and generated artifacts. | `CR-REFSVC-006..010`, `CR-SVCDEPLOY-001..032` |
| Observable reference service demonstrates logs, metrics, traces and error-reporting patterns. | Observability proof must describe semantics, context/correlation and support story, not only middleware presence. | `CR-REFSVC-017..019`, `CR-SUPDIAG-001..032` |
| Task examples include operational and domain-like tasks. | Task reference evidence must classify task intent and prove completion/failure/retry semantics. | `CR-REFSVC-013..014`, `CR-EXTAUTO-001..032` |
| Integration examples show object artifact and secret-store dependency patterns. | Dependency examples must prove managed capability interaction while excluding raw values and production claims. | `CR-REFSVC-011`, `CR-REFSVC-015..016`, `CR-SECRETRUN-001..032` |
| Boilerplate docs have the right pages but can remain placeholder-heavy. | Docs scaffold is not docs readiness until overview, interface, architecture, runbook, FAQ, owner and freshness are filled. | `CR-REFSVC-020..021`, `CR-DOCMEM-001..032` |
| Data practice guidance emphasizes ownership, change discipline and explicit behavior. | Data-backed reference services must prove schema/resource ownership and migration/change expectations. | `CR-REFSVC-012`, `CR-STATEFULRUN-001..032` |
| Existing requirements already cover workflow, deployment, docs, support, release, portal/UI, catalog and integration. | New work must be a portfolio evidence gate that links those proofs without absorbing them. | `CR-REFSVC-029..032`, `CR-CAPEVID-040` |

## Added Requirements And Artifacts

| Artifact | Purpose |
|---|---|
| [../49-reference-service-portfolio-evidence.md](../49-reference-service-portfolio-evidence.md) | Adds `CR-REFSVC-001..032` for reference service portfolio evidence. |
| [../templates/reference-service-portfolio-evidence-template.md](../templates/reference-service-portfolio-evidence-template.md) | Adds reusable reference service portfolio evidence template. |
| [../examples/reference-service-portfolio-evidence-example.md](../examples/reference-service-portfolio-evidence-example.md) | Adds source-safe synthetic filled example. |
| [../scenarios/stage1/SCENARIO-STAGE1-010-reference-service-portfolio-evidence.md](../scenarios/stage1/SCENARIO-STAGE1-010-reference-service-portfolio-evidence.md) | Adds Stage 1 reference service portfolio scenario. |

## ID Changes

- Added `CR-REFSVC-001..032`.
- Added `CR-CONF-050`.
- Added `CR-CAPEVID-040`.
- Added `CR-SPECTPL-044`.
- Added `CR-SPECEX-032`.
- Added `WS-042`.
- Added `CONF-STAGE1-026`.
- Added `SCENARIO-STAGE1-010`.

## Non-Claims

This pass does not prove:

- live execution of the reference services;
- production template readiness;
- final language, framework, runtime or tool choice;
- provider catalog publication;
- portal or embedded UI readiness;
- production deployment, scaling, performance or SLA;
- security vulnerability absence;
- dependency/license correctness;
- full line-by-line or all-history source coverage.

## Source-Safety Notes

- Requirements use product concepts and synthetic examples only.
- Old service names, exact commands, local values, source paths, endpoints,
  package/import names, dependency lists, credentials and private operational
  details are intentionally not preserved.
- A private-marker scan and strict-secret scan must pass after integration.
