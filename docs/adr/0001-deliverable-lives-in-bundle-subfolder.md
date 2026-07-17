# The deliverable lives in `bundle/`; the workshop root is the dev environment

Claude Code auto-discovers `CLAUDE.md`, `CONTEXT.md`, and `.claude/skills/` from the
**repo root**, so whoever works in the repo gets the root for free. The maintainers
work in this repo and the client never does (they receive a package), so the root
holds our development environment and the shippable **deliverable** lives entirely
under `bundle/`. Shipping is therefore an allowlist — "only `bundle/` ships" — not a
denylist.

## Considered options

- **Deliverable at root, dev docs in a `dev-docs/` subfolder.** Rejected: Claude Code
  does not auto-discover docs in a subfolder, so the maintainer's own `CONTEXT.md` /
  ADRs — the docs we use most — would be invisible to our agents. It also forced
  `export-ignore` gymnastics to keep them from shipping, and left a root `CONTEXT.md`
  that the bundle's own skills would misread as a client app's glossary.

## Consequences

- Dev docs (`CONTEXT.md`, `docs/adr/`, `for_liam.md`) sit at the root: auto-found, and
  never shipped because they are outside `bundle/`.
- Client **usage docs** are unaffected: `bundle/.gitignore` (secrets + OS cruft only)
  flattens to the client's root, so the client commits their own `CONTEXT.md` / ADRs.
- To test the deliverable as a client sees it, open Claude with `bundle/` as the
  working directory — `bundle/CLAUDE.md` and `bundle/.claude/skills/` then load as root.
- One-time restructure: `git mv` today's root deliverable into `bundle/`, and add the
  dev-facing root files.
