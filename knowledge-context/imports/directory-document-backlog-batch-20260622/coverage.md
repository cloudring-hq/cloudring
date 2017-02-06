# Directory Document Backlog Coverage

- Source kind: directory document backlog batch
- Source target documents: 617
- Target hashes matched: 617
- Document backlog signals written: 617
- Document backlog cases: 45
- Structural coverage added: 464
- Structural probe failed: 152
- Sensitive-signal backlog documents: 13

## Prior Text Status

| prior_status | count |
| --- | ---: |
| `extract_failed:AttributeError` | 221 |
| `extract_failed:BadZipFile` | 150 |
| `unsupported_document_format` | 145 |
| `too_large_for_document_batch` | 96 |
| `extract_failed:KeyError` | 2 |
| `extract_failed:FileNotDecryptedError` | 1 |
| `extract_failed:EmptyFileError` | 1 |
| `extract_failed:PdfStreamError` | 1 |

## Structure Status

| structure_status | count |
| --- | ---: |
| `zip_structure_extracted` | 321 |
| `zip_structure_failed:BadZipFile` | 150 |
| `legacy_ole_identified` | 94 |
| `legacy_structure_identified` | 26 |
| `pdf_structure_extracted` | 23 |
| `pdf_structure_encrypted` | 1 |
| `pdf_structure_failed:EmptyFileError` | 1 |
| `pdf_structure_failed:PdfStreamError` | 1 |

## Magic Families

| magic_family | count |
| --- | ---: |
| `zip_document_container` | 321 |
| `unknown_document_signature` | 152 |
| `legacy_ole_container` | 94 |
| `legacy_or_diagram_document` | 25 |
| `pdf_document` | 24 |
| `rtf_document` | 1 |

## Extensions

| extension | count |
| --- | ---: |
| `pptx` | 273 |
| `docx` | 140 |
| `xls` | 48 |
| `doc` | 41 |
| `xlsx` | 33 |
| `pdf` | 26 |
| `vsdx` | 23 |
| `vss` | 9 |
| `mpp` | 8 |
| `vsd` | 7 |
| `ppt` | 7 |
| `vsdm` | 1 |
| `vdx` | 1 |

## Document Backlog Tags

| tag | count |
| --- | ---: |
| `structural_coverage_added` | 464 |
| `prior_extract_failed` | 376 |
| `magic_zip_document_container` | 321 |
| `embedded_media_structure` | 301 |
| `extension_pptx` | 273 |
| `presentation_container_structure` | 259 |
| `presentation_structure` | 259 |
| `magic_unknown_document_signature` | 152 |
| `structural_probe_failed` | 152 |
| `legacy_document_structured` | 145 |
| `prior_unsupported_document_format` | 145 |
| `extension_docx` | 140 |
| `large_document_structured` | 96 |
| `prior_too_large_for_document_batch` | 96 |
| `legacy_ole_structure` | 94 |
| `magic_legacy_ole_container` | 94 |
| `embedded_objects_structure` | 66 |
| `document_body_structure` | 60 |
| `extension_xls` | 48 |
| `legacy_extension_xls` | 48 |
| `extension_doc` | 41 |
| `legacy_extension_doc` | 41 |
| `word_processing_container_structure` | 37 |
| `extension_xlsx` | 33 |
| `extension_pdf` | 26 |
| `magic_legacy_or_diagram_document` | 25 |
| `magic_pdf_document` | 24 |
| `pdf_page_structure` | 23 |
| `extension_vsdx` | 23 |
| `extension_vss` | 9 |
| `legacy_extension_vss` | 9 |
| `extension_mpp` | 8 |
| `legacy_extension_mpp` | 8 |
| `extension_vsd` | 7 |
| `extension_ppt` | 7 |
| `legacy_extension_ppt` | 7 |
| `legacy_extension_vsd` | 6 |
| `extension_vsdm` | 1 |
| `macro_enabled_structure` | 1 |
| `diagram_document_structure` | 1 |
| `extension_vdx` | 1 |
| `legacy_extension_vdx` | 1 |
| `encrypted_document_backlog` | 1 |
| `encrypted_document_structure` | 1 |
| `magic_rtf_document` | 1 |

## Signals By Domain

| domain | count |
| --- | ---: |
| `networking_connectivity` | 475 |
| `billing_commercial` | 429 |
| `containers_clusters` | 415 |
| `general_business_context` | 262 |
| `developer_api` | 96 |
| `compute_virtualization` | 78 |
| `product_market` | 53 |
| `storage_backup` | 39 |
| `identity_security` | 16 |
| `platform_operations` | 13 |
| `support_incident` | 5 |
| `migration_onboarding` | 5 |
| `compliance_legal` | 4 |

## Signals By Problem

| signal | count |
| --- | ---: |
| `context_signal` | 411 |
| `billing_friction` | 376 |
| `contractual_process` | 173 |
| `data_loss_recovery` | 9 |
| `availability` | 5 |
| `quota_capacity` | 4 |
| `integration_friction` | 4 |
| `latency_performance` | 1 |
| `support_handoff` | 1 |
