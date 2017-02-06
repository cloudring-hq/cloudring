# Conformance Profile - Stage 2 Private Presence Ready

---
profile_id: stage2-private-presence-ready
profile_version: 0.6
stage: 2
stage_file: ../stages/02-private-cloud-os-zone.md
change_note: SRC-PASS-020 added reusable private presence bootstrap activation evidence gate after recovery, secret and image evidence gates.
---

## Purpose

Доказать, что Stage 2 дает автономную private CloudRING presence под локальным
контролем: install, health, policy, self-service workload, backup/restore,
upgrade path and graceful degradation.

## Gates

| ID | Gate | Why | Required Evidence | Critical Blocker |
|---|---|---|---|---|
| CONF-STAGE2-001 | Presence installs in declared profile. | Private cloud must be usable without public provider. | Single-host or multi-node install evidence with declared capabilities, image/template identity, bootstrap policy and first-boot validation where VM images are used. | Install requires hidden manual integration. |
| CONF-STAGE2-002 | Local portal/API/CLI/Agent API and admin health view exist. | Admin and agent need one operational reality. | Admin/agent sees health, capacity, alerts, upgrade status and policy violations. | No unified health/control view. |
| CONF-STAGE2-003 | Basic workload self-service works. | Stage 2 must deliver cloud value, not only installation. | User creates, observes, changes and removes supported basic workload. | Workload requires operator ticket/manual provisioning. |
| CONF-STAGE2-004 | IAM/resource ownership/audit baseline exists. | Private cloud needs accountable boundaries. | Identity, owner, resource, policy and audit evidence. | Critical action has no owner/audit. |
| CONF-STAGE2-010 | Core capability matrix is explicit. | Private presence must show what is available, degraded or unsupported. | Compute, network, storage, monitoring, image/template supply, diagnostics, policy and audit capability matrix. | Missing critical capability is hidden from readiness report. |
| CONF-STAGE2-005 | Backup/restore/failover is tested for claimed stateful or HA capability. | Untested backup and unproven failover are not cloud readiness. | Evidence shows topology and endpoint ownership, selected backup identity, archive continuity, restore target, integrity checks, service smoke test, observed RPO/RTO, failover drill freshness, normalized audit bundle, source-safe redaction/classification and recovery note. | Stateful/HA capability is claimed without current restore/PITR/failover proof or has blocking audit failures. |
| CONF-STAGE2-012 | Stateful recovery evidence bundle is reusable and source-safe. | Private presence recovery must be reproducible by a human with agents without raw operational context. | Stateful readiness evidence links topology, backup/archive, restore/PITR, failover, endpoint ownership, audit findings, role matrix, source/history coverage, source-safety and non-claims through the reusable template. | Backup, restore or failover readiness is described only in prose, raw logs, raw inventories or stale runbook notes. |
| CONF-STAGE2-006 | Upgrade uses plan/apply/validate flow. | Local platform must evolve safely. | Upgrade plan, impact, validation and rollback/compensation evidence. | Upgrade mutates platform without validation. |
| CONF-STAGE2-007 | Secret management and operational evidence follow trust boundary. | Private presence contains real trust boundaries and sensitive operational evidence. | Secret references have owner/scope/environment; no plaintext secret artifacts; build profiles, generated image evidence and operational audit bundles classify secret, sensitive-private, public-catalog, generated and local-only fields. | Secret values or source-private topology/log/grant/IaC state appear in generated specs, reports or agent context. |
| CONF-STAGE2-013 | Secret runtime readiness evidence is reusable and source-safe. | Private presence must not treat encrypted-at-rest or secret-safe documentation as runtime credential readiness. | Evidence links `CR-SECRETRUN-001..032`, `SCENARIO-STAGE2-006`, key custody, scope binding, observed generation/conditions, install/delete behavior, RBAC, health/metrics, rotation/degraded behavior, source safety and non-claims through the reusable template. | Raw secret, credential, encrypted material or key material enters report/agent context; scope/key/status is unknown; or readiness is claimed from encryption alone. |
| CONF-STAGE2-014 | Base OS image factory readiness evidence is reusable and source-safe. | Private presence must not treat a built VM template as cloud-ready without install, provisioning, cleanup, first-boot, provenance and promotion proof. | Evidence links `CR-BASEIMG-001..032`, `SCENARIO-STAGE2-007`, input classification, unattended install summary, provisioning roles, guest readiness, cleanup/sealing, immutable artifact identity, first-boot smoke, rollback/deprecation, source safety and non-claims through the reusable template. | Raw build profile values enter report/agent context; cleanup/sealing or first-boot state is unknown; artifact identity is mutable; or backend-specific image is claimed portable without limitations. |
| CONF-STAGE2-015 | Presence bootstrap activation evidence is reusable and source-safe. | Private presence readiness cannot be inferred from local bootstrap docs, CLI install or runtime start. | Evidence links `CR-PRESBOOT-001..032`, `SCENARIO-STAGE2-008`, activation workflow, artifact provenance, config schema/profile, preflight, runtime provider matrix, diagnostics, rollback/cleanup, infrastructure profile state, agent approval, source safety and non-claims through the reusable template. | Presence is marked ready while artifact trust, preflight, rollback, diagnostics, local autonomy or private-source redaction is missing. |
| CONF-STAGE2-008 | Federation-ready metadata exists without requiring federation. | Stage 2 should not become a dead end. | Catalog/policy/usage/audit metadata shaped for future sync. | Future federation requires redesign of resource identity. |
| CONF-STAGE2-009 | Graceful degradation is visible. | Private infrastructure can be imperfect. | Degraded capability affects health, placement, user actions and report. | Platform reports ready while critical capability is degraded. |
| CONF-STAGE2-011 | Role scenario coverage matrix exists for private presence. | Admin, user and AI-agent must operate private cloud without hidden support project. | Scenario matrix links admin install/health/recovery/update, user workload, support/emergency and agent operation fixtures with not-applicable roles marked. | Stage 2 passes without reusable admin/user/agent scenario evidence. |

## Required Report Outcome

`stage2-private-presence-ready` is passed when private presence works locally,
critical state is recoverable, degradation is honest and federation is only a
future-ready path, not a hidden dependency.

## Profile Non-Goals

- Private app store.
- Public tenant marketplace.
- Multi-provider federation.
- Global settlement or global portal dependency.
