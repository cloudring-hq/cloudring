# Document Residual Context

This run derives safe handling requirements from document backlog records where structural probing failed or detected encryption. It preserves damaged-container, parser-failure, encrypted-access, and sensitive routing context while keeping document text and metadata values out of stored context.

Agent usage:

- Use `document-residual-cases.jsonl` for damaged document, encrypted document, and parser-fallback situations.
- Use `document-residual-signals.jsonl` for stable ids, residual statuses, handling routes, and risk buckets.
- Use `document-residual-controls.jsonl` as a repair/access/parser planning checklist.
- Never treat this layer as document text, internal member names, metadata values, or decrypted content.
