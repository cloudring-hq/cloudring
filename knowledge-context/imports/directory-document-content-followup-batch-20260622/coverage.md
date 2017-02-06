# Document Content Followup Coverage

- Source kind: directory document content followup batch
- Source document backlog run: `directory-document-backlog-batch-20260622`
- Source document backlog signals: 617
- Followup signals written: 617
- Followup cases: 83
- Control requirements written: 23
- Structure-ready content routes: 464
- Repair or access-before-content routes: 153
- Sensitive content routes: 13
- Privacy/vendor scan hits: 0

## Followup Status Counts

| content_followup_status | count |
| --- | ---: |
| `structured_presentation_redacted_summarization_requirements_modeled` | 259 |
| `damaged_document_repair_before_content_requirements_modeled` | 150 |
| `legacy_document_parser_requirements_modeled` | 120 |
| `structured_word_processing_redacted_summarization_requirements_modeled` | 37 |
| `structured_diagram_redacted_summarization_requirements_modeled` | 25 |
| `structured_pdf_redacted_summarization_requirements_modeled` | 23 |
| `pdf_parser_fallback_before_content_requirements_modeled` | 2 |
| `encrypted_document_access_before_content_requirements_modeled` | 1 |

## Content Readiness Counts

| content_readiness | count |
| --- | ---: |
| `structure_ready_for_redacted_summarization` | 464 |
| `repair_or_access_required_before_content` | 153 |

## Content Route Counts

| content_route | count |
| --- | ---: |
| `presentation_redacted_summarization_route` | 259 |
| `damaged_container_repair_first_route` | 150 |
| `legacy_parser_then_redacted_summarization_route` | 120 |
| `word_processing_redacted_summarization_route` | 37 |
| `diagram_visual_text_redaction_route` | 25 |
| `pdf_redacted_summarization_route` | 23 |
| `pdf_parser_fallback_first_route` | 2 |
| `encrypted_access_gate_route` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `metadata_value_exclusion` | 617 |
| `raw_document_text_exclusion` | 617 |
| `retention_minimization` | 617 |
| `source_name_path_exclusion` | 617 |
| `structure_bucket_traceability` | 617 |
| `support_traceability` | 617 |
| `training_payload_review_gate` | 617 |
| `parser_sandbox` | 616 |
| `internal_member_name_exclusion` | 471 |
| `redacted_chunk_summarization_gate` | 464 |
| `visual_media_ocr_gate` | 301 |
| `presentation_media_ocr_gate` | 280 |
| `word_processing_embedded_object_gate` | 244 |
| `damaged_container_repair_before_content` | 150 |
| `legacy_parser_capability_gate` | 120 |
| `spreadsheet_formula_value_guard` | 81 |
| `diagram_visual_text_gate` | 41 |
| `secret_aware_document_content_route` | 13 |
| `project_plan_schedule_value_guard` | 8 |
| `pdf_parser_fallback_before_content` | 2 |
| `macro_embedded_object_gate` | 1 |
| `encrypted_document_access_gate` | 1 |
| `non_decryption_default` | 1 |

## Safety Notes

- This is a derived-only run over structural metadata records.
- It does not read source documents or copy document text, internal member
  names, metadata values, paths, domains, providers, people, brands, vendors,
  or secrets.
- Use these records for content-handling routes and controls, not as document
  content or training material.
