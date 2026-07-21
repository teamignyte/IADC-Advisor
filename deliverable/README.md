# Appian Architect-in-a-Box

An **Appian architect, in a box.** This is a Claude Code bundle that turns Claude into an advisory architect for your Appian projects. Its main job: help a developer work out **how to build the ticket in front of them** — getting oriented in your application (what a change touches, its blast radius, the objects involved), sharpening the approach, and leaving an implementation note. It also answers questions about your Appian application from the real source of truth and, for net-new work, turns a rough idea into a spec and a ready-to-build ticket breakdown.

It's built for two audiences:

- **Developers building tickets** — the day-to-day path. Start from a ticket or a described task and work out *how* to implement it in this app: where it lives, what it touches, the Appian patterns to use, a sharpened approach, and a short implementation note. Answers are drawn from the live environment, the application's dependency graph, the Jira board, the team's documents, and the official Appian docs.
- **Architects and leads** — pressure-test a design before anyone builds it, shape net-new work into specs and tickets, break big foggy efforts into a resolvable map of decisions, and keep the plan grounded in how the application actually works.

The architect **advises and plans**; your developers build. It reads and reasons; it doesn't ship code.

## What it can do

- **Work out how to build a ticket** — from a Jira ticket or a described task, get oriented in the app (blast radius, objects, platform how-to), sharpen the approach by interview, and leave a short implementation note (posted to the ticket on request).
- **Interrogate a plan** relentlessly, one question at a time, until the thinking is sharp — capturing the resulting glossary and decisions as `CONTEXT.md` and ADRs.
- **Turn a conversation into a spec**, then split the spec into tracer-bullet tickets with proper blocking edges, published to your tracker.
- **Chart the way through a huge, foggy effort** as a shared map of decision tickets, resolved one at a time.
- **Answer "how does our app work"** — with `/orient`, a single cited briefing that composes the dependency graph, the live environment, the Jira board, and your domain docs into the shape of the app, its data model, the decisions behind it, and what's in flight. Ideal for onboarding a new developer or catching up on an unfamiliar area. (Or go straight to the raw graph — what calls this, what breaks if I change it, how these objects relate.)
- **Answer "how does Appian work"** with semantic search over the Appian documentation, confirmed against the official docs at your environment's version.
- **Inspect your Appian environment** directly (read-only) to ground advice in the real configuration.
- **Read your requirements and design documents** from SharePoint / OneDrive, and pull context from Teams and Outlook. _(Planned — the Office/SharePoint integration isn't built yet.)_
- **Read your Jira board for context** — what's planned, in flight, decided, blocked, or already tracked — so the architect's planning and answers are grounded in the work your team is actually tracking. (Jira stays human-first; the architect reads, and writes only light comments on request.)
- **Research a question** against primary sources in the background, leaving a cited Markdown file in the repo.

## Getting started

1. **Clone** this repo and open it in Claude Code.
2. **Run `/setup`.** It walks you through connecting the MCP servers (graph, Appian, docs) and the Jira connector, setting your Jira project key and Appian/graph endpoints, and laying out your issue tracker and domain docs — then verifies everything connects.
3. **Ask `/which-skill`** any time you're not sure which flow fits your situation. It's the router over the whole toolkit.

## The main flow

```
your ticket  →  /gumby  →  /pokey  →  build spec  →  (you build)
```

You have a ticket (or a described task). **`/gumby`** orients you in the app — what the change touches, its blast radius, the objects involved, the project's own docs — then runs a one-question-at-a-time Socratic dialectic that *asks but doesn't answer*, so you sharpen the approach yourself. When it's confirmed, **`/pokey`** turns the conversation into a developer-ready **build spec** (the context plus an ordered list of Appian build steps), shown for your review and written only on your approval. It advises; you build.

**No ticket yet — shaping net-new work?** Use the greenfield flow: `/interrogate-with-docs → /to-spec → /to-tickets`, then hand the tickets to your team (who each start them with `/gumby`). For an effort too big to hold in one session, start with `/wayfinder`; when its map clears it merges into `/to-spec`.

## Configuration & secrets

The bundle ships as a template, so no secrets live in tracked files. Copy the committed `.mcp.json.example` → `.mcp.json` and fill in your real MCP credentials (graph endpoint + key, Appian environment); the real `.mcp.json` is gitignored. Jira connects as a Claude connector (no tokens to store). `/setup` handles all of this and confirms each connection is live.
