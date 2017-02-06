# Text Decoder Followup Coverage

- Source kind: directory text decoder followup batch
- Source text residual follow-up run: `directory-text-residual-followup-batch-20260622`
- Source follow-up signals: 87
- Followup signals written: 87
- Followup cases: 8
- Control requirements written: 17
- Mixed printable decoder routes: 36
- Unknown signature routes: 47
- Structured routing routes: 4
- Sensitive decoder routes: 87
- Privacy/vendor scan hits: 0

## Lifecycle Status Counts

| text_decoder_lifecycle_status | count |
| --- | ---: |
| `unknown_signature_identification_lifecycle_requirements_modeled` | 47 |
| `mixed_printable_decoder_lifecycle_requirements_modeled` | 36 |
| `misrouted_image_structural_routing_lifecycle_requirements_modeled` | 3 |
| `misrouted_property_list_routing_lifecycle_requirements_modeled` | 1 |

## Lifecycle Route Counts

| text_decoder_lifecycle_route | count |
| --- | ---: |
| `unknown_signature_identification_lifecycle_route` | 47 |
| `mixed_binary_text_decoder_lifecycle_route` | 36 |
| `image_structural_routing_lifecycle_route` | 3 |
| `property_list_structural_routing_lifecycle_route` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `byte_shape_traceability` | 87 |
| `metadata_only_inventory` | 87 |
| `payload_export_block` | 87 |
| `raw_payload_bytes_exclusion` | 87 |
| `raw_text_exclusion` | 87 |
| `retention_minimization` | 87 |
| `sensitive_text_route` | 87 |
| `source_name_path_exclusion` | 87 |
| `special_decoder_sandbox` | 87 |
| `support_traceability` | 87 |
| `training_payload_review_gate` | 87 |
| `decoder_capability_vetting` | 83 |
| `signature_identification_gate` | 47 |
| `mixed_binary_text_gate` | 36 |
| `structured_artifact_routing_gate` | 4 |
| `image_structural_pipeline_gate` | 3 |
| `property_list_structural_pipeline_gate` | 1 |

## Safety Notes

- This is a derived-only run over text residual follow-up metadata records.
- It does not open source files, decode payloads, copy raw bytes, copy text,
  copy source names, paths, domains, providers, people, brands, vendors, or
  secrets.
- Use these records for decoder and routing lifecycle planning, not as decoded
  text, payload bytes, or training material.
