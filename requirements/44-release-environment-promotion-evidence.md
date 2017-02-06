# Release Environment Promotion Evidence

## Назначение

Release Environment Promotion Evidence фиксирует требования к тому, как
CloudRING доказывает, что модуль, сервис, task image, UI bundle, base image или
provider artifact можно безопасно продвигать между окружениями и откатывать.

Главный урок source slice: наличие CI-файла, build script, lockfile, Dockerfile,
values/profile файла, release badge, manual job, tag или локального архива
полезно как сигнал, но не доказывает controlled promotion. CloudRING должен
собирать release evidence как цепочку: что именно выпущено, из каких входов,
каким runner, с какими проверками, в какой profile/environment bundle, кем
одобрено, как откатывается и какие non-claims остаются.

Этот документ описывает what/why/evidence. Он не выбирает CI-систему, registry,
package manager, builder, image format, orchestrator, cloud backend, signing
tool, SBOM tool or deployment mechanism.

## Product Boundary

- Releasable module - unit of product release: service, control-plane module,
  task image, UI extension, base image, connector, template or documentation
  package.
- Release candidate - artifact and evidence bundle that passed declared checks
  but is not yet promoted.
- Promotion - audited transition of one immutable artifact identity to a target
  environment/profile/scope.
- Environment bundle - source-safe set of profile, placement, policy, config,
  secret references and compatibility data for a target environment.
- Runner semantics - where and under which trust boundary a build/test/promotion
  action ran: local, CI, private runner, provider runner or managed CloudRING
  runner.
- Release ledger - append-only record that links source revision class,
  artifact identity, dependency lock, test results, source safety, approval,
  promotion target, rollback target and non-claims.
- Rollback record - explicit evidence that previous usable state is retained or
  that rollback is impossible with visible consequences and approval.

## Source-Derived Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| CI/build/test/lint/integration entrypoints existed, but external pipeline behavior was not fully visible. | Entry points are not proof that checks passed for a release. | `CR-RELPROM-001..006`, `CR-RELPROM-021` |
| Separate environment/profile files existed for development, staging-like and production-like targets. | Profile separation is useful, but promotion must prove bundle completeness and parity limits. | `CR-RELPROM-007..010`, `CR-RELPROM-020` |
| Encrypted secret-shaped values and plaintext/local secret-shaped values both appeared as evidence classes. | Release evidence must classify and redact secret-adjacent material in every environment, not only production. | `CR-RELPROM-011..013`, `CR-SECRETRUN-*` |
| Tags and badges existed in one source class, while another had branch-shaped history without release tags. | Tags are useful release signals, not sufficient promotion or rollback evidence. | `CR-RELPROM-014..016`, `CR-RELPROM-026` |
| VM/base-image build flow looked build-per-environment rather than artifact promotion. | CloudRING should promote immutable artifacts forward instead of rebuilding separately unless exception is explicit. | `CR-RELPROM-017..018`, `CR-BASEIMG-*` |
| Task image and frontend modules had mixed build/test/lockfile confidence. | Module boundary and lock strategy must be part of release readiness. | `CR-RELPROM-019`, `CR-RELPROM-022..025` |
| Manual job/readme steps existed but approval trail was not provenance-grade. | Manual execution is not approval. | `CR-RELPROM-027..028` |
| Rollback, previous artifact retention and last-known-good mapping were weak or absent. | Rollback must be first-class release evidence. | `CR-RELPROM-029..031` |
| Source included legacy/prototype and current-tree-only slices. | Release lessons must preserve signal without claiming production readiness. | `CR-RELPROM-032`, `CR-SRCOV-*` |

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-RELPROM-001 | Release readiness must be an evidence chain, not a build result. | A successful build can hide missing tests, secrets, approval, promotion or rollback. | Evidence links module identity, source revision class, dependency lock, build result, test result, artifact identity, environment bundle, approval, promotion state, rollback and non-claims. |
| CR-RELPROM-002 | Every releasable module must declare module type and ownership. | Services, UI bundles, task images and base images have different release risks. | Module record states type, build owner, runtime owner, support owner, evidence owner, release owner and target stages. |
| CR-RELPROM-003 | Build, test, package, publish and promote must be separate states. | Combining them makes local success look like provider readiness. | Release ledger records each state with status, runner class, evidence ref, freshness and blocker/non-goal. |
| CR-RELPROM-004 | Check existence must not count as check success. | A script, config or CI entrypoint only proves intent. | Evidence distinguishes declared check, executed check, passed check, skipped check, stale check, external check and unknown check. |
| CR-RELPROM-005 | Test confidence must be scoped by kind. | Unit, lint, integration, smoke, e2e, first-boot and publication checks prove different things. | Release record labels each check kind, target, input artifact, result, coverage limits and required next check. |
| CR-RELPROM-006 | External pipeline or delegated runner behavior must be visible or marked unknown. | Hidden CI logic can become a new lock-in point. | Runner evidence states local/CI/private/provider/managed runner, trust boundary, inputs, outputs, logs redaction, permissions and non-claims. |
| CR-RELPROM-007 | Environment bundles must be explicit product objects. | Promotion cannot be reviewed if profile/config/secret/placement are implicit files. | Bundle contains profile id, target scope, placement class, config classes, secret references, policy result, compatibility and source-safety status. |
| CR-RELPROM-008 | Environment promotion must state parity and differences. | Staging-like success is not production equivalence. | Promotion report lists parity claims, known differences, missing values, placeholders, degraded states and blocker/warning decision. |
| CR-RELPROM-009 | Production/provider promotion must require complete environment bundle. | Missing or placeholder config can create silent runtime or billing failures. | Promotion blocks if required config/secret refs, owners, policy, health checks, support and rollback targets are missing or unknown. |
| CR-RELPROM-010 | Development/test environments must follow secret policy too. | Unsafe dev evidence often leaks into docs, agents and release records. | All environment bundles pass secret classification, redaction and raw-value exclusion, with documented exceptions and review triggers. |
| CR-RELPROM-011 | Encrypted payloads are still sensitive evidence. | Encrypted blobs, key metadata and secret field names can leak topology or future attack surface. | Evidence stores redacted classification and custody status, not encrypted payloads, decrypted values, key material or raw secret-shaped config. |
| CR-RELPROM-012 | Release evidence must classify topology-adjacent values. | Hostnames, endpoints, network addresses and connection strings can expose private operations. | Source-safety scan redacts topology, endpoints, connection data, tenant data, internal URLs, CI tokens and secret-shaped examples. |
| CR-RELPROM-013 | Decryption/use of secret material in runners must have cleanup evidence. | Build and promotion jobs can leave residue. | Runner evidence includes secret injection method, no-raw-log proof, cleanup/scrub status, retained artifacts and failure behavior. |
| CR-RELPROM-014 | Release tags must have a canonical policy. | Mixed debug, pre-release, lightweight or ambiguous tags weaken audit. | Policy defines canonical release tag, pre-release/debug handling, signing/attestation expectation, owner and exception process. |
| CR-RELPROM-015 | A tag or badge must not count as promotion. | Tags show version intent, not target environment state. | Promotion record links tag/version signal to artifact identity, environment bundle, check results, approval and target activation evidence. |
| CR-RELPROM-016 | Release history must support repeated-fix learning. | Fix/test/tag churn without regression evidence becomes recurring toil. | Repeated release failure cluster creates regression, conformance check, runbook, ADR or owner-approved no-change rationale. |
| CR-RELPROM-017 | Immutable artifact identity must be promoted forward. | Rebuilding per environment can produce unreviewable drift. | Promotion uses digest/immutable id and records if rebuild-per-environment is used, why, what changed and how equivalence is proven. |
| CR-RELPROM-018 | Base image and VM release must be artifact-first. | Image readiness is not proved by builder job success. | Evidence links source revision, builder identity, base media checksum/class, provisioning inputs, cleanup/sealing, first-boot smoke, artifact id, alias/pointer and rollback target. |
| CR-RELPROM-019 | Task image release must have its own release record. | Tooling containers can mutate data, expose env or become hidden supply chain. | Record includes task contract, base image identity, embedded tool versions, dependency summary, smoke test, scope, publish destination class, deprecation and rollback. |
| CR-RELPROM-020 | UI release must separate build, type-check, test, preview and publication. | A frontend can build locally while failing runtime, accessibility or store publication expectations. | UI release evidence labels build, type-check, unit, e2e, accessibility/localization, preview, artifact identity and publication readiness separately. |
| CR-RELPROM-021 | Local archives or imports are local evidence only. | A tarball/import proves convenience, not registry publication or provider deployment. | Evidence labels local artifact class and blocks publication claims until registry/provenance/promotion records exist. |
| CR-RELPROM-022 | Each module must have one authoritative dependency lock strategy. | Mixed lockfiles and moving dependencies break reproducibility. | Module declares package manager/lock family or explicit multi-manager policy, with checksum/provenance evidence and exception expiry. |
| CR-RELPROM-023 | Floating dependency/tool/image references are development evidence unless approved. | Mutable inputs make release recreation and incident analysis unreliable. | Release blocks or warns on mutable base images, tool installs, package snapshots or role references without owner-approved exception and rollback path. |
| CR-RELPROM-024 | Toolchain version expectations must be evidence, not tribal memory. | Agents and runners need reproducible build/runtime context. | Module record includes language/runtime/toolchain version source, compatibility range, runner match, drift detection and non-claims. |
| CR-RELPROM-025 | Scaffold/demo modules must not be treated as releasable modules by default. | Examples often lack checksums, tests, support or runtime ownership. | Module is marked demo/scaffold/local-only until ownership, checks, artifact identity, source safety and promotion record are present. |
| CR-RELPROM-026 | Release coverage must record history availability. | Current tree and tags do not prove deleted-path or all-ref decisions. | Source pass states current-tree, refs/tags/deleted-path treatment, dirty state if known and no-full-history non-claims. |
| CR-RELPROM-027 | Manual trigger is not approval. | A human pressing run does not prove policy, risk or business acceptance. | Approval artifact records approver, reason, scope, risk, policy result, expiry/review and revocation/rollback expectation. |
| CR-RELPROM-028 | Production/provider promotion must have protected decision boundary. | High-impact rollout should not be implicit in build permissions. | Report shows dual-control or accepted single-owner exception, protected scope, policy checks, audit and emergency bypass rules. |
| CR-RELPROM-029 | Rollback must be planned before promotion. | Rollback discovered during incident is too late. | Promotion includes previous artifact/bundle, eligibility, health checks, data compatibility, user impact, owner and irreversible warning if rollback is impossible. |
| CR-RELPROM-030 | Stable names and aliases must be controlled pointers, not mutable truth. | Overwriting "latest" or a template name can erase recovery context. | Alias/pointer update is atomic/audited, previous target retained, consumers visible, cache behavior known and rollback target preserved. |
| CR-RELPROM-031 | Release record must include post-promotion verification and retention. | Activation can fail after promotion and evidence can disappear. | Evidence includes smoke/health/support checks after promotion, retained logs/artifacts, retention policy and stale evidence review trigger. |
| CR-RELPROM-032 | Source-derived release lessons must not claim production readiness. | Old sources preserve experience, not current operational proof. | Pass output states source class, coverage, limits, non-claims and avoids raw commands, configs, endpoints, secret payloads, commit subjects and private names. |

## Evidence Shape

Minimum evidence for release/promotion readiness:

- module identity, type and owners;
- source revision class and coverage status;
- dependency lock and toolchain evidence;
- build/package result with runner semantics;
- test/check matrix with confidence and limits;
- immutable artifact identity and provenance;
- environment bundle and parity/difference statement;
- secret/topology redaction and source-safety scan;
- approval and policy decision;
- promotion target and activation evidence;
- rollback/alias/retention evidence;
- post-promotion health/support evidence;
- explicit non-claims.

## Stop Conditions

Agent обязан остановиться и запросить owner/ADR/approval, если:

- build success, tag, badge, CI entrypoint, local archive or readme step is used
  as promotion readiness;
- artifact identity, environment bundle, runner semantics, approval or rollback
  target is missing;
- release evidence contains raw paths, endpoints, network values, secret-shaped
  values, encrypted payloads, internal URLs, tenant data, commit subjects or
  source snippets;
- debug/pre-release tag is treated as canonical production/provider release;
- mutable dependency, mutable base image or floating tool install is used
  without scoped exception;
- staging/test evidence is claimed as production parity without difference
  record;
- manual trigger is treated as approval;
- rollback is unknown while promotion changes provider/public/private users;
- source-derived evidence claims full history, production deployment or safe
  secret handling without coverage proof.

## Non-Goals

- Не выбирать финальную CI/CD, registry, signing, SBOM, package manager,
  deployment or image-builder technology.
- Не требовать full production-grade pipeline for every local prototype, если
  scope честно ограничен.
- Не хранить raw CI logs, command lines, profile files, env files, encrypted
  payloads, dependency lists or commit subjects.
- Не считать этот pass security, vulnerability, dependency-license or live
  deployment audit.
