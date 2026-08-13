---
name: orient
description: Get oriented in an Appian application when you have NO ticket or build in view — you just need to understand what the app does and how it does it. Composes the dependency graph, the Jira board, and the domain docs (the glossary + ADRs) into one cited briefing. Use this for a new developer landing on the app, for catching up on an unfamiliar area ("what is the Claims record model", "how does billing hang together"), or for a single-object dossier. Do NOT use it when you have a ticket or a defined task in hand — that's /iadc-advisor:pressure-test, which orients you *toward a build*.
disable-model-invocation: true
argument-hint: "an area or object to orient on, or nothing for the whole app"
---

# Orient

Answer **"what does this app do, and how does it do it"** — for someone with no build in view yet. A new developer landing on the codebase, or an experienced one dropped into an unfamiliar corner, needs a *map* before they need anything else: the shape of the app, the objects that carry it, the data model, the decisions that explain why it's built this way, and where it's heading.

This skill produces that map as a single **cited briefing**. It doesn't interview you and it doesn't plan a change — it reads the real application from every grounding source the plugin has and narrates what it finds.

## When this — and when something else

The line is **do you have a build in view?**

- **A ticket or a described task in hand** — "how do I build TICKET-123", "what's my approach for adding X" → **`/iadc-advisor:pressure-test`** (then `/iadc-advisor:to-spec`). That flow also orients you in the app, but *toward a build*, and ends in a build spec. Orientation there is a means; here it's the whole point.
- **Just understanding, no build** — "what is this app", "how does the Claims model work", "explain this object to me" → **you're in the right place.**
- **A single Appian platform question** with no app attached — "what does `a!queryEntity` do" → that's **`/iadc-advisor:context7`** + `/iadc-advisor:appian`, not this.

Orient is the *packaged, narrated* form of what `/iadc-graph:iadc-graph` + `/iadc-advisor:appian` + `/iadc-advisor:jira` do as raw primitives. Reach for those directly when you already know exactly what one edge or one object you want; reach for orient when you want the synthesis and don't yet know what to ask.

## Read-only, always

Everything here inspects. The graph MCP is read-only by nature; Jira is read-only for orientation (no comments, no writes — orientation is not a board action). The only thing orient writes on its own is the briefing it hands back to you; any diagram it draws (via `/iadc-advisor:to-diagram`) is *presented*, and saved to `outputs/` only if you approve — so orientation stays a read-only act.

## Scope the ask first

One question, only if it's ambiguous: **the whole app, one area, or one object?** That answer decides how much of the graph you pull — it's the difference between `graph_overview` across everything and `reachable` from a single starting node. Don't interrogate beyond this; orientation is exposition, not the interview primitive.

## The process

Sequenced so each layer tells the next one where to look — cheap context first, then the graph to find *what matters*, then meaning and direction, then synthesis.

### 1. Read the cheap grounding first

Before touching a tool, read the project glossary (`outputs/CONTEXT.md`, the project's ubiquitous language) and the ADRs alongside it in the `outputs/` workspace, plus `docs/agents/domain.md` if present. This costs almost nothing and gives you the team's **vocabulary and the "why"** up front — so when the graph shows you an object, you already have the team's name for it and any decision that shaped it. Load `/iadc-advisor:domain-modeling` if you need to reason about the language itself.

### 2. Seed the graph

Load the **`/iadc-graph:iadc-graph`** skill first — it is mandatory before any `iadc` call and carries the session lifecycle and node-id rules the tool schemas can't express. Then `seed` the configured application — its UUID is in the ambient **Project configuration** (the `Application` entry, written by `/iadc-advisor:setup`), so there's no live lookup — and poll `seed_status` until it's ready. Respect the 30-minute TTL, and `close` the session when you're done (step 6).

### 3. Find what matters — don't dump the inventory

A newcomer needs the handful of objects that *run* the app, not an alphabetized list of hundreds.

- `graph_overview` for the counts by kind / object_type — the app at a glance.
- Rank by **node degree** to surface the **hubs** (high fan-in / fan-out objects) — these are what to learn first.
- `list_nodes` on entry-point kinds (**sites, portals**) for the **user-facing surfaces** — the top of the call chains, where the app is actually used. `shortest_path` from a surface down to a hub shows how a click reaches the core.

For a scoped or single-object ask, resolve a starting `node_id` with `find_nodes` — the graph holds the whole application, so it resolves its own nodes by name — and traverse out from there with `reachable` / `get_neighbors` instead of surveying the whole graph.

### 4. Draw the data model

`record_model` → render a **Mermaid ERD** via `/iadc-advisor:to-diagram`. The record model is the backbone a new developer orients around fastest, and the ERD is the single most reusable artifact this skill produces — worth including whenever the data model is in scope.

### 5. Bind structure to meaning, and add direction

- **Meaning:** map each hub back to its glossary term (`outputs/CONTEXT.md`) and any ADR that explains its shape. This is the step the graph alone can't do — the graph shows the wiring, the docs say *why* the wiring is like that. Confirm any Appian platform mechanic against `/iadc-advisor:context7` (then `docs.appian.com` at the environment's version via `/iadc-advisor:appian`) rather than asserting it from memory.
- **Direction:** load `/iadc-advisor:jira` and read the board (read-only) for work in flight or planned against those hubs, so orientation includes where the app is *going*, not just its frozen structure.

### 6. Synthesize one cited briefing

Close the graph session, then hand back a single narrated document, top-down:

1. **What the app does** — one paragraph, in the team's own vocabulary.
2. **The shape** — the hubs and how they connect; the user-facing surfaces. Render this as a
   **topology flowchart** via `/iadc-advisor:to-diagram` (hubs as nodes, their edges between them, the
   user-facing surfaces pinned at the top).
3. **The data model** — the Mermaid ERD (from step 4, via `/iadc-advisor:to-diagram`).
4. **Why it's built this way** — the decisions (ADRs) behind the structure.
5. **Where it's heading** — what's in flight on the board.

**Every claim carries a citation** — a graph node/edge, an ADR, or a ticket — per the plugin's house rule that answers are grounded in sources. A briefing the reader can't trace back is worse than no briefing.

## After the map

Offer the natural next move rather than stopping cold:

- **Zoom into one object** — the single-object dossier: attributes (`get_node`), who calls it (`callers_of`), what it reaches (`reachable`), and the platform mechanics behind it (`/iadc-advisor:context7`). This is just orient re-run at object scope.
- **Go deeper on the Appian platform** — `/iadc-advisor:context7` + `/iadc-advisor:appian` for how the platform itself works.
- **A build has emerged** — if orientation surfaced a concrete task, that's the handoff to **`/iadc-advisor:pressure-test`** (then `/iadc-advisor:to-spec`).
