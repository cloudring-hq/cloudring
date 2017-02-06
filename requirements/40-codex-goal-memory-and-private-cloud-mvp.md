# Codex Goal Memory and Private Cloud MVP Requirements

This file preserves the durable product intent from Codex goals so the
repository remains sufficient to continue the platform without relying on chat
history. It is intentionally source-safe: it captures requirements and reasons,
not private company names, private URLs, credentials, hostnames, or one-off lab
details.

## Governance Requirements

| ID | Requirement | Reason | Acceptance Evidence |
| --- | --- | --- | --- |
| CR-GOALMEM-001 | Every user-provided Codex goal that changes product direction must be captured in this repository as English, source-safe requirements before the goal is considered complete. | Chat context is transient; the repository must preserve why architecture and UX decisions exist. | A requirements file or update records the goal-derived requirements without private names, secrets, or lab-only operational details. |
| CR-GOALMEM-002 | Goal memory must preserve intent, scope, risks, and acceptance criteria, not verbatim prompts. | Verbatim prompts can contain private context and can overfit the product to one organization. | Requirements are phrased as reusable product obligations for any private-cloud provider deployment. |
| CR-GOALMEM-003 | New goal-derived requirements must be linked to implementation evidence, test gates, documentation, or an explicit backlog item. | Requirements without evidence are easy to forget or accidentally regress. | Operations logs, test plans, conformance reports, or roadmap entries reference the requirement IDs. |
| CR-GOALMEM-004 | Repository scans must reject private company names, private source URLs, credentials, host-specific secrets, and direct legacy-vendor branding. | The product must be reusable and source-safe for multiple organizations. | CI or local review commands show no forbidden branding or secrets in tracked files. |

## Private Cloud Provider MVP

| ID | Requirement | Reason | Acceptance Evidence |
| --- | --- | --- | --- |
| CR-PCPMVP-001 | The platform must be deployable from this repository as a boxed private cloud product on Ubuntu-based bare metal or corporate nested virtualization. | Operators must be able to start from OS access and converge to a working cloud without tribal knowledge. | IaC, installer, deployment docs, and live lab verification demonstrate repeatable install and upgrade. |
| CR-PCPMVP-002 | The control plane must avoid single points of failure across API, GitOps, controllers, portal, networking, storage, and tenant API access. | The platform must remain usable during host, pod, disk, and network failures. | HA topology tests and disruption drills show continued operation or documented degraded behavior without data loss. |
| CR-PCPMVP-003 | Provider APIs must support horizontally scalable, shardable reconciliation and must stay responsive under high read/write load. | Cloud-provider UX depends on fast APIs even when many tenants and resources exist. | Load tests cover provider API, portal summary, write API, controller sharding, and API fairness. |
| CR-PCPMVP-004 | The platform must support tenant self-service for virtual machines, Kubernetes clusters, volumes, networks, firewall rules, access grants, subscriptions, orders, backups, and restores. | Users must be able to build complete projects without provider engineers performing manual work. | API and portal smoke tests create, observe, update, and delete each supported resource within tenant permissions. |
| CR-PCPMVP-005 | Tenants must be isolated by namespace, RBAC, quota, network policy, admission control, audit scope, and self-service visibility. | One tenant must not affect, inspect, or exhaust another tenant's resources. | Positive and negative RBAC tests, quota/admission tests, and cross-tenant denial tests pass. |
| CR-PCPMVP-006 | Administrators must have a full operations interface for cluster health, capacity, users, roles, tenants, catalog, lifecycle, upgrades, diagnostics, repair, backup, and recovery. | A boxed product is not operationally complete if administrators must bypass the product for routine cloud management. | Admin UI/API scenarios and operational runbooks cover each lifecycle function. |
| CR-PCPMVP-007 | Users must be able to register, attach or create tenants, invite other users, and manage allowed tenant resources through UI, API, and IaC. | A private cloud must support real organizational onboarding and delegation, not only pre-created lab users. | Identity, invitation, tenant membership, and role-management flows are implemented and tested. |
| CR-PCPMVP-008 | The portal must provide a modern cloud-provider UX in English for both users and administrators. | The product must be understandable to users familiar with VM-centric clouds and Kubernetes-centric platforms. | Browser smoke tests, role scenario tests, responsive layout review, and accessibility checks pass. |
| CR-PCPMVP-009 | Dangerous operations must show an explicit warning dialog before execution and must execute only after the user clicks a red `Yes` confirmation button. | Destructive and service-disrupting actions must not happen by accidental click. | UI tests cover delete and disruptive order actions such as suspend, cancel, and plan change. |
| CR-PCPMVP-010 | The portal summary/read model must remain responsive during API-server pressure, controller restarts, pod replacement, and high object counts. | Dashboards are the first operational surface during incidents and must not cascade-fail. | Portal summary tests cover bounded lists, stale-while-refresh behavior, pod failover retries, compact payload size, and fresh read-after-write. |
| CR-PCPMVP-011 | Order lifecycle operations must support immediate and scheduled execution windows, including delayed `notBefore`, `expiresAt`, invalid windows, expired windows, and idempotent terminal behavior. | Provider-grade subscriptions need safe lifecycle control and reliable delayed changes. | API and portal contract tests verify scheduled, suspend, resume, renew, cancel, and plan-change flows. |
| CR-PCPMVP-012 | The platform must include complete English deployment, operations, upgrade, backup, restore, troubleshooting, and conformance documentation. | The repository must be enough for a new operator to deploy and safely run the product. | Docs are updated alongside implementation and referenced from operations logs and test plans. |

## Current Goal-Derived Backlog

| ID | Requirement | Reason | Acceptance Evidence |
| --- | --- | --- | --- |
| CR-GOALBACKLOG-001 | Implement a durable goal-memory workflow that records future Codex goals as source-safe requirements during each iteration. | Future work must not regress or forget previous objectives. | A checklist or automation enforces requirements updates before completion. |
| CR-GOALBACKLOG-002 | Expand the portal from prototype console to complete provider/admin/user console with role-specific navigation and safe workflows. | The MVP must be usable as a cloud-provider control panel, not only as a technical demo. | Role-based UI smoke tests and UX review artifacts cover admin and tenant journeys. |
| CR-GOALBACKLOG-003 | Add account registration, first-admin bootstrap, tenant creation, tenant invitation, user management, and role assignment. | Real pilots require onboarding without manually editing Kubernetes objects. | Identity and onboarding flows are tested through UI, API, and IaC. |
| CR-GOALBACKLOG-004 | Complete operational coverage review against a mature cloud-operations reference model without copying vendor-specific terminology or branding. | The product must cover provider and customer lifecycle operations comprehensively while remaining source-safe. | A source-safe coverage matrix maps lifecycle scenarios to platform capabilities, tests, and gaps. |
| CR-GOALBACKLOG-005 | Replace live fan-out dashboard reads with a materialized, scalable read model for provider and tenant views. | High object counts and API pressure require predictable dashboard latency. | Summary/read-model latency remains within target under load and during controller/API disruptions. |
