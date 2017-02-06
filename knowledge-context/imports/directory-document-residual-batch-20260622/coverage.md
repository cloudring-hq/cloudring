# Document Residual Coverage

- Source kind: directory document residual batch
- Source document backlog run: `directory-document-backlog-batch-20260622`
- Source residual targets: 153
- Residual signals written: 153
- Residual cases: 26
- Control requirements written: 14
- Damaged zip-document containers: 150
- PDF parser failures: 2
- Encrypted documents: 1
- Sensitive residual signals: 5
- Privacy/vendor scan hits: 0

## Residual Status Counts

| residual_status | count |
| --- | ---: |
| `damaged_zip_document_repair_requirements_modeled` | 150 |
| `pdf_parser_failure_requirements_modeled` | 2 |
| `encrypted_document_access_requirements_modeled` | 1 |

## Handling Route Counts

| handling_route | count |
| --- | ---: |
| `damaged_container_repair_or_reingest_route` | 150 |
| `bounded_pdf_parser_fallback_route` | 2 |
| `encrypted_document_access_gate` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `internal_member_name_exclusion` | 153 |
| `metadata_only_inventory` | 153 |
| `metadata_value_exclusion` | 153 |
| `raw_document_text_exclusion` | 153 |
| `retention_minimization` | 153 |
| `safe_parser_sandbox` | 153 |
| `support_traceability` | 153 |
| `container_integrity_check` | 150 |
| `repair_or_reingest_guidance` | 150 |
| `tiny_container_validation` | 149 |
| `secret_aware_document_handling` | 5 |
| `pdf_parser_fallback` | 2 |
| `encrypted_document_access_gate` | 1 |
| `non_decryption_default` | 1 |

## Safety Notes

- This is a derived-only run over structural metadata records.
- It does not read source documents or copy document text, internal member
  names, metadata values, paths, domains, providers, people, brands, vendors,
  or secrets.
- Use these records for repair/access/parser planning, not as document content.
