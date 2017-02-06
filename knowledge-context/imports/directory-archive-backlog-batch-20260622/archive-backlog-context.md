# Directory Archive Backlog Context

This run refines archive backlog that could not be fully listed in the archive batch. It adds structural triage for direct failed or unsupported containers and recursively lists nested zip-like containers in memory, without copying raw paths, file names, member names, payload text, addresses, domains, people, provider names, brand names, vendor names, or secrets.

## Agent Use

- Use `archive-backlog-cases.jsonl` for failed, unsupported, and nested archive situations.
- Use `archive-backlog-signals.jsonl` for stable-id traceability and backlog status.
- Use `archive-backlog-members.jsonl` only for anonymized recursive member composition.
- Treat direct parser/repair needs and unsupported nested containers as retained queues, not dropped context.

## Largest Archive Backlog Cases

- `archivebacklogcase-5d0ae7c55c28` (6 signals): An archive backlog cluster preserved support incident context; the dominant backlog state is direct format parser needed and the dominant operational signal is context signal.
- `archivebacklogcase-751ad0adf90c` (5 signals): An archive backlog cluster preserved networking connectivity context; the dominant backlog state is direct zip repair needed and the dominant operational signal is context signal.
- `archivebacklogcase-84990859cf01` (4 signals): An archive backlog cluster preserved developer api context; the dominant backlog state is direct format parser needed and the dominant operational signal is support handoff.
- `archivebacklogcase-4a8fffef34e0` (3 signals): An archive backlog cluster preserved general business context context; the dominant backlog state is direct format parser needed and the dominant operational signal is context signal.
- `archivebacklogcase-afe210672858` (2 signals): An archive backlog cluster preserved storage backup context; the dominant backlog state is nested zip listed and the dominant operational signal is context signal.
- `archivebacklogcase-98983dbc4629` (1 signals): An archive backlog cluster preserved storage backup context; the dominant backlog state is direct format parser needed and the dominant operational signal is data loss recovery.
- `archivebacklogcase-70aaabdff203` (1 signals): An archive backlog cluster preserved networking connectivity context; the dominant backlog state is nested zip listed and the dominant operational signal is context signal.
