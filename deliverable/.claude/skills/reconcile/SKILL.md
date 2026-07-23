---
name: reconcile
description: "Close the loop on a ticket's escalated architectural gaps. After /pressure-test escalates a decision to the project lead (async, via Slack or a Jira comment), run this — with the ticket key — to check whether the lead has replied, fold their answers into the ticket's decisions, re-check impact on the approach, and update readiness. Use when the lead has responded to an escalation, or to check whether they have. Verbs: reconcile, check escalations, did the lead reply, pull in the lead's answer, gumby-reconcile, close the loop on TICKET."
argument-hint: "the ticket key to reconcile, e.g. IMM-2"
---

# Reconcile — close the escalation loop

`/pressure-test` escalates architectural gaps to the project lead **asynchronously** (Slack DM/channel, or
a Jira comment) and moves on, marking the ticket `BLOCKED` and proceeding on a provisional lean.
This skill is how the lead's answer gets **back into the analysis** and how the ticket becomes
**ready for development**. Input: the **ticket key** (e.g. `IMM-2`).

It's the same discipline as `/pressure-test` — read-mostly, gated writes, capture to the outputs workspace
— just scoped to resolving what's open, not a fresh interview.

## Process

1. **Load the ticket's open gaps.** Read `outputs/<TICKET-KEY>/decisions.md`. If there's no
   *Open / escalated* section, there's nothing to reconcile — report `Status: READY` and stop.
   Otherwise take each open item's **thread pointer** (Slack `channel_id`+`message_ts`, or the
   Jira comment) and its **provisional lean**.
2. **Check each thread for a reply.**
   - **Slack** — `slack_read_thread` on the stored `channel_id`+`message_ts`. Read replies *after*
     the escalation message.
   - **Jira comment** — read the ticket's comments via `/jira` for the lead's response.
   - No reply yet → leave the item open; note it as still pending.
3. **Play back your reading — don't blind-parse.** A reply may be "A", a paragraph, or ambiguous.
   State how you're interpreting it and confirm with the builder before recording:
   *"Liam replied 'A' → recording scope = visible/filtered set only; correct?"* If the reply is
   unclear or partial, treat the gap as **still open** and (with the builder) draft a follow-up
   rather than guessing.
4. **Record the resolution.** Move the item from *Open / escalated* to the resolved decisions in
   `decisions.md`, noting the lead's answer and who gave it. Update `/domain-modeling` (glossary /
   a cross-cutting ADR) if the answer warrants it.
5. **Re-check impact.** Compare the answer to the provisional lean Pressure-test proceeded on:
   - **Same as the lean** → nothing downstream changes; say so.
   - **Different** → flag exactly what shifts — which acceptance criteria, and which `/to-spec` build
     steps (if a spec already exists) — so the change is visible, not silent.
6. **Refresh readiness.** Recompute the **`Status:`** line at the top of `decisions.md`:
   `READY` when nothing is open, else `BLOCKED — N open escalation(s)`. If mirrored to a Jira
   **`needs-info`** label, update it (gated). Report what's now resolved and what's still pending.
7. **Hand off when clear.** On `Status: READY`, tell the builder the ticket is ready and the next
   step is **`/to-spec`** (or, if a provisional spec already exists, that `/to-spec` can now finalize
   it). If items remain open, say which, and that they can re-run `/reconcile <TICKET-KEY>`
   after the lead replies.

## Gated, read-mostly

Reading threads/comments is free. The only writes are to the local `outputs/` workspace and — if
configured — a **gated** Jira label update. Never send anything outward from reconcile without the
builder's explicit yes (a follow-up to the lead follows `/pressure-test`'s escalation gate).

## Relationship to the other skills

- **Follows `/pressure-test`:** `ticket → /pressure-test → (/reconcile) → /to-spec`. Pressure-test raises and escalates
  the gaps; reconcile closes them and flips the ticket to `READY`.
- Uses `/jira` (read the ticket / comments) and the Slack connector (`slack_read_thread`) to find
  replies; `/domain-modeling` to record resolved decisions.
- **Gates `/to-spec`:** `/to-spec` reads the `Status:` line — a final build-ready spec requires `READY`.
