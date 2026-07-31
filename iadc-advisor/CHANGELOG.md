# Changelog — iadc-advisor

## 1.1.0 — 2026-07-31

The IADC graph MCP moved to its own service, so this release repoints clients at it and
refreshes the `iadc-graph` skill to match the deployed server.

- **Action required for existing installs:** the graph MCP is now served on port **8001** by a
  standalone Graph service, over **`http`**. An existing `.mcp.json` pointing at
  `https://<host>:8000/mcp/` stops working — 8000 no longer serves `/mcp` at all, and `https`
  fails the handshake against a cleartext endpoint. Re-run `/setup`, or edit the `iadc` server's
  `url` to `http://<your-graph-host>:8001/mcp/`.
- `iadc-graph` skill refreshed to a **byte-identical** copy of IADC's canonical skill at the sha
  that built the deployed graph image (`6dc3999`), replacing a stale fork. It now documents all
  **18** server tools — previously 17, missing `get_sail` — verified against the deployed
  server's live tool list rather than against IADC `HEAD`.
- The skill's seed-target guidance is now upstream rather than a local patch: it reads the
  Application UUID from the ambient Project configuration where one exists, and falls through to
  an ordinary lookup where none does. Behaviour for clients is unchanged; it is no longer a
  divergence that a refresh could silently revert.
- Recorded the vendoring contract in `docs/vendored-iadc-graph-skill.md` and ADR 0011: refresh
  from the **deployed** sha, never from `HEAD` — the skill may lag the server, never lead it.

## 1.0.0 — 2026-07-26

First release as a Claude Code plugin (previously installed by copying files into the
app repo — no migration path; this is a clean break).

- Install from the `ignyte` marketplace at **project scope**, per Appian-app repo.
- Session hook injects the operating posture + `docs/agents/project.md`
  (+ personal `project.local.md` override — per-person Audience).
- `/setup` now materializes all per-project state: `.mcp.json`, project configuration,
  tracker/domain docs, `outputs/`, `.gitignore` entries.
- No per-project values live in skill files anymore.
- Fixed the plugin loading nothing on install: the manifest must **not** declare `skills` or
  `hooks` — both are auto-discovered, and declaring them too made every install report
  `✘ failed to load — Duplicate hooks file detected` (no skills, no session hook).
