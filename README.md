# Appian Architect-in-a-Box

An **Appian architect, in a box.** This is a Claude Code bundle that turns Claude into an advisory architect for your Appian projects: it interrogates and sharpens your development planning, answers questions about your Appian application from the real source of truth, and turns a rough idea into a spec and a ready-to-build ticket breakdown.

It's built for two audiences:

- **Architects and leads** — pressure-test a design before anyone builds it, break big foggy efforts into a resolvable map of decisions, and keep the plan grounded in how the application actually works.
- **New developers** — ask questions and learn the domain and the Appian platform, with answers drawn from the live environment, the application's dependency graph, the Jira board, the team's documents, and the official Appian docs.

The architect **advises and plans**; your developers build. It reads and reasons; it doesn't ship code.

## What it can do

- **Interrogate a plan** relentlessly, one question at a time, until the thinking is sharp — capturing the resulting glossary and decisions as `CONTEXT.md` and ADRs.
- **Turn a conversation into a spec**, then split the spec into tracer-bullet tickets with proper blocking edges, published to your tracker.
- **Chart the way through a huge, foggy effort** as a shared map of decision tickets, resolved one at a time.
- **Answer "how does our app work"** by traversing an exact dependency graph of your Appian application (what calls this, what breaks if I change it, how these objects relate).
- **Answer "how does Appian work"** with semantic search over the Appian documentation, confirmed against the official docs at your environment's version.
- **Inspect your Appian environment** directly (read-only) to ground advice in the real configuration.
- **Read your requirements and design documents** from SharePoint / OneDrive, and pull context from Teams and Outlook. _(Planned — the Office/SharePoint integration isn't built yet.)_
- **Read your Jira board for context** — what's planned, in flight, decided, blocked, or already tracked — so the architect's planning and answers are grounded in the work your team is actually tracking. (Jira stays human-first; the architect reads, and writes only light comments on request.)
- **Research a question** against primary sources in the background, and **teach** a concept over multiple sessions.

## Getting started

1. **Clone** this repo and open it in Claude Code.
2. **Run `/setup`.** It walks you through connecting the MCP servers (graph, Appian, docs) and the Jira connector, setting your Jira project key and Appian/graph endpoints, and laying out your issue tracker and domain docs — then verifies everything connects.
3. **Ask `/which-skill`** any time you're not sure which flow fits your situation. It's the router over the whole toolkit.

## The main flow

```
/interrogate-with-docs  →  /to-spec  →  /to-tickets  →  (developers build)
```

Sharpen the idea by interview, synthesize it into a spec, break it into tickets — and hand the tickets to your team (or coding agents) to implement. For an effort too big to hold in one session, start with `/wayfinder` instead; when its map clears it merges back into `/to-spec`.

## Configuration & secrets

The bundle ships as a template, so no secrets live in tracked files. Copy the committed `.mcp.json.example` → `.mcp.json` and fill in your real MCP credentials (graph endpoint + key, Appian environment); the real `.mcp.json` is gitignored. Jira connects as a Claude connector (no tokens to store). `/setup` handles all of this and confirms each connection is live.
