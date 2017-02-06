# Capability Contract - Security Secrets And Supply Chain

## Назначение

Security Secrets And Supply Chain защищает CloudRING от главного риска открытой
cloud-of-clouds сети: каждый service, connector, plugin, image, template,
usage gateway, UI extension and AI-agent action становится trust boundary. Этот
contract фиксирует продуктовые требования к secret handling, brokered access,
artifact integrity, build provenance, image hardening, extension isolation,
credential lifecycle, audit and source safety.

Contract описывает security promises. Он не выбирает конкретный secret manager,
signing format, CI system, scanner, SBOM format or policy engine.

## Продуктовая Граница

- Secret Boundary controls references, encryption, brokered access, rotation,
  revocation and audit.
- Supply Chain controls source, dependencies, templates, images, artifacts,
  signatures, provenance and deprecation.
- Extension Trust controls connectors, plugins, UI extensions and generated
  code boundaries.
- Runtime Security controls least privilege, tenant isolation, redaction,
  emergency containment and evidence.
- Source Safety controls legacy/source intake anonymization and copyright-safe
  memory.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SECSUPPLY-001 | Secret values must never be stored in manifests, requirements, generated specs, logs or agent context. | Secrets leak through documents faster than systems. | Validation blocks plaintext secret values and allows only secret references or brokered capabilities. |
| CR-SECSUPPLY-002 | Secret access must be brokered and purpose-scoped. | Agents and services need capabilities, not raw credentials. | Access grant shows actor, purpose, resource, environment, expiry, approval and audit without exposing value. |
| CR-SECSUPPLY-003 | Encrypted configuration must distinguish encrypted secret data from normal config. | Mixed config creates accidental leaks. | Product config marks secret fields, sensitive-private fields, public-catalog fields, generated fields, local-only fields, encryption boundary, owner and rotation/rebinding behavior. |
| CR-SECSUPPLY-004 | Secret rotation and revocation must be product lifecycle operations. | Compromise response must not require platform rewrite. | Rotation/revocation plan shows affected services, downtime risk, validation, rollback/compensation and audit. |
| CR-SECSUPPLY-005 | Service credentials must be scoped by product, resource, environment and action. | Broad tokens create cross-product blast radius. | Credential record shows allowed products/resources/actions/environments and cannot bill/control unrelated product. |
| CR-SECSUPPLY-006 | Credential freshness and sync state must be visible. | Cached or stale permissions can accept wrong actions. | Access state shows active, stale, revoked, pending-sync or degraded with timestamp, source, last successful sync, source health and fail-open/fail-closed behavior. |
| CR-SECSUPPLY-007 | Usage/API gateway access must authenticate and authorize product scope. | One service must not submit usage or actions for another. | Gateway decision verifies service/product/resource scope and records accepted/rejected/quarantined reason. |
| CR-SECSUPPLY-008 | Sensitive logs/traces/docs must be redacted by default. | Observability and docs are common leak channels. | Redaction policy covers secrets, tokens, tenant data, internal topology, source-derived context, generated docs/specs, examples and CI diagnostics. |
| CR-SECSUPPLY-009 | Artifact provenance must be recorded for service builds, images, connectors and plugins. | Marketplace trust requires knowing what was built from what. | Artifact record links source reference, builder, inputs, dependencies, version, owner, integrity evidence and timestamp. |
| CR-SECSUPPLY-010 | Artifact integrity must be verifiable before install/publish/run. | Federation cannot trust arbitrary binaries or images. | Install/publish checks signature/digest/provenance or marks artifact untrusted/blocked/manual-review. |
| CR-SECSUPPLY-011 | Image/template factory must include hardening and cleanup evidence. | Golden images can carry build secrets, debug state and insecure access. | Image readiness shows hardening baseline, pre/post cleanup manifest retained outside the image, cleanup idempotence, known leftovers, guest/bootstrap readiness, emergency access boundary and known limitations. |
| CR-SECSUPPLY-012 | Image/template must support post-failure diagnostics without unrestricted exposure. | Serial/debug/crash evidence helps recovery but can leak data. | Diagnostic capability declares enabled/disabled/restricted state per profile, approval path, collection scope, redaction, retention and audit requirements. |
| CR-SECSUPPLY-013 | Dependencies and template libraries must be versioned and updateable. | Unpinned or stale dependencies create supply-chain drift. | Dependency record shows immutable identity or approved exception, source/base image trust, checksum or equivalent trust evidence, update path, compatibility impact, freshness, source/registry allowlist where relevant and deprecation status. |
| CR-SECSUPPLY-014 | Build and release pipelines must publish validation evidence. | Users need proof, not just artifact existence. | Release evidence includes tests, conformance, security checks, artifact integrity and known exceptions. |
| CR-SECSUPPLY-015 | Connector/plugin execution must be sandboxed or explicitly bounded. | Extensions are executable trust boundaries. | Extension contract declares permissions, data access, network access, secret access, lifecycle and support owner. |
| CR-SECSUPPLY-016 | UI extension must not bypass portal permissions and validation. | Embedded UI can become policy bypass. | UI extension receives scoped context, typed inputs, allowed actions, lifecycle events, validation contract, telemetry/redaction boundary, permissions and isolation boundary without raw credentials or host authority takeover. |
| CR-SECSUPPLY-017 | Validation libraries/rules must be source of policy-consistent input checks. | UI-only validation is not enough, but UX should catch errors early. | Same business rule has human-readable error, machine-readable code and server/agent validation equivalent where needed. |
| CR-SECSUPPLY-018 | Tenant isolation must be explicit in every runtime and extension contract. | Cloud-of-clouds must assume partial trust. | Contract states tenant boundary, shared resources, data flow, audit and failure isolation. |
| CR-SECSUPPLY-019 | Emergency containment must be predefined and auditable. | Security incidents require speed without hidden governance bypass. | Emergency action references trigger, scope, actor, approval policy, containment evidence and retrospective follow-up. |
| CR-SECSUPPLY-020 | Federation trust anchors must be replaceable and not single-owner lock-in. | Trust root can become platform lock-in. | Trust model supports rotation, revocation, distributed governance and offline verification where relevant. |
| CR-SECSUPPLY-021 | Participant/service suspension must preserve customer data control where policy permits. | Security response must not become data loss. | Suspension record shows reason, scope, allowed export/recovery, appeal/remediation and unaffected resources. |
| CR-SECSUPPLY-022 | Source intake must be anonymized and copyright-safe. | Requirements memory should survive without leaking source text. | Source-derived requirement links signal/category, not private names, source snippets, local paths or secret values. |
| CR-SECSUPPLY-023 | Security conformance must be stage-aware. | Stage 1 and Stage 6 need different proof. | Readiness report lists required security evidence, accepted non-goals, exceptions and future-stage blockers. |
| CR-SECSUPPLY-024 | AI-agent security actions must follow risk and approval matrix. | Agents should help security, not create invisible root. | Agent action includes identity, scope, risk class, approval, validation, final evidence and no raw secret exposure. |
| CR-SECSUPPLY-025 | Vulnerability and compatibility downgrades must affect marketplace/federation availability. | Users must be protected after trust changes. | Critical trust downgrade updates offer visibility, warnings, blocks, support guidance and remediation path. |
| CR-SECSUPPLY-026 | Security learning must feed requirements, ADR, runbooks and conformance. | Repeated security issues should harden the product. | Incident/drift closes with artifact update or explicit no-change rationale. |
| CR-SECSUPPLY-027 | Brokered secret access must produce a decision ledger. | Secret access must be explainable after the value is gone. | Ledger records actor, delegated subject, purpose, resource, environment, expiry, approval, broker boundary, key owner, freshness and outcome without secret value. |
| CR-SECSUPPLY-028 | Secret fields must be classified by machine-readable policy. | Encrypted and plain configuration look similar to agents. | Config/schema marks secret, sensitive, public and generated fields across all profiles and generated artifacts; validation blocks plain secret-like values where reference/encrypted value is required. |
| CR-SECSUPPLY-029 | Broad secret scope must require explicit risk approval. | Sometimes bootstrap requires broad access, but it must not become default power. | Broad scope record shows owner, reason, allowed scopes, approval, expiry/review date and compensating controls. |
| CR-SECSUPPLY-030 | Artifact trust gate must require immutable identity. | Tags, mutable names and intended locations are not enough for marketplace/federation trust. | Publish/install/run checks actual built artifact identity, digest or equivalent immutable identity, provenance, registration evidence, signature/attestation, dependency lock consistency, SBOM or approved exception. |
| CR-SECSUPPLY-031 | Image/template hardening must prove final credential residue is absent. | Image build secrets and bootstrap accounts often survive cleanup. | Readiness evidence covers final users/access, privileged bootstrap users, sudo posture, local passwords or locked accounts, authorized keys, build args, shell history, host identity regeneration, automation residue, cleanup result and diagnostic boundary. |
| CR-SECSUPPLY-032 | UI extension trust must be install-time declared. | Raw embedded UI can bypass portal policy. | Extension manifest declares signed or otherwise verified artifact origin, allowed hosts, permissions, scoped context, route/theme boundary, lifecycle support, CSP/sandbox/SRI or equivalent isolation, redaction status, support owner and publishable-build restrictions. |
| CR-SECSUPPLY-033 | Source/history hygiene must trigger rotation and remediation. | Old repositories, generated docs, config examples and validation outputs can contain security-class material even after cleanup. | Discovery of secret-class material creates rotation decision, affected-scope review, remediation evidence and source-safe requirement update. |
| CR-SECSUPPLY-034 | Security and billing validation rules must have parity and safety budgets. | UI-only or unsafe validation creates bypass and denial risks. | Critical validation rule has server/agent equivalent, machine-readable code, max input/pattern size where relevant, safe engine or approved exception, timeout/runtime budget, untrusted-pattern policy, redacted sensitive params and tested failure mode. |
| CR-SECSUPPLY-035 | Readiness above prototype/reference must require release evidence. | Unreleased artifacts should not become provider/store promises. | Release evidence includes immutable artifact identity, source/ref or tag discipline, provenance, validation result, known exceptions, registration/publication result, rollback/deprecation note and owner. |
| CR-SECSUPPLY-036 | Critical validation rules must include negative fixtures. | Validation parity is not proven by happy-path checks. | Rule evidence includes shared identity, human message, machine code, client/server/agent parity, bounded runtime/size behavior and negative fixtures for empty, malformed, boundary, overlong, invalid type, event ordering, conditional transition and worst-case pattern inputs where applicable. |
| CR-SECSUPPLY-037 | Image/template readiness evidence must have freshness score. | A hardened image becomes stale as dependencies and threats change. | Readiness report shows provenance, dependency/base image state, cleanup/final credential residue check, diagnostic boundary, known limits, freshness, next due date and stale-build blocker or exception. |
| CR-SECSUPPLY-038 | Operational evidence artifacts must be source-safe before reuse. | Audit logs, grants, IaC state, inventories and encrypted material can leak old environments into product memory. | Source intake or publication evidence classifies topology, grants, logs, IaC state, generated audit output and encrypted material; raw values are redacted, scoped or excluded before requirements, generated specs, agent context or marketplace artifacts. |
| CR-SECSUPPLY-039 | Controlled automation artifacts must pass trust, scope and redaction gates before managed execution. | Task images, plugin binaries, dependency tools and templates are executable supply-chain surfaces. | Evidence links immutable artifact identity, provenance/integrity, version pinning or exception, allowlist policy, scope, env/secret boundary, sandbox/boundary limits, redacted output and rollback/disable path. |

## Evidence

- Secret reference validation report.
- Brokered access grant and audit.
- Brokered secret access decision ledger.
- Secret-field classifier and redaction scan across profiles, generated specs,
  examples and CI diagnostics.
- Credential scope/freshness record.
- Usage/API gateway access decision.
- Redaction policy evidence.
- Artifact provenance and integrity record.
- Image/template hardening, pre/post cleanup, final credential residue and
  sealed-image readiness report.
- Extension/plugin/UI trust manifest and sandbox record.
- Dependency/template library version, immutable identity, trust and freshness
  state.
- Release evidence for non-prototype readiness, including immutable identity,
  provenance, ref/tag discipline, validation result and known exceptions.
- Validation parity with negative fixtures, timing evidence and safety budgets.
- Image/template freshness and next-due-date record.
- Emergency containment and retrospective record.
- Source/history hygiene remediation record.
- Operational evidence artifact redaction and source-safety record.
- Controlled automation trust, allowlist, scope and redaction record.
- Secret runtime readiness evidence bundle for encrypted declaration scope, key custody, reconciliation, install/delete, RBAC, health/metrics, rotation and degraded/fail-closed behavior.
- Source intake anonymization check.
- Security conformance report.

## Stage Guardrails

- Stage 1 requires secret-safe templates, local validation and artifact/source
  hygiene.
- Stage 2 requires private secret boundary, local emergency control and
  infrastructure template hardening.
- Stage 3 requires store publication checks for artifacts, connectors, plugins
  and UI extensions.
- Stage 4 requires provider-grade credential lifecycle, tenant isolation and
  support/security incident evidence.
- Stage 5 requires federation trust anchors, scoped sharing, suspension and
  dispute evidence.
- Stage 6 requires global trust propagation without central trust lock-in.
- Stage 7 requires security incidents and drift to update product memory.

## Stop Conditions

Agent обязан остановиться и запросить owner/security approval/ADR, если:

- plaintext secret would enter manifest, docs, requirements, logs or agent
  context;
- action needs raw secret where brokered capability is possible;
- brokered secret access lacks purpose, expiry, owner, approval or ledger;
- secret-like config value appears outside encrypted/reference boundary;
- credential scope is broad, stale, ownerless or unrelated to purpose;
- broad secret scope lacks explicit approval and review/expiry;
- artifact lacks immutable identity, integrity or provenance for publish/install/run;
- provider/store readiness is claimed without release evidence;
- image/template cleanup, hardening or final credential residue evidence is
  missing;
- image/template freshness is expired or unknown for publication/readiness claim;
- plugin/connector/UI extension permissions are undeclared;
- task/plugin/dependency/template automation lacks artifact trust, allowlist,
  scope, redaction or disable/rollback evidence for managed execution;
- UI extension lacks trust manifest or scoped context boundary;
- critical validation lacks parity, negative fixtures or bounded
  runtime/size/pattern behavior;
- trust downgrade does not affect availability or warning state;
- source/history discovery of secret-class material has no rotation/remediation
  decision;
- operational evidence artifact includes raw topology, grant, log, IaC state,
  credential-like value or encrypted material outside a redacted evidence
  boundary;
- source-derived output contains private names, local paths, source snippets or
  secret values.

## Non-Goals

- Не выбирать secret manager, signing system, CI/CD, scanner or SBOM format.
- Не обещать perfect security.
- Не раскрывать internal topology as security proof.
- Не использовать emergency as permanent governance bypass.
- Не переносить private source text into requirements.
