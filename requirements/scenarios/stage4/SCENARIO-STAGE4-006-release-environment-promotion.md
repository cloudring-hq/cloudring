# SCENARIO-STAGE4-006 - Release Environment Promotion Evidence

---
id: SCENARIO-STAGE4-006
stage: 4
title: Provider Release Promotion With Rollback Evidence
roles:
  - provider
  - release-owner
  - support
  - security
  - AI-agent
capabilities:
  - release-environment-promotion
  - public-provider-kit
  - marketplace-productization
  - security-secret-and-supply-chain
---

## Intent

Provider wants to promote a new service artifact to provider production scope.
CloudRING must prove artifact identity, environment bundle completeness,
runner/check evidence, source safety, approval and rollback before the release
can affect tenants.

## Preconditions

- Candidate module has owner, support owner and release owner.
- Artifact has immutable identity and source-safe provenance record.
- Environment bundle exists for target provider scope.
- Required checks are classified by confidence and freshness.
- Previous released artifact or irreversible warning is visible.

## Happy Path

1. Release owner submits promotion plan with artifact, environment bundle,
   policy scope and rollback target.
2. CloudRING validates module ownership, dependency lock, toolchain evidence,
   check matrix and runner semantics.
3. Secret/topology scan confirms evidence is redacted and safe for agent review.
4. Provider approver reviews policy, parity limits, support impact and rollback.
5. Promotion is activated through an auditable pointer or target state change.
6. Post-promotion health/support checks are recorded.
7. Release ledger stores source-safe evidence and explicit non-claims.

## Negative Cases

| Case | Expected Behavior |
|---|---|
| Build succeeded but artifact identity is mutable or unknown. | Promotion is blocked until immutable artifact evidence exists. |
| Tag exists but no environment bundle or approval exists. | Tag is treated as version signal only, not release readiness. |
| Staging-like evidence is claimed as production parity without differences. | Manual review is required and promotion cannot auto-pass. |
| Encrypted payloads or topology values appear in evidence. | Evidence is blocked for redaction/classification repair. |
| Rollback target is missing for tenant-impacting promotion. | Promotion is blocked or requires explicit irreversible warning and approval. |
| External runner behavior is hidden. | Evidence is warning or blocked depending on risk scope. |

## Evidence

- `CR-RELPROM-001..032`
- `CR-CONF-045`
- `CR-CAPEVID-035`
- `WS-037`
- Release environment promotion evidence bundle.
- Source-safe promotion ledger record.

## Stop Conditions

Agent must stop if:

- local build/test/tag evidence is used as provider promotion proof;
- approval, artifact identity, environment bundle or rollback is unknown;
- raw source/private/secret/topology data would enter the evidence bundle;
- release changes tenant-visible state without support and post-promotion checks.

## Non-Claims

- This scenario does not choose a specific CI/CD, registry, signing or deployment
  technology.
- This scenario does not prove vulnerability scanning, license clearance or live
  deployment unless linked evidence explicitly covers them.
