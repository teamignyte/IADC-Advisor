# Re-point the main flow to start from an existing ticket

> **Superseded by [ADR-0006](0006-rename-spine-skills-and-collapse-greenfield.md).** The spine
> described here (entry point `groundwork`) was later reshaped — the entry point became `gumby`,
> then `pressure-test` — and the greenfield `to-spec → to-tickets` tail collapsed to `to-tickets`.
> Kept for history; the current spine is `ticket → /pressure-test → (/reconcile) → /to-spec`.

The documented main flow ran idea → `interrogate` → `to-spec` → `to-tickets`: produce
a backlog and hand off. But ~99% of real use is the *other side* of that handoff — a
developer already holds a ticket and needs help figuring out how to build it in this
Appian app. So the **spine** is re-pointed to start from a defined unit of work — a
ticket or a plain description of it (read the ticket if there is one, gather its
surrounding requirements/design context, locate it and its blast radius, inspect the
objects, look up the Appian how-to, sharpen the approach) — and the old
idea→spec→tickets flow is demoted to a secondary "greenfield / net-new planning" path.
Its skills, including `to-tickets`, are kept — demoted, not deleted.

## Consequences

- The skill is **orient-led**: it grounds the developer in the app first (context →
  inspection → how-to), then uses interrogation to *sharpen* the resulting approach.
  Interrogation hardens the plan; it is not the opening move.
- Entry accepts either a Jira ticket **or a plain description of the work** — the anchor
  is a *defined unit of work*, not necessarily a tracked one (which is why the skill is
  named `groundwork`, not `from-ticket`).
- The default ending is a short **implementation note**: drafted locally; offered to
  Jira as a gated, propose-first write when the entry was a ticket, or kept local when
  it was only a description. An **ADR** is added only when a genuine, hard-to-reverse
  decision surfaced; the developer may also end with no artifact at all. The skill never
  mints a ticket — that stays with the greenfield flow.
- Context is gathered from more than the tracker: the ticket (Jira) anchors it, but
  requirements and design context also live in **SharePoint / OneDrive** and **Teams /
  Outlook**, and the flow should draw on all of them. The Office/SharePoint source
  depends on the **Office MCP, which is not yet built** (today a placeholder) — until it
  exists, that input is limited to what the developer supplies.
- The flow is packaged as a new named skill, `groundwork` — a thin orchestrator that
  invokes the existing skills as steps rather than reimplementing them (`jira`, and the
  Office surface once built, for context; `iadc-graph`, `appian`, `context7` for
  inspection; `interrogate` to sharpen), in the shape of `interrogate-with-docs`. A
  primary flow needs an invocable front door, and the cross-skill glue — e.g. resolving
  a ticket's Appian object names to graph UUIDs — needs a home.
- Boundary with the greenfield flow: `groundwork` works out *how to build a defined
  piece of work*; shaping or decomposing an undefined or large effort stays with
  `interrogate`→`to-spec`→`to-tickets`, or `wayfinder` when it's huge and foggy.
- Jira writes stay inside the human-first posture. The implementation note posted as a
  **comment** is the *only* write `groundwork` makes, always proposed then confirmed. It
  does **not create** tickets — if orientation shows the work should be split or a
  prerequisite is untracked, it flags that and offers to hand off to `to-tickets`, where
  creation lives. It does **not modify** tickets either (no editing the body, no status
  transitions, no labels); a ticket that needs rescoping or clearer acceptance criteria
  is called out for a human, with the clarified understanding left in the note.
