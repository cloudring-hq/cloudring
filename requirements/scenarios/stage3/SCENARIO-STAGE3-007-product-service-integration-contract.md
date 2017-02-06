# SCENARIO-STAGE3-007 Product Service Integration Contract

## Intent

An ISV connects a private-store service to a shared CloudRING capability using a
source-safe integration package that humans, validators and AI agents can review
without old source access.

## Roles

| Role | Goal |
|---|---|
| ISV | Connect service to shared usage/catalog capability without leaking private context. |
| Admin | Understand what the service will send, what it can access and how it fails. |
| Support | Receive a safe diagnostic handle and ownership boundary. |
| Governance | Verify source-safety, drift and non-claims before publication. |
| AI agent | Validate package completeness and stop on unsafe evidence. |

## Preconditions

- `service-a` has an OCS manifest candidate.
- `product-a` is the canonical product identity.
- `usage-resource-a` is the synthetic metered resource.
- `stage3-private-store-ready` is the target profile.

## Happy Path

1. ISV creates a Product Service Integration Package for `service-a`.
2. Package declares product identity, capability target, profile scope and
   support owners.
3. Admin reviews scoped service credential evidence without seeing credential
   values.
4. ISV registers `usage-resource-a` or records blocked registration evidence.
5. Machine contract validates request, result, error, version and fixture shape.
6. Human onboarding guide explains prerequisites, resource lifecycle, retry,
   support and decommission in product terms.
7. Agent runs positive and negative synthetic fixtures.
8. Governance checks generated docs freshness and source-safety.
9. Report marks integration ready, warning or blocked for private-store
   publication.

## Stop Conditions

| Condition | Expected Result |
|---|---|
| Product identity is ambiguous or alias policy is missing. | Publication blocked pending owner decision. |
| Credential scope is broad, stale or profile-unknown. | Integration blocked or limited to local/dev. |
| Usage can be submitted for unregistered resources without warning. | Integration blocked for billable usage. |
| Docs/spec/runtime drift is found. | Warning or blocker with owner and fix path. |
| Success response is claimed as invoice or settlement truth. | Agent rejects evidence as overclaim. |
| Example contains real endpoint, token, path, tenant or source snippet. | Source-safety blocker. |
| Only local smoke tests exist. | Private/provider readiness remains unproven. |

## Expected Evidence

- Product service integration contract evidence.
- OCS manifest validation.
- Service registry/catalog publication evidence where service becomes visible.
- Billing runtime evidence where billable usage is claimed.
- Source-safety validation summary.

## Requirement Coverage

- `CR-SVCINT-001..032`
- `CR-CATREG-001..032`
- `CR-BILLRUN-001..032`
- `CR-CONF-046`
- `CR-CAPEVID-036`

## Non-Claims

- Does not prove downstream settlement.
- Does not prove production provider readiness.
- Does not execute live integration.
- Does not require old source files or raw API examples.
