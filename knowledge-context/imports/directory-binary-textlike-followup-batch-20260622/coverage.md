# Binary Text-Like Follow-Up Coverage

- Source kind: directory binary text-like follow-up batch
- Source binary text-like run: `directory-binary-textlike-batch-20260622-02`
- Source follow-up targets: 70
- Follow-up signals written: 70
- Follow-up cases: 17
- Control requirements written: 10
- Sensitive follow-up signals: 69
- Chunked follow-up signals: 17
- Credential-marker follow-up signals: 10
- Privacy/vendor scan hits: 0

## Follow-Up Status Counts

| followup_status | count |
| --- | ---: |
| `sensitive_counts_only_followup_modeled` | 43 |
| `sensitive_chunked_followup_modeled` | 16 |
| `credential_marker_followup_modeled` | 10 |
| `large_chunked_followup_modeled` | 1 |

## Decoder Route Counts

| decoder_route | count |
| --- | ---: |
| `secret_aware_counts_only_review` | 43 |
| `secret_aware_chunked_decoder_gate` | 16 |
| `credential_marker_secret_lifecycle_route` | 10 |
| `redacted_large_artifact_chunk_review` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `raw_text_exclusion` | 70 |
| `redaction_marker_accounting` | 70 |
| `retention_minimization` | 70 |
| `support_traceability` | 70 |
| `training_payload_gate` | 70 |
| `secret_aware_review` | 69 |
| `configuration_residue_modeling` | 56 |
| `chunked_redacted_ingestion` | 17 |
| `large_artifact_sampling_policy` | 17 |
| `credential_marker_routing` | 10 |

## Safety Notes

- This is a derived-only run over decoded-metadata records.
- It does not read source files and does not copy raw decoded text, paths,
  names, domains, providers, people, brands, vendors, or secrets.
- Use these records for secret-aware handling, redacted chunk policy, and
  training-payload gates, not as text content.
