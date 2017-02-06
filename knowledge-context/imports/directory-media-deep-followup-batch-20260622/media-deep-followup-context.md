# Media Deep Followup Context

This run derives safe deep-processing routes from media/design backlog records. It separates audio transcription, video visual review, design-source parsing, font review, visual OCR, package parsing, external-reference handling, and generic parser triage while keeping OCR text, transcripts, visual text, EXIF text, source names, paths, URLs, and domains out of stored context.

Agent usage:

- Use `media-deep-followup-cases.jsonl` for OCR, transcription, design-parser, font-review, package-parser, and generic media triage situations.
- Use `media-deep-followup-signals.jsonl` for stable ids, deep-processing routes, status buckets, and risk buckets.
- Use `media-deep-followup-controls.jsonl` as a redaction and parser checklist before summarization or training use.
- Never treat this layer as OCR text, transcript text, visual text, design-layer text, EXIF text, source names, URLs, or training payload.
