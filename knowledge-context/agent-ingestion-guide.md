# Agent Ingestion Guide

This context is designed for retrieval and future model training datasets.
Do not reconstruct source identities. Do not add raw quoted mail text. Append
new source runs under `imports/`.

## Retrieval Order

1. Read `cloud-experience-context.md` for reusable platform lessons.
2. Read `coverage-backlog.md` to understand which layers are covered and which
   queues require specialized safe extractors.
3. Retrieve per-run `*-cases.jsonl` files by `domain_tags` and `problem_tags`.
4. Use per-run signal files only for stable-id traceability, counts, statuses,
   and controlled tags.
5. Use mail `messages.jsonl` only for anonymized evidence metadata and source
   integrity hashes.
6. Use mail `attachments.jsonl` to understand whether a thread included
   documents, diagrams, spreadsheets, meetings, or binary evidence.
7. Use archive and archive-backlog member files only for anonymized composition,
   stable ids, status fields, and counts.
8. Use archive-residual files only for repair/parser status, partial member
   composition buckets, and stable ids; never treat partial listings as
   complete payload recovery.
9. Use archive-residual-followup files for parser capability, repair completion,
   nested-boundary, and support-diagnostic controls; never use them as archive
   payload text, raw member names, complete recovery, or training payload.
10. Use database/index files only for metadata buckets, schema type counts,
   object-count buckets, stable ids, and statuses.
11. Use database-index-residual files for metadata-only parser planning,
    migration residue, cache policy, and secret-aware decoder gates; never use
    them as decoded rows, schema text, or customer payload.
12. Use credential artifact files only for marker-only secret-lifecycle metadata;
    never use them as training payload.
13. Use credential-lifecycle files for secret storage, rotation, renewal,
    revocation, access-audit, and entitlement-review product requirements;
    never infer key values, subjects, issuers, identities, domains, or license
    text.
14. Use media-backlog files only for structural buckets, stable ids, and
    deferred-processing status; never treat them as OCR or transcript output.
15. Use media-deep-followup files for redacted OCR, transcription, design
    parser, font-review, package-parser, external-reference, and generic media
    triage controls; never use them as OCR text, transcript text, visual text,
    design-layer text, EXIF text, source names, URLs, or training payload.
16. Use binary-textlike files only for decoded metadata, redaction/count
    buckets, and statuses; never treat them as a raw text corpus.
17. Use binary-textlike-followup files for secret-aware review, chunked
    ingestion policy, credential-marker routing, and training-payload gates;
    never use them as decoded text.
18. Use document-content-followup files for redacted summarization readiness,
    repair-first routing, legacy parser gates, and content-handling controls;
    never use them as document text, metadata values, internal member names,
    decrypted content, or training payload.
19. Use document-repair-followup files for damaged-container repair, reingest,
    fallback-parser, encrypted-access, support-communication, and lifecycle
    controls; never use them as document text, metadata values, internal member
    names, decrypted content, or training payload.
20. Use document-residual files for damaged-container repair, encrypted-access,
    and parser-fallback requirements; never use them as document text,
    metadata values, internal member names, or decrypted content.
21. Use text-residual files only for magic-family, byte-shape buckets, routing
    statuses, and stable ids; never treat them as decoded text.
22. Use text-residual-followup files for special decoder gates, signature
    identification, and structured-artifact routing; never use them as decoded
    text or payload evidence.
23. Use text-decoder-followup files for decoder lifecycle, unknown-signature
    identification, and structured-artifact routing controls; never use them as
    decoded text, payload bytes, source names, paths, or training payload.

## Record Guarantees

- Every parsed message has a stable `message_id`.
- Every parsed message belongs to exactly one `case_id`.
- Raw addresses, domains, names, provider names, product names, and source
  paths are not stored.
- Unsupported or binary attachments are still counted and linked by anonymized
  attachment ids.
- Unsupported directory artifacts are recorded in `coverage-backlog.md` and in
  their layer-specific signal files; do not treat them as missing or safe to
  quote.
- Document residual records convert structural failures and encrypted-document
  evidence into repair/access/parser controls; they still do not authorize
  document text, internal member-name, metadata-value, or decrypted-content use.
- Document content follow-up records convert document backlog evidence into
  readiness, route, and control requirements; they still do not authorize raw
  document text, metadata-value, internal member-name, decrypted-content, or
  training-payload use.
- Document repair follow-up records convert damaged-container, fallback-parser,
  and encrypted-access residuals into lifecycle controls; they still do not
  authorize repair payload export, decrypted content, raw document text,
  metadata-value, internal member-name, or training-payload use.
- Nested and unsupported archive containers are retained as explicit queues
  until a safe parser or repair flow can add member-only structure.
- Archive residual repair preserves partial member composition where available;
  parser gaps and failed nested repair probes remain explicit queues, not
  missing context.
- Archive residual follow-up records convert parser gaps, partial repair
  listings, and nested repair probes into capability, repair-completion, and
  boundary controls; they still do not authorize payload extraction, raw member
  names, or training-payload use.
- Database/index artifacts never expose row values, table names, column names,
  file names, or source paths; treat generic and sensitive statuses as backlog.
- Database/index residual records convert generic and sensitive metadata queues
  into safe decoder and migration-planning controls; they still do not
  authorize row, schema, or payload extraction.
- Credential artifact markers preserve handling requirements only; they do not
  authorize copying key material, subject values, license text, or payload text.
- Credential lifecycle records convert marker-only evidence into product
  controls; use them as requirements, not as credential payload evidence.
- Media/design backlog structure preserves evidence of recordings, visual
  assets, fonts, and design files; visual text and speech remain unextracted.
- Media/design deep follow-up records convert media backlog evidence into
  OCR, transcription, design-parser, font-review, package-parser, and generic
  parser controls; they still do not authorize raw OCR, transcript, visual
  text, design-layer text, source-name, URL, or training-payload use.
- Binary text-like decoding preserves classification evidence only; raw decoded
  text remains excluded from stored context and model-training payload.
- Binary text-like follow-up records convert sensitive, credential-like, and
  chunked decoded-metadata queues into safety controls; they still do not
  authorize raw decoded text use.
- Text residual triage preserves magic-family and byte-shape evidence only;
  mixed, unknown, and misrouted artifacts remain decoder queues, not text
  corpora.
- Text residual follow-up records convert mixed, unknown, and misrouted
  byte-shape evidence into decoder/routing controls; they still do not
  authorize raw text or payload extraction.
- Text decoder follow-up records convert decoder/routing controls into
  lifecycle requirements; they still do not authorize raw text, payload bytes,
  source-name, path, or training-payload use.
