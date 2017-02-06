# Synthetic Source Coverage Manifest Example

This example follows
[../templates/source-coverage-manifest-template.md](../templates/source-coverage-manifest-template.md).
It mirrors the current product-memory pattern without exposing raw source
paths.

```yaml
source_pass:
  pass_id: SRC-PASS-007-example
  source_class: significant source inventory reconciliation
  snapshot_date: 2026-06-22
  coverage_mode: inventory-only
  coverage_claim: significant files classified by source class; no full audit claim
  non_claims:
    - not a line-by-line source audit
    - not a full deleted-path audit
    - not a vulnerability or secret-history audit
    - not proof of runtime behavior
  inventory:
    raw_files_indexed: 3577
    significant_files: 418
    excluded_categories:
      - category: dependency
        count_or_class: 3158
        reason: vendored or third-party dependency material
      - category: generated
        count_or_class: 1
        reason: derived build output, not source-of-truth
    high_signal_categories:
      - docs
      - contracts
      - configuration
      - operations
      - tests
      - release
      - security
      - billing
      - user-experience
  git_history:
    repositories_found: 6
    repositories_analyzed: 5 product-signal repositories plus one inventory-only empty repository
    refs_scope: all-available-refs where covered by prior passes
    commit_count_class: mixed
    tags_count_class: mixed
    deleted_path_treatment: theme-scan where covered by prior passes
    limitations:
      - no universal full-history claim
      - not all source classes have line-by-line review
  slices:
    - slice_name: legacy platform prototype
      status: completed
      method: targeted current-tree pass
      product_signal_focus:
        - service manifest
        - local runtime
        - task and plugin model
      requirement_refs:
        - CR-SERVICEFACTORY-001..050
        - CR-OCSCONTRACT-001..046
      conformance_refs:
        - stage1-service-ready
    - slice_name: usage gateway prototype
      status: completed
      method: current-tree and history-theme review
      product_signal_focus:
        - usage events
        - billing trust
        - queue/backpressure
      requirement_refs:
        - CR-BILL-001..036
        - CR-FED-019..036
      conformance_refs:
        - stage4-public-provider-ready
    - slice_name: remaining classification
      status: completed
      method: inventory reconciliation
      product_signal_focus:
        - coverage honesty
        - non-claim preservation
      requirement_refs:
        - CR-SRCOV-001..018
        - CR-SPECEX-008
      conformance_refs:
        - stage7-self-evolving-ready
  source_safety:
    private_marker_scan: passed
    strict_secret_scan: passed
    copyright_safety_review: passed
    unsafe_classes_found:
      - category-only source-safety signals in historical material
    raw_values_transferred_to_requirements: false
    remediation_or_owner_review:
      - preserve only product lessons and category-level findings
  outputs:
    requirement_updates:
      - CR-SRCOV-001..018
      - CR-SPECTPL-001..024
      - CR-SPECEX-001..012
    adr_updates:
      - ADR-0016
    conformance_updates:
      - stage7-self-evolving-ready
    traceability_updates:
      - significant source inventory classification closure
  validation_summary:
    markdown_count: example-value
    cr_id_consistency: passed
    stage_id_consistency: passed
    links: passed
    private_marker_scan: passed
    strict_secret_scan: passed
    conflict_or_trailing_whitespace: passed
    raw_match_output_retained: false
  next_passes:
    - pass_id: SRC-PASS-008
      scope: scenario corpus and filled synthetic examples
      reason: templates need safe examples for agent reuse
      expected_output: examples and expanded role fixtures
```

## Non-Claims

- This example is not an updated live inventory by itself.
- This example must be refreshed when source inventory changes.
- This example demonstrates the distinction between classification closure and
  complete source/history audit.
