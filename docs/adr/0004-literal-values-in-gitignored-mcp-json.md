# Configure MCP servers with literal values in a gitignored `.mcp.json`, not `${VAR}`

The `appian` server's `.mcp.json` `env` block holds a password, so the credentials have
to reach the MCP process reliably. `${VAR}` expansion in `.mcp.json` was rejected: it
reads only the OS/shell process environment (a `settings.json` `env` block is not
confirmed to feed it), and — decisive here — the **Windows Desktop app has a bug where it
does not expand `${VAR}` in a `.mcp.json` `env` block at all**. This project runs on the
Desktop app, so expansion would silently fail exactly where the secret is needed. So the
real `.mcp.json` holds **literal values and is gitignored**, and a committed
`.mcp.json.example` carries placeholders.

## Consequences

- Secrets live only in the gitignored `.mcp.json` (and `.secrets/` for the deploy PAT) —
  never in a tracked file.
- A maintainer tempted to "clean this up" into `${VAR}` should not: it silently breaks on
  the Windows Desktop app. That is the whole reason this is written down.
- `/setup` copies `.mcp.json.example` → `.mcp.json` and fills in literals; it never
  introduces `${VAR}`.

## Amended by [ADR-0009](0009-ship-as-claude-code-plugin.md)

The decision above still stands, and is load-bearing: the real `.mcp.json` holds **literal
values and is gitignored**, and `${VAR}` is still forbidden for the same Windows Desktop
reason. What changed is **where the template lives and who writes the file**. The product
now ships as a plugin, which cannot place files in the client repo, so there is no
committed `.mcp.json.example` — the template rides inside the plugin as the `/setup` asset
`iadc-advisor/skills/setup/mcp-template.json`, and `/setup` **generates** the client's
`.mcp.json` from it (merging into an existing one rather than overwriting, and establishing
the `.gitignore` entry *before* writing any credential). The last consequence above is
stale only in its mechanism — "copies `.mcp.json.example`" is now "generates from the
template shipped inside the plugin".

The plugin manifest deliberately declares **no** `mcpServers`: these servers span per-app
(graph URL, `LCP_URL`), per-person (Appian credentials), and per-machine (`uv` path) values,
which `userConfig` — one value per machine across all projects — cannot express.

## Amended by IV-442

The `appian` server named above (opening sentence, and `LCP_URL` in the per-app/per-person/
per-machine breakdown just above) no longer exists — Advisor dropped it entirely; no client
repo holds a live Appian credential any more. The underlying decision is unaffected: whatever
secret *does* land in `.mcp.json` still gets a **literal value, not `${VAR}`**, for the same
Windows Desktop reason. What changed is which servers that reaches: today it's an optional
`context7` API key (written by this plugin, keyless by default) and the `iadc` graph's
URL/key (written by the separate `/iadc-graph:setup` skill this ADR doesn't own). The
per-app/per-person/per-machine framing narrows with it — `LCP_URL` and the `uv` path are gone,
and Appian credentials were the only per-person value this plugin ever wrote into this file;
there is none left. `iadc`'s URL and key remain the per-app case the framing still needs.
