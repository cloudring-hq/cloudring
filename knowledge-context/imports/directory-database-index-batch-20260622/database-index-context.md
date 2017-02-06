# Directory Database/Index Context

This run refines database and index artifacts from the binary batch. It records safe metadata only: header families, schema type counts, object-count buckets, container member-count buckets, size buckets, stable ids, and status fields. It does not copy raw paths, file names, table names, column names, row values, payload text, URLs, domains, people, provider names, brand names, vendor names, or secrets.

## Agent Use

- Use `database-index-cases.jsonl` for local-store, index, packfile, metadata-cache, and migration-residue cases.
- Use `database-index-signals.jsonl` for stable-id traceability and safe metadata buckets only.
- Treat probe failures, generic stores, and sensitive signals as retained queues, not dropped context.
- Never infer source identities from schema counts or object-count buckets.

## Largest Database/Index Cases

- `dbindexcase-0a53b8068f61` (52 signals): A database/index cluster preserved content addressed pack index metadata for developer api; the dominant signal is context signal.
- `dbindexcase-751ad0adf90c` (24 signals): A database/index cluster preserved generic database index artifact metadata for developer api; the dominant signal is billing friction.
- `dbindexcase-743b73e8273c` (4 signals): A database/index cluster preserved generic database index artifact metadata for networking connectivity; the dominant signal is contractual process.
- `dbindexcase-70aaabdff203` (4 signals): A database/index cluster preserved generic local store metadata for compute virtualization; the dominant signal is context signal.
- `dbindexcase-32106a0f3915` (2 signals): A database/index cluster preserved generic local store metadata for storage backup; the dominant signal is data loss recovery.
- `dbindexcase-605ee7880e25` (2 signals): A database/index cluster preserved generic database index artifact metadata for networking connectivity; the dominant signal is contractual process.
- `dbindexcase-bf4dc4499799` (2 signals): A database/index cluster preserved content addressed pack index metadata for developer api; the dominant signal is context signal.
- `dbindexcase-28490af7bdaf` (1 signals): A database/index cluster preserved generic local store metadata for general business context; the dominant signal is context signal.
- `dbindexcase-af0bfb91baa0` (1 signals): A database/index cluster preserved generic database index artifact metadata for networking connectivity; the dominant signal is contractual process.
