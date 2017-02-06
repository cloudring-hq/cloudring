# Media Deep Followup Coverage

- Source kind: directory media deep followup batch
- Source media backlog run: `directory-media-backlog-batch-20260622`
- Source backlog signals: 1145
- Followup signals written: 1145
- Followup cases: 82
- Control requirements written: 29
- Audio transcription routes: 260
- Video visual/transcription routes: 310
- Design parser routes: 145
- Font review routes: 192
- Generic parser triage routes: 209
- Sensitive followup routes: 52
- Privacy/vendor scan hits: 0

## Deep Status Counts

| media_deep_status | count |
| --- | ---: |
| `video_transcription_and_visual_review_requirements_modeled` | 310 |
| `audio_transcription_redaction_requirements_modeled` | 260 |
| `generic_media_parser_triage_requirements_modeled` | 209 |
| `font_asset_review_requirements_modeled` | 192 |
| `design_source_parser_redaction_requirements_modeled` | 145 |
| `visual_ocr_review_requirements_modeled` | 27 |
| `media_package_parser_requirements_modeled` | 1 |
| `external_reference_metadata_only_requirements_modeled` | 1 |

## Deep Route Counts

| media_deep_route | count |
| --- | ---: |
| `video_transcription_visual_ocr_route` | 310 |
| `audio_transcription_redaction_route` | 260 |
| `generic_media_parser_triage_route` | 209 |
| `font_asset_embedding_review_route` | 192 |
| `design_source_parser_redaction_route` | 145 |
| `visual_ocr_redaction_route` | 27 |
| `media_package_parser_sandbox_route` | 1 |
| `external_reference_metadata_only_route` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `raw_audio_text_exclusion` | 1145 |
| `raw_exif_text_exclusion` | 1145 |
| `raw_ocr_text_exclusion` | 1145 |
| `raw_transcript_exclusion` | 1145 |
| `raw_visual_text_exclusion` | 1145 |
| `retention_minimization` | 1145 |
| `source_name_path_exclusion` | 1145 |
| `structure_bucket_traceability` | 1145 |
| `support_traceability` | 1145 |
| `training_payload_review_gate` | 1145 |
| `url_domain_exclusion` | 1145 |
| `sample_truncation_confidence_guard` | 661 |
| `design_source_parser_sandbox` | 354 |
| `visual_identity_exclusion` | 337 |
| `audio_track_transcription_gate` | 310 |
| `video_frame_ocr_gate` | 310 |
| `speaker_identity_exclusion` | 260 |
| `transcription_redaction_gate` | 260 |
| `parser_capability_vetting` | 209 |
| `font_embedding_rights_review` | 192 |
| `font_name_table_value_exclusion` | 192 |
| `embedded_asset_name_exclusion` | 146 |
| `design_layer_text_gate` | 145 |
| `sensitive_media_route` | 52 |
| `print_graphic_ocr_gate` | 27 |
| `vector_text_redaction_gate` | 27 |
| `package_member_name_exclusion` | 1 |
| `package_parser_sandbox` | 1 |
| `external_reference_non_fetch_default` | 1 |

## Safety Notes

- This is a derived-only run over media/design structural metadata records.
- It does not run OCR, transcribe audio, fetch references, copy visual text,
  copy speech text, copy EXIF text, copy source names, copy paths, copy URLs,
  or store domains, providers, people, brands, vendors, or secrets.
- Use these records for media/design processing routes and controls, not as
  OCR output, transcript output, design-layer text, or training material.
