# Rename the spine skills to descriptive names, and collapse the greenfield flow

The main-flow skills carried character names — `gumby` (the ticket dialectic) and `pokey` (the
build spec) — which don't say what they do. They are renamed to descriptive names, and the rename
forced a related cleanup of the greenfield flow:

- `gumby` → **`pressure-test`** — the Socratic ticket dialectic.
- `gumby-reconcile` → **`reconcile`** — closes the escalation loop.
- `pokey` → **`to-spec`** — the developer-ready build spec.

`to-spec` was already the name of a *different* skill: the greenfield PRD step that published a spec
to the tracker for `to-tickets` to split. That skill is **retired**, and the greenfield flow
**collapses** to `/interrogate-with-docs → /to-tickets` — `to-tickets` already breaks work down
straight from the conversation, so the separate PRD step wasn't essential. `wayfinder` now hands off
to `/to-tickets`. The spine reads: `ticket → /pressure-test → (/reconcile) → /to-spec`.

This **supersedes** the flow in [ADR-0002](0002-repoint-spine-to-existing-ticket.md) (which named
the entry point `groundwork`, a name that had already been replaced by `gumby`).

## Why

- **Descriptive over cute.** A maintainer or developer reads `/pressure-test` and `/to-spec` and
  knows what each does; `gumby` / `pokey` had to be learned.
- **One `to-spec`, not two overlapping "spec" skills.** The build spec (was pokey) and the old
  greenfield PRD both produced "a spec," blurring the vocabulary. Consolidating to a single
  `to-spec` — the local, Appian-flavored, executable build spec — removes the overload.
- **The greenfield PRD step wasn't pulling its weight.** For a *defined* ticket the spine already
  superseded it; for net-new work, `/to-tickets` breaks the interrogation down directly.

## Consequences

- **A capability is dropped, intentionally:** net-new work no longer produces a published
  umbrella-PRD with an extensive user-story list — the tickets become the artifact. Nothing from
  the retired `to-spec` is preserved.
- The rename is applied **everywhere** the names appeared — skill directories and frontmatter, the
  `which-skill` router, `CLAUDE.md`, both READMEs, `setup`, `orient`, `office`, `domain-modeling`,
  the `outputs/` workspace docs, and this `docs/adr/` set. The `/gumby` and `/pokey` slash-commands
  stop resolving; `gumby` / `pokey` / `gumby-reconcile` are kept as **trigger words** in the new
  skills' descriptions so natural-language "run gumby" still routes during the transition.
- `/to-spec` (was pokey) is **model-invocable**; the retired greenfield `to-spec` was slash-only.
- The maintainer glossary in `CONTEXT.md` is updated to the new spine vocabulary.
