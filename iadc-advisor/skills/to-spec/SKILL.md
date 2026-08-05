---
name: to-spec
description: "The build spec — To-spec follows Pressure-test. Turn a sharpened plan (usually a /iadc-advisor:pressure-test conversation for a ticket) into a developer-ready build spec: a PRD backbone (problem, solution, decisions) PLUS an ordered, executable list of Appian configuration steps the developer follows to build it. Synthesis only, no re-interview. Lays the full spec out for review and invites final clarifying questions FIRST, and only writes it to the gitignored outputs workspace once the developer approves — never auto-writes. Launch after Pressure-test, or whenever the user wants to turn the plan into a spec / build guide / design doc. Verbs: make the build spec, write the spec, turn this into a spec, design spec, build guide, spec this out, pokey."
---

# To-spec — the build spec (Pressure-test's counterpart)

Pressure-test sharpens the *thinking*; **To-spec lays out the *steps*.** To-spec turns a sharpened plan —
usually the `/iadc-advisor:pressure-test` conversation for a ticket — into a **developer-ready build spec**: the
PRD context *plus* an ordered, executable list of Appian configuration steps the developer
follows to build it. It is the handoff artifact — it replaces splitting work into tickets.

## Posture

- **Synthesis, not interview.** To-spec does not re-interrogate — it synthesizes from the Pressure-test
  conversation, the decision record/ADR, the glossary, and the grounding already done. If
  something essential is genuinely missing, ask — but don't re-run Pressure-test.
- **Present first, write only on approval — never auto-write.** Lay the full spec out *in the
  conversation*, then explicitly invite final clarifying questions and iterate. Only once the
  developer says they're happy do you write it to disk.
- **Advisory.** The spec is instructions for a *human* to execute; the agent never builds
  Appian objects. To-spec produces the plan, not the build.
- **The `outputs/` workspace, not the tracker.** Output goes to the `outputs/` workspace in the
  repo — gitignored where `/iadc-advisor:setup`'s ignore rules were accepted, never committed as plugin
  source, and (absent O365 write scopes) not SharePoint. Same workspace Pressure-test captures to.
- **Readiness gate — reconcile, then check the ticket's `Status:`.** If escalations are open, run
  **`/iadc-advisor:reconcile <TICKET-KEY>`** first (step 1) to pull any late Slack replies, then read the
  `Status:` line of `outputs/<TICKET-KEY>/decisions.md`. On **`READY`** (no open escalations) you
  produce the final, build-ready spec. On **`BLOCKED`** you may still produce a spec, but it is
  **PROVISIONAL** — every decision riding on an unresolved escalation is flagged *assumed, pending
  `<lead>`*, and you must **not** stamp it build-ready; the builder re-runs once the lead replies.

## Process

1. **Reconcile first, then check readiness.** Before anything else, if the ticket's `decisions.md`
   shows any **open escalations**, **run `/iadc-advisor:reconcile <TICKET-KEY>`** — the lead may have answered on
   Slack since the pressure-test session, and folding that reply in now can flip a `BLOCKED` ticket
   to `READY` (so you produce the final spec instead of a provisional one). Then read the **`Status:`**
   line: `READY` → produce the final build-ready spec; still `BLOCKED — N open escalation(s)` → a
   **provisional** spec only (see the readiness gate in Posture). Then pull the plan together from the
   Pressure-test thread, `decisions.md`, and the glossary (`outputs/CONTEXT.md`). Reuse the grounding
   Pressure-test already did (record model, dependency order, blast radius); re-check the live app
   (`/iadc-advisor:appian`, `/iadc-graph:iadc-graph`) only where a build step needs a fact you don't have. Use the glossary's
   vocabulary; respect existing ADRs.
2. **Name every object — split NEW vs. MODIFY — in dependency order.** This is the heart of the
   spec: don't describe the work abstractly ("update the interface"), say **exactly which Appian
   objects the build touches**, each tagged **[NEW]** (create) or **[MODIFY]** (change an existing
   object):
   - **[NEW]** — the exact name (following the app's naming convention), the type (record type,
     field, expression rule, interface, process model, constant, record action/view, site page, …),
     and what it must contain or do.
   - **[MODIFY]** — the exact name **as it exists in the app/graph**, and the *precise* change: the
     field added and its type, the specific rule branch or expression altered, the process node
     inserted and how it's wired — never just "update X".

   Confirm exact names and current shape against `/iadc-graph:iadc-graph` + `/iadc-advisor:appian` rather than guessing.
   Then order the steps in **Appian dependency order** (data model → relationships → constants →
   rules → interfaces → process models → record actions/views → data migration → tests) so **every
   object exists before anything that references it**. Each step carries a **"done when"** check.
   Render the ordered steps as a **build-step dependency DAG** with `/iadc-advisor:to-diagram` — what gates what,
   what can run in parallel — and inline it in the spec.
3. **Present the full spec in the conversation** for review. Lay out the plan, then **explicitly
   invite final clarifying questions.** Do **not** write anything yet.
4. **Iterate** on their questions and adjustments until they're happy.
5. **On approval, write it.** Confirm the target path, write to
   `outputs/<TICKET-KEY>/<TICKET-KEY> Spec.md` (create the ticket folder if it doesn't
   exist — same workspace Pressure-test uses), and verify it landed. Report the path. **If the ticket is
   `BLOCKED`,** title it `<TICKET-KEY> Spec (PROVISIONAL).md` and open with a
   `> PROVISIONAL — pending escalations:` banner listing each assumed-pending decision; re-run once
   `/iadc-advisor:reconcile` flips the status to `READY` to produce the final spec.
6. **Hand off.** The developer executes the build steps outside this plugin; the spec is the
   source of record for the build.

## Spec template

<spec-template>

# <TICKET-KEY> — <title>

## Problem
The problem, from the user's perspective (from the ticket + Pressure-test).

## Solution
The approach, from the user's perspective.

## Key decisions
The resolved decisions from Pressure-test, each on a line, linked to the decision record/ADR.

## Build steps

Open with an **object inventory** — a table of every Appian object the build touches, split into
**New (create)** and **Existing (modify)**, each with its exact name and type:

| Object | Type | New / Modify |
|---|---|---|
| `<exact name>` | record type / field / rule / interface / process model / constant / action / view | NEW or MODIFY |

Then the **ordered** steps, in Appian dependency order — each step:
- **Object:** the exact name + type, tagged **[NEW]** or **[MODIFY]**.
- **Change:** precisely what to create or alter — the field and its type, the specific rule logic,
  the process node and its wiring — concrete enough to execute without guessing, never "update X".
- **Done when:** the observable check that the step is complete.

Order so every object exists before anything that references it. Include data-migration steps
explicitly. Inline the **build-step dependency DAG** here (via `/iadc-advisor:to-diagram`), plus a
**target-state ERD** for the data-model steps.

## Testing
The object tests / checks to add or run (the app has a deterministic-test harness). Test
external behavior, not implementation detail.

## Risks & watch-outs
Blast radius and regression areas to be careful of.

## Out of scope / deferred
What this build does not cover (carried from Pressure-test).

</spec-template>

_(User stories — the long "As an X, I want Y, so that Z" list — are optional.
Include them only when the feature is broad enough to warrant it; for a scoped config ticket
they usually add noise.)_

## Relationship to the other skills

- **Follows `/iadc-advisor:pressure-test`:** `ticket → /iadc-advisor:pressure-test` (dialectic) → **`/iadc-advisor:to-spec`** (build spec). It's the
  handoff step.
- Uses `/iadc-advisor:domain-modeling`'s glossary + the decision record/ADR; grounds via `/iadc-advisor:appian`,
  `/iadc-graph:iadc-graph`, `/iadc-advisor:office`.
- **Replaces splitting a defined ticket into subtickets** — `/iadc-advisor:to-tickets` is the inverse
  (greenfield) direction. This is the **local**, **Appian-flavored** build spec: executable build
  steps, gated on your approval before writing.
