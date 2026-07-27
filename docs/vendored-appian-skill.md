# The vendored `appian` skill — divergences and how to update it

`iadc-advisor/skills/appian/` is **not ours**. It is vendored from Appian's public
repository and we carry deliberate local patches on top of it.

| | |
|---|---|
| **Upstream** | <https://github.com/appian/dev-mcp-skills> (path `skills/appian`) |
| **Licence** | see `iadc-advisor/skills/appian/LICENSE` |
| **Vendored at** | `0ab639c4` (2026-07-15) — the state upstream was in when this file was written |
| **Local prefix** | `iadc-advisor/skills/appian` |

This file lives **outside** that prefix on purpose. Anything inside the prefix conflicts
on every update.

> **Status when written (2026-07-27): the copy is materially stale.** Upstream ships 65
> reference files; we have 52. Beyond our own patches, eight files have simply been
> improved upstream since our copy was taken — `interfaces.md` alone has grown by ~540
> lines. We are giving clients older Appian guidance than Appian publishes. Pulling is
> worth doing soon.

---

## 1. Deliberate divergences — these must survive an update

Twelve files carry local patches. If an update reverts one of these, that is a
**regression**, not a merge resolution.

### A. Config out of skill files — [ADR 0010](adr/0010-no-config-in-skill-files.md)

**This is the one that matters most.** Upstream hardcodes the Appian version in a
`## Configuration` block:

```markdown
**Appian Version:** 26.6
```

We removed it. Plugin skills live in a **shared, read-only cache that is wiped on every
update**, so a per-project value cannot live there: `/setup` cannot write to it, and one
client's version would be served to every other client. Ours reads the value from the
ambient **Project configuration** that the SessionStart hook injects from the client's
`docs/agents/project.md`.

| File | Patch |
|---|---|
| `SKILL.md` | Configuration block reads the ambient `Appian version`, not a literal. Plus four edits in the *Appian Documentation Search* workflow: each bash block is self-contained with a guard that fails loudly if the version is unsubstituted (the Bash tool starts a fresh shell per call, so `$VERSION` does not carry between blocks) |
| `references/function-reference.md` | `{VERSION}` definition and the worked-example URL point at the ambient config, not `SKILL.md` |
| `references/expressions.md` | same treatment for its version-bearing bash snippet |

**If an update reintroduces a literal version anywhere, that is the regression to catch.**
It fails silently — nothing errors; the plugin just starts telling every client their
Appian version is whatever upstream hardcoded.

### B. Dangling reference repairs — an upstream bug

Upstream cites four files **that do not exist in upstream**. Verified absent from
`0ab639c4`, from three other copies of this skill on this machine, and from our git
history. Seventeen citations pointed at them; four were phrased as mandatory reads
(`ALWAYS read … before using ANY icon parameter`), so an agent obeying them stalls or
guesses — the exact failure the instruction existed to prevent.

Missing upstream: `rich-text-icon-aliases.md`, `node-types.md`,
`display-conversion-{grids,actions}.md`, `tool-change-proposal-dependency-detection.md`.
The `/ui-guidelines/`, `/conversion-guidelines/` and `/my-docs/` trees that some paths
were anchored to do not exist either.

We repointed all seventeen at the plugin's real capabilities — `/context7` semantic docs
search, then version-exact `docs.appian.com` per the `appian` skill's own documentation
workflow — **keeping the imperative force**: an icon alias is still never guessed.

Files patched: `references/components/{button,rich-text,stamp-field,grid-field}-instructions.md`,
`references/sail.md`, `references/applications.md`, `references/confirmation-patterns.md`,
`SKILL.md`.

> **Upstream this if you can.** It is a genuine upstream bug and that repo has a
> `CONTRIBUTING.md`. Merged upstream, these seventeen stop being our conflicts forever.
> Unlike §A, nothing about this fix is specific to our plugin.

### C. Path repairs

| File | Patch |
|---|---|
| `references/patterns/tabs.md`, `references/layouts/tab-layout-instructions.md` | cross-references used a `guidelines/…` prefix; no such tree exists — corrected to `references/…` |
| `references/iadc-graph`-side citations of `tools-mcp.md` | cited by name rather than a relative path that cannot resolve from a sibling skill in the plugin cache |

### D. Line endings

Upstream is LF. Our copy arrived CRLF. Normalized to LF and pinned by `.gitattributes`
(`* text=auto eol=lf`). **Do not let CRLF back in** — mismatched endings make every file
read as fully rewritten, burying real conflicts.

---

## 2. Not ours — just stale

These eight differ from upstream **only because upstream moved on**. There is no local
patch to protect. On a conflict, **take upstream**:

`references/component-reference.md` · `references/components/chart-instructions.md` ·
`references/expression-rules.md` · `references/interfaces.md` ·
`references/layouts/card-layout-instructions.md` ·
`references/query-record-type-patterns.md` · `references/record-types.md` ·
`references/tools-mcp.md`

Plus **13 files we do not have at all** — pure addition, no conflict risk:
`accessibility-audit`, `accessibility-reference`, `appian-workflow-patterns`,
`component-checks`, `component-loading-index`, `documentation-lookup-strategy`,
`dropdown-patterns`, `interface-generation-checklist`, `layouts/section-layout-instructions`,
`record-summary-views`, `sail-verification-checkpoint`, `validation-checkpoint`,
`write-records-patterns`.

---

## 3. One-time setup: convert the directory into a subtree

The directory already exists with content, so `git subtree add` will refuse
(`prefix already exists`). Bootstrap it once, on its own branch:

```bash
git checkout -b vendor/appian-subtree
git remote add appian-skills https://github.com/appian/dev-mcp-skills.git
git fetch appian-skills main
```

Then graft upstream's history onto the existing path so future pulls have a merge base:

```bash
git merge -s ours --no-commit --allow-unrelated-histories appian-skills/main
git commit -m "vendor: graft appian/dev-mcp-skills history for subtree tracking"
```

From then on, updating is one command (see §4). Verify the graft worked by running a pull
immediately — it should report real changes, not "up to date" and not a total rewrite.

**Do this on its own branch and review it as its own change.** It brings in 13 new files
and updates 8 more; mixed into feature work it is unreviewable.

---

## 4. Updating: `git subtree pull`

```bash
git checkout -b vendor/appian-update-YYYY-MM-DD
git fetch appian-skills main
git subtree pull --prefix=iadc-advisor/skills/appian appian-skills main --squash
```

`--squash` keeps upstream's individual commits out of our history; we only record "vendored
up to <sha>".

**Why a merge and not a copy script:** a copy overwrites, and every patch in §1 vanishes
silently — you would discover it months later when a client is told their Appian version is
26.6. A merge raises a **conflict** exactly where upstream touched a line we patched, which
turns a silent revert into a decision you have to make.

---

## 5. Resolving conflicts

For each conflicted file, find it in §1 or §2 above. That tells you the answer.

**In §2 (stale, no local patch) → take upstream.**

```bash
git checkout --theirs <file> && git add <file>
```

**In §1 (deliberate patch) → keep ours *for the patched lines only*, take upstream for
everything else.** Do not resolve these wholesale in either direction: `--ours` throws away
genuine upstream improvements, `--theirs` reverts the patch. Open the file and merge by
hand, using §1 to identify what must survive.

### The check that actually matters

Line-by-line review misses silent reverts. Run these after every update — they encode §1
as assertions:

```bash
# A. No literal Appian version may reappear as configuration.
#    (An illustrative version inside a docs-lookup example is fine; a
#     "**Appian Version:** 26.6" configuration line is the regression.)
grep -rn "Appian Version:\*\* *[0-9]" iadc-advisor/skills/appian/

# B. All six config-reading skills still read the ambient block.
grep -rln "Project configuration" \
  iadc-advisor/skills/{appian,iadc-graph,pressure-test,office,orient,context7}/SKILL.md | wc -l   # expect 6

# C. No dangling citation came back.
grep -rn "rich-text-icon-aliases\|node-types\.md\|display-conversion-\|/ui-guidelines/\|/conversion-guidelines/\|/my-docs/" \
  iadc-advisor/

# D. No CRLF crept back in.
git ls-files iadc-advisor/skills/appian | while read -r f; do
  file "$f" | grep -q CRLF && echo "CRLF: $f"
done
```

**A, C and D must return nothing. B must print 6.**

Then the real gate — a plugin that validates can still be broken:

```bash
claude plugin validate iadc-advisor     # necessary, not sufficient
```

Install it into a scratch repo and confirm `claude plugin list` reports **`✔ enabled`**.
See the dogfooding recipe in the workshop `CLAUDE.md`.

Finally, update the **Vendored at** SHA in the table at the top of this file, and add a
`CHANGELOG.md` entry if client-visible guidance changed.

---

## 6. Keeping this cheap

The conflict burden is proportional to how far we diverge, so shrink the divergence:

1. **Upstream the §B fixes.** They are a real upstream bug and are not specific to us.
2. **Never patch a vendored file for a reason that is not written down here.** An
   undocumented divergence is indistinguishable from staleness at conflict time, and gets
   resolved away.
3. **Pull regularly.** One year of drift is far worse than four quarterly pulls — and the
   §2 list is the cost of having waited.
