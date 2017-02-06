# Document Repair Followup Coverage

- Source kind: directory document repair followup batch
- Source document residual run: `directory-document-residual-batch-20260622`
- Source residual signals: 153
- Followup signals written: 153
- Followup cases: 26
- Control requirements written: 17
- Damaged repair lifecycle routes: 150
- PDF fallback lifecycle routes: 2
- Encrypted access lifecycle routes: 1
- Sensitive lifecycle routes: 5
- Privacy/vendor scan hits: 0

## Lifecycle Status Counts

| document_lifecycle_status | count |
| --- | ---: |
| `damaged_document_repair_lifecycle_requirements_modeled` | 150 |
| `pdf_parser_fallback_lifecycle_requirements_modeled` | 2 |
| `encrypted_document_access_lifecycle_requirements_modeled` | 1 |

## Lifecycle Route Counts

| document_lifecycle_route | count |
| --- | ---: |
| `document_repair_or_reingest_lifecycle_route` | 150 |
| `pdf_parser_fallback_lifecycle_route` | 2 |
| `encrypted_document_access_lifecycle_route` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `chain_of_custody_traceability` | 153 |
| `customer_communication_guidance` | 153 |
| `internal_member_name_exclusion` | 153 |
| `metadata_value_exclusion` | 153 |
| `raw_document_text_exclusion` | 153 |
| `repair_sandbox` | 153 |
| `retention_minimization` | 153 |
| `source_name_path_exclusion` | 153 |
| `support_traceability` | 153 |
| `training_payload_review_gate` | 153 |
| `container_integrity_check` | 150 |
| `repair_or_reingest_guidance` | 150 |
| `tiny_placeholder_validation` | 149 |
| `sensitive_document_route` | 5 |
| `pdf_parser_fallback_vetting` | 2 |
| `encrypted_access_ownership_gate` | 1 |
| `non_decryption_default` | 1 |

## Safety Notes

- This is a derived-only run over document residual metadata records.
- It does not open, repair, decrypt, or parse source documents, and it does not
  copy document text, metadata values, internal member names, source names,
  paths, domains, providers, people, brands, vendors, or secrets.
- Use these records for repair/access/parser lifecycle planning, not as
  document content or training material.
