# Source Coverage Manifest Template

Purpose: record what a source intake pass actually covered, what it excluded,
what product signals were extracted and what must not be inferred.

This template protects CloudRING requirements from two opposite failures:
losing valuable experience and overclaiming that every file/history decision
has been fully analyzed.

```yaml
source_pass:
  pass_id: SRC-PASS-000
  source_class: anonymized source class
  snapshot_date: date
  coverage_mode: inventory-only | targeted-current-tree | history-theme | all-refs-theme | line-by-line | full-history-audit
  coverage_claim: concise honest claim
  non_claims:
    - what this pass does not prove
  inventory:
    raw_files_indexed: count-or-class
    significant_files: count-or-class
    excluded_categories:
      - category: dependency | generated | binary | static | history-store | empty | third-party-reference | local-cache | other
        count_or_class: count-or-class
        reason: why excluded
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
    repositories_found: count-or-class
    repositories_analyzed: count-or-class
    refs_scope: default-branch | selected-refs | all-available-refs | all-refs-plus-deleted-paths | not-applicable
    commit_count_class: none | small | medium | large | huge | not-counted
    tags_count_class: none | small | medium | large | not-counted
    deleted_path_treatment: not-reviewed | category-scan | theme-scan | line-by-line | not-applicable
    limitations:
      - limitation
  slices:
    - slice_name: source-safe category name
      status: completed | targeted | sampled | excluded | future-pass
      method: read | search | history-theme | agent-review | other
      product_signal_focus:
        - signal category
      requirement_refs:
        - CR-...
      conformance_refs:
        - profile-id
  source_safety:
    private_marker_scan: passed | failed | warning | not-run
    strict_secret_scan: passed | failed | warning | not-run
    copyright_safety_review: passed | warning | blocked | not-run
    unsafe_classes_found:
      - category only, no raw value
    raw_values_transferred_to_requirements: false
    remediation_or_owner_review:
      - decision
  outputs:
    requirement_updates:
      - CR-...
    adr_updates:
      - ADR-...
    conformance_updates:
      - profile-id
    traceability_updates:
      - safe-reference
  validation_summary:
    markdown_count: count
    cr_id_consistency: passed | failed | not-run
    stage_id_consistency: passed | failed | not-run
    links: passed | failed | not-run
    private_marker_scan: passed | failed | not-run
    strict_secret_scan: passed | failed | not-run
    conflict_or_trailing_whitespace: passed | failed | not-run
    raw_match_output_retained: false
  next_passes:
    - pass_id: SRC-PASS-000
      scope: bounded source class
      reason: why needed
      expected_output: product requirement or evidence artifact
```

## Coverage Claim Rules

| Claim | Required Evidence |
|---|---|
| Inventory-only | File counts/classes, exclusions and no product-completeness claim. |
| Targeted current-tree | Source slice, significant files/classes, read/search method and limitations. |
| History-theme | Refs scope, commit/tag class, deleted-path treatment and redacted signal themes. |
| All-refs theme | All available refs or explicit missing-ref limitation plus source-safety treatment. |
| Line-by-line | File list/classes, reviewed scope, exclusions, reviewer method and validation summary. |
| Full-history audit | All refs, deleted paths, tags, generated/vendor exclusions, source-safety, copyright-safety and owner review. |

## Stop Conditions

Agent must stop if:

- asked to claim full source or history coverage without the required evidence;
- source-derived output would include private names, internal endpoints,
  hostnames, network addresses, credentials, exact source snippets or raw
  operational commands;
- a source class is excluded without category and reason;
- history analysis omits refs or deleted paths but claims every decision;
- validation succeeds structurally but semantic/source coverage remains
  unproven;
- old implementation details are promoted to future requirements without
  product reason.
