# Archive Residual Context

This run refines archive backlog targets that still needed parser or repair handling. It records partial repair inventory where the local archive lister could recover member composition, and preserves explicit parser-capability gaps where it could not. It does not store source paths, archive names, member names, payload text, domains, provider names, people, brands, or secrets.

Agent usage:

- Use `archive-residual-cases.jsonl` for parser-capability and damaged-container situations.
- Use `archive-residual-signals.jsonl` for residual status, stable ids, and composition counts.
- Use `archive-residual-members.jsonl` only for anonymized extension/kind/depth buckets.
- Treat partial repair listings as useful composition evidence, not complete payload recovery.
