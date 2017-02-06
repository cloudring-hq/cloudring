# Text Residual Follow-Up Context

This run derives safe follow-up handling from text residual byte-shape metadata. It separates mixed printable candidates, unknown binary signatures, and misrouted structured artifacts without reading source files or decoding payloads.

Agent usage:

- Use `text-residual-followup-cases.jsonl` for special decoder and routing product situations.
- Use `text-residual-followup-signals.jsonl` for stable ids, follow-up statuses, decoder routes, and risk buckets.
- Use `text-residual-followup-controls.jsonl` as a safety checklist before any residual decoder work.
- Never treat this layer as decoded text or reconstruct payload from byte-shape buckets.
