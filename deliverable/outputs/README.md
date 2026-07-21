# outputs — generated planning artifacts (git-ignored)

The advisory skills write their **project artifacts** here — they are *not* committed
(this folder's contents are git-ignored; only this README and `.gitkeep` are tracked).

- **`CONTEXT.md`** — the project-wide glossary / ubiquitous language, maintained by
  `/gumby` and `/domain-modeling`.
- **`<TICKET-KEY>/`** — one folder per ticket (e.g. `IV-207/`), holding that ticket's
  decision record(s)/ADRs (from `/gumby`) and its build spec (`<TICKET-KEY> Spec.md`,
  from `/pokey`). Created on demand.

These are working design artifacts for the developer, not shippable bundle source — which
is why they live outside version control. If your team wants them tracked instead, remove
the `/outputs/*` rule from `.gitignore`.
