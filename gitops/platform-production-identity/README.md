# Platform Production Identity Overlay

This overlay shows how a production platform promotion layers external
OIDC/JWKS identity onto the provider portal.

Do not apply this overlay as-is. Replace the placeholder issuer, JWKS, and
client values in `iac/kubernetes/production-identity/oidc-contract.yaml`, wire
the Secret through a production secret manager, and complete the provider-portal
JWKS runtime cutover before promotion.

The current lab keeps `gitops/platform` on the HS256 test issuer so the small
Hyper-V sandbox stays reproducible.
