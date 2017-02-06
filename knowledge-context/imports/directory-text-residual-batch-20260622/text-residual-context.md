# Directory Text Residual Context

This run refines text backlog artifacts whose samples were not text-like. It records signatures, byte-shape buckets, stable ids, and residual statuses only. It does not copy raw text, paths, file names, URLs, domains, people, provider names, brand names, vendor names, or secrets.

## Agent Use

- Use `text-residual-cases.jsonl` for non-text residual evidence from prior text candidates.
- Use `text-residual-signals.jsonl` only for stable ids, magic families, byte-shape buckets, and routing statuses.
- Treat null-heavy, mixed-printable, and misrouted artifacts as retained evidence, not missing text.
- Never infer raw source names or content from residual byte-shape buckets.
