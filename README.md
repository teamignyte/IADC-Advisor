# Appian Architect-in-a-Box — Workshop

The development workshop for the **Appian Architect-in-a-Box** product — shipped as the
**`iadc-advisor` Claude Code plugin**, which turns Claude into an advisory Appian architect.

- **The plugin** — what ships to a client — lives entirely under
  [`iadc-advisor/`](iadc-advisor/); this repo doubles as its private marketplace
  (`.claude-plugin/marketplace.json`). The plugin's own README is the user-facing guide.
- **Dev docs** for maintainers live here at the root: `CONTEXT.md` (design vocabulary)
  and `docs/adr/` (decisions).
- **To try the plugin** as a client would, see "Working here" in `CLAUDE.md` — install it
  from this repo as a local marketplace into a scratch repo (never into this repo itself).

Only `iadc-advisor/` is shipped; everything else here is the workshop. See
[docs/adr/0001](docs/adr/0001-deliverable-lives-in-a-subfolder.md) and
[docs/adr/0009](docs/adr/0009-ship-as-claude-code-plugin.md).
