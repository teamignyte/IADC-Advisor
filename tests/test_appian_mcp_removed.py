"""Guard: no live `appian` MCP entry anywhere in the shipped tree (IV-442).

IV-442 drops the `appian` MCP server entirely — `/iadc-advisor:setup` no longer writes it, and
the vendored `appian` skill's two live workflows (blast radius, accessibility audit) are
repointed at the `iadc` graph instead. The point of the ticket is credential removal: after it,
a client following this plugin's docs is never asked for an Appian username or password, and
`/iadc-advisor:setup` never writes `lcp_mcp_server` or an `LCP_*` env var into `.mcp.json`.

That is a whole-shipped-tree invariant, not a vendored-appian-tree one — the actual write site
was `iadc-advisor/skills/setup/mcp-template.json` and `iadc-advisor/skills/setup/SKILL.md`, both
outside `tests/test_vendored_appian_skill.py`'s `APPIAN_ROOT` scope, and the client-facing
`README.md`/`hooks/posture.md` are outside `skills/` entirely. So this check scans the whole
shipped tree (`iadc-advisor/`), every tracked file type, not just `*.md` — `mcp-template.json`
is JSON, not markdown, and a literal env-var name or module path there is exactly the shape this
check exists to catch.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHIPPED_ROOT = REPO_ROOT / "iadc-advisor"

# The exact literal forms that only ever existed to configure the now-removed `appian` MCP
# server: the stdio module it ran (`python -m lcp_mcp_server`) and its four env-var names.
# `LCP_API_PATH` isn't named in the ticket's own prose but was part of the same removed `env`
# block (the old mcp-template.json's `appian` entry) and would be exactly as much of a
# regression left standing.
FORBIDDEN_RE = re.compile(
    r"lcp_mcp_server|LCP_URL|LCP_USERNAME|LCP_PASSWORD|LCP_TOOL_MODE|LCP_API_PATH"
)


def _tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", str(root)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [REPO_ROOT / line for line in result.stdout.splitlines() if line]


def _find_forbidden_hits(root: Path) -> list[tuple[Path, int, str]]:
    hits = []
    for f in _tracked_files(root):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary asset (e.g. a registry blob) -- not a config or prose site
        for lineno, line in enumerate(text.splitlines(), start=1):
            m = FORBIDDEN_RE.search(line)
            if m:
                hits.append((f, lineno, m.group(0)))
    return hits


def test_no_lcp_appian_mcp_config_anywhere_in_shipped_tree():
    hits = _find_forbidden_hits(SHIPPED_ROOT)
    assert not hits, (
        "found a removed appian-MCP config token in the shipped tree (IV-442 regression): "
        f"{hits}"
    )


def _inject_and_scan(target: Path, injected_content: str) -> tuple[list[tuple[Path, int, str]], int]:
    """Temporarily append `injected_content` to a real tracked file already inside
    `SHIPPED_ROOT`, drive the guard's actual entry point (`_find_forbidden_hits(SHIPPED_ROOT)`)
    over it, then revert unconditionally.

    The property under test is "the scan reaches every tracked file in the shipped tree" -- not
    "the regex matches this string". Calling `_find_forbidden_hits(SHIPPED_ROOT)` for real,
    against a real tracked file, means this is sensitive to a regression in either half of the
    guard: if `_tracked_files` stops walking the tree, the injected line is never read; if
    `SHIPPED_ROOT` is narrowed to a subset that excludes `target`, the same thing happens. A
    control built by reimplementing the scan loop over a synthetic `tmp_path`, or by calling
    `FORBIDDEN_RE.search` directly, is blind to both regressions -- which is exactly what let the
    two controls this replaces stay green while stubbed to `return []` and while `SHIPPED_ROOT`
    was collapsed to `skills/appian/`.
    """
    original = target.read_text(encoding="utf-8")
    mutated = original.rstrip("\n") + "\n" + injected_content.rstrip("\n") + "\n"
    injected_lineno = len(mutated.splitlines())
    target.write_text(mutated, encoding="utf-8")
    # Did-it-apply: confirm the write landed before trusting anything the scan reports.
    assert target.read_text(encoding="utf-8") == mutated, f"injection into {target} did not apply"
    try:
        hits = _find_forbidden_hits(SHIPPED_ROOT)
    finally:
        target.write_text(original, encoding="utf-8")
        assert target.read_text(encoding="utf-8") == original, (
            f"revert of {target} did not restore the original content"
        )
    return hits, injected_lineno


def test_catches_a_reintroduced_lcp_env_var_outside_the_vendored_appian_tree():
    # README.md sits outside `skills/` entirely -- the exact site
    # test_vendored_appian_skill.py's APPIAN_ROOT-scoped suite cannot see, and one of the two
    # real write sites this module's own docstring names as the reason a whole-tree scan exists.
    target = SHIPPED_ROOT / "README.md"
    hits, lineno = _inject_and_scan(target, "Set `LCP_URL` to your Appian tenant's address.")
    assert (target, lineno, "LCP_URL") in hits, (
        f"real scan over SHIPPED_ROOT failed to catch a reintroduced LCP_URL token in {target}: "
        f"{hits}"
    )


def test_catches_a_bare_module_path_with_no_env_var_present():
    # Distinct fact from the control above: a reintroduced `command`/`args` block naming the
    # module but no env vars yet (someone restores the stdio launch line first) must still be
    # caught -- the module path alone is enough to know the appian MCP server is back. Same
    # real-scan mechanism, a different one of the module's two named write sites
    # (hooks/posture.md), so this control is independently sensitive to both regressions too.
    target = SHIPPED_ROOT / "hooks" / "posture.md"
    hits, lineno = _inject_and_scan(target, "python -m lcp_mcp_server")
    assert (target, lineno, "lcp_mcp_server") in hits, (
        f"real scan over SHIPPED_ROOT failed to catch a bare lcp_mcp_server module path in "
        f"{target}: {hits}"
    )


def test_catches_a_reintroduced_lcp_env_var_under_skills():
    # Neither control above touches `skills/` at all -- both targets (README.md,
    # hooks/posture.md) sit outside it. The module's own docstring (`:9-15`) names
    # `iadc-advisor/skills/setup/mcp-template.json` as *the actual write site* the whole-tree
    # scope exists for, and no control exercised that subtree: narrowing `_tracked_files` to
    # drop every path containing `/skills/` left all three prior tests green (probe pasted in
    # the fix report), because none of them ever reads a file under it. This control closes that
    # axis the same way the other two closed theirs -- inject into a real tracked file inside
    # `skills/`, drive the real scan, assert it's caught.
    target = SHIPPED_ROOT / "skills" / "setup" / "mcp-template.json"
    hits, lineno = _inject_and_scan(target, '"LCP_URL": "https://example.appiancloud.com"')
    assert (target, lineno, "LCP_URL") in hits, (
        f"real scan over SHIPPED_ROOT failed to catch a reintroduced LCP_URL token under "
        f"skills/ in {target}: {hits}"
    )
