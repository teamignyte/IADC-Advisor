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
scope from the **Catalog**. The product this repo produces.

**Catalog**:
`IADC-Marketplace`'s `.claude-plugin/marketplace.json`, which lists this plugin alongside the
rest of the IADC family. It is a *separate repo* — this one is only the workshop. Clients
declare it at **project scope, once per app repo**
(`claude plugin marketplace add https://github.com/teamignyte/IADC-Marketplace.git --scope project`),
then install and update the plugin from it.
_Avoid_: marketplace (ambiguous — the catalog file, the repo holding it, and the `ignyte`
registration are three different things) The `/plugin marketplace add` slash form takes no `--scope` and
lands at **user** scope — which leaves the repo declaring a plugin its teammates cannot
resolve, so it is not the path to hand a client.

**Workshop**:
This repo, where the plugin is developed. Its root is the maintainer's dev
environment — auto-discovered by Claude Code — and is never shipped.

**Per-project state**:
A family **convention**, not a term this plugin defines — see
`docs/agents/per-project-state.md` in the umbrella (family
[ADR 0009](https://github.com/teamignyte/IADC/blob/main/docs/adr/0009-umbrella-owns-per-project-state-convention.md)).

**`.mcp.json`**:
The gitignored MCP server configuration at the client app repo's root. Holds literal
credential values, never `${VAR}` — the Windows Desktop app does not expand it. See
`docs/adr/0004`.

**`outputs/`**:
The workspace `/setup` creates at the client app repo's root for generated planning
artifacts — the domain glossary, decision records/ADRs, and build specs the advisory
skills produce. Git-ignored where `/setup`'s ignore rules were accepted; in that case
`outputs/README.md` is the only file tracked inside it. See `docs/adr/0005`.

**Session hook**:
The plugin's SessionStart hook — the replacement for the shipped `CLAUDE.md` (plugins
cannot load one). Injects the operating posture plus `advisor.md`/`advisor.local.md`
on `startup`, `clear`, and `compact` in an app repo where the plugin is enabled — deliberately
**not** on `resume`/`fork`, whose transcript already carries whatever the preceding `startup`/
`clear`/`compact` injected (see `docs/adr/0012`). Not "every session": a long-lived session that
is only ever resumed, never cleared or compacted, gets this exactly once.

**Dev docs**:
Design docs about *building the plugin* — this `CONTEXT.md` and `docs/adr/`. They sit
at the workshop root, are shared among the plugin's
maintainers, and are never shipped.

**Usage docs**:
The `CONTEXT.md` and ADRs a *client* produces when they use the plugin on their own
Appian app. They live in the client's repo and describe the client's project; the
plugin never ships them.

**Doubled path**:
A file path that names a **Dev doc** here and a **Usage doc** in a client's repo — the same
name, two documents, two repositories. `docs/agents/` is the standing example: `domain.md`
exists in both senses, and `skills/setup/` holds seed *templates* whose prose refers to the
client's copy, not this repo's. So a search for one of these names returns hits belonging to
two different projects, and a hit is not evidence that this repo's copy is still needed.
_Avoid_: duplicate, shared doc (neither is a copy of the other)

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
