# Drop the `appian` MCP; blast radius and accessibility audits read the `iadc` graph instead

`/iadc-advisor:setup` wrote an `appian` MCP entry into every client's `.mcp.json`: a stdio
`lcp_mcp_server` process needing the client's own Appian tenant URL, username, and password. The
vendored `appian` skill used it for exactly two live reads: `getObjectDependents` for blast
radius ("what breaks if I remove this?") and `getInterface` for reading an interface's SAIL
before an accessibility audit. Everything else the skill describes — create/update/delete/
validate workflows — was already advisory reference for a full-access build tool outside this
plugin, never something Advisor itself called.

[Tester ADR
0001](https://github.com/teamignyte/IADC-Tester/blob/main/docs/adr/0001-tester-reads-the-app-through-the-graph.md)
hit the identical problem and solved it the same way — Tester dropped the same `appian` MCP,
`listInterfaces`/`getInterface` becoming `list_nodes`/`find_nodes`/`get_sail` — and the graph
plugin never had this server at all. Advisor was the family's last holdout: the one client
credential surface still asking for a live Appian username and password.

**Advisor drops the `appian` MCP entirely.** No client repo `.mcp.json` written by this plugin
carries an Appian username, password, or tenant URL any more.

| was | now |
|---|---|
| `getObjectDependents` (blast radius) | `reachable`/`get_in_edges`/`get_edge` against the `iadc` graph |
| `getInterface` (accessibility-audit SAIL read) | `find_nodes` + `get_sail` against the `iadc` graph |
| `listApplications` (Application UUID resolution, `/setup`) | asked directly of the user, recorded as per-project state |

**The Application UUID is now always a per-project value the user provides** — the pattern
Tester ADR 0001 already established ("the application UUID, recorded in config" rather than
looked up per run). `/setup` tells the user where to find it if they don't have it to hand
(Appian Designer's address bar and General properties panel), and finishes without it if they
still don't, the same deliberately-unconfigured path `/setup` already used for a
placeholder-valued `.mcp.json` — now generalized to the ordinary case rather than an exceptional
one.

**This closes [ADR 0003](0003-store-application-identity-in-graph-skill.md)'s own live-lookup
exception.** That ADR — already superseded by ADR 0010 and marked historical — recorded the UUID
as a no-live-lookup value with one stated carve-out: `/setup` could resolve it live "optionally,
once," because the graph is *seeded from* that UUID and so cannot itself produce it. Dropping the
`appian` MCP closes that carve-out by removing the only tool it depended on — the graph plugin's
own skill states the underlying rule plainly: re-resolving a recorded application UUID live "is a
defect, not diligence."

## Considered options

- **Keep `getObjectDependents`/`getInterface` live, drop only the credential-writing prose.**
  Rejected: the whole point is removing the credential, and these two tools are exactly what
  needs it. Keeping either live keeps the server.
- **Resolve the Application UUID from the graph instead of asking the user.** Rejected — not
  possible in principle, not merely undesirable: the graph is seeded *from* the application UUID,
  so nothing in it can produce that UUID before it exists.
- **Delete the placeholder-valued `.mcp.json` branch outright once `appian` is gone**, since its
  original condition (`appian` unconfigured) no longer exists. Rejected: after the drop, "the
  user doesn't know the UUID yet" is the *ordinary* case, not a placeholder-`.mcp.json`
  exception — deleting the branch would leave `/setup` with no documented path forward when the
  user genuinely can't supply it.

## Consequences

- **The family's last live Appian credential is gone.** The entire client credential surface any
  Advisor-installed repo holds is now the one `iadc` graph entry (URL and API key) — the state
  Tester ADR 0001 already reached for Tester-only repos.
- **Family [ADR 0010](https://github.com/teamignyte/IADC/blob/main/docs/adr/0010-graph-plugin-owns-graph-configuration.md)'s
  consequence line is superseded.** It read: "Advisor's `/setup`... keeps ownership of the
  `appian` and `context7` entries, which are its own." `/setup` now keeps ownership of `context7`
  only.
- **Existing clients keep their credentials until they re-run `/setup`.** Not writing the entry
  going forward does nothing for a repo already configured — its `.mcp.json` keeps the Appian
  username and password indefinitely. `/setup`, on re-run, detects a stale `appian` entry and
  offers to remove it: an offer with explicit consent, never a silent edit of a file that may
  hold other servers the team owns.
- **Blast radius gains transitivity and provenance, loses one-call convenience and
  cross-application reach.** `reachable(direction="in")` is the full transitive closure where
  `getObjectDependents` was one-hop; `get_edge` carries exact occurrence line/column where the
  old breadcrumb gave line numbers only. Against that: a 47-dependent blast radius the old tool
  returned in one call now costs 1 + N graph calls for the same breadcrumb detail, and the graph
  is scoped to one seeded application — a dependent in a *different* application is invisible to
  it, silently.
- **One clean capability gain: field-level dependencies.** `getObjectDependents` documented that
  it could not see `recordType!RT.fields.fieldName` references; the graph's `uses_record_field`
  relation does.
- **The record-type deletion workflow's structural checks (Step 6) split: some repoint to the
  graph, some don't.** `record_model` gives a record type's relationships/views/actions in one
  call, and "contained objects of this application" is free (the graph *is* the seeded
  application — no separate per-application call is needed). But the graph tracks design objects,
  not runtime state: whether a record type holds any rows, a group's hierarchy or membership, and
  a record type's title expression have no graph representation at all. Those three still need a
  full-access build tool — unchanged from before this drop, but now stated plainly in
  `confirmation-patterns.md` rather than left routed through a tool (`listRecordData`,
  `listGroups`, `listGroupMembers`, `getRecordType(...).titleExpression`) that no longer exists.
- **Blast-radius answers are now as-of-seed, not live.** The graph is a point-in-time snapshot;
  `report_changes` refreshes it but explicitly does not re-materialize a record type's own
  structural children. The old tool read the live tenant on every call.
- **The vendored `appian` skill carries a fifth local patch** (Patch E, on top of A–D) —
  `docs/vendored-appian-skill.md` records it, since an undocumented divergence from upstream is
  indistinguishable from staleness at the next refresh.
