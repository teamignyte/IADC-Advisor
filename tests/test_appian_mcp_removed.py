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


def test_catches_a_single_reintroduced_lcp_token(tmp_path):
    # Discriminating control: the check must actually fail on exactly one reintroduced
    # instance, not just on an empty/never-matching pattern.
    (tmp_path / "mcp-template.json").write_text(
        '{"mcpServers": {"appian": {"env": {"LCP_URL": "https://x"}}}}\n', encoding="utf-8"
    )
    hits = []
    for f in tmp_path.rglob("*"):
        if f.is_file():
            for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
                m = FORBIDDEN_RE.search(line)
                if m:
                    hits.append((f, lineno, m.group(0)))
    assert hits, "check failed to catch a single reintroduced LCP_URL token"


def test_catches_the_bare_module_path_without_any_env_var():
    # A reintroduced `command`/`args` block naming the module but no env vars (e.g. someone
    # restores the stdio launch line but not the env block yet) must still be caught -- the
    # module path alone is enough to know the appian MCP server is back.
    text = 'python -m lcp_mcp_server\n'
    assert FORBIDDEN_RE.search(text), "check failed to catch a bare lcp_mcp_server module path"
