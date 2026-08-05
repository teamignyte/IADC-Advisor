"""Wires IV-392's check-portable-invocation.py into the suite so it actually runs (IV-402).

check-portable-invocation.py is deliberately named `check-*`, not `test_*`, and its functions are
`check_command_entry`/`main`, not `test_*`. Default pytest collection will not pick it up, and
widening `python_files` to catch `check_*.py` would collect the module and find zero `test_*`
functions inside it — a collection that passes vacuously, which is exactly the decorative-check
defect this ticket exists to remove. So this thin wrapper invokes the real script the way a human
would: as a subprocess, against the actual shipped hooks.json, asserting its exit code.

The `pytest.mark.parametrize` below exists for one reason only: it bakes the script's own filename
into the pytest node id, so `python3 -m pytest -v` prints a log line that names
check-portable-invocation.py verbatim — proof it ran, not an inference from the wrapper's own name.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECK_SCRIPT = REPO_ROOT / "tests" / "hooks" / "check-portable-invocation.py"
HOOKS_JSON = REPO_ROOT / "iadc-advisor" / "hooks" / "hooks.json"


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
