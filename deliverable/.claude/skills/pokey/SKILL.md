---
name: pokey
description: "The build spec — Pokey follows Gumby. Turn a sharpened plan (usually a /gumby conversation for a ticket) into a developer-ready build spec: a PRD backbone (problem, solution, decisions) PLUS an ordered, executable list of Appian configuration steps the developer follows to build it. Synthesis only, no re-interview. Lays the full spec out for review and invites final clarifying questions FIRST, and only writes it to the gitignored outputs workspace once the developer approves — never auto-writes. Launch after Gumby, or whenever the user wants to turn the plan into a spec / build guide / design doc. Verbs: make the build spec, write the spec, turn this into a spec, design spec, build guide, spec this out, pokey."
---

# Pokey — the build spec (Gumby's counterpart)

Gumby sharpens the *thinking*; **Pokey lays out the *steps*.** Pokey turns a sharpened plan —
usually the `/gumby` conversation for a ticket — into a **developer-ready build spec**: the
PRD context *plus* an ordered, executable list of Appian configuration steps the developer
follows to build it. It is the handoff artifact — it replaces splitting work into tickets.

## Posture

- **Synthesis, not interview.** Pokey does not re-interrogate — it synthesizes from the Gumby
  conversation, the decision record/ADR, the glossary, and the grounding already done. If
  something essential is genuinely missing, ask — but don't re-run Gumby.
- **Present first, write only on approval — never auto-write.** Lay the full spec out *in the
  conversation*, then explicitly invite final clarifying questions and iterate. Only once the
  developer says they're happy do you write it to disk.
- **Advisory.** The spec is instructions for a *human* to execute; the agent never builds
  Appian objects. Pokey produces the plan, not the build.
- **Gitignored outputs workspace, not the tracker.** Output goes to the gitignored `outputs/`
  workspace in the repo — never committed as bundle source, and (absent O365 write scopes) not
  SharePoint. Same workspace Gumby captures to.
- **Readiness gate — check the ticket's `Status:` first.** Read the first line of
  `outputs/<TICKET-KEY>/decisions.md`. On **`READY`** (no open escalations) you produce the final,
  build-ready spec. On **`BLOCKED`** you may still produce a spec, but it is **PROVISIONAL** — every
  decision riding on an unresolved escalation is flagged *assumed, pending `<lead>`*, and you must
  **not** stamp it build-ready. Point the builder at **`/gumby-reconcile <TICKET-KEY>`** to clear the
  block, then finalize.

## Process

1. **Check readiness, then synthesize.** First read the **`Status:`** line of
   `outputs/<TICKET-KEY>/decisions.md`: `READY` → you'll produce the final build-ready spec;
   `BLOCKED — N open escalation(s)` → a **provisional** spec only (see the readiness gate in
   Posture), until `/gumby-reconcile <TICKET-KEY>` clears the block. Then pull the plan together
   from the Gumby thread, `decisions.md`, and the glossary (`outputs/CONTEXT.md`). Reuse the
   grounding Gumby already did (record model, dependency order, blast radius); re-check the live
   app (`/appian`, `/iadc-graph`) only where a build step needs a fact you don't have. Use the
   glossary's vocabulary; respect existing ADRs.
2. **Order the build steps** in Appian dependency order (data model → relationships → rules →
   interfaces → process models → record actions/views → migration → tests). Each step names the
   object and is concrete enough to execute, with a **"done when"** check.
3. **Present the full spec in the conversation** for review. Lay out the plan, then **explicitly
   invite final clarifying questions.** Do **not** write anything yet.
4. **Iterate** on their questions and adjustments until they're happy.
5. **On approval, write it.** Confirm the target path, write to
   `outputs/<TICKET-KEY>/<TICKET-KEY> Spec.md` (create the ticket folder if it doesn't
   exist — same workspace Gumby uses), and verify it landed. Report the path. **If the ticket is
   `BLOCKED`,** title it `<TICKET-KEY> Spec (PROVISIONAL).md` and open with a
   `> PROVISIONAL — pending escalations:` banner listing each assumed-pending decision; re-run once
   `/gumby-reconcile` flips the status to `READY` to produce the final spec.
6. **Hand off.** The developer executes the build steps outside this bundle; the spec is the
   source of record for the build.

## Spec template

<spec-template>

# <TICKET-KEY> — <title>

## Problem
The problem, from the user's perspective (from the ticket + Gumby).

## Solution
The approach, from the user's perspective.

## Key decisions
The resolved decisions from Gumby, each on a line, linked to the decision record/ADR.

## Build steps
An **ordered** list, in Appian dependency order. Each step:
- **What:** the object to create/modify (record type, relationship, rule, interface, process
  model, record action, migration) and the specifics.
- **Done when:** the observable check that the step is complete.

Concrete enough that the developer just follows it. Include data-migration steps explicitly.

## Testing
The object tests / checks to add or run (the app has a deterministic-test harness). Test
external behavior, not implementation detail.

## Risks & watch-outs
Blast radius and regression areas to be careful of.

## Out of scope / deferred
What this build does not cover (carried from Gumby).

</spec-template>

_(User stories — the long "As an X, I want Y, so that Z" list from `/to-spec` — are optional.
Include them only when the feature is broad enough to warrant it; for a scoped config ticket
they usually add noise.)_

## Relationship to the other skills

- **Follows `/gumby`:** `ticket → /gumby` (dialectic) → **`/pokey`** (build spec). It's the
  handoff step.
- Uses `/domain-modeling`'s glossary + the decision record/ADR; grounds via `/appian`,
  `/iadc-graph`, `/office`.
- **Supersedes `/to-tickets`** (splitting into subtasks — the inverse direction) and **`/to-spec`**
  (a PRD published to the tracker). Pokey is `/to-spec` reborn: **local**, **Appian-flavored**,
  **with executable build steps**, and **gated on your approval** before writing.
