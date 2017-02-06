# Product Capability Map

Этот документ связывает стратегию, архитектуру, stages and conformance profiles
в одну карту capability CloudRING. Он нужен, чтобы AI-агенты и будущие команды
строили платформу как целостный продукт, а не как набор несвязанных сервисов.

Capability здесь означает устойчивую продуктовую способность: что CloudRING
должен позволять сделать, кому это нужно, почему это снижает lock-in или
операционный toil, на каком stage capability впервые становится готовым
продуктом и каким readiness profile это проверяется.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-CAP-001 | Каждая capability должна иметь purpose, users, first product stage, dependencies and readiness profile. | Без этого агенты будут строить функции вне продуктового контекста. | Capability map shows these fields for each major cluster. |
| CR-CAP-002 | Capability must describe product outcome, not implementation technology. | Технологии заменяемы, а смысл должен жить дольше. | Capability statement can survive runtime/provider/backend replacement. |
| CR-CAP-003 | Capability dependencies must be explicit. | CloudRING is end-to-end; hidden dependency becomes lock-in. | Map shows upstream and downstream product dependencies. |
| CR-CAP-004 | Capability maturity must follow stages. | Каждый stage должен быть законченным продуктом. | Capability has first_stage and later_expansion stages instead of all-at-once scope. |
| CR-CAP-005 | Capability must link to conformance. | Readiness needs evidence, not intent. | Each cluster links to one or more readiness profiles. |
| CR-CAP-006 | Capability must include anti-lock-in reason when relevant. | Main mission is reducing provider, technology and jurisdiction lock-in. | Map explains how capability protects choice, portability or autonomy. |
| CR-CAP-007 | Capability must include agent-operability expectation. | Platform must be operable by one human with AI agents. | Capability declares required agent-readable state or safe agent action surface. |
| CR-CAP-008 | Capability map must avoid internal source names and implementation copying. | Requirements must remain copyright-safe and reusable. | Map uses generic product names and links to requirements, not source snippets. |

## Capability Clusters

| Capability | Purpose | Primary Users | First Product Stage | Expands In | Key Dependencies | Readiness |
|---|---|---|---|---|---|---|
| Experience Surface | Unified UI/API/CLI/Agent API for ordering, operating and understanding CloudRING. | User, admin, provider, ISV, agent | Stage 1 | All stages | Product Control Plane, Knowledge, Policy | `stage1-service-ready`, `stage6-global-ready` |
| Product Design Quality Evidence | Task-based evidence that flows are intent-first, consequence-visible, comparable, economics-aware, jurisdiction-aware, support-ready and human-agent consistent. | Product owner, user, admin, provider, governance, agent | Stage 0 | All stages | Experience Surface, Scenario Fixtures, Conformance, Metrics | All readiness profiles |
| Portal Experience Evidence | Evidence that portal/self-service UI is role/task-oriented, consequence-visible, action-parity mapped, support-ready, party-scoped and agent-safe before portal readiness is claimed. | User, admin, developer/ISV, provider, support, governance, agent | Stage 1 | Stage 4, Stage 6 | Experience Surface, Self-Service Agent Operations, UI Extension Runtime Certification, Release Environment Promotion Evidence, Support And SLA Operations, Billing Runtime Evidence, Conformance | All profiles that claim portal, operational self-service UI or provider portal readiness |
| Knowledge And Requirements Memory | Machine-readable product memory: requirements, ADR, runbooks, sources, checks and learning records. | Founder, architect, agent, governance owner | Stage 0 | Stage 7 | Governance, Agent Operations, Conformance | `stage0-requirements-memory-ready`, `stage7-self-evolving-ready` |
| Documentation And Decision Memory | Source-safe docs, ADR/no-ADR rationale, feedback, source-pass lessons, templates, examples, scenarios and conformance gates as one reusable product memory chain. | Founder, developer, support, governance owner, AI agent | Stage 0 | All stages | Knowledge Memory, Source Coverage, Conformance, Scenario Fixtures | `stage0-requirements-memory-ready`, `stage1-service-ready`, `stage7-self-evolving-ready` |
| End-To-End Product Architecture | Cross-layer product contract connecting roles, presences, service lifecycle, marketplace, billing, trust, exit, operations and learning loops. | Founder, architect, provider, governance, agent | Stage 0 | All stages | Requirements Memory, Stages, Capability Contracts, Conformance | All readiness profiles |
| Open Cloud Standard | Portable service/capability/lifecycle contract with information model, schema governance, environment, dependency, UI, task and evidence semantics independent of runtime. | Developer, ISV, provider, agent | Stage 1 | All stages | Service Factory, Conformance, Policy | `stage1-service-ready`, `stage3-private-store-ready` |
| Service Factory | Create, validate, document, observe and package services from standard templates, runtime profiles, bounded tasks and agent-readable outputs. | Developer, ISV, agent | Stage 1 | Stage 3, Stage 4 | Open Cloud Standard, Local Runtime, Docs, Tasks | `stage1-service-ready` |
| Developer Workflow Scenario Evidence | Role-based proof that developer onboarding and local lifecycle are complete journeys with prerequisites, states, negative cases, cleanup, e2e scope, confidence and source-safety. | Developer, service owner, support, AI agent | Stage 1 | All stages where workflow proof is claimed | Service Factory, Lifecycle Command Surface, Documentation, Agent Operations, Conformance | `stage1-service-ready`; all workflow-claiming profiles |
| Reference Service Portfolio Evidence | Portfolio proof that golden/reference services cover required archetypes with purpose, first useful behavior, contract source-of-truth, docs/template readiness, observability, task/data/object/secret evidence, support handoff, portability lessons and non-claims. | Developer, service owner, support, governance, AI agent | Stage 1 | Stage 3, Stage 4, Stage 6 | Service Factory, Developer Workflow Scenario Evidence, Service Dependency Deployment Model, Documentation, Support Diagnostics, Release Environment Promotion Evidence, Service Registry Catalog Publication, Conformance | `stage1-service-ready`; provider/catalog/global profiles when reference portfolio readiness is claimed |
| Lifecycle Command Surface | Command/API/Agent action evidence for create, validate, debug, start, stop, logs, env, docs, tasks, plugins and generated artifacts. | Developer, support, admin, agent | Stage 1 | All stages | Open Cloud Standard, Service Factory, Agent Operations, Conformance | `stage1-service-ready`; all command-exposing profiles |
| Local Runtime And Dependency Sandbox | Run service and declared dependencies locally with safe secret and observability flows. | Developer, agent | Stage 1 | Stage 2 | Service Factory, Components, Secret Boundary | `stage1-service-ready` |
| Presence Bootstrap Activation | Trusted activation of local/private presence through artifact provenance, config schema, preflight, runtime provider matrix, diagnostics, rollback/cleanup, offline/private distribution and agent approval evidence. | Developer, admin, infrastructure owner, support, AI agent | Stage 1 | Stage 2, Stage 4 | Service Factory, Infrastructure Profiles, Security, Agent Operations, Conformance | `stage1-service-ready`, `stage2-private-presence-ready` |
| Controlled Extension And Task Automation | Governed tasks, plugins, dependency mutations and boilerplate generation with owner, provenance, scope, env/secret boundary, rollback, structured result and agent approval. | Developer, service owner, security owner, support, AI agent | Stage 1 | Stage 2, Stage 3, Stage 4 | Service Factory, Security, Agent Operations, Open Cloud Standard, Conformance | `stage1-service-ready`; managed execution profiles when task/plugin automation is claimed |
| Service Dependency Deployment Model | Effective service model, dependency graph, generated artifact inventory, env handoff, component ownership, conflict preflight and portability evidence. | Developer, service owner, support, agent | Stage 1 | Stage 2, Stage 3, Stage 4 | Open Cloud Standard, Service Factory, Local Runtime, Portability, Conformance | `stage1-service-ready`; private/provider profiles when generated deployment artifacts are claimed |
| UI Extension Runtime Certification | Embedded UI and validation runtime certification with host authority, scoped context, lifecycle cleanup, validation parity, browser/accessibility evidence, artifact identity and support owner. | ISV, admin, user, support, governance, agent | Stage 3 | Stage 4, Stage 6 | Open Cloud Standard, Experience Surface, Security Secret And Supply Chain, Marketplace Productization, Conformance | `stage3-private-store-ready`; provider/global profiles when embedded UI publication is claimed |
| IAM And Resource Manager | Identity, ownership, permissions and resource accounting across all scopes. | User, admin, provider, agent | Stage 2 | All stages | Policy, Audit, Domain Model | `stage2-private-presence-ready` |
| Policy And Placement | Decide allowed actions, placement, data residency, budgets, trust and approvals before execution. | User, admin, governance, agent | Stage 2 | Stage 5, Stage 6 | IAM, Provider Attributes, Trust, Compliance | `stage2-private-presence-ready`, `stage6-global-ready` |
| Infrastructure Capabilities | Compute, network, storage, backup, observability and replaceable backend profiles. | Admin, provider, service owner | Stage 2 | Stage 4, Stage 6 | IAM, Policy, Control Plane, Conformance | `stage2-private-presence-ready`, `stage4-public-provider-ready` |
| Base OS Image Factory | Reusable VM/base image lines with classified build inputs, unattended install evidence, provisioning, guest readiness, cleanup/sealing, immutable artifact identity and promotion lifecycle. | Admin, provider, support, security owner, agent | Stage 2 | Stage 4, Stage 5, Stage 6 | Infrastructure Capabilities, Security Secret And Supply Chain, Observability, Conformance | `stage2-private-presence-ready`; provider profiles when reusable image catalogs are claimed |
| Stateful Recovery Evidence | Reusable proof for topology, backup, restore, PITR, failover, endpoint ownership, audit findings and recovery source safety. | Admin, provider, support, tenant, agent | Stage 2 | Stage 4, Stage 5, Stage 6 | Infrastructure, Observability, Portability, Conformance | `stage2-private-presence-ready`, `stage4-public-provider-ready`, `stage5-federation-ready` |
| Private Presence | Autonomous local/private CloudRING installation with local control and future federation path. | Admin, private cloud owner, agent | Stage 2 | Stage 3, Stage 5 | Installer, IAM, Infrastructure, Backup | `stage2-private-presence-ready` |
| Service Store | Private app-store model for finding, installing, updating, licensing and removing services. | Admin, user, ISV, agent | Stage 3 | Stage 6 | Open Cloud Standard, Certification, Entitlement | `stage3-private-store-ready` |
| Service Registry Catalog Publication | Governed service registry records, catalog cards, publication lifecycle, sync/cache and source-safe publication evidence before services become visible or install-ready. | ISV, admin, support, governance, AI agent | Stage 3 | Stage 4, Stage 5, Stage 6 | Open Cloud Standard, Service Store, Security, Support, Conformance | `stage3-private-store-ready`; provider/federation/global profiles when catalog sync or publication is claimed |
| Product Service Integration Contract | Source-safe package proving that a product service can connect to shared platform capabilities with stable identity, scoped access, resource lifecycle, docs/spec consistency, fixtures and support handoff. | ISV, admin, support, governance, AI agent | Stage 3 | Stage 4, Stage 5, Stage 6 | Open Cloud Standard, Service Registry, Billing Runtime Evidence, Security, Documentation, Conformance | `stage3-private-store-ready`; provider/federation/global profiles when shared-capability integration is claimed |
| Marketplace Productization | Service cards, plans, artifact publication evidence, compatibility, trust, support, pricing and buyer decision support. | Buyer, ISV, provider | Stage 3 | Stage 6 | Service Store, Billing, Trust, Experience | `stage3-private-store-ready`, `stage6-global-ready` |
| Entitlement And Licensing | Local/connected/offline rights to use, update, support and monetize services. | User, admin, ISV, provider | Stage 3 | Stage 6 | Marketplace, Billing, Store, Trust | `stage3-private-store-ready` |
| Public Provider Kit | Allow independent operator to run a public provider presence and sell services. | Provider, tenant, agent | Stage 4 | Stage 5, Stage 6 | Provider Onboarding, Billing, Support, Security | `stage4-public-provider-ready` |
| Release Environment Promotion Evidence | Governed release/promotion proof for modules, services, task images, UI bundles and base images with artifact identity, environment bundle, runner semantics, approval, rollback and source safety. | Provider, release owner, developer, support, security owner, AI agent | Stage 4 | Stage 1, Stage 2, Stage 3, Stage 5, Stage 6 | Security Secret And Supply Chain, Marketplace Productization, Base OS Image Factory, UI Extension Runtime Certification, Conformance | `stage4-public-provider-ready`; all artifact-promotion profiles when release readiness is claimed |
| Usage Billing And Credits | Transparent usage validation, decision ledger, invoice, credit, dispute and billing evidence. | Buyer, provider, ISV, finance agent | Stage 4 | Stage 5, Stage 6 | Orders, Entitlements, Usage Gateway, Audit | `stage4-public-provider-ready`, `stage6-global-ready` |
| Billing Runtime Evidence | Billable usage receipt/status, event identity, idempotency, backpressure, replay/quarantine, release history and settlement freeze evidence. | Buyer, provider, support, finance agent, AI agent | Stage 4 | Stage 5, Stage 6 | Usage Billing, Entitlements, Audit, Conformance | `stage4-public-provider-ready`, `stage5-federation-ready`, `stage6-global-ready` |
| Settlement Closure And Dispute Evidence | Provider-local and cross-participant periods close only after reconciliation, freeze, correction lineage, dispute hold/release, participant-share views, approval and closeout export evidence. | Buyer, provider, participant, ISV, support, finance agent, governance, AI agent | Stage 4 | Stage 5, Stage 6 | Billing Runtime Evidence, Entitlements, Federation, Support, Audit, Conformance | `stage4-public-provider-ready`, `stage5-federation-ready`, `stage6-global-ready` |
| Support And SLA Operations | Support ownership, incident flow, SLA/SLO, maintenance and credit evidence. | User, provider, support agent | Stage 4 | Stage 5, Stage 6 | Observability, Billing, Provider Chain | `stage4-public-provider-ready`, `stage6-global-ready` |
| Support Diagnostics Evidence | Read-only source-safe diagnostics package with lifecycle state, correlation, primary failure story, issue classification, operational signals, image/stateful summaries, redaction, approval and retention. | Provider, tenant, support, governance, AI agent | Stage 4 | Stage 5, Stage 6, Stage 7 | Observability, Billing Runtime Evidence, Stateful Recovery Evidence, Security, Conformance | `stage4-public-provider-ready`; all profiles that claim support diagnostics readiness |
| Support Case SLA Credit Evidence | Source-safe support case object with owner, escalation, support boundary, SLA clock, customer impact, diagnostics/billing/settlement links, credit/refund review, party views and agent handoff. | Tenant, provider, support, finance, governance, AI agent | Stage 4 | Stage 5, Stage 6, Stage 7 | Support Diagnostics Evidence, Billing Runtime Evidence, Settlement Closure, Marketplace Productization, Conformance | `stage4-public-provider-ready`; all profiles that claim support, SLA, credit, refund or dispute readiness |
| Federation Layer | Connect independent presence through scoped sync, authentic/replay-safe events, trust, catalog, settlement and operations. | Provider, private owner, buyer, governance | Stage 5 | Stage 6 | Event Sync, Trust, Billing, Policy | `stage5-federation-ready` |
| Cross-Provider Operations | Backup, replication, migration, DR, burst and support handoff across participants. | User, admin, provider, agent | Stage 5 | Stage 6 | Portability, Policy, Settlement, Support | `stage5-federation-ready`, `stage6-global-ready` |
| Global Discovery And Network | Global cloud-of-clouds discovery, policy, trust, settlement and portfolio view without central lock-in. | Buyer, provider, ISV, governance, agent | Stage 6 | Stage 7 | Federation, Trust, Policy, Settlement | `stage6-global-ready` |
| Distributed Trust And Governance | Certification, trust anchors, downgrades, disputes, waivers and scoped governance. | Governance owner, buyer, provider, agent | Stage 5 | Stage 6, Stage 7 | Conformance, Audit, Federation, Policy | `stage5-federation-ready`, `stage6-global-ready` |
| Portability And Exit | Export, migration, restore, exit evidence and honest non-portability limits. | User, admin, buyer, agent | Stage 1 | All stages | Open Cloud Standard, Storage, Policy | All readiness profiles |
| Observability And Operations | Health, metrics, logs, traces, incidents, capacity and remediation evidence. | Admin, provider, support, agent | Stage 1 | All stages | Service Factory, Infrastructure, Support | All readiness profiles |
| Security Secret And Supply Chain | Secret boundary, brokered access ledger, artifact integrity/provenance, image residue checks, extension trust and audit. | Admin, security owner, agent | Stage 1 | All stages | IAM, Policy, Conformance, Plugin Security | All readiness profiles |
| Secret Runtime Readiness | Encrypted credential runtime evidence for scope binding, key custody, reconciliation, install/delete, health/metrics, rotation and source-safe non-claims. | Admin, security owner, support, agent | Stage 2 | Stage 4, Stage 5, Stage 6 | Security Secret And Supply Chain, IAM, Policy, Observability, Conformance | `stage2-private-presence-ready`; provider/federation profiles when secret-managed runtime is claimed |
| Agent Operations | Scoped agent identity, plan, dry-run, validation, rollback and audit. | Founder, admin, provider, governance | Stage 1 | All stages | Approval Matrix, Knowledge, Conformance | All readiness profiles |
| Continuous Evolution | Convert signals into requirements, ADR, runbooks, checks and validated learning. | Founder, governance, agent, ecosystem | Stage 7 | Ongoing | Knowledge, Metrics, Conformance, Agents | `stage7-self-evolving-ready` |

## Catalog And Marketplace Taxonomy

| Term | First Stage | Product Meaning |
|---|---:|---|
| Service Catalog | Stage 1 | Canonical service/version/capability/support/readiness records used by control plane and agents. It is not necessarily commercial. |
| Private Service Store | Stage 3 | Local/private app-store experience for install/update/remove/licensing under private owner policy. It can work without public marketplace or settlement. |
| Public Provider Marketplace | Stage 4 | Provider-local commercial surface for tenants, plans, billing, support, SLA and public offers operated by one provider. |
| Federated Marketplace | Stage 5 | Multi-participant catalog/offer/usage/settlement evidence exchange across independent presences. |
| Global Discovery Index | Stage 6 | Global search/comparison/ranking layer that explains policy/trust/freshness and points back to local owners without becoming lifecycle owner. |

## Detailed Capability Contracts

- [capabilities/open-cloud-standard-contract.md](capabilities/open-cloud-standard-contract.md)
  - portable service manifest schema, lifecycle result object, dependency
  connection, task operation, UI embed, validation, runtime certification,
  extension and conformance contract.
- [capabilities/service-factory-local-runtime.md](capabilities/service-factory-local-runtime.md)
  - templates, local runtime profile, dependency sandbox, command matrix, task
  runner, docs, plugins, generated artifact inventory, presence bootstrap
  activation and developer/agent paved road.
- [40-presence-bootstrap-activation-evidence.md](40-presence-bootstrap-activation-evidence.md)
  - trusted bootstrap assets, config schema/profile, preflight, runtime provider
  matrix, diagnostics, rollback/cleanup, offline/private distribution,
  infrastructure profile update and source-safe activation evidence.
- [41-controlled-extension-and-task-automation-evidence.md](41-controlled-extension-and-task-automation-evidence.md)
  - governed task, plugin, dependency mutation and boilerplate generation
  evidence for artifact trust, scope, env/secret boundary, rollback,
  structured result, managed-runner boundary and agent approval.
- [43-developer-workflow-scenario-evidence.md](43-developer-workflow-scenario-evidence.md)
  - role-based developer workflow evidence for prerequisites, thin e2e scope,
  run-profile confidence, negative cases, cleanup, handoff and source safety.
- [44-release-environment-promotion-evidence.md](44-release-environment-promotion-evidence.md)
  - release/promotion evidence for module identity, dependency/toolchain state,
  checks, runner semantics, immutable artifact, environment bundle, approval,
  rollback, retention, post-promotion verification and source safety.
- [42-service-registry-catalog-publication-evidence.md](42-service-registry-catalog-publication-evidence.md)
  - governed registry identity, catalog card publication, lifecycle, policy
  visibility, sync/cache, source coverage and source-safe publication evidence.
- [45-product-service-integration-contract-evidence.md](45-product-service-integration-contract-evidence.md)
  - product service integration package, stable product identity, scoped access,
  resource lifecycle, human onboarding, machine contract, docs/spec drift,
  positive/negative fixtures, support handoff, decommission and source safety.
- [46-support-diagnostics-evidence.md](46-support-diagnostics-evidence.md)
  - read-only support diagnostics package, lifecycle state, correlation,
  primary failure story, issue classification, image/stateful summaries,
  staged disclosure, approval, retention and source safety.
- [47-support-case-sla-credit-evidence.md](47-support-case-sla-credit-evidence.md)
  - support case, owner/escalation, support boundary, SLA clock, customer
  impact, diagnostics/billing/settlement links, credit/refund review,
  party-scoped views, agent boundaries and source safety.
- [48-portal-experience-evidence.md](48-portal-experience-evidence.md)
  - portal/self-service UI evidence for role journeys, action parity,
  consequence-before-action, mode claims, support handoff, party-scoped views,
  completion metrics and agent boundaries.
- [capabilities/security-secrets-supply-chain.md](capabilities/security-secrets-supply-chain.md)
  - secret boundary, brokered access ledger, classified secret fields, artifact
  provenance/integrity, image hardening, extension trust and source safety.
- [capabilities/federation-global-trust-network.md](capabilities/federation-global-trust-network.md)
  - participant registry, scoped sync, authentic/replay-safe event envelope,
  global discovery, trust governance, disputes, offboarding and local autonomy.
- [capabilities/iam-resource-manager.md](capabilities/iam-resource-manager.md) -
  ownership, identity, permissions, agent boundaries, resource lifecycle and
  local autonomy.
- [capabilities/policy-placement.md](capabilities/policy-placement.md) -
  explainable policy decisions, jurisdiction, data residency, provider chain,
  placement, ranking transparency and approvals.
- [capabilities/service-catalog-product-control-plane.md](capabilities/service-catalog-product-control-plane.md)
  - service/version/offer/order/instance/support boundaries,
  provider/publisher readiness, artifact evidence, lifecycle and
  readiness-governed catalog behavior.
- [capabilities/billing-entitlements-settlement.md](capabilities/billing-entitlements-settlement.md)
  - usage validation, decision ledger, period/overlap policy, replay/duplicate
  tests, invoices, entitlements, settlement closure, disputes, staged
  settlement and commercial exit.
- [39-settlement-closure-and-dispute-evidence.md](39-settlement-closure-and-dispute-evidence.md)
  - closure runs, input manifests, reconciliation, freeze, correction lineage,
  participant shares, dispute hold/release, approval, closeout export,
  release/history and source-safe financial evidence.
- [capabilities/infrastructure-capability-profiles.md](capabilities/infrastructure-capability-profiles.md)
  - replaceable infrastructure profiles, capacity, private/edge/public presence,
  bootstrap activation state, backup/restore, base image supply and cross-cloud
  connectivity.
- [capabilities/observability-support-operations.md](capabilities/observability-support-operations.md)
  - health, incidents, SLO/SLA, support ownership, maintenance, remediation and
  operational learning.
- [capabilities/portability-exit-cross-provider.md](capabilities/portability-exit-cross-provider.md)
  - portability profiles, export/import/restore, provider/jurisdiction/technology
  exit and cross-provider operations.
- [capabilities/self-service-agent-operations.md](capabilities/self-service-agent-operations.md)
  - user/admin/provider/ISV self-service, agent plans, approvals, dry-run,
  validation and evidence.
- [25-end-to-end-cloudring-architecture-spec.md](25-end-to-end-cloudring-architecture-spec.md)
  - cross-layer product architecture for role journeys, presences, service
  product thread, marketplace, federation, trust, exit, operations and learning
  loops.

## Capability Dependency Rules

1. A capability cannot be called product-ready without a readiness profile or a
   documented future-stage non-goal.
2. A capability that touches data, money, trust, policy or lifecycle must expose
   evidence and audit for both humans and agents.
3. A capability that introduces a backend or provider dependency must also define
   portability, exit or containment story.
4. A capability used by marketplace/federation must be described through Open
   Cloud Standard or a documented ADR exception.
5. A capability that needs AI-agent operation must declare risk class, allowed
   actions, forbidden actions and validation evidence.

## Agent Usage

Before designing or implementing any CloudRING feature, an AI-agent should:

1. Identify the capability cluster.
2. Read linked stage, ADR and conformance profile.
3. Confirm first product stage and non-goals.
4. Check upstream dependencies.
5. Produce plan with required evidence and readiness target.
6. Stop if the feature bypasses ownership, policy, portability, secret boundary
   or conformance.
