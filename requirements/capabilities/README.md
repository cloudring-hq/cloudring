# Capability Contracts

Эта папка хранит detailed product contracts для ключевых capability CloudRING.
Они дополняют product capability map, stage profiles и conformance profiles:

- capability map показывает, где capability живет в продукте;
- stage profile показывает, когда capability становится частью finished
  increment;
- conformance profile показывает, чем доказать readiness;
- capability contract показывает, какие продуктовые обещания домен обязан
  выполнять, почему они нужны, какие evidence требуются и когда AI-agent должен
  остановиться.

## Contracts

- [open-cloud-standard-contract.md](open-cloud-standard-contract.md) -
  portable service manifest schema, lifecycle result object, dependency
  connection, task operation, UI, validation, extension and conformance
  contract.
- [service-factory-local-runtime.md](service-factory-local-runtime.md) -
  templates, trusted bootstrap activation, runtime profile, command matrix,
  controlled tasks/plugins, docs, generated artifacts, provenance-aware updates
  and developer/agent paved road.
- [security-secrets-supply-chain.md](security-secrets-supply-chain.md) -
  secret boundary, brokered access ledger, artifact provenance/integrity, image
  hardening, extension trust, source/history hygiene and source safety.
- [federation-global-trust-network.md](federation-global-trust-network.md) -
  participant registry, scoped sync, authentic/replay-safe events, global
  discovery, trust governance, disputes, offboarding and local autonomy.
- [iam-resource-manager.md](iam-resource-manager.md) - ownership, identity,
  permissions, agents, resource lifecycle and local autonomy.
- [policy-placement.md](policy-placement.md) - explainable policy decisions,
  jurisdiction, data residency, provider chain, placement and approvals.
- [service-catalog-product-control-plane.md](service-catalog-product-control-plane.md)
  - product catalog, service/version/offer/order/instance/support boundaries,
  provider/publisher readiness, artifact evidence and lifecycle operations.
- [billing-entitlements-settlement.md](billing-entitlements-settlement.md) -
  usage validation, decision ledger, period/overlap policy, replay/duplicate
  tests, invoices, entitlements, settlement closure, disputes, staged settlement
  and commercial exit.
- [infrastructure-capability-profiles.md](infrastructure-capability-profiles.md)
  - replaceable infrastructure profiles, bootstrap-backed private/edge/public
  presence, capacity, backup/restore and cross-cloud connectivity.
- [observability-support-operations.md](observability-support-operations.md) -
  health, incidents, SLO/SLA, support ownership, maintenance, remediation and
  learning loops.
- [portability-exit-cross-provider.md](portability-exit-cross-provider.md) -
  portability profiles, export/import/restore, provider/jurisdiction/technology
  exit and cross-provider operations.
- [self-service-agent-operations.md](self-service-agent-operations.md) -
  user/admin/provider/ISV self-service, agent plans, approvals, dry-run,
  validation and evidence.

## Правило

Capability contract описывает what/why/acceptance/evidence/non-goals, но не
выбирает конкретный backend, framework, vendor, protocol, payment provider,
identity provider или deployment runtime.
