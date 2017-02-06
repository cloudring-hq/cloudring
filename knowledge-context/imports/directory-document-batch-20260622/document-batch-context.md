# Directory Document Batch Context

This run classifies document-like artifacts without copying raw document text, paths, domains, addresses, provider names, people, or secrets. It adds signals from proposals, presentations, runbooks, architecture materials, billing/legal documents, support cases, and compliance artifacts.

## Agent Use

- Use `document-cases.jsonl` for document-derived cloud product and operations evidence.
- Use `document-signals.jsonl` for file-level traceability by stable ids only.
- Treat unsupported or too-large document statuses as a queue for later safe extraction, not as missing coverage.
- Convert access-credential document signals into product requirements for managed secrets and audit workflows.

## Largest Document Cases

- `doccase-751ad0adf90c` (875 signals): A document cluster captured product presentation within billing commercial; the dominant operational signal is billing friction.
- `doccase-84990859cf01` (502 signals): A document cluster captured finance billing within billing commercial; the dominant operational signal is billing friction.
- `doccase-f306cc7f9459` (158 signals): A document cluster captured commercial offer within billing commercial; the dominant operational signal is billing friction.
- `doccase-4a8fffef34e0` (136 signals): A document cluster captured general document signal within general business context; the dominant operational signal is context signal.
- `doccase-1bdd066224f1` (74 signals): A document cluster captured finance billing within billing commercial; the dominant operational signal is billing friction.
- `doccase-e192288c592e` (60 signals): A document cluster captured finance billing within identity security; the dominant operational signal is billing friction.
- `doccase-de3f1785d431` (55 signals): A document cluster captured general document signal within general business context; the dominant operational signal is context signal.
- `doccase-70aaabdff203` (55 signals): A document cluster captured support customer case within compute virtualization; the dominant operational signal is context signal.
- `doccase-4ed622f8acff` (47 signals): A document cluster captured support customer case within compute virtualization; the dominant operational signal is billing friction.
- `doccase-61ea5737de3a` (44 signals): A document cluster captured unread supported document within storage backup; the dominant operational signal is context signal.
- `doccase-5d0ae7c55c28` (29 signals): A document cluster captured unsupported legacy document within general business context; the dominant operational signal is context signal.
- `doccase-ce775a271b74` (26 signals): A document cluster captured commercial offer within storage backup; the dominant operational signal is quota capacity.
- `doccase-afe210672858` (18 signals): A document cluster captured finance billing within compute virtualization; the dominant operational signal is billing friction.
- `doccase-d4e5fdf4ef5e` (16 signals): A document cluster captured unsupported legacy document within general business context; the dominant operational signal is context signal.
- `doccase-a09616ae0715` (15 signals): A document cluster captured unread supported document within general business context; the dominant operational signal is context signal.
- `doccase-98983dbc4629` (15 signals): A document cluster captured finance billing within compute virtualization; the dominant operational signal is billing friction.
- `doccase-2fb01de21bd5` (13 signals): A document cluster captured support customer case within product market; the dominant operational signal is billing friction.
- `doccase-943f5f47292c` (12 signals): A document cluster captured contract legal within networking connectivity; the dominant operational signal is access blocked.
- `doccase-54dd1a70b44f` (9 signals): A document cluster captured support customer case within storage backup; the dominant operational signal is data loss recovery.
- `doccase-474fa159f0a4` (8 signals): A document cluster captured support customer case within compute virtualization; the dominant operational signal is support handoff.
