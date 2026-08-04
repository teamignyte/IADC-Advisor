# Changelog — iadc-advisor

## 1.5.0 — 2026-08-04

**HIGH severity fix.** `/iadc-advisor:setup`'s credential-write gate could be bypassed by a
`.gitignore` flagged `git update-index --skip-worktree` or `--assume-unchanged` — the standard
idiom for keeping a personal ignore line out of a shared file. Either flag makes git stop
comparing that file's working-tree copy to the index at all, so `git diff --quiet HEAD --
.gitignore` reported no difference even when the working copy carried a `.mcp.json` rule the
committed copy at HEAD lacked — every other check in the gate agreed the file was durably
protected when it was not, and a fresh clone (which starts with no such flag) would stage the
credential on the next `git add -A`.

The gate now also requires `git ls-files -v .gitignore | grep -q '^H '` — `ls-files -v` is the
only place either flag is actually visible (`H` = plain cached entry, `S` = skip-worktree,
lowercase `h` = assume-unchanged), since `git diff` has no flag of its own to see past either one.
This is additive, not a replacement: the existing `cat-file`/`diff` pair still catches an ordinary
edited-but-uncommitted `.gitignore` that carries neither flag. **Action for an existing install:**
none required — this only makes the gate refuse a write in a state it previously let through; it
never removes protection it granted before. A repo already flagged this way on `.gitignore` will
be told to clear it (`git update-index --no-skip-worktree` / `--no-assume-unchanged`) before the
next credential write.

## 1.4.1 — 2026-08-04

Two follow-ups to 1.4.0's gate, no change to the gate's own logic:

- **Step 9's report matched the write gate to the weak check the write gate no longer uses.** A
  repo with a pre-existing `.mcp.json` and only a `.git/info/exclude` rule could have step 3 refuse
  to write (correctly), then step 9 report `.mcp.json` "configured and ignored" off plain
  `check-ignore` anyway — the run contradicting itself in one pass. Step 9 now re-runs the same
  four-part check step 3 does, so it can't certify a state step 3 just refused.
- **1.4.0's own explanation of the negation case was backwards**, here and in
  `per-project-state.md`. Plain `git check-ignore` correctly reads a negated `.gitignore` line as
  *not* ignored — it does not "go green" for one. The trap belongs to `git check-ignore -v`, which
  reports a source and exits 0 even when that source is the negation, which is why the compound's
  second bullet excludes a `!`-prefixed source rather than leaning on the plain half alone. No
  command changed; only the write-up of why the compound is correct.

No action needed for an existing install: no gate command changed in this release.

## 1.4.0 — 2026-08-04

`/iadc-advisor:setup` gates the `appian`/`context7` credential write into `.mcp.json` more
strictly. The old check asked only whether `git check-ignore .mcp.json` currently succeeds, which
also goes green when the match lives in `.git/info/exclude` or `core.excludesFile` (neither
travels with a clone), or regardless of whether `.mcp.json` is already a committed blob at HEAD —
states where a fresh clone of the repo would commit the credential even though this check reported
it as protected. The gate now also confirms the match traces to a committed, non-negated
`.gitignore` line at HEAD, and that no committed blob for `.mcp.json` already exists there — the
same minimum bar `/iadc-graph:setup` holds its own credential write to. No action needed for an
existing install: this only makes the gate refuse a write in states it previously let through; it
never removes protection it granted before.

## 1.3.1 — 2026-08-04

`/iadc-advisor:setup` no longer calls MCP credentials "per-project state" in its frontmatter
description or prose. The `.gitignore` comment it writes above `.mcp.json` is now separate from
the one above `docs/agents/advisor.local.md` — one comment per entry, matching the `outputs/`
pair below them. Wording only: which files get written or ignored is unchanged, and there is no
existing install for this to affect — nothing to do on update.

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
