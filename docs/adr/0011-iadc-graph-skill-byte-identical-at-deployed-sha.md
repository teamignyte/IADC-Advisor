# The iadc-graph skill is a byte-identical copy at the deployed server's sha

> **Superseded by the family's
> [ADR 0003](https://github.com/teamignyte/IADC/blob/main/docs/adr/0003-shared-skills-ship-as-pinned-marketplace-plugins.md).**
> This plugin no longer vendors the skill at all. `iadc-graph` ships as its own plugin in the
> `IADC-Marketplace` catalog, and `iadc-advisor` declares it as a dependency, so it installs
> automatically and there is nothing here to keep in sync.
>
> **Both rules below survive verbatim** — they were right, and the new arrangement enforces them
> rather than replacing them: the copy is taken at the sha that built the **deployed** graph image,
> and *the skill may lag the deployed server, never lead it*. What changed is the count and the
> location: **one** mirror for the whole family, in `IADC-Marketplace`, instead of one per consumer.
> That is what this ADR's third rejected option ("a shared plugin or sub-repo as the single home")
> ruled out — correctly at the time, since moving the *canonical* file would have killed the drift
> guard. The new arrangement keeps canonical authorship in IADC-Core and moves only the copy, which
> is the distinction the rejection missed.

The `iadc-graph` skill exists twice: the canonical copy in the IADC repo
(`.claude/skills/iadc-graph/`), machine-coupled to the graph server's code by a drift-guard
test that fails any commit whose tool roster and skill disagree — and this repo's copy in
`iadc-advisor/skills/iadc-graph/`, which ships to clients inside the plugin. The two forked:
ours mixed *deliberate* client adaptations (the Configuration section reading the seed UUID
from the ambient Project configuration, the no-live-lookup rule, audience framing) with
*accidental* staleness (17 tools vs the server's 18 — `get_sail` landed upstream and never
arrived here), and nothing distinguished the two or bound our copy to any server version.

Two rules fix this permanently:

1. **Fold, don't fork.** The deliberate adaptations move upstream into IADC's canonical
   skill as conditional knowledge ("when the ambient Project configuration records the
   Application UUID, read it from there — re-resolving it live is then a defect"), which
   falls through cleanly for IADC's own sessions where no Project configuration exists.
   This keeps ADR 0010's rule (a `SKILL.md` carries knowledge, never configuration) and
   preserves ADR 0003's no-live-lookup posture. After the fold, this repo carries **zero
   local patches**: its copy is byte-identical to IADC's skill directory at a specific sha.

2. **Track the deployed server, not IADC HEAD.** Clients talk to the *deployed* graph
   service, so our copy is refreshed **when a new graph image is deployed**, copied from
   exactly the sha that built that image. The sha is recorded in
   `docs/vendored-iadc-graph-skill.md` (dev docs, never shipped — a stamp inside the skill
   would break byte-identity), alongside the refresh procedure. Verification is mechanical:
   `diff -r` against IADC at the recorded sha.

**The skill may lag the deployed server, never lead it.** A server tool the skill doesn't
mention yet is harmless; a skill that promises a tool the deployed server lacks makes Claude
call it and fail. Ordering is therefore release-blocking: deploy the graph image first, then
refresh the copy and release the plugin.

## Considered options

- **Patched vendor with a divergence ledger** (the `skills/appian` model). Rejected: that
  model is for upstreams we don't control; this upstream is ours, so every divergence can
  simply be upstreamed. Keeping patches buys client-tailored prose at the cost of a manual
  merge per refresh and silent-revert risk — the appian ledger itself records one near-miss.
- **Sync to IADC HEAD on plugin release.** Rejected: HEAD can be ahead of the deployed
  server, shipping documentation for tools clients can't call — the harmful direction.
- **A shared plugin or sub-repo as the single home.** Rejected: client distribution must
  ride this plugin regardless (clients cannot take the IADC repo as a marketplace without
  receiving the whole review-tool source), and moving the canonical file out of IADC would
  kill the drift guard that keeps skill and server code honest per-commit.

## Consequences

- `docs/vendored-iadc-graph-skill.md` records the current source sha and the refresh
  procedure; the plugin release checklist gains the byte-compare step.
- The 17-vs-18 staleness (missing `get_sail`) is cured by the first fold-and-refresh, once
  the deployed graph service actually serves 18 tools.
- `skills/appian` is unaffected — it stays a patched vendor precisely because *its*
  upstream is not ours (`docs/vendored-appian-skill.md` continues to govern it).
- The fold itself is IADC-side work (its skill gains the conditional Project-configuration
  guidance and the "any application" framing); this repo's part is the refresh + stamp +
  procedure doc.
