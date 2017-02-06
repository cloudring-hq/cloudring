# Credential Lifecycle Context

This run derives secret-lifecycle requirements from marker-only credential artifact records. It preserves the operational lesson that cloud platforms need first-class handling for private keys, encrypted keys, certificates, certificate requests, and entitlement-like artifacts, while excluding all payload material and identity-bearing values.

Agent usage:

- Use `credential-lifecycle-cases.jsonl` for secret lifecycle product situations.
- Use `credential-lifecycle-signals.jsonl` for stable ids, material classes, risk buckets, and required controls.
- Use `credential-lifecycle-controls.jsonl` as a product requirement checklist.
- Never use this layer as proof of a key value, certificate subject, issuer, domain, account, or license text.
