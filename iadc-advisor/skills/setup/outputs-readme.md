# outputs — generated planning artifacts (git-ignored)

The advisory skills write their **project artifacts** here — they are *not* committed
(this folder's contents are git-ignored; only this README and `.gitkeep` are tracked).

- **`CONTEXT.md`** — the project-wide glossary / ubiquitous language, maintained by
  `/pressure-test` and `/domain-modeling`.
- **`adr/`** — the **chronological decision history**: one lightweight, project-wide
  sequentially-numbered ADR (`NNNN-slug.md`) per substantive decision, in the order made.
- **`<TICKET-KEY>/`** — one folder per ticket (e.g. `IV-207/`), holding that ticket's
  **`decisions.md`** (the rollup — status + resolved decisions, each linking its ADR — plus
  open/escalated items) and its build spec (`<TICKET-KEY> Spec.md`, from `/to-spec`). Created on demand.

These are working design artifacts for the developer, not committed project files — which
is why they live outside version control. If your team wants them tracked instead, remove
the `outputs/` entries `/setup` added to `.gitignore`.
