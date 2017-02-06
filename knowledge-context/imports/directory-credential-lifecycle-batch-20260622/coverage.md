# Credential Lifecycle Coverage

- Source kind: directory credential lifecycle batch
- Source credential artifact run: `directory-credential-artifact-batch-20260622`
- Source marker-only signals: 12
- Lifecycle signals written: 12
- Lifecycle cases: 6
- Control requirements written: 12
- Private-key lifecycle signals: 4
- Certificate/request lifecycle signals: 7
- Entitlement lifecycle signals: 1
- Privacy/vendor scan hits: 0

## Lifecycle Status Counts

| lifecycle_status | count |
| --- | ---: |
| `certificate_lifecycle_requirements_modeled` | 6 |
| `private_key_lifecycle_requirements_modeled` | 4 |
| `entitlement_lifecycle_requirements_modeled` | 1 |
| `certificate_request_lifecycle_requirements_modeled` | 1 |

## Material Class Counts

| material_class | count |
| --- | ---: |
| `certificate` | 5 |
| `private_key` | 3 |
| `certificate_or_request_marker` | 1 |
| `license_or_entitlement` | 1 |
| `certificate_request` | 1 |
| `encrypted_private_key` | 1 |

## Required Control Counts

| control | count |
| --- | ---: |
| `access_audit` | 12 |
| `ownership_registry` | 12 |
| `training_exclusion` | 12 |
| `deployment_binding` | 10 |
| `revocation_plan` | 10 |
| `sensitive_path_quarantine` | 10 |
| `renewal_monitoring` | 6 |
| `managed_secret_storage` | 4 |
| `rotation_workflow` | 4 |
| `entitlement_review` | 1 |
| `request_approval_flow` | 1 |
| `encrypted_key_handling` | 1 |

## Safety Notes

- This is a derived-only run over marker-only credential artifact signals.
- It does not read source files and does not copy key material, subject/issuer
  values, license text, payload text, source paths, names, domains, providers,
  people, brands, vendors, or secrets.
- Use these records for cloud product requirements around secret lifecycle,
  not as training payload.
