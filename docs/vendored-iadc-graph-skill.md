# The vendored `iadc-graph` skill — source sha and how to refresh it

`iadc-advisor/skills/iadc-graph/` is a **byte-identical copy** of the canonical skill in the
IADC repo (`.claude/skills/iadc-graph/`), taken at the sha that built the **deployed** graph
image. It carries **zero local patches** — see
[ADR 0011](adr/0011-iadc-graph-skill-byte-identical-at-deployed-sha.md).

| | |
|---|---|
| **Upstream** | the IADC repo, path `.claude/skills/iadc-graph/` — *ours*, not a third party |
| **Vendored at** | `6dc3999` (IADC `main`) — refreshed on 2026-07-31 |
| **Local prefix** | `iadc-advisor/skills/iadc-graph` |
| **Contents** | 7 `.md` files: `SKILL.md` + 6 under `references/` |
| **Local patches** | **none.** Any difference is staleness — take upstream |

This file lives **outside** that prefix on purpose: a version stamp inside the skill would
break byte-identity, which is the only property that makes a refresh verifiable.

---

## The ordering rule — it is release-blocking

**The skill may lag the deployed server, never lead it.** A server tool the skill doesn't
mention yet is harmless. A skill that promises a tool the deployed server lacks makes Claude
call it and fail.

So: **deploy the graph image first, then refresh this copy from the sha that built it, then
release the plugin.** Never refresh from IADC `HEAD` — `HEAD` can be ahead of what is
deployed, which is the harmful direction.

The copy is refreshed **when a new graph image is deployed**, not on a plugin-release
schedule. A plugin release that does not follow a graph deploy needs no refresh.

---

## Refreshing

Everything below is mechanical. There are no patches to reapply, and nothing in the skill
tree may be hand-edited here — a fix belongs upstream in IADC, where a drift-guard test
couples the skill to the server's actual tool roster per commit.

```bash
IADC=/path/to/IADC
SHA=<the sha that built the deployed graph image>

# 1. Prove the deployed image really is at that sha (the host has no git — compare content).
#    From the IADC repo, with its ops skill sourced:
#      iadc-ssh 'cd ~/iadc && docker compose exec -T graph md5sum \
#        /app/graph_mcp/__main__.py /app/graph_mcp/service.py'
#    must equal, locally:
#      md5sum <(git show "$SHA":graph_mcp/__main__.py) <(git show "$SHA":graph_mcp/service.py)

# 2. Replace the tree wholesale from that sha (not from the working copy).
rm -rf iadc-advisor/skills/iadc-graph
mkdir -p iadc-advisor/skills/iadc-graph
git -C "$IADC" archive "$SHA" .claude/skills/iadc-graph \
  | tar -x --strip-components=3 -C iadc-advisor/skills/iadc-graph

# 3. Byte-compare — the only acceptance test that matters. Must print nothing.
diff -r iadc-advisor/skills/iadc-graph "$IADC"/.claude/skills/iadc-graph

# 4. Lag-not-lead check: the DEPLOYED server's roster must be a superset of what the
#    refreshed skill documents. List tools over the deployed /mcp (see below), then compare
#    against the roster the skill's frontmatter enumerates.

# 5. Hygiene: LF only.
for f in $(find iadc-advisor/skills/iadc-graph -type f); do
  file "$f" | grep -q CRLF && echo "CRLF: $f"
done

# 6. Bump `version` in iadc-advisor/.claude-plugin/plugin.json, record it in
#    iadc-advisor/CHANGELOG.md, and update this file's "Vendored at" row.
```

### Listing the deployed server's tool roster

The graph port is not open to arbitrary IPs (its SG rule is per-operator-IP and normally
revoked), so run the handshake **on the host**, against `localhost`. Streamable HTTP needs
`initialize` → `notifications/initialized` → `tools/list`, carrying the `mcp-session-id` the
initialize response returns, with the Graph service's own key in the `Appian-API-Key` header
(read it from the host's `~/iadc/.env.graph`; never echo it).

---

## What the 2026-07-31 refresh verified

* **The deployed image is at `6dc3999`**, proven by content rather than assumed: in-container
  `md5sum` of `/app/graph_mcp/__main__.py` (`98583ce9…`) and `/app/graph_mcp/service.py`
  (`dd2929ee…`) match `git show 6dc3999:` for both files.
* **The deployed server serves 18 tools** — `callers_of`, `close`, `edges_by_relation`,
  `find_nodes`, `get_edge`, `get_in_edges`, `get_neighbors`, `get_node`, `get_out_edges`,
  `get_sail`, `graph_overview`, `list_nodes`, `reachable`, `record_model`, `report_changes`,
  `seed`, `seed_status`, `shortest_path`.
* **The refreshed skill documents exactly those 18** — so the lag is zero, not merely
  non-negative. This cures the staleness ADR 0011 was written against (the old fork
  documented 17 and omitted `get_sail`).
* `diff -r` against IADC @ `6dc3999`: empty. 7 files, all LF.

---

## Known consequences of byte-identity — do not "fix" these here

Byte-identity means the copy carries IADC-shaped references. That is the deal, not a defect
in the copy. Fix any of these **upstream in IADC** so the next refresh inherits the fix;
editing them here would silently break the only property this vendoring rests on.

* `references/return-shapes-and-errors.md` cites `graph_mcp/__main__.py` and
  `graph_mcp/tools.py` as the source of truth for return shapes. Those are IADC server
  sources and exist in no client repo. This is correct as provenance and harmless as
  guidance.
* `references/identifiers-and-discovery.md` cites the Appian skill's UUID discipline as
  `.claude/skills/appian/references/tools-mcp.md`. That file **does** ship inside this plugin
  — at `iadc-advisor/skills/appian/references/tools-mcp.md` — so the reference resolves by
  name but not by the literal path a client would try. Worth making prefix-neutral upstream.
* `SKILL.md`'s seed-target section reads the Application UUID from the ambient **Project
  configuration** and names `docs/agents/project.md` / `project.local.md`. Those are the
  client-repo paths `/setup` writes, so this one is correct for clients by design — it is the
  deliberate client adaptation ADR 0011 folded upstream, and the reason a verbatim copy is
  safe at all.
* `SKILL.md`'s frontmatter hardcodes "18 tools" and "the 24-relation vocabulary". Both are
  accurate at `6dc3999` (verified: 18 live tools; 24 rows in `relation-vocabulary.md`), but
  IADC's drift guard does not read frontmatter, so neither count is machine-guarded. A
  frontmatter count that goes stale upstream propagates to every client on the next refresh —
  check both when refreshing.

## The port and scheme clients are given

`iadc-advisor/skills/setup/mcp-template.json` templates the `iadc` server at
**`http://<your-graph-host>:8001/mcp/`**. Both parts matter and both changed at the graph
split (IADC IV-305/IV-312):

* **8001, not 8000.** The graph MCP moved to the standalone Graph service. The review API on
  8000 no longer serves `/mcp` at all — a client left on 8000 gets a 404, not a redirect.
* **`http`, not `https`.** The deployed endpoint is cleartext today; `https` fails the
  handshake. Onboarding a genuinely external client is gated on the IADC-side HTTPS revisit
  (IADC IV-117) — the port is deliberately not opened to external client IPs before then.
  When that lands, the scheme becomes `https` and the port may move; the template's
  `_comment` says so, and the coupling is recorded in IADC's `docs/environments.md`.
