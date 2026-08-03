# Appian Architect-in-a-Box — Workshop

The development workshop for the **Appian Architect-in-a-Box** product — shipped as the
**`iadc-advisor` Claude Code plugin**, which turns Claude into an advisory Appian architect.

- **The plugin** — what ships to a client — lives entirely under
  [`iadc-advisor/`](iadc-advisor/). The plugin's own README is the user-facing guide.
  Clients install it from the family catalog,
  [`teamignyte/IADC-Marketplace`](https://github.com/teamignyte/IADC-Marketplace) — not from
  this repo, which is only the workshop.
- **Dev docs** for maintainers live here at the root: `CONTEXT.md` (design vocabulary)
  and `docs/adr/` (decisions).
- **To try the plugin** as a client would, see "Working here" in `CLAUDE.md` — install it
  from the catalog into a scratch repo (never into this repo itself).

Only `iadc-advisor/` is shipped; everything else here is the workshop. See
[docs/adr/0001](docs/adr/0001-deliverable-lives-in-a-subfolder.md) and
[docs/adr/0009](docs/adr/0009-ship-as-claude-code-plugin.md).
