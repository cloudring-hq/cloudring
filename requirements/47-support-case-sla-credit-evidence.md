# Support Case SLA Credit Evidence

## Назначение

Support Case SLA Credit Evidence фиксирует требования к тому, как CloudRING
превращает инцидент, жалобу, деградацию, спор по использованию или запрос на
компенсацию в управляемый продуктовый support case.

Главный урок source-slice: support-ready диагностика, operational docs,
service card, idempotent usage receipt и maintenance discipline сами по себе не
являются SLA, коммерческой поддержкой или credit/refund workflow. Они дают
важные доказательства, но покупатель, провайдер, ISV, support и AI-агенту нужен
отдельный объект, который связывает: кто отвечает, что было обещано, какое
воздействие на пользователя, какие часы SLA идут, что исключено, какие данные
безопасно раскрывать, когда возможен credit/refund, кто утверждает спор и что
остается non-claim.

Этот документ описывает what/why/evidence. Он не выбирает ticketing system,
ITSM-платформу, billing engine, observability stack, юридический шаблон,
конкретную схему хранения, конкретный runtime или конкретного провайдера.

## Product Boundary

- Support case - продуктовая сущность, которая связывает пользователя, заказ,
  offer, service instance, план, entitlement, support owner, severity,
  incident, SLA clock, diagnostics package and financial outcome.
- SLA/SLO decision - объяснимое решение о том, был ли нарушен обещанный уровень
  сервиса, с окном измерения, исключениями, evidence и owner approval.
- Credit/refund review - отдельный финансовый review, который использует billing
  and support evidence, но не переписывает settlement trail без коррекции и
  approvals.
- Support chain - явная цепочка first line, product owner, platform owner, ISV,
  provider, reseller or external dependency, with handoff state.
- Party-scoped view - разные безопасные представления одного case для tenant,
  provider, ISV, reseller, finance, governance and AI agent.
- Non-claim boundary - явное отделение accepted diagnostics, usage intake and
  customer communication от root cause, SLA breach, credit approval or final
  settlement.

## Source-Derived Product Signals

| Signal | Product Meaning | Requirement Output |
|---|---|---|
| Service documentation and boilerplate had support owner/contact/card placeholders, but no complete support operating model. | Support responsibility must be first-class, standardized and visible in service/offer context. | `CR-SUPCASE-001..005` |
| Service manifest and registry signals described service identity and components, but support/SLA metadata was absent or indirect. | Support metadata must be declared or linked explicitly; missing support fields are readiness gaps, not defaults. | `CR-SUPCASE-002..007`, `CR-SUPCASE-026..027` |
| Runbook and command docs supported local diagnosis, start/stop/log/docs flows and component inspection. | A support case must distinguish local troubleshooting, provider incident handling, customer action and escalation. | `CR-SUPCASE-005..007`, `CR-SUPCASE-011`, `CR-SUPCASE-016` |
| Observability and maintenance guidance existed as engineering readiness, not commercial SLA evidence. | Engineering signals are inputs to SLA/SLO decision, not the decision itself. | `CR-SUPCASE-008..013`, `CR-SUPCASE-026` |
| Usage intake had period, unit, product/resource identity, idempotency and support-safe receipt semantics. | Credits and disputes can rely on receipt/status evidence, but intake success is not invoice, settlement or credit truth. | `CR-SUPCASE-018..022` |
| Explicit credit/refund/SLA automation and support case state machine were not found in the reviewed slice. | CloudRING must block provider support/SLA claims until case, SLA and credit evidence are productized. | `CR-SUPCASE-023..032` |

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SUPCASE-001 | Every tenant-facing support request must become a Support Case object, not only free-form text. | Without a product object, agents cannot prove ownership, SLA clock, evidence, communication, financial state or closure. | Case has stable id, type, affected product object, requester role, support owner, status, severity, evidence refs, communication policy, financial relevance and non-claims. |
| CR-SUPCASE-002 | Case identity must bind offer, order, service instance, plan, entitlement and profile where applicable. | Support cannot decide responsibility or SLA without knowing the purchased promise and runtime scope. | Evidence links safe synthetic identifiers for offer/order/instance/plan/entitlement/profile and marks unknown fields warning or blocked. |
| CR-SUPCASE-003 | Service card and offer must disclose support scope before order or install. | Buyers should know who supports the service before a failure happens. | Catalog/offer view states support tier, support owner class, escalation path, maintenance policy, SLA/SLO availability and credit policy availability. |
| CR-SUPCASE-004 | Support owner and escalation owner must be explicit for every supportable service and offer. | Ownerless support creates silent failure and agent loops. | Case records first-line owner, product owner, platform owner if applicable, provider owner, ISV/reseller owner if applicable, escalation trigger and manual-review condition. |
| CR-SUPCASE-005 | Support boundary must separate customer input, service issue, platform dependency, provider incident, ISV issue, reseller issue and external dependency. | Different failure locations require different owners, evidence and promises. | Case classification uses bounded vocabulary, links diagnostics evidence and shows current owner plus prior handoff history. |
| CR-SUPCASE-006 | Severity must be a declared product decision with tenant impact, urgency and escalation consequence. | Severity cannot be inferred safely from noisy logs or emotional wording. | Severity record states impact class, affected users/services, data-risk class, response expectation, escalation deadline and who may change severity. |
| CR-SUPCASE-007 | Support case lifecycle states must be standardized. | Agents and humans need comparable progress across services and providers. | State vocabulary includes opened, triaged, waiting-customer, waiting-provider, waiting-ISV, in-remediation, workaround, resolved, credit-review, disputed, closed, learning and blocked. |
| CR-SUPCASE-008 | SLA/SLO policy must be attached or explicitly absent before SLA claims are made. | A provider cannot sell an operating promise that support cannot evaluate. | Case links SLA/SLO policy, measurement window, target, severity mapping, excluded states, maintenance treatment, evidence source and allowed non-claim. |
| CR-SUPCASE-009 | SLA clock rules must define start, pause, resume, stop and breach decision. | Ambiguous clocks cause unfair credits and support disputes. | Evidence records trigger time class, pause reasons, waiting-customer handling, maintenance handling, unknown evidence behavior, breach result and approver. |
| CR-SUPCASE-010 | Maintenance, update and deprecation events must be visible inside related cases. | Planned work can look like an outage unless impact and promise boundaries are explicit. | Case links planned/unplanned maintenance, update, rollback or deprecation event, notification state, tenant impact, SLA clock effect and compensation eligibility effect. |
| CR-SUPCASE-011 | Case must link to a Support Diagnostics Package when technical evidence is required. | Support case decisions should use safe evidence, not raw logs or private operational context. | Case references `CR-SUPDIAG-001..032`, diagnostics package id, issue classification, redaction status, retention status and unresolved diagnostic gaps. |
| CR-SUPCASE-012 | Customer impact statement must be separate from internal root-cause hypothesis. | Users need clear consequence, while root cause may be unknown or sensitive. | Case records impact summary, affected capabilities, degraded/unavailable states, workaround status, customer-visible message and explicit root-cause non-claim when needed. |
| CR-SUPCASE-013 | Communication cadence and status visibility must be declared by severity and stage. | Silence during incidents is a product failure even when remediation is ongoing. | Case states next update deadline, audience, public/private status level, current message, owner, stale communication warning and escalation when cadence is missed. |
| CR-SUPCASE-014 | Evidence disclosure must be staged by party and purpose. | Support evidence can expose tenant data, topology, finance data or source-private context. | Case separates tenant summary, provider/support details, finance details, restricted attachments, approval requirements and retention policy. |
| CR-SUPCASE-015 | Customer-required input must be explicit and bounded. | Cases stall when support waits for vague information or unsafe data dumps. | Waiting-customer state names required safe input, why it is needed, deadline, accepted redaction, SLA clock effect and alternative path if input is unavailable. |
| CR-SUPCASE-016 | Agent actions inside a support case must be allowed, forbidden or approval-required. | AI agents must help support without mutating tenant, financial or trust state unexpectedly. | Case handoff lists read-only actions, safe draft actions, remediation actions requiring approval, forbidden financial changes and validation needed. |
| CR-SUPCASE-017 | Workaround, remediation, rollback and compensation must be distinct outcomes. | A workaround may restore user flow without fixing cause or creating credit eligibility. | Case records outcome type, user consequence, permanence, rollback/compensation relation, owner and follow-up evidence. |
| CR-SUPCASE-018 | Billing/usage evidence linked to a case must preserve receipt/status semantics. | Intake success is not invoice truth, and support must not double-count or erase usage. | Case links receipt/status, event identity, period, resource/unit class, duplicate/retry status, access freshness and settlement/closure non-claim. |
| CR-SUPCASE-019 | Credit/refund request must be its own review state, not an implicit incident result. | Not every incident creates a credit, and not every credit comes from an incident. | Case enters credit-review with request reason, eligible policy, affected period, evidence refs, amount class, approver, decision and appeal path. |
| CR-SUPCASE-020 | Credit calculation evidence must be explainable without exposing raw invoices or private finance data. | Users and agents need trust, while finance details may be restricted. | Credit evidence shows policy basis, affected period, units/amount class, exclusions, correction refs, approval and party-scoped summary. |
| CR-SUPCASE-021 | Dispute hold/release must be linked to case lifecycle and settlement closure. | Disputed amounts must not settle silently or disappear from audit. | Case records disputed scope, hold status, release decision, correction lineage, closeout impact, approvals and unresolved blocker. |
| CR-SUPCASE-022 | Financial adjustments must not rewrite settlement history without correction lineage. | Auditability is part of trust and anti-lock-in. | Credit/refund/rebill outcome links original evidence, correction event, approval, settlement period impact, party views and non-destructive audit trail. |
| CR-SUPCASE-023 | Denied credits or SLA exclusions must be explainable and appealable. | Trust requires transparent refusal, not silent policy invocation. | Denial records policy clause category, evidence summary, excluded window/state, approver, customer-facing explanation, appeal route and review trigger. |
| CR-SUPCASE-024 | Party-scoped case views must protect tenant, provider, ISV, reseller and finance boundaries. | Multi-party support needs shared truth without over-sharing sensitive context. | Case view matrix states fields visible to each party, redacted classes, attachment rules, dispute visibility and governance access. |
| CR-SUPCASE-025 | Privacy and source-safety must be enforced on case text, attachments and examples. | Support cases are likely to collect unsafe names, paths, endpoints, logs, commands and tenant data. | Validation blocks private markers, secrets, network literals, raw source snippets, copied commands, raw logs, private contacts and unsafe generated examples. |
| CR-SUPCASE-026 | Runbook freshness and support metadata freshness must be visible. | Stale runbooks and outdated owners create false readiness. | Case links runbook/support metadata version, freshness, owner, last review class, stale behavior and next repair action. |
| CR-SUPCASE-027 | Missing support/SLA/credit evidence must become warning or blocker, never inferred readiness. | Absence of evidence is especially dangerous in paid provider flows. | Readiness report marks missing owner, SLA policy, maintenance policy, credit policy, diagnostics, receipt/status, communication cadence or party-view rule as warning/blocked. |
| CR-SUPCASE-028 | Post-incident learning must produce requirement, runbook, fixture, conformance or no-change rationale. | Repeated support toil should make CloudRING stronger. | Closed case records learning outcome, linked requirement/ADR/runbook/scenario/conformance update or owner-approved no-change reason. |
| CR-SUPCASE-029 | Support self-service must let users see case state, impact, next update and allowed actions. | Support should not require hidden operator knowledge. | User-visible case view shows status, impact, owner class, next update, required customer input, workaround, credit-review state and export/appeal path. |
| CR-SUPCASE-030 | Jurisdiction, contract and provider-specific overlays must be represented as policy inputs, not hard-coded behavior. | CloudRING must support different jurisdictions and providers without forking support logic. | Case records applicable policy overlay, data disclosure boundary, local exception, review owner and non-legal-contract statement. |
| CR-SUPCASE-031 | Source-derived support lessons must remain product abstractions. | Reimplementation should preserve experience without cloning old source, docs or operational context. | Requirements and evidence omit raw paths, endpoints, hostnames, IPs, credentials, contacts, commands, package names, source snippets, generated docs text and private identifiers. |
| CR-SUPCASE-032 | Support case/SLA/credit evidence must have reusable template, example, scenario and conformance gate. | Future agents need a repeatable shape, not prose-only support memory. | Linked artifacts include template, synthetic example, Stage 4 scenario, `CR-CONF-048`, `CR-CAPEVID-038`, `CR-SPECTPL-042`, `CR-SPECEX-030` and `WS-040`. |

## Evidence Shape

Minimum Support Case SLA Credit evidence:

```yaml
support_case_sla_credit_evidence:
  evidence_id: support-case-sla-credit-evidence-id
  profile_refs:
    - stage4-public-provider-ready
  scenario_refs:
    - SCENARIO-STAGE4-008
  requirement_refs:
    - CR-SUPCASE-001..032
  case_identity:
    case_id: support-case-id
    case_type: incident | request | dispute | credit-review | maintenance-impact | unknown
    object_binding_status: passed | warning | failed | blocked
    stage_scope:
      - STAGE-004
  parties:
    requester_role: tenant | provider | ISV | reseller | support | finance | governance | AI-agent
    support_owner_status: passed | warning | failed | blocked
    escalation_status: passed | warning | failed | blocked
    party_view_status: passed | warning | failed | blocked
  service_promise:
    support_scope_status: passed | warning | failed | blocked
    sla_policy_status: passed | warning | failed | blocked | not-applicable
    maintenance_policy_status: passed | warning | failed | blocked | not-applicable
    runbook_freshness_status: passed | warning | failed | blocked
  lifecycle:
    state: opened | triaged | waiting-customer | waiting-provider | waiting-ISV | in-remediation | workaround | resolved | credit-review | disputed | closed | learning | blocked
    severity_status: passed | warning | failed | blocked
    communication_status: passed | warning | failed | blocked
    customer_impact_status: passed | warning | failed | blocked
  evidence_links:
    diagnostics_status: passed | warning | failed | blocked | not-applicable
    billing_receipt_status: passed | warning | failed | blocked | not-applicable
    settlement_link_status: passed | warning | failed | blocked | not-applicable
    source_safety_status: passed | warning | failed | blocked
  sla_clock:
    clock_status: passed | warning | failed | blocked | not-applicable
    breach_decision: breached | not-breached | excluded | unknown | not-applicable
    approver_status: passed | warning | failed | blocked | not-applicable
  credit_review:
    requested: true | false
    policy_status: passed | warning | failed | blocked | not-applicable
    calculation_evidence_status: passed | warning | failed | blocked | not-applicable
    dispute_hold_status: passed | warning | failed | blocked | not-applicable
    decision: approved | denied | partial | pending | not-applicable
  agent_handoff:
    allowed_actions:
      - action-summary
    forbidden_actions:
      - action-summary
    required_approvals:
      - approval-summary
  non_claims:
    - does not prove root cause unless linked diagnostics and incident evidence exists
    - does not prove credit approval unless credit-review decision exists
    - does not prove final settlement unless closure evidence exists
```

## Stop Conditions

Agent must stop and request owner/review if:

- support owner, escalation owner or party responsibility is unknown;
- support case lacks offer/order/instance/plan/entitlement binding for a paid
  tenant-facing case;
- SLA is claimed without policy, measurement window, excluded states, clock
  rules and evidence source;
- credit/refund is promised without policy, calculation evidence, approval and
  settlement correction lineage;
- intake receipt, diagnostic package or maintenance note is treated as final
  invoice, root cause, breach or credit proof;
- disputed amounts can settle without hold/release evidence;
- case text or attachments contain raw source, paths, endpoints, host
  identifiers, network literals, credentials, raw logs, commands, personal
  contacts or tenant-private data;
- AI agent is asked to mutate service, tenant, billing, settlement, credit or
  public status without required approval;
- missing support/SLA/credit evidence is being hidden as "ready".

## Non-Goals

- Не выбирать конкретный ticketing, ITSM, billing, legal, observability,
  notification or incident-management product.
- Не заменять `CR-SUPDIAG-*`, `CR-BILLRUN-*`, `CR-SETTLE-*`,
  `CR-OBSOPS-*` or `CR-MKT-*`; this document binds those evidence families into
  a support case decision flow.
- Не хранить реальные support tickets, customer names, provider names, contacts,
  source paths, raw logs, commands, endpoints, invoice details or operational
  dumps.
- Не утверждать production root cause, legal SLA interpretation, actual credit
  amount, tax/accounting correctness, final financial settlement, vulnerability
  absence, full line-by-line source review or full all-refs history coverage.
