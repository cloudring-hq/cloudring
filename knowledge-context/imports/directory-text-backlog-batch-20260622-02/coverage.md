# Directory Text Backlog Coverage

- Source kind: directory text backlog batch
- Backlog candidates seen: 892
- Backlog signals written: 892
- Backlog cases: 100
- Sample-classified signals: 250
- Not-text-like samples retained as backlog: 642
- Sensitive-signal backlog files: 819
- Max sample bytes per file: 262144

## Target Reasons

| target_reason | count |
| --- | ---: |
| `unknown_extension_text_candidate` | 676 |
| `binary_or_database_text_probe` | 152 |
| `large_text_from_previous_batch` | 64 |

## Status

| status | count |
| --- | ---: |
| `sample_not_text_like` | 642 |
| `text_like_binary_full_file_sampled_classified` | 128 |
| `large_text_edge_middle_sampled_classified` | 54 |
| `unknown_extension_full_file_sampled_classified` | 44 |
| `text_like_binary_edge_middle_sampled_classified` | 24 |

## Kinds

| kind | count |
| --- | ---: |
| `text_or_code` | 740 |
| `binary_or_unknown` | 151 |
| `database_or_index` | 1 |

## Byte Profiles

| byte_profile | count |
| --- | ---: |
| `binary_with_nulls` | 556 |
| `text_like_bytes` | 233 |
| `mixed_bytes` | 53 |
| `binary_bytes` | 50 |

## Text Signals

| text_signal | count |
| --- | ---: |
| `unclassified_text_backlog` | 642 |
| `network_connectivity` | 185 |
| `text_like_binary_backlog` | 152 |
| `billing_contract` | 136 |
| `compute_storage` | 133 |
| `developer_automation` | 132 |
| `trial_onboarding` | 113 |
| `access_secret_management` | 107 |
| `migration_transfer` | 104 |
| `managed_support` | 99 |
| `performance_capacity` | 98 |
| `community_education` | 88 |
| `lead_sales` | 69 |
| `compliance_policy` | 67 |
| `large_text_artifact` | 64 |
| `partner_channel` | 62 |
| `pricing_packaging` | 46 |
| `backup_recovery` | 40 |
| `product_positioning` | 36 |
| `general_text_signal` | 34 |
| `incident_outage` | 16 |

## Structural Signals

| structure | count |
| --- | ---: |
| `sample_full_file_sampled` | 804 |
| `size_lt_1_mib` | 793 |
| `kind_text_or_code` | 740 |
| `extension_none` | 681 |
| `target_unknown_extension_text_candidate` | 676 |
| `profile_binary_with_nulls` | 556 |
| `entropy_medium_entropy` | 402 |
| `entropy_very_low_entropy` | 253 |
| `profile_text_like_bytes` | 233 |
| `entropy_low_entropy` | 227 |
| `has_version_signal` | 199 |
| `has_url_or_domain_shape` | 173 |
| `target_binary_or_database_text_probe` | 152 |
| `kind_binary_or_unknown` | 151 |
| `has_config_shape` | 114 |
| `sample_edge_middle_sampled` | 88 |
| `has_script_or_code` | 81 |
| `size_lt_1_kib` | 69 |
| `has_email_shape` | 66 |
| `target_large_text_from_previous_batch` | 64 |
| `profile_mixed_bytes` | 53 |
| `has_form_fields` | 51 |
| `profile_binary_bytes` | 50 |
| `extension_scssc` | 46 |
| `has_currency_signal` | 41 |
| `has_percent_signal` | 37 |
| `extension_custom_ext` | 36 |
| `size_lt_100_mib` | 30 |
| `extension_csv` | 27 |
| `has_secret_line_shape` | 16 |
| `extension_js` | 15 |
| `has_table_markup` | 15 |
| `extension_bak` | 14 |
| `entropy_high_entropy` | 10 |
| `extension_txt` | 9 |
| `extension_tscproj` | 8 |
| `extension_numeric_ext` | 7 |
| `extension_pem` | 6 |
| `extension_map` | 4 |
| `extension_url` | 4 |
| `extension_html` | 3 |
| `extension_orig` | 3 |
| `extension_crt` | 3 |
| `extension_iml` | 2 |
| `extension_grammar` | 2 |
| `extension_com` | 2 |
| `extension_xml` | 2 |
| `extension_sesx` | 2 |
| `extension_bmml` | 2 |
| `extension_log` | 1 |
| `extension_lib` | 1 |
| `extension_dat` | 1 |
| `kind_database_or_index` | 1 |
| `extension_sql` | 1 |
| `extension_csr` | 1 |
| `extension_tdy` | 1 |
| `extension_spec` | 1 |
| `extension_pm` | 1 |
| `extension_scandeps` | 1 |
| `extension_scap` | 1 |
| `extension_lock` | 1 |
| `extension_rpp` | 1 |
| `extension_rpp-bak` | 1 |
| `extension_bpmn` | 1 |

## Signals By Domain

| domain | count |
| --- | ---: |
| `general_business_context` | 411 |
| `storage_backup` | 237 |
| `developer_api` | 223 |
| `networking_connectivity` | 201 |
| `billing_commercial` | 180 |
| `identity_security` | 161 |
| `compute_virtualization` | 156 |
| `containers_clusters` | 108 |
| `support_incident` | 105 |
| `compliance_legal` | 83 |
| `product_market` | 73 |
| `platform_operations` | 53 |
| `migration_onboarding` | 41 |

## Signals By Problem

| signal | count |
| --- | ---: |
| `context_signal` | 581 |
| `data_loss_recovery` | 188 |
| `billing_friction` | 170 |
| `access_blocked` | 90 |
| `support_handoff` | 76 |
| `integration_friction` | 71 |
| `latency_performance` | 71 |
| `quota_capacity` | 69 |
| `contractual_process` | 69 |
| `availability` | 62 |
| `unclear_requirements` | 11 |
