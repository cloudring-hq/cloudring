# Database/Index Residual Context

This run derives safe handling requirements for database/index artifacts whose first metadata pass retained generic or sensitive statuses. It records decoder routes, risk buckets, required controls, and platform implications only. It does not read source files or copy rows, schema names, table names, column names, payload text, source paths, domains, provider names, people, brands, vendors, or secrets.

Agent usage:

- Use `database-index-residual-cases.jsonl` for local-store, cache, index, and migration-residue product situations.
- Use `database-index-residual-signals.jsonl` for stable ids, residual statuses, decoder routes, and risk buckets.
- Use `database-index-residual-controls.jsonl` as a safe parser and migration-planning checklist.
- Never treat this layer as decoded database rows, schema text, or customer payload.
