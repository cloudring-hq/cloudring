# Open Cloud Standard Information Model And Schema Governance

Этот документ уточняет Open Cloud Standard как продуктовую информационную
модель. Он не выбирает окончательный формат файла, протокол, язык реализации
или runtime. Его задача - сделать стандарт достаточно формальным, чтобы сервис,
connector, marketplace offer, private install, provider publication, federation
sync and AI-agent validation можно было заново реализовать без старых исходных
текстов.

OCS information model is the stable meaning. Serialization is only one possible
representation. If serialization changes, identity, fields, references,
validation, compatibility and evidence semantics must remain explainable and
machine-checkable.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-OCSIM-001 | Open Cloud Standard must have a versioned information model separate from concrete serialization. | Формат файла может устареть, а продуктовый смысл должен жить дольше. | OCS release names model version, supported serializations and compatibility policy. |
| CR-OCSIM-002 | Every OCS artifact must declare standard version, model version, kind, identity, owner and maturity. | Agents and conformance need to know what is being validated. | Artifact header includes version, kind, stable id, owner, maturity and source-safety state. |
| CR-OCSIM-003 | OCS artifact kinds must be explicitly registered. | Без registry сервисный manifest, extension, report and event can drift into incompatible shapes. | Model registry lists artifact kinds, purpose, required sections, references and validation scope. |
| CR-OCSIM-004 | Stage 1 minimum service manifest kind must be defined as a product baseline. | Первый finished product needs the smallest useful contract, not an endless schema project. | Minimum kind covers identity, purpose, owner, profiles, dependencies, lifecycle, observability, docs, support, portability and evidence. |
| CR-OCSIM-005 | Artifact kinds must distinguish service, component, dependency, profile, lifecycle action, task, usage resource, UI descriptor, evidence, extension and change record. | Collapsing these concepts creates hidden lock-in and unreviewable automation. | Registry maps each kind to product owner, lifecycle and allowed references. |
| CR-OCSIM-006 | OCS must have a stable reference model. | Cross-document links are the spine of marketplace, billing, support and audit. | References identify target kind, stable id, version/maturity expectation and missing-target behavior. |
| CR-OCSIM-007 | Field registry must be mandatory for each artifact kind and model version. | A schema without field ownership and compatibility rules will drift. | Field registry records path, purpose, requiredness, type class, owner, default, profile behavior, validation code and deprecation state. |
| CR-OCSIM-008 | Field requiredness must distinguish required, optional, conditional, extension, deprecated and forbidden. | Binary required/optional is too weak for staged cloud products. | Validator reports missing conditional requirements with reason and profile context. |
| CR-OCSIM-009 | Defaults must be visible, reproducible and consequence-aware. | Hidden defaults become lock-in and billing/support surprises. | Effective model report lists default source, affected profile and user/agent-visible consequence. |
| CR-OCSIM-010 | Unknown field policy must be explicit for every artifact kind. | Ignoring unknown fields creates false readiness. | Unknown fields are rejected, quarantined or accepted only as declared extension namespace with owner and compatibility impact. |
| CR-OCSIM-011 | Extension namespaces must be registered with owner, purpose, scope and compatibility class. | Innovation should not fork the standard silently. | Extension registry links namespace to owner, mandatory/optional status, baseline constraints and conformance checks. |
| CR-OCSIM-012 | Extensions must not weaken mandatory identity, secret, lifecycle, policy, billing, trust, support, portability or evidence rules. | Extension freedom must not become a bypass. | Validation runs mandatory baseline before extension checks and blocks weakening attempts. |
| CR-OCSIM-013 | Compatibility classes must be standardized. | Providers and private installations need to know whether a change is safe. | Change is classified as additive, default-changing, profile-scoped, deprecated, breaking or forbidden. |
| CR-OCSIM-014 | Breaking and default-changing model changes must require migration/deprecation evidence. | Ecosystem participants cannot migrate instantly. | Change record names affected artifact kinds, profiles, users, migration window, fallback and conformance impact. |
| CR-OCSIM-015 | Model evolution must use profile change records and ADR linkage when product meaning changes. | Standards cannot evolve through silent parser changes. | Change record links requirements, ADR, conformance profiles and owner approval. |
| CR-OCSIM-016 | Validation code catalog must be part of the model. | UI, API, CLI and Agent API need stable remediation logic. | Catalog separates machine code, message key, field path, severity, retryability, owner and remediation. |
| CR-OCSIM-017 | Validation output must distinguish model error, profile error, policy error, extension error and evidence freshness error. | Different failures have different owners and next actions. | Error object names class, owner, user impact, agent next action and evidence pointer. |
| CR-OCSIM-018 | Effective configuration/model report must be a standard artifact. | Users and agents need to see resolved base, profile, defaults, generated values and secret references. | Report shows resolved values without raw secrets and lists provenance for each resolved field. |
| CR-OCSIM-019 | Secret binding must be reference-only and redacted in model artifacts. | Schema rigor must not encourage storing secrets. | Field registry marks secret-adjacent paths and validator blocks raw secret material. |
| CR-OCSIM-020 | Generated artifacts must reference model version, field registry version and source artifact identity. | Runtime outputs must not become hidden source of truth. | Artifact inventory records source kind/id/version, generator, target profile, freshness and publish boundary. |
| CR-OCSIM-021 | OCS model must support human-agent parity. | One human plus AI agents need the same product facts. | Human docs, manifest, API, CLI and Agent API expose same identity, state, validation, consequence and evidence refs. |
| CR-OCSIM-022 | OCS model must support service card and marketplace decision rendering. | Marketplace should not invent product meaning outside the standard. | Service card can be derived from OCS identity, capability, trust, price/usage, support, portability and limitations fields. |
| CR-OCSIM-023 | OCS model must support support-case and dispute evidence binding. | Cross-provider support and billing need reliable references. | Support/dispute artifacts can reference service, instance, order, usage, policy, evidence and owner without free-text reconstruction. |
| CR-OCSIM-024 | OCS model must support federation-safe partial disclosure. | Participants should share enough to interoperate without exposing internal topology. | Artifact kinds declare publishable, restricted, local-only and redacted fields with purpose. |
| CR-OCSIM-025 | OCS model must support local-to-global promotion without rewriting product meaning. | A service should grow through stages by adding evidence, not by changing identity. | Promotion report shows same identity with added profiles, conformance and limitations. |
| CR-OCSIM-026 | OCS model must support source-safe examples for each mandatory artifact family. | Requirements should survive old sources disappearing. | Examples use synthetic objects only and include non-claims. |
| CR-OCSIM-027 | OCS model must have a machine-checkable conformance matrix. | Readiness should not depend on reviewer memory. | Matrix maps artifact kinds and fields to `CR-*`, ADR, stage, profile and validation code. |
| CR-OCSIM-028 | OCS model must reject product promises that cannot be traced to requirements, evidence or explicit future-stage gaps. | Manifest can otherwise become marketing copy. | Validator marks untraced promise as warning or blocker by profile criticality. |
| CR-OCSIM-029 | OCS model must allow multiple serializations only when they round-trip through the same semantic model. | Multiple formats are useful only if they do not fork meaning. | Round-trip evidence proves identity, required fields, validation results and compatibility classification are preserved. |
| CR-OCSIM-030 | OCS model must treat schema governance as product governance. | Changing the standard changes ecosystem promises. | Governance records owner, decision, affected participants, rollout and appeal or exception path. |
| CR-OCSIM-031 | Stage readiness must not claim OCS compatibility without model-version evidence. | A service can look compatible while relying on obsolete or private assumptions. | Conformance report links OCS model version, field registry, validation catalog and compatibility review. |
| CR-OCSIM-032 | OCS information model artifacts must remain source-safe. | The standard is intended for ecosystem sharing. | Private marker and strict secret scans pass for templates, examples, reports and generated requirements. |
| CR-OCSIM-033 | OCS must maintain a canonical core field catalog for the baseline service manifest. | A field matrix template is not enough if no one knows the mandatory field inventory. | Catalog lists core fields, product meaning, cardinality, requiredness, profile behavior, defaulting and omission consequence. |
| CR-OCSIM-034 | OCS extension lifecycle must cover registration, ownership transfer, compatibility review, deprecation and removal. | Extension governance is where independent implementations can silently fork. | Extension record has lifecycle state, owner, transfer rules, review trigger, deprecation path and removal/migration rule. |
| CR-OCSIM-035 | OCS must have a versioned conformance suite tied to model version. | Reimplementation needs a durable test oracle, not only documents. | Suite version names test groups for model, fields, profiles, unknown fields, extensions, errors, artifacts, source-safety and round-trip preservation. |
| CR-OCSIM-036 | OCS schema governance record must be required for every model or field-registry release. | Standard changes affect ecosystem trust, migration and support. | Release record names decision owner, approval path, changed artifacts, compatibility class, rollout, migration and appeal/exception handling. |

## Artifact Kind Registry

| Kind | Product Purpose | Minimum Owner | Required Evidence |
|---|---|---|---|
| `service_manifest` | Describes a service as product contract. | Service owner | Field registry, validation, docs, conformance. |
| `component` | Describes a service part with role and lifecycle. | Service owner | Readiness, observability, dependency edges. |
| `dependency_contract` | Describes required external capability and safe failure. | Service owner and provider/admin | Connection outputs, secret boundary, fallback. |
| `profile` | Describes local/private/provider/federation/global context. | Profile owner | Overrides, defaults, policy, generated values. |
| `lifecycle_action` | Describes allowed operation and result shape. | Capability owner | Risk, idempotency, approval, evidence. |
| `task_operation` | Describes repeatable build/maintenance/diagnostic work. | Service owner | Inputs, scope, risk, validation, result. |
| `usage_resource` | Describes billable or informational consumption. | Billing owner | Unit, scope, exclusions, correction behavior. |
| `ui_descriptor` | Describes embedded or standalone user surface. | Service owner and platform owner | Permissions, context, lifecycle, support owner. |
| `evidence_bundle` | Describes proof without unsafe raw data. | Evidence owner | Proven claim, limits, freshness, redaction. |
| `extension_namespace` | Describes compatible innovation outside core. | Extension owner | Scope, baseline constraints, compatibility. |
| `model_change_record` | Describes standard evolution. | Standard owner | Impact, migration, profile/conformance updates. |

## Canonical Core Field Catalog Baseline

This baseline is intentionally semantic. A future serialization can rename or
nest fields only if round-trip evidence preserves the same meaning.

| Core Field Family | Product Meaning | Baseline Rule |
|---|---|---|
| Identity | Stable kind, id, name, owner, publisher, support owner and maturity. | Required for every service manifest. |
| Purpose | User outcome, product promises, non-goals and supported roles. | Required before readiness claim. |
| Profiles | Local/private/provider/federation/global/edge support, overrides and policy. | Required at least for the current stage profile. |
| Components | Service parts with role, owner, lifecycle and readiness. | Required when service has runnable or managed parts. |
| Dependencies | Capability contracts, connection outputs, secret boundary, fallback and owner. | Required when service depends on another capability. |
| Lifecycle Actions | Validate, publish, order, provision, update, suspend, resume, remove, export and migrate semantics where applicable. | Required actions depend on stage and profile. |
| Usage Resources | Billable or informational units, scope, exclusions and correction behavior. | Required before commercial publication. |
| Health And Observability | Health/readiness, logs, metrics, traces and events with redaction. | Required for runnable services. |
| Policy And Trust | Placement, data class, jurisdiction, audit, certification and trust state. | Required before placement/order/publication. |
| Portability | Exportable data/metadata/state, compatible targets, restore/import and limitations. | Required before anti-lock-in or marketplace claim. |
| UI Descriptor | Embed mode, scoped context, permissions, allowed actions and support owner. | Required when service exposes UI. |
| Documentation | Overview, API, architecture, runbook, FAQ and known limits. | Required before readiness claim. |
| Evidence | Conformance report, validation summary, freshness, owner and review trigger. | Required for readiness claim. |
| Source Safety | Sensitivity, redaction, copy-risk and forbidden-content decision. | Required for artifacts consumed by agents or ecosystem participants. |

## Compatibility Classes

| Class | Meaning | Default Gate |
|---|---|---|
| `additive` | Adds optional field/kind without changing existing meaning. | Warning review. |
| `profile-scoped` | Changes behavior only in named profiles with visible consequence. | Profile owner approval. |
| `default-changing` | Changes effective behavior when user does nothing. | Owner approval, migration note and user-visible consequence. |
| `deprecated` | Keeps behavior but starts removal clock. | Deprecation path and replacement. |
| `breaking` | Existing compatible artifacts may fail or change meaning. | ADR/profile change, migration window and conformance update. |
| `forbidden` | Weakens mandatory safety, identity, trust, billing or evidence rules. | Blocked unless a new standard version explicitly redefines the baseline. |

## Versioned OCS Conformance Suite

Each OCS model version must define a reusable conformance suite with at least
these groups:

| Test Group | Must Prove |
|---|---|
| Model Header | Version, kind, identity, owner and maturity are present and valid. |
| Core Field Catalog | Required and conditional baseline fields are present or explicitly not-applicable. |
| Profile Precedence | Base, profile, owner override, generated value and secret binding resolve predictably. |
| Unknown Fields | Unknown data follows reject/quarantine/extension-only policy. |
| Extension Lifecycle | Extension is registered, owned, compatible and cannot weaken baseline. |
| Validation Codes | UI/API/CLI/Agent API expose stable code, path, severity and remediation. |
| Effective Model Report | Defaults, generated values and redacted secret references are visible. |
| Generated Artifacts | Runtime outputs reference model, field registry and source identity. |
| Round Trip | Supported serializations preserve semantic identity and validation results. |
| Source Safety | Artifacts contain no private context, raw secrets or copied source text. |

## Required Artifacts

- [templates/ocs-information-model-template.md](templates/ocs-information-model-template.md)
- [examples/ocs-information-model-example.md](examples/ocs-information-model-example.md)
- [templates/ocs-service-manifest-template.md](templates/ocs-service-manifest-template.md)
- [templates/ocs-supporting-contract-templates.md](templates/ocs-supporting-contract-templates.md)
- [adr/0002-open-cloud-standard-schema-format.md](adr/0002-open-cloud-standard-schema-format.md)

## Stop Conditions

Agent must stop when:

- a new artifact kind has no owner, purpose or validation scope;
- a field has no requiredness, compatibility rule or validation code;
- unknown fields are silently ignored;
- an extension weakens mandatory baseline rules;
- a default changes user-visible behavior without change record;
- serialization cannot round-trip through the information model;
- schema/model artifact contains private source context, raw secret material,
  endpoint, network address or copied source text.

## Non-Goals

This document does not define final syntax, parser implementation, runtime API,
storage schema, protocol, UI framework or code generator. It defines the
product meaning that those implementations must preserve.
