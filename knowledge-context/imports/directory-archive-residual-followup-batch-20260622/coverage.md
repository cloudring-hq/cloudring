# Archive Residual Followup Coverage

- Source kind: directory archive residual followup batch
- Source archive residual run: `directory-archive-residual-batch-20260622`
- Source residual signals: 18
- Followup signals written: 18
- Followup cases: 10
- Control requirements written: 16
- Direct parser capability routes: 11
- Nested parser capability routes: 3
- Direct repair completion routes: 2
- Nested repair completion routes: 2
- Sensitive followup routes: 12
- Privacy/vendor scan hits: 0

## Followup Status Counts

| archive_followup_status | count |
| --- | ---: |
| `direct_archive_parser_capability_requirements_modeled` | 11 |
| `nested_archive_parser_capability_requirements_modeled` | 3 |
| `nested_zip_repair_completion_requirements_modeled` | 2 |
| `direct_zip_repair_completion_requirements_modeled` | 2 |

## Followup Route Counts

| archive_followup_route | count |
| --- | ---: |
| `direct_parser_capability_gate` | 11 |
| `nested_parser_capability_gate` | 3 |
| `nested_zip_repair_completion_gate` | 2 |
| `direct_zip_repair_completion_gate` | 2 |

## Required Control Counts

| control | count |
| --- | ---: |
| `archive_name_path_exclusion` | 18 |
| `integrity_traceability` | 18 |
| `member_composition_only` | 18 |
| `no_payload_extraction_to_disk` | 18 |
| `raw_member_name_exclusion` | 18 |
| `raw_payload_text_exclusion` | 18 |
| `retention_minimization` | 18 |
| `sandboxed_parser_execution` | 18 |
| `tool_failure_observability` | 18 |
| `training_payload_review_gate` | 18 |
| `parser_capability_vetting` | 14 |
| `unsupported_format_customer_guidance` | 14 |
| `sensitive_archive_route` | 12 |
| `nested_container_boundary` | 5 |
| `partial_listing_confidence_guard` | 4 |
| `repair_completion_gate` | 4 |

## Safety Notes

- This is a derived-only run over archive residual metadata records.
- It does not open source archives, extract payloads, or copy archive names,
  member names, payload text, paths, domains, providers, people, brands,
  vendors, or secrets.
- Use these records for parser and repair planning, not as archive content.
