# Source Pass 003 - Image Template Factory

Source pass `SRC-PASS-003` covers the VM/image template factory prototype as a
product signal source for CloudRING artifact trust, private/provider
infrastructure readiness, marketplace publication and support diagnostics.

This file is source-safe. It records categories, product signals, requirements
and limitations. It does not store raw source paths, private names, URLs,
tokens, env values, IPs, commit subjects or implementation snippets.

## Pass Metadata

| Field | Value |
|---|---|
| Pass ID | `SRC-PASS-003` |
| Source class | VM/image template factory prototype |
| Snapshot date | 2026-06-22 |
| Indexed files in source class | 20 |
| Tracked files in git repository | 22 |
| Git commits | 35 |
| Git tags | 0 |
| High-signal categories | Image build contract, build/profile variables, bootstrap, hardening, cleanup, guest readiness, diagnostics, history/release evidence |
| Coverage mode | Current-tree analysis plus git history/theme review |
| Coverage claim | Completed targeted product-signal and history/theme coverage, not full line-by-line vulnerability/secret audit |

## Slice Coverage

| Slice | Coverage Status | Product Signal Focus | Requirement Areas |
|---|---|---|---|
| Build and publication contract | Completed targeted current-tree coverage | Reproducible image build, profile parameters, immutable identity, provenance, artifact inventory, support handoff. | `CR-SECSUPPLY-*`, `CR-MKT-*`, `CR-CATALOG-*` |
| Hardening, bootstrap and diagnostics | Completed targeted current-tree coverage | Guest readiness, cleanup, final credential residue, storage resize, emergency diagnostics, virtualization integration. | `CR-SECSUPPLY-*`, `CR-INFRA-*`, `CR-OPS-*`, `CR-OBSOPS-*` |
| History, release and source safety | Completed all-refs theme coverage | Branch/theme evolution, release evidence gaps, repeated fixes, source-safety risk classes, freshness evidence. | `CR-SRCOV-*`, `CR-STAGE7-*`, `CR-METRIC-*` |

## Initial Product Signals

| Signal | Product Meaning | Current Coverage |
|---|---|---|
| Reproducible image build | A provider/private presence must know what base artifact was built and why it is safe to run. | Covered by supply-chain and marketplace requirements; pass checks evidence gaps. |
| Profile-driven build parameters | Image output must vary by declared profile, not hidden environment convention. | Covered in principle; pass checks source-safety and profile boundary. |
| Guest bootstrap readiness | A VM template must be ready for first boot, identity, network, storage and agent handoff. | Covered by infra/security requirements; pass checks missing readiness states. |
| Hardening and cleanup | Build-time access, debug state and temporary residue must not survive into published images. | Covered; pass checks final residue evidence. |
| Diagnostics without exposure | Serial/debug/crash evidence is necessary for support but can leak sensitive context. | Covered; pass checks approval, redaction and retention shape. |
| Artifact publication handoff | Marketplace/catalog must receive artifact identity, provenance, limitations and support owner. | Covered; pass checks release evidence and inventory gaps. |
| Freshness and dependency drift | A hardened image becomes unsafe or unsupported over time. | Covered; pass checks freshness scoring and next-review evidence. |

## Expected Evidence From Pass

- Source-safe slice summaries for build/publication, hardening/bootstrap/
  diagnostics and history/source-safety evolution.
- Gap list mapped to existing requirement ranges or new requirement updates.
- Updates to coverage manifest, traceability, marketplace/catalog/security or
  conformance if needed.
- Explicit non-claims about vulnerability/secret/line-by-line/runtime coverage.
- Validation after edits: CR IDs, links, private marker scan and secret-pattern
  scan.

## Stop Conditions

Agent must stop and request owner/review if:

- source-derived output would include raw token, env value, endpoint, IP, local
  path, private name, exact source snippet or raw commit subject;
- image publication can happen without immutable identity, provenance, hardening
  and cleanup evidence;
- a build profile contains sensitive/private operational context that would leak
  into requirements or marketplace metadata;
- final image readiness lacks final credential-residue, support owner,
  diagnostic boundary or freshness evidence;
- history coverage claims every decision without all-refs/deleted-path evidence;
- requirements would promote an old image-builder implementation instead of a
  replaceable artifact trust contract.

## Current Status

`SRC-PASS-003` completed a targeted current-tree and all-refs history/theme
review on 2026-06-22. It preserves product signals and requirement gaps for the
image/template factory source class, but it is not proof of runtime image
readiness, vulnerability absence, secret absence, sealed-image state or full
line-by-line source coverage.

## Validation Summary

Latest recorded aggregate validation: 2026-06-22 during `SRC-PASS-006`.
Scope: `requirements/` corpus. Result: CR/stage ID consistency, markdown links,
private-marker scan, strict secret-pattern scan and conflict/trailing-whitespace
checks passed after source-safe repairs. Raw match output is not retained in
this pass file.

## Integrated Slice Results

### Build And Publication Contract

The source signal treats image/template publication as an operational product
promise. A future CloudRING implementation must distinguish a procedural build
workflow from a release-grade artifact:

- build profiles must be declared as a schema with field classes: secret,
  sensitive-private, public-catalog, generated and local-only;
- image build output must produce an actual immutable artifact identity, digest
  or equivalent stable identity, not only a mutable name or intended location;
- publication must include build provenance, source/base image trust, dependency
  state, validation result, known exceptions, support owner, diagnostic boundary
  and rollback/deprecation target;
- catalog registration must have a response/evidence record and must not be
  treated as complete when only a local file or intended location exists;
- CI/build diagnostics must be redacted by default and must not expose private
  topology, raw registration payloads with private context or credential-class
  material;
- local manual build success is useful evidence, but it is not provider/store
  readiness.

These signals refine `CR-SECSUPPLY-003`, `CR-SECSUPPLY-008`,
`CR-SECSUPPLY-013`, `CR-SECSUPPLY-030`, `CR-SECSUPPLY-035`,
`CR-SECSUPPLY-037`, `CR-MKT-029`, `CR-MKT-033`, `CR-MKT-035`,
`CR-CATALOG-021`, `CR-CATALOG-023`, `CR-CATALOG-025` and `CR-CATALOG-026`.

### Hardening, Bootstrap And Diagnostics

The source signal shows that image readiness is not proven by provisioning code
alone. Readiness must be backed by a sealed-image evidence bundle:

- pre/post cleanup manifest retained outside the image, redacted, idempotent and
  explicit about known leftovers;
- final users/access posture, privileged bootstrap users, sudo posture, local
  passwords or locked accounts, authorized access residue, host identity
  regeneration, build args, shell history and automation residue checks;
- first-boot bootstrap validation including resolver/mirror/network policy,
  private/offline mode and no hidden endpoint dependency;
- storage resize validation and degraded/blocked state if first-boot resize
  support is absent;
- guest integration expressed as capability features such as shutdown, network,
  time/signal visibility, support diagnostics and graceful degradation;
- serial/debug/crash diagnostics declared per profile as enabled, disabled or
  restricted, with approval path, collection scope, retention, redaction and
  audit.

These signals refine `CR-INFRA-019..025`, `CR-INFPROFILE-008`,
`CR-SECSUPPLY-011`, `CR-SECSUPPLY-012`, `CR-SECSUPPLY-031`,
`CR-SECSUPPLY-037`, `CR-MKT-031`, `CR-MKT-032`, `CR-MKT-035` and the Stage 2,
Stage 3 and Stage 4 readiness gates.

### History, Release And Source Safety

History review covered all local refs at theme level. The repository had 35
unique all-refs commits, 33 commits reachable from current default HEAD, 2
commits reachable only outside current HEAD, 8 merge commits, 27 non-merge
commits, 1 local branch ref, 3 remote branch refs, 1 remote HEAD pointer, 2
non-default topic refs and 0 tags. Current tracked tree had 22 tracked files;
the source manifest tracks 20 significant product files, leaving a two-file
metadata/support delta. All-history path review found 36 ever-touched paths, 10
deleted paths, 34 add events, 46 modify events, 20 delete events and 2 rename
events.

The strongest change clusters were guest bootstrap/readiness, repo metadata/CI,
docs/release guidance, provisioning automation, image build contract,
scripts/build commands and vars/config/templates. Repeated diagnostics/console
iteration is a Stage 7 learning signal: VM image readiness must require boot and
console diagnostic evidence plus regression or negative-validation coverage.

Source-safety findings stayed at category level. Current and deleted-path
history contained endpoint-like, host-like, environment/profile-context,
absolute-path-like and credential-keyword classes. Credential-assignment-like
material was observed as a risk class in provisioning, image-build and
script/build categories. Any real implementation must perform owner review,
redaction, rotation/remediation decision and source-safe update before sharing
or publishing derived evidence.

### Requirement Updates Made

- Strengthened artifact release identity, registration response, rollback target
  and publication handoff evidence.
- Strengthened image/profile schema classification, generated-output redaction
  and source/history hygiene expectations.
- Strengthened final credential-residue, pre/post cleanup, first-boot,
  storage-resize, diagnostics and freshness evidence.
- Strengthened Stage 2, Stage 3 and Stage 4 readiness gates for image/template
  artifacts.
- Updated source coverage manifest to mark this pass complete as targeted
  current-tree plus history/theme coverage.

### Non-Claims

This pass does not claim:

- every source line or deleted path was audited;
- image build, runtime boot, serial console, crash dump or first-boot resize was
  executed;
- external roles, packages or dependency sources were validated;
- encrypted profiles were decrypted;
- the source is free of vulnerabilities or secrets;
- a locally modified cleanup-script category represents stable release evidence;
- old image-builder technology should be reused.
