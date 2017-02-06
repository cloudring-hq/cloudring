# Directory Credential Artifact Coverage

- Source kind: directory credential artifact batch
- Source target signals: 12
- Target hashes matched: 12
- Credential artifact signals written: 12
- Credential artifact cases: 4
- Armor-marker artifacts: 10
- Private-key marker artifacts: 4
- Certificate/request marker artifacts: 6
- License-like marker artifacts: 1
- Truncated marker scans: 0
- Sensitive-signal artifacts: 12

## Extensions

| extension | count |
| --- | ---: |
| `pem` | 6 |
| `crt` | 3 |
| `lic` | 1 |
| `csr` | 1 |
| `cer` | 1 |

## Marker Status

| marker_status | count |
| --- | ---: |
| `armor_markers_counted` | 10 |
| `binary_or_text_marker_retained` | 2 |

## Credential Artifact Tags

| tag | count |
| --- | ---: |
| `not_training_payload` | 12 |
| `secret_management_required` | 12 |
| `sensitive_signal` | 12 |
| `armor_markers_present` | 10 |
| `marker_status_armor_markers_counted` | 10 |
| `path_sensitive_marker` | 10 |
| `extension_pem` | 6 |
| `certificate_marker_present` | 5 |
| `content_sensitive_marker` | 4 |
| `private_key_marker_present` | 4 |
| `extension_crt` | 3 |
| `marker_status_binary_or_text_marker_retained` | 2 |
| `extension_lic` | 1 |
| `license_or_entitlement_marker` | 1 |
| `encrypted_key_marker_present` | 1 |
| `certificate_request_marker_present` | 1 |
| `extension_csr` | 1 |
| `extension_cer` | 1 |

## Signals By Domain

| domain | count |
| --- | ---: |
| `general_business_context` | 6 |
| `networking_connectivity` | 4 |
| `developer_api` | 3 |
| `compliance_legal` | 2 |
| `compute_virtualization` | 1 |

## Signals By Problem

| signal | count |
| --- | ---: |
| `context_signal` | 9 |
| `integration_friction` | 3 |
