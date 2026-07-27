---
name: setup
description: Configure the iadc-advisor plugin for this Appian project — write the per-project state into this repo (MCP servers + secrets, project configuration, issue tracker, domain docs), verify everything connects. Run once per app repo after installing the plugin, before first use of the other skills.
disable-model-invocation: true
---

# Setup

Configure the plugin for the Appian project you're pointing it at. The plugin itself is installed out of this repo, in a shared cache that is read-only and replaced on every update — so it holds **no** per-project values and can ship **no** files here. This skill is what materializes them: it collects the real values and **generates** the per-project state in this repo, then confirms every connection is live.

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write. Take it one section at a time — one question, one answer, then the next.

## Process

### 1. Explore

Read the current state; don't assume:

- The plugin is installed at **project scope**: `.claude/settings.json` in this repo
  enables `iadc-advisor` (it's how this skill is running — verify, don't assume).
- `.mcp.json` at the repo root — exists? which servers, which values still placeholders?
- `docs/agents/` — `project.md`, `project.local.md`, `issue-tracker.md`,
  `triage-labels.md`, `domain.md` — which exist from a prior run?
- `outputs/` — does the workspace exist yet?
- `.gitignore` — does it have the entries listed in step 2c?
- `git remote -v` — is there a remote, and where?

### 2. Wire the MCP servers

The plugin talks to its data sources through MCP, configured **in this repo**, not in the
plugin. **Generate `.mcp.json` at the repo root from this skill's
[mcp-template.json](./mcp-template.json)** and fill in **literal** credential values —
not `${VAR}` (the Windows Desktop app does not reliably expand `${VAR}` in `.mcp.json`).
`.mcp.json` is gitignored (step 2c) so no secret is ever tracked; the template stays in
the plugin.

This is an existing app repo, not a fresh clone — respect what's already there:

- **`.mcp.json` already exists** → **merge, never overwrite**: add or update only the
  `iadc`, `appian`, and `context7` entries; preserve every other server the team has
  configured. Show the diff before writing.
- **`.mcp.json` is tracked in git** (`git ls-files --error-unmatch .mcp.json` succeeds) →
  stop and surface it: the team has committed it deliberately. Propose
  `git rm --cached .mcp.json` + the gitignore entry so credentials stop being tracked,
  but make no git change without an explicit yes — if they decline, warn that literal
  credentials must then never go in it, and record where the team wants secrets instead.

Servers this plugin expects (collect each value with the user, write it into `.mcp.json`):

- **`iadc`** (graph) — HTTP `url` + `appian-api-key` header. Builds and serves a dependency graph for any Appian application.
- **`appian`** (read-only) — stdio `lcp_mcp_server`. Fill `command`/`--directory` (paths to `uv` and the extracted server bundle), and the `env`: `LCP_URL`, `LCP_USERNAME`, `LCP_PASSWORD`. Keep **`LCP_TOOL_MODE: "readonly"`** — inspection only, no mutation.
- **`context7`** — HTTP docs search. Keyless works; add a `CONTEXT7_API_KEY` header only for higher rate limits.
- **Jira** — connected as a **Claude connector** (the Atlassian connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. Jira is **human-first**: the architect reads via the connector and does only light, gated writes. the `jira` and `to-tickets` skills both go through this connector; the project key lives in `docs/agents/issue-tracker.md` (step 4), not an env var.
- **Office / Microsoft 365** — connected as a **Claude connector** (the Microsoft 365 connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. This surface is **read-only**: the `office` skill finds and reads SharePoint/OneDrive documents and Teams/Outlook discussion to ground planning, and never sends, uploads, or edits. Optional — if the project has no SharePoint/M365 source docs, leave the connector alone and record the deliberate `none` answer in step 3, so `/office` stops asking. (Its pinned source-of-truth folder is a project value — step 3.)
- **Slack** — connected as a **Claude connector** (not in `.mcp.json`). Used only for **escalation**: `/pressure-test` can draft and — **gated** (propose → confirm → send) — send an architectural-gap question to the project lead's Slack channel. Point the user at their client's connector settings. Optional — skip if escalations go via a Jira comment or by handing the drafted text to the builder.

### 2c. Materialize the workspace and ignores

The plugin can't ship files into this repo, so create them here (idempotently — leave
existing content alone):

- **`outputs/`** — create the folder, write [outputs-readme.md](./outputs-readme.md) to
  `outputs/README.md`, and `touch outputs/.gitkeep`.
- **`.gitignore`** — ensure these entries exist (append any that are missing):

  ```
  # iadc-advisor per-project state — secrets and personal overrides, never committed
  .mcp.json
  docs/agents/project.local.md
  # generated planning artifacts (glossary, ADRs, specs) — working files, not source
  /outputs/*
  !/outputs/.gitkeep
  !/outputs/README.md
  ```

### 3. Set project values

Collect these and write them into **`docs/agents/project.md`**, from this skill's
[project-config-template.md](./project-config-template.md) — never into any `SKILL.md`
(plugin skills are shared, read-only, and replaced on update; workshop ADR 0010). That
file is the whole per-project schema: the session hook injects it verbatim as the ambient
**Project configuration**, and six skills read it.

**Keep the template's field labels verbatim** — `Audience`, `Appian version`,
`Application` (+ `Nicknames`, `UUID`), `Escalation` (+ `Project lead`),
`Office source of truth` (+ `Row`, `Active prospect`) — and keep its
*How to fill these in* paragraph. The skills match on those exact labels; rename or
reword one and the value simply stops being found.

Fill every value **in place**, replacing the `<...>` placeholder with a real answer — and
where a field doesn't apply, write the **deliberate** answer the template names (`none`
for `Office source of truth` and for an empty `Nicknames`, `hand-off` for `Escalation`)
rather than skipping it. A placeholder left standing is how a skill knows a field is
genuinely unset, so it will ask again every session; that is the nag `/setup` exists to
prevent. Never invent a value, and never delete a line unless the template says to.

- **Jira project key** (e.g. `IV`) — the one value that is *not* a `project.md` field: it
  belongs in `docs/agents/issue-tracker.md` (step 4), where the `jira` and `to-tickets`
  skills read it.
- **`Appian version`** (e.g. `26.6`) — a bare version string, no trailing note. `/appian`
  and `/context7` read this line for version-exact `docs.appian.com` lookups; it is the
  single source of truth, so don't leave it to drift from a skill's fallback default.
- **`Application`** — the Appian application the `iadc` graph is seeded from: its **full
  name** on `Application`, the team's shorthand on **`Nicknames`**, and the **`UUID`**.
  Resolve the UUID via the `appian` MCP (`listApplications`) or take it from the user —
  this is the one time a live lookup is worth it. Recorded here, seeding reads the UUID
  from the configuration and never needs the Appian MCP again.
- **`Office source of truth`** (+ **`Row`**, **`Active prospect`**) — the SharePoint/OneDrive
  **site** and **pinned folder** holding this project's requirements/design docs, so
  `/office` searches there first instead of the whole tenant. Keep the template's shipped
  value `rows below`, fill the `Row:` line (prospect name, site, folder) and name the live
  one on `Active prospect:`; tracking more than one prospect in this repo, duplicate the
  `Row:` line per prospect — that one `Active prospect` line is then the whole toggle.
  **If this project has no M365 source documents, write the bare word `none` on the
  `Office source of truth` line and delete the `Row:` and `Active prospect:` lines** — do
  not skip the field and do not leave the placeholder. `none` is the deliberate answer
  that tells `/office` to stop searching SharePoint/OneDrive; a placeholder left standing
  only makes it ask again every session.
- **`Audience`** — who the advisor is talking to: **`developer`** (the default — the person
  who will build the ticket), or `lead`/`architect` if the primary user owns architectural
  decisions. The operating posture reads this line; it shapes how `/pressure-test` pitches
  questions and whether it escalates gaps or asks the user directly.
- **`Escalation`** (+ **`Project lead`**) — where `/pressure-test` sends an architectural
  gap: the channel (`Slack` | `Jira comment` | `hand-off`) and the lead (Slack
  channel/handle, or Jira account). **No one to escalate to** — a lead/architect audience,
  say? Write **`hand-off`**, the deliberate "hand me the drafted text and I'll send it"
  answer, which needs no `Project lead`. Same rule as the field above: a written answer,
  never a placeholder left standing.

**Per-person override:** ask whether this user's role differs from the repo default
(e.g. a lead in a `developer`-default repo). If so, write just the differing lines to
**`docs/agents/project.local.md`** (gitignored — step 2c): same field names; the session
hook injects it after `project.md`, so its values win. Any teammate can do the same on
their machine without touching the committed default.

### 4. Issue tracker

Where issues live. `jira` (read), `to-tickets`, and `wayfinder` read from and write to it. Lead with the recommended answer.

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

Show the user a draft of every file this run will write — `docs/agents/project.md` first, then `issue-tracker.md`, `triage-labels.md`, `domain.md`, and `project.local.md` if there's a personal override — and let them edit before anything lands. Merge into files that already exist rather than clobbering them, and don't touch surrounding content. The client's `CLAUDE.md` is theirs: this skill writes nothing into it and needs nothing from it — the plugin's operating posture arrives through its session hook.

### 8. Verify the plugin is live

This is the payoff — confirm the configuration actually works, don't just write files:

1. **`.mcp.json` exists** (generated from the template), parses as JSON, has no
   `<placeholder>` strings left, and is matched by a `.gitignore` entry
   (`git check-ignore .mcp.json` succeeds).
2. **Each MCP server handshakes** — list its tools (`iadc`, `appian`, `context7`). For `appian`, confirm it came up in **read-only** mode (mutating/test tools absent). For Jira, confirm the Atlassian connector is connected. For Office (if used), confirm the Microsoft 365 connector is connected (e.g. a `get_me` call). For Slack (if used for escalation), confirm the Slack connector is connected.
3. **Project configuration is live** — `docs/agents/project.md` exists with no
   placeholders; if `project.local.md` was written, `git check-ignore` confirms it's
   ignored.
4. **The session hook fires** — tell the user to start a fresh session in this repo and
   confirm the "iadc-advisor — operating posture" and "Project configuration" sections
   appear at the top of context.

Report what connected and what didn't, with the specific fix for each failure (missing env var, connector not enabled, wrong endpoint).

### 9. Done

Tell the user setup is complete and which skills now read from these files. They can edit `docs/agents/*.md` and the gitignored `.mcp.json` directly later — re-run this skill only to switch trackers or re-point the plugin at a different Appian project.
