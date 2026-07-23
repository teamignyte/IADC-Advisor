# Capture every substantive decision as a chronological ADR, rolled up per ticket

The advisory skills now record decisions at **two grains**, both in the gitignored `outputs/`
workspace:

- **`outputs/adr/NNNN-slug.md`** — one **ADR per substantive decision**, with **project-wide
  sequential numbering** in the order decisions are made. This single ascending sequence is the
  **chronological history of every decision** across all tickets.
- **`outputs/<TICKET-KEY>/decisions.md`** — the **per-ticket rollup**: the readiness `Status:` line,
  the ticket's resolved decisions (each **linking its ADR number**), and its open/escalated items.
  It is an index over the ADRs, not a separate record.

A "substantive decision" is any resolved choice that had a real alternative — what was put to the
developer or the lead, and each resolved escalation. Trivial advisor's-call mechanics with no real
alternative are noted in `decisions.md` only, not given an ADR.

## Why

- **We want both, and they serve different needs.** The per-ticket rollup answers "what was decided
  for this ticket, and is it ready to build?"; the chronological ADR sequence answers "what has this
  project decided, in what order, and why?" Neither substitutes for the other.
- **A complete, ordered decision trail has standalone value** — onboarding, audit, and "why is it
  like this?" six months later. Burying decisions inside per-ticket files loses the timeline.
- **Cheap when lightweight.** An ADR is a paragraph (see `domain-modeling`'s ADR-FORMAT), so
  one-per-decision is affordable; the exclusion of trivial mechanics keeps the log signal-rich.

## Consequences

- This **widens** the ADR bar that an earlier iteration had narrowed. Prior wording reserved ADRs for
  *cross-cutting/architectural* decisions and made `decisions.md` the primary record; that "sparingly"
  three-part gate in `domain-modeling`'s ADR-FORMAT is **replaced** by "an ADR per substantive
  decision." The per-ticket `decisions.md` rollup is kept — now it links the ADRs.
- ADR numbering is **project-wide and chronological** in `outputs/adr/`, not per-ticket — there is one
  sequence, not a pile per ticket. (Multi-context projects may still keep per-context `adr/` folders.)
- `/pressure-test` (capture step) and `/reconcile` (resolution step) both write an ADR **and** the
  linking rollup entry as each decision lands. `domain-modeling`, `setup/domain.md`, the
  `pressure-test` *Where outputs go* section, and `outputs/README.md` are updated to match.
- These remain **gitignored project artifacts** ([ADR-0005](0005-generated-artifacts-live-in-a-gitignored-outputs-workspace.md)) — the volume increase lands in `outputs/`, never in the tracked bundle.
