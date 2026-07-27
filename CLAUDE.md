# Appian Architect-in-a-Box — Workshop

This is the **workshop**: the development environment for the Appian Architect-in-a-Box plugin. You are working *on the product here, not with it*.

## The deliverable is the plugin — `iadc-advisor/`, and only it ships

The client receives the **`iadc-advisor` Claude Code plugin**: everything under
[`iadc-advisor/`](iadc-advisor/) — its `.claude-plugin/plugin.json`, `skills/`, `hooks/`,
and templates. This repo doubles as the private **marketplace**
(`.claude-plugin/marketplace.json` at the root). Shipping is still an allowlist: the
marketplace `source` points at `iadc-advisor/` and nothing else ships. Releases are
deliberate: bump `version` in `plugin.json` and record it in `iadc-advisor/CHANGELOG.md`.
See [docs/adr/0001](docs/adr/0001-deliverable-lives-in-a-subfolder.md) and
[docs/adr/0009](docs/adr/0009-ship-as-claude-code-plugin.md).

## Dev docs live here at the root (never shipped)

- `CONTEXT.md` — **maintainer** vocabulary for how the plugin is built and reasoned about. This is *not* a client Appian app's glossary; the plugin's own skills would misread it as one, which is exactly why the plugin's skills live in `iadc-advisor/`, not here.
- `docs/adr/` — decisions about building the plugin.

## Working here

- **Develop the plugin** by editing files under `iadc-advisor/`.
- **Dogfood / test as a client sees it** in a scratch client repo — create one if you
  don't have it (`mkdir ../iadc-dogfood && git -C ../iadc-dogfood init`), a sibling of
  this repo, outside it — never inside the marketplace tree. Add this repo as a local
  marketplace (`claude plugin marketplace add .` from this repo's root), then from
  `../iadc-dogfood` run `claude plugin install iadc-advisor@ignyte --scope project`,
  open Claude there, and run `/setup`. The session hook, namespaced skills, and
  per-project state behave exactly as they will for the client. After editing the
  plugin, refresh **from `../iadc-dogfood`** (project scope is keyed to the working
  directory) with
  `claude plugin marketplace update ignyte && claude plugin update iadc-advisor@ignyte --scope project`
  and start a fresh session.
- **Never install or enable `iadc-advisor` in this repo itself** — its SessionStart
  hook would inject the advisory-architect posture ("you do not write code") into every
  maintainer session. Dogfood only in the scratch repo. (Since the restructure, the
  product's skills no longer auto-load anywhere in this repo — expected.)
- **The advisory posture holds even in the workshop:** this repo produces docs,
  decisions, and configuration — it does not build client Appian objects.

## Deploying

Push this workshop repo with the **PAT in `.secrets/git-credentials`** (gitignored; never committed) — that PAT is the deploy identity. Don't fall back to ambient GitHub or `gh` auth. It needs `repo` scope and must be SSO-authorized for the `teamignyte` org; refresh it there when it expires.

## Extending the plugin

Author or edit skills with **`skill-creator`** — it carries the frontmatter conventions,
progressive-disclosure structure, and description-triggering guidance, and can run eval
loops to harden a new skill. Keep skills **advisory**: the plugin is deliberately
execution-free (no code-writing or triage skills; it plans and hands off). When you add or
rename a skill, update **`which-skill`** (the router). Never put a per-project value in a
`SKILL.md` — that's [ADR 0010](docs/adr/0010-no-config-in-skill-files.md); per-project
state is written by `/setup` into the client repo. Record hard-to-reverse decisions as ADRs
in `docs/adr/`.

**Never declare `skills` or `hooks` in `iadc-advisor/.claude-plugin/plugin.json`.** Both are
auto-discovered from `skills/` and `hooks/hooks.json`; declaring them as well registers the same
paths twice and the plugin **installs successfully but loads nothing** — `✘ failed to load —
Duplicate hooks file detected`, no skills, no posture hook. Adding a skill means adding a folder
under `skills/`, never a manifest key. This one bites silently: **`claude plugin validate` passes
on the broken manifest**, so it is not a gate. The release check is a real install reporting the
plugin as `enabled` in `claude plugin list` — verify there, not with `validate`.

## Agent skills

### Issue tracker

Work on the plugin is tracked as plan-and-progress files, not tickets: the implementation plan
lives in `docs/superpowers/plans/` (committed), and task-by-task progress in `.superpowers/sdd/`
(gitignored working notes). There is no `.scratch/` tree here — `docs/agents/issue-tracker.md`
records the local-markdown ticket conventions for if issues are ever filed as files.

### Triage labels

The five canonical roles, unchanged — `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`, recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
