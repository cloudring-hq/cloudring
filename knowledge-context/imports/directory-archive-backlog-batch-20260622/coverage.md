# Directory Archive Backlog Coverage

- Source kind: directory archive backlog batch
- Source direct unlisted archive targets: 13
- Source nested archive targets: 9
- Direct targets matched: 13
- Nested targets matched: 9
- Archive backlog signals written: 22
- Nested member signals written: 114
- Archive backlog cases: 7
- Direct archives structurally triaged: 13
- Direct archives still requiring member parser or repair: 13
- Nested archives listed: 4
- Nested archives not listed: 5
- Truncated nested listings: 0

## Target Types

| target_type | count |
| --- | ---: |
| `direct_unlisted_archive` | 13 |
| `nested_archive_member` | 9 |

## Backlog Status

| status | count |
| --- | ---: |
| `direct_format_parser_needed` | 11 |
| `nested_zip_listed` | 4 |
| `nested_listing_unsupported_format` | 3 |
| `direct_zip_repair_needed` | 2 |
| `nested_zip_list_failed:BadZipFile` | 2 |

## Magic Families

| magic_family | count |
| --- | ---: |
| `rar_container` | 10 |
| `nested_zip_container` | 6 |
| `zip_container` | 2 |
| `nested_rar_container` | 2 |
| `seven_z_container` | 1 |
| `nested_7z_container` | 1 |

## Archive Extensions

| extension | count |
| --- | ---: |
| `rar` | 12 |
| `zip` | 8 |
| `7z` | 2 |

## Backlog Tags

| tag | count |
| --- | ---: |
| `target_direct_unlisted_archive` | 13 |
| `extension_rar` | 12 |
| `backlog_direct_format_parser_needed` | 11 |
| `prior_archive_listing_unsupported` | 11 |
| `specialized_parser_required` | 11 |
| `magic_rar_container` | 10 |
| `prior_nested_archive_member` | 9 |
| `target_nested_archive_member` | 9 |
| `extension_zip` | 8 |
| `magic_nested_zip_container` | 6 |
| `backlog_nested_zip_listed` | 4 |
| `nested_member_composition_captured` | 4 |
| `recursive_listing_added` | 4 |
| `backlog_nested_listing_unsupported_format` | 3 |
| `unsupported_nested_archive_retained` | 3 |
| `backlog_direct_zip_repair_needed` | 2 |
| `magic_zip_container` | 2 |
| `prior_archive_list_failed` | 2 |
| `repair_or_reingest_required` | 2 |
| `extension_7z` | 2 |
| `magic_nested_rar_container` | 2 |
| `backlog_nested_zip_list_failed:BadZipFile` | 2 |
| `magic_seven_z_container` | 1 |
| `magic_nested_7z_container` | 1 |

## Nested Member Kinds

| kind | count |
| --- | ---: |
| `binary_or_unknown` | 67 |
| `document` | 20 |
| `media_or_design` | 18 |
| `text_or_code` | 9 |

## Nested Member Extensions

| extension | count |
| --- | ---: |
| `custom_ext` | 67 |
| `pptx` | 16 |
| `png` | 12 |
| `none` | 9 |
| `gif` | 3 |
| `psd` | 3 |
| `pdf` | 3 |
| `docx` | 1 |

## Signals By Domain

| domain | count |
| --- | ---: |
| `support_incident` | 15 |
| `containers_clusters` | 13 |
| `networking_connectivity` | 11 |
| `developer_api` | 9 |
| `storage_backup` | 7 |
| `general_business_context` | 7 |
| `billing_commercial` | 4 |
| `compliance_legal` | 4 |
| `compute_virtualization` | 3 |
| `identity_security` | 1 |

## Signals By Problem

| signal | count |
| --- | ---: |
| `context_signal` | 18 |
| `support_handoff` | 15 |
| `billing_friction` | 4 |
| `availability` | 2 |
| `data_loss_recovery` | 2 |
| `contractual_process` | 2 |
| `latency_performance` | 1 |
