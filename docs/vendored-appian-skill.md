# The vendored `appian` skill — divergences and how to update it

`iadc-advisor/skills/appian/` is **not ours**. It is vendored from Appian's public
repository and we carry deliberate local patches on top of it.

| | |
|---|---|
| **Upstream** | <https://github.com/appian/dev-mcp-skills> (path `skills/appian`) |
| **Licence** | see `iadc-advisor/skills/appian/LICENSE` |
| **Vendored at** | `0ab639c4` (2026-07-15) — refreshed to this SHA on 2026-07-27 |
| **Local prefix** | `iadc-advisor/skills/appian` |
| **Contents** | 65 `.md` + `registry/components-registry.json` + `LICENSE` |

This file lives **outside** that prefix on purpose. Anything inside the prefix would be
overwritten by a refresh.

---

## ⚠️ Read this before you refresh

**On the 2026-07-27 refresh, a local patch that is not obvious from any diff was very
nearly lost** — the advisory posture block (Patch D below). It exists only in our copy,
upstream has nothing like it, and losing it would have silently converted the plugin's
most-loaded skill from *advisory* to *builder-oriented* — contradicting the product's
central premise, with nothing failing and no test going red.

It was missed when this document was first written, and recovered only by reconstructing
the original vendoring commit to see what the very first import had changed.

The lesson: **the patch list below is the only thing standing between a refresh and a
silent regression.** If you patch a vendored file, add it here in the same commit. An
undocumented divergence is indistinguishable from staleness at refresh time, and gets
overwritten.

---

## 1. The local patches — these must survive every refresh

Upstream fixed none of these as of `0ab639c4`; assume all four still apply.

### Patch A — no per-project config in skill files ([ADR 0010](adr/0010-no-config-in-skill-files.md))

**Upstream hardcodes the Appian version** in `SKILL.md`:

```markdown
**Appian Version:** 26.6
```

That cannot work here. Plugin skills live in a **shared, read-only cache serving every
client project**, wiped and replaced on every plugin update — so there is exactly one copy
of that line, whatever it says is served to all clients, and `/setup` cannot write to it.
Ours reads the value from the ambient **Project configuration** the SessionStart hook
injects from each client's own `docs/agents/project.md`.

| File | Patch |
|---|---|
| `SKILL.md` | Configuration block reads the ambient `Appian version`; the *Appian Documentation Search* workflow reads it too. Each bash block that uses the version is **self-contained with a guard that fails loudly if unsubstituted** — the Bash tool starts a fresh shell per call, so a variable does not carry between blocks |
| `references/function-reference.md` | `{VERSION}` definition and worked-example URL point at the ambient config |
| `references/expressions.md` | same, for its version-bearing bash snippet |
| `references/documentation-lookup-strategy.md` | *(new at this refresh)* hardcoded `VERSION="26.6"` in a runnable block |
| `references/sail-verification-checkpoint.md` | *(new at this refresh)* same |

**This one fails silently.** Nothing errors — the plugin just starts telling a client on
25.3 that they are on 26.6, and every doc link it hands them is subtly wrong. Note the
scope grows as upstream adds files: two newly-vendored files needed this patch.

### Patch B — citations to files that do not exist (15 citations)

Upstream cites files **upstream itself does not contain**: `rich-text-icon-aliases.md`,
`node-types.md`, `display-conversion-{grids,actions}.md`,
`tool-change-proposal-dependency-detection.md`. Some are anchored to `/ui-guidelines/`,
`/conversion-guidelines/`, `/my-docs/` trees that do not exist either.

Four were phrased as **mandatory reads** — *"ALWAYS read … before using ANY icon
parameter"*, *"MUST … DO NOT GUESS"* — because an Appian icon alias is a closed vocabulary
that fails silently when wrong. An agent obeying them stalls or guesses: the exact failure
the instruction existed to prevent.

We repoint each at the plugin's real capabilities — `/context7` semantic docs search, then
version-exact `docs.appian.com` per the `appian` skill's own documentation workflow —
**keeping the imperative force**: the value is verified, never guessed.

Patched: `references/components/{button,rich-text,stamp-field,grid-field}-instructions.md`,
`references/sail.md`, `references/applications.md`, `SKILL.md`.

The `/conversion-guidelines/` citations describe a mockup-to-Appian **converter** workflow
this advisory plugin does not perform — those pointers are **deleted, not redirected**.

> Was 17 citations before the refresh. `confirmation-patterns.md` no longer needs the patch
> (upstream deleted the enclosing section). **This is a real upstream bug** and that repo
> has a `CONTRIBUTING.md` — reporting it is the single highest-leverage way to shrink our
> patch set, since nothing about this fix is specific to our plugin.

### Patch C — path repairs

`references/patterns/tabs.md` and `references/layouts/tab-layout-instructions.md`
cross-reference each other through a `guidelines/…` prefix; no such tree exists. Corrected
to `references/…`.

### Patch D — the advisory posture block ← easiest to lose

`SKILL.md` carries a local `## Posture: read-only / advisory` section stating that this is
an **architect, not a builder**; that the Appian MCP runs with `LCP_TOOL_MODE=readonly` so
`create*`/`update*`/`delete*` are not exposed; and — the load-bearing part — that the
skill's create/update material is **advisory reference for giving correct advice**, not a
set of actions to take.

**Upstream has nothing like this**, because upstream's skill is written for people who do
build. Losing it flips the plugin's most-loaded skill against the product's premise.

This matters more after each refresh, not less: upstream keeps adding builder-oriented
material (this refresh brought a create/update workflow back into `expressions.md` plus
four build-and-verify checklists). The posture block is what reframes all of it as
reference.

**Verify it by name after every refresh** — see the checks in §4.

---

## 2. Everything else is upstream's

As of the 2026-07-27 refresh we are at **parity with `0ab639c4`** apart from Patches A–D.
There is no remaining local drift to protect: a prior audit reconstructed the original
import and confirmed exactly 12 files ever carried local edits.

If a future diff shows a difference in a file **not** listed in §1, it is upstream having
moved on — **take upstream.**

---

## 3. Refreshing

We refresh by **direct copy, then reapply the patches**. `git subtree` is the more
sophisticated option (it turns a silent overwrite into a merge conflict at exactly the
patched lines) but it requires a one-time history graft, since `git subtree add` refuses
over an existing directory. Revisit it if the patch set grows.

```bash
git checkout -b vendor/appian-refresh-YYYY-MM-DD
git clone --depth 1 https://github.com/appian/dev-mcp-skills.git /tmp/appian-upstream
git -C /tmp/appian-upstream rev-parse HEAD          # record this SHA
```

1. **Copy** `/tmp/appian-upstream/skills/appian/` over `iadc-advisor/skills/appian/`,
   keeping `LICENSE`. Include non-`.md` assets — `registry/components-registry.json` is
   referenced by five files, and omitting it creates fresh dangling citations.
2. **Reapply Patches A–D.** Read our pre-refresh version of each patched file first, then
   reproduce the patch's *intent* on top of upstream's new prose — upstream may have
   rewritten the surrounding text, so do not paste old sentences in mechanically.
3. **Check whether the patch scope grew.** Patch A in particular: grep every newly-added
   file for a hardcoded version.
4. **Run the checks in §4.**
5. **Update this file** — the SHA, the date, the counts, and any patch that changed scope
   or became unnecessary.

Do this on its own branch and review it alone. This refresh touched 26 files; mixed into
feature work it is unreviewable.

---

## 4. Verification — run all of these

Line-by-line review misses silent reverts. These encode §1 as assertions.

```bash
# A. No literal Appian version as configuration, anywhere.
grep -rn "Appian Version:\*\* *[0-9]" iadc-advisor/skills/appian/
grep -rn 'VERSION="2[0-9]' iadc-advisor/skills/appian/

# B. No citation to a file that does not exist.
grep -rn "rich-text-icon-aliases\|node-types\.md\|display-conversion-\|/ui-guidelines/\|/conversion-guidelines/\|/my-docs/" iadc-advisor/

# C./D. The posture block survived, and the six config-readers still read the ambient block.
grep -c '^## Posture: read-only / advisory' iadc-advisor/skills/appian/SKILL.md   # expect 1
grep -rln "Project configuration" \
  iadc-advisor/skills/{appian,iadc-graph,pressure-test,office,orient,context7}/SKILL.md | wc -l   # expect 6

# Hygiene: LF only (CRLF makes every future diff unreadable).
git ls-files iadc-advisor/skills/appian | while read -r f; do
  file "$f" | grep -q CRLF && echo "CRLF: $f"
done
```

**A, B and the CRLF check must return nothing. The posture check must print 1, the
config-readers check 6.**

Then the real gate — a plugin that validates can still be broken:

```bash
claude plugin validate iadc-advisor     # necessary, NOT sufficient
```

Install into a scratch repo and confirm `claude plugin list` reports **`✔ enabled`**. See
the dogfooding recipe in the workshop `CLAUDE.md`.

---

## 5. Keeping this cheap

1. **Report Patch B upstream.** It is a genuine bug in their repo affecting all their
   users, and nothing about the fix is specific to us. Merged upstream, 15 citations stop
   being our problem permanently — leaving Patches A and D, which are ours by design and
   always will be.
2. **Never patch a vendored file without adding it to §1 in the same commit.** See the
   warning at the top: this exact rule was broken once and cost a near-miss on the
   advisory posture.
3. **Refresh regularly.** This refresh spanned 13 missing files and ~500 lines of drift in
   a single reference. Four small refreshes beat one large one.
4. **Re-read §1 against upstream's new content each time.** Upstream adds builder-oriented
   material; Patch D's framing has to keep covering it.
