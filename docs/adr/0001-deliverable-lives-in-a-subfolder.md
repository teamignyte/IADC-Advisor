# The deliverable lives in its own `deliverable/` subfolder; the workshop root is the dev environment

Claude Code auto-discovers `CLAUDE.md`, `CONTEXT.md`, and `.claude/skills/` from the
**repo root**, so whoever works in the repo gets the root for free. The maintainers
work in this repo and the client never does (they receive a package), so the root
holds our development environment and the shippable **deliverable** lives entirely
under `deliverable/`. Shipping is therefore an allowlist — "only `deliverable/` ships" — not a
denylist.

## Considered options

- **Deliverable at root, dev docs in a `dev-docs/` subfolder.** Rejected: Claude Code
  does not auto-discover docs in a subfolder, so the maintainer's own `CONTEXT.md` /
  ADRs — the docs we use most — would be invisible to our agents. It also forced
  `export-ignore` gymnastics to keep them from shipping, and left a root `CONTEXT.md`
  that the bundle's own skills would misread as a client app's glossary.

## Consequences

- Dev docs (`CONTEXT.md` and `docs/adr/`) sit at the root: auto-found, and
  never shipped because they are outside `deliverable/`.
- Client **usage docs** are unaffected: `deliverable/.gitignore` (secrets + OS cruft only)
  flattens to the client's root, so the client commits their own `CONTEXT.md` / ADRs.
- To test the deliverable as a client sees it, open Claude with `deliverable/` as the
  working directory — `deliverable/CLAUDE.md` and `deliverable/.claude/skills/` then load as root.
- One-time restructure: `git mv` today's root deliverable into `deliverable/`, and add the
  dev-facing root files.

## Amended by [ADR-0009](0009-ship-as-claude-code-plugin.md)

The decision above still stands in its core: the product lives in **its own subfolder** and the
workshop root is the maintainers' dev environment, so shipping stays an **allowlist**. What
changed is the folder, the mechanism, and everything downstream of "the client receives a
package".

- **The folder is `iadc-advisor/`**, not `deliverable/` — a Claude Code **plugin**, not a
  copied bundle. Read "only `deliverable/` ships" as "only `iadc-advisor/` ships".
- **The allowlist is enforced by the marketplace `source`**, not by copying: this repo's
  `.claude-plugin/marketplace.json` points at `iadc-advisor/`, and nothing outside it is
  distributed.
- **Nothing is copied or flattened into the client repo.** There is no shipped `.gitignore`
  and no shipped `CLAUDE.md` (plugins cannot load one — the operating posture arrives through
  the SessionStart hook). So the second consequence above is stale twice over: nothing
  "flattens to the client's root", and per
  [ADR-0005](0005-generated-artifacts-live-in-a-gitignored-outputs-workspace.md) the client's
  glossary and ADRs are **generated into the git-ignored `outputs/` workspace** that `/setup`
  writes — not committed usage docs. The per-project state the client does hold (`.mcp.json`,
  `docs/agents/*.md`, `.gitignore` entries, `outputs/`) is written by `/setup`, not shipped.
- **Dogfooding is retired as written.** Opening Claude with the product folder as the working
  directory no longer tests anything: install the plugin from this repo as a **local-path
  marketplace** into a scratch client repo (a sibling of this repo, never inside it), and run
  it there. See `CLAUDE.md` → "Working here".
