# Changelog — iadc-advisor

## 1.3.0 — 2026-08-03

Per-project state files are renamed to match the plugin that owns them, ahead of the Tester
shipping its own alongside.

- **Action required for existing installs:** `docs/agents/project.md` / `project.local.md` are
  now `docs/agents/advisor.md` / `advisor.local.md` — a generic name would have read as
  family-wide configuration once the Tester ships `tester.md` alongside it. Re-run
  `/iadc-advisor:setup`: it detects the old files and offers to rename them in place, carrying
  their values over rather than re-asking, and fixes the matching `.gitignore` line. It also now
  asks for any field the template has gained since your install ran — `Row`, on a file this old
  — instead of reporting the migrated file complete with one missing outright.
- **`/iadc-advisor:setup` no longer writes the `iadc` (graph) entry.** It now tells the user to
  run `/iadc-graph:setup` instead — installed automatically as this plugin's dependency, and now
  the one place in the family that writes that credential (family ADR 0010). This plugin keeps
  only `appian` and `context7`, the entries that are its own. It can be run any time, before or
  after this one, and never disturbs an existing install: `/iadc-graph:setup` never silently
  overwrites a working `iadc` entry, so a repo that ran the old setup keeps what it already has
  unless the user chooses otherwise.

## 1.2.0 — 2026-08-03

This plugin is now distributed from the family catalog rather than from its own repo, and it no
longer carries its own copy of the `iadc-graph` skill.

- **Action required for existing installs:** the marketplace moved. Re-add it, pointing at the
  catalog rather than at this plugin's repo:
  `claude plugin marketplace add https://github.com/teamignyte/IADC-Marketplace.git --scope project`,
  then reinstall. Installing from the old URL will stop resolving.
- **`iadc-graph` is now a separate plugin, installed automatically** as a dependency of this one.
  You do not install it yourself, and there is no longer a copy inside this plugin to fall out of
  step with the deployed server. The single mirror lives in the catalog, still taken at the sha
  that built the deployed graph image.
- **The graph skill is now addressed `/iadc-graph:iadc-graph`** — the skill `iadc-graph` inside the
  plugin `iadc-graph`. The doubled name is correct, not a typo. Every reference in this plugin's
  skills was updated.
- To install the whole suite — this plugin plus Selenium test generation — install `iadc@ignyte`
  instead, which pulls in both.

## 1.1.0 — 2026-07-31

The IADC graph MCP moved to its own service, so this release repoints clients at it and
refreshes the `iadc-graph` skill to match the deployed server.

- **Action required for existing installs:** the graph MCP is now served on port **8001** by a
  standalone Graph service, over **`http`**. An existing `.mcp.json` pointing at
  `https://<host>:8000/mcp/` stops working — 8000 no longer serves `/mcp` at all, and `https`
  fails the handshake against a cleartext endpoint. Re-run `/iadc-advisor:setup`, or edit the `iadc` server's
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
- `/iadc-advisor:setup` now materializes all per-project state: `.mcp.json`, project configuration,
  tracker/domain docs, `outputs/`, `.gitignore` entries.
- No per-project values live in skill files anymore.
- Fixed the plugin loading nothing on install: the manifest must **not** declare `skills` or
  `hooks` — both are auto-discovered, and declaring them too made every install report
  `✘ failed to load — Duplicate hooks file detected` (no skills, no session hook).
