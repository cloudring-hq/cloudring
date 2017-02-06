# Role Scenario Fixtures

Эта папка хранит reusable role scenario fixtures для проверки CloudRING stages.
Fixtures используют только synthetic objects from
[synthetic-fixture-catalog.md](synthetic-fixture-catalog.md), чтобы агенты могли
проверять продуктовые сценарии без старых исходников, private context or real
tenant data.

## Index

| Stage | Fixture | Primary Roles |
|---|---|---|
| Stage 0 | [stage0/SCENARIO-STAGE0-001-requirements-memory-continuation.md](stage0/SCENARIO-STAGE0-001-requirements-memory-continuation.md) | founder, architect, AI agent |
| Stage 0 | [stage0/SCENARIO-STAGE0-002-source-intake-review.md](stage0/SCENARIO-STAGE0-002-source-intake-review.md) | developer, governance, AI agent |
| Stage 0 | [stage0/SCENARIO-STAGE0-003-requirements-design-quality-intake.md](stage0/SCENARIO-STAGE0-003-requirements-design-quality-intake.md) | product owner, governance, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-001-first-portable-service.md](stage1/SCENARIO-STAGE1-001-first-portable-service.md) | developer, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-002-user-docs-support-handoff.md](stage1/SCENARIO-STAGE1-002-user-docs-support-handoff.md) | user, support, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-003-developer-simplicity-quality.md](stage1/SCENARIO-STAGE1-003-developer-simplicity-quality.md) | developer, service owner, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-004-ocs-minimum-model-validation.md](stage1/SCENARIO-STAGE1-004-ocs-minimum-model-validation.md) | developer, service owner, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-005-service-lifecycle-command-evidence.md](stage1/SCENARIO-STAGE1-005-service-lifecycle-command-evidence.md) | developer, service owner, support, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-006-documentation-decision-memory-handoff.md](stage1/SCENARIO-STAGE1-006-documentation-decision-memory-handoff.md) | developer, service owner, support, governance, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-007-service-dependency-deployment-model.md](stage1/SCENARIO-STAGE1-007-service-dependency-deployment-model.md) | developer, service owner, support, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-008-controlled-extension-task-automation.md](stage1/SCENARIO-STAGE1-008-controlled-extension-task-automation.md) | developer, service owner, security owner, support, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-009-developer-workflow-scenario-evidence.md](stage1/SCENARIO-STAGE1-009-developer-workflow-scenario-evidence.md) | developer, service owner, support, AI agent |
| Stage 1 | [stage1/SCENARIO-STAGE1-010-reference-service-portfolio-evidence.md](stage1/SCENARIO-STAGE1-010-reference-service-portfolio-evidence.md) | developer, service owner, support, governance, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-001-private-presence-recovery.md](stage2/SCENARIO-STAGE2-001-private-presence-recovery.md) | admin, support, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-002-private-user-workload-policy.md](stage2/SCENARIO-STAGE2-002-private-user-workload-policy.md) | user, admin, governance, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-003-private-degraded-choice.md](stage2/SCENARIO-STAGE2-003-private-degraded-choice.md) | admin, user, support, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-004-stateful-restore-drill.md](stage2/SCENARIO-STAGE2-004-stateful-restore-drill.md) | admin, support, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-005-stateful-failover-drill.md](stage2/SCENARIO-STAGE2-005-stateful-failover-drill.md) | admin, support, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-006-secret-runtime-readiness.md](stage2/SCENARIO-STAGE2-006-secret-runtime-readiness.md) | admin, user, support, governance, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-007-base-os-image-readiness.md](stage2/SCENARIO-STAGE2-007-base-os-image-readiness.md) | admin, support, governance, AI agent |
| Stage 2 | [stage2/SCENARIO-STAGE2-008-presence-bootstrap-activation.md](stage2/SCENARIO-STAGE2-008-presence-bootstrap-activation.md) | admin, infrastructure owner, security owner, support, AI agent |
| Stage 3 | [stage3/SCENARIO-STAGE3-001-private-store-install.md](stage3/SCENARIO-STAGE3-001-private-store-install.md) | admin, user, ISV, AI agent |
| Stage 3 | [stage3/SCENARIO-STAGE3-002-service-support-disclosure.md](stage3/SCENARIO-STAGE3-002-service-support-disclosure.md) | support, governance, admin, ISV |
| Stage 3 | [stage3/SCENARIO-STAGE3-003-private-store-choice-quality.md](stage3/SCENARIO-STAGE3-003-private-store-choice-quality.md) | user, admin, ISV, AI agent |
| Stage 3 | [stage3/SCENARIO-STAGE3-004-ocs-extension-compatibility.md](stage3/SCENARIO-STAGE3-004-ocs-extension-compatibility.md) | ISV, admin, governance, AI agent |
| Stage 3 | [stage3/SCENARIO-STAGE3-005-ui-extension-runtime-certification.md](stage3/SCENARIO-STAGE3-005-ui-extension-runtime-certification.md) | ISV, admin, user, support, governance, AI agent |
| Stage 3 | [stage3/SCENARIO-STAGE3-006-service-registry-publication.md](stage3/SCENARIO-STAGE3-006-service-registry-publication.md) | ISV, admin, support, governance, AI agent |
| Stage 3 | [stage3/SCENARIO-STAGE3-007-product-service-integration-contract.md](stage3/SCENARIO-STAGE3-007-product-service-integration-contract.md) | ISV, admin, support, governance, AI agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-001-public-provider-order-support.md](stage4/SCENARIO-STAGE4-001-public-provider-order-support.md) | provider, tenant, support, billing agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-002-isv-publication-certification.md](stage4/SCENARIO-STAGE4-002-isv-publication-certification.md) | ISV, provider, governance, certification agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-003-provider-economics-transparency.md](stage4/SCENARIO-STAGE4-003-provider-economics-transparency.md) | provider, buyer, billing agent, support |
| Stage 4 | [stage4/SCENARIO-STAGE4-004-billing-runtime-ingestion-evidence.md](stage4/SCENARIO-STAGE4-004-billing-runtime-ingestion-evidence.md) | provider, buyer, support, billing agent, AI agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-005-stateful-provider-recovery-evidence.md](stage4/SCENARIO-STAGE4-005-stateful-provider-recovery-evidence.md) | provider, tenant, support, governance, AI agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-006-release-environment-promotion.md](stage4/SCENARIO-STAGE4-006-release-environment-promotion.md) | provider, release owner, support, security, AI agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-007-support-diagnostics-evidence.md](stage4/SCENARIO-STAGE4-007-support-diagnostics-evidence.md) | provider, tenant, support, governance, AI agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-008-support-case-sla-credit.md](stage4/SCENARIO-STAGE4-008-support-case-sla-credit.md) | provider, tenant, support, finance, governance, AI agent |
| Stage 4 | [stage4/SCENARIO-STAGE4-009-provider-portal-experience-evidence.md](stage4/SCENARIO-STAGE4-009-provider-portal-experience-evidence.md) | provider, tenant, support, governance, AI agent |
| Stage 5 | [stage5/SCENARIO-STAGE5-001-federated-operation-dispute.md](stage5/SCENARIO-STAGE5-001-federated-operation-dispute.md) | participant, buyer, support, governance, AI agent |
| Stage 5 | [stage5/SCENARIO-STAGE5-002-private-participant-sync.md](stage5/SCENARIO-STAGE5-002-private-participant-sync.md) | admin, ISV, provider, AI agent |
| Stage 5 | [stage5/SCENARIO-STAGE5-003-settlement-dispute-negative.md](stage5/SCENARIO-STAGE5-003-settlement-dispute-negative.md) | participant, buyer, provider, support, governance, AI agent |
| Stage 5 | [stage5/SCENARIO-STAGE5-004-ocs-cross-participant-version-mismatch.md](stage5/SCENARIO-STAGE5-004-ocs-cross-participant-version-mismatch.md) | participant, provider, buyer, support, AI agent |
| Stage 5 | [stage5/SCENARIO-STAGE5-005-cross-participant-usage-replay.md](stage5/SCENARIO-STAGE5-005-cross-participant-usage-replay.md) | participant, buyer, provider, support, governance, AI agent |
| Stage 5 | [stage5/SCENARIO-STAGE5-006-settlement-closure-dispute-evidence.md](stage5/SCENARIO-STAGE5-006-settlement-closure-dispute-evidence.md) | buyer, provider, participant, support, governance, AI agent |
| Stage 6 | [stage6/SCENARIO-STAGE6-001-global-discovery-exit.md](stage6/SCENARIO-STAGE6-001-global-discovery-exit.md) | buyer, provider, ISV, governance, AI agent |
| Stage 6 | [stage6/SCENARIO-STAGE6-002-policy-overlay-governance.md](stage6/SCENARIO-STAGE6-002-policy-overlay-governance.md) | admin, governance, provider, AI agent |
| Stage 6 | [stage6/SCENARIO-STAGE6-003-jurisdiction-overlay-choice.md](stage6/SCENARIO-STAGE6-003-jurisdiction-overlay-choice.md) | buyer, governance, provider, AI agent |
| Stage 7 | [stage7/SCENARIO-STAGE7-001-source-signal-learning.md](stage7/SCENARIO-STAGE7-001-source-signal-learning.md) | owner, governance, AI agent |
| Stage 7 | [stage7/SCENARIO-STAGE7-002-support-incident-learning.md](stage7/SCENARIO-STAGE7-002-support-incident-learning.md) | support, provider, developer, governance, AI agent |
| Stage 7 | [stage7/SCENARIO-STAGE7-003-design-regression-learning.md](stage7/SCENARIO-STAGE7-003-design-regression-learning.md) | product owner, support, developer, governance, AI agent |
| Stage 7 | [stage7/SCENARIO-STAGE7-004-ocs-model-evolution.md](stage7/SCENARIO-STAGE7-004-ocs-model-evolution.md) | governance, product owner, developer, provider, AI agent |

## Required Companions

- [synthetic-fixture-catalog.md](synthetic-fixture-catalog.md)
- [role-coverage-matrix.md](role-coverage-matrix.md)
- [../templates/role-scenario-fixture-template.md](../templates/role-scenario-fixture-template.md)

## Rules

1. Scenario fixtures prove role journeys, not implementation behavior.
2. Every scenario must include happy path and stop-condition cases.
3. Every scenario must state surfaces and expected shared state vocabulary.
4. `unknown` evidence is a warning or blocker, never a pass.
5. No fixture may include real customer/source names, endpoints, network
   addresses, credentials, source snippets or operational commands.
