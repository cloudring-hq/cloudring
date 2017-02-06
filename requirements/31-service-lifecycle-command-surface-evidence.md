# Service Lifecycle Command Surface Evidence

Этот документ фиксирует продуктовые требования из source-slice pass по legacy
platform lifecycle/deployment surfaces. Старый prototype показал ценность
простого manifest-first developer loop, но также показал риски: команды могут
быть unstable/unimplemented, task execution может стать скрытой автоматизацией,
environment export может быть secret-adjacent, plugins могут стать trust
bypass, а generated files могут незаметно стать source of truth.

CloudRING must treat every command/API/agent action as a product contract with
intent, state, risk, evidence, rollback/cleanup and support semantics.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-LIFECMD-001 | Service lifecycle command surface must be derived from OCS/service contract, not hand-maintained behavior. | Если команды живут отдельно от manifest, self-service расходится с продуктовой правдой. | Command catalog links each action to OCS artifact, lifecycle action and conformance check. |
| CR-LIFECMD-002 | Each lifecycle command must declare intent, actor, scope, risk class, inputs, outputs and state transition. | AI agents cannot safely run opaque commands. | Command contract includes human summary and agent-readable action record. |
| CR-LIFECMD-003 | Create/scaffold flow must produce a minimal complete service product, not only source files. | Stage 1 should start from a usable service loop. | Generated starter includes manifest, docs, runbook, validation target, source-safety boundary and conformance gap list. |
| CR-LIFECMD-004 | Create/scaffold flow must fail before writing when identity or destination is invalid. | Half-created services become support debt. | Validation checks name/identity, target existence, permissions and rollback/cleanup plan before writing. |
| CR-LIFECMD-005 | Service name/identity validation must use stable validation codes and remediation. | String-only errors are weak for agents and UI/API parity. | Invalid identity returns code, field path, reason, remediation and owner. |
| CR-LIFECMD-006 | Environment/profile resolution must produce an effective configuration report. | Users and agents need to see merged defaults/overrides without reading code. | Report lists base values, profile overrides, generated values, redacted secret refs and source of each value. |
| CR-LIFECMD-007 | Environment export must be classified as secret-adjacent by default. | Exporting runtime environment can leak credentials or private topology. | Export action requires redaction policy, publish boundary and warning/support-safe output. |
| CR-LIFECMD-008 | Debug dependency flow must be separated from full service start. | Developers often need dependencies running while service runs in debugger. | Command catalog distinguishes dependency-only debug, full start and unsupported/unimplemented states. |
| CR-LIFECMD-009 | Unimplemented or unstable lifecycle action must be first-class state, not hidden failure. | Prototype-grade commands should not look production-ready. | Readiness report marks action as unsupported, preview, unstable or blocked with replacement path. |
| CR-LIFECMD-010 | Pre-run checks must be mandatory before lifecycle actions that change runtime state. | Comments or intentions do not protect users. | Preflight verifies platform readiness, manifest validity, port/resource conflicts, policy and cleanup boundary. |
| CR-LIFECMD-011 | Generated deployment artifacts must be disposable and traceable. | Runtime files can become fake product truth. | Artifact evidence includes source manifest/model version, generator, target profile, freshness and cleanup/regeneration rule. |
| CR-LIFECMD-012 | Generator capabilities must have readiness states. | A pluggable generator that is unimplemented must not pass conformance. | Generator is ready, preview, unsupported or blocked with supported profiles and evidence. |
| CR-LIFECMD-013 | Platform and service components must be modeled separately. | Debug/runtime dependencies often mix platform-provided and service-owned parts. | Effective deployment report separates platform components, service components, owners and support responsibility. |
| CR-LIFECMD-014 | Component connection outputs must be typed and redacted where needed. | Derived environment names and connection strings can leak secret/topology information. | Connection outputs declare data class, secret boundary, redaction and owner. |
| CR-LIFECMD-015 | Stop/remove/cleanup actions must state data and orphan-resource consequences. | Stopping dependencies can delete useful local state or leave hidden resources. | Stop result lists removed resources, retained data, orphan detection and next allowed actions. |
| CR-LIFECMD-016 | Log viewing must state what runtime mode it covers. | Logs from dependency runtime and debugged service may have different sources. | Log action declares source, retention, redaction, profile and unsupported modes. |
| CR-LIFECMD-017 | Documentation preview must be part of lifecycle readiness. | Docs are support/product evidence, not a static afterthought. | Doc preview action checks docs presence, port conflict, runtime profile, support owner and graceful shutdown behavior. |
| CR-LIFECMD-018 | Documentation tooling must be replaceable. | A docs flow tied to one renderer becomes accidental lock-in. | Docs contract declares content source and renderer profile separately. |
| CR-LIFECMD-019 | Task operations must be modeled as bounded product operations. | Arbitrary task execution can bypass approvals and leak data. | Task contract includes purpose, inputs, image/tool identity, mounts, network, data access, timeout, risk and result shape. |
| CR-LIFECMD-020 | Task command arguments must be structured and secret-safe. | Free-form command substitution is hard to validate and redact. | Task arguments declare schema, redaction, allowed interpolation and blocked raw-secret patterns. |
| CR-LIFECMD-021 | Task list and task execution must share the same source of truth. | Users should not discover tasks that agents cannot validate. | Task list is generated from manifest/model and each task has validation/evidence status. |
| CR-LIFECMD-022 | Plugin actions must be higher-trust extensions, not default automation. | Plugins can execute broad behavior and inherit environment. | Plugin contract declares capability, permission, environment scope, isolation, audit, support owner and revocation path. |
| CR-LIFECMD-023 | Plugin lifecycle must include install, discover, run, update, disable, revoke and support impact. | Extension governance is incomplete without operational lifecycle. | Plugin evidence includes version, owner, trust state, compatibility and deprecation/removal path. |
| CR-LIFECMD-024 | Command output must have a standard result object. | Humans, UI, CLI, API and agents need the same interpretation. | Result includes status, state transition, operation id, warnings, evidence refs, error code, owner and next actions. |
| CR-LIFECMD-025 | Command errors must distinguish unsupported, invalid input, missing precondition, runtime failure, policy denial and unsafe evidence. | Different failures need different remediation. | Error class maps to owner, retryability, support handoff and stop condition. |
| CR-LIFECMD-026 | Lifecycle command docs must be generated or checked against command contracts. | Docs drift creates false self-service. | Conformance compares documented commands with implemented/supported command registry and flags drift. |
| CR-LIFECMD-027 | E2E command evidence must cover more than binary availability. | "Tool exists" does not prove product readiness. | E2E evidence covers create, validate, debug/start, env, task, docs, stop/cleanup and negative cases. |
| CR-LIFECMD-028 | Local runtime command profile must not force future private/provider architecture. | Stage 1 should prepare future stages without freezing runtime choice. | Runtime profile is replaceable and maps to same lifecycle/action/evidence model. |
| CR-LIFECMD-029 | Command surface must support agent dry-run before state change. | One human plus agents need previewable automation. | Controlled/risky/destructive actions expose plan, consequences, approval and rollback/cleanup before execution. |
| CR-LIFECMD-030 | Lifecycle evidence must be support-ready. | Self-service fails if support must reconstruct what happened. | Each action can emit evidence bundle with manifest version, profile, action, logs/metrics refs, redactions and next owner. |
| CR-LIFECMD-031 | Source-derived command lessons must not transfer prototype-specific tool names or private paths into product requirements. | Requirements should preserve why, not old implementation branding. | Requirements use neutral lifecycle/action terms and pass private marker scan. |
| CR-LIFECMD-032 | Current-tree source pass without git metadata must not claim history coverage. | Completion audit must remain honest. | Source pass records current-tree contract-surface coverage and explicit no-history non-claim. |

## Lifecycle Surface Families

| Surface | Product Meaning | Required Evidence |
|---|---|---|
| Create/Scaffold | Start a service with minimum complete product loop. | Identity validation, generated files inventory, docs/runbook, conformance gaps, rollback. |
| Validate/Preflight | Prove action is safe before runtime change. | Manifest/model check, platform readiness, policy, ports/resources, source-safety. |
| Debug Dependencies | Run dependencies while service code runs elsewhere. | Dependency list, connection outputs, redaction, cleanup, unsupported modes. |
| Full Start | Run complete service profile. | Generator readiness, artifact provenance, health/readiness, rollback/stop. |
| Stop/Cleanup | Stop runtime and handle leftovers/data. | Removed/retained resources, orphan detection, data consequence. |
| Logs/Status | Explain runtime state. | Source, mode, retention, redaction, support owner. |
| Environment Export | Provide effective config for local/debug use. | Redacted effective config report, secret boundary, publishability. |
| Documentation Preview | Make docs part of lifecycle. | Renderer profile, port conflict, docs presence, support-safe shutdown. |
| Task Operation | Run bounded maintenance/build/diagnostic action. | Inputs, mounts, network, risk, timeout, validation, structured result. |
| Plugin Action | Run higher-trust extension. | Permission, isolation, audit, trust, support impact, revocation. |

## Stop Conditions

Agent must stop if:

- lifecycle action has no command contract or OCS lifecycle reference;
- state-changing action lacks dry-run/preflight/approval boundary;
- environment/task/plugin output could include raw secret or private context;
- generated artifact has no source manifest/model/provenance;
- command is unsupported/unstable but readiness claim treats it as ready;
- plugin lacks owner, permissions, isolation or revocation path;
- E2E evidence only proves executable presence, not product journey;
- source-derived claim would require copying old command text, paths or code.

## Non-Goals

This document does not prescribe final CLI names, implementation language,
container runtime, docs renderer, shell syntax, task image format or plugin
binary protocol. It preserves the product contract and safety semantics.
