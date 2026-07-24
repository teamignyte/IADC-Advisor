---
name: "jira"
description: "Read the project's Jira board through the Jira MCP to give the Appian advisor context — what's planned, in flight, decided, blocked, or already tracked — and optionally post light comments. Jira is human-first: read-mostly, with at most light gated writes. Load when the architect needs to ground planning or answer a question against the board, look up a ticket, or check what work already exists. Verbs: read jira, board context, what's planned, ticket status, look up issue, comment on ticket."
---

Pull **context from the Jira board** to help the Appian advisor. Jira here is **human-first**: your job is mostly to **read** — via the Jira MCP connector — so the architect's planning and answers are grounded in what the team is actually tracking. Writing is rare and light: at most a comment, and only when the user asks, proposed first.

The board's conventions (project key, issue types, statuses, label vocabulary, title scheme) live in `docs/agents/issue-tracker.md` — read it so you interpret the board correctly.

## What this is for

- **Ground the advisor in reality.** Before answering "should we build X" or breaking down a plan, check what's already on the board: is there an existing ticket, an in-flight effort, a prior decision, a blocker? Bring that into the conversation.
- **Answer board questions.** "What's the status of `<KEY>-42`?", "what's planned for this feature?", "is anything blocking this?" — read and summarize.
- **Surface relevant tickets** when interrogating a plan or writing a spec, so the architect isn't planning in a vacuum.

It is **not** a board-cleanup tool. If you notice something messy (a stale status, a broken link, a duplicate), mention it in passing so a human can fix it — don't go on a cleanup pass.

## Reading (the default)

Use the Jira MCP tools:

- **Search** with JQL, e.g. `project = <KEY> AND status = "In Progress" ORDER BY updated DESC`, or `project = <KEY> AND text ~ "<topic>"` to find tickets about a concept.
- **Get** an issue by key to read its full detail. The description is stored as **ADF** — read the rendered text, not the raw field.
- Summarize what's relevant back into the conversation; cite the ticket keys.

## Light writing (rare, gated)

Only when the user asks, and always proposed first:

- **Post a comment** on a ticket (e.g. a decision reached during interrogation, a pointer to a spec). Prefix agent-written comments so they're identifiable, and verify it landed by re-reading.

Anything heavier — creating tickets, transitioning status, editing fields, changing labels, linking dependencies — is the job of `to-tickets` (also gated), or a human. This skill stays on the reading side.
