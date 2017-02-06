# SCENARIO-STAGE1-008 - Controlled Extension And Task Automation

## Role Mix

- Developer/ISV
- Service owner
- Security owner
- Support
- AI agent

## User Story

Developer needs repeatable service automation for validation, local data
preparation and dependency updates. The AI agent may inspect, plan and run safe
or approved operations, but CloudRING must prevent tasks/plugins from becoming a
hidden path around policy, secrets, conformance and source safety.

## Preconditions

- Service has OCS manifest and Stage 1 local profile.
- Presence bootstrap activation evidence exists for local runtime.
- Controlled automation template is available.
- Approval matrix is active for agent-run automation.

## Main Flow

1. Developer declares an automation need.
2. CloudRING classifies it as core action, safe task, controlled task, plugin,
   library mutation or boilerplate generation.
3. If plugin is requested, CloudRING records why task/core action is
   insufficient.
4. CloudRING checks artifact identity, provenance, version policy and allowed
   distribution mode.
5. CloudRING checks scope: workspace, data, network, secrets, service env and
   working context.
6. AI agent receives redacted evidence and proposes dry-run/plan.
7. Required approval is collected for controlled/risky mutation.
8. Automation runs only within declared boundary.
9. Result is structured, redacted and linked to conformance.
10. Failure or repeated friction creates requirement, ADR, runbook, fixture or
    no-change rationale.

## Acceptance

- `CR-EXTAUTO-001..032` are covered or explicitly blocked.
- Task is preferred over plugin unless exception rationale exists.
- Artifact identity/provenance/version policy are known before readiness claim.
- Raw secrets, private topology and local paths are not exposed to the agent or
  report.
- Dependency/library mutation has plan/apply/validate and rollback evidence.
- Boilerplate output is a candidate, not a readiness claim.
- Local automation success does not imply private/provider/federation readiness.

## Negative Paths

- Plugin without owner, trust evidence or permission declaration is blocked.
- Floating dependency update in protected profile is blocked or requires
  explicit expiring approval.
- Task output containing sensitive local context is redacted or excluded before
  handoff.
- Agent request to run controlled/risky automation without dry-run and approval
  stops.
- A scaffolded service without validation remains not-ready.

## Evidence

- Controlled extension/task automation evidence.
- Task/plugin/library/boilerplate selection record.
- Artifact trust and distribution record.
- Redacted env/scope report.
- Structured result object.
- Approval and rollback/compensation record.
- Source-safety scan result.

## Non-Goals

- Не выбирать final plugin runtime, task runner, package manager or template
  engine.
- Не доказывать production/provider automation readiness.
- Не переносить source commands, plugin examples, local paths or env output.
