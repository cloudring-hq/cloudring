# Synthetic Fixture Catalog

Этот каталог задает безопасные synthetic objects для role scenario fixtures.
Они не соответствуют реальным source objects, customers, providers, regions,
domains, IPs or internal systems.

## Objects

| Object ID | Type | Purpose |
|---|---|---|
| `org-owner-a` | organization | Generic owner of requirements, services or presences. |
| `user-buyer-a` | user | Generic service buyer/user. |
| `admin-private-a` | admin | Generic private presence administrator. |
| `developer-a` | developer | Generic service developer. |
| `agent-builder-a` | AI agent | Generic scoped build/verification agent. |
| `agent-support-a` | AI agent | Generic support/remediation agent. |
| `provider-public-a` | provider | Generic public provider participant. |
| `provider-public-b` | provider | Second generic public provider participant. |
| `participant-private-a` | participant | Generic private federation participant. |
| `publisher-isv-a` | publisher | Generic service publisher/ISV. |
| `product-owner-a` | product owner | Generic product owner for quality review. |
| `support-owner-a` | support owner | Generic support/SLA owner. |
| `governance-owner-a` | governance owner | Generic waiver/trust/policy owner. |
| `presence-local-a` | presence | Local development presence. |
| `presence-private-a` | presence | Private presence under local control. |
| `presence-provider-a` | presence | Public provider presence. |
| `presence-provider-b` | presence | Second independent participant presence. |
| `service-portable-a` | service | Generic portable service candidate. |
| `service-stateful-a` | service | Generic service with stateful dependency. |
| `offer-public-a` | offer | Generic public provider offer. |
| `offer-public-b` | offer | Second generic public provider offer. |
| `offer-private-a` | offer | Generic private/local offer alternative. |
| `order-a` | order | Generic order for service. |
| `usage-resource-a` | usage resource | Generic billable/informational usage resource. |
| `invoice-a` | invoice | Generic provider-local invoice. |
| `settlement-a` | settlement | Generic cross-participant settlement record. |
| `support-case-a` | support case | Generic support incident. |
| `dispute-a` | dispute | Generic billing/support/trust dispute. |
| `policy-profile-a` | policy profile | Generic policy overlay profile. |
| `jurisdiction-zone-a` | jurisdiction | Generic allowed jurisdiction class. |
| `jurisdiction-zone-b` | jurisdiction | Generic manual-review jurisdiction class. |
| `design-review-a` | review | Generic product design quality review. |
| `migration-target-a` | migration target | Generic compatible target for migration/DR. |
| `trust-profile-a` | trust profile | Generic certification/trust evidence. |
| `coverage-manifest-a` | source coverage manifest | Generic source-intake evidence. |
| `evidence-bundle-a` | evidence bundle | Generic evidence bundle for conformance. |
| `evidence-bundle-design-a` | evidence bundle | Generic design quality evidence bundle. |
| `ocs-model-a` | OCS model | Generic Open Cloud Standard information model. |
| `ocs-kind-service-manifest-a` | OCS artifact kind | Generic service manifest artifact kind. |
| `ocs-extension-a` | OCS extension | Generic namespaced standard extension. |
| `compatibility-review-a` | compatibility review | Generic OCS compatibility and migration review. |
| `standard-change-a` | standard change | Generic OCS model evolution record. |

## Data Rules

- Synthetic IDs are stable enough for requirements tests but carry no real
  operational meaning.
- Scenario fixtures may add new synthetic objects only in this file.
- Synthetic objects must not use real provider, customer, domain, host, network,
  repository or person names.
- Synthetic objects must not imply a specific implementation technology.
