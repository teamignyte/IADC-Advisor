# Appian Architect-in-a-Box — Workshop

This is the **workshop**: the development environment for the Appian Architect-in-a-Box plugin. You are working *on the product here, not with it*.

## The deliverable is the plugin — `iadc-advisor/`, and only it ships

The client receives the **`iadc-advisor` Claude Code plugin**: everything under
[`iadc-advisor/`](iadc-advisor/) — its `.claude-plugin/plugin.json`, `skills/`, `hooks/`,
and templates. Shipping is an allowlist: the catalog's `source` points at `iadc-advisor/`
and nothing else ships. Releases are deliberate: bump `version` in `plugin.json` and record
it in `iadc-advisor/CHANGELOG.md`.
See [docs/adr/0001](docs/adr/0001-deliverable-lives-in-a-subfolder.md) and
[docs/adr/0009](docs/adr/0009-ship-as-claude-code-plugin.md).

**The catalog no longer lives here.** It moved to
[`teamignyte/IADC-Marketplace`](https://github.com/teamignyte/IADC-Marketplace), the family's
client-facing distribution repo, which lists this plugin alongside `iadc-tester`, the shared
`iadc-graph` skill, and an `iadc` bundle that installs the suite in one command. This repo is now
*only* the workshop. See the family's
[ADR 0001](https://github.com/teamignyte/IADC/blob/main/docs/adr/0001-iadc-family-is-five-repos-in-two-tiers.md).

## Dev docs live here at the root (never shipped)

- `CONTEXT.md` — **maintainer** vocabulary for how the plugin is built and reasoned about. This is *not* a client Appian app's glossary; the plugin's own skills would misread it as one, which is exactly why the plugin's skills live in `iadc-advisor/`, not here.
- `docs/adr/` — decisions about building the plugin.

## Working here

- **Develop the plugin** by editing files under `iadc-advisor/`.
- **Dogfood / test as a client sees it** in a scratch client repo — the loop (marketplace add,
  install, refresh-after-edit, and its push-first gotcha) is the runbook
  [docs/dogfooding.md](docs/dogfooding.md).
- **Never install or enable `iadc-advisor` in this repo itself** — its SessionStart
  hook would inject the advisory-architect posture ("you do not write code") into every
  maintainer session. Dogfood only in the scratch repo. (Since the restructure, the
  product's skills no longer auto-load anywhere in this repo — expected. Third-party and
  family plugins are also disabled in dev sessions at user level — umbrella ADR 0013 — so
  enabling it *per-project here* is the one path left to that mistake.)
- **The advisory posture holds even in the workshop:** this repo produces docs,
  decisions, and configuration — it does not build client Appian objects.

## Pushing

Per-device SSH key at machine level (family ADR 0007); the umbrella `ship` skill carries the
setup and the failed-push diagnosis. There is no PAT and no credential store.

## Extending the plugin

Author or edit skills with **`skill-creator`** — it carries the frontmatter conventions,
progressive-disclosure structure, and description-triggering guidance, and can run eval
loops to harden a new skill. Keep skills **advisory**: the plugin is deliberately
execution-free (no code-writing or triage skills; it plans and hands off). When you add or
rename a skill, update **`which-skill`** (the router). Never put a per-project value in a
`SKILL.md` — that's [ADR 0010](docs/adr/0010-no-config-in-skill-files.md); per-project
state is written by `/setup` into the client repo. Record hard-to-reverse decisions as ADRs
in `docs/adr/`.

**Shell commands written into skill prose are ratcheted.** `tests/skill_command_baseline.py`
records a count per skill file and the suite fails when one moves either way — up means write a
script instead, down means lower the baseline in the same commit. That file documents the
counting method, what it deliberately misses, and how to update it. **This repo authors the
guard; `IADC-Tester` carries a mirror of `tests/test_skill_command_ratchet.py`, so a fix belongs
here first and travels there in the same change.** Nothing mechanical binds the two copies.

**Never declare `skills` or `hooks` in `iadc-advisor/.claude-plugin/plugin.json`.** Both are
auto-discovered from `skills/` and `hooks/hooks.json`; declaring them as well registers the same
paths twice and the plugin **installs successfully but loads nothing** — `✘ failed to load —
Duplicate hooks file detected`, no skills, no posture hook. Adding a skill means adding a folder
under `skills/`, never a manifest key. This one bites silently: **`claude plugin validate` passes
on the broken manifest**, so it is not a gate. The release check is a real install reporting the
plugin as `enabled` in `claude plugin list` — verify there, not with `validate`.

## The vendored `appian` skill

`iadc-advisor/skills/appian/` is vendored from <https://github.com/appian/dev-mcp-skills> and
carries deliberate local patches — chiefly the ADR 0010 config relocation (upstream hardcodes
`**Appian Version:** 26.6`; we read it from the ambient Project configuration), repairs to 15
citations upstream points at files that do not exist, and (since IV-442) repointing the skill's
two live workflows — blast radius, accessibility audit — at the `iadc` graph instead of a live
Appian MCP, which this plugin no longer configures at all. **Never edit that tree without reading
[docs/vendored-appian-skill.md](docs/vendored-appian-skill.md) first** — it records every
deliberate divergence, the refresh procedure, and the greps that catch a silent revert.
Refreshed to upstream `0ab639c4` on 2026-07-27. **Adding a local patch means adding it to that
doc in the same commit** — an undocumented divergence is indistinguishable from staleness at
refresh time, and one nearly cost us the skill's advisory posture.

## The `iadc-graph` skill is no longer vendored here

This plugin used to carry its own copy at `iadc-advisor/skills/iadc-graph/`. It doesn't any more.
`iadc-graph` is a **separate plugin** in the family catalog, and this plugin declares it as a
dependency — so installing `iadc-advisor` installs it automatically, and there is nothing here to
keep in sync.

That has one consequence in the skills' prose: the graph skill is now addressed
**`/iadc-graph:iadc-graph`** — the skill `iadc-graph` inside the plugin `iadc-graph`. The doubled
name looks like a typo and is not.

The single mirror now lives in `IADC-Graph-Plugin`, its own client-facing repo, and refreshing it
is not a step in this plugin's release any more. The rule this repo's ADR 0011 established is
unchanged and still release-blocking — the skill may lag the deployed server, never lead it — but
*which sha* a refresh takes belongs to the runbook, not to this file: it is normally the sha that
built the **deployed** graph image, and `IADC-Core` HEAD when the runbook's own check establishes
the deployed server has not moved. Procedure and current sha:
[IADC-Marketplace/docs/mirrored-iadc-graph-skill.md](https://github.com/teamignyte/IADC-Marketplace/blob/main/docs/mirrored-iadc-graph-skill.md).
The rule and its rationale are unchanged; only the location and the copy-count are
([docs/adr/0011](docs/adr/0011-iadc-graph-skill-byte-identical-at-deployed-sha.md), superseded by
the family's
[ADR 0003](https://github.com/teamignyte/IADC/blob/main/docs/adr/0003-shared-skills-ship-as-pinned-marketplace-plugins.md)).

## Agent skills

### Issue tracker

Work on the plugin is tracked on the **shared IADC Jira board**, alongside the other two products —
tracking is a family concern, so the CLI, its convention docs and the triage vocabulary all live in
the umbrella (family
[ADR 0004](https://github.com/teamignyte/IADC/blob/main/docs/adr/0004-family-work-tracked-in-jira-iv.md)).

Implementation *plans* still live here as files: `docs/superpowers/plans/` (committed) and
task-by-task progress in `.superpowers/sdd/` (gitignored working notes). Those are plans, not
tickets.

### Domain docs

Single-context — `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
