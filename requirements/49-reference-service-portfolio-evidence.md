# Reference Service Portfolio Evidence

Этот документ фиксирует продуктовые требования к портфелю эталонных сервисов
CloudRING. Такой портфель нужен, чтобы команда человека и AI-агентов могла
проверять платформу не по одному счастливому примеру, а по набору объяснимых
архетипов: минимальный сервис, документированный сервис, наблюдаемый сервис,
task/data service, сервис с объектным хранилищем, сервис с managed secret store
и базовый template.

`CR-REFSVC-*` не выбирает язык, framework, runtime, базу данных, secret manager,
object storage или конкретный deployment tool. Эти требования сохраняют подход:
каждый эталонный сервис должен ясно объяснять, что он доказывает, почему этого
достаточно для заявленного stage, что не доказано и какие соседние evidence
пакеты нужны до production/provider/public claims.

`CR-REFSVC-*` дополняет `CR-WORKFLOW-*`, `CR-SVCDEPLOY-*`, `CR-SVCINT-*`,
`CR-DOCMEM-*`, `CR-SUPDIAG-*`, `CR-PORTALUX-*`, `CR-UICERT-*`,
`CR-RELPROM-*` and `CR-CATREG-*`. Эти семейства остаются источниками truth для
workflow, deployment model, integration contract, docs memory, support,
portal/UI, release and catalog publication. `CR-REFSVC-*` связывает их как
portfolio/reference evidence gate.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-REFSVC-001 | Reference service portfolio readiness must be an evidence gate, not a sample count. | Один работающий пример может скрывать недоказанные зависимости, docs gaps, support gaps and overclaims. | Evidence states portfolio scope, archetypes, stage claims, owners, blockers, source-safety and explicit non-claims before reference portfolio readiness is claimed. |
| CR-REFSVC-002 | Portfolio must maintain an explicit archetype registry. | Агентам нужно понимать, какой класс опыта покрывает каждый пример. | Registry includes minimal runtime, docs-only/documented service, observable service, task/data service, object-storage integration, secret-store integration and template baseline, or marks each missing archetype as a gap. |
| CR-REFSVC-003 | Each reference service must declare purpose, audience, stage scope and non-goals. | Без границ демо легко принять за production proof. | Service entry names intended reviewer roles, product lesson, supported stage, readiness claim and what the service intentionally does not prove. |
| CR-REFSVC-004 | Each reference service must map to capability and conformance claims. | Reference examples are useful only when tied to product readiness. | Entry links relevant capability families, conformance profile checks, source pass, template/example refs and scenario refs. |
| CR-REFSVC-005 | Portfolio must separate docs-only, executable, integration, task and production claims. | Documentation scaffold, local start, task execution and shipped service are different evidence levels. | Evidence labels each claim class and blocks escalation from one class to another without the required supporting evidence. |
| CR-REFSVC-006 | Service contract or manifest must remain the portfolio source of truth. | Direct/debug run files and generated artifacts can drift from the product contract. | Entry shows canonical contract reference, derived artifact boundary, direct/debug mode limitations and conflict handling. |
| CR-REFSVC-007 | Each executable reference service must have a first useful behavior and observable outcome. | A service that only starts does not prove user or agent value. | Evidence describes the behavior, input class, expected result, success state, failure state and support handoff. |
| CR-REFSVC-008 | Platform-supported run path and direct/debug run path must be separated. | Developer conveniences can bypass platform ownership, secret handling and dependency contracts. | Evidence marks supported path, debug-only path, unsupported path, claim boundary, cleanup expectation and promotion blocker. |
| CR-REFSVC-009 | Environment and profile values must be classified. | Demo values can accidentally become production habits or sensitive evidence. | Entry classifies values as synthetic, local-only, generated, secret-adjacent, managed secret reference, production candidate or forbidden-in-evidence. |
| CR-REFSVC-010 | Demo credentials, local endpoints and seed data must never prove production readiness. | Local fixtures are useful for learning but unsafe as trust claims. | Readiness report states demo/local values as non-claims and links separate secret/runtime/release evidence for stronger claims. |
| CR-REFSVC-011 | External dependency examples must define capability, owner, lifecycle and failure expectations. | A dependency component in a manifest is not yet supportable product behavior. | Dependency evidence covers purpose, owner, lifecycle state, readiness/failure behavior, portability assumption and support boundary. |
| CR-REFSVC-012 | Data-backed reference services must prove data ownership and change discipline. | Data services fail when schema ownership, migrations and compatibility are informal. | Evidence shows schema/resource ownership, migration/change tracking, validation responsibility, rollback/forward expectation and explicit data non-claims. |
| CR-REFSVC-013 | Task-oriented services must separate operational tasks from domain tasks. | Mixing infra maintenance and business work hides risk and approval needs. | Task evidence classifies each task intent, owner, risk, allowed surfaces, result object and required approval. |
| CR-REFSVC-014 | Task evidence must cover completion, retry, failure and duplicate/re-run semantics. | A listed task does not prove reliable automation. | Entry includes success result, blocked/error result, retryability, idempotency or duplicate handling and cleanup/handoff. |
| CR-REFSVC-015 | Object/data artifact integration examples must prove a bounded lifecycle. | A configured storage dependency does not prove safe artifact handling. | Evidence covers create/read/list/delete or equivalent lifecycle, synthetic artifact identity, retention/non-retention and failure behavior. |
| CR-REFSVC-016 | Secret-store integration examples must prove brokered dependency, not secret value handling. | Reference services must teach secret safety from the first day. | Evidence shows managed secret reference, scope, owner, access boundary, rotation/degraded expectation and absence of raw values in reports. |
| CR-REFSVC-017 | Observable reference services must prove log, metric, trace and error semantics. | Observability is supportability, not only middleware wiring. | Evidence links structured logs, metrics, trace/correlation, top-level error policy, support diagnostic summary and non-claims. |
| CR-REFSVC-018 | Metrics evidence must include success/failure semantics and cost/cardinality rationale. | Unbounded metrics can become expensive or misleading. | Metric evidence states event meaning, success/failure split, labels/dimensions policy, aggregation/freshness and known gaps. |
| CR-REFSVC-019 | Trace and log evidence must preserve context hierarchy without duplicate noise. | Agents need one coherent failure story, not scattered logs. | Evidence shows correlation scope, parent/child context, where errors are logged, where they are not duplicated and how support receives the summary. |
| CR-REFSVC-020 | Documentation evidence must be filled, owned and freshness-aware. | Generated docs navigation is not operational readiness. | Docs evidence covers overview, interface/API contract, architecture, runbook, FAQ/support boundary, owner and freshness or marks each placeholder as blocker. |
| CR-REFSVC-021 | Boilerplate/template readiness must prove placeholder replacement. | A scaffold can look complete while preserving empty sections and private placeholders. | Template evidence blocks readiness when purpose, architecture, runbook, FAQ, API, support owner or known limits are still placeholders. |
| CR-REFSVC-022 | Reference tests/fixtures must prove core behavior, not only build/start success. | Build success and local start can miss the product promise. | Evidence links positive fixtures, expected outputs, contract checks and limitations for each archetype. |
| CR-REFSVC-023 | Negative and failure fixtures must be present for each relevant archetype. | Cloud platforms earn trust by safe refusal and recovery. | Fixtures cover missing dependency, misconfiguration, invalid input, blocked task, unavailable secret/artifact or stale docs where relevant. |
| CR-REFSVC-024 | Portfolio must cover both simple and composed behavior. | A minimal endpoint cannot prove multi-capability service composition. | Coverage matrix distinguishes minimal proof, composed proof and missing composed behavior for each capability. |
| CR-REFSVC-025 | Portfolio coverage matrix must map archetypes to capabilities and gaps. | Without matrix, evidence remains anecdotal and agents cannot plan next slices. | Matrix lists archetype, services, capability refs, stage refs, required evidence, known gaps, owner and next action. |
| CR-REFSVC-026 | Each reference service must have support handoff and diagnostic summary expectations. | A reference service should teach supportability, not only development. | Entry states support owner class, diagnostic summary, failure story, logs/metrics/traces refs and when `CR-SUPDIAG-*` is required. |
| CR-REFSVC-027 | Portfolio evidence must be source-safe by design. | Reference examples are often copied into agent prompts and docs. | Evidence excludes private names, paths, endpoints, hostnames, exact commands, credentials, raw config/code and copied source shape. |
| CR-REFSVC-028 | Each reference service must state portability and replaceability lessons. | Anti-lock-in depends on knowing which dependency can be replaced and under what contract. | Entry records replaceable dependency profile, portability constraints, exit/migration lesson and stage-specific limitations. |
| CR-REFSVC-029 | Release and publication claims must require artifact identity and promotion evidence. | A reference service in a repo is not automatically a shipped or catalog-ready product. | Portfolio marks release/publication as blocked, preview or proven and links `CR-RELPROM-*` and `CR-CATREG-*` when claimed. |
| CR-REFSVC-030 | AI agents must evaluate portfolio entries through bounded plans. | Raw commands, raw env and direct source inspection can leak unsafe context or overclaim readiness. | Agent handoff lists allowed inspections, forbidden raw evidence, required approvals, validation summary and final evidence requirements. |
| CR-REFSVC-031 | Portfolio evolution must be governed through evidence change records. | Reference services become stale unless additions/removals explain why. | Adding, removing or reclassifying an archetype records reason, affected claims, compatibility impact, owner, freshness and no-ADR/ADR decision. |
| CR-REFSVC-032 | Reference service portfolio evidence must state explicit non-claims. | The main risk of examples is false confidence. | Evidence says what is not proven: production deployment, security absence, performance, support SLA, catalog publication, portal UX, release readiness, full source coverage or complete history unless separately linked. |

## Evidence Bundle

Minimum evidence bundle for reference service portfolio readiness:

1. Portfolio identity, owner, stage scope, freshness, source-safety class and
   readiness claim.
2. Archetype registry and coverage matrix for minimal, documented, observable,
   task/data, object artifact, secret-store and template baseline services.
3. Service entries with purpose, audience, stage claim, non-goals, canonical
   contract, run-mode boundaries, dependency ownership and first useful
   behavior.
4. Observability, docs, task, data, artifact and secret evidence where the
   archetype claims those capabilities.
5. Positive and negative fixtures, support handoff, diagnostic summary and
   agent-readable validation result.
6. Links to workflow, deployment, integration, docs, support, release, catalog,
   portal/UI and conformance evidence where stronger claims are made.
7. Explicit blockers, gaps, future-stage items and non-claims.

## Stop Conditions

Stop and require owner/review when:

- portfolio readiness is claimed from one sample, one local start or one docs
  scaffold;
- a reference service has no declared archetype, purpose, audience, stage scope
  or non-goals;
- docs-only, local/debug, integration, task, release, catalog or production
  claims are mixed without evidence boundaries;
- manifest/contract, generated artifact and direct/debug path disagree without
  conflict handling;
- demo credentials, local endpoints, seed data or raw environment values are
  used as readiness proof;
- dependency examples lack owner, lifecycle, failure behavior or portability
  assumption;
- observable services lack coherent log/metric/trace/error semantics;
- task services lack completion/failure/retry/duplicate semantics;
- documentation pages remain placeholders while docs readiness is claimed;
- support handoff, diagnostic summary, negative fixtures or source-safety scan
  is missing;
- evidence contains private names, source paths, endpoints, hostnames, network
  literals, exact commands/configs, credentials, source snippets or copied
  source shape.
