            # Cloud Experience Context

            Source coverage: 3773 anonymized messages were assigned
            into 2327 durable cases. Directory, document, archive, media, binary,
            and backlog artifact layers are tracked in `coverage-backlog.md` and
            per-run context files. The imports keep every parsed message and
            artifact signal reachable through stable ids so later agents can append
            refinements without replacing earlier context.

            ## Agent Principles

            - Treat every customer request as a linked state machine: intent, resource state,
              commercial state, support state, and evidence trail.
            - Prefer self-service workflows with clear validation, idempotency, rollback,
              and audit output.
            - Make provider operations explainable to customers without exposing internal
              implementation names or vendor-specific dependencies.
            - Preserve long-tail support signals. Billing, documents, access recovery,
              migration, and incident communication are part of the cloud product, not
              side processes.
            - Keep context vendor-neutral. If a source mentions a named company, product,
              provider, person, address, domain, or ticket, use only the anonymized role
              and the reusable operational lesson.

            ## Recurrent Domains

            | domain | count |
| --- | ---: |
| `identity_security` | 2394 |
| `networking_connectivity` | 2318 |
| `billing_commercial` | 2005 |
| `support_incident` | 1981 |
| `product_market` | 1664 |
| `compute_virtualization` | 1664 |
| `storage_backup` | 1433 |
| `compliance_legal` | 937 |
| `migration_onboarding` | 814 |
| `developer_api` | 753 |
| `platform_operations` | 667 |
| `general_business_context` | 463 |
| `containers_clusters` | 193 |

            ## Recurrent Problem Signals

            | signal | count |
| --- | ---: |
| `billing_friction` | 1959 |
| `support_handoff` | 1593 |
| `contractual_process` | 1334 |
| `context_signal` | 993 |
| `quota_capacity` | 819 |
| `unclear_requirements` | 806 |
| `data_loss_recovery` | 621 |
| `availability` | 504 |
| `latency_performance` | 357 |
| `integration_friction` | 320 |
| `access_blocked` | 252 |

            ## Product Implications

            - Capacity must be explainable before provisioning, not only after failures.
            - Storage and backup need customer-visible recovery objectives, evidence, and
              tests.
            - Network, naming, certificate, and reachability diagnostics should be
              available without a support escalation.
            - Access management needs recoverable ownership, least privilege, and audit
              trails.
            - Billing and contract workflows should be connected to usage and service
              lifecycle so commercial friction does not become technical support load.
            - Incidents need timeline, ownership, impact, next action, and post-incident
              learning in the same durable record.
            - Migration and onboarding should be run as guided workflows with prerequisites,
              validation, fallback, and handoff to operations.

            ## Largest Derived Cases

- `case-2fa0be0fbfd7` (17 messages, 36 attachments): A recurring source thread captured commercial reconciliation, billing, or contract workflow; the dominant signal is billing friction.
- `case-af5b9284a270` (15 messages, 102 attachments): A recurring source thread captured network reachability, naming, or secure connectivity; the dominant signal is availability.
- `case-684f7e51c988` (14 messages, 26 attachments): A recurring source thread captured network reachability, naming, or secure connectivity; the dominant signal is contractual process.
- `case-003176a092a4` (14 messages, 96 attachments): A recurring source thread captured commercial reconciliation, billing, or contract workflow; the dominant signal is data loss recovery.
- `case-3fa7ea9c48e1` (13 messages, 33 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is billing friction.
- `case-885e49d2658b` (13 messages, 45 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is quota capacity.
- `case-59ab9efe9f70` (12 messages, 32 attachments): A recurring source thread captured network reachability, naming, or secure connectivity; the dominant signal is billing friction.
- `case-2fbabacba52c` (12 messages, 24 attachments): A recurring source thread captured persistent data protection or storage lifecycle; the dominant signal is quota capacity.
- `case-d47ffd472d09` (12 messages, 24 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is availability.
- `case-e3bf5ba8d95e` (12 messages, 43 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is data loss recovery.
- `case-f53524ece7ae` (11 messages, 36 attachments): A recurring source thread captured persistent data protection or storage lifecycle; the dominant signal is billing friction.
- `case-6d86defa097a` (11 messages, 24 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is data loss recovery.
- `case-2cc6d5fb72da` (11 messages, 24 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is data loss recovery.
- `case-f4fb75a5737d` (11 messages, 29 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is quota capacity.
- `case-d8c4365520c3` (11 messages, 31 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is billing friction.
- `case-c89f547f73aa` (10 messages, 40 attachments): A recurring source thread captured network reachability, naming, or secure connectivity; the dominant signal is unclear requirements.
- `case-ddb76d88975d` (9 messages, 20 attachments): A recurring source thread captured persistent data protection or storage lifecycle; the dominant signal is contractual process.
- `case-4d82a8f311f4` (9 messages, 21 attachments): A recurring source thread captured network reachability, naming, or secure connectivity; the dominant signal is latency performance.
- `case-01f0c3882bf1` (9 messages, 100 attachments): A recurring source thread captured persistent data protection or storage lifecycle; the dominant signal is access blocked.
- `case-7e35f383bb40` (9 messages, 41 attachments): A recurring source thread captured tenant capacity request or virtual compute lifecycle; the dominant signal is latency performance.
