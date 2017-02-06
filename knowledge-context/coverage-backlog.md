# Coverage Backlog

This file records what has been safely covered and what still needs specialized
processing. Unsupported status means the artifact is counted, anonymized, and
traceable by stable id; it does not mean the life experience was intentionally
dropped.

## Covered Layers

| layer | run | coverage |
| --- | --- | ---: |
| legacy mail | `mail-archive-20260621` | 3773 parsed messages, 2327 cases, 8410 referenced attachments |
| directory snapshot | `directory-snapshot-20260621` | 21680 files, 154 cases, 109 unsafe extension buckets sanitized |
| text code | `directory-text-batch-20260622` | 10761 text signals, 106 cases, 10021 extracted |
| text backlog | `directory-text-backlog-batch-20260622-02` | 892 target signals, 100 cases, 250 sample-classified, 642 retained not-text-like |
| text residual | `directory-text-residual-batch-20260622` | 642 residual signals, 97 cases, 555 binary residuals, 4 misrouted structured artifacts, 36 mixed-printable retained, 47 unknown retained |
| text residual follow-up | `directory-text-residual-followup-batch-20260622` | 87 follow-up signals, 8 cases, 12 control requirements, 36 mixed-printable decoder candidates, 47 unknown signature candidates, 4 misrouted structured artifacts |
| text decoder follow-up | `directory-text-decoder-followup-batch-20260622` | 87 follow-up signals, 8 cases, 17 control requirements, 36 mixed printable decoder routes, 47 unknown signature routes, 4 structured routing routes |
| binary text-like | `directory-binary-textlike-batch-20260622-02` | 152 text-like binary signals, 19 cases, 125 full-file decoded for metadata, 17 chunk decoded, 10 credential-like excluded |
| binary text-like follow-up | `directory-binary-textlike-followup-batch-20260622` | 70 follow-up signals, 17 cases, 10 control requirements, 69 sensitive routes, 17 chunked routes, 10 credential-marker routes, 1 non-sensitive chunked route |
| documents | `directory-document-batch-20260622` | 2375 document signals, 105 cases, 1758 extracted |
| document backlog | `directory-document-backlog-batch-20260622` | 617 target signals, 45 cases, 464 structural coverage added, 152 structural probe failures, 1 encrypted |
| document residual | `directory-document-residual-batch-20260622` | 153 residual signals, 26 cases, 14 control requirements, 150 damaged zip-document containers, 2 PDF parser failures, 1 encrypted document, 5 sensitive routes |
| document content follow-up | `directory-document-content-followup-batch-20260622` | 617 follow-up signals, 83 cases, 23 control requirements, 464 structure-ready content routes, 153 repair/access-before-content routes |
| document repair follow-up | `directory-document-repair-followup-batch-20260622` | 153 follow-up signals, 26 cases, 17 control requirements, 150 damaged repair lifecycle routes, 2 PDF fallback lifecycle routes, 1 encrypted access lifecycle route |
| archives | `directory-archive-batch-20260622` | 172 archive signals, 68268 anonymized member signals, 33 cases |
| archive backlog | `directory-archive-backlog-batch-20260622` | 22 backlog archive signals, 114 recursive member signals, 7 cases, 13 direct archives structurally triaged, 4 nested archives listed |
| archive residual | `directory-archive-residual-batch-20260622` | 18 residual archive signals, 170 repaired member signals, 6 cases, 2 direct zip partial listings, 11 direct parser gaps, 3 nested parser gaps, 2 nested zip repair probes retained |
| archive residual follow-up | `directory-archive-residual-followup-batch-20260622` | 18 follow-up signals, 10 cases, 16 control requirements, 11 direct parser capability routes, 3 nested parser capability routes, 4 repair completion routes |
| database/index | `directory-database-index-batch-20260622` | 92 database/index metadata signals, 9 cases, 52 pack/index headers parsed, 4 container member-count artifacts, 36 generic metadata retained |
| database/index residual | `directory-database-index-residual-batch-20260622` | 36 residual signals, 14 cases, 10 control requirements, 19 sensitive routes, 24 text-like routes |
| credential artifacts | `directory-credential-artifact-batch-20260622` | 12 marker-only credential signals, 4 cases, 10 armor-marker artifacts, 4 private-key marker artifacts, 6 certificate/request marker artifacts |
| credential lifecycle | `directory-credential-lifecycle-batch-20260622` | 12 lifecycle signals, 6 cases, 12 control requirements, 4 private-key lifecycle signals, 7 certificate/request lifecycle signals, 1 entitlement lifecycle signal |
| media/design | `directory-media-batch-20260622-02` | 7618 media/design signals, 86 cases |
| media/design backlog | `directory-media-backlog-batch-20260622` | 1145 media backlog signals, 48 cases, 602 audio/video structural signals, 531 design/font/package structural signals, 209 generic retained |
| media/design deep follow-up | `directory-media-deep-followup-batch-20260622` | 1145 follow-up signals, 82 cases, 29 control requirements, 310 video routes, 260 audio routes, 209 generic parser-triage routes, 192 font review routes |
| binary/database | `directory-binary-batch-20260622` | 756 binary/database signals, 35 cases |

## Remaining Safe-Processing Queues

| queue | count | next safe extractor |
| --- | ---: | --- |
| mixed printable decoder lifecycle after follow-up | 36 | vetted mixed binary/text decoder lifecycle with sandboxing, byte-shape traceability, and no raw text, source names, or payload export |
| unknown signature identification lifecycle after follow-up | 47 | signature identification before parser assumptions, with metadata-only output and no payload bytes export |
| misrouted structured artifact routing lifecycle after follow-up | 4 | route image-like and property-list artifacts to structural pipelines without text ingestion, OCR text, or payload export |
| damaged document repair lifecycle after follow-up | 150 | bounded repair/reingest lifecycle with integrity checks, customer guidance, and no document text, internal member names, metadata values, or payload export |
| PDF parser fallback lifecycle after follow-up | 2 | vetted fallback parser lifecycle without document text, metadata values, or payload export |
| encrypted document access lifecycle after follow-up | 1 | ownership/access workflow and non-decryption metadata handling unless authorization and keys are present |
| document structure-ready redacted summarization after content follow-up | 464 | bounded redacted/chunked summarizer using structure buckets only, with no raw document text, metadata values, internal member names, source names, or training payload export |
| direct archive parser capability vetting after follow-up | 11 | vetted parser capability for unsupported direct archive formats with sandboxing, composition-only output, and no payload or member-name export |
| direct archive repair completion after follow-up | 2 | repair-completion validation for damaged direct containers while retaining partial member composition only |
| nested archive parser capability vetting after follow-up | 3 | vetted nested-container parser capability with explicit trust boundaries and no payload extraction to disk |
| nested archive repair completion after follow-up | 2 | nested repair-completion flow without member-name export, payload extraction, or temporary payload persistence |
| media video redacted review after deep follow-up | 310 | bounded video visual review, frame OCR, and audio-track transcription with no raw visual text, transcript, identity, or training payload export |
| media audio redacted transcription after deep follow-up | 260 | bounded transcription with speaker-identity exclusion and no raw audio text or training payload export |
| media generic parser triage after deep follow-up | 209 | vetted media/design parser triage with sandboxing and no source-name, payload, OCR, or transcript export |
| font asset review after deep follow-up | 192 | font metadata-value exclusion, embedding-rights review, and no name-table value export |
| design source parser redaction after deep follow-up | 145 | sandboxed design-source parser review with layer-text redaction and no embedded asset-name export |
| visual OCR review after deep follow-up | 27 | redacted OCR or visual inspection for raster/vector/print graphics without raw visual text export |
| media package parser after deep follow-up | 1 | sandboxed package parser with no package member-name or payload export |
| external reference metadata-only after deep follow-up | 1 | safe-fetch workflow gate; retain metadata-only context without URL or domain export |

## Guardrails

- Do not copy source names, source paths, member names, OCR text, transcripts,
  database rows, EXIF text, URLs, domains, provider names, people, brand names,
  or secrets into this folder.
- Every future extractor should write controlled tags, stable ids, counts,
  status fields, and platform implications.
- If a parser cannot safely process an artifact, preserve a backlog status with
  the stable id and the reason.
- Privacy/vendor scan must remain zero before a run is considered usable.
