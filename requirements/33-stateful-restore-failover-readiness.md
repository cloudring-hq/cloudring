# Stateful Restore And Failover Readiness

This document turns stateful operations experience into a reusable CloudRING
product contract for recovery evidence. It does not prescribe a database,
orchestration tool, backup engine or HA stack. It defines what must be true
before CloudRING can honestly claim that a stateful capability is recoverable,
operable by a small team with AI agents and resistant to provider or technology
lock-in.

The source lesson is sharp: backup config, HA inventory, audit logs and runbooks
are not enough by themselves. Readiness means a current, source-safe evidence
bundle that proves restore, PITR where claimed, failover, endpoint ownership,
access boundaries, operational findings and rollback/compensation behavior.

## Requirements

| ID | Requirement | Why | Acceptance |
|---|---|---|---|
| CR-STATEFULRUN-001 | Stateful readiness must be proven by a reusable evidence bundle. | Recovery claims are repeated across stages, providers and services; prose cannot be the proof. | Evidence bundle contains identity, scope, owner, freshness, topology, backup, restore, failover, audit, access, blockers, warnings and non-claims. |
| CR-STATEFULRUN-002 | Evidence must separate backup existence from restore success. | A backup that was never restored is only hope. | Report has separate backup identity/freshness, restore target, restore execution, integrity check and service smoke-test statuses. |
| CR-STATEFULRUN-003 | PITR readiness must prove archive continuity and restore target semantics. | Point-in-time recovery fails when archives are stale, incomplete or not mapped to a business recovery point. | PITR evidence includes archive continuity, latest restorable point, target selection reason, gap handling, observed RPO and failure behavior. |
| CR-STATEFULRUN-004 | Failover readiness must prove endpoint ownership and client impact. | A promoted node is not useful if writes, DNS or clients still point to the wrong place. | Evidence shows write/read endpoint owner, routing or discovery state, client reconnect behavior, split-brain prevention and observed RTO. |
| CR-STATEFULRUN-005 | Stateful topology must be modeled as node classes and failure domains. | Host lists hide quorum, witness, replica and single-point-of-failure meaning. | Topology model names logical node classes, quorum/failure domains, replication roles, maintenance states and unsupported/manual-review states. |
| CR-STATEFULRUN-006 | Per-node overrides must not become the primary product contract. | Manual per-host duplication creates drift and makes recovery impossible to reason about. | Configuration model separates shared cluster contract, environment overrides and per-node exceptions with drift detection and owner review. |
| CR-STATEFULRUN-007 | Backup configuration changes must be treated as migrations. | Changing archive path, retention or target can silently break restore. | Change record includes compatibility check, last known good backup, rollback/compensation, validation drill and affected scopes. |
| CR-STATEFULRUN-008 | Stateful operational tasks must have preflight, dry-run where possible and result evidence. | Routine maintenance can be as dangerous as deployment. | Task evidence includes intent, scope, risk, expected mutation, preflight result, approval, execution result, validation and rollback/compensation. |
| CR-STATEFULRUN-009 | Database schema and extension boundaries must support recovery. | Schema drift and unmanaged extensions make replay, restore and migration fragile. | Service contract separates app schema, extension/system schemas, migration owner, extension policy and incompatible drift behavior. |
| CR-STATEFULRUN-010 | Schema evolution must be controlled by migration evidence, not implicit drift hiding. | Convenience patterns can mask divergent runtime states. | Migration evidence records ordered changes, rollback or compensation, explicit object ownership, drift detection and failure handling. |
| CR-STATEFULRUN-011 | Recovery runbooks must be first-class service artifacts. | A recoverable service must explain recovery before the incident. | Runbook covers restore, PITR if claimed, failover, degraded mode, validation, escalation, rollback/compensation and source-safe evidence handling. |
| CR-STATEFULRUN-012 | Recovery runbooks must be tested or marked unproven. | Untested instructions rot. | Readiness report links latest drill or marks the runbook stale, warning or blocker with owner and review trigger. |
| CR-STATEFULRUN-013 | Audit bundles must be normalized, redacted and finding-oriented. | Raw logs are noisy, unsafe and hard for agents to compare. | Audit bundle summarizes resource state, disk/capacity, replication/lag, backup/archive, critical logs, role/access changes, findings, owners and remediation status. |
| CR-STATEFULRUN-014 | Audit failures must block readiness when they affect recovery. | A report that records a failure but still passes is worse than no report. | Critical findings map to blocked, failed, degraded, waived or manual-review states with approver, expiry and compensation. |
| CR-STATEFULRUN-015 | Critical logs must be evidence, not permanent raw source memory. | Operational traces can contain tenant data, topology and secrets. | Log evidence is summarized, classified, redacted, retained by policy and linked to incidents or findings without raw sensitive payloads. |
| CR-STATEFULRUN-016 | Access roles for stateful operations must be explicit and least-privilege. | Recovery often tempts broad emergency access. | Role matrix separates read, backup, restore, failover, migration, audit, emergency and support actions with approval and evidence. |
| CR-STATEFULRUN-017 | Root or break-glass access removal must be verified. | Emergency power should not become the normal control plane. | Evidence shows normal path, break-glass path, approval, audit, revocation and post-use review without storing credentials. |
| CR-STATEFULRUN-018 | IaC state, inventory and operational plans must be classified before agent use. | Infrastructure artifacts can reveal topology, addresses, provider details and secrets. | Evidence package marks publishable, redacted, local-only and forbidden material and stops if classification is unknown. |
| CR-STATEFULRUN-019 | Current branch, alternate refs and deleted paths must be declared for stateful source passes. | Stateful decisions often live in history rather than the current tree. | Source-pass manifest records current tracked files, refs, tags, commit counts, deleted-path themes, dirty state and non-claims. |
| CR-STATEFULRUN-020 | A minimal current tree must not erase historical operational memory. | Default branch cleanup can hide the real recovery lessons. | Requirement extraction records history-backed lessons separately from current-tree lessons and avoids claiming implementation availability. |
| CR-STATEFULRUN-021 | Repeated audit, backup and HA fixes must become regression fixtures or conformance checks. | Repetition is product memory. | Repeated-fix themes create fixture backlog, readiness checks, runbook updates, ADRs or signed no-change decisions. |
| CR-STATEFULRUN-022 | Zero-tag or informal release history must weaken readiness claims. | Stateful operations need reproducible provenance. | Release/readiness evidence includes artifact/runbook version, source ref, dependency versions, validation result and rollback note; no tag means explicit limitation. |
| CR-STATEFULRUN-023 | Stateful dependency versions must be governed as recovery inputs. | Role collections, modules and backup tools can change recovery behavior. | Evidence records dependency identity, freshness, compatibility, known risks and update validation. |
| CR-STATEFULRUN-024 | Capacity and disk evidence must be tied to backup and failover decisions. | Disk pressure and archive growth can turn recovery into outage. | Audit bundle includes capacity, archive growth, threshold, forecast, affected failure domain and remediation action. |
| CR-STATEFULRUN-025 | Restore/failover drills must expose blast radius and customer impact. | Recovery can protect data while still harming users. | Drill evidence states affected services, downtime, degraded behavior, data loss window, notification, support path and billing/SLA consequence where relevant. |
| CR-STATEFULRUN-026 | Degraded recovery must be a supported state, not an ad hoc incident. | Private and edge environments often recover partially. | Report distinguishes ready, degraded, stale, blocked, manual-review and unsupported recovery with visible user/agent consequences. |
| CR-STATEFULRUN-027 | Cross-provider recovery must reuse local recovery evidence instead of inventing new trust. | Federation cannot be safer than local proof. | Stage 5+ operation references local evidence plus participant share, policy, target compatibility, replay and closure evidence. |
| CR-STATEFULRUN-028 | Recovery evidence must be portable across technology changes. | The product promise must survive database, backup engine or runtime replacement. | Evidence fields describe product semantics: topology, archive, restore, endpoint, validation, impact and source safety, not tool-specific commands. |
| CR-STATEFULRUN-029 | Stateful support must have a dispute and remediation path. | Recovery evidence is often needed after customer-visible loss. | Support flow links recovery evidence, incident timeline, affected users, owner, remediation, waiver, credit/appeal path and learning record. |
| CR-STATEFULRUN-030 | Agents must treat stateful recovery actions as controlled or risky operations. | A small team with agents needs power without unsafe mutation. | Agent handoff names allowed review actions, forbidden mutation actions, required approvals, validation needed and rollback/compensation. |
| CR-STATEFULRUN-031 | Synthetic examples must show both proof and non-proof. | Future agents need to recognize gaps, not just fill happy-path YAML. | Example includes passed, warning, blocked and non-claim fields for backup, restore, PITR, failover, audit and source safety. |
| CR-STATEFULRUN-032 | Stateful recovery evidence must remain source-safe and party-scoped. | Recovery investigations touch topology, logs, roles and customer data. | Evidence redacts secrets, topology, private source identifiers and tenant-sensitive data while preserving hashes/IDs/states enough for audit and support. |

## Evidence Model

Stateful recovery readiness evidence must answer:

- What stateful capability and stage is being claimed?
- What topology, node classes and endpoint ownership are in scope?
- Which backup/archive is selected and how fresh is it?
- What restore target was tested and what did it prove?
- Is PITR claimed, and what point can actually be restored?
- What failover behavior was drilled and what client impact was observed?
- Which audit findings block, degrade or warn readiness?
- Which roles can operate, approve, inspect and support recovery?
- Which source/history evidence informed the product requirement?
- What sensitive operational material was redacted or excluded?

## Stop Conditions

An agent must stop or mark readiness blocked when:

- backup exists but restore is untested or stale;
- PITR is claimed without archive continuity and target semantics;
- failover is claimed without endpoint ownership and split-brain prevention;
- topology, node class, quorum or failure domain is unknown;
- audit findings affect recovery but are ignored;
- recovery evidence contains raw topology, credentials, tenant data, private
  source paths, source snippets or raw log payloads;
- agent action would mutate state, roles, backup, restore, failover, endpoint or
  billing/SLA impact without approval;
- source pass claims full stateful implementation proof from current tree alone.

## Non-Goals

- Do not choose a final database, HA, DNS, storage or backup implementation.
- Do not store raw inventories, Terraform state, logs, grants, hostnames,
  addresses, credentials or commit subjects.
- Do not claim live restore, PITR or failover success from source analysis.
- Do not turn recovery evidence into a framework-specific runbook.
- Do not weaken existing `CR-OPS`, `CR-OBSOPS`, `CR-INFPROFILE` or `CR-PORTX`
  requirements; this document makes their proof reusable.
