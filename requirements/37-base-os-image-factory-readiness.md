# Base OS Image Factory Readiness

Этот документ фиксирует продуктовые требования к фабрике базовых VM-образов
CloudRING. Он не описывает конкретный image-builder, дистрибутив, гипервизор,
роль provisioning или команду сборки. Он отвечает на вопрос: что должно быть
доказано, чтобы базовый образ можно было считать воспроизводимым, переносимым,
source-safe и пригодным для private/provider cloud presence.

`CR-BASEIMG-*` дополняет `CR-INFPROFILE-*` и `CR-SECSUPPLY-*`: infrastructure
profile говорит, какие capabilities есть у presence, а base image factory
evidence доказывает, что host/workload image был создан, подготовлен, очищен,
проверен и продвинут в каталог без скрытого lock-in и приватного контекста.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-BASEIMG-001 | Base OS image factory must be a governed product capability, not a one-off build script. | Облачный провайдер не может опираться на ручные, неповторяемые образы. | Evidence describes purpose, owner, supported profiles, artifact lifecycle, validation gates and non-claims for every base image line. |
| CR-BASEIMG-002 | Base OS selection must state product rationale and support window. | Выбор ОС влияет на security, package freshness, guest tooling, support and exit. | Evidence records OS family/class, support status, update window, unsupported versions and replacement/deprecation plan without freezing one vendor. |
| CR-BASEIMG-003 | Image build inputs must be classified by sensitivity and promotion scope. | Build profiles often mix public defaults, local overrides and private provider data. | Inputs are classified as public default, environment override, generated, secret-adjacent, private-profile or excluded; unsafe classes are redacted before agent handoff. |
| CR-BASEIMG-004 | Environment-specific build profiles must not become product contract. | Profiles are necessary, but their values can lock the image to one backend or private context. | Evidence separates stable product knobs from environment values and marks profile-specific limitations. |
| CR-BASEIMG-005 | Virtualization/backend details must be modeled as replaceable adapter constraints. | Anti-lock-in fails if the image contract is secretly tied to one hypervisor or storage/network backend. | Image readiness records required adapter capabilities, backend-specific assumptions, portability class and alternative adapter gap. |
| CR-BASEIMG-006 | Unattended installation must be explicit evidence, not implied by successful artifact creation. | A built artifact does not explain how locale, users, packages, disk and boot policy were chosen. | Evidence summarizes unattended install choices, owner, policy rationale and hidden-manual-step absence without copying raw answer files. |
| CR-BASEIMG-007 | Disk layout and resize behavior must be product-visible. | Cloud images often fail later because partitions or filesystems cannot grow safely. | Image evidence states root/data/swap policy, grow-on-first-boot behavior, unsupported resize cases and validation status. |
| CR-BASEIMG-008 | Bootstrap account and access policy must be auditable without exposing credentials. | First access must be supportable, but credentials must not enter requirements or agent context. | Evidence records account classes, SSH/console access intent, disabled/temporary access handling, owner and deletion/rotation expectations. |
| CR-BASEIMG-009 | Guest initialization must be part of the image contract. | CloudRING needs first-boot configuration, metadata handling and user-data behavior to be predictable. | Evidence states initialization mechanism, metadata boundary, idempotence expectation, failure state and profile-specific support. |
| CR-BASEIMG-010 | Guest tooling must be declared as capability evidence. | Tools for shutdown, networking, disk resize and status reporting affect provider operations. | Image profile lists guest integration capabilities, health signal, version/freshness class and unsupported backend behavior. |
| CR-BASEIMG-011 | Console and diagnostic access must be designed before incidents. | If SSH or network fails, support needs bounded low-level evidence without uncontrolled privilege. | Evidence describes console/serial/log/crash diagnostic capability, access boundary, audit requirement and redaction rule. |
| CR-BASEIMG-012 | Kernel crash and boot diagnostics must be scoped readiness evidence. | Provider support needs post-failure data, but diagnostics can leak sensitive state. | Evidence states whether crash/boot diagnostics are enabled, where artifacts live, who may access them and how they are redacted. |
| CR-BASEIMG-013 | Package baseline must be minimal, purposeful and freshness-aware. | Bloated or stale base images increase attack surface and maintenance burden. | Evidence lists package classes, purpose, freshness window, known exceptions and owner-approved exclusions without copying package manifests. |
| CR-BASEIMG-014 | Security hardening must be a checklist with evidence and exceptions. | Cleanup or successful boot is not proof of hardening. | Evidence covers access, services, updates, firewall/network assumptions, logging/audit, unsafe defaults, exceptions and review trigger. |
| CR-BASEIMG-015 | Provisioning roles must be composable, idempotent and owner-visible. | Image build logic becomes unmaintainable when roles hide side effects. | Evidence records role purpose, input classes, changed capability, idempotence claim, failure behavior and owner. |
| CR-BASEIMG-016 | External role or dependency sources must have provenance and freshness. | Supply-chain drift can change image behavior without product review. | Evidence records dependency identity, version/pin/freshness class, trust boundary, update policy and unavailable-source behavior. |
| CR-BASEIMG-017 | Cleanup/sealing must remove build residue and machine identity before promotion. | A reusable image must not carry temporary keys, logs, caches, identities or host-specific config. | Seal evidence covers machine identity, temporary credentials, shell history, logs, package cache, generated files, network resolver state and excluded residue. |
| CR-BASEIMG-018 | Cleanup must preserve diagnostic usefulness without leaking private context. | Over-cleaning destroys support value; under-cleaning leaks old environment details. | Evidence states kept, redacted and removed artifacts plus retention reason and support owner. |
| CR-BASEIMG-019 | Image artifact identity must be immutable before catalog or provider use. | Mutable template names cannot prove what tenants will run. | Artifact record includes immutable identity, build timestamp or equivalent, source input fingerprint, role/dependency versions, validation summary and supersession link. |
| CR-BASEIMG-020 | Build output must have provenance that survives source disappearance. | Future agents need to know why the image exists without old source files. | Provenance links product purpose, requirement refs, source-pass refs, input classes, builder identity, artifact identity and non-claims. |
| CR-BASEIMG-021 | Build validation must separate syntax validation, provisioning success and boot readiness. | Passing one layer can still leave an unbootable or unusable image. | Report has separate statuses for config validation, install, provisioning, cleanup, shutdown, first boot, networking, guest initialization and diagnostics. |
| CR-BASEIMG-022 | First-boot smoke test is required before readiness claims. | A template that built once may fail as a fresh instance. | Readiness includes fresh-instance boot, metadata/init result, disk resize check, access check, health signal and cleanup residue scan or an explicit blocker. |
| CR-BASEIMG-023 | Build timing and boot reliability must be tracked as quality signals. | Slow or flaky boot/install loops create operational toil for one human with agents. | Evidence records timeout budget, retries/flakes, known slow stages, remediation owner and trend/threshold where available. |
| CR-BASEIMG-024 | CI validation must be treated as evidence with limits. | Automated validate/build wiring is useful, but it is not a complete image certification. | CI evidence states what was validated, what was not run, freshness, owner, failure handling and promotion blocker rules. |
| CR-BASEIMG-025 | Image promotion must be stage-aware. | Local/dev images, private presence templates and provider catalog images need different evidence. | Promotion record maps local, private, provider and marketplace states to required gates, warnings, non-goals and future-stage gaps. |
| CR-BASEIMG-026 | Template/catalog placement must not hide readiness state. | A folder or catalog entry can look official before evidence is complete. | Catalog entry exposes readiness status, artifact identity, owner, support policy, limitations and deprecation state. |
| CR-BASEIMG-027 | Image rollback and deprecation must be product operations. | Broken base images can affect every future workload. | Evidence shows current, previous, deprecated and blocked image states plus rollback path, affected consumers and removal criteria. |
| CR-BASEIMG-028 | Image factory must include source-safety rules for profiles and evidence. | Build variables can contain private locations, accounts, topology and credentials. | Handoff forbids raw profiles, endpoints, local paths, credentials, private topology and copied source snippets; report includes scan status. |
| CR-BASEIMG-029 | Agent operation of image factory must be bounded by approvals. | Image mutation is high-impact infrastructure work. | Agent handoff defines read-only review, safe evidence drafting, validation requests, approval-gated build/promotion and forbidden privileged actions. |
| CR-BASEIMG-030 | Multi-version and multi-family image roadmap must be explicit when only one family is implemented. | A single base OS can be a valid first slice but must not become hidden platform lock-in. | Evidence marks current supported family/version, unsupported families, abstraction gaps and decision trigger for adding another line. |
| CR-BASEIMG-031 | Source-derived image lessons must be paraphrased and copyright-safe. | Requirements must preserve experience without copying build files or private workflow names. | Source pass stores product abstractions, counts and non-claims; it excludes raw paths, exact commands, private profile names, endpoints, secrets and copied configs. |
| CR-BASEIMG-032 | Base image readiness must state explicit non-claims. | Build evidence can be mistaken for security, compliance, multi-cloud or provider certification. | Evidence says whether it does not prove live provider operation, vulnerability absence, compliance, full history audit, multi-backend support, marketplace publication or production hardening. |

## Evidence Bundle

Minimum evidence bundle for base OS image readiness:

1. Image line identity, purpose, owner, supported stage/profile scope and
   product rationale.
2. Build input classification with public/default, profile override, generated,
   secret-adjacent and excluded classes.
3. Unattended install summary for locale/time/access/disk/package/security
   choices without raw answer files.
4. Provisioning role inventory with owner, idempotence, dependency provenance
   and failure behavior.
5. Guest readiness summary for initialization, guest tooling, disk expansion,
   network/access, console and diagnostics.
6. Cleanup/sealing evidence for machine identity, temporary access, logs,
   caches, generated files and source-private residue.
7. Immutable artifact identity, provenance, freshness, validation and
   supersession/deprecation state.
8. First-boot smoke result, residue scan, source-safety scan and explicit
   non-claims.

## Stop Conditions

Stop and require owner/review when:

- build evidence requires raw profile values, endpoints, credentials, private
  locations, hostnames or copied source configuration;
- a local/dev image is promoted as private/provider-ready without stage-specific
  gates;
- cleanup/sealing evidence is missing before template/catalog publication;
- artifact identity is mutable or cannot be tied to build inputs and validation;
- first-boot smoke test, guest initialization or disk resize evidence is absent
  while readiness is claimed;
- external role/dependency provenance is unknown;
- one backend-specific image is presented as portable without adapter
  limitations and exit story;
- security/compliance readiness is claimed from build success alone.
