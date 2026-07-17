---
name: which-skill
description: Ask which skill or flow fits your situation. A router over the skills in this Appian architect-in-a-box bundle.
disable-model-invocation: true
---

# Which Skill

You don't remember every skill, so ask. This is a router over the skills in this bundle — an **advisory Appian architect**. It helps a developer figure out **how to build the ticket in front of them**, answers questions about an Appian application, and — for net-new work — sharpens planning into specs and ticket breakdowns. It does **not** write code or build Appian objects; execution happens outside this bundle.

A **flow** is a path through the skills. Most work runs along the **main flow**; the other two flows are for when the work *isn't* a defined build. Everything else is a standalone tool or a vocabulary layer that runs underneath.

## The main flow: a piece of work → how to build it

The route most work travels. You have a **ticket, or a described task**, and you need to work out **how** to build it in this Appian app.

- **`/groundwork`** — start here. From a Jira ticket or a plain description, it orients you in the actual application (what the change touches, its blast radius, the objects involved, the platform how-to), sharpens your approach by interview, and leaves a short implementation note. It's **orient-led** — ground yourself in the app first, then interrogate — and **adaptive**: a one-line change gets a quick pass, a wide-blast-radius change gets the full treatment. It advises and hands off; it does not build.

`/groundwork` uses the inspection skills below (`/jira`, `/iadc-graph`, `/appian`, `/context7`) and the `/interrogating` primitive as its steps. Reach for one of those directly when you only need the single thing it does — but when you're working out how to *build* something, start with `/groundwork` and let it orchestrate them.

## When the work isn't a defined build

Two situations sit outside the main flow. The line is simple: `/groundwork` is for a **defined** piece of work; these are for work that isn't defined yet.

### Greenfield — shaping net-new work into a plan

You have an idea to shape into something a developer can pick up and build — not a ticket to implement.

1. **`/interrogate-with-docs`** — sharpen the idea by interview. Start here when the project **has a domain model**: it's stateful, retaining what it learns in `CONTEXT.md` and ADRs. (No `CONTEXT.md`/codebase to ground against? Use `/interrogate-me` — see Standalone. Both run the same `/interrogating` primitive; `interrogate-with-docs` is the one that leaves a paper trail.)
2. **`/to-spec`** — turn the sharpened thread into a spec (a PRD). Synthesis only, no re-interview.
3. **`/to-tickets`** — split the spec into tracer-bullet tickets, each declaring its **blocking edges**. On a local tracker that's one file per ticket; on a real tracker (Jira, etc.) the edges become native blocking links, so any ticket whose blockers are done can be grabbed.

**This is the handoff point.** The tickets go to developers (or coding agents) *outside* this bundle to implement — where each one becomes a starting point for `/groundwork`.

Keep steps 1–3 in **one unbroken context window** so the interrogation, spec, and tickets all build on the same thinking. If a session gets too long before `/to-tickets`, don't push on degraded — `/handoff` and continue in a fresh thread (see Crossing sessions).

### A huge, foggy effort — too big for one session

- **`/wayfinder`**, the most cognitively demanding flow here. When the way from here to the destination isn't visible yet, it charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time — producing **decisions and ADRs, not deliverables** — until the fog clears. Where greenfield sharpens an idea you can hold in one session, wayfinder is for the effort you can't. When the map clears, **it hands off** into the greenfield flow at `/to-spec`.

## Understanding the app, with no build in view

You have **no ticket** — you just need to understand what the app does and how. A new developer landing on the codebase, or catching up on an unfamiliar area.

- **`/orient`** — a single **cited briefing** on the app (or one area, or one object): the shape and its hubs, the data model as an ERD, the decisions behind it, and what's in flight. It composes the inspection skills below — the graph, the live environment, the board, and `CONTEXT.md` + ADRs — into the narrated answer to "how does our app work." It's the packaged form of `/iadc-graph` + `/appian`; reach for those raw when you know the exact edge you want, and for `/orient` when you want the synthesis. The boundary with `/groundwork` is simple: **have a build in view → `/groundwork`; just understanding → `/orient`.**

## Appian knowledge & inspection

The domain skills that let the architect answer questions and ground plans in the real Appian application — the steps `/groundwork` orchestrates, and the sources `/orient` composes. All are **read-only** — inspect and advise, never mutate.

- **`/appian`** — the Appian domain layer: naming conventions, relationship rules, data-modeling patterns, dependency order, SAIL, security. Load before touching the Appian MCP (which runs read-only). Use it to inspect the environment and pressure-test a design against how Appian actually works.
- **`/iadc-graph`** — traverse the application's dependency graph (the `iadc` MCP) to answer structural questions: what calls this, what's the blast radius of a change, how do these objects relate, what's the record model. This is also how you understand how an existing feature of *this app* already works (or, packaged into a briefing, via `/orient`).
- **`/context7`** — semantic search over Appian **platform** documentation (first stop for "how does Appian do…/what's the function for…"). Confirm version-sensitive answers against the authoritative `docs.appian.com` via `/appian`. (Understanding how *your own* app works is the different question above — that's `/iadc-graph` + `/appian`.)
- **`/jira`** — read the Jira board (via the Jira MCP) for context: what's planned, in flight, decided, blocked, or already tracked. Grounds the advisor's planning and answers in what the team is actually tracking. Read-mostly; light gated comments only (Jira is human-first here).

## Vocabulary underneath

A model-invoked reference that runs *beneath* the other skills — the single source of truth for domain language. Reach for it directly when the **words**, not the process, are the problem; or let the skills above pull it in.

- **`/domain-modeling`** — sharpen the project's *domain* language: challenge a fuzzy term, resolve an overloaded word ("account" doing three jobs), record a hard-to-reverse decision as an ADR. It's the active discipline `/interrogate-with-docs` drives to keep `CONTEXT.md` a clean glossary.

## Crossing sessions

- **`/handoff`** — when a thread is full or you need to branch off, this compacts the conversation into a markdown file. You don't continue in place — you **open a new session and reference that file** to carry the context across. Use it when you want a **fresh session** but need the **current conversation preserved**.
- **`/compact`** (built-in) — stay in the **same conversation**, letting earlier turns be summarized. Use it at **intentional breaks between phases**. `/handoff` forks; `/compact` continues.

## Standalone

Off the main flow entirely.

- **`/interrogate-me`** — the same relentless interview as `/interrogate-with-docs`, but stateless: it saves nothing locally, builds no `CONTEXT.md`. Reach for it to sharpen any plan or design that doesn't need a paper trail.
- **`/research`** — delegate reading legwork to a **background agent**: it investigates a question against **primary sources**, then leaves a cited Markdown file in the repo. Keep working while it reads. What it produces feeds the thinking at `/interrogate-with-docs`; it doesn't replace it.

## Precondition

**`/setup`** — run once before your first flow to configure this bundle for your project: connect the MCP servers, set your Jira project key and Appian/graph endpoints, and lay out the issue tracker and domain docs the other skills assume.
