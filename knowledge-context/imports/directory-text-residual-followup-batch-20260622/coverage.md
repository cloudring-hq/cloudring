# Text Residual Follow-Up Coverage

- Source kind: directory text residual follow-up batch
- Source text residual run: `directory-text-residual-batch-20260622`
- Source follow-up targets: 87
- Follow-up signals written: 87
- Follow-up cases: 8
- Control requirements written: 12
- Mixed printable candidates: 36
- Unknown signature candidates: 47
- Misrouted structured artifacts: 4
- Privacy/vendor scan hits: 0

## Follow-Up Status Counts

| followup_status | count |
| --- | ---: |
| `unknown_signature_identification_requirements_modeled` | 47 |
| `mixed_printable_special_decoder_requirements_modeled` | 36 |
| `misrouted_image_structural_route_modeled` | 3 |
| `misrouted_property_list_route_modeled` | 1 |

## Decoder Route Counts

| decoder_route | count |
| --- | ---: |
| `signature_identification_before_decoder` | 47 |
| `bounded_mixed_binary_text_decoder_gate` | 36 |
| `visual_design_structural_route` | 3 |
| `property_list_metadata_route` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `metadata_only_inventory` | 87 |
| `payload_export_block` | 87 |
| `raw_text_exclusion` | 87 |
| `retention_minimization` | 87 |
| `special_decoder_sandbox` | 87 |
| `support_traceability` | 87 |
| `training_payload_gate` | 87 |
| `signature_identification` | 47 |
| `mixed_binary_text_gate` | 36 |
| `structured_artifact_routing` | 4 |
| `visual_or_design_route` | 3 |
| `property_list_route` | 1 |

## Safety Notes

- This is a derived-only run over byte-shape and magic-family metadata.
- It does not read source files or copy raw text, decoded payload, paths,
  names, domains, providers, people, brands, vendors, or secrets.
- Use these records for special decoder and routing planning, not as text.
