# Controlled Extension And Task Automation Evidence

Этот документ углубляет `CR-SERVICEFACTORY-*`, `CR-SECSUPPLY-*` and
`CR-AGOPS-*`: tasks, plugins, dependency/library operations and boilerplate
generation должны быть не скрытыми локальными скриптами, а governed automation
surface CloudRING.

Главный продуктовый урок source-slice: service tasks дают переносимость и
единый developer loop, plugins дают escape hatch для частной/специфичной
автоматизации, а boilerplate/library operations меняют кодовую и dependency
поверхность. Будущий CloudRING должен сохранить силу этих механизмов, но
обязать их иметь purpose, owner, provenance, policy, risk, redaction,
rollback/compensation and agent-readable evidence.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-EXTAUTO-001 | Extension/task automation must be a named product surface with local-vs-managed boundary. | Иначе произвольные локальные команды обходят OCS, security and agent policy while looking like platform readiness. | Evidence identifies automation kind and execution class: local developer automation, managed runner, CI-like validation, private runner or provider runner. |
| CR-EXTAUTO-002 | Every automation unit must declare purpose, owner and support boundary. | Автоматизация без владельца становится неразбираемым operational debt. | Record includes purpose, owner, maintainer, support owner, expected users, stage scope and retirement path. |
| CR-EXTAUTO-003 | Task must be preferred over plugin when the operation fits portable task semantics. | Plugin is an escape hatch and should not become default power. | Selection record explains why action is core, task or plugin, with risk class and approval need. |
| CR-EXTAUTO-004 | Plugin use must have an exception rationale. | Plugins can execute arbitrary behavior and carry private/process-specific logic. | Plugin record states why core/task/library path is insufficient, what boundary it crosses and when the exception is reviewed. |
| CR-EXTAUTO-005 | Automation artifacts must have immutable identity and provenance. | Images, binaries and templates without identity cannot be trusted across providers. | Evidence records version, digest/signature or equivalent immutable identity, source class, owner, compatibility and freshness. |
| CR-EXTAUTO-006 | Automation dependency references must not float silently. | "Latest" and mutable references create unreproducible service behavior. | Protected profiles require pinned version or approved floating-reference exception with owner, expiry and rollback note. |
| CR-EXTAUTO-007 | Automation must declare capability scope before execution. | A plugin or task can touch code, data, network, secrets and host state. | Manifest/evidence declares workspace scope, file classes, network need, data classes, secret access, service context and external systems class. |
| CR-EXTAUTO-008 | Service environment handoff must be least-privilege, escaped and redacted. | Passing full env into automation can leak secrets, topology or shell-sensitive values. | Automation receives only declared env classes; report shows allowed/denied keys, escaping policy, redacted env summary, secret references and forbidden raw-value checks. |
| CR-EXTAUTO-009 | Raw secret values must not be required for normal automation. | Tasks and plugins should use brokered capabilities or safe references. | Secret-like inputs are references/capabilities; raw secret requirement is blocked or explicit exceptional approval with expiry. |
| CR-EXTAUTO-010 | Automation arguments and working context must be structured where possible. | Free-form command strings are hard to validate and easy to misuse. | Evidence declares inputs, argument schema, defaults, validation, working context, unsafe string/command exceptions and test fixtures. |
| CR-EXTAUTO-011 | Task execution must have bounded runtime, resources, filesystem and network policy. | Long or broad automation can stall workflows or escape intended scope. | Result records timeout class, resource budget, mount mode, network mode, execution identity, retryability, idempotency, partial state and safe next action. |
| CR-EXTAUTO-012 | Automation must produce a structured result object. | Agents need stable proof, not only stdout/stderr. | Result includes status, operation id, actor, target, started/finished time, risk, warnings, artifacts, validation and redacted log summary. |
| CR-EXTAUTO-013 | Automation logs and artifacts must be source-safe before handoff. | Tool output often contains paths, env values, private topology or source snippets. | Evidence marks raw output handling, redaction, retained artifacts, excluded sensitive material and copy-risk status. |
| CR-EXTAUTO-014 | Local, CI and private/provider automation semantics must be comparable and non-overclaimed. | A local task that means different things in managed surfaces breaks portability and safety. | Compatibility matrix states local/CI/private/provider support, managed-runner evidence, differences, unsupported states, local-only artifacts and conformance impact. |
| CR-EXTAUTO-015 | Task image/tool catalog must be governed. | A task library is supply chain, not a folder of helper images. | Catalog record includes task purpose, immutable artifact identity, provenance/integrity, SBOM/scan status or approved exception, supported profiles, compatibility, deprecation and offline/private availability. |
| CR-EXTAUTO-016 | Plugin catalog must support private extensions without leaking private logic. | CloudRING needs extensibility for local/private needs while preserving OSS/product core. | Catalog stores safe metadata, trust evidence, permission class and support boundary without exposing protected process details. |
| CR-EXTAUTO-017 | Plugin execution must be isolated, allowlisted or explicitly bounded. | Arbitrary executables can bypass platform permissions. | Execution evidence declares allowlist/trust state, isolation mode or approved boundary, permissions used, service context access and containment limitations. |
| CR-EXTAUTO-018 | Automation must integrate with approval matrix. | Agents should not silently run code-changing, data-moving or trust-changing actions. | Risk class maps to required approval, dry-run, policy check and forbidden autonomous execution conditions. |
| CR-EXTAUTO-019 | Destructive or data-changing automation must prove rollback or compensation. | Migration, seeding, cleanup and dependency changes can damage state. | Plan includes affected data/state, backup/restore or compensation, irreversible warning, approval and validation. |
| CR-EXTAUTO-020 | Dependency/library mutation must be plan/apply/validate. | Dependency updates can change security, licensing and runtime behavior. | Plan shows requested dependency, version policy, affected files/classes, lock/update impact, compatibility, validation, rollback and source-safety. |
| CR-EXTAUTO-021 | Dependency/library operations must publish trust and freshness evidence. | Private or stale dependencies can lock services to hidden infrastructure. | Evidence includes source class, allowed registry/mirror class, freshness, vulnerability/license review state or explicit deferred non-claim. |
| CR-EXTAUTO-022 | Boilerplate generation must have template identity and migration path. | Scaffolded service code becomes the long-lived starting point. | Generation evidence records template version/provenance, created files/classes, product promises, non-goals, update/migration and rollback/cleanup. |
| CR-EXTAUTO-023 | Boilerplate must create product readiness foundations, not just code skeleton. | The first commit should teach the service how to be operated. | Template evidence includes manifest, docs, runbook, tests, observability hooks, task placeholders, build ownership policy and conformance gaps. |
| CR-EXTAUTO-024 | Generated boilerplate must not claim service readiness by itself. | A scaffold is a candidate, not a working cloud service. | Readiness report distinguishes scaffold-created, locally validated, private-ready, provider-ready and blocked states. |
| CR-EXTAUTO-025 | Automation registry updates must be versioned and reversible. | Updating tasks/plugins/templates can break many services at once. | Update record shows old/new versions, affected services, compatibility impact, migration, rollback/deprecation and owner approval. |
| CR-EXTAUTO-026 | Automation must support offline/private distribution where stage requires it. | Private/edge users cannot depend on a central service for every task or plugin. | Evidence shows cached/mirrored artifact identity, freshness, trust anchor, allowed offline duration and sync recovery. |
| CR-EXTAUTO-027 | Automation capability must be represented in conformance reports. | A service cannot be certified if its build/migration/plugin paths are invisible. | Conformance links task/plugin/library/boilerplate evidence, unsupported states, exceptions and next-stage blockers. |
| CR-EXTAUTO-028 | Automation failures must be product signals. | Repeated task/plugin failures reveal missing platform capability. | Failure trend creates requirement, ADR, runbook, catalog update, test fixture or owner-approved no-change rationale. |
| CR-EXTAUTO-029 | Automation examples must be synthetic and safe. | Example commands and env output can leak source shape or unsafe practices. | Examples use generic IDs, redacted outputs, no real paths/endpoints/secrets and explicit non-claims. |
| CR-EXTAUTO-030 | Automation must preserve replaceability of tools and languages. | Plugins/tasks should not lock CloudRING to one language, runner or package manager. | Requirement states capability contracts and evidence, not mandatory implementation technology. |
| CR-EXTAUTO-031 | Agent-run automation must start in plan/dry-run for controlled or risky classes. | An agent with task/plugin execution is effectively an operator. | Agent flow records plan, policy, scope, approval, execution, validation, rollback/compensation and final evidence. |
| CR-EXTAUTO-032 | Source-derived extension lessons must remain reimplementation-oriented. | Requirements must survive without copying old docs, plugin code or commands. | Source pass output uses product abstractions and avoids raw plugin names, commands, local paths, private examples, env values and copied text. |

## Evidence Model

Minimum controlled automation evidence:

```yaml
controlled_extension_task_automation_evidence:
  evidence_id: controlled-automation-evidence-id
  profile_refs:
    - stage1-service-ready
  scenario_refs:
    - SCENARIO-STAGE1-008
  automation_unit:
    kind: core-action | safe-task | controlled-task | plugin | library-mutation | boilerplate-generation
    execution_class_status: passed | warning | failed | blocked
    purpose_status: passed | warning | failed | blocked
    owner_support_status: passed | warning | failed | blocked
    selection_rationale_status: passed | warning | failed | blocked
    stage_scope_status: passed | warning | failed | blocked
  trust_and_distribution:
    artifact_identity_status: passed | warning | failed | blocked
    provenance_integrity_status: passed | warning | failed | blocked
    version_pin_status: passed | warning | failed | blocked
    catalog_status: passed | warning | failed | blocked
    offline_private_status: passed | warning | failed | blocked | not-applicable
  execution_boundary:
    capability_scope_status: passed | warning | failed | blocked
    env_redaction_status: passed | warning | failed | blocked
    env_export_policy_status: passed | warning | failed | blocked
    secret_boundary_status: passed | warning | failed | blocked
    argument_schema_status: passed | warning | failed | blocked
    isolation_or_boundary_status: passed | warning | failed | blocked
    filesystem_network_policy_status: passed | warning | failed | blocked
    runtime_budget_status: passed | warning | failed | blocked
  mutation_and_rollback:
    dependency_mutation_status: passed | warning | failed | blocked | not-applicable
    boilerplate_generation_status: passed | warning | failed | blocked | not-applicable
    rollback_compensation_status: passed | warning | failed | blocked
    update_migration_status: passed | warning | failed | blocked | not-applicable
  results_and_conformance:
    structured_result_status: passed | warning | failed | blocked
    local_ci_private_parity_status: passed | warning | failed | blocked
    managed_runner_boundary_status: passed | warning | failed | blocked
    conformance_link_status: passed | warning | failed | blocked
    failure_learning_status: passed | warning | failed | blocked
  agent_safety:
    risk_class_status: passed | warning | failed | blocked
    dry_run_approval_status: passed | warning | failed | blocked
    final_evidence_status: passed | warning | failed | blocked
  source_safety:
    redaction_status: passed | warning | failed | blocked
    private_marker_status: passed | warning | failed | blocked
    copy_risk_status: passed | warning | failed | blocked
  unresolved_gaps:
    - gap
```

## Stop Conditions

Agent must stop and request owner/security/ADR review if:

- task or plugin can execute without owner, purpose, risk class or evidence;
- plugin is used where a safe task or core action would be sufficient;
- local developer automation is claimed as managed CI/private/provider runner
  evidence;
- artifact identity, provenance, integrity or version policy is unknown;
- automation receives raw secrets, full unclassified env or private topology;
- debug/environment-inspection automation is allowed in a profile that can
  contain real secrets;
- arguments, working context or mutation target are free-form and unvalidated;
- dependency/library update uses floating version in protected profile without
  approval;
- destructive or data-changing automation lacks rollback/compensation;
- scaffolded service is treated as ready without validation evidence;
- task/plugin output would expose raw paths, endpoints, env values, source text
  or private process details;
- agent is asked to run controlled/risky automation without dry-run and approval.

## Non-Goals

- Не выбирать plugin runtime, container runtime, package manager, signing
  technology, scanner or template engine.
- Не запрещать private extensions; сделать их явными, bounded and auditable.
- Не считать task/plugin examples production-ready automation.
- Не переносить old command syntax, plugin filenames, local directories or env
  values as future standard.
