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
