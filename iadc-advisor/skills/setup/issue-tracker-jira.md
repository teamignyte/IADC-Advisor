# Issue tracker: Jira

> **Seed template.** `/iadc-advisor:setup` copies this into `docs/agents/issue-tracker.md` and fills the
> `<PLACEHOLDERS>` for your project. Replace the example workstream labels with your own.

Issues and PRDs for this repo live in a **Jira board** — project key **`<PROJECT_KEY>`**. Drive the
tracker **only through the Jira MCP** (the Atlassian connector). Jira here is **human-first**: the
architect **reads** the board freely and does at most **light, gated writes** — never bulk changes.

## Mechanism: the Jira MCP

All Jira access goes through the **Jira MCP connector** — search, read, create, comment, transition,
link. Connect it in your Claude client's connector settings (Atlassian); it authenticates via the
connector, so there are no tokens or URLs to configure here.

**Reads are free. Every write is gated:** propose the change, get an explicit yes, then write — and
verify it landed by a fresh read, not by the tool's response. Never bulk-mutate the board without
showing the list first. Because Jira is human-first, prefer *reporting* a needed change over making
it; reserve writes for light, low-risk touch-ups (a label, a comment, a status transition).

> **Known MCP gap:** the Jira MCP can create an issue link but **cannot delete or flip one**. A
> wrong-direction or duplicate link is *reported for a human to fix in Jira*, not corrected by the agent.

## Board model

- **Issue types:** `Epic` (one per feature — the grouping level), `Task` (a unit of work),
  `Subtask` (rarely needed).
- **Columns / statuses (execution lifecycle)** — each is a real board column; set the status via a
  transition, never encode it as summary text or a label: `To Do` (default for a new Task),
  `In Progress`, `In Review`, `Done`, and typically a `Deferred` column for parked-but-kept work.
- **Lifecycle is a column, not text.** A card's state lives in its status. Don't prefix the summary
  ("Deferred: …", "WIP: …") or invent labels to convey it — that duplicates the column and drifts.
- **Triage roles are Jira _labels_, not columns** (orthogonal to lifecycle — a `To Do` card carries a
  readiness label). See `docs/agents/triage-labels.md`.
- **Grouping:** every Task belongs to a feature Epic via its `parent`. Start a new feature by creating
  an Epic first, then parent its Tasks to it.

## Workstream label axis (customize per project)

Cutting *across* the feature Epics is a second axis — your product **workstreams / layers** — carried
by **labels**. This is the one project-specific section: **replace the example below with your
project's own controlled label set**, and keep it in sync with `docs/agents/triage-labels.md`.

> _Example only — replace with your workstreams:_
>
> | Label | Meaning |
> |---|---|
> | `<workstream-a>` | first major workstream |
> | `<workstream-b>` | second major workstream |
> | `<shared-substrate>` | shared foundation serving multiple workstreams |

**Assignment principle:** tag a ticket with the workstream(s) whose *deliverable* it produces
(multi-output → multiple labels). Leaf Tasks carry their own labels; an Epic carries the union of its
children's. Filter by the axis with JQL, e.g. `project = <PROJECT_KEY> AND labels = <workstream-a>`.

**Canonical label set** (don't invent ad-hoc labels): the workstream axis labels above · the triage
labels (`docs/agents/triage-labels.md`) · any durable topical workstream labels you define. The
`jira` skill reads the board and can note stray/misspelled variants in passing.

## Preferred issue format

Every issue carries three parts. Keep the human part jargon-free; put technical depth in the agent part.

### Summary (human)
- **Now:** current state / behavior
- **Want:** desired end-state behavior
- **Why:** the reason it matters — the value delivered or problem solved

### Acceptance criteria
Observable, testable outcomes — the contract. Include a discriminating control where one applies.

### Agent notes (technical)
Files, ADR links, discriminating controls, gotchas. Scale to the ticket; omit for trivia.

### Title (summary) scheme
A plain imperative phrase naming the outcome ("Make X do Y"). **No** `NN —` numeric prefixes, phase
prefixes, or `SN:` prefixes — the workstream is a **label** (see above), never part of the title.

### State lives in Jira, not the body
Don't carry `Source:`, `Status:`, or `Type:` header lines in the description: status is the **column**,
readiness is a **triage label**. New tickets (via `to-tickets`) follow this shape. Retrofit
only issues that are **not yet complete** — never rewrite Done tickets.

### Formatting (ADF)
Rich text is stored as **ADF** (Atlassian Document Format). When the MCP renders a description oddly
(a `##` heading swallowed after a list, or a literal `*`/`` ` `` showing through), it's an ADF
conversion artifact — re-author the text cleanly rather than echoing the escaped body back, and
**confirm the result by re-reading the rendered issue**, not the write response.

## Conventions (operation → Jira MCP tool)

Use the Jira MCP tools (Atlassian connector). Reads are free; writes are gated (propose → confirm →
write → verify by re-read). Representative tools:

- **Create an issue** — the MCP `create issue` tool: project `<PROJECT_KEY>`, issuetype `Task`,
  summary, description (the MCP takes Markdown/ADF), `parent` = the feature Epic, labels incl. the
  triage label. For a new feature, create the **Epic** first (issuetype `Epic`, no parent). A new
  issue lands in `To Do`.
- **Link a dependency (blocker)** — the MCP `create issue link` tool, type `Blocks`: **inward =
  blocker, outward = blocked** ("A blocked by B" → inward B, outward A). Keep a human-readable
  `Blocked by <KEY>` line in the body too. **The MCP cannot delete a link** — report wrong-direction
  links for manual fix.
- **Read an issue** — the MCP `get issue` tool. Read the rendered text (description is ADF).
- **List / query** — the MCP `search (JQL)` tool, e.g.
  `project = <PROJECT_KEY> AND status = "To Do" AND labels = ready-for-agent ORDER BY key`.
- **Comment** — the MCP `add comment` tool.
- **Apply / change a label** — the MCP `edit issue` tool (read the current label set, keep what stays,
  add/remove the rest).
- **Move across columns / close** — the MCP `get transitions` tool to find the transition, then the
  `transition issue` tool. `wontfix` = the `wontfix` label plus a transition to `Done`.

## Wayfinding operations

How `wayfinder` expresses its map on this tracker:

- **Map** — a Jira `Epic` (or a Task on a flat board) labelled `wayfinder:map`. Its body holds the
  Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope sections.
- **Child ticket** — a `Task` parented to the map Epic, labelled `wayfinder:<type>`
  (`research`/`prototype`/`interrogating`/`task`). The question goes in the body.
- **Blocking** — the native `Blocks` link (above); the frontier renders visually on the board.
- **Claim** — assign the ticket to the driving user before any work (an open, unassigned child is
  unclaimed).
- **Frontier query** — `project = <PROJECT_KEY> AND parent = <MAP_KEY> AND statusCategory != Done AND
  assignee IS EMPTY` (via the MCP search tool); unblocked children are those with no open blockers.

## When a skill says "publish to the issue tracker"

Create a `Task` in project `<PROJECT_KEY>` via the Jira MCP, parented to the relevant feature Epic
(create the Epic first if the feature is new). Apply the appropriate triage label from
`docs/agents/triage-labels.md`. Propose first; write on confirmation.

## When a skill says "fetch the relevant ticket"

Use the Jira MCP `get issue` tool for `<PROJECT_KEY>-<n>` (the user will normally pass the key).
