"""Wires check-portable-invocation.py into the suite so it actually runs (IV-392, IV-402).

check-portable-invocation.py is deliberately named `check-*`, not `test_*`, and its functions are
`check_command_entry`/`main`, not `test_*`. Default pytest collection will not pick it up, and
widening `python_files` to catch `check_*.py` would collect the module and find zero `test_*`
functions inside it — a collection that reports success without exercising anything. So this thin
wrapper invokes the real script the way a human would: as a subprocess, against the actual shipped
hooks.json, asserting its exit code.

The `pytest.mark.parametrize` below exists for one reason only: it bakes the script's own filename
into the pytest node id, so `python3 -m pytest -v` prints a log line that names
check-portable-invocation.py verbatim — proof it ran, not an inference from the wrapper's own name.

The happy-path test below proves the script accepts a valid hooks.json; it says nothing about
whether the script would reject an invalid one. The three tests after it each build a minimal
hooks.json in `tmp_path` that violates exactly one of the three portability rules the script's own
docstring names, and assert both that the script exits 1 and that its stdout names the rule that
fired — so a checker that stopped checking (returns success unconditionally) is caught, not just a
checker that stopped running.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECK_SCRIPT = REPO_ROOT / "tests" / "hooks" / "check-portable-invocation.py"
HOOKS_JSON = REPO_ROOT / "iadc-advisor" / "hooks" / "hooks.json"


def _run_check(hooks_json_path):
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), str(hooks_json_path)],
        capture_output=True,
        text=True,
    )


def _write_hooks_json(tmp_path, command, *, shell="bash"):
    """Write a minimal single-entry hooks.json to tmp_path and return its path.

    `shell=None` omits the "shell" key entirely (rule 3 violation); any other value is written
    as given.
    """
    entry = {"type": "command", "command": command}
    if shell is not None:
        entry["shell"] = shell
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(
        json.dumps({"hooks": {"SessionStart": [{"hooks": [entry]}]}})
    )
    return hooks_json_path


@pytest.mark.parametrize("script_name", [CHECK_SCRIPT.name])
def test_check_portable_invocation_passes_on_shipped_hooks_json(script_name):
    assert CHECK_SCRIPT.is_file(), f"{script_name} moved or was renamed out of tests/hooks/"
    assert HOOKS_JSON.is_file(), f"shipped hooks.json not found at {HOOKS_JSON}"

    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), str(HOOKS_JSON)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{script_name} rejected the shipped hooks.json (exit {result.returncode}):\n"
        f"{result.stdout}{result.stderr}"
    )


def test_rejects_missing_shell_bash(tmp_path):
    """Rule 3: an entry with no "shell": "bash" must be rejected, not silently accepted."""
    (tmp_path / "script").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(tmp_path, "dispatch.cmd script", shell=None)

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "rule 3" in result.stdout, result.stdout


def test_rejects_non_dispatcher_command(tmp_path):
    """Rule 2: a bare interpreter prefix (no .cmd dispatcher) must be rejected."""
    hooks_json_path = _write_hooks_json(tmp_path, "bash hooks/script")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "rule 2" in result.stdout, result.stdout


def test_rejects_extensioned_target_script(tmp_path):
    """Rule 1: a target script carrying a suffix (e.g. .sh) must be rejected."""
    hooks_json_path = _write_hooks_json(tmp_path, "dispatch.cmd hooks/script.sh")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "rule 1" in result.stdout, result.stdout
