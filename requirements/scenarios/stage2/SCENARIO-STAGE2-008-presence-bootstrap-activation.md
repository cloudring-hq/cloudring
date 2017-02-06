# SCENARIO-STAGE2-008 - Presence Bootstrap Activation

## Purpose

Проверить, что Stage 2 private presence activation is a self-service,
evidence-first workflow: trusted bootstrap artifact, validated profile,
preflight, runtime provider state, diagnostics, rollback/cleanup, local autonomy
and agent-safe handoff.

## Roles

| Role | Goal |
|---|---|
| Private admin | Активировать single-host private presence with explicit limits. |
| Infrastructure owner | Проверить ресурсы, network/ingress and local autonomy. |
| Security owner | Убедиться, что bootstrap assets/config/env are trusted and redacted. |
| Support | Получить activation report and doctor evidence. |
| AI agent | Выполнить dry-run, собрать evidence and refuse unsafe mutation. |

## Preconditions

- Synthetic bootstrap bundle and infrastructure profile exist.
- Admin selected single-host private profile.
- Agent has approval to run dry-run and collect evidence, but not to mutate
  runtime state without explicit approval.

## Happy Path

1. Agent reads Stage 2 profile and bootstrap template.
2. Agent creates activation plan with target profile, artifact identity,
   preflight checks, expected changes and rollback plan.
3. Admin approves controlled activation.
4. Bootstrap validates artifact, config schema, profile resolution and
   resource/network prerequisites.
5. Runtime provider state is marked supported, degraded, manual-external or
   blocked with consequences.
6. Activation writes config atomically, starts supported runtime actions where
   applicable and emits activation report.
7. Doctor report summarizes health, capacity, routes, asset freshness, warnings
   and next actions.
8. Conformance report links evidence or blocks `stage2-private-presence-ready`.

## Stop-Condition Cases

| Case | Expected Product Behavior |
|---|---|
| Bootstrap artifact has unknown provenance. | Activation blocks before config write. |
| Existing config would be overwritten without backup. | Activation blocks and requests rollback plan. |
| Runtime provider is unsupported. | Presence is not marked active; report shows blocked/manual path. |
| Preflight detects insufficient resources or route conflict. | Activation stops or degrades with explicit remediation. |
| Effective env contains raw secret/topology/local path. | Evidence publication is blocked for redaction. |
| Agent attempts activation without approval. | Agent must stop and request approval. |

## Evidence

- Presence bootstrap activation evidence using
  [../../templates/presence-bootstrap-activation-template.md](../../templates/presence-bootstrap-activation-template.md).
- Infrastructure capability profile snapshot.
- Source-safe activation report.
- Doctor/diagnostic report.
- Rollback/cleanup plan.
- Source-safety validation summary.

## Requirement References

- `CR-PRESBOOT-001..032`
- `CR-INFPROFILE-001..031`
- `CR-SERVICEFACTORY-038`
- `CR-SERVICEFACTORY-048`
- `CR-LIFECMD-029..030`
- `CR-CONF-041`
- `CR-CAPEVID-031`

## Non-Claims

- This scenario does not require public provider, marketplace or federation.
- This scenario does not choose final installer, runtime provider or package
  manager.
- This scenario does not use real configs, endpoints, local paths, tenant data
  or credentials.
