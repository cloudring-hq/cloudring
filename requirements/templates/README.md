# Specification Templates

Эта папка хранит source-safe templates для заполнения будущими агентами.
Templates описывают форму доказательств и продуктовых контрактов, а не выбор
технологии реализации.

## Templates

- [ocs-service-manifest-template.md](ocs-service-manifest-template.md) -
  product-level service manifest shape for Open Cloud Standard.
- [ocs-supporting-contract-templates.md](ocs-supporting-contract-templates.md) -
  manifest field matrix, environment/profile precedence, validation code catalog
  and generated artifact provenance shapes.
- [conformance-report-template.md](conformance-report-template.md) -
  readiness report shape for stage and capability conformance.
- [evidence-bundle-template.md](evidence-bundle-template.md) -
  reusable evidence bundle shape for conformance, support, source intake and
  product flows.
- [profile-change-record-template.md](profile-change-record-template.md) -
  conformance profile evolution record shape.
- [role-scenario-fixture-template.md](role-scenario-fixture-template.md) -
  role-based product scenario fixture for user/admin/provider/ISV/support/
  governance/agent journeys.
- [source-coverage-manifest-template.md](source-coverage-manifest-template.md) -
  source intake and history coverage manifest shape.
- [product-design-quality-review-template.md](product-design-quality-review-template.md) -
  task-based review shape for visible consequences, alternatives, economics,
  jurisdiction, failures and human-agent parity.
- [ocs-information-model-template.md](ocs-information-model-template.md) -
  OCS model version, artifact kind registry, canonical field catalog, extension
  lifecycle, conformance suite and schema governance shape.
- [billing-runtime-evidence-template.md](billing-runtime-evidence-template.md) -
  billing runtime evidence shape for usage receipt/status, idempotency,
  backpressure, replay, release history and settlement freeze.
- [stateful-readiness-evidence-template.md](stateful-readiness-evidence-template.md) -
  stateful recovery evidence shape for topology, backup, restore, PITR,
  failover, audit findings, access controls and source safety.
- [documentation-decision-memory-template.md](documentation-decision-memory-template.md) -
  documentation, ADR/no-ADR, source-pass, freshness, feedback and source-safety
  evidence shape for product decision memory.
- [secret-runtime-readiness-evidence-template.md](secret-runtime-readiness-evidence-template.md) -
  encrypted secret runtime evidence shape for scope binding, key custody,
  reconciliation, install/delete, observability, release/source evidence and
  source safety.
- [service-dependency-deployment-evidence-template.md](service-dependency-deployment-evidence-template.md) -
  service dependency/deployment evidence shape for effective model, dependency
  graph, generated artifacts, env handoff, preflight, portability and source
  safety.
- [base-os-image-readiness-evidence-template.md](base-os-image-readiness-evidence-template.md) -
  base OS image readiness evidence shape for build inputs, unattended install,
  provisioning, guest readiness, cleanup, artifact lifecycle and source safety.
- [ui-extension-runtime-certification-template.md](ui-extension-runtime-certification-template.md) -
  UI extension runtime certification shape for embed contract, host authority,
  validation parity, browser evidence, accessibility, publication and source
  safety.
- [settlement-closure-evidence-template.md](settlement-closure-evidence-template.md) -
  settlement closure evidence shape for closure runs, reconciliation, freeze,
  disputes, participant shares, approvals, closeout export and source safety.
- [presence-bootstrap-activation-template.md](presence-bootstrap-activation-template.md) -
  presence bootstrap activation shape for trusted assets, config schema,
  preflight, runtime provider state, diagnostics, rollback, offline/private
  distribution and source safety.
- [controlled-extension-task-automation-template.md](controlled-extension-task-automation-template.md) -
  controlled task, plugin, dependency mutation and boilerplate automation shape
  for trust, scope, redaction, rollback, structured result and agent approval.
- [service-registry-catalog-publication-template.md](service-registry-catalog-publication-template.md) -
  service registry/catalog publication shape for identity, visibility,
  lifecycle, evidence links, sync/cache, source coverage and source safety.
- [developer-workflow-scenario-evidence-template.md](developer-workflow-scenario-evidence-template.md) -
  developer workflow scenario shape for role intent, prerequisites, steps,
  negative cases, cleanup, e2e scope, confidence and source safety.
- [release-environment-promotion-evidence-template.md](release-environment-promotion-evidence-template.md) -
  release promotion shape for artifact identity, environment bundle, checks,
  runner semantics, approval, rollback and source safety.
- [product-service-integration-contract-template.md](product-service-integration-contract-template.md) -
  product-service integration shape for product identity, scoped access,
  resource lifecycle, docs/spec drift, submission semantics, fixtures, handoff
  and source safety.
- [support-diagnostics-evidence-template.md](support-diagnostics-evidence-template.md) -
  support diagnostics shape for lifecycle state, correlation, primary failure
  story, operational signals, image/stateful evidence, export control and
  source safety.
- [support-case-sla-credit-evidence-template.md](support-case-sla-credit-evidence-template.md) -
  support case, SLA clock, credit/refund review, party-scoped view and
  agent-handoff evidence shape.
- [portal-experience-evidence-template.md](portal-experience-evidence-template.md) -
  portal/self-service UI evidence shape for role journeys, action parity,
  consequences, mode claims, support handoff, party-scoped views and agent
  boundaries.
- [reference-service-portfolio-evidence-template.md](reference-service-portfolio-evidence-template.md) -
  reference service portfolio evidence shape for archetype coverage, first
  useful behavior, contract/run-mode boundaries, docs/template readiness,
  observability, task/data/object/secret proof, support handoff and non-claims.

## Rules

1. Keep filled templates generic, paraphrased and source-safe.
2. Link filled templates to `CR-*`, `ADR-*`, `STAGE-*`, workstream and profile
   references.
3. Treat unknown evidence as unknown, warning or blocker.
4. Do not paste source code, private names, internal endpoints, hostnames,
   credentials, tenant data, exact commands or raw match output.
5. Record limitations and non-claims; do not infer full source coverage from a
   narrow scan.
