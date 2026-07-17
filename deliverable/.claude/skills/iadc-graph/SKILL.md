---
name: "iadc-graph"
description: "MANDATORY skill for the IADC graph MCP (`iadc` server, tools surfaced as `mcp__iadc__*`, 17 tools). Provides the session lifecycle (seed -> seed_status -> read tools -> close, 30-min TTL), the node-id forms read tools require (never a display name — get a starting node_id from find_nodes/list_nodes, or resolve an Appian object name to its UUID via the Appian MCP first), the 24-relation vocabulary (exact-match string, unknown relation -> [] not an error), the 10 node kinds/object_types, and the return-shape/error conventions the tool schemas can't express (compact enriched records, node_label as the wire key not `name`, occurrences only via get_edge, session-error dict shapes). Load BEFORE calling any `iadc` MCP tool. Covers: seed, seed_status, close, report_changes, get_neighbors, get_node, callers_of, shortest_path, get_out_edges, get_in_edges, get_edge, edges_by_relation, list_nodes, find_nodes, graph_overview, reachable, record_model. Verbs: seed, traverse, find, list, path, callers, neighbors, reachable, blast radius, record model, close session."
---

## Why this matters

The `iadc` MCP grounds impact reasoning in an **exact App Graph** built
from a real Appian export — not a guess from reading SAIL text. It answers
"what calls this," "what breaks if I change this," and "is there a path from
A to B" precisely, because the graph was built by parsing and resolving the
actual export, not by pattern-matching.

The `iadc` server builds this graph for **any** Appian application you seed it
with — `iadc` is the name of the graph product, not a particular app. Point it
at your project's export or application UUID and it grounds the same
impact reasoning against your graph.

It is **session-based**: nothing is queryable until you `seed` a graph and
get back a `session_id`. Every other tool call is scoped to that session and
resolves against that session's graph only.

## How to recognize the tools

Surfaced as `mcp__iadc__*`. All 17:

`seed`, `seed_status`, `close`, `report_changes` (session/lifecycle) —
`get_neighbors`, `get_node`, `callers_of`, `shortest_path`, `get_out_edges`,
`get_in_edges`, `get_edge`, `edges_by_relation`, `list_nodes`, `find_nodes`,
`graph_overview`, `reachable`, `record_model` (read/query).

If you see these, this skill is MANDATORY — load it before the first call.

## Resource Reference Map

Each file covers what the tool schemas can't say. Load on demand:

| When you need | Reference File |
|---|---|
| Session states, TTL, principal binding, the two `seed` front doors, cancellation | `references/session-lifecycle.md` |
| A starting `node_id` (from a name, a UUID, or a search term) | `references/identifiers-and-discovery.md` |
| The exact relation strings, provenance (reference vs structural), `calls` vs `calls_builtin` vs `references` | `references/relation-vocabulary.md` |
| What `kind` and `object_type` values mean, node-id forms per kind | `references/node-kinds.md` |
| Multi-step traversal patterns (blast radius, callers, path, record-model walks) | `references/traversal-recipes.md` |
| Exact JSON shapes returned, and every error dict / empty-vs-not-found distinction | `references/return-shapes-and-errors.md` |

## MANDATORY first sequence

1. **Seed — pick the right front door.**
   - `seed(export_ref="<path>")` — server-local already-extracted export
     directory. Synchronous; returns `state: "ready"` immediately.
   - `seed(application_uuid="<uuid>")` — live Appian application UUID.
     Asynchronous; returns `state: "queued"` immediately, before the build
     finishes.
2. **If you used `application_uuid`**, poll `seed_status(session_id)` until
   `state` is `"ready"` or `"ready_with_warnings"` (both queryable — stop and
   read on), or one of the failure states — `"export_failed"`,
   `"export_timed_out"`, `"build_failed"`, `"failed"` (stop and surface
   `message`). In between you'll see `"queued"` -> `"exporting"` ->
   `"downloading"` -> `"building"`. Every read tool rejects a session that
   isn't `"ready"`/`"ready_with_warnings"` yet.
3. **Obtain a starting `node_id`.** You almost never have one up front — use
   `find_nodes(session_id, query)` (substring match on label/id/name) or
   `list_nodes(session_id, kind=..., object_type=...)`. See
   `references/identifiers-and-discovery.md` for resolving a human-given
   object name to the UUID you actually need first.
4. **Walk the graph** with the query tools (`get_neighbors`, `callers_of`,
   `shortest_path`, `get_out_edges`/`get_in_edges`, `get_edge`,
   `edges_by_relation`, `reachable`, `graph_overview`, `get_node`,
   `record_model`) using the `id` values the tools themselves return — never
   a label you typed by hand.
5. **Close when done.** `close(session_id)` frees the session. Not required
   for correctness (TTL reclaims it), but do it when you're finished with a
   session, and it's also how you cancel an in-flight (still-in-progress)
   build.

## Common pitfalls

- **The label key is `node_label`, not `name`.** Every compact record is
  `{id, kind, node_label, object_type?}`. Don't look for `name` or
  `display_name` in tool output — `node_label` is the wire key, and it's the byte-identical string a human sees in the
  graphify visualization.
- **Node ids are not always UUIDs.** Forms include a bare Appian UUID, a
  synthesized `appian:{name}` (built-ins), a composite `{rt_uuid}/{stub}`
  (record views and view-backed fields), or raw ref text (some boundary
  nodes). Always pass an `id` exactly as another tool returned it — never
  construct or guess one.
- **`relation` is an exact-match string, not fuzzy.** `edges_by_relation`
  with an unknown/misspelled relation returns `[]` — a valid empty result,
  not an error. A typo and "this relation genuinely doesn't occur" look
  identical; check spelling against `references/relation-vocabulary.md`.
- **Sessions expire after a 30-minute idle TTL.** A `session_id` that
  worked earlier in a long conversation may now return
  `{"error": "unknown or expired session", ...}`. Re-`seed` if so — don't
  assume a bug.
- **`get_out_edges`/`get_in_edges`/`edges_by_relation` never include the full
  `occurrences` list** — only `occurrence_count`. Drill into a specific edge
  with `get_edge(session_id, source, target, relation)` for the full
  occurrences and provenance.
- **`[]` vs `{"error": ...}` are both real, distinct outcomes** — don't treat
  an empty list as failure. See `references/return-shapes-and-errors.md` for
  which tools distinguish "exists but empty" from "not found."
- **A session belongs to the principal that created it.** Reusing another
  agent's/user's `session_id` fails with a distinct
  `"session does not belong to this caller"` error, not "unknown session."

## Quick-reference: all 17 tools

| Tool | Purpose | Key params |
|---|---|---|
| `seed` | Build a session from an export or app UUID | `export_ref` XOR `application_uuid` |
| `seed_status` | Poll a `seed(application_uuid=...)` build | `session_id` |
| `close` | Free a session / cancel an in-flight build | `session_id` |
| `report_changes` | Patch/delete session graph nodes after live edits | `session_id`, `uuids: list[str]` |
| `get_neighbors` | Direct successors/predecessors of a node | `session_id`, `node_id`, `direction: "in"\|"out"` |
| `get_node` | Full attribute dict + degree for one node | `session_id`, `node_id` |
| `callers_of` | Nodes with a `calls`-relation edge into this node only | `session_id`, `node_id` |
| `shortest_path` | Shortest directed path between two nodes | `session_id`, `source`, `target` |
| `get_out_edges` | Every outgoing edge, compact form | `session_id`, `node_id`, `relation?` |
| `get_in_edges` | Every incoming edge, compact form | `session_id`, `node_id`, `relation?` |
| `get_edge` | Full single-edge record, incl. `occurrences` | `session_id`, `source`, `target`, `relation` |
| `edges_by_relation` | Every edge with a given relation name | `session_id`, `relation` |
| `list_nodes` | Browse/filter nodes by kind/object_type | `session_id`, `kind?`, `object_type?`, `limit` |
| `find_nodes` | Substring search over label/id/name | `session_id`, `query`, `kind?`, `object_type?`, `limit` |
| `graph_overview` | Graph-wide counts by kind/object_type/relation/provenance | `session_id` |
| `reachable` | Full/depth-bounded transitive closure (blast radius) | `session_id`, `node_id`, `direction`, `depth?`, `limit` |
| `record_model` | One-call record type substructure: fields, views, actions, relationships | `session_id`, `record_type_id` |
