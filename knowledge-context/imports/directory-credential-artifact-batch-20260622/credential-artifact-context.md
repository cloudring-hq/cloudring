# Directory Credential Artifact Context

This run refines credential and certificate-like artifacts from the binary batch. It records marker-only evidence: controlled armor block types, count buckets, sensitive handling tags, stable ids, and status fields. It does not copy raw paths, file names, key material, certificate subject or issuer values, license text, payload text, URLs, domains, people, provider names, brand names, vendor names, or secrets.

## Agent Use

- Use `credential-artifact-cases.jsonl` for secret-lifecycle and certificate/request/license-like situations.
- Use `credential-artifact-signals.jsonl` only for marker counts, stable ids, and handling requirements.
- Treat every signal in this layer as excluded from training payload unless a future redaction policy explicitly allows derived metadata.
- Never infer identities, domains, issuers, subjects, file names, or secret values from marker buckets.

## Largest Credential Artifact Cases

- `credentialcase-820095105147` (9 signals): A credential artifact cluster preserved armor markers counted evidence for general business context; the dominant signal is context signal.
- `credentialcase-427d5dfc14cf` (1 signals): A credential artifact cluster preserved armor markers counted evidence for networking connectivity; the dominant signal is context signal.
- `credentialcase-9eeee0158a6f` (1 signals): A credential artifact cluster preserved binary or text marker retained evidence for compliance legal; the dominant signal is context signal.
- `credentialcase-5992c9039f5c` (1 signals): A credential artifact cluster preserved binary or text marker retained evidence for compliance legal; the dominant signal is context signal.
