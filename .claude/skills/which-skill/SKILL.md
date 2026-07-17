---
name: which-skill
description: Ask which skill or flow fits your situation. A router over the skills in this Appian architect-in-a-box bundle.
disable-model-invocation: true
---

# Which Skill

You don't remember every skill, so ask. This is a router over the skills in this bundle — an **advisory Appian architect**. It interrogates and sharpens dev planning, answers questions about an Appian application, and produces specs and ticket breakdowns. It does **not** write code or build Appian objects; execution happens outside this bundle.

A **flow** is a path through the skills. Most planning work runs along one **main flow**; two **on-ramps** merge onto it. Everything else is a standalone tool or a vocabulary layer that runs underneath.

## The main flow: idea → handoff-ready plan

The route most planning travels. You have an idea and want it sharpened into something a developer can pick up and build.

1. **`/interrogate-with-docs`** — sharpen the idea by interview. Start here when the project **has a domain model**: it's stateful, retaining what it learns in `CONTEXT.md` and ADRs. (No `CONTEXT.md`/codebase to ground against? Use `/interrogate-me` — see Standalone. Both run the same `/interrogating` primitive; `interrogate-with-docs` is the one that leaves a paper trail.)
2. **`/to-spec`** — turn the sharpened thread into a spec (a PRD). Synthesis only, no re-interview.
3. **`/to-tickets`** — split the spec into tracer-bullet tickets, each declaring its **blocking edges**. On a local tracker that's one file per ticket; on a real tracker (Jira, etc.) the edges become native blocking links, so any ticket whose blockers are done can be grabbed.

**This is the handoff point.** The tickets go to developers (or coding agents) *outside* this bundle to implement. The architect-in-a-box plans and hands off — it does not build.

### Context hygiene

Keep steps 1–3 in **one unbroken context window** so the interrogation, spec, and tickets all build on the same thinking. If a session gets too long before `/to-tickets`, don't push on degraded — `/handoff` and continue in a fresh thread (see Crossing sessions).

## Working a specific ticket

The default way to start when you've been handed a ticket.

- **`/gumby`** — **the dialectic.** When you're working on a specific ticket and want to pressure-test the approach *before* building. A relentless, **one-question-at-a-time Socratic** interview that asks but doesn't answer — *you* do the reasoning — grounded in the live app (the Jira ticket, the graph, the Appian environment, the project's own docs) and captured to `CONTEXT.md`/ADRs. Say "I'm working on a ticket" and this is where you land. (Its sibling `/interrogate-with-docs` runs the same kind of interview but *proposes* answers as it goes — reach for Gumby when you want to think it through yourself.)
- **`/pokey`** — **the build spec.** After Gumby, turns the sharpened plan into a developer-ready build spec (PRD context + ordered Appian build steps). It lays the spec out for your review and takes final questions, then writes it to the **local workspace** only once you approve. `ticket → /gumby → /pokey`. **Supersedes `/to-tickets` and `/to-spec`** for ticket-driven work.

## On-ramp

A starting situation that generates planning work, then merges onto the main flow.

- **A huge, foggy effort — too big for one session** → **`/wayfinder`**, the most cognitively demanding flow here. When the way from here to the destination isn't visible yet, it charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time — producing **decisions and ADRs, not deliverables** — until the fog clears. Where `/interrogate-with-docs` sharpens an idea you can hold in one session, wayfinder is for the idea you can't. When the map clears, **it hands off**: merge onto the main flow at `/to-spec`.

## Appian knowledge & inspection

The domain skills that let the architect answer questions and ground plans in the real Appian application. All are **read-only** — inspect and advise, never mutate.

- **`/appian`** — the Appian domain layer: naming conventions, relationship rules, data-modeling patterns, dependency order, SAIL, security. Load before touching the Appian MCP (which runs read-only). Use it to inspect the environment and pressure-test a design against how Appian actually works.
- **`/iadc-graph`** — traverse the application's dependency graph (the `iadc` MCP) to answer structural questions: what calls this, what's the blast radius of a change, how do these objects relate, what's the record model.
- **`/context7`** — semantic search over Appian documentation (first stop for "how do I…/what's the function for…"). Confirm version-sensitive answers against the authoritative `docs.appian.com` via `/appian`.
- **`/jira`** — read the Jira board (via the Jira MCP) for context: what's planned, in flight, decided, blocked, or already tracked. Grounds the advisor's planning and answers in what the team is actually tracking. Read-mostly; light gated comments only (Jira is human-first here).
- **`/office`** — read Microsoft 365 (via the connector) for context: SharePoint/OneDrive requirements and design docs, and Teams/Outlook discussion where decisions were recorded. Grounds planning in what the spec actually says. Read-only — find, read, cite; never send or edit.

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
- **`/teach`** — learn a concept over multiple sessions, using the current directory as a stateful workspace. Good for onboarding a new developer onto the domain or the Appian platform.

## Precondition

**`/setup`** — run once before your first flow to configure this bundle for your project: connect the MCP servers, set your Jira project key and Appian/graph endpoints, and lay out the issue tracker and domain docs the other skills assume.
