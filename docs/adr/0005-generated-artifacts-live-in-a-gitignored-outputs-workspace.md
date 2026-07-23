# Generated planning artifacts live in a gitignored `outputs/` workspace

The advisory skills produce **project artifacts** — the domain glossary, decision
records/ADRs, and build specs from `/pressure-test`, `/to-spec`, `/interrogate-with-docs`, and
`/domain-modeling`. These are working outputs *about the client's Appian application*, not
part of the shipped bundle. They now land in a **gitignored `outputs/` workspace** at the
deliverable root: the glossary at `outputs/CONTEXT.md`, per-ticket decision records and
build specs under `outputs/<TICKET-KEY>/`, ADRs under `outputs/adr/` (or the relevant
context/ticket subfolder). Only `outputs/README.md` and `.gitkeep` are tracked.

This **amends one consequence of [ADR-0001](0001-deliverable-lives-in-a-subfolder.md)**,
which stated the client would *commit* their own `CONTEXT.md` / ADRs. ADR-0001's core
decision — the deliverable lives in `deliverable/` and only that ships — still stands; only
the disposition of the *generated* domain docs changes here.

## Why

- **They're generated, not authored source.** Treating a per-ticket build spec or an
  evolving glossary like committed code invites noisy diffs and merge friction over
  artifacts that are really a developer's working notes.
- **They can hold app-specific detail** the client may not want in version control by
  default. Gitignored-by-default is the safer floor; committing is an opt-in a team can
  choose.
- **One location for both flows.** The ticket flow (`/pressure-test` → `/to-spec`) and the greenfield
  flow (`/interrogate-with-docs` → `/domain-modeling`) now share a single glossary/ADR home
  instead of splitting between a committed `CONTEXT.md` and a separate workspace.

## Considered options

- **Commit the domain model, gitignore only the build specs** (closer to ADR-0001's
  original intent). Rejected for now: it splits the artifacts across two dispositions and
  reintroduces the "is the glossary committed or not" ambiguity. A team that wants the model
  version-controlled can still opt in (below).
- **Write outputs outside the repo entirely** (an earlier demo-branch approach — a local
  `Documents/` workspace). Rejected: harder to find, not co-located with the bundle the
  developer is already working in.

## Consequences

- `deliverable/.gitignore` ignores `/outputs/*` (keeping `README.md` + `.gitkeep`). The
  skills and `setup/domain.md` point at `outputs/` as the glossary/ADR home.
- The domain model is **not version-controlled by default**. A team that wants it tracked
  removes the `/outputs/*` rule from `.gitignore` — called out in `outputs/README.md`.
- Nothing about outputs ever flows back to the workshop repo; they are client-instance
  artifacts by construction.
