# Document Repair Followup Context

This run derives repair, reingest, parser fallback, encrypted access, and support lifecycle controls from document residual metadata. It keeps document text, metadata values, internal member names, source names, and paths out of stored context.

Agent usage:

- Use `document-repair-followup-cases.jsonl` for damaged-container, fallback-parser, encrypted-access, and support workflow situations.
- Use `document-repair-followup-signals.jsonl` for stable ids, lifecycle routes, readiness, and risk buckets.
- Use `document-repair-followup-controls.jsonl` as a repair/access lifecycle checklist.
- Never treat this layer as document text, metadata values, internal member names, decrypted content, or training payload.
