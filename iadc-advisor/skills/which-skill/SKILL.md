---
name: which-skill
description: Ask which skill or flow fits your situation. A router over the skills in this Appian architect-in-a-box plugin.
disable-model-invocation: true
---

# Which Skill

You don't remember every skill, so ask. This is a router over the skills in this plugin — an **advisory Appian architect**. It helps a developer figure out **how to build the ticket in front of them**, answers questions about an Appian application, and — for net-new work — sharpens planning into specs and ticket breakdowns. It does **not** write code or build Appian objects; execution happens outside this plugin.

A **flow** is a path through the skills. Most work runs along the **main flow**; the other two flows are for when the work *isn't* a defined build. Everything else is a standalone tool or a vocabulary layer that runs underneath.

## The main flow: a ticket → the dialectic → a build spec

The route most work travels. You have a **ticket, or a described task**, and you need to work out **how** to build it in this Appian app:

1. **`/iadc-advisor:pressure-test`** — start here. A relentless, one-question-at-a-time **Socratic dialectic** that pressure-tests your approach to the ticket. It's **orient-led** (grounds you in the app first — blast radius, objects, the project's own docs — *then* interrogates) and **adaptive** (a one-line change gets a quick pass; a wide-blast-radius change gets the full treatment). Unlike `/iadc-advisor:interrogate-with-docs`, Pressure-test **asks but does not answer** — *you* do the reasoning. Questions you can't own (architectural gaps) it **escalates to the project lead** rather than forcing an answer. It captures the sharpened glossary and decisions as it goes.
2. **`/iadc-advisor:reconcile <TICKET>`** — only if Pressure-test escalated a gap. Async: when the lead replies (Slack/Jira), run this to pull their answer back in, resolve the decision, and flip the ticket from `BLOCKED` to `READY`. Re-run until nothing's open.
3. **`/iadc-advisor:to-spec`** — once the approach is confirmed *and the ticket is `READY`*, To-spec synthesizes the Pressure-test conversation into a **developer-ready build spec**: the PRD context *plus* an ordered, executable list of Appian configuration steps. It presents the spec for review and writes it only on your approval, and it **replaces** splitting the work into subtickets. (While the ticket is `BLOCKED` on an open escalation, To-spec produces only a *provisional* spec.)

`ticket → /iadc-advisor:pressure-test → (/iadc-advisor:reconcile) → /iadc-advisor:to-spec`. Pressure-test uses the inspection skills below (`/iadc-advisor:jira`, `/iadc-graph:iadc-graph`, `/iadc-advisor:appian`, `/iadc-advisor:context7`, `/iadc-advisor:office`) and the `/iadc-advisor:interrogating` primitive as its steps; reach for one directly when you only need the single thing it does — but when you're working out how to *build* something, start with `/iadc-advisor:pressure-test`.

## When the work isn't a defined build

Two situations sit outside the main flow. The line is simple: `/iadc-advisor:pressure-test` is for a **defined** piece of work; these are for work that isn't defined yet.

### Greenfield — shaping net-new work into a plan

You have an idea to shape into something a developer can pick up and build — not a ticket to implement.

1. **`/iadc-advisor:interrogate-with-docs`** — sharpen the idea by interview. Start here when the project **has a domain model**: it's stateful, retaining what it learns in `CONTEXT.md` and ADRs. (No `CONTEXT.md`/codebase to ground against? Use `/iadc-advisor:interrogate-me` — see Standalone. Both run the same `/iadc-advisor:interrogating` primitive; `interrogate-with-docs` is the one that leaves a paper trail.)
2. **`/iadc-advisor:to-tickets`** — split the sharpened thinking into tracer-bullet tickets, each declaring its **blocking edges**. On a local tracker that's one file per ticket; on a real tracker (Jira, etc.) the edges become native blocking links, so any ticket whose blockers are done can be grabbed.

**This is the handoff point.** The tickets go to developers (or coding agents) *outside* this plugin to implement — where each one becomes a starting point for `/iadc-advisor:pressure-test`. (A *defined* ticket skips this flow: `ticket → /iadc-advisor:pressure-test → /iadc-advisor:to-spec` produces the build spec directly, no split needed.)

Keep steps 1–2 in **one unbroken context window** so the interrogation and tickets build on the same thinking. If a session gets too long before `/iadc-advisor:to-tickets`, don't push on degraded — `/iadc-advisor:handoff` and continue in a fresh thread (see Crossing sessions).

### A huge, foggy effort — too big for one session

- **`/iadc-advisor:wayfinder`**, the most cognitively demanding flow here. When the way from here to the destination isn't visible yet, it charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time — producing **decisions and ADRs, not deliverables** — until the fog clears. Where greenfield sharpens an idea you can hold in one session, wayfinder is for the effort you can't. When the map clears, **it hands off** into the greenfield flow at `/iadc-advisor:to-tickets`.

## Understanding the app, with no build in view

You have **no ticket** — you just need to understand what the app does and how. A new developer landing on the codebase, or catching up on an unfamiliar area.

- **`/iadc-advisor:orient`** — a single **cited briefing** on the app (or one area, or one object): the shape and its hubs, the data model as an ERD, the decisions behind it, and what's in flight. It composes the inspection skills below — the graph, the live environment, the board, and the glossary + ADRs — into the narrated answer to "how does our app work." It's the packaged form of `/iadc-graph:iadc-graph` + `/iadc-advisor:appian`; reach for those raw when you know the exact edge you want, and for `/iadc-advisor:orient` when you want the synthesis. The boundary with `/iadc-advisor:pressure-test` is simple: **have a build in view → `/iadc-advisor:pressure-test`; just understanding → `/iadc-advisor:orient`.**

## Appian knowledge & inspection

The domain skills that let the architect answer questions and ground plans in the real Appian application — the steps `/iadc-advisor:pressure-test` orchestrates, and the sources `/iadc-advisor:orient` composes. All are **read-only** — inspect and advise, never mutate.

- **`/iadc-advisor:appian`** — the Appian domain layer: naming conventions, relationship rules, data-modeling patterns, dependency order, SAIL, security. Load before touching the Appian MCP (which runs read-only). Use it to inspect the environment and pressure-test a design against how Appian actually works.
- **`/iadc-graph:iadc-graph`** — traverse the application's dependency graph (the `iadc` MCP) to answer structural questions: what calls this, what's the blast radius of a change, how do these objects relate, what's the record model. This is also how you understand how an existing feature of *this app* already works (or, packaged into a briefing, via `/iadc-advisor:orient`).
- **`/iadc-advisor:context7`** — semantic search over Appian **platform** documentation (first stop for "how does Appian do…/what's the function for…"). Confirm version-sensitive answers against the authoritative `docs.appian.com` via `/iadc-advisor:appian`. (Understanding how *your own* app works is the different question above — that's `/iadc-graph:iadc-graph` + `/iadc-advisor:appian`.)
- **`/iadc-advisor:jira`** — read the Jira board (via the Jira MCP) for context: what's planned, in flight, decided, blocked, or already tracked. Grounds the advisor's planning and answers in what the team is actually tracking. Read-mostly; light gated comments only (Jira is human-first here).
- **`/iadc-advisor:office`** — read **Microsoft 365** source-of-truth documents (SharePoint/OneDrive requirements, specs, process docs) and Teams/Outlook discussion, via the Microsoft 365 connector. Grounds planning in what the spec actually says — `/iadc-advisor:pressure-test` searches these by ticket key. **Read-only**: find and cite, never send, upload, or edit.

## Vocabulary underneath

A model-invoked reference that runs *beneath* the other skills — the single source of truth for domain language. Reach for it directly when the **words**, not the process, are the problem; or let the skills above pull it in.

- **`/iadc-advisor:domain-modeling`** — sharpen the project's *domain* language: challenge a fuzzy term, resolve an overloaded word ("account" doing three jobs), record a hard-to-reverse decision as an ADR. It's the active discipline `/iadc-advisor:pressure-test` and `/iadc-advisor:interrogate-with-docs` drive to keep the project glossary (`outputs/CONTEXT.md`) clean. (Project glossary and decision records are written to the `outputs/` workspace — git-ignored where `/iadc-advisor:setup`'s ignore rules were accepted; see `/iadc-advisor:pressure-test`.)

## Crossing sessions

- **`/iadc-advisor:handoff`** — when a thread is full or you need to branch off, this compacts the conversation into a markdown file. You don't continue in place — you **open a new session and reference that file** to carry the context across. Use it when you want a **fresh session** but need the **current conversation preserved**.
- **`/compact`** (built-in) — stay in the **same conversation**, letting earlier turns be summarized. Use it at **intentional breaks between phases**. `/iadc-advisor:handoff` forks; `/compact` continues.

## Standalone

Off the main flow entirely.

- **`/iadc-advisor:interrogate-me`** — the same relentless interview as `/iadc-advisor:interrogate-with-docs`, but stateless: it saves nothing locally, builds no `CONTEXT.md`. Reach for it to sharpen any plan or design that doesn't need a paper trail.
- **`/iadc-advisor:research`** — delegate reading legwork to a **background agent**: it investigates a question against **primary sources**, then leaves a cited Markdown file in the repo. Keep working while it reads. What it produces feeds the thinking at `/iadc-advisor:interrogate-with-docs`; it doesn't replace it.
- **`/iadc-advisor:to-diagram`** — render a diagram (flowchart, sequence, ERD, state machine, …) from what's in context: it picks the right type, gets the syntax right, saves it to `outputs/`, and presents it as an artifact. Directly invocable ("diagram how these records relate"), and the flow skills pull it in — `/iadc-advisor:orient` (topology + ERD), `/iadc-advisor:to-spec` (build-step DAG), `/iadc-advisor:pressure-test` (blast radius), `/iadc-advisor:to-tickets` (ticket dependency graph).

## Precondition

**`/iadc-advisor:setup`** — run once before your first flow. It materializes this project's own state **into this repo**, since the plugin itself ships none of it: `.mcp.json` (the MCP servers and their literal credentials), `docs/agents/project.md` (the project configuration the session hook injects and six skills read), the `.gitignore` entries that keep those out of git, the `outputs/` workspace, and the issue-tracker and domain-doc config the other skills assume — then verifies every connection is live.
