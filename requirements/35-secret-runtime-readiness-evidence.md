# Secret Runtime Readiness Evidence

Этот документ фиксирует продуктовые требования к runtime readiness для
encrypted secrets и credential boundary в CloudRING. Он отвечает на вопрос:
когда можно честно сказать, что секретная подсистема готова к stage-ready
эксплуатации, а не просто хранит значение в зашифрованном виде.

`CR-SECRETRUN-*` не заменяет `CR-SEC-*` и `CR-SECSUPPLY-*`. Эти семейства
задают границу доверия, brokered access, redaction, artifact trust and source
safety. `CR-SECRETRUN-*` добавляет reusable evidence package: scope binding,
key custody, public-certificate distribution, status/conditions, reconciliation,
install/delete behavior, rotation/rebinding, degraded mode, source-safe
configuration and non-claims.

## Requirements

| ID | Требование | Почему | Acceptance |
|---|---|---|---|
| CR-SECRETRUN-001 | Secret runtime evidence must describe reference custody, never raw secret value custody. | Durable product memory should prove who may bind to a secret, not store the payload. | Evidence contains references, owners, scopes, allowed capabilities and outcomes without secret values. |
| CR-SECRETRUN-002 | Encrypted secret objects must bind ciphertext to an explicit scope. | Encrypted data can still be replayed or reused incorrectly if scope is ambient. | Evidence distinguishes strict, namespace-wide, cluster-wide or equivalent scope and shows the replay boundary. |
| CR-SECRETRUN-003 | Scope weakening must be explicit, approved and visible. | Broad secret usability can be necessary, but it increases blast radius. | Broader-than-strict scope records owner, reason, risk, expiry/review trigger and compensating controls. |
| CR-SECRETRUN-004 | Encrypted credential data must be classified separately from ordinary configuration. | Agents and docs must not treat encrypted material as harmless config. | Config/evidence classifies encrypted secret data, public metadata, generated fields, local-only fields and sensitive-private fields. |
| CR-SECRETRUN-005 | Per-key encrypted data must preserve field identity without exposing values. | Operators need to know which secret keys exist and are synced without seeing payloads. | Evidence lists key names/classes, validation status and missing/extra key findings without plaintext. |
| CR-SECRETRUN-006 | Template metadata for generated secret objects must be source-safe and bounded. | Labels, annotations and owner references can leak private context or create hidden authority. | Evidence states which metadata is preserved, stripped or generated, and blocks unsafe owner/reference propagation. |
| CR-SECRETRUN-007 | Decryption must happen only inside the trusted target boundary. | GitOps-friendly encrypted secrets are useful only if the private key never leaves the runtime trust domain. | Evidence names trust boundary, private-key owner, runtime actor and forbidden export surfaces. |
| CR-SECRETRUN-008 | Public key or certificate distribution must be separate from private key custody. | Users need a safe way to seal data without access to decrypt it. | Evidence shows public verification/fingerprint/freshness and confirms private key is not exposed through docs, API, logs or agent context. |
| CR-SECRETRUN-009 | Key identity and fingerprint must be visible for support without revealing key material. | Rotation and incident review need to know which key was used. | Evidence records safe key identity, fingerprint or equivalent, validity window, owner and current/deprecated state. |
| CR-SECRETRUN-010 | Key generation, rotation, renewal and rebinding must be lifecycle operations. | Secret readiness decays when keys age, rotate or are replaced. | Rotation/rebinding evidence shows impacted objects, compatibility, validation, rollback/compensation and stale-object treatment. |
| CR-SECRETRUN-011 | Runtime must support multiple valid keys only with explicit migration semantics. | Multi-key decrypt can hide stale ciphertext and unclear ownership. | Evidence states active, deprecated and retired keys plus migration window and stop condition. |
| CR-SECRETRUN-012 | Secret runtime status must be generation-aware. | A declared encrypted object is not ready until the runtime has reconciled the current generation. | Evidence includes observed generation, current condition, last transition and stale/unknown behavior. |
| CR-SECRETRUN-013 | Sync conditions must separate success, failure and unknown. | Absence of error is not proof of secret creation. | Status vocabulary includes synced, failed, unknown/stale and human/agent-readable reason. |
| CR-SECRETRUN-014 | Error evidence must be redacted but actionable. | Support needs remediation without seeing secret values. | Failure reports include safe reason category, affected scope, next action, owner and redaction status. |
| CR-SECRETRUN-015 | Runtime install must state CRD/API contract and schema strictness. | A loose schema can accept unsafe or future-incompatible secret declarations. | Install evidence states resource version, served/storage status, validation strictness, unknown-field policy and compatibility risk. |
| CR-SECRETRUN-016 | Multi-document or bundle installation must preserve document boundaries and ordering assumptions. | Secret runtimes are often installed as bundles where partial apply creates unsafe drift. | Bundle evidence lists artifact count/class, ordering requirement, unsupported multi-doc behavior and partial-install stop condition. |
| CR-SECRETRUN-017 | Runtime deployment must have explicit service account and least-privilege access evidence. | The controller that decrypts secrets is a high-trust actor. | Evidence links service account, role scope, allowed resources/actions and broad-permission rationale. |
| CR-SECRETRUN-018 | Key-admin rights must be separated from ordinary runtime operation where possible. | Key material authority is more sensitive than reconciliation. | Evidence distinguishes key custody, secret object mutation, status update, service/proxy and monitoring permissions. |
| CR-SECRETRUN-019 | Runtime must expose health/readiness without exposing secret material. | Operators need liveness while preserving confidentiality. | Health evidence confirms endpoint/status availability and redaction/no-payload behavior. |
| CR-SECRETRUN-020 | Metrics and dashboards must be secret-safe. | Observability can leak names, scopes, namespaces or failure details. | Metrics evidence covers reconciliation counts, failures, key age/freshness and redaction/cardinality controls. |
| CR-SECRETRUN-021 | Install and uninstall must state CRD/resource retention behavior. | Removing a secret runtime can orphan or destroy critical credential state. | Evidence states keep/delete behavior, owner decision, backup/export expectation and irreversible warnings. |
| CR-SECRETRUN-022 | Existing secret adoption must be explicit and audited. | Taking over an existing secret can change ownership and lifecycle unexpectedly. | Adoption evidence records owner, reason, previous state, managed/unmanaged status and rollback path. |
| CR-SECRETRUN-023 | Deletion must distinguish encrypted declaration removal from decrypted secret removal. | Users need to know whether deleting source memory deletes runtime credential material. | Evidence states derived object cleanup, retention, residual data and manual review rules. |
| CR-SECRETRUN-024 | Runtime must support fail-closed behavior for missing key, stale key or invalid scope. | Secret systems should block unsafe use rather than silently create wrong credentials. | Evidence shows blocked states for missing key, invalid ciphertext, scope mismatch, stale public key and unsupported format. |
| CR-SECRETRUN-025 | Degraded mode must be visible and scoped. | A presence may continue operating while secret rotation or sync is impaired. | Degraded evidence states affected objects, blocked actions, allowed read-only operations, user impact and review trigger. |
| CR-SECRETRUN-026 | Secret runtime evidence must be stage-aware. | Stage 1 local safety, Stage 2 private autonomy and provider/federation readiness require different proof. | Evidence maps required-now, future-stage gap, non-goal and not-applicable states per profile. |
| CR-SECRETRUN-027 | Agent access to secret runtime must be brokered and non-extractive. | Agents should operate references and evidence, not secret payloads. | Agent handoff forbids raw value retrieval and lists allowed read-only, validation, rotation-plan and approval-gated actions. |
| CR-SECRETRUN-028 | Secret runtime examples and docs must use synthetic data only. | Examples are copied and must not seed leaks. | Example, docs and conformance artifacts pass private marker, strict secret and source-copy scans. |
| CR-SECRETRUN-029 | Runtime readiness cannot be claimed from encryption alone. | Encrypted-at-rest does not prove controller health, key custody, scope, rotation or observability. | Readiness report requires runtime evidence bundle, not only encrypted object existence. |
| CR-SECRETRUN-030 | Source-derived secret evidence must classify encrypted material as sensitive even when no plaintext appears. | Encrypted blobs, grants and key names can still reveal operational context. | Source pass records encrypted-material class, redaction, exclusion and non-claim decisions. |
| CR-SECRETRUN-031 | Release/artifact evidence is required before provider or marketplace claims. | Secret controllers and charts are supply-chain trust boundaries. | Evidence links version, artifact identity, provenance, validation result, known exceptions, freshness and rollback/deprecation note. |
| CR-SECRETRUN-032 | Secret runtime evidence must explicitly state non-claims. | Overclaiming secret readiness creates false trust. | Evidence states it does not prove absence of all vulnerabilities, live runtime execution, provider-grade readiness, secret value correctness or full source-history audit unless separately proven. |

## Evidence Contract

Secret runtime readiness evidence is complete only when it shows:

1. secret reference, scope, owner and allowed capability;
2. encrypted-data classification and field/key inventory without values;
3. public-key/certificate freshness and private-key custody boundary;
4. generation-aware reconciliation and condition state;
5. install/update/delete/retention behavior;
6. RBAC/service-account/key-admin evidence;
7. health, metrics and redaction controls;
8. rotation/rebinding/revocation and degraded behavior;
9. source-safety and non-claims.

## Source-Safety Rules

- Never store secret values, encrypted blobs, private key material, tenant data,
  raw source paths, exact operational commands, raw chart values with private
  context or source snippets in requirements.
- Treat encrypted material, key names, grants, topology and operational events
  as sensitive unless owner review classifies them otherwise.
- Use synthetic examples and role names only.
- Mark runtime execution, key compromise resistance and vulnerability absence
  as non-claims unless separately verified.
