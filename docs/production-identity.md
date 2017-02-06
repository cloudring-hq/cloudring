# Production Identity Blueprint

The lab provider portal currently proves the self-service authorization model
with `PORTAL_WRITE_AUTH_MODE=oidc-jwks`, short-lived RS256 bearer JWTs, and a
deterministic self-hosted lab JWKS stored in `platform-system/provider-portal-auth`.
That is good for a reproducible Hyper-V demo, but production identity must use
an external OIDC issuer with remote JWKS-backed signature validation and
explicit claim mapping.

## Target Contract

- The identity provider exposes standard OIDC discovery metadata for issuer,
  authorization, token, and JWKS endpoints.
- The portal API accepts bearer JWTs whose issuer, audience, expiry, signature,
  subject, groups, and tenant namespace claims validate against the configured
  contract.
- `groups` or the configured group claim maps platform operators to
  `platform:admins` and tenant operators to each `Project.spec.adminsGroup`.
- `platform_namespaces` or the configured namespace-scope claim limits tenant
  self-service writes to the namespaces granted by identity policy.
- The production overlay removes `PORTAL_WRITE_TOKENS_JSON` and
  `PORTAL_JWT_HS256_SECRET` from the portal runtime and allows only asymmetric
  signing algorithms such as `RS256` or `ES256`.

## Repository Artifacts

- `iac/kubernetes/production-identity/oidc-contract.yaml` defines the template
  ConfigMap and Secret placeholders for an external issuer.
- `iac/kubernetes/production-identity/provider-portal-oidc-patch.yaml` shows
  the portal Deployment env cutover and deletes lab-only auth env entries.
- `gitops/platform-production-identity` layers the identity contract over the
  shared platform overlay with external issuer placeholders.
- `iac/scripts/verify-production-identity-blueprint.ps1` checks that the
  blueprint stays opt-in, placeholder-backed, and aligned with the documented
  cutover contract.

## Cutover Plan

1. Keep the Hyper-V lab on the reproducible self-hosted JWKS issuer until an
   external identity provider is selected and reachable from the provider cell.
2. Refactor provider-portal authentication out of the monolithic `app.py` into
   a small module with focused tests for issuer/audience/expiry/claim failures.
3. Exercise remote JWKS discovery/cache/rotation validation against the
   selected identity provider, including key rollover and fail-closed behavior.
4. Add a browser login edge, for example with an OIDC-capable gateway or
   oauth2-proxy, while preserving bearer-token API access for automation.
5. Promote through `gitops/platform-production-identity` only after replacing
   every `REPLACE_WITH_*` placeholder and storing client secrets outside Git.

This is a blueprint and operating contract, not a claim that the current lab
self-hosted issuer is a production identity provider or that final external
OIDC evidence has already been accepted.
