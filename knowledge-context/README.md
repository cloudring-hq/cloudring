# Knowledge Context

This folder is append-only context for future cloud-platform agents. It stores
anonymized experience records, derived cases, and coverage reports. Raw source
messages, source paths, addresses, domains, company names, product names,
provider names, and secrets are intentionally not copied here.

Current source runs:

- `directory-archive-backlog-batch-20260622`: directory archive backlog batch, 22 backlog signals, 114 recursive member signals, 7 backlog cases.
- `directory-archive-batch-20260622`: directory archive batch, 172 archive signals, 68268 anonymized member signals, 33 archive cases.
- `directory-archive-residual-followup-batch-20260622`: directory archive residual follow-up batch, 18 follow-up signals, 16 control requirements, 10 follow-up cases.
- `directory-archive-residual-batch-20260622`: directory archive residual batch, 18 residual signals, 170 repaired member signals, 6 residual cases.
- `directory-binary-batch-20260622`: directory binary batch, 756 binary/database signals, 35 binary cases.
- `directory-binary-textlike-batch-20260622-02`: directory binary text-like batch, 152 decoded-metadata signals, 19 binary text-like cases.
- `directory-binary-textlike-followup-batch-20260622`: directory binary text-like follow-up batch, 70 follow-up signals, 10 control requirements, 17 follow-up cases.
- `directory-credential-artifact-batch-20260622`: directory credential artifact batch, 12 marker-only signals, 4 credential cases.
- `directory-credential-lifecycle-batch-20260622`: directory credential lifecycle batch, 12 lifecycle signals, 12 control requirements, 6 lifecycle cases.
- `directory-database-index-batch-20260622`: directory database/index batch, 92 metadata signals, 9 database/index cases.
- `directory-database-index-residual-batch-20260622`: directory database/index residual batch, 36 residual signals, 10 control requirements, 14 residual cases.
- `directory-document-backlog-batch-20260622`: directory document backlog batch, 617 document backlog signals, 45 document backlog cases.
- `directory-document-batch-20260622`: directory document batch, 2375 document signals, 105 document cases.
- `directory-document-content-followup-batch-20260622`: directory document content follow-up batch, 617 follow-up signals, 23 control requirements, 83 follow-up cases.
- `directory-document-repair-followup-batch-20260622`: directory document repair follow-up batch, 153 follow-up signals, 17 control requirements, 26 follow-up cases.
- `directory-document-residual-batch-20260622`: directory document residual batch, 153 residual signals, 14 control requirements, 26 residual cases.
- `directory-media-backlog-batch-20260622`: directory media backlog batch, 1145 backlog signals, 48 media backlog cases.
- `directory-media-batch-20260622-02`: directory media batch, 7618 media/design signals, 86 media cases.
- `directory-media-deep-followup-batch-20260622`: directory media/design deep follow-up batch, 1145 follow-up signals, 29 control requirements, 82 follow-up cases.
- `directory-snapshot-20260621`: directory snapshot import, 21680 indexed files, 154 derived directory cases.
- `directory-text-decoder-followup-batch-20260622`: directory text decoder follow-up batch, 87 follow-up signals, 17 control requirements, 8 follow-up cases.
- `directory-text-backlog-batch-20260622-02`: directory text backlog batch, 892 backlog signals, 100 backlog cases.
- `directory-text-batch-20260622`: directory text batch, 10761 text signals, 106 text cases.
- `directory-text-residual-followup-batch-20260622`: directory text residual follow-up batch, 87 follow-up signals, 12 control requirements, 8 follow-up cases.
- `directory-text-residual-batch-20260622`: directory text residual batch, 642 residual signals, 97 residual cases.
- `mail-archive-20260621`: legacy mail archive import, 3773 parsed messages, 2327 derived cases, 8410 referenced attachments.

Usage rule for agents: prefer `cloud-experience-context.md` and per-run
`*-context.md` files for principles, then retrieve JSONL case files for
traceable anonymized evidence.

Coverage/backlog rule: read `coverage-backlog.md` before planning new
extractors so unsupported artifacts are refined instead of ignored.
