# Text Decoder Followup Context

This run derives decoder, signature-identification, and structured-routing lifecycle controls from text residual follow-up metadata. It keeps raw text, payload bytes, source names, and paths out of stored context.

Agent usage:

- Use `text-decoder-followup-cases.jsonl` for mixed binary/text decoder, unknown signature, image-routing, and property-list-routing situations.
- Use `text-decoder-followup-signals.jsonl` for stable ids, lifecycle routes, byte-shape buckets, and risk buckets.
- Use `text-decoder-followup-controls.jsonl` as a decoder and routing lifecycle checklist.
- Never treat this layer as decoded text, payload bytes, source names, paths, or training payload.
