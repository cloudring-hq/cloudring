# Production Identity Blueprint

This directory is an opt-in template for replacing the reproducible lab portal
issuer and self-hosted JWKS with a production external OIDC issuer and JWKS
validation contract.

It is intentionally not referenced by `gitops/platform` or by the current
`gitops/cells/lab-hyperv` overlay. Copy or layer it only for a real production
promotion after replacing every `REPLACE_WITH_*` value and after the
provider-portal runtime has accepted live token/JWKS evidence for the target
identity provider.

## Contract

- OIDC issuer discovery is the source of truth for issuer metadata.
- `issuer` and `jwksUri` must match the selected identity provider.
- `audience` must be the portal API audience, defaulting to `platform-portal`.
- `groupsClaim` maps to tenant and platform-admin groups.
- `namespacesClaim` maps to tenant namespace scope for self-service writes.
- `adminGroup` maps to the provider-admin group.
- HS256 and static token fallback must remain absent from production runtime
  env.

The current lab portal validates signed JWTs with `oidc-jwks` mode and a
reproducible self-hosted lab JWKS. This blueprint defines the production
manifest contract and cutover shape for a real external issuer, remote JWKS,
and non-lab evidence.
