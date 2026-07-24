---
name: pressure-test
description: "The dialectic. Pressure-test and sharpen the approach to a specific ticket or work item through a relentless, one-question-at-a-time Socratic interview — questions only, NO proposed answers, so the builder does the reasoning. Launch this whenever the user says they're working on / picked up / were assigned a ticket, or wants to verify or sharpen an approach before building. Grounds every question in the live app (the Jira ticket, the iadc graph, the Appian environment, the project's own docs) and captures the resulting glossary and decisions to the gitignored outputs workspace. Verbs: I'm working on a ticket, just got assigned, picking up a ticket, help me think through this ticket, verify my approach, pressure-test my plan, dialectic, socratic, gumby."
---

# Pressure-test — the dialectic

Pressure-test is how you start when you've **picked up a specific ticket** and want the approach right
*before* building. It runs a **relentless, one-question-at-a-time Socratic interview** — but
unlike `/interrogating`, Pressure-test **does not propose answers**. It asks; *you* reason; it probes
the next layer. The output is an approach you arrived at yourself and are ready to build,
stress-tested against the live app and the ticket's own contradictions.

**Who it's talking to.** By default the **developer who will build the ticket** (the `Audience` line in the ambient **Project configuration** — developer unless configured otherwise; a personal `project.local.md` override wins). The questions are there to sharpen
*your* understanding and readiness to implement — not to extract decisions above your authority.
A decision that genuinely needs the project lead (an **architectural gap**) is **routed to
them**, not forced onto you — see *Escalate the gaps*.

## Posture

- **Questions only. No recommended answers.** During the interview, never hand over the
  answer — probe until the user reasons it out. This is the one deliberate deviation from
  `/interrogating` (which recommends as it goes). _Escape hatch:_ if the user says "just
  tell me what you think," give your read, then resume probing.
- **One question at a time.** No compound asks. Wait for the answer before the next one.
- **Short and direct — one idea per question.** Numbered (`Q1`, `Q2`, …), each a single line the
  dev can answer in a sentence. No multi-clause setups, no embedded mini-essay, no long wind-up —
  if a fact is needed to frame the question you already looked it up (facts are yours). A question
  that takes three sentences to ask is really several questions; split it. Err on the side of too
  short.
- **Aim for comprehension, not extraction.** Each question moves the *developer's* understanding one
  concrete step toward the **implementation** — "where would this live?", "what happens to X when Y?",
  "what would you check first?" — so the plan takes shape in their head and they arrive at the best
  approach themselves. You're building their grasp of the build, not quizzing them. Genuine
  scoping/product decisions are **not** dialectic fodder — they're surfaced up front and escalated
  (see the arc), never smuggled into the interview.
- **Orient before you interrogate.** Ground yourself in the app *first* (the arc below):
  a developer — especially one new to this app — often has nothing to interrogate yet.
  Interrogation is how a plan gets *hardened*, not the opening move.
- **Adaptive — scale to the work.** The floor is three things that always happen: get the
  ticket (step 1), a blast-radius check (part of step 2), and capture (step 6). Scale
  everything else to the size and risk of the change. A one-line label change gets a fast
  pass — no scoping gaps to surface, a question or two, done; a change whose blast radius fans
  across the app, or one in unfamiliar territory, earns the full treatment. Running the whole
  pipeline on trivial work just trains people to skip the skill.
- **Right person for the question; facts are yours.** If something can be looked up — a record
  type's fields, what calls an object, what the spec says — look it up; don't ask. Of the genuine
  decisions that remain, put to the builder only the ones they can **own**: how to implement it,
  understanding the change, choices within their remit. A decision needing authority or context
  they don't have — product intent, a cross-team contract, a wide-blast-radius model change — is
  an **architectural gap**: name it and **escalate to the lead** rather than pressing the builder
  to invent an answer. (If `Audience` is a lead/architect, they own these too — ask directly.)
- **Advise, don't execute.** Pressure-test plans and captures; it never builds Appian objects or
  writes application code.

## Demo mode

A capped, fast pass for live demos — **off by default.** Real work wants the full dialectic;
this exists only so a demo doesn't turn into a long back-and-forth.

- **Demo mode:** `off`
- **Max questions:** `4`

**When `on`:** still surface + escalate the scoping gaps up front (steps 3–4), then announce the cap
("running in demo mode — a few sharp questions, then I'll synthesize"), ask only the
**highest-leverage** comprehension questions up to *Max questions*, and go straight to **Synthesize
and confirm** (step 7). Pick the ones that move the plan most — typically the root *why / what
problem*, the **blast-radius** check, the sharpest **contradiction** the grounding surfaced, and the
one **key decision** the build hinges on. Still ground first (step 2) and still capture (step 6);
just stop interrogating at the cap.

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
   - the live objects (`/appian`) and the dependency graph / blast radius (`/iadc-graph`) — seed
     the graph from the **application UUID in the Project configuration**, never from a
     live `listApplications` lookup; when the blast radius is wide, render it as a fan-in diagram
     with `/to-diagram` and keep it with the ticket's `decisions.md`;
   - **the project's own documentation (`/office`).** First read the documents the **ticket
     itself references** (the attachments and links from step 1). Then **also search SharePoint
     by the ticket number/key** (e.g. `<TICKET-KEY>`) — related design and spec docs are routinely
     named after the ticket (`<TICKET-KEY> Design.pdf`) and belong in the ticket's subfolder under the
     pinned source-of-truth folder. Read every match **before** interviewing: it may already
     answer, extend, or *contradict* the plan. Folder-name search is unreliable here, so also
     search by content/filename and read the ticket subfolder directly.
   - existing decisions — the outputs workspace's glossary and prior decision records
     (see *Where outputs go* below).
3. **Surface the scoping questions — to the developer first.** From the grounding and the ticket's
   own open questions, list the genuine **scoping / product / architectural decisions** the work
   hinges on — the ones needing intent or authority a developer may not hold (e.g. *"does 'mark all
   as read' mean the whole inbox or just the filtered view?"*). Put the **whole list to the dev up
   front**, before any dialectic: for each, *do you know the answer, or is it yours to make?* A dev
   often knows more than the ticket says — capture whatever they can answer as a decision right here.
   (Trivial work surfaces none of these — skip straight to the dialectic.)
4. **Escalate what's left — to the lead, up front.** Whatever the dev *can't* answer is an
   **architectural gap**: escalate it **now**, before the dialectic (see *Escalate the gaps*), so the
   lead has the most time to reply. Record each as *Open / escalated* in `decisions.md`, set the
   **`Status:`** line, and proceed on a **provisional lean** — never dead-wait. Replies get folded in
   later (see *Readiness & reconcile*).
5. **Build comprehension with the developer — the dialectic.** The main event, and where the short,
   direct, one-at-a-time questions (see Posture) do their work: walk the dev to the best
   **implementation** — how it fits the existing objects, what order to build in, what breaks nearby,
   the edge cases — so they arrive at the plan themselves. Move from the root outward, one dependency
   at a time. **Surface contradictions the moment they appear** — between the AC, the dev's answers,
   and what the code and docs actually say — with a concrete scenario ("A shares a rule with B; A
   deletes it — what happens to B?"). This stays with the dev and about the build; it does **not**
   re-open the scoping gaps already escalated in step 4.
6. **Capture as you go** (via `/domain-modeling`) — to the **gitignored outputs workspace** (see
   below), never committed. Glossary terms into `outputs/CONTEXT.md`. Every **substantive decision**
   gets captured **twice, as it lands** (don't batch):
   - a **numbered ADR** in `outputs/adr/NNNN-slug.md` — project-wide sequential numbering, so the
     ADR sequence is the **chronological history of every decision** (see `/domain-modeling`'s
     ADR-FORMAT); and
   - a **rollup entry** in the ticket's `outputs/<TICKET-KEY>/decisions.md` that states the decision
     and **links its ADR number** — `decisions.md` is the per-ticket index over the ADRs.

   A substantive decision is any resolved choice that had a real alternative (what you put to the
   dev, each resolved escalation, a design call that shapes the build). A trivial advisor's-call
   mechanic with no real alternative is noted in `decisions.md` only — no ADR.
7. **Synthesize and confirm.** Play back the sharpened approach and every decision. Recommendations
   are welcome *here* — the no-answers rule governs the interview, not the synthesis. Then run a quick
   **auto-reconcile** (see *Readiness & reconcile*): check whether any escalation from step 4 already
   has a reply, fold it in, and refresh the **`Status:`** line. **Do not act until the developer
   confirms** it's a shared understanding.
8. **Hand off — when ready.** Once the approach is confirmed *and the ticket is* **`READY`** (no open
   escalations), hand off to **`/to-spec`** — it turns this conversation into a build spec **you then
   implement** (offer a blast-radius pass first if the change is risky). If gaps are still open, the
   ticket stays **not ready for dev**: tell the developer to run **`/reconcile <TICKET-KEY>`** once the
   lead replies, and note that `/to-spec` produces only a **provisional** spec until then.
   `ticket → /pressure-test → (/reconcile) → /to-spec → you build`.

## Escalate the gaps

When the up-front triage (arc step 3) leaves an **architectural gap** — a scoping/product decision
the developer can't answer or own — don't force an answer. Capture it and **draft a crisp question
to the project lead** so they can unblock it:

1. **Draft** a short message. Open with a line that **identifies it as an automated escalation
   from the advisor** — e.g. `🤖 *Architect Agent — escalation on <TICKET-KEY>*` — because the
   Slack/Jira connector posts **as the logged-in user**, so the *content* must make clear it's
   agent-sent, not a personal note. Then give the specific decision needed and the options with their
   trade-offs — **stated neutrally, with no recommendation and no steer.** The call is the lead's; lay
   out the options even-handedly and let them decide, rather than nudging them toward one. (You *do*
   hold a **provisional lean** internally so planning can continue — see step 4 — but that lean stays
   in `decisions.md`; it is **not** put in the message to the lead.) One decision per message; make it
   answerable in a reply. **Close by telling the lead exactly what to do:** just reply in this
   thread — the developer is notified automatically and will pick it up, so **no further action is
   required** on their side.
2. **Pick the recipient — never guess one.** The recipient is the **Project lead** configured
   below. If it's unset, or the gap clearly belongs to someone else (a data-model call vs. a
   product question), **ask the builder who it should go to** — never look up or resolve a Slack
   user yourself.
3. **Confirm both, then send — gated.** Show the builder the **drafted message *and* the named
   recipient** together ("send this to `<recipient>` on Slack? — y/n") and send only on an
   explicit yes. There is **no auto-send.** Channel: **Slack** (`slack_send_message`; stage it
   with `slack_send_message_draft` first if useful) or, alternatively, a **Jira comment** on the
   ticket tagging the lead (via `/jira`). If no channel/lead is configured, fall back to
   **hand-off** — give the builder the drafted text to send themselves. Prefer a destination the
   **developer also sees** (a shared channel, or @-mention the dev) so the lead's in-thread reply
   notifies them automatically. **Capture the send's `channel_id` + `message_ts`** — reconcile needs
   them to find the reply later.
4. **Record** the gap under *Open / escalated* in `decisions.md`: the question, its **provisional
   lean** (so planning continues on a marked assumption), **who** it went to, and the **thread
   pointer** (the Slack `channel_id` + `message_ts`, or the Jira comment id) so the reply can be
   found. Then refresh the ticket's **`Status:`** line (see *Readiness & reconcile*).

Office/M365 is **read-only** and is *not* a send channel. Slack sends and Jira comments are the
only outward writes here, and both are **gated**.

### Configuration

Escalation is configured in the ambient **Project configuration** (from
`docs/agents/project.md`, written by `/setup`): the **`Escalation`** line (channel —
Slack | Jira comment | hand-off) and **`Project lead`** (Slack channel/handle, or Jira
account). If unset, ask the user where escalations should go and suggest running `/setup`.

## Readiness & reconcile

An escalation is **asynchronous** — the lead may answer in seconds or days — so Pressure-test never
dead-waits. It proceeds on the provisional lean and tracks readiness explicitly.

- **Status line.** The first line of `outputs/<TICKET-KEY>/decisions.md` is a status:
  `Status: READY` (no open escalations) or `Status: BLOCKED — N open escalation(s)`. Pressure-test and
  `/reconcile` keep it current; `/to-spec` reads it. Optionally mirror it to a gated Jira
  **`needs-info`** label so the board shows the block.
- **Auto-reconcile (end of pass).** After synthesis, check each escalation raised this session for
  a reply already back — `slack_read_thread` on the stored `channel_id`+`message_ts`, or the Jira
  comment — and fold any answers in before you finish.
- **`/reconcile <TICKET-KEY>` (later).** When the lead replies after the session, the builder
  runs this. It reads the ticket's *Open / escalated* items, checks their threads, and for each
  reply **plays back its reading** ("Liam replied A → recording *scope = visible set*; right?"),
  records the resolved decision, re-checks impact (flagging any `/to-spec` step that changes), and
  refreshes the status. Re-run until nothing is open.
- **Readiness gate.** While `Status: BLOCKED` the ticket is **not ready for development**:
  `/to-spec` produces only a clearly-marked **provisional** spec — never a final build-ready one —
  until every escalation is resolved.

## Where outputs go

The glossary, decision logs, and ADRs Pressure-test produces are **project artifacts, not bundle source**
— written to the **gitignored `outputs/` workspace**, never committed:

- **Glossary:** `outputs/CONTEXT.md` — the project-wide ubiquitous language (cross-cutting, not
  ticket-scoped).
- **ADRs — the chronological decision history:** `outputs/adr/NNNN-slug.md`, one per **substantive
  decision**, **project-wide sequential numbering** in the order decisions are made. This single
  ascending sequence is the durable record of *every* decision across all tickets. Lightweight — a
  paragraph each.
- **Per-ticket decisions (the rollup):** `outputs/<TICKET-KEY>/decisions.md` — the `Status:` line,
  this ticket's resolved decisions (**each linking its ADR number**), and its open/escalated items.
  It's the per-ticket index over the ADRs, not a separate record. Create the folder if it doesn't exist.

`outputs/` is git-ignored, so these stay close at hand without landing in version control.
(SharePoint would be the firm's system of record, but its Microsoft 365 connector is read-only —
so `/office` stays read-only, for grounding only.)

## Relationship to the other skills

- Built on the `/interrogating` discipline, run in **pure-Socratic (no-recommendation) mode**.
- Uses `/domain-modeling` to keep the glossary and ADRs sharp underneath.
- Grounds through `/jira`, `/appian`, `/iadc-graph`, and `/office`.
- **Sibling to `/interrogate-with-docs`:** reach for **Pressure-test** when you're pressure-testing
  a *specific ticket* and want to do the reasoning yourself; reach for
  `/interrogate-with-docs` when you want the interview to *propose* answers as it sharpens a
  broader plan.
- **The ticket-first entry point.** Pressure-test is where the main flow starts when you have a
  defined piece of work: `ticket → /pressure-test → /to-spec`. It orients you in the app and sharpens
  the *thinking*; `/to-spec` turns the result into the build spec.
