# Database/Index Residual Coverage

- Source kind: directory database/index residual batch
- Source database/index run: `directory-database-index-batch-20260622`
- Source generic metadata targets: 36
- Residual signals written: 36
- Residual cases: 14
- Control requirements written: 10
- Sensitive residual routes: 19
- Text-like residual routes: 24
- Privacy/vendor scan hits: 0

## Residual Status Counts

| residual_status | count |
| --- | ---: |
| `sensitive_text_like_index_decoder_gate_modeled` | 17 |
| `generic_text_like_index_decoder_candidate_modeled` | 7 |
| `generic_local_store_parser_candidate_modeled` | 5 |
| `generic_mixed_binary_index_probe_modeled` | 3 |
| `generic_binary_index_probe_modeled` | 2 |
| `sensitive_database_index_decoder_gate_modeled` | 2 |

## Decoder Route Counts

| decoder_route | count |
| --- | ---: |
| `secret_aware_metadata_only_decoder` | 19 |
| `redacted_text_like_index_decoder` | 7 |
| `bounded_local_store_metadata_parser` | 5 |
| `bounded_mixed_binary_probe` | 3 |
| `bounded_binary_index_probe` | 2 |

## Required Control Counts

| control | count |
| --- | ---: |
| `cache_rebuild_policy` | 36 |
| `metadata_only_inventory` | 36 |
| `migration_residue_analysis` | 36 |
| `retention_minimization` | 36 |
| `row_value_exclusion` | 36 |
| `safe_parser_sandbox` | 36 |
| `schema_name_exclusion` | 36 |
| `support_handoff_traceability` | 36 |
| `billing_context_review` | 29 |
| `secret_aware_decoder_gate` | 19 |

## Safety Notes

- This is a derived-only run over safe database/index metadata signals.
- It does not open source files or copy row values, schema names, table names,
  column names, payload text, paths, domains, providers, people, brands,
  vendors, or secrets.
- Use these records for parser planning, migration requirements, and
  secret-aware routing, not as decoded database content.
