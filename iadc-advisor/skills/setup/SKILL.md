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

- The plugin is **enabled for this repo** — that much is given, it's how this skill is
  running. What's worth checking is *where*: project scope (`.claude/settings.json`,
  committed) is the one every teammate inherits, while `.claude/settings.local.json` or the
  user's own settings enable it on this machine only. If it isn't enabled at project scope,
  don't treat that as a failure — say where it *is* enabled, and offer to add it at project
  scope so the rest of the team gets the plugin too.
- `.mcp.json` at the repo root — exists? which servers, which values still placeholders?
  Is it **tracked** (`git ls-files --error-unmatch .mcp.json` succeeds)?
  **Redaction rule — it holds for the whole run, starting with this first read:** never print
  a credential value back into the transcript. Report the file's *shape* — server entries and
  key names, `••••` where a secret sits — never its secret contents. This matters most right
  here: on a re-run the file you are reading is already filled in with live values. Every
  later place this skill shows `.mcp.json` (the merge diff in step 3, the review in step 8)
  means this rule.
- `docs/agents/` — `project.md`, `project.local.md`, `issue-tracker.md`,
  `triage-labels.md`, `domain.md` — which exist from a prior run?
- `outputs/` — does the workspace exist yet?
- `.gitignore` — does it have the entries listed in step 2?
- `git remote -v` — is there a remote, and where?

### 2. Establish the ignore rules and the workspace

**This step runs before anything writes a credential.** Step 3 puts a literal Appian password
and API keys into `.mcp.json` at the repo root; **the ignore rules must exist before any
credential is written**, or a `git add -A` in the gap between the two stages the secret. That
ordering is the reason this step comes first, not a formality.

The plugin can't ship files into this repo, so create them here (idempotently — leave
existing content alone):

- **`.gitignore`** — these entries must exist:

  ```
  # iadc-advisor per-project state — secrets and personal overrides, never committed
  .mcp.json
  docs/agents/project.local.md
  # generated planning artifacts (glossary, ADRs, specs) — working files, not source
  /outputs/*
  !/outputs/README.md
  ```

  Show the user exactly which of these lines are missing and **get an explicit yes before you
  append them** — the `.gitignore` is theirs, and it's a committed file. If they decline,
  append nothing and don't ask again (one narrow exception, spelled out in step 3: if the user
  there agrees to `git rm --cached` a tracked `.mcp.json`, that changes the facts this refusal
  was made against, so that single re-ask is legitimate — and a second decline is final). Tell
  them plainly what follows — the decline reaches every piece of per-project state this run
  would write, not just the secrets:

  - **`.mcp.json`** stays placeholder-valued (step 3), because this skill does not write
    credentials into a repo that doesn't ignore them.
  - **The `outputs/` workspace** below is still created, but **don't write
    `outputs/README.md`**: its opening line says the folder's contents are git-ignored, which
    would be false in this repo. Say that out loud instead, and let the team decide.
  - **A personal override** in `docs/agents/project.local.md` (step 4) would be a trackable
    file. Only write one if the user says yes knowing that.

  Step 9 expects `git check-ignore` to fail on all of these here, and reports them as
  deliberately unignored rather than broken.

  **Edge case — `outputs/` already excluded as a directory.** If their `.gitignore` already
  has a bare `outputs/` or `/outputs/` rule (no trailing `*`), git never descends into the
  folder, and **no appended negation can re-include `outputs/README.md`**. Don't append one
  that cannot take effect — surface it instead: the fix is to change their existing rule to
  `/outputs/*`, and that call is theirs, not yours. This reaches the README below as well: in
  that repo the README is itself ignored, so it can't be committed without `git add -f`, and
  its own line saying it is the tracked file that keeps the folder in git would be false.

- **`outputs/`** — create the folder if it isn't there. **If `outputs/README.md` does not
  already exist**, show the user [outputs-readme.md](./outputs-readme.md) and **get an
  explicit yes before you write it** — same gate as the `.gitignore` above and for the same
  reason: it is a committed file newly appearing in their repo. **In the bare-`outputs/` repo
  above, say so as you offer it**: there the README lands ignored and untrackable until they
  change that rule, so the real decision in front of them is the rule, not the README. If it
  does exist, leave it exactly as the team has it. If they decline it, write nothing and carry
  on — the workspace itself works either way; that tracked README is only what keeps the folder
  in git and documents what lands there, and nothing else needs it.

### 3. Wire the MCP servers

The plugin talks to its data sources through MCP, configured **in this repo**, not in the
plugin. **Generate `.mcp.json` at the repo root from this skill's
[mcp-template.json](./mcp-template.json)** and fill in **literal** credential values —
not `${VAR}` (the Windows Desktop app does not reliably expand `${VAR}` in `.mcp.json`) —
unless a guard below stops you. **Drop every `_comment` key as you write**: they are notes to
you about the template, never configuration, and they must not appear in the real file. The
ignore rules from step 2 must already be in place before you write a credential. If they
aren't **because you skipped ahead**, go back and settle step 2 now. If they aren't **because
the user declined them**, don't re-ask and don't append them anyway — that answer stands.
Produce the outcome step 2 named instead: generate `.mcp.json` — **merging** into it rather
than clobbering it if one is already there, per the merge rule below — with every
`<placeholder>` left standing, write **no** credential value into it, and hand the values off
exactly the way the decline branch below does. With the rules in place `.mcp.json` is
gitignored and no secret is ever tracked; the template stays in the plugin.

This is an existing app repo, not a fresh clone — respect what's already there. Take these two
in order, the tracked check **first**, before you write anything:

- **`.mcp.json` is tracked in git** (`git ls-files --error-unmatch .mcp.json` succeeds) →
  stop and surface it: the team has committed it deliberately, and a **tracked file is never
  ignored**, whatever `.gitignore` says. Propose `git rm --cached .mcp.json` (step 2's entry
  then takes effect) so credentials stop being tracked, but make no git change without an
  explicit yes.
  - **They agree** → run it, then check `git check-ignore .mcp.json`. Both outcomes are
    reachable, so read which one you got before writing anything:
    - **It succeeds** → the file is untracked *and* ignored — but only in the **index**, and
      that is not yet durable. `git rm --cached` removed the index entry and nothing more:
      **HEAD still carries the file**, so any operation that restores the index (`git reset`,
      `git restore --staged .mcp.json`, `git stash`) puts it back to **tracked**, where no
      `.gitignore` line can reach it and the next `git add -A` would stage the password you
      are about to write. So the staged deletion has to be **committed before you write any
      credential** — say that plainly, show `git status` so they can see it pending, and
      **offer to commit it now** (run it only on their yes, like every other git change
      here). Only once that removal is committed do you carry on below with literal values.
      If they'd rather commit it themselves, that's fine — then write **no** credential
      value this run: leave the placeholders standing, tell them which values are still
      needed, and re-show the pending deletion in step 8 so it isn't forgotten.
    - **It still fails** → step 2's `.mcp.json` entry was never added (the user declined the
      append, or it got skipped), and an untracked file with no matching rule is not ignored.
      **Write no credential value.** Say what just changed and why it matters: `git rm
      --cached` staged the file's deletion, so the next `git add -A` would re-add whatever it
      holds as a fresh blob — writing a password now would leave the repo *worse* off than
      when this step started. Then either settle step 2 and re-check (this is the first ask
      about that rule since the file became untracked, not a re-nag of a refusal), or, if
      they decline again, take the decline branch below as written: placeholders standing,
      values handed off, nothing secret in the file. On that second decline, don't leave the
      repo mid-operation either — this step is what staged the deletion, so offer
      `git restore --staged .mcp.json` to put it back, and run it only on their yes, like
      every other git change here.
  - **They decline** → **this step ends here for `.mcp.json`.** Write **no** credential value
    into a tracked file — not the password, not an API key, not "just the URL and username".
    Leave every `<placeholder>` standing exactly as it is. Then tell the user which values are
    still needed, named one by one (`iadc`: `url` + `appian-api-key`; `appian`: `command`,
    `--directory`, `LCP_URL`, `LCP_USERNAME`, `LCP_PASSWORD`; `context7`: nothing unless they
    want a key), and that those have to go wherever they told you their team keeps secrets —
    outside this repo. Skip only the rest of this step's `.mcp.json` write-up (the merge
    bullet and the three server-value bullets); **still walk the connector bullets** — Jira,
    Office, Slack — with the user, since those are Claude connectors that hold no credential
    in this repo, and Office's deliberate `none` still gets recorded in step 4. Then move on
    to step 4. Step 9 will report `.mcp.json` as deliberately unconfigured; that is the
    correct outcome, not a failure to paper over.
- **`.mcp.json` already exists** (and the check above cleared) → **merge, never overwrite**:
  add or update only the `iadc`, `appian`, and `context7` entries; preserve every other server
  the team has configured. Show the diff before writing, redacted per the redaction rule in
  step 1.

Servers this plugin expects — collect each value with the user and write it into `.mcp.json`,
**unless the user declined step 2's ignore rules (the stop at the top of this step) or one of
the two guards above stopped you**, in which case the `<placeholder>` stays and the value is
handed off instead of written. **Before the first literal value goes in, confirm the rule
actually bites: `git check-ignore .mcp.json` must succeed.** The tracked branch above already
reads that check; on the ordinary paths it is what turns "we appended the line" into "the line
takes effect". If it fails, write no credential — go back and settle step 2, then re-check.

- **`iadc`** (graph) — HTTP `url` + `appian-api-key` header. Builds and serves a dependency graph for any Appian application.
- **`appian`** (read-only) — stdio `lcp_mcp_server`. Fill `command`/`--directory` (paths to `uv` and the extracted server bundle), and the `env`: `LCP_URL`, `LCP_USERNAME`, `LCP_PASSWORD`. Keep **`LCP_TOOL_MODE: "readonly"`** — inspection only, no mutation.
- **`context7`** — HTTP docs search. Keyless works, which is why the template ships **no `headers` block** for it; add one carrying `CONTEXT7_API_KEY` only if the team has a key and wants the higher rate limits.
- **Jira** — connected as a **Claude connector** (the Atlassian connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. Jira is **human-first**: the architect reads via the connector and does only light, gated writes. the `jira` and `to-tickets` skills both go through this connector; the project key lives in `docs/agents/issue-tracker.md` (step 5), not an env var.
- **Office / Microsoft 365** — connected as a **Claude connector** (the Microsoft 365 connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. This surface is **read-only**: the `office` skill finds and reads SharePoint/OneDrive documents and Teams/Outlook discussion to ground planning, and never sends, uploads, or edits. Optional — if the project has no SharePoint/M365 source docs, leave the connector alone and record the deliberate `none` answer in step 4, so `/office` stops asking. (Its pinned source-of-truth folder is a project value — step 4.)
- **Slack** — connected as a **Claude connector** (not in `.mcp.json`). Used only for **escalation**: `/pressure-test` can draft and — **gated** (propose → confirm → send) — send an architectural-gap question to the project lead's Slack channel. Point the user at their client's connector settings. Optional — skip if escalations go via a Jira comment or by handing the drafted text to the builder.

### 4. Set project values

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
for `Office source of truth`, `hand-off` for `Escalation`) rather than skipping it. A
placeholder left standing is how a skill knows a field is genuinely unset, so it will ask
again every session; that is the nag `/setup` exists to prevent. Never invent a value, and
never delete a line unless the template says to.

- **Jira project key** (e.g. `IV`) — the one value that is *not* a `project.md` field: it
  belongs in `docs/agents/issue-tracker.md` (step 5), where the `jira` and `to-tickets`
  skills read it.
- **`Appian version`** (e.g. `26.6`) — a bare version string, no trailing note. `/appian`
  and `/context7` read this line for version-exact `docs.appian.com` lookups; it is the
  single source of truth, so don't leave it to drift from a skill's fallback default.
- **`Application`** — the Appian application the `iadc` graph is seeded from: its **full
  name** on `Application`, the team's shorthand on **`Nicknames`**, and the **`UUID`**.
  Resolve the UUID via the `appian` MCP (`listApplications`) or take it from the user —
  this is the one time a live lookup is worth it. Recorded here, seeding reads the UUID
  from the configuration and never needs the Appian MCP again. `Nicknames` is genuinely
  optional and has **no deliberate-answer sentinel**: write the shorthands the team actually
  uses, and if they have none, leave that one line's placeholder standing rather than writing
  a word like `none` into it, which would only seed a fake nickname. Nothing nags about an
  unfilled `Nicknames`.
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
  never a placeholder left standing. **On `hand-off`, the `Project lead` line stays exactly
  as the template ships it, placeholder and all** — unlike the Office branch above, nothing
  is deleted here, because the template doesn't say to and `/pressure-test` reads an unset
  `Project lead` as expected under `hand-off`. Any other channel needs a real `Project lead`,
  since that's who the escalation goes to.

**Per-person override:** ask whether this user's role differs from the repo default
(e.g. a lead in a `developer`-default repo). If so, write just the differing lines to
**`docs/agents/project.local.md`** (gitignored by step 2's entry — unless the user declined
that append, in which case take the decline branch there before writing one): same field
names; the session
hook injects it after `project.md`, so its values win. Any teammate can do the same on
their machine without touching the committed default.

### 5. Issue tracker

Where issues live. `jira` (read), `to-tickets`, and `wayfinder` read from and write to it. Lead with the recommended answer.

Default posture: this plugin is built for a real tracker. If a `git remote` points at GitHub, propose GitHub; if GitLab, propose GitLab; if the project tracks work in **Jira** (the common case here), record that. Options:

- **Jira** — issues live in the project's Jira board, accessed through the **Jira MCP connector** (human-first; read-mostly, light gated writes). Record the project key from step 4.
- **GitHub** — GitHub Issues (`gh` CLI).
- **GitLab** — GitLab Issues (`glab` CLI).
- **Local markdown** — files under `.scratch/<feature>/` (good for a project without a remote tracker).

Record the choice in `docs/agents/issue-tracker.md`, using the matching seed template in this skill folder as a starting point:

- [issue-tracker-jira.md](./issue-tracker-jira.md) — Jira (the common case here; fill `<PROJECT_KEY>` and the workstream label axis — Jira auth is via the connector, so there's no URL to set)
- [issue-tracker-github.md](./issue-tracker-github.md)
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md)
- [issue-tracker-local.md](./issue-tracker-local.md)

Each seed already carries a **"Wayfinding operations"** section — `wayfinder` needs to know how *this* tracker expresses a map issue, child tickets, blocking edges, and a frontier query. For any other tracker (Linear, etc.), write `docs/agents/issue-tracker.md` from the user's description and include that section too.

### 6. Readiness labels

`to-tickets` applies a readiness label when it publishes a breakdown, and `jira` reads these labels to interpret the board. Ask one question:

> Keep the default readiness labels? (recommended: **yes**)

Defaults are five canonical roles: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write [triage-labels.md](./triage-labels.md) as-is. Only if the tracker already uses other names collect the overrides so the skills apply existing labels instead of creating duplicates.

### 7. Domain docs

Default to **single-context** — one `outputs/CONTEXT.md` + `outputs/adr/` in the `outputs/` workspace (git-ignored, unless the user declined step 2's rules). Offer **multi-context** (an `outputs/CONTEXT-MAP.md` pointing to per-context `CONTEXT.md` files) only if exploration found monorepo signals. Seed the consuming-side config (`docs/agents/domain.md`) from [domain.md](./domain.md).

### 8. Review everything this run touched

Writes happen **inline**: each section above shows its draft, takes the user's edits, and
writes on their confirmation — nothing lands unconfirmed, and nothing is held back to the end.
This step is the review gate over the finished state: re-show, in one place, everything the run
touched, so the user sees the whole shape of it and can correct anything before you call setup
done.

- **`.mcp.json`** — **redacted per the redaction rule in step 1** (server entries and key
  names, `••••` where a secret sits), or a note that it was deliberately left
  placeholder-valued (step 3).
- **Any pending `git rm --cached` deletion still to be committed** (step 3) — if this run
  untracked `.mcp.json`, that removal is only *staged*. Say so here: until it is committed the
  file can come back tracked, carrying whatever credentials were just written into it.
- **The `.gitignore` diff** — the exact lines step 2 appended, or that they were already there,
  or that the user declined them.
- **`outputs/`** — created or already present, and whether `README.md` was written, left as
  the team had it, declined, or withheld by this skill because the ignore rules were declined
  (step 2).
- **`docs/agents/project.md`** first, then `issue-tracker.md`, `triage-labels.md`, `domain.md`,
  and `project.local.md` if there's a personal override.

Merge into files that already exist rather than clobbering them, and don't touch surrounding content. The client's `CLAUDE.md` is theirs: this skill writes nothing into it and needs nothing from it — the plugin's operating posture arrives through its session hook.

### 9. Verify the plugin is live

This is the payoff — confirm the configuration actually works, don't just write files:

1. **`.mcp.json` is configured and ignored** — it exists (generated from the template), parses
   as JSON, carries no `<placeholder>` string and no `_comment` key, and is matched by a
   `.gitignore` entry (`git check-ignore .mcp.json` succeeds). If `check-ignore` fails,
   diagnose before you fix: run `git ls-files --error-unmatch .mcp.json` — if **that** succeeds
   the file is **tracked**, and no `.gitignore` line can ignore a tracked file, so the fix is
   `git rm --cached .mcp.json` (with the user's yes), not another entry; only when it's
   untracked is a missing `.gitignore` entry the explanation. If the user declined the ignore
   entries (step 2) or the `git rm --cached` (step 3), report `.mcp.json` as **deliberately
   unconfigured** with the list of values they still owe — don't call that a failure and don't
   quietly fill it in now.
2. **Each MCP server handshakes** — list its tools (`iadc`, `appian`, `context7`). For `appian`, confirm it came up in **read-only** mode (mutating/test tools absent). For Jira, confirm the Atlassian connector is connected. For Office (if used), confirm the Microsoft 365 connector is connected (e.g. a `get_me` call). For Slack (if used for escalation), confirm the Slack connector is connected. **Exception — if `.mcp.json` was deliberately left placeholder-valued (item 1), `iadc` and `appian` have no values to connect with *by design*:** report them as deliberately unconfigured, exactly as item 1 does, not as a failed handshake. (`context7` is keyless and should still come up.)
3. **The workspace is live** — `outputs/` exists and holds its `README.md` (unless that write
   was withheld: the user declined it, or step 2's ignore rules were declined and this skill
   held the README back on its own), and the ignore actually bites:
   `git check-ignore outputs/CONTEXT.md` succeeds (generated artifacts are ignored) while
   `git check-ignore outputs/README.md` fails (the README stays trackable).
   The two ways that can come out wrong have opposite causes —
   read which one you got:
   - **`outputs/README.md` *is* ignored** (its check succeeds when it should fail) → the
     negation never took effect, which is the bare-`outputs/` directory-exclusion case from
     step 2. Surface it — the fix is theirs, changing their rule to `/outputs/*` — rather than
     layering on more rules.
   - **A path inside `outputs/` is *not* ignored** (`outputs/CONTEXT.md`'s check fails) → the
     `/outputs/*` rule is absent, or the user declined the `.gitignore` append (step 2). If
     they declined, this is the state step 2 predicted, not a failure: report the workspace as
     deliberately unignored and leave it.
4. **Project configuration is live** — `docs/agents/project.md` exists and every field carries a
   real answer, with the two exceptions this file documents: `Project lead` stays a placeholder
   when `Escalation` is `hand-off`, and `Nicknames` stays one when the team has no shorthand
   (step 4). Any **other** `<...>` still standing means that field is genuinely unset — go back
   and fill it rather than reporting success, with one further exception on the
   deliberately-unconfigured path: with `.mcp.json` left placeholder-valued the `appian` MCP
   can't run `listApplications`, so if the user doesn't know the `Application` `UUID` by hand
   that placeholder stands for a reason — report it with the other values they still owe, not
   as a failure to fix now. If `project.local.md` was written,
   `git check-ignore` confirms it's ignored — unless the user declined the ignore entries
   (step 2), in which case it is trackable by their choice, and that is what you report.
5. **The session hook fires** — tell the user to start a fresh session in this repo and
   confirm the "iadc-advisor — operating posture" and "Project configuration" sections
   appear at the top of context.

Report what connected and what didn't, with the specific fix for each failure (missing env var, connector not enabled, wrong endpoint).

### 10. Done

Tell the user setup is complete and which skills now read from these files. They can edit `docs/agents/*.md` and `.mcp.json` (gitignored, where step 2's rules were accepted) directly later — re-run this skill only to switch trackers or re-point the plugin at a different Appian project.
