# Archive Residual Coverage

- Source kind: directory archive residual batch
- Source archive backlog run: `directory-archive-backlog-batch-20260622`
- Source residual targets: 18
- Residual signals written: 18
- Residual member signals written: 170
- Archive residual cases: 6
- Direct zip repair targets with partial listings: 2
- Direct format parser unavailable targets: 11
- Nested targets still unlisted after probe: 5
- Privacy/vendor scan hits: 0

## Residual Status Counts

| status | count |
| --- | ---: |
| `direct_format_parser_unavailable` | 11 |
| `nested_format_parser_unavailable` | 3 |
| `direct_zip_partial_listing_added` | 2 |
| `nested_zip_repair_probe_unlisted` | 2 |

## Archive Extension Counts

| extension | count |
| --- | ---: |
| `rar` | 12 |
| `zip` | 4 |
| `7z` | 2 |

## Recovered Member Kind Counts

| kind | count |
| --- | ---: |
| `text_or_code` | 125 |
| `binary_or_unknown` | 26 |
| `document` | 11 |
| `legacy_document_or_diagram` | 6 |
| `media_or_design` | 2 |

## Safety Notes

- Raw source paths, archive names, member names, payload text, domains, brands,
  providers, people, and secrets are not written.
- Member names from the local archive lister are used only in memory to derive
  stable ids and controlled extension/kind/depth buckets.
- Partial listings from damaged containers are retained as evidence, not as a
  guarantee that the container was fully recovered.
