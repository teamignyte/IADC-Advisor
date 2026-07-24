# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

The domain docs are **generated project artifacts** — they live in the git-ignored `outputs/`
workspace (see `outputs/README.md`), not committed bundle source:

- **`outputs/CONTEXT.md`** — the project glossary, or
- **`outputs/CONTEXT-MAP.md`** if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`outputs/adr/`** — the chronological, project-wide ADR history (one per substantive decision); read the ADRs that touch the area you're about to work in. A ticket's `outputs/<TICKET-KEY>/decisions.md` rolls up and links the ADRs made for that ticket.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/pressure-test` or `/interrogate-with-docs`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context project (most projects):

```
outputs/
├── CONTEXT.md
├── adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── <TICKET-KEY>/                      ← per-ticket decision records/specs
```

Multi-context project (presence of `CONTEXT-MAP.md`):

```
outputs/
├── CONTEXT-MAP.md
├── adr/                               ← system-wide decisions
├── ordering/
│   ├── CONTEXT.md
│   └── adr/                           ← context-specific decisions
└── billing/
    ├── CONTEXT.md
    └── adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `outputs/CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
