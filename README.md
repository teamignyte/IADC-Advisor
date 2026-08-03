# Appian Architect-in-a-Box — Workshop

The development workshop for **Appian Architect-in-a-Box**, shipped as the **`iadc-advisor`**
Claude Code plugin: an advisory Appian architect that helps a developer work out *how to build the
ticket in front of them*, grounded in the live application, its dependency graph, the Jira board and
the team's own documents.

**You are working *on* the product here, not with it.** The plugin's own
[README](iadc-advisor/README.md) is the user-facing guide and describes what it does.

## Layout

```
iadc-advisor/          THE DELIVERABLE — everything that ships, and only this
├── skills/            the advisory skills
├── hooks/             the SessionStart hook carrying the operating posture
└── .claude-plugin/    the manifest
CONTEXT.md             maintainer vocabulary — how the plugin is built
docs/adr/              decisions about building the plugin
```

`CONTEXT.md` is deliberately *not* a client Appian application's glossary. The plugin's own skills
would misread it as one — which is exactly why they live under `iadc-advisor/` and not at the root
([ADR 0001](docs/adr/0001-deliverable-lives-in-a-subfolder.md),
[ADR 0009](docs/adr/0009-ship-as-claude-code-plugin.md)).

## Two dependencies that are not ours to edit freely

- **`iadc-advisor/skills/appian/`** is vendored from Appian's own repository and carries deliberate
  local patches. Read its divergence ledger before touching that tree: an undocumented patch is
  indistinguishable from staleness at the next refresh.
- **`iadc-graph` is not vendored here at all.** It is a separate plugin that this one declares as a
  dependency, so it installs automatically and there is nothing to keep in sync. In skill prose it
  is addressed `iadc-graph:iadc-graph` — the skill inside the plugin of the same name. The doubled
  name is correct.

## Developing

Edit under `iadc-advisor/`. Author skills with `skill-creator`, which carries the frontmatter and
progressive-disclosure conventions. Keep them **advisory**: the plugin plans and hands off; it never
writes application code.

Two traps worth knowing before you hit them:

- **Never declare `skills` or `hooks` in the manifest.** Both are auto-discovered, and declaring
  them as well registers the same paths twice — after which the plugin installs successfully and
  loads *nothing*. `claude plugin validate` passes on that broken manifest, so it is not a gate; the
  real check is a live install reporting the plugin as `enabled`.
- **Never install this plugin in this repo.** Its SessionStart hook would inject the advisory
  posture — *you do not write code* — into every maintainer session.

To test what a client actually gets, install from the
[catalog](https://github.com/teamignyte/IADC-Marketplace) into a scratch repo. The catalog fetches
this plugin from the repo's default branch rather than from your working tree, so push before
refreshing, or you will be testing the previous version.

## Releasing

Deliberate: bump `version` in the manifest and record the change in
[`iadc-advisor/CHANGELOG.md`](iadc-advisor/CHANGELOG.md). Anything that changes how clients install
or configure the plugin belongs in that entry — it is where they look to find out what they must do.

## Related

Part of the **IADC** family. The [umbrella](https://github.com/teamignyte/IADC) holds the other
repositories, the decisions that bind more than one of them, and the shared issue tracking.
