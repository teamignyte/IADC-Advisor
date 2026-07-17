---
name: pokey
description: "The build spec — Pokey follows Gumby. Turn a sharpened plan (usually a /gumby conversation for a ticket) into a developer-ready build spec: a PRD backbone (problem, solution, decisions) PLUS an ordered, executable list of Appian configuration steps the developer follows to build it. Synthesis only, no re-interview. Lays the full spec out for review and invites final clarifying questions FIRST, and only writes it to the local workspace once the developer approves — never auto-writes. Launch after Gumby, or whenever the user wants to turn the plan into a spec / build guide / design doc. Verbs: make the build spec, write the spec, turn this into a spec, design spec, build guide, spec this out, pokey."
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
- **Local workspace, not the tracker.** Output goes to the local project workspace — never the
  git repo, and (absent O365 write scopes) not SharePoint. The location is configured in
  `docs/agents/domain.md`.

## Process

1. **Synthesize.** Pull the plan together from the Gumby thread, the decision record/ADR, and
   the glossary (`CONTEXT.md`). Reuse the grounding Gumby already did (record model, dependency
   order, blast radius); re-check the live app (`/appian`, `/iadc-graph`) only where a build
   step needs a fact you don't have. Use the glossary's vocabulary; respect existing ADRs.
2. **Order the build steps** in Appian dependency order (data model → relationships → rules →
   interfaces → process models → record actions/views → migration → tests). Each step names the
   object and is concrete enough to execute, with a **"done when"** check.
3. **Present the full spec in the conversation** for review. Lay out the plan, then **explicitly
   invite final clarifying questions.** Do **not** write anything yet.
4. **Iterate** on their questions and adjustments until they're happy.
5. **On approval, write it.** Confirm the target path, write to
   `<workspace>/<TICKET-KEY>/<TICKET-KEY> Spec.md` (create the ticket folder if it doesn't
   exist — see `docs/agents/domain.md` for the base), and verify it landed. Report the path.
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
