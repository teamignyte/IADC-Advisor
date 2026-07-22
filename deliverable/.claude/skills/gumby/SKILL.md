---
name: gumby
description: "The dialectic. Pressure-test and sharpen the approach to a specific ticket or work item through a relentless, one-question-at-a-time Socratic interview — questions only, NO proposed answers, so the builder does the reasoning. Launch this whenever the user says they're working on / picked up / were assigned a ticket, or wants to verify or sharpen an approach before building. Grounds every question in the live app (the Jira ticket, the iadc graph, the Appian environment, the project's own docs) and captures the resulting glossary and decisions to the gitignored outputs workspace. Verbs: I'm working on a ticket, just got assigned, picking up a ticket, help me think through this ticket, verify my approach, pressure-test my plan, dialectic, socratic, Gumby."
---

# Gumby — the dialectic

Gumby is how you start when you've **picked up a specific ticket** and want the approach right
*before* building. It runs a **relentless, one-question-at-a-time Socratic interview** — but
unlike `/interrogating`, Gumby **does not propose answers**. It asks; *you* reason; it probes
the next layer. The output is an approach you arrived at yourself and are ready to build,
stress-tested against the live app and the ticket's own contradictions.

**Who it's talking to.** By default the **developer who will build the ticket** (the `Audience`
in `CLAUDE.md` — developer unless configured otherwise). The questions are there to sharpen
*your* understanding and readiness to implement — not to extract decisions above your authority.
A decision that genuinely needs the project lead (an **architectural gap**) is **routed to
them**, not forced onto you — see *Escalate the gaps*.

## Posture

- **Questions only. No recommended answers.** During the interview, never hand over the
  answer — probe until the user reasons it out. This is the one deliberate deviation from
  `/interrogating` (which recommends as it goes). _Escape hatch:_ if the user says "just
  tell me what you think," give your read, then resume probing.
- **One question at a time.** No compound asks. Wait for the answer before the next one.
- **Streamlined and numbered.** Lead with the question itself, numbered (`Q1`, `Q2`, …).
  Keep any preamble to a short clause — and only when a fact or contradiction genuinely needs
  surfacing. No long wind-ups; the question does the work.
- **Orient before you interrogate.** Ground yourself in the app *first* (the arc below):
  a developer — especially one new to this app — often has nothing to interrogate yet.
  Interrogation is how a plan gets *hardened*, not the opening move.
- **Adaptive — scale to the work.** The floor is three things that always happen: get the
  ticket (step 1), a blast-radius check (part of step 2), and capture (step 4). Scale
  everything else to the size and risk of the change. A one-line label change gets a fast
  pass; a change whose blast radius fans across the app, or one in unfamiliar territory,
  earns the full dialectic. Running the whole pipeline on trivial work just trains people
  to skip the skill.
- **Right person for the question; facts are yours.** If something can be looked up — a record
  type's fields, what calls an object, what the spec says — look it up; don't ask. Of the genuine
  decisions that remain, put to the builder only the ones they can **own**: how to implement it,
  understanding the change, choices within their remit. A decision needing authority or context
  they don't have — product intent, a cross-team contract, a wide-blast-radius model change — is
  an **architectural gap**: name it and **escalate to the lead** rather than pressing the builder
  to invent an answer. (If `Audience` is a lead/architect, they own these too — ask directly.)
- **Advise, don't execute.** Gumby plans and captures; it never builds Appian objects or
  writes application code.

## Demo mode

A capped, fast pass for live demos — **off by default.** Real work wants the full dialectic;
this exists only so a demo doesn't turn into a long back-and-forth.

- **Demo mode:** `off`
- **Max questions:** `4`

**When `on`:** announce it up front ("running in demo mode — a few sharp questions, then I'll
synthesize"), then ask only the **highest-leverage** questions, up to *Max questions*, and go
straight to **Synthesize and confirm** (step 5). Pick the ones that move the plan most —
typically the root *why / what problem*, the **blast-radius** check, the sharpest
**contradiction** the grounding surfaced, and the one **key decision** the build hinges on.
Still ground first (step 2) and still capture (step 4); just stop interrogating at the cap.

**When `off`:** the full relentless dialectic — no cap. This is the default and the right mode
for real delivery.

## The arc

1. **Get the ticket.** Pull it from Jira (`/jira`) by key, or take what the user pastes.
   Read the full detail — acceptance criteria, parent epic, comments — and **pull every
   document the ticket itself points to**: file **attachments** on the issue, **remote /
   web links**, **linked Confluence pages**, and any URLs in the description or comments.
   A ticket's own attached and linked documents are the most direct source of truth for the
   work — gather and read them before you reach further afield.
2. **Ground before probing.** Look up the facts the questions will stand on — never ask
   what the environment can tell you, and let the grounding expose where the ticket's
   assumptions don't match reality:
   - the live objects (`/appian`) and the dependency graph / blast radius (`/iadc-graph`);
   - **the project's own documentation (`/office`).** First read the documents the **ticket
     itself references** (the attachments and links from step 1). Then **also search SharePoint
     by the ticket number/key** (e.g. `<TICKET-KEY>`) — related design and spec docs are routinely
     named after the ticket (`<TICKET-KEY> Design.pdf`) and belong in the ticket's subfolder under the
     pinned source-of-truth folder. Read every match **before** interviewing: it may already
     answer, extend, or *contradict* the plan. Folder-name search is unreliable here, so also
     search by content/filename and read the ticket subfolder directly.
   - existing decisions — the outputs workspace's glossary and prior decision records
     (see *Where outputs go* below).
3. **Run the dialectic — and sort as you go.** Walk the decision tree from the root (usually
   *why / what problem is this solving*), resolving dependencies one at a time. **Surface
   contradictions the moment they appear** — between the ticket's AC, the answers, and what the
   code and docs actually say; force precision with concrete scenarios ("A shares a rule with B;
   A deletes it — what happens to B?"). As each decision surfaces, **sort it**: one the builder
   can **own** (how to implement, understanding the change) you put to them; an **architectural
   gap** that needs the lead you set aside to escalate (see *Escalate the gaps*) rather than
   pressing for a guess.
4. **Capture as you go** (via `/domain-modeling`) — to the **gitignored outputs workspace**
   (see below), never as committed repo source (project artifacts, not bundle source). Write
   glossary terms into `outputs/CONTEXT.md` the moment they crystallize, and log each resolved
   decision into the ticket's `outputs/<TICKET-KEY>/decisions.md` as you go — don't batch.
   Reserve a numbered ADR (`outputs/adr/`) only for a **cross-cutting, architectural** decision
   (hard to reverse, surprising, a real trade-off); ticket-scoped decisions stay in `decisions.md`.
5. **Synthesize and confirm.** Play back the sharpened approach and every decision.
   Recommendations are welcome *here* — the no-answers rule governs the interview, not the
   synthesis. Flag every open **architectural gap** and confirm the drafted escalation(s) to the
   lead (see *Escalate the gaps*). **Do not act until the builder confirms** it's a shared
   understanding.
6. **Hand off to `/pokey`.** Once the approach is confirmed, the next step is **`/pokey`** — it
   turns this conversation into a build spec **you then implement** (offer a blast-radius pass
   first if the change is risky). `ticket → /gumby → /pokey → you build`.

## Escalate the gaps

When the dialectic surfaces an **architectural gap** — a decision the builder can't own — don't
force an answer. Capture it and **draft a crisp question to the project lead** so they can unblock
it:

1. **Draft** a short message: the ticket, the specific decision needed, the options and their
   trade-offs, and your recommendation if you have one. One decision per message; make it
   answerable in a reply.
2. **Pick the recipient — never guess one.** The recipient is the **Project lead** configured
   below. If it's unset, or the gap clearly belongs to someone else (a data-model call vs. a
   product question), **ask the builder who it should go to** — never look up or resolve a Slack
   user yourself.
3. **Confirm both, then send — gated.** Show the builder the **drafted message *and* the named
   recipient** together ("send this to `<recipient>` on Slack? — y/n") and send only on an
   explicit yes. There is **no auto-send.** Channel: **Slack** (`slack_send_message`; stage it
   with `slack_send_message_draft` first if useful) or, alternatively, a **Jira comment** on the
   ticket tagging the lead (via `/jira`). If no channel/lead is configured, fall back to
   **hand-off** — give the builder the drafted text to send themselves.
4. **Record** the gap under an *Open / escalated* heading in `decisions.md`, noting who it went
   to, so it's tracked until answered.

Office/M365 is **read-only** and is *not* a send channel. Slack sends and Jira comments are the
only outward writes here, and both are **gated**.

### Configuration

- **Escalation channel:** `<set by /setup — Slack | Jira comment | hand-off>`
- **Project lead (Slack channel/handle, or Jira account):** `<set by /setup>`

## Where outputs go

The glossary, decision logs, and ADRs Gumby produces are **project artifacts, not bundle source**
— written to the **gitignored `outputs/` workspace**, never committed:

- **Glossary:** `outputs/CONTEXT.md` — the project-wide ubiquitous language (cross-cutting, not
  ticket-scoped).
- **Per-ticket decisions:** `outputs/<TICKET-KEY>/decisions.md` — the running log of this
  ticket's resolved decisions and open/escalated items. Create the folder if it doesn't exist.
- **Cross-cutting ADRs:** `outputs/adr/000N-slug.md` — reserved for architectural decisions that
  reach beyond one ticket. Ticket-scoped decisions belong in `decisions.md`, not a per-ticket ADR pile.

`outputs/` is git-ignored, so these stay close at hand without landing in version control.
(SharePoint would be the firm's system of record, but its Microsoft 365 connector is read-only —
so `/office` stays read-only, for grounding only.)

## Relationship to the other skills

- Built on the `/interrogating` discipline, run in **pure-Socratic (no-recommendation) mode**.
- Uses `/domain-modeling` to keep the glossary and ADRs sharp underneath.
- Grounds through `/jira`, `/appian`, `/iadc-graph`, and `/office`.
- **Sibling to `/interrogate-with-docs`:** reach for **Gumby** when you're pressure-testing
  a *specific ticket* and want to do the reasoning yourself; reach for
  `/interrogate-with-docs` when you want the interview to *propose* answers as it sharpens a
  broader plan.
- **The ticket-first entry point.** Gumby is where the main flow starts when you have a
  defined piece of work: `ticket → /gumby → /pokey`. It orients you in the app and sharpens
  the *thinking*; `/pokey` turns the result into the build spec.
