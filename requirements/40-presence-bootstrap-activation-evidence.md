# Presence Bootstrap Activation Evidence

Этот документ углубляет `CR-SERVICEFACTORY-*`, `CR-LIFECMD-*`,
`CR-INFPROFILE-*` and Stage 1/2 readiness: bootstrap должен быть не скачиванием
конфигурации и не ручной инструкцией, а доказуемым activation workflow для
local/private CloudRING presence.

Главный продуктовый урок source-slice: ранний platform prototype сделал
полезный путь к local runtime через CLI, config, asset registry and local
provider, но будущий CloudRING должен превратить это в self-service product:
trusted assets, preflight, profile matrix, atomic config, rollback/cleanup,
diagnostics, offline/private behavior and agent-readable evidence.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-PRESBOOT-001 | Presence bootstrap must be a named activation workflow with evidence. | Install/activation is the first trust moment of a cloud platform. | Activation has id, actor, target profile, artifact versions, status, evidence bundle, blockers and next allowed actions. |
| CR-PRESBOOT-002 | Bootstrap must distinguish CLI installation, configuration activation and runtime/presence activation. | A binary existing on disk does not prove a usable CloudRING presence. | Evidence separately covers tool availability, install source/provenance, OS/profile compatibility, config source, runtime provider readiness, local control plane and workload readiness where applicable. |
| CR-PRESBOOT-003 | Bootstrap artifacts must have identity, provenance and compatibility. | A config or asset without identity can silently change platform behavior. | Artifact record includes version, source class, integrity/provenance, compatibility range, owner, freshness and deprecation/rollback note. |
| CR-PRESBOOT-004 | Bootstrap distribution channel must be trusted and replaceable. | Central asset hosting can become lock-in or supply-chain risk. | Distribution profile supports connected, cached/offline, private mirror and manual import modes with trust evidence and freshness state. |
| CR-PRESBOOT-005 | Bootstrap configuration must have schema, profile and purpose. | Free-form config becomes tribal knowledge and unsafe agent input. | Config contract declares profiles, runtime provider, resource sizing, dependency settings, toolchain env, unsupported values, defaults, validation and redaction classes. |
| CR-PRESBOOT-006 | Configuration write must be atomic, recoverable and non-destructive. | A failed bootstrap should not leave half-configured local/private control. | Activation backs up previous config, writes atomically, validates after write, records previous/current identity and provides rollback/restore path. |
| CR-PRESBOOT-007 | Preflight must run before bootstrap changes local or private state. | Missing runtime, resources or permissions should fail before partial setup. | Preflight checks OS/profile support, CPU/memory/disk, network, ports/routes, runtime tools, permissions, policy and existing state conflicts. |
| CR-PRESBOOT-008 | Runtime provider matrix must be explicit and stage-aware. | Local development, single-host private and provider presence have different promises. | Matrix marks supported, manual-external, unstartable, unsupported, degraded, blocked and future-stage states with consequences. |
| CR-PRESBOOT-009 | A preferred local provider must not become architecture lock-in. | The source showed a pragmatic provider choice; CloudRING needs replaceable profiles. | Requirements express capability needs such as multi-service routing, ingress, isolation and resource limits, not a mandatory runtime technology. |
| CR-PRESBOOT-010 | Bootstrap resource profile must be visible before activation. | Users and agents need to know whether the machine can support the requested presence. | Activation plan shows requested CPU, memory, disk, runtime version class, expected footprint, limits, conflicts and safe downgrade/blocked options. |
| CR-PRESBOOT-011 | Asset registry or bootstrap catalog must expose safe asset index, not raw internal storage. | Bootstrap is supply chain; directory listings and ad hoc files are weak product surfaces. | Catalog exposes asset id, type, version, digest/signature, compatibility, purpose, owner, freshness, retention and download policy. |
| CR-PRESBOOT-012 | Offline/private bootstrap must be a first-class mode. | Private adoption cannot depend on permanent central connectivity. | Evidence shows cached bundle identity, allowed offline duration, freshness, trust anchor, manual import path and sync/upgrade recovery. |
| CR-PRESBOOT-013 | Manual bootstrap path must produce the same evidence as automatic bootstrap. | Manual setup is useful for recovery, but must not bypass validation. | Manual flow validates schema, preflight, redaction, artifact identity, rollback and activation report before readiness claim. |
| CR-PRESBOOT-014 | Toolchain/environment bootstrap values must be classified as secret-adjacent by default. | Proxy, private module and local runtime values can reveal topology or credentials. | Effective env/config report marks public, internal, secret-reference, local-only and forbidden raw values with redacted preview. |
| CR-PRESBOOT-015 | Bootstrap must produce a shared status taxonomy across UI/API/CLI/Agent API. | Humans and agents need the same interpretation of install state. | Statuses include not-started, preflighting, blocked, downloading, configured, starting-runtime, active, degraded, manual-external, rolling-back, failed and cleaned-up. |
| CR-PRESBOOT-016 | Start/stop runtime actions must be idempotent, timeout-aware and profile-aware. | Runtime lifecycle failures are common and should not corrupt presence state. | Start/stop evidence shows target profile, current state, timeout policy, retryability, concurrency lock, unsupported/unstartable state, partial state and cleanup/rollback guidance. |
| CR-PRESBOOT-017 | Unsupported or unstartable provider states must be explicit product states. | Some providers do not need start/stop; others are unsupported. | Readiness report marks manual-external, unsupported or blocked with reason, user impact, next action and non-claim. |
| CR-PRESBOOT-018 | Bootstrap must include diagnostics and doctor-style evidence. | Self-service install fails without actionable diagnostics. | Diagnostic report covers config used, runtime provider, tool versions/classes, resource checks, network/ingress, asset freshness, component health, logs summary, redactions and suggested remediation. |
| CR-PRESBOOT-019 | Bootstrap generated artifacts must not become hidden source of truth. | Generated config/runtime files can drift from product contract. | Artifact inventory states source config/model, generator, target profile, deterministic generation inputs, created/overwritten/cache/user-state classes, local-state boundary, cleanup/regeneration rule and publish/ignore decision. |
| CR-PRESBOOT-020 | Activation report must be support-ready and agent-readable. | One human with AI agents needs a handoff after install. | Report includes actor, profile, artifact versions, checks, smoke/readiness result, changed files/classes, retained state, warnings, evidence refs, owner and next actions. |
| CR-PRESBOOT-021 | Rollback and cleanup must be part of bootstrap readiness. | Failed activation can leave local runtimes, configs, ports or assets behind. | Cleanup plan lists changed config, downloaded assets, runtime resources, volumes/state, logs/evidence, retained backups and irreversible warnings. |
| CR-PRESBOOT-022 | Multi-service routing/ingress readiness must be checked where claimed. | The provider choice was driven by simultaneous service access; readiness must prove the capability. | Evidence checks routes, ingress, name resolution, port conflicts, certificate/trust boundary and unsupported states before multi-service claims. |
| CR-PRESBOOT-023 | Bootstrap update must be plan/apply/validate, not overwrite-in-place. | Updating bootstrap config can break every service and local/private presence. | Update plan shows old/new artifact, compatibility impact, affected services, migration, checkpoints, resume/repair option, validation, rollback and deprecation state. |
| CR-PRESBOOT-024 | Bootstrap must preserve local autonomy. | Private/local CloudRING must not become a SaaS dependency at activation time. | Local allowed operations continue with cached config/assets when external channel is unavailable, with freshness/degraded markers. |
| CR-PRESBOOT-025 | Bootstrap must protect secrets and private topology in logs, reports and agent context. | Activation touches local paths, proxies, runtime env and infrastructure details. | Evidence redacts secret values, internal endpoints, local paths, raw env and topology while preserving support-safe state and hashes/ids. |
| CR-PRESBOOT-026 | Bootstrap security must include artifact trust and downgrade protection. | An attacker or stale mirror could install an unsafe platform profile. | Activation verifies allowed source, integrity, version policy, downgrade/rollback approval, revoked artifact status and trust anchor freshness. |
| CR-PRESBOOT-027 | Presence activation must link to infrastructure capability profile. | Bootstrap success must translate into declared product capability. | Activation report updates local/private profile state, supported/degraded/unsupported capabilities, capacity, health and conformance refs. |
| CR-PRESBOOT-028 | Bootstrap docs must be checked against actual activation contract. | Docs drift creates failed installs and false readiness. | Documentation check compares install/bootstrap/manual/start/stop guidance with activation schema, supported profiles, warnings and non-goals. |
| CR-PRESBOOT-029 | Bootstrap fixtures must include happy, manual, offline and failure paths. | Readiness must prove safe refusal, not only one successful command. | Tests/scenarios cover trusted download, invalid artifact, existing config, insufficient resources, unsupported provider, offline cache, rollback and source-safety failure. |
| CR-PRESBOOT-030 | Agent-run bootstrap must require dry-run and approval for state-changing activation. | Agents should help install but not silently mutate local/private control plane. | Agent flow exposes plan, risk, changes, approval, validation, rollback and forbidden raw-secret/topology access. |
| CR-PRESBOOT-031 | Source-derived bootstrap lessons must remain reimplementation-oriented. | Requirements must survive source disappearance without copying old docs or commands. | Pass output uses product abstractions and avoids raw source paths, exact commands, private endpoints, credentials, local examples or copied text. |
| CR-PRESBOOT-032 | Bootstrap failures must feed the continuous learning loop. | Repeated install toil is a product signal. | Repeated preflight/activation/config/docs failures create requirement, ADR, runbook, fixture, conformance check or owner-approved no-change rationale. |

## Evidence Model

Minimum presence bootstrap activation evidence:

```yaml
presence_bootstrap_activation_evidence:
  evidence_id: presence-bootstrap-evidence-id
  profile_refs:
    - stage1-service-ready
    - stage2-private-presence-ready
  scenario_refs:
    - SCENARIO-STAGE2-008
  activation:
    workflow_status: passed | warning | failed | blocked
    install_provenance_status: passed | warning | failed | blocked
    scope_status: passed | warning | failed | blocked
    status_taxonomy_status: passed | warning | failed | blocked
  artifact_and_distribution:
    artifact_identity_status: passed | warning | failed | blocked
    provenance_integrity_status: passed | warning | failed | blocked
    distribution_channel_status: passed | warning | failed | blocked
    offline_cache_status: passed | warning | failed | blocked | not-applicable
  config_and_preflight:
    schema_profile_status: passed | warning | failed | blocked
    atomic_write_status: passed | warning | failed | blocked
    resource_preflight_status: passed | warning | failed | blocked
    env_redaction_status: passed | warning | failed | blocked
  runtime_presence:
    provider_matrix_status: passed | warning | failed | blocked
    runtime_lifecycle_status: passed | warning | failed | blocked | not-applicable
    ingress_routing_status: passed | warning | failed | blocked | not-applicable
    infrastructure_profile_status: passed | warning | failed | blocked
  operations:
    diagnostics_status: passed | warning | failed | blocked
    smoke_readiness_status: passed | warning | failed | blocked | not-applicable
    generated_artifact_inventory_status: passed | warning | failed | blocked
    resumability_lock_status: passed | warning | failed | blocked
    rollback_cleanup_status: passed | warning | failed | blocked
    update_plan_status: passed | warning | failed | blocked | not-applicable
    docs_contract_status: passed | warning | failed | blocked
    agent_dry_run_approval_status: passed | warning | failed | blocked
  source_safety:
    redaction_status: passed | warning | failed | blocked
    private_marker_status: passed | warning | failed | blocked
    copy_risk_status: passed | warning | failed | blocked
  unresolved_gaps:
    - gap
```

## Stop Conditions

Agent must stop and request owner/review if:

- bootstrap artifact identity, provenance, freshness or compatibility is
  unknown;
- CLI/install source, compatibility or integrity is unknown but activation is
  treated as trusted;
- activation would overwrite config without backup, validation or rollback;
- activation cannot explain partial state, resume/repair path or parallel-run
  lock;
- runtime provider is unsupported, degraded or manual-external but readiness
  treats it as fully active;
- effective config/env contains raw secret, private endpoint, local path or
  topology detail in agent/report context;
- Stage 1 local bootstrap is used as proof of Stage 2 private presence readiness;
- agent is asked to mutate local/private runtime state without dry-run and
  approval evidence;
- source-derived requirement would copy old docs, commands, paths, endpoints or
  config snippets.

## Non-Goals

- Не выбирать final installer, package manager, orchestrator, hypervisor,
  runtime provider, registry implementation or signing technology.
- Не утверждать, что analyzed prototype proves Stage 2 private cloud install.
- Не переносить old bootstrap commands or config format as future standard.
- Не считать binary installation equivalent to activated CloudRING presence.
