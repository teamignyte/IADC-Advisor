# No per-project config lives in skill files

Plugin-delivered skills live in a shared, read-only cache (`~/.claude/plugins/cache/…`)
that is replaced on every update — so `/setup` can no longer write project values into
`SKILL.md` Configuration blocks (Appian version, app UUID, escalation target, office
profile), as it did when skills were copied into each app repo. One app's values would
also clobber another's.

**Supersedes ADR 0003** (store application identity in the graph skill): the application
name/nicknames/UUID now live in `docs/agents/project.md`, not `iadc-graph/SKILL.md` —
the no-live-lookup rule 0003 established is unchanged; only the storage location moves.

All per-project values move to **files in the app repo**: `docs/agents/project.md`
(committed team defaults), `docs/agents/project.local.md` (gitignored per-person
overrides — Audience), plus the existing `docs/agents/issue-tracker.md`,
`triage-labels.md`, `domain.md`. The plugin's SessionStart hook injects
`project.md` + `project.local.md` ambiently, so skills read config from context, exactly
as the shipped `CLAUDE.md` once made the Audience ambient.

Rule going forward: **a `SKILL.md` may carry knowledge, never configuration.** If a value
differs between two client apps, it belongs in `docs/agents/`, written by `/setup`.

## Considered options

- **Skills read config files on demand (no ambient injection).** Rejected: every skill
  grows a read step, and cross-cutting values (Audience, Appian version) stop being
  ambient, regressing behavior the shipped `CLAUDE.md` provided.
- **Plugin `userConfig`.** Rejected: plugin-wide per machine — wrong granularity for
  per-app values (see ADR 0009).

## Consequences

- `appian`, `iadc-graph`, `pressure-test`, and `office` lose their Configuration blocks
  and point at the ambient Project configuration instead.
- `/setup` writes `docs/agents/project.md` from a template asset and offers the
  per-person `project.local.md` override.
- The hook resolves precedence itself (Audience is not a native Claude Code settings
  key): `project.local.md` (per-person) overrides `project.md` (committed), which falls
  back to the built-in default `Audience: developer`.
