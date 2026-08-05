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
of that line, whatever it says is served to all clients, and `/iadc-advisor:setup` cannot
write to it. (Address it namespaced, never bare `/setup` — a bare form is only safe until a
second plugin ships a skill of the same name, and this epic ships one in each of the other
two products.) Ours reads the value from the ambient **Project configuration** the
SessionStart hook injects from each client's own `docs/agents/advisor.md` (renamed from
`project.md`, so a generic name wouldn't read as family-wide config once the Tester ships
`tester.md` alongside it).

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

We repoint each at the plugin's real capabilities — `/iadc-advisor:context7` semantic docs
search (namespaced — Advisor ships its own `context7` skill, never address it as bare
`/context7`), then version-exact `docs.appian.com` per the `appian` skill's own documentation
workflow — **keeping the imperative force**: the value is verified, never guessed.

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
`create*`/`update*`/`delete*` **and the test tools** (`testInterface`, `testRule`,
`validateExpression`) are not exposed; and — the load-bearing part — that the skill's
**create, update, delete, validate and verify** workflows are **advisory reference for
giving correct advice**, not a set of actions to take.

It also carries two carve-outs that a blanket "this is all reference" would get wrong:

- **`getObjectDependents` is live** — you cannot delete, but the deletion workflow's
  dependency check is a `get*` tool and is exactly the right answer to "what breaks if we
  remove this?"
- **Accessibility audits are in scope, done from source** — `testInterface` is absent, so
  read the SAIL with `getInterface` and evaluate against `component-checks.md` /
  `accessibility-reference.md`. Only the render step is unavailable.

**Upstream has nothing like this**, because upstream's skill is written for people who do
build. Losing it flips the plugin's most-loaded skill against the product's premise.

This matters more after each refresh, not less: upstream keeps adding builder-oriented
material (this refresh brought a create/update workflow back into `expressions.md`, four
build-and-verify checklists, and an accessibility-audit workflow). **Re-read this patch
against the new content every time** — the 2026-07-27 refresh proved the framing can go
out of date rather than just get lost: its original clause covered only "create/update
material", which left the 80-line deletion workflow, the new blocking verification gates,
and the audit workflow outside its literal scope. The audit was the live one — read-only
advisory work the product genuinely wants to do, depending on a tool that isn't there.

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
6. **Re-derive the command-count baseline.** `iadc-advisor/skills/appian/SKILL.md` carries an
   entry in [`tests/skill_command_baseline.py`](../tests/skill_command_baseline.py), and a
   refresh that adds or removes a shell command in it will fail the ratchet. Run
   `python3 tests/test_skill_command_ratchet.py` and write the new number into the refresh
   commit. **Do not edit the vendored tree to satisfy that guard** — its advice to invoke a
   script instead is addressed to prose we author, and this tree is upstream's. The number
   moving here records what upstream did; it is not a defect to fix locally.

Do this on its own branch and review it alone. This refresh touched 26 files; mixed into
feature work it is unreviewable.

---

## 4. Verification — run all of these

Line-by-line review misses silent reverts. §1 is encoded as assertions in
[`tests/test_vendored_appian_skill.py`](../tests/test_vendored_appian_skill.py) (IV-396) — run
them with `python3 -m pytest tests -v`. The commands used to live here as prose a maintainer ran
by hand; what follows is what each check protects and why, which the test file's own docstrings
and comments carry too but a refresher reading this doc shouldn't have to go find them to get.

Before IV-396: 8 lettered checks, 10 assertions (A1, A2, B, C, D, E, F1, F2, G, CRLF). After: 7
checks, 9 assertions — B and G merge into one citation-resolution check derived from the tree
itself, described under B/G below. No check was deleted outright: every remaining letter still
has a fixture in the test module that violates it and is asserted to turn the check red. The
merge is a net gain — it resolves two citation shapes neither old check recognized — but it is
not coverage-neutral: see B/G's own paragraph for what it gained and what narrowed.

**A. No literal Appian version as configuration, anywhere.** Two assertions: no hardcoded
`**Appian Version:** N` declaration, and no hardcoded `VERSION="2N…"` bash variable, anywhere
under the vendored tree.

**B/G. No citation to a file that does not exist.** Checks B and G are unified into one: every
`.md` citation found anywhere in the vendored tree must resolve to a real file, resolved relative
to the citing file's own directory, relative to the tree root, or — for a bare filename with no
directory component at all — by basename anywhere else in the tree. A prefixed-but-wrong
citation (e.g. a `references/…` path pointing at a file that only exists under
`references/patterns/`) does not get the basename fallback; only a bare filename does. B used to
be a six-string blocklist (`rich-text-icon-aliases`, `node-types.md`, `display-conversion-`,
`/ui-guidelines/`, `/conversion-guidelines/`, `/my-docs/`) that could only catch a citation
already known bad; G generalized past Patch C's specific `guidelines/` prefix (which "Design
Guidelines" prose and "logic-guidelines" compounds would have false-fired on) to every `*.md`
citation actually resolving to a real file, but only recognized a citation written with a literal
`references/` or `guidelines/` prefix. Neither caught a citation written relative to the citing
file's own directory, or as a bare filename with no prefix at all — which is exactly the shape of
two live defects IV-396 measured: `references/sail-verification-checkpoint.md:180` cites
`components/picker-field-users-instructions.md`, and
`references/interface-generation-checklist.md:127` cites `icon-aliases.md`; neither file exists
anywhere in the tree. Repairing those two is Patch B's job, not this check's — see §1. The test
module tracks each individually so a citation reintroduced or newly broken anywhere else in the
tree still fails the suite.

Two things narrowed in the merge, both deliberate, not oversights. **Scope:** old B ran
`grep` over the whole plugin (`iadc-advisor/`); this check runs over the vendored appian tree
only (`iadc-advisor/skills/appian/`, same root G already used) — measured: widening it to the
whole plugin flags over a hundred strings in the plugin's *own* skills (`domain-modeling`,
`setup`, and others cite template placeholders like `outputs/CONTEXT.md` or `decisions.md` in
their own prose, names that are meant to describe a future file a session will create, not
resolve today). The invariant "every `.md` token is a real citation into this tree" is true of
the vendored appian content specifically; it is not true of this repo's own skill docs, so the
check stays scoped to where the invariant holds. **Token shape:** the citation regex only
recognizes a token ending in `.md`. A bare mention of one of B's old blocklisted trees with no
filename after it (`the /my-docs/ folder`) is not caught; the same string followed by an actual
filename (`/my-docs/notes.md`) is, structurally, the same as any other unresolvable citation.
Widening the token match to other extensions is not free either — the appian skill's own prose
legitimately names remote paths like `functions.json` and `VERSION.json` (Appian's hosted API
docs, resolved over the network by the skill's own workflow, never a local file), and a token
match wide enough to catch a local `.json` citation catches those too. Both narrowings are
recorded here rather than closed with a second blocklist, which would need the same maintenance
the six-string one did.

**C./D. The posture block survived, and the six config-readers still read the ambient block.**
Two assertions: the posture heading appears exactly once in `SKILL.md`, and each of
`appian`, `context7`, `office`, `orient`, `pressure-test`, `setup` has a `SKILL.md` that mentions
"Project configuration". The six are named explicitly rather than derived by globbing
`skills/*/SKILL.md` — `iadc-graph` is excluded because **it is not vendored here**: there is no
`iadc-advisor/skills/iadc-graph/` directory any more, since it ships from `IADC-Marketplace` as a
separate plugin dependency (§ "The `iadc-graph` skill is no longer vendored here" in the workshop
`CLAUDE.md`). That is the whole reason — the mirror's own content is beside the point, since this
check never reaches it either way, and it is a file this repo does not own
(`IADC-Marketplace/docs/mirrored-iadc-graph-skill.md` owns its refresh schedule and its own
checks; do not assert a fact about its current content here — it drifts on its own timeline, not
this doc's). `setup` was added because it both writes and reads back `advisor.md`'s values. The
old grep-based version of this check failed **on stderr, not in the count**: a stale literal name
in the list made `grep` warn `No such file or directory` while `wc -l` still returned a number
computed from stdout alone, so one stale name silently turned the true 5 back into the expected
6. The test module removes that failure mode structurally by asserting on each of the six names
individually — a missing or renamed skill is reported by name, not folded into a count.

**Deliberately left unasserted:** Patch D's two carve-outs (`getObjectDependents` is live;
accessibility audits are in scope) have no check of their own — not because a keyword grep is
defeated by a polarity flip (it isn't: an exact-phrase `grep -c` does go 1→0 when "is live"
becomes "is NOT live", verified by direct test). The real reason is §3 step 2: it tells a
refresher to reproduce a patch's *intent* against upstream's new prose, not paste the old sentence
back verbatim. A phrase anchor tight enough to catch a revert fires on a faithful re-authoring
that words the same intent differently; loosened enough to survive rewording, it stops catching
the revert it was meant to. Either way it asserts a sentence, not the invariant §1 actually cares
about — and the live text doesn't even hand you a clean sentence to anchor to: `SKILL.md` reads
"the deletion workflow's dependency check is live … `getObjectDependents` is a `get*` tool and it
works", not "`getObjectDependents` is live" — §1's own paraphrase above is already not a literal
quote of it. The posture-heading count above is the part of Patch D that *is* safe to assert this
way; the carve-outs still need the line-by-line read on every refresh that the rest of this
section exists to make unnecessary.

**E. Namespaced addresses only** — no bare reference to any Advisor skill, or to iadc-graph,
survives in the vendored tree (Patch A, B; IV-362 amended both to require this). Every skill name
including `appian` itself, plus `iadc-graph` (no longer a local directory to list). The trailing
class — not `\b` — excludes a following `:`, `-`, and `/`: `\b` matches at a colon too, so without
this a required `/iadc-graph:iadc-graph` would false-fire identically to a bare `/iadc-graph`. See
below for what this protects against, why none of it is live in this tree yet, and how to tell if
that changes.

**Check E — the trailing class is insurance, not a current repair.** `iadc-graph` occurs zero
times under `iadc-advisor/skills/appian/`, so none of the three exclusions in the trailing class —
`:`, `-`, `/` — is catching anything at check E's actual scope today. `/iadc-graph` is written
freely everywhere else in the repo — the plugin's README and CHANGELOG, the non-vendored skills,
`CLAUDE.md`, the ADRs, this doc, the test module — and a plain `\b` would match at many of those
sites. None of them is in check E's scope: it reads `iadc-advisor/skills/appian/` and nothing else
(`APPIAN_ROOT` in the test module). No count of those outside sites is given here on purpose — any
census of them goes stale the next time anyone cites the graph skill, and the scope is the part
that matters. No hyphenated (`/orient-style`) or path-continuation (`/orient/…`) false positive
exists in the appian tree either.

Each exclusion is forward-looking. `:` protects the correct, required `/iadc-graph:iadc-graph`
citation (the one reference CLAUDE.md warns looks like a typo and isn't) from being flagged as
bare, and also lets a legitimate prose colon (`/orient: the router`) pass that plain `\b` would
have caught as a false positive. `-` and `/` protect a hyphenated compound or a path-like
continuation from the same false-positive fate. None of the three is worth reverting to plain `\b`
over — the appian tree doesn't currently contain what any of them would misfire on.

Observable trigger: re-run check E's pattern with `\b` substituted for the trailing class
`(?:[^:A-Za-z0-9/-]|$)`, over the same tree (`iadc-advisor/skills/appian/`). Today the two outputs
are byte-identical (both empty). The day they diverge, one of these exclusions has started doing
real work — or blocking a real false-fire — in this tree, and this note needs a fresh scope check.

**F. Per-project state is `advisor.md`, never the old `project.md` name** (Patch A; IV-361). F1 is
word-bounded so it doesn't fire on `subproject.md`/`myproject.md`. F2 is paired with a positive
count so a refresher picking a third wrong name (or dropping the mention) can't pass just by
avoiding the literal string `project.md` — but F2's word boundary has to exclude `-` as well as
alphanumerics (IV-396): a plain `\b` still matches inside `iadc-advisor.md`, since a regex word
boundary treats `-` as a non-word character exactly like a space — the same `\b`-matches-at-a-
colon property noted for check E above, here on a hyphen instead of a colon. Measured directly:
baseline count 3, wipe the one real hit → 2, then add an unrelated `…/docs/iadc-advisor.md…`
mention → a plain `\b` bounces the count back to 3, restored by an occurrence other than the one
it targets, while the hyphen-excluding form correctly stays at 2.

**Hygiene: LF only** — CRLF makes every future diff unreadable. Scoped to every file `git` tracks
under the vendored prefix, not just `*.md`, so `LICENSE` and `registry/components-registry.json`
are covered too.

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
