# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Application under advisement

This bundle advises on the Appian application **"Ignyte Appian Developer Copilot"**. The `iadc` graph
MCP is seeded from this application (its export is the source of the dependency graph), and the
`appian` MCP inspects the environment at `https://ignytedemo.appiancloud.com`. When a skill needs a
graph seed target or "the app we're advising on," this is it.

### The project's documentation (SharePoint)

Distinct from the *Appian platform docs* (how Appian works), this is the **IADC project's own
documentation** — requirements, project plans, working-session notes, and decisions collected over
the project's lifecycle. It lives in SharePoint on the `netorg189334` (Ignyte) tenant, at
`Shared Documents / Internal Projects / Appian / Appian Center of Excellence / Automated Code Review /`:

- **`v2/`** — **current.** The Appian-native rebuild matching the live application and the in-flight
  parity/Epic-1 work. Default here when grounding analysis in "what the project intends."
- `v1/` — historical: original requirements, working-session notes, user guides. Decision history only.

Reach these via `/office` (read-only). Content search finds them; folder-name search does not (the
folders are named "Automated Code Review / v1 / v2", not "IADC"). The operational detail lives in the
`office` skill; this is the durable project-scoped record of where the docs are.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/interrogate-with-docs`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo (most repos):

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repo (presence of `CONTEXT-MAP.md` at the root):

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← context-specific decisions
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
