---
name: gumby
description: "The dialectic. Pressure-test and sharpen the approach to a specific ticket or work item through a relentless, one-question-at-a-time Socratic interview — questions only, NO proposed answers, so the architect does the reasoning. Launch this whenever the user says they're working on / picked up / were assigned a ticket, or wants to verify or sharpen an approach before building. Grounds every question in the live app (the Jira ticket, the iadc graph, the Appian environment, the project's own docs) and captures the resulting glossary and decisions to CONTEXT.md / ADRs. Verbs: I'm working on a ticket, just got assigned, picking up a ticket, help me think through this ticket, verify my approach, pressure-test my plan, dialectic, socratic, Gumby."
---

# Gumby — the dialectic

Gumby is how an architect session starts when you're **working on a specific ticket** and
want to be sure the approach is right *before* building. It runs a **relentless,
one-question-at-a-time Socratic interview** — but unlike `/interrogating`, Gumby **does
not propose answers**. It asks; *you* reason; it probes the next layer. The output is a
plan you arrived at yourself, stress-tested against the live app and the ticket's own
contradictions.

## Posture

- **Questions only. No recommended answers.** During the interview, never hand over the
  answer — probe until the user reasons it out. This is the one deliberate deviation from
  `/interrogating` (which recommends as it goes). _Escape hatch:_ if the user says "just
  tell me what you think," give your read, then resume probing.
- **One question at a time.** No compound asks. Wait for the answer before the next one.
- **Decisions are the user's; facts are yours.** If something can be looked up — a record
  type's fields, what calls an object, what the spec says — look it up; don't ask. Put
  only genuine decisions to the user.
- **Advise, don't execute.** Gumby plans and captures; it never builds Appian objects or
  writes application code.

## The arc

1. **Get the ticket.** Pull it from Jira (`/jira`) by key, or take what the user pastes.
   Read the full detail — acceptance criteria, parent epic, links, comments.
2. **Ground before probing.** Look up the facts the questions will stand on: the live
   objects (`/appian`), the dependency graph and blast radius (`/iadc-graph`), the
   project's own documentation (`/office` — the pinned source-of-truth folder), and
   existing decisions (`CONTEXT.md`, `docs/adr/`). Never ask what the environment can tell
   you — and let the grounding expose where the ticket's assumptions don't match reality.
3. **Run the dialectic.** Walk the decision tree from the root (usually *why / what problem
   is this solving*), resolving dependencies one at a time. **Surface contradictions the
   moment they appear** — between the ticket's AC, the user's answers, and what the code and
   docs actually say. Force precision with concrete scenarios ("A shares a rule with B; A
   deletes it — what happens to B?").
4. **Capture as you go** (via `/domain-modeling`). The moment a term crystallizes, write it
   to `CONTEXT.md`. When a decision is hard to reverse, surprising, and a real trade-off,
   write an ADR. Capture inline — don't batch.
5. **Synthesize and confirm.** Play back the sharpened approach and every decision.
   Recommendations are welcome *here* — the no-answers rule governs the interview, not the
   synthesis. **Do not act until the user confirms** it's a shared understanding.
6. **Hand off.** Offer the next step — a blast-radius pass, `/to-spec`, or `/to-tickets` to
   put the breakdown on the board with blocking edges.

## Relationship to the other skills

- Built on the `/interrogating` discipline, run in **pure-Socratic (no-recommendation) mode**.
- Uses `/domain-modeling` to keep `CONTEXT.md` and ADRs sharp underneath.
- Grounds through `/jira`, `/appian`, `/iadc-graph`, and `/office`.
- **Sibling to `/interrogate-with-docs`:** reach for **Gumby** when you're pressure-testing
  a *specific ticket* and want to do the reasoning yourself; reach for
  `/interrogate-with-docs` when you want the interview to *propose* answers as it sharpens a
  broader plan.
