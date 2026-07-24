# Appian Architect-in-a-Box — Plugin Design

The working vocabulary for building and maintaining this plugin *itself* — how the
product is structured, shipped, and reasoned about. This is maintainer vocabulary; it
is **not** the domain language of any client's Appian application. That lives in the
client's own `CONTEXT.md`, in the client's repo (see `docs/adr/0001`).

## Language

### Product and repository

**Plugin**:
The shippable artifact — the Claude Code plugin named `iadc-advisor`: everything under
`iadc-advisor/` (skills, the session hook, templates), installed by clients at project
scope from this repo's marketplace. The product this repo produces.

**Marketplace**:
This repo's `.claude-plugin/marketplace.json`, which lists the plugin. Clients add it
once (`/plugin marketplace add`), then install and update the plugin from it.

**Workshop**:
This repo, where the plugin is developed. Its root is the maintainer's dev
environment — auto-discovered by Claude Code — and is never shipped.

**Per-project state**:
Everything `/setup` materializes into a client app repo: the gitignored `.mcp.json`,
the `docs/agents/*.md` configuration (including `project.md` and the gitignored
per-person `project.local.md`), and the `outputs/` workspace. The plugin ships the
intelligence; the app repo holds the per-project state.

**Session hook**:
The plugin's SessionStart hook — the replacement for the shipped `CLAUDE.md` (plugins
cannot load one). Injects the operating posture plus `project.md`/`project.local.md`
into every session in an app repo where the plugin is enabled.

**Dev docs**:
Design docs about *building the plugin* — this `CONTEXT.md` and `docs/adr/`. They sit
at the workshop root, are shared among the plugin's
maintainers, and are never shipped.

**Usage docs**:
The `CONTEXT.md` and ADRs a *client* produces when they use the plugin on their own
Appian app. They live in the client's repo and describe the client's project; the
plugin never ships them.

### Flow and posture

**Spine** (a.k.a. the main flow):
The primary path most work travels through the skills. Per `docs/adr/0006` (which superseded
`docs/adr/0002`), it starts from a defined unit of work — a ticket or a description of it — and
runs `ticket → /pressure-test → (/reconcile) → /to-spec`, ending in a build spec.

**Pressure-test** (`/pressure-test`):
The spine's entry point — the **dialectic**. A relentless, one-question-at-a-time Socratic
interview that *asks but does not answer*: it grounds in the app first, then sharpens the
developer's approach to a defined ticket. (Formerly `gumby`.)

**Reconcile** (`/reconcile`):
Closes the loop when `/pressure-test` escalated an architectural gap to the project lead — folds the
reply into the ticket's decisions and flips it `BLOCKED → READY`. (Formerly `gumby-reconcile`.)

**To-spec** (`/to-spec`):
Turns the sharpened plan into a developer-ready **build spec** — PRD context plus an ordered,
executable list of Appian build steps — written to the `outputs/` workspace on approval. (Formerly
`pokey`; distinct from the retired greenfield PRD skill of the same name — see `docs/adr/0006`.)

**To-diagram** (`/to-diagram`):
The shared **diagram primitive** — renders a Mermaid diagram (app topology, ERD, blast radius,
build-step DAG, status lifecycle, …), saves it to `outputs/`, and presents it as an artifact.
Pulled in by `/orient`, `/pressure-test`, `/to-spec`, and `/to-tickets`. See `docs/adr/0007`.

**On-ramp**:
A starting situation that generates planning work and then merges onto the spine —
e.g. `wayfinder` for a huge, foggy effort.

**Handoff point**:
The moment advisory output leaves the plugin for execution elsewhere. The plugin plans
up to this point and stops.

**Advisory posture**:
The house rule that the plugin only inspects, reasons, plans, and hands off — it never
writes application code or mutates Appian design objects.
_Avoid_: read-only (that's the MCP mode, narrower than the posture)
