# Conformance Profile - Stage 3 Private Store Ready

---
profile_id: stage3-private-store-ready
profile_version: 0.4
stage: 3
stage_file: ../stages/03-service-store-for-private-cloud.md
change_note: SRC-PASS-025 added product service integration contract evidence gate.
---

## Purpose

Доказать, что Stage 3 дает private cloud владельцу app-store модель готовых
сервисов: find, evaluate, install, update, remove, license and support services
without losing local control.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE3-001 | Local catalog/store is usable. | Private user needs product choice, not artifact list. | Search/filter/service card evidence with capability, compatibility and support terms. | Services can only be installed by manual operator action. |
| CONF-STAGE3-002 | Open Cloud Standard is the install contract. | Store without standard does not reduce lock-in. | Candidate has manifest, compatibility profile and conformance report. | Service installs without declared contract. |
| CONF-STAGE3-003 | `private-ready` certification gates normal install. | Private cloud must not accept unknown services as production-ready. | Dev/test install is warning-scoped; normal install requires certification including artifact identity, provenance, hardening/cleanup, boot validation and freshness where images/templates are used. | Uncertified service installs as normal production service. |
| CONF-STAGE3-004 | Install/update/remove lifecycle is idempotent plan/apply/validate self-service. | App-store model needs complete lifecycle, not only install. | User/admin completes install, update, rollback/remove with plan, validation, status and audit. | Update/removal requires undocumented manual steps. |
| CONF-STAGE3-005 | Entitlement/licensing is local-safe. | License must not become a kill switch for private cloud. | Entitlement state, offline/connected behavior, support/update terms. | Existing basic runtime stops only because remote entitlement is unavailable. |
| CONF-STAGE3-006 | Security, docs, observability and backup claims are visible. | Buyer needs informed decision before install. | Service card and readiness report show dependencies, data handling, backup/restore, docs, runbook, diagnostic boundary, known limits and image/template trust state where applicable. | Risk-critical information appears only after install. |
| CONF-STAGE3-007 | Portability statement is mandatory. | Exit must be visible before entry. | Export/import/backup/restore story or explicit limitation. | Service hides non-portability until user tries to leave. |
| CONF-STAGE3-008 | Seller/ISV gets self-service readiness feedback. | Ecosystem cannot scale through manual certification. | Failed checks expose shared validation code, path/scope, owner, next action and readiness evidence visible to seller. | Rejection gives no actionable reason. |
| CONF-STAGE3-009 | Stage 3 does not require global settlement. | Store must be complete without future federation economy. | Entitlement/usage-ready metadata can exist without multi-party settlement. | Profile blocks readiness because global settlement is absent. |
| CONF-STAGE3-010 | Connector/plugin trust follows `ADR-0006`. | Store extensibility must not bypass product trust. | Plugin/UI extension permissions, isolation, signed or otherwise verified origin, scoped context, lifecycle, redaction, support owner and policy boundaries are visible. | Plugin can bypass store policy, secret boundary or user approval. |
| CONF-STAGE3-011 | Role scenario coverage matrix exists for private service store. | App-store readiness must prove buyer/admin/ISV/agent journeys, not only catalog data. | Scenario matrix links private-store buyer, admin installer, ISV publisher, support owner and agent verification fixtures. | Stage 3 passes without reusable store role scenario evidence. |
| CONF-STAGE3-012 | UI extension runtime certification evidence is reusable and source-safe. | Private store must not treat local preview, component tests or build success as embedded UI publication readiness. | Evidence links `CR-UICERT-001..032`, `SCENARIO-STAGE3-005`, typed embed descriptor, host authority, scoped context, runtime lifecycle, validation phase/error contract, parity matrix, browser/runtime proof, accessibility/localization, artifact identity, support owner, telemetry redaction, source safety and non-claims through the reusable template. | Extension is installed as private-ready while host authority, lifecycle cleanup, validation parity, browser/runtime proof, support owner, artifact identity or source-safety is unknown. |
| CONF-STAGE3-013 | Service registry/catalog publication evidence is reusable and source-safe. | Private store must not treat static assets, seed rows, local manifests or debug success as governed catalog readiness. | Evidence links `CR-CATREG-001..032`, `SCENARIO-STAGE3-006`, registry identity, publication intent, lifecycle event, policy visibility, manifest/effective model validation, artifact trust, support chain, portability, sync/cache behavior, source coverage, source safety and non-claims through the reusable template. | Service is visible or install-ready while owner, identity scope, publication approval, lifecycle audit, support chain, artifact/dependency evidence, offline cache behavior, source coverage or source safety is unknown. |
| CONF-STAGE3-014 | Product service integration contract evidence is reusable and source-safe. | Private store must not treat API docs, generated specs, credential existence or local tests as proof that a service can safely use shared platform capabilities. | Evidence links `CR-SVCINT-001..032`, `SCENARIO-STAGE3-007`, product identity, scoped access, resource lifecycle, docs/spec/runtime drift, API version policy, submission semantics, fixtures, support handoff, decommission, source safety and non-claims through the reusable template. | Service is private-store ready while product identity, credential scope/freshness, resource registration, docs/spec/runtime consistency, negative fixtures, support handoff or source safety is unknown. |

## Required Report Outcome

`stage3-private-store-ready` is passed when private users can safely consume and
manage ready services locally, with honest license/support/portability limits.

## Profile Non-Goals

- Public provider tenant onboarding.
- Provider-local invoices.
- Cross-participant settlement.
- Global marketplace scale.
