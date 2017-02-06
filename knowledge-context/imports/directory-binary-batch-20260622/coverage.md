# Directory Binary Batch Coverage

- Source kind: directory binary batch
- Binary/database files seen: 756
- Binary signals written: 756
- Binary cases: 35
- Sample bytes per file: 131072
- Sensitive-signal binary files: 189

## Kinds

| kind | count |
| --- | ---: |
| `binary_or_unknown` | 697 |
| `database_or_index` | 59 |

## Extensions

| extension | count |
| --- | ---: |
| `scssc` | 242 |
| `trec` | 224 |
| `custom_ext` | 102 |
| `idx` | 26 |
| `pack` | 26 |
| `dot` | 15 |
| `bak` | 14 |
| `nib` | 13 |
| `wma` | 12 |
| `tscproj` | 8 |
| `numeric_ext` | 7 |
| `pem` | 6 |
| `arf` | 6 |
| `map` | 4 |
| `url` | 4 |
| `db` | 4 |
| `orig` | 3 |
| `dat` | 3 |
| `crt` | 3 |
| `com` | 3 |
| `iml` | 2 |
| `textclipping` | 2 |
| `grammar` | 2 |
| `odt` | 2 |
| `sesx` | 2 |
| `bmml` | 2 |
| `scc` | 2 |
| `iba` | 1 |
| `lic` | 1 |
| `lib` | 1 |
| `csr` | 1 |
| `tdy` | 1 |
| `spec` | 1 |
| `scandeps` | 1 |
| `imb` | 1 |
| `scap` | 1 |
| `car` | 1 |
| `cer` | 1 |
| `lock` | 1 |
| `partial` | 1 |
| `rpp` | 1 |
| `rpp-bak` | 1 |
| `bpmn` | 1 |
| `tmp` | 1 |

## Magic Families

| magic_family | count |
| --- | ---: |
| `unknown_binary_signature` | 331 |
| `media_signature` | 226 |
| `custom_extension_binary` | 101 |
| `database_or_index_extension` | 33 |
| `git_pack_or_packfile` | 26 |
| `zip_container_signature` | 19 |
| `certificate_or_key_text` | 10 |
| `numeric_extension_binary` | 7 |
| `certificate_or_license_extension` | 2 |
| `pdf_signature` | 1 |

## Byte Profiles

| byte_profile | count |
| --- | ---: |
| `binary_bytes` | 370 |
| `mixed_bytes` | 212 |
| `text_like_bytes` | 152 |
| `binary_with_nulls` | 22 |

## Binary Signals

| binary_signal | count |
| --- | ---: |
| `application_binary_artifact` | 744 |
| `project_metadata_artifact` | 266 |
| `recording_or_capture_artifact` | 231 |
| `text_like_binary_backlog` | 152 |
| `sanitized_unknown_extension` | 109 |
| `database_or_index_artifact` | 92 |
| `backup_or_dump_artifact` | 38 |
| `container_misclassified_as_binary` | 19 |
| `credential_or_certificate_artifact` | 12 |
| `mail_or_message_artifact` | 7 |
| `general_binary_signal` | 1 |

## Signals By Domain

| domain | count |
| --- | ---: |
| `networking_connectivity` | 585 |
| `storage_backup` | 106 |
| `developer_api` | 88 |
| `containers_clusters` | 85 |
| `compute_virtualization` | 68 |
| `identity_security` | 40 |
| `general_business_context` | 24 |
| `billing_commercial` | 23 |
| `platform_operations` | 5 |
| `support_incident` | 5 |
| `compliance_legal` | 4 |
| `product_market` | 3 |
| `migration_onboarding` | 2 |

## Signals By Problem

| signal | count |
| --- | ---: |
| `contractual_process` | 578 |
| `context_signal` | 149 |
| `data_loss_recovery` | 98 |
| `billing_friction` | 19 |
| `access_blocked` | 13 |
| `integration_friction` | 3 |
| `support_handoff` | 2 |
| `quota_capacity` | 1 |
