# Appian Architect-in-a-Box

An **Appian architect, in a box.** This is a Claude Code plugin that turns Claude into an advisory architect for your Appian projects. Its main job: help a developer work out **how to build the ticket in front of them** — getting oriented in your application (what a change touches, its blast radius, the objects involved), sharpening the approach, and leaving an implementation note. It also answers questions about your Appian application from the real source of truth and, for net-new work, turns a rough idea into a spec and a ready-to-build ticket breakdown.

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

Declare **both** the marketplace and the plugin at **project** scope, from your Appian
app's repo — that writes them into the repo's `.claude/settings.json`, so a teammate who
clones it can resolve the plugin. (A project-scope plugin whose marketplace lives only on
your machine simply reports as not installed for everyone else, with nothing to explain
why.)

1. **Add the marketplace** (once per repo), from a terminal in that repo:
   `claude plugin marketplace add <this repo's git URL> --scope project` — access uses the
   same credentials as the repo.
2. **Install the plugin** (once per repo):
   `claude plugin install iadc-advisor@ignyte --scope project`. Commit the resulting
   `.claude/settings.json`.

   **Desktop app:** there's no shell for those two commands — use the `/plugin` browser
   instead: add the marketplace by URL, then install **iadc-advisor** from **ignyte** at
   **project** scope.
3. **Each teammate installs on their first session.** The commit records the plugin; it
   doesn't install it for them. Claude Code prompts each teammate to install it when they
   first open the repo — they accept once, and there's nothing else to configure.
4. **Run `/setup`** in that repo. It generates the gitignored `.mcp.json` (graph, Appian,
   docs — literal values, no secrets tracked), writes the project configuration
   (`docs/agents/project.md` — Appian version, application UUID, audience, escalation),
   points the Jira/Microsoft 365 connectors, lays out the tracker + domain docs and the
   `outputs/` workspace — then verifies everything connects.
5. **Ask `/which-skill`** any time you're not sure which flow fits.

Updates: `claude plugin update iadc-advisor`, then start a fresh session — the update only
takes effect on restart. See `CHANGELOG.md` for what changed.

## The main flow

```
your ticket  →  /pressure-test  →  /to-spec  →  build spec  →  (you build)
```

You have a ticket (or a described task). **`/pressure-test`** orients you in the app — what the change touches, its blast radius, the objects involved, the project's own docs — then runs a one-question-at-a-time Socratic dialectic that *asks but doesn't answer*, so you sharpen the approach yourself. When it's confirmed, **`/to-spec`** turns the conversation into a developer-ready **build spec** (the context plus an ordered list of Appian build steps), shown for your review and written only on your approval. It advises; you build.

**No ticket yet — shaping net-new work?** Use the greenfield flow: `/interrogate-with-docs → /to-tickets`, then hand the tickets to your team (who each start them with `/pressure-test`). For an effort too big to hold in one session, start with `/wayfinder`; when its map clears it merges into `/to-tickets`.

## Configuration & secrets

Nothing secret is ever committed: `/setup` writes real credentials only to the gitignored
`.mcp.json`, and your personal role override lives in the gitignored
`docs/agents/project.local.md`. Jira and Microsoft 365 connect as Claude connectors — no
tokens on disk. The committed `docs/agents/project.md` holds only team-shared,
non-secret values.
