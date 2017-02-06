# Document Content Followup Context

This run derives safe content-handling routes from document backlog structural records. It separates structure-ready documents from records that require repair, parser fallback, or access workflow before content handling. It keeps document text, metadata values, internal member names, and source names out of stored context.

Agent usage:

- Use `document-content-followup-cases.jsonl` for redacted summarization, repair-first, legacy parser, and access-gate situations.
- Use `document-content-followup-signals.jsonl` for stable ids, content readiness, routes, and risk buckets.
- Use `document-content-followup-controls.jsonl` as a content-handling checklist before summarization or training use.
- Never treat this layer as document text, internal member names, metadata values, decrypted content, or a training payload.
