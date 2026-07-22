---
name: setup
description: Configure this Appian architect-in-a-box bundle for a project — wire up the MCP servers and secrets, verify they connect, and set the issue tracker, readiness labels, and domain-doc layout the skills assume. Run once after cloning, before first use of the other skills.
disable-model-invocation: true
---

# Setup

Configure this bundle for the Appian project you're pointing it at. Everything ships as a template with placeholder values; this skill collects the real ones, wires them up, and confirms the bundle is live.

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write. Take it one section at a time — one question, one answer, then the next.

## Process

### 1. Explore

Read the current state; don't assume:

- `.mcp.json` at the repo root — which servers are defined, which values are still `<...>` placeholders.
- `.mcp.json` — does the real (gitignored) file exist yet, or only `.mcp.json.example`?
- `CLAUDE.md` at the repo root — does an `## Agent skills` block already exist?
- `outputs/` (glossary `CONTEXT.md`, `CONTEXT-MAP.md`, `adr/`) and `docs/agents/` — prior domain/config output.
- `git remote -v` — is there a remote, and where?

### 2. Wire the MCP servers

The bundle talks to its data sources through MCP. **Copy `.mcp.json.example` → `.mcp.json`** (gitignored) and fill in **literal** credential values — not `${VAR}`. Literal, because the Windows Desktop app does not reliably expand `${VAR}` in `.mcp.json` (there's a known bug in the `env` block), and a settings `env` block isn't guaranteed to feed `.mcp.json` expansion either. Literal values in a gitignored file are the robust, portable choice; the committed `.mcp.json.example` carries only placeholders, so no secret is ever tracked.

Servers this bundle expects (collect each value with the user, write it into `.mcp.json`):

- **`iadc`** (graph) — HTTP `url` + `appian-api-key` header. Builds and serves a dependency graph for any Appian application.
- **`appian`** (read-only) — stdio `lcp_mcp_server`. Fill `command`/`--directory` (paths to `uv` and the extracted server bundle), and the `env`: `LCP_URL`, `LCP_USERNAME`, `LCP_PASSWORD`. Keep **`LCP_TOOL_MODE: "readonly"`** — inspection only, no mutation.
- **`context7`** — HTTP docs search. Keyless works; add a `CONTEXT7_API_KEY` header only for higher rate limits.
- **Jira** — connected as a **Claude connector** (the Atlassian connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. Jira is **human-first**: the architect reads via the connector and does only light, gated writes. the `jira` and `to-tickets` skills both go through this connector; the project key lives in `docs/agents/issue-tracker.md` (step 4), not an env var.
- **Office / Microsoft 365** — connected as a **Claude connector** (the Microsoft 365 connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. This surface is **read-only**: the `office` skill finds and reads SharePoint/OneDrive documents and Teams/Outlook discussion to ground planning, and never sends, uploads, or edits. Optional — skip if the project has no SharePoint/M365 source docs. (Its pinned source-of-truth folder is a project value — step 3.)

### 3. Set project values

- **Jira project key** (e.g. `IV`) — used by the `jira` and `to-tickets` skills.
- **Appian version** (e.g. `26.6`) — used by `/appian` for version-exact `docs.appian.com` lookups. Write it into the **Configuration block of `appian/SKILL.md`**, which is the single source of truth `/appian` reads — don't leave it to drift from the skill's default.
- **Application identity (graph seed target)** — the Appian application the `iadc` graph is built from. Ask for the **full application name** and any **nicknames** the team uses; get the **application UUID** either by resolving the name via the `appian` MCP (`listApplications`) or from the user directly — both are fine, and this is the one time a live lookup is worth it. Write name, nicknames, and UUID **together** into the **Configuration block of `iadc-graph/SKILL.md`**, so seeding reads the UUID there and never needs the Appian MCP again.
- **Office source-of-truth folder** (only if the Microsoft 365 connector is used) — the SharePoint/OneDrive **site** and the **pinned folder** holding the project's requirements/design docs, so `/office` searches there first instead of the whole tenant. Write it as a **profile row** in the Configuration block of `office/SKILL.md` and set the **Active prospect** line. (Running several prospects from one instance? Add a row per prospect and toggle via that one line.) Skip if the project has no M365 source docs.

### 4. Issue tracker

Where issues live. `jira` (read), `to-tickets`, `to-spec`, and `wayfinder` read from and write to it. Lead with the recommended answer.

Default posture: this bundle is built for a real tracker. If a `git remote` points at GitHub, propose GitHub; if GitLab, propose GitLab; if the project tracks work in **Jira** (the common case here), record that. Options:

- **Jira** — issues live in the project's Jira board, accessed through the **Jira MCP connector** (human-first; read-mostly, light gated writes). Record the project key from step 3.
- **GitHub** — GitHub Issues (`gh` CLI).
- **GitLab** — GitLab Issues (`glab` CLI).
- **Local markdown** — files under `.scratch/<feature>/` (good for a project without a remote tracker).

Record the choice in `docs/agents/issue-tracker.md`, using the matching seed template in this skill folder as a starting point:

- [issue-tracker-jira.md](./issue-tracker-jira.md) — Jira (the common case here; fill `<PROJECT_KEY>` and the workstream label axis — Jira auth is via the connector, so there's no URL to set)
- [issue-tracker-github.md](./issue-tracker-github.md)
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md)
- [issue-tracker-local.md](./issue-tracker-local.md)

Each seed already carries a **"Wayfinding operations"** section — `wayfinder` needs to know how *this* tracker expresses a map issue, child tickets, blocking edges, and a frontier query. For any other tracker (Linear, etc.), write `docs/agents/issue-tracker.md` from the user's description and include that section too.

### 5. Readiness labels

`to-tickets` applies a readiness label when it publishes a breakdown, and `jira` reads these labels to interpret the board. Ask one question:

> Keep the default readiness labels? (recommended: **yes**)

Defaults are five canonical roles: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write [triage-labels.md](./triage-labels.md) as-is. Only if the tracker already uses other names collect the overrides so the skills apply existing labels instead of creating duplicates.

### 6. Domain docs

Default to **single-context** — one `outputs/CONTEXT.md` + `outputs/adr/` in the git-ignored outputs workspace. Offer **multi-context** (an `outputs/CONTEXT-MAP.md` pointing to per-context `CONTEXT.md` files) only if exploration found monorepo signals. Seed the consuming-side config (`docs/agents/domain.md`) from [domain.md](./domain.md).

### 7. Confirm and write

Show the user a draft of the `docs/agents/*.md` files and the `## Agent skills` block for `CLAUDE.md`, and let them edit before writing. If an `## Agent skills` block already exists, update it in place rather than duplicating; don't overwrite surrounding sections.

### 8. Verify the bundle is live

This is the payoff — confirm the configuration actually works, don't just write files:

1. **`.mcp.json` exists** (copied from `.mcp.json.example`), parses as JSON, and has real values filled in — no `<placeholder>` strings left.
2. **Each MCP server handshakes** — list its tools (`iadc`, `appian`, `context7`). For `appian`, confirm it came up in **read-only** mode (mutating/test tools absent). For Jira, confirm the Atlassian connector is connected. For Office (if used), confirm the Microsoft 365 connector is connected (e.g. a `get_me` call).
3. **Skill frontmatter is valid** — every `.claude/skills/*/SKILL.md` has a `name` and `description`.

Report what connected and what didn't, with the specific fix for each failure (missing env var, connector not enabled, wrong endpoint).

### 9. Done

Tell the user setup is complete and which skills now read from these files. They can edit `docs/agents/*.md` and the secrets file directly later — re-run this skill only to switch trackers or re-point the bundle at a different Appian project.
