# Archive Residual Followup Context

This run derives parser-capability, repair-completion, and nested-boundary controls from archive residual metadata. It keeps archive payload text, member names, source names, and paths out of stored context while preserving support and migration signals.

Agent usage:

- Use `archive-residual-followup-cases.jsonl` for unsupported parser, damaged-container, and nested-boundary situations.
- Use `archive-residual-followup-signals.jsonl` for stable ids, follow-up routes, status buckets, and composition counts.
- Use `archive-residual-followup-controls.jsonl` as a parser and repair checklist.
- Never treat this layer as archive payload text, raw member names, complete recovery, or training payload.
