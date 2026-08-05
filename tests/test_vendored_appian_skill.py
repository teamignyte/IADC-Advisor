"""Executable form of docs/vendored-appian-skill.md's guard checks (IV-396).

Family ADR 0011 (docs/adr/0011-scripts-replace-prose-once-a-check-clears-a-viability-test.md,
umbrella repo) is the governing standard: each of these checks is deterministic, has a fixed
pass/fail outcome, is testable with a fixture and no model in the loop, and every input it needs
(file content on disk) is observable from this process — so it ships as code, not prose a
maintainer runs by hand. docs/vendored-appian-skill.md §4 keeps the explanation of what each
check protects and why; this module is the machine-readable form.

Every "resolves against real content" test below runs against the actual vendored tree at
iadc-advisor/skills/appian/ and iadc-advisor/skills/*/SKILL.md, so a passing suite means the
real tree is clean today. Every "catches ..." test below builds a minimal fixture under
tmp_path that violates exactly one rule and asserts the corresponding check flags it — proving
each check can fail, not just that it currently doesn't. Every test/rule pairing here was
verified directly: disable the predicate in a scratch copy of this module, confirm the
corresponding test then fails, restore the module, confirm the suite passes again.

Checks B ("no citation to a file that does not exist") and G ("no dangling references/ or
guidelines/ citation") are unified below into one citation-resolution check. Both were partial:
B was a six-string blocklist of citations known bad at one point in time, and could not catch a
new one; G only recognized a citation written with a literal "references/" or "guidelines/"
prefix, missing a citation written relative to the citing file's own directory (e.g.
"components/foo.md" from within references/) or as a bare filename. A check derived from the
tree itself closes both of those resolution gaps, and does not need the maintenance a blocklist
needs -- but it is scoped to the vendored appian tree (narrower than old B's whole-plugin scan)
and only recognizes a ".md"-suffixed token (narrower than old B's blocklist, which also matched a
bare directory-prefix mention with no filename). docs/vendored-appian-skill.md's B/G section
records both narrowings and why they are deliberate rather than restored with a second blocklist.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "iadc-advisor" / "skills"
APPIAN_ROOT = SKILLS_ROOT / "appian"


def _md_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def _find_pattern(root: Path, pattern: re.Pattern[str]) -> list[tuple[Path, int]]:
    """Every (file, line number) under `root` where `pattern` matches a line."""
    hits = []
    for f in _md_files(root):
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern.search(line):
                hits.append((f, lineno))
    return hits


# --- Check A: no literal Appian version as configuration, anywhere -----------------------
#
# Upstream hardcodes the Appian version (`**Appian Version:** 26.6`, and a `VERSION="26.6"`
# bash variable in two reference files). Patch A (docs/vendored-appian-skill.md §1) repoints
# both at the ambient Project configuration instead, because plugin skills live in a shared,
# read-only cache serving every client project — there is exactly one copy of either line,
# and it cannot hold a value specific to one client. This fails silently: nothing errors, the
# skill just tells a client on 25.3 that they are on 26.6.

VERSION_DECL_RE = re.compile(r"Appian Version:\*\* *[0-9]")
VERSION_BASH_RE = re.compile(r'VERSION="2[0-9]')


def test_a1_no_hardcoded_appian_version_declaration():
    hits = _find_pattern(APPIAN_ROOT, VERSION_DECL_RE)
    assert not hits, f"hardcoded '**Appian Version:** N' declaration found (Patch A reverted): {hits}"


def test_a1_catches_reintroduced_version_declaration(tmp_path):
    (tmp_path / "SKILL.md").write_text("**Appian Version:** 26.6\n", encoding="utf-8")
    assert _find_pattern(tmp_path, VERSION_DECL_RE), (
        "check A1 failed to catch a reintroduced '**Appian Version:** N' declaration"
    )


def test_a2_no_hardcoded_version_bash_variable():
    hits = _find_pattern(APPIAN_ROOT, VERSION_BASH_RE)
    assert not hits, f"hardcoded VERSION=\"2X...\" bash variable found (Patch A reverted): {hits}"


def test_a2_catches_reintroduced_version_bash_variable(tmp_path):
    (tmp_path / "documentation-lookup-strategy.md").write_text(
        'VERSION="26.6"\n', encoding="utf-8"
    )
    assert _find_pattern(tmp_path, VERSION_BASH_RE), (
        'check A2 failed to catch a reintroduced VERSION="2X..." bash variable'
    )


# --- Checks B/G (unified): no citation to a file that does not exist ---------------------
#
# A citation resolves against the tree in one of three ways, matching how a reader actually
# follows it: relative to the citing file's own directory (a same-directory sibling, a `../`
# parent reference, or a subdirectory-relative citation like `components/foo.md` written from
# within `references/`); relative to the vendored tree's own root (a citation written as a
# full in-tree path, e.g. `references/sail.md` from `SKILL.md`); or, for a bare filename, by
# basename anywhere else in the tree (e.g. `card_lists.md`, meant to resolve into
# `references/patterns/` regardless of which file cites it). A token beginning `docs/` is
# never a citation into this tree — it is always the client's own ambient
# `docs/agents/advisor.md`, injected at session start (Patch A); no `docs/` directory exists
# here to resolve it against.
#
# The basename fallback applies only to a bare filename with no directory component at all (no
# "/" anywhere in the token). A prefixed-but-wrong citation, e.g. "references/card_lists.md"
# when the real file lives at "references/patterns/card_lists.md", must still resolve for
# real — the "/" guard keeps a wrong prefix from being waved through just because some file
# with the trailing basename exists somewhere else in the tree, matching what old check G's
# prefix-based scan actually required. Only a bare filename with no prefix at all gets the
# permissive basename search, and it stays deliberately permissive there: it does not verify a
# bare citation names the *specific* file its author intended, only that some file with that
# name exists somewhere in the tree. Tightening it further would need knowing each bare
# citation's intended directory, information the citation itself doesn't carry.

CITATION_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*\.md")

# Documented, measured exceptions (IV-396): these two citations exist in the real vendored
# tree today and do not resolve. Repairing them is Patch B's job (docs/vendored-appian-skill.md
# §1), not this check's — a check that repaired content itself would not be a guard. Excluded
# by exact (citing file, cited token) pair, so any *other* dangling citation anywhere else in
# the tree still fails test_bg_citations_resolve_to_real_files below. The two xfail tests
# beneath it track these individually: either turns XPASS (caught by strict=True) the day its
# citation is repaired, which is the signal to delete that test and this exception.
KNOWN_DANGLING_CITATIONS = {
    ("references/interface-generation-checklist.md", "icon-aliases.md"),
    ("references/sail-verification-checkpoint.md", "components/picker-field-users-instructions.md"),
}


def _find_dangling_citations(root: Path) -> list[tuple[Path, str]]:
    md_files = _md_files(root)
    by_basename = {p.name for p in md_files}
    dangling: set[tuple[Path, str]] = set()
    for f in md_files:
        for m in CITATION_TOKEN_RE.finditer(f.read_text(encoding="utf-8")):
            token = m.group(0)
            if token.startswith("docs/"):
                continue
            if (f.parent / token).resolve().is_file():
                continue
            if (root / token).resolve().is_file():
                continue
            if "/" not in token and token in by_basename:
                continue
            dangling.add((f, token))
    return sorted(dangling, key=lambda pair: (str(pair[0]), pair[1]))


def test_bg_citations_resolve_to_real_files():
    dangling = _find_dangling_citations(APPIAN_ROOT)
    unexpected = [
        (f, t)
        for f, t in dangling
        if (str(f.relative_to(APPIAN_ROOT)), t) not in KNOWN_DANGLING_CITATIONS
    ]
    assert not unexpected, f"citation(s) to a file that does not exist: {unexpected}"


def test_bg_catches_a_new_dangling_citation(tmp_path):
    (tmp_path / "a.md").write_text(
        "See rich-text-icon-aliases.md for the closed vocabulary.\n", encoding="utf-8"
    )
    dangling = _find_dangling_citations(tmp_path)
    assert dangling, "citation check failed to catch a fabricated dangling citation"


def test_bg_resolves_relative_to_citing_directory(tmp_path):
    # This is defect 1's exact shape (IV-396): sail-verification-checkpoint.md, itself inside
    # references/, cites "components/picker-field-users-instructions.md" -- a citation that
    # only makes sense resolved against the *citing file's own directory*
    # (references/components/...), not against the tree root (components/... at the root
    # doesn't exist and isn't what the citation means). The old check G required a literal
    # "references/" or "guidelines/" prefix on the citation text itself and so never even
    # looked at this one; resolving relative to the citing file's directory catches it
    # instead, without needing that prefix.
    (tmp_path / "references" / "components").mkdir(parents=True)
    (tmp_path / "references" / "components" / "real.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "references" / "b.md").write_text(
        "a directory-relative sibling: components/real.md\n", encoding="utf-8"
    )
    dangling = _find_dangling_citations(tmp_path)
    assert dangling == [], f"a directory-relative citation that does resolve was flagged: {dangling}"


def test_bg_resolves_relative_to_tree_root(tmp_path):
    # Exercises the tree-root branch on its own: a citation written as a full in-tree path
    # from a file whose own directory does not contain it. The token carries a "/", so the
    # basename fallback is out of the running by construction (it only applies to a bare
    # filename) -- if this resolves at all, the tree-root branch is what did it.
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "logo-instructions.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "references").mkdir()
    (tmp_path / "references" / "b.md").write_text(
        "a root-relative citation: assets/logo-instructions.md\n", encoding="utf-8"
    )
    dangling = _find_dangling_citations(tmp_path)
    assert dangling == [], f"a root-relative citation that does resolve was flagged: {dangling}"


def test_bg_basename_fallback_does_not_rescue_a_wrong_prefix(tmp_path):
    # This is Patch C's exact shape (IV-396): a citation with the right basename but the wrong
    # directory prefix must not resolve just because some file with that basename exists
    # somewhere else in the tree. The basename fallback is for a bare filename only (no "/" in
    # the token at all) -- a prefixed token has to resolve for real, the same way old check G
    # required. Measured: without the "/" guard, this fixture's dangling citation silently
    # resolves, because a file named "tabs.md" happens to exist under a different directory.
    (tmp_path / "references" / "patterns").mkdir(parents=True)
    (tmp_path / "references" / "patterns" / "tabs.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "references" / "layouts").mkdir(parents=True)
    (tmp_path / "references" / "layouts" / "b.md").write_text(
        "wrong prefix: guidelines/patterns/tabs.md\n", encoding="utf-8"
    )
    dangling = _find_dangling_citations(tmp_path)
    assert dangling, (
        "basename fallback wrongly resolved a prefixed citation with the wrong directory "
        "just because a file with that basename exists elsewhere in the tree"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "IV-396: interface-generation-checklist.md cites icon-aliases.md, and no such file "
        "exists anywhere in the vendored tree. Repairing it is Patch B's job "
        "(docs/vendored-appian-skill.md §1); this test starts passing (XPASS) the day it is "
        "fixed, which is the signal to delete this test and its KNOWN_DANGLING_CITATIONS entry."
    ),
)
def test_known_defect_icon_aliases_citation_should_resolve():
    dangling = {
        (str(f.relative_to(APPIAN_ROOT)), t) for f, t in _find_dangling_citations(APPIAN_ROOT)
    }
    assert ("references/interface-generation-checklist.md", "icon-aliases.md") not in dangling


@pytest.mark.xfail(
    strict=True,
    reason=(
        "IV-396: sail-verification-checkpoint.md cites components/picker-field-users-"
        "instructions.md, and no such file exists anywhere in the vendored tree. Repairing "
        "it is Patch B's job (docs/vendored-appian-skill.md §1); this test starts passing "
        "(XPASS) the day it is fixed, which is the signal to delete this test and its "
        "KNOWN_DANGLING_CITATIONS entry."
    ),
)
def test_known_defect_picker_field_citation_should_resolve():
    dangling = {
        (str(f.relative_to(APPIAN_ROOT)), t) for f, t in _find_dangling_citations(APPIAN_ROOT)
    }
    assert (
        "references/sail-verification-checkpoint.md",
        "components/picker-field-users-instructions.md",
    ) not in dangling


# --- Check C/D: the posture block survived, and the config-readers still read it ----------
#
# SKILL.md carries a local "## Posture: read-only / advisory" section stating this is an
# architect, not a builder. Upstream has nothing like it; losing it flips the plugin's
# most-loaded skill against the product's premise, and nothing about a missing heading fails
# loudly (Patch D). Six skills — appian, context7, office, orient, pressure-test, setup — must
# each mention the ambient "Project configuration" block, since each reads a per-project value
# from it (setup also writes it back). This list is named explicitly rather than derived by
# globbing skills/*/SKILL.md, so a skill that stops reading the block is caught by exactly the
# same mechanism as a skill that was renamed or removed — both fail as an explicit, named
# assertion. That matters because the old grep-based version of this check failed on stderr,
# not in its count: a stale literal name in the list makes `grep` warn "No such file or
# directory" while `wc -l` still returns a number computed from stdout alone, so a maintainer
# piping stderr into that count (e.g. with `2>&1 | wc -l`) sees a stale name's absence folded
# back in as if it were a real hit. Asserting on each name individually removes that failure
# mode structurally: a missing file is a missing file, not a warning a count can quietly
# absorb.

POSTURE_HEADING = "## Posture: read-only / advisory"
CONFIG_READER_SKILLS = ("appian", "context7", "office", "orient", "pressure-test", "setup")


def _posture_heading_count(skill_md: Path) -> int:
    return skill_md.read_text(encoding="utf-8").splitlines().count(POSTURE_HEADING)


def test_c_posture_heading_survives_exactly_once():
    count = _posture_heading_count(APPIAN_ROOT / "SKILL.md")
    assert count == 1, f"expected exactly one {POSTURE_HEADING!r} heading in SKILL.md, found {count}"


def test_c_catches_a_dropped_posture_heading(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("# Some other heading\n", encoding="utf-8")
    assert _posture_heading_count(skill_md) == 0, (
        "check C failed to catch a dropped posture heading"
    )


def _config_reader_report(skills_root: Path, names) -> tuple[list[str], list[str]]:
    """Return (missing, not_reading): skill names with no SKILL.md on disk, and skill names
    whose SKILL.md exists but no longer mentions "Project configuration"."""
    missing = []
    not_reading = []
    for name in names:
        skill_md = skills_root / name / "SKILL.md"
        if not skill_md.is_file():
            missing.append(name)
            continue
        if "Project configuration" not in skill_md.read_text(encoding="utf-8"):
            not_reading.append(name)
    return missing, not_reading


def test_d_six_skills_read_the_ambient_config():
    missing, not_reading = _config_reader_report(SKILLS_ROOT, CONFIG_READER_SKILLS)
    assert not missing, f"config-reader skill(s) not found on disk: {missing}"
    assert not not_reading, f"skill(s) no longer mention the ambient Project configuration: {not_reading}"


def test_d_catches_a_stale_skill_name(tmp_path):
    for name in ("appian", "context7", "office", "orient", "pressure-test"):
        d = tmp_path / name
        d.mkdir()
        (d / "SKILL.md").write_text("...Project configuration...\n", encoding="utf-8")
    missing, _ = _config_reader_report(
        tmp_path, CONFIG_READER_SKILLS[:-1] + ("setup-renamed",)
    )
    assert missing == ["setup-renamed"], (
        "check D failed to name a stale/renamed skill explicitly instead of silently "
        "miscounting it"
    )


def test_d_catches_a_dropped_config_read(tmp_path):
    d = tmp_path / "setup"
    d.mkdir()
    (d / "SKILL.md").write_text("no ambient config mention here\n", encoding="utf-8")
    _, not_reading = _config_reader_report(tmp_path, ("setup",))
    assert not_reading == ["setup"], "check D failed to catch a skill that stopped reading the config"


# --- Check E: namespaced addresses only ----------------------------------------------------
#
# No bare reference to any Advisor skill, or to iadc-graph, may survive in the vendored tree
# (Patch A, B; IV-362 amended both to require this). The skill-name set is read from disk
# (`skills_root`'s own subdirectories) plus "iadc-graph", which is no longer a local directory
# to list. The trailing exclusion class — not a plain word boundary — excludes a following
# ':', '-', and '/': a word boundary matches at a colon too, so without this exclusion a
# required `/iadc-graph:iadc-graph` citation would false-fire identically to a bare
# `/iadc-graph`.

def _bare_skill_ref_pattern(skills_root: Path) -> re.Pattern[str]:
    names = sorted(p.name for p in skills_root.iterdir() if p.is_dir())
    names.append("iadc-graph")
    alternation = "|".join(re.escape(n) for n in names)
    return re.compile(rf"(?<![:A-Za-z0-9/])/(?:{alternation})(?:[^:A-Za-z0-9/-]|$)")


def test_e_no_bare_skill_or_iadc_graph_references():
    pattern = _bare_skill_ref_pattern(SKILLS_ROOT)
    hits = []
    for f in _md_files(APPIAN_ROOT):
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern.search(line):
                hits.append((f, lineno, line))
    assert not hits, f"bare (non-namespaced) skill/iadc-graph reference found: {hits}"


def test_e_catches_a_bare_skill_reference(tmp_path):
    skills_root = tmp_path / "skills"
    (skills_root / "orient").mkdir(parents=True)
    pattern = _bare_skill_ref_pattern(skills_root)
    assert pattern.search("Run /orient to get started."), (
        "check E failed to catch a bare /orient reference"
    )


def test_e_does_not_flag_the_required_namespaced_form(tmp_path):
    skills_root = tmp_path / "skills"
    (skills_root / "orient").mkdir(parents=True)
    pattern = _bare_skill_ref_pattern(skills_root)
    assert not pattern.search("Call /iadc-graph:iadc-graph for the graph skill."), (
        "the required, namespaced /iadc-graph:iadc-graph form was wrongly flagged as bare"
    )


# --- Check F: per-project state is advisor.md, never the old project.md name -------------
#
# Patch A (IV-361) renamed Advisor's per-project state file to advisor.md so a generic
# "project.md" wouldn't read as family-wide config once the Tester ships tester.md alongside
# it. F1 is word-bounded so it doesn't fire on subproject.md/myproject.md. F2 is paired with a
# positive count so a refresher picking a third wrong name (or dropping the mention entirely)
# can't pass just by avoiding the literal string "project.md" — but F2 must itself be
# word-bounded (IV-396): unbounded, its count is restored by any other file whose path merely
# contains "advisor.md" as a substring (e.g. a mention of `docs/iadc-advisor.md`), which
# defeats the exact anti-evasion property it exists to provide. A plain `\b` is not enough on
# its own: regex word boundaries treat `-` as a non-word character exactly like a space, so
# `\badvisor\.md\b` still matches inside "iadc-advisor.md" (there is a boundary right after
# the hyphen) — the same "\b matches at a colon too" property check E's own comment already
# names, here on a hyphen instead of a colon. The leading edge below is a negative lookbehind
# that excludes alphanumerics, `_`, and `-` explicitly, so a hyphenated prefix can no longer
# manufacture a false boundary; `/agents/advisor.md`, the real citation, is unaffected since
# `/` is not in the excluded set.

PROJECT_MD_RE = re.compile(r"\bproject\.md\b|\bproject\.local\.md\b")
ADVISOR_MD_RE = re.compile(r"(?<![A-Za-z0-9_-])advisor\.md\b")


def test_f1_no_old_project_md_name():
    hits = _find_pattern(APPIAN_ROOT, PROJECT_MD_RE)
    assert not hits, f"old 'project.md' name found (Patch A/IV-361 reverted): {hits}"


def test_f1_catches_the_old_name(tmp_path):
    (tmp_path / "SKILL.md").write_text("edit project.md to configure\n", encoding="utf-8")
    assert _find_pattern(tmp_path, PROJECT_MD_RE), "check F1 failed to catch 'project.md'"


def test_f1_word_boundary_does_not_false_fire_on_similar_names(tmp_path):
    (tmp_path / "SKILL.md").write_text(
        "edit subproject.md or myproject.md, never project\n", encoding="utf-8"
    )
    assert not _find_pattern(tmp_path, PROJECT_MD_RE), (
        "check F1 false-fired on subproject.md/myproject.md"
    )


def _advisor_md_reader_files(root: Path) -> list[Path]:
    return [f for f in _md_files(root) if ADVISOR_MD_RE.search(f.read_text(encoding="utf-8"))]


def test_f2_three_files_mention_advisor_md():
    files = _advisor_md_reader_files(APPIAN_ROOT)
    assert len(files) == 3, f"expected 3 files mentioning advisor.md, found {len(files)}: {files}"


def test_f2_word_boundary_resists_the_measured_evasion(tmp_path):
    real = tmp_path / "real.md"
    real.write_text("reads docs/agents/advisor.md at session start\n", encoding="utf-8")
    assert len(_advisor_md_reader_files(tmp_path)) == 1

    # Wipe the one real hit.
    real.write_text("no mention of the per-project file here\n", encoding="utf-8")
    assert len(_advisor_md_reader_files(tmp_path)) == 0

    # Add an unrelated file whose path merely contains "advisor.md" as a substring.
    decoy = tmp_path / "decoy.md"
    decoy.write_text("see docs/iadc-advisor.md for background\n", encoding="utf-8")
    assert len(_advisor_md_reader_files(tmp_path)) == 0, (
        "word-bounded check F2 was fooled by 'iadc-advisor.md' containing 'advisor.md' as a "
        "substring -- the exact anti-evasion defect IV-396 measured and fixed"
    )


# --- Hygiene: LF only ------------------------------------------------------------------------
#
# CRLF makes every future diff unreadable. Scoped to every file `git` tracks under the
# vendored prefix, not just *.md, so LICENSE and registry/components-registry.json are covered
# too.

def _has_crlf(path: Path) -> bool:
    return b"\r\n" in path.read_bytes()


def _tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", str(root)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [REPO_ROOT / line for line in result.stdout.splitlines() if line]


def test_hygiene_no_crlf_line_endings():
    crlf_files = [f for f in _tracked_files(APPIAN_ROOT) if _has_crlf(f)]
    assert not crlf_files, f"CRLF line endings found (breaks every future diff): {crlf_files}"


def test_hygiene_catches_a_crlf_file(tmp_path):
    f = tmp_path / "x.md"
    f.write_bytes(b"unix\nline endings\n")
    assert not _has_crlf(f)
    f.write_bytes(b"crlf\r\nline endings\r\n")
    assert _has_crlf(f), "CRLF detector failed to catch a mutated CRLF file"
