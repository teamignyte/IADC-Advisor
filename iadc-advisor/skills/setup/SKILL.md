---
name: setup
description: Configure the iadc-advisor plugin for this Appian project — write the per-project state into this repo (project configuration, issue tracker, domain docs), wire the MCP servers and their credentials, verify everything connects. Run once per app repo after installing the plugin, before first use of the other skills.
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
- `docs/agents/` — `advisor.md`, `advisor.local.md`, `issue-tracker.md`,
  `triage-labels.md`, `domain.md` — which exist from a prior run? A `project.md` or
  `project.local.md` here instead means an earlier version of this skill ran — step 2 offers to
  rename them.
- `outputs/` — does the workspace exist yet?
- `.gitignore` — does it have the entries listed in step 2?
- `git remote -v` — is there a remote, and where?

### 2. Establish the ignore rules and the workspace

**This step runs before anything writes a credential.** Step 3 puts a literal Appian password
(and, if the team wants one, a context7 API key) into `.mcp.json` at the repo root; **the ignore
rules must exist before any credential is written**, or a `git add -A` in the gap between the two
stages the secret. That ordering is the reason this step comes first, not a formality.

The plugin can't ship files into this repo, so create them here (idempotently — leave
existing content alone):

- **Old names, if this repo already ran setup.** Check for `docs/agents/project.md` and
  `docs/agents/project.local.md` before creating anything new. If `docs/agents/advisor.md` is
  still absent and either old file is present, this repo ran an earlier version of this skill,
  under the names this plugin used before — offer to rename rather than writing
  `advisor.md`/`advisor.local.md` beside them and leaving the repo with both. Name only the
  file(s) you actually found — don't assume both exist:

  > Found `docs/agents/project.md` from an earlier setup. Rename it to `docs/agents/advisor.md`
  > (and `project.local.md` → `advisor.local.md`, if present too)? (recommended: **yes**)

  On **yes**, in this order — the `.gitignore` fix and the `.local` rename are the two halves
  of one hazard and belong **back to back, with nothing else between them**: fixing the line
  first but renaming the file later (or the reverse) both leave a window where the file sitting
  under one name matches an ignore rule written for the other:

  1. **Fix `.gitignore` first, if the old line is there.** A repo on the old names has
     `docs/agents/project.local.md` committed in its `.gitignore`; left standing after the
     rename it matches nothing, and the renamed `advisor.local.md` would show up trackable.
     Replace that line with `docs/agents/advisor.local.md` — don't just add the new line beside
     the stale one. **If the old line isn't there** (the user declined step 2's rules on an
     earlier run), there's nothing to replace — the `.gitignore` bullet below still offers to
     add the new line on its own, same as any other missing entry.
  2. **Immediately after — rename `docs/agents/project.local.md`, if it's present.** Always a
     plain `mv`: gitignored files are untracked by design, so there's nothing for `git mv` to
     move in the index. Do this right after item 1, before anything else, so no other step gets
     a chance to run `git add -A` (or similar) while the file sits under its old name and the
     new ignore line — the two do not agree during that gap.
  3. **Rename `docs/agents/project.md`, only if it's present.** Check whether it's tracked
     (`git ls-files --error-unmatch docs/agents/project.md`) before choosing how: **tracked** →
     `git mv docs/agents/project.md docs/agents/advisor.md` (renames and stages the move in one
     step). **Present but untracked** → a plain `mv` instead — `git mv` refuses an untracked
     source outright (`fatal: not under version control`, exit 128). **Not present at all**
     (only `.local` existed) → nothing to do here, move on to the next item. This one has no
     `.gitignore` interaction — `project.md` is either absent or already tracked, and a tracked
     file is never subject to an ignore rule — so it carries none of item 2's ordering risk and
     can safely come after it.
  4. **Fix the renamed file's own contents, not just its name — only if item 3 renamed
     `project.md`.** Its first line, written from this skill's template at the time of the
     original setup, names `docs/agents/project.local.md` as where personal overrides go. That
     sentence is now sitting inside `advisor.md` and still says the old name: leave it, and the
     ambient configuration the hook injects tells the user (and Claude) to write overrides into
     a file the hook no longer reads and `.gitignore` no longer covers — a silently unapplied
     override, next committed by an ordinary `git add -A`. Rewrite just that one filename
     mention to `docs/agents/advisor.local.md` inside the renamed file — the same substitution
     the template itself now carries — and touch nothing else in it.

  Show the user the rename and the `.gitignore` line together and get one yes for both before
  doing either.

  On **decline** — rename nothing and don't ask again this run, **and skip step 4's write this
  run too: don't create a fresh `docs/agents/advisor.md` either** (step 4 says so). That's what
  makes this promise true rather than empty: leaving `advisor.md` absent keeps this bullet's own
  gate open, so the offer genuinely returns on a later run instead of closing the moment step 4
  would otherwise write a brand-new file over the question. Say plainly what that means: the
  session hook and every skill below read `advisor.md`, not `project.md`, so this repo's
  existing values won't be picked up until it's renamed (this run or a later one) — everything
  else this run does (issue tracker, labels, domain docs) proceeds normally.

- **`.gitignore`** — these entries must exist:

  ```
  # iadc-advisor MCP credentials — never committed
  .mcp.json
  # iadc-advisor per-project state — personal overrides, never committed
  docs/agents/advisor.local.md
  # generated planning artifacts (glossary, ADRs, specs) — working files, not source
  /outputs/*
  !/outputs/README.md
  ```

  Show the user exactly which of these lines are missing and **get an explicit yes before you
  append them** — the `.gitignore` is theirs, and it's a committed file. If they decline,
  append nothing and don't ask again (one narrow exception, spelled out in step 3: if the user
  there agrees to `git rm --cached` a tracked `.mcp.json`, that changes the facts this refusal
  was made against, so that single re-ask is legitimate — and a second decline is final). Tell
  them plainly what follows — the decline reaches everything this run would otherwise write
  next, not just `.mcp.json`'s credentials:

  - **`.mcp.json`** stays placeholder-valued (step 3), because this skill does not write
    credentials into a repo that doesn't ignore them.
  - **The `outputs/` workspace** below is still created, but **don't write
    `outputs/README.md`**: its opening line says the folder's contents are git-ignored, which
    would be false in this repo. Say that out loud instead, and let the team decide.
  - **A personal override** in `docs/agents/advisor.local.md` (step 4) would be a trackable
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
exactly the way the decline branch below does. The template stays in the plugin regardless —
whether `.mcp.json` ends up gitignored with no secret ever committed is what the gate later in
this step confirms, not something the rules merely being in place guarantees on their own.

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
    still needed, named one by one (`appian`: `command`, `--directory`, `LCP_URL`,
    `LCP_USERNAME`, `LCP_PASSWORD`; `context7`: nothing unless they want a key), and that those
    have to go wherever they told you their team keeps secrets — outside this repo. Skip only
    the rest of this step's `.mcp.json` write-up (the merge bullet and the two server-value
    bullets); **still walk the `iadc` bullet and the connector bullets** — Jira, Office, Slack —
    with the user, since none of them write a credential into this file: `iadc` only points at
    `/iadc-graph:setup`. Office's deliberate `none` still gets recorded in step 4. Then move on
    to step 4. Step 9 will report `.mcp.json` as deliberately unconfigured; that is the
    correct outcome, not a failure to paper over.
- **`.mcp.json` already exists** (and the check above cleared) → **merge, never overwrite**:
  add or update only the `appian` and `context7` entries; preserve every other server the team
  has configured — `iadc` included, since `/iadc-graph:setup` owns that entry and does its own
  merge into this same file. Show the diff before writing, redacted per the redaction rule in
  step 1.

Servers this plugin expects — collect each value with the user and write it into `.mcp.json`,
**unless the user declined step 2's ignore rules (the stop at the top of this step) or one of
the two guards above stopped you**, in which case the `<placeholder>` stays and the value is
handed off instead of written. **Before the first literal value goes in, this repo has to clear
the same bar every credential write into `.mcp.json` clears in this family: would a fresh clone of
this repo also protect the file, not just does it look protected right now.** `git check-ignore
.mcp.json` alone doesn't distinguish that on its own: it goes green identically whether the match
comes from the tracked `.gitignore`, from `.git/info/exclude`, or from `core.excludesFile` — the
last two never travel with a clone — and, separately, it says nothing about whether `.mcp.json`
itself might already be a committed blob at HEAD regardless of what `.gitignore` currently says.
Re-confirm all of it here, regardless of what step 2 already did — protection can be lost again in
between (a `stash`, a `checkout -- .gitignore`, a flag re-applied, another commit landing):

- `git check-ignore .mcp.json` succeeds — the path reads as ignored right now. This plain form
  already handles a later `.gitignore` line negating an earlier match back out correctly: a
  negated path is genuinely not ignored, and this exits non-zero for it, the same as no match at
  all — the negation trap sits elsewhere, in the next bullet's `-v` half, not here.
- `git check-ignore -- .mcp.json 2>/dev/null && git check-ignore -v -- .mcp.json 2>/dev/null |
  grep -q '^\.gitignore:[0-9]*:[^!]'` — the plain half repeats the bullet above so this check
  stays correct read on its own, since `-v` alone is not enough: it prints a source and exits 0
  even for a line that negates the match back out, which is why the pattern also excludes a
  `!`-prefixed source rather than relying only on the plain half in front of it. Together they
  confirm the match is real **and** traces to the tracked `.gitignore`, not to one of the two
  machine-local sources named above.
- `git cat-file -e HEAD:.gitignore 2>/dev/null && git diff --quiet HEAD -- .gitignore 2>/dev/null`
  — that `.gitignore` copy is committed at HEAD, not only sitting in the working tree or the index.
- `git ls-files -v .gitignore 2>/dev/null | grep -q '^H '` — and git is actually comparing that committed copy
  to the working tree, not skipping the comparison. `git update-index --skip-worktree .gitignore`
  or `--assume-unchanged .gitignore` — the standard idiom for keeping a personal ignore line out of
  a shared file — makes git treat HEAD's copy as authoritative and stop looking at the working tree
  for this one file, so the bullet above reports **no** difference even when the working copy
  carries a `.mcp.json` rule the committed copy at HEAD lacks. `ls-files -v` is the one place either
  flag is actually visible: `H` marks a plain cached entry, `S` marks skip-worktree, lowercase `h`
  marks assume-unchanged — `git diff` has no flag of its own to see past either one, which is why the
  bullet above cannot catch this case by itself. This doesn't replace that bullet: an ordinary
  edited-but-uncommitted `.gitignore` carrying neither flag is still caught there, not here.
- `git cat-file -e HEAD:.mcp.json` **fails** — no committed blob for this file exists at HEAD
  already (the tracked branch above is what gets this file to that state; this confirms it held).

If any check above does not hold, write no credential — name which one, and offer to settle it the
same way the tracked branch above does (stage and commit `.gitignore`, or the pending `git rm
--cached`, only on an explicit yes) before trying again — **except when the `cat-file`/`diff` bullet
passed and the `ls-files -v` bullet alone fails with a letter actually reported**, which neither of
those fixes: offer `git update-index --no-skip-worktree .gitignore` (or `--no-assume-unchanged`,
matching whichever flag was reported) instead, same explicit-yes basis. **A `.gitignore` that is
fully untracked — never `git add`ed, so it isn't in the index at all — is what actually prints no
letter for `ls-files -v`; a staged-but-uncommitted one still shows one** (`ls-files -v` reads the
index, not HEAD, so a file only `git add`ed reports `S` or `h` there just as a committed one does,
even though `cat-file -e HEAD:.gitignore` still fails for it). Only the fully-untracked case leaves
`git update-index --no-skip-worktree` nothing to clear (`fatal: Unable to mark file`), and that's the
ordinary missing/not-yet-durable case above, not this one. Either flag exists specifically to hide a
personal working-tree edit from git, so clearing it may surface an edit the user meant to keep local
— say so before running it.

- **`iadc`** (graph) — no longer configured here: tell the user to run `/iadc-graph:setup` (installed automatically — this plugin declares `iadc-graph` as a dependency), and say plainly that it can wait — before, during, or after this setup; the other skill runs fine mid-session, it's only its *connection* that needs a fresh session before it shows as live — since nothing below depends on it. That skill writes this entry and runs its own credential-safety sequence, and never silently overwrites a working entry — a repo that ran an older version of this skill keeps what it already has unless the user chooses otherwise. This skill neither writes that entry nor waits on the other one — mention it here and move on to the servers below.
- **`appian`** (read-only) — stdio `lcp_mcp_server`. Fill `command`/`--directory` (paths to `uv` and the extracted server bundle), and the `env`: `LCP_URL`, `LCP_USERNAME`, `LCP_PASSWORD`. Keep **`LCP_TOOL_MODE: "readonly"`** — inspection only, no mutation.
- **`context7`** — HTTP docs search. Keyless works, which is why the template ships **no `headers` block** for it; add one carrying `CONTEXT7_API_KEY` only if the team has a key and wants the higher rate limits.
- **Jira** — connected as a **Claude connector** (the Atlassian connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. Jira is **human-first**: the architect reads via the connector and does only light, gated writes. the `jira` and `to-tickets` skills both go through this connector; the project key lives in `docs/agents/issue-tracker.md` (step 5), not an env var.
- **Office / Microsoft 365** — connected as a **Claude connector** (the Microsoft 365 connector), not in `.mcp.json` and with no tokens or env vars to configure here. Point the user at their client's connector settings. This surface is **read-only**: the `office` skill finds and reads SharePoint/OneDrive documents and Teams/Outlook discussion to ground planning, and never sends, uploads, or edits. Optional — if the project has no SharePoint/M365 source docs, leave the connector alone and record the deliberate `none` answer in step 4, so `/iadc-advisor:office` stops asking. (Its pinned source-of-truth folder is a project value — step 4.)
- **Slack** — connected as a **Claude connector** (not in `.mcp.json`). Used only for **escalation**: `/iadc-advisor:pressure-test` can draft and — **gated** (propose → confirm → send) — send an architectural-gap question to the project lead's Slack channel. Point the user at their client's connector settings. Optional — skip if escalations go via a Jira comment or by handing the drafted text to the builder.

### 4. Set project values

Collect these and write them into **`docs/agents/advisor.md`**, from this skill's
[project-config-template.md](./project-config-template.md) — never into any `SKILL.md`
(plugin skills are shared, read-only, and replaced on update; workshop ADR 0010). **If step 2's
migration offer was just declined, skip only the `advisor.md`-specific fields below and the
write itself** — writing a fresh `advisor.md` now would permanently close the gate that offer
depends on, stranding the old file's values exactly as step 2 says won't happen. **Still
collect the Jira project key** (the first bullet below) regardless: it was never an
`advisor.md` field, step 5 needs it, and nothing about declining the rename changes that. That
file is the whole per-project schema: the session hook injects it verbatim as the ambient
**Project configuration**, and six skills read it.

**On a repo that already has real values here** — a prior run, or a file step 2 just renamed
from `project.md` this run — don't re-ask a field that already carries a real answer; only ask
about one still showing its `<...>` placeholder or missing outright (next paragraph) — the two
signals this step goes on. Confirm the existing values with the user rather than re-collecting
them from scratch.

**A field can also be missing outright — no placeholder, no line at all.** A file written
against an older template predates a field this one has since gained, so there's nothing
standing for the placeholder check above to catch. Check for this too: compare the field-label
bullets already in front of you — the ones in
[project-config-template.md](./project-config-template.md), the copy you just read for this
step's field guidance, against the ones in `docs/agents/advisor.md`. **Don't go looking for
another copy of the template to check this against.** The plugin runs from a **read-only shared
cache that can hold more than one installed version side by side** (step 1) — a freshly-resolved
path can land on a stale version and silently pass a file that's missing exactly what the
version actually running just added, which is this exact failure with extra steps. The copy
already open in this step is the only one guaranteed current. A field-label bullet is a line
starting `- **Label:**` (any indent) in the template's data section — not a label merely
mentioned in its prose: the *How to fill these in* paragraph names `` `- **Row:**` `` as an
example of the duplication syntax, which doesn't make it a second `Row` field. Every such bullet
the template carries should have a matching bullet in `docs/agents/advisor.md`'s **own data
section** too — not just any matching line anywhere in the file: `advisor.md` keeps that same
*How to fill these in* paragraph (below, this step says so), so it can carry the same literal
`` `- **Row:**` `` mention, which doesn't count there any more than it does in the template. A
label with **no** matching line at all — not a placeholder, no line, nothing to show the user — is
unset exactly like a standing placeholder: ask for it now, the same way, using the template's
guidance for that field, and add the line where the template positions it relative to its
neighbors. **Except** a nested field whose parent already holds the value that deletes it by
design: `Office source of truth` holding the deliberate `none` answer — matched the same way
`/iadc-advisor:office` matches it, **case-insensitively** (`none` / `None` / `NONE`), a bare
`N/A` included — deletes `Row` and `Active prospect` below it, so their absence there is
correct, not a gap — don't ask.

**Keep the template's field labels verbatim** — `Audience`, `Appian version`,
`Application` (+ `Nicknames`, `UUID`), `Escalation` (+ `Project lead`),
`Office source of truth` (+ `Row`, `Active prospect`) — and keep its
*How to fill these in* paragraph. The skills match on those exact labels; rename or
reword one and the value simply stops being found.

Fill every value **in place**, replacing the `<...>` placeholder with a real answer — and
where a field doesn't apply, write the **deliberate** answer the template names (`none`
for `Office source of truth`, `hand-off` for `Escalation`) rather than skipping it. A
placeholder left standing is how a skill knows a field is genuinely unset, so it will ask
again every session; that is the nag `/iadc-advisor:setup` exists to prevent. Never invent a value, and
never delete a line unless the template says to.

- **Jira project key** (e.g. `IV`) — the one value that is *not* an `advisor.md` field: it
  belongs in `docs/agents/issue-tracker.md` (step 5), where the `jira` and `to-tickets`
  skills read it. Collect this one even when the rest of this step is skipped (the migration
  decline above) — step 5 depends on it, `advisor.md` never held it.
- **`Appian version`** (e.g. `26.6`) — a bare version string, no trailing note. `/iadc-advisor:appian`
  and `/iadc-advisor:context7` read this line for version-exact `docs.appian.com` lookups; it is the
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
  `/iadc-advisor:office` searches there first instead of the whole tenant. Keep the template's shipped
  value `rows below`, fill the `Row:` line (prospect name, site, folder) and name the live
  one on `Active prospect:`; tracking more than one prospect in this repo, duplicate the
  `Row:` line per prospect — that one `Active prospect` line is then the whole toggle.
  **If this project has no M365 source documents, write the bare word `none` on the
  `Office source of truth` line and delete the `Row:` and `Active prospect:` lines** — do
  not skip the field and do not leave the placeholder. `none` is the deliberate answer
  that tells `/iadc-advisor:office` to stop searching SharePoint/OneDrive; a placeholder left standing
  only makes it ask again every session.
  **`Row` missing outright while `Active prospect` already has a real answer** — the shape a
  file written before `Row` existed arrives in — means that answer isn't settled just because
  it isn't a placeholder: it was given with no `Row` line to name. Offer it back as the likely
  name when you ask for `Row` rather than asking blind, and once `Row` is written, confirm
  `Active prospect` names one of the `Row` entries exactly — fix `Active prospect` to match if
  the user gives `Row` a different name, rather than leaving the two to disagree.
- **`Audience`** — who the advisor is talking to: **`developer`** (the default — the person
  who will build the ticket), or `lead`/`architect` if the primary user owns architectural
  decisions. The operating posture reads this line; it shapes how `/iadc-advisor:pressure-test` pitches
  questions and whether it escalates gaps or asks the user directly.
- **`Escalation`** (+ **`Project lead`**) — where `/iadc-advisor:pressure-test` sends an architectural
  gap: the channel (`Slack` | `Jira comment` | `hand-off`) and the lead (Slack
  channel/handle, or Jira account). **No one to escalate to** — a lead/architect audience,
  say? Write **`hand-off`**, the deliberate "hand me the drafted text and I'll send it"
  answer, which needs no `Project lead`. Same rule as the field above: a written answer,
  never a placeholder left standing. **On `hand-off`, the `Project lead` line stays exactly
  as the template ships it, placeholder and all** — unlike the Office branch above, nothing
  is deleted here, because the template doesn't say to and `/iadc-advisor:pressure-test` reads an unset
  `Project lead` as expected under `hand-off`. Any other channel needs a real `Project lead`,
  since that's who the escalation goes to.

**Per-person override:** ask whether this user's role differs from the repo default
(e.g. a lead in a `developer`-default repo). If so, write just the differing lines to
**`docs/agents/advisor.local.md`** (gitignored by step 2's entry — unless the user declined
that append, in which case take the decline branch there before writing one): same field
names; the session
hook injects it after `advisor.md`, so its values win. Any teammate can do the same on
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
- **`docs/agents/advisor.md`** first (note if it was renamed from `project.md` this run, or
  that it's deliberately absent because step 2's migration offer was declined — not a failure,
  just say so), then `issue-tracker.md`, `triage-labels.md`, `domain.md`, and `advisor.local.md`
  if there's a personal override.

Merge into files that already exist rather than clobbering them, and don't touch surrounding content. The client's `CLAUDE.md` is theirs: this skill writes nothing into it and needs nothing from it — the plugin's operating posture arrives through its session hook.

### 9. Verify the plugin is live

This is the payoff — confirm the configuration actually works, don't just write files:

1. **`.mcp.json` is configured and durably protected** — it exists (generated from the template),
   parses as JSON, carries no `<placeholder>` string and no `_comment` key, and clears step 3's
   whole five-part check again, not `git check-ignore .mcp.json` alone: that plain form reads
   green off a rule sitting only in `.git/info/exclude` or `core.excludesFile`, off a `.gitignore`
   line that isn't yet committed at HEAD, or off a `.gitignore` flagged `--skip-worktree`/
   `--assume-unchanged` that stops git from ever comparing the working copy against what's actually
   committed — exactly as readily as off real, durable protection — the same gap step 3 exists to
   close, so step 9 must not certify a state step 3 would have refused to write into. If any part of
   that check fails, diagnose before you fix: run `git ls-files --error-unmatch .mcp.json` — if
   **that** succeeds the file is **tracked**, and no `.gitignore` line can ignore a tracked file, so
   the fix is `git rm --cached .mcp.json` (with the user's yes), not another entry.

   If it's untracked, check `git cat-file -e HEAD:.mcp.json` next, **before** naming any
   `.gitignore` fix — step 3's own fifth bullet, and a question the four `.gitignore` bullets below
   it can't answer. **If it succeeds**, HEAD still carries a committed blob at this path even though
   the index doesn't — the interrupted-prior-run state step 3 itself names: a `git rm --cached` ran
   at some point but the removal was never committed. No `.gitignore` entry fixes that; a fresh clone
   still carries the credential in its history regardless of what `.gitignore` says. Offer to commit
   the pending removal instead (`git status` shows it staged already; run `git rm --cached
   .mcp.json` first only if it isn't), the same remedy the tracked branch above uses, never another
   `.gitignore` append. **Only once that check fails too** — no blob at HEAD, same as step 3 expects
   — do the remaining four `.gitignore` bullets decide it: name which one actually failed before
   naming a fix — **except when the `cat-file`/`diff` bullet passed and the `ls-files -v` bullet
   alone fails with a letter reported, a missing or not-yet-durable `.gitignore` entry is not the
   explanation, the same exception step 3 itself makes**: that shape means `.gitignore` is flagged
   `--skip-worktree` or `--assume-unchanged`, and offering to commit an entry or re-run `git rm
   --cached` is a no-op against it — offer `git update-index --no-skip-worktree .gitignore` (or
   `--no-assume-unchanged`, matching whichever flag was reported) instead, same explicit-yes basis as
   step 3. Only when the failure is one of the other three `.gitignore` bullets — or the
   `cat-file`/`diff` and `ls-files -v` bullets fail together with no letter reported, the
   fully-untracked-`.gitignore` case step 3 also carves out — is a missing or not-yet-durable
   `.gitignore` entry the explanation. If the user declined the ignore entries (step 2) or the `git
   rm --cached` (step 3), report `.mcp.json` as **deliberately unconfigured** with the list of
   values they still owe — don't call that a failure and don't quietly fill it in now.
2. **Each MCP server handshakes** — list its tools (`iadc`, `appian`, `context7`). For `appian`, confirm it came up in **read-only** mode (mutating/test tools absent). For Jira, confirm the Atlassian connector is connected. For Office (if used), confirm the Microsoft 365 connector is connected (e.g. a `get_me` call). For Slack (if used for escalation), confirm the Slack connector is connected. **Exception — if `.mcp.json` was deliberately left placeholder-valued (item 1), `appian` has no values to connect with *by design*:** report it as deliberately unconfigured, exactly as item 1 does, not as a failed handshake. (`context7` is keyless and should still come up.) **`iadc` is a separate case — this skill never writes that entry (step 3). If its tools are absent, that's not this skill's failed handshake, for any of several reasons: `/iadc-graph:setup` may not have run yet, may have run this same session (its write needs a fresh one to take effect), may have been declined inside it, or the key on file may be wrong (the graph service is fail-closed on it, so a bad key and no key look identical from here). Point the user at that command rather than diagnosing which.**
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
4. **Project configuration is live** — **Exception first: if step 2's migration offer was
   declined this run, `docs/agents/advisor.md` is deliberately absent — not a failure.** Report
   that project values remain unset until the repo is renamed (this run or a later one), exactly
   as step 2 told the user, and skip the rest of this item; there is no file yet for the checks
   below to run against. Otherwise: `docs/agents/advisor.md` exists and every field carries a
   real answer, with the two exceptions this file documents: `Project lead` stays a placeholder
   when `Escalation` is `hand-off`, and `Nicknames` stays one when the team has no shorthand
   (step 4). Any **other** `<...>` still standing means that field is genuinely unset — go back
   and fill it rather than reporting success, with one further exception on the
   deliberately-unconfigured path: with `.mcp.json` left placeholder-valued the `appian` MCP
   can't run `listApplications`, so if the user doesn't know the `Application` `UUID` by hand
   that placeholder stands for a reason — report it with the other values they still owe, not
   as a failure to fix now. **That placeholder check alone misses a field with no line at
   all** — re-apply step 4's field-label comparison, the same way, to
   **`docs/agents/advisor.md`** specifically (not `advisor.local.md`, named two sentences below:
   it's partial **by design** — step 4 says so — and would diff as several gaps for a reason
   that has nothing to do with this one). A template label with no matching line in
   `docs/agents/advisor.md` at all is a gap — report it and go back and ask, the same as a
   standing placeholder, not success. Where `Row` is present, also confirm `Active prospect`
   names one of its entries exactly; naming one that doesn't exist as a `Row` — stale from
   before `Row` existed, or from a rename — is the same gap, not a pass just because neither
   field is individually a placeholder. If `advisor.local.md` was written or renamed from
   `project.local.md` this run, `git check-ignore` confirms it's ignored — unless the user
   declined the ignore entries (step 2), in which case it is trackable by their choice, and that
   is what you report. **If `advisor.md` was renamed from `project.md` this run**, also confirm
   its content was fixed, not just its name: plain **`grep -q project.local.md
   docs/agents/advisor.md`** (not `git grep` — a `project.md` that was present but untracked was
   moved with a plain `mv`, per item 3 of step 2, so it can still be untracked here too, and
   `git grep` silently skips untracked files rather than failing loudly) should fail (no match)
   — if it still matches, step 2's content fix (its item 4) was missed and needs to be applied
   now, not reported as done.
5. **The session hook fires** — tell the user to start a fresh session in this repo and
   confirm the "iadc-advisor — operating posture" and "Project configuration" sections
   appear at the top of context.

Report what connected and what didn't, with the specific fix for each failure (missing env var, connector not enabled, wrong endpoint).

### 10. Done

Tell the user setup is complete and which skills now read from these files. **If `iadc` is still outstanding, say so again here** — step 9 already reported it once, but this is the last thing the user reads, so repeat it rather than let it drop: name `/iadc-graph:setup` and that it's fine to run whenever, same session included — only its connection needs a fresh session before it shows as live. They can edit `docs/agents/*.md` and `.mcp.json` (gitignored, where step 2's rules were accepted) directly later — re-run this skill only to switch trackers or re-point the plugin at a different Appian project.
