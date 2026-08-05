"""Wires check-portable-invocation.py into the suite so it actually runs (IV-392, IV-402).

check-portable-invocation.py is deliberately named `check-*`, not `test_*`, and its functions are
`check_command_entry`/`main`, not `test_*`. Default pytest collection will not pick it up, and
widening `python_files` to catch `check_*.py` would collect the module and find zero `test_*`
functions inside it — a collection that reports success without exercising anything. So this thin
wrapper invokes the real script the way a human would: as a subprocess, against the actual shipped
hooks.json, asserting its exit code.

The `pytest.mark.parametrize` on the happy-path test exists for one reason only: it bakes the
script's own filename into the pytest node id, so `python3 -m pytest -v` prints a log line that
names check-portable-invocation.py verbatim — proof it ran, not an inference from the wrapper's
own name.

The happy-path test proves the script accepts a valid hooks.json; it says nothing about whether
the script would reject an invalid one. Every test after it builds a minimal hooks.json (and, for
most, a `hooks/` directory alongside it — the checker resolves a dispatcher and its script
argument against real files on disk, not just the command string) that violates exactly one of the
script's own predicates, and asserts both that the script exits 1 and that its stdout carries a
message fragment unique to that predicate — so a checker that stopped enforcing one rule (returns
success unconditionally, or falls through to a different check that happens to share the same
generic wording) is caught, not just a checker that stopped running entirely.

**Isolation matters more than exit code.** A fixture that merely deletes the file its own target
names, without also creating the dispatcher, can still fail for the *wrong* reason (a missing
dispatcher, not the rule under test) and still pass its assertions if the two violation messages
happen to share a substring — a discriminating fixture proves nothing if it never isolates the one
predicate it claims to guard. Every fixture below that exercises an on-disk check creates every
*other* file the checker might otherwise stumble on, so exactly one violation fires, asserted by
`FAIL:`-line count where that matters. Every test/rule pairing here was verified directly: disable
the predicate in a scratch copy of the script, confirm the corresponding test then fails, restore
the script, confirm the suite passes again.
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

# The dispatcher token every fixture below uses, matching the shipped hooks.json's own
# convention: an absolute-from-plugin-root reference, never a bare relative name.
DISPATCHER_CMD = '"${CLAUDE_PLUGIN_ROOT}/hooks/dispatch.cmd"'


def _run_check(hooks_json_path):
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), str(hooks_json_path)],
        capture_output=True,
        text=True,
    )


def _hooks_dir(tmp_path):
    """A `hooks/` directory under tmp_path, mirroring `iadc-advisor/hooks/`'s own layout: this
    is where hooks.json, `dispatch.cmd`, and the scripts it names all live side by side, and is
    what `${CLAUDE_PLUGIN_ROOT}` resolves to the parent of.
    """
    d = tmp_path / "hooks"
    d.mkdir()
    return d


def _write_hooks_json(hooks_dir, command, *, shell="bash"):
    """Write a minimal single-entry hooks.json into `hooks_dir` and return its path.

    `shell=None` omits the "shell" key entirely (rule 3 violation); any other value is written
    as given.
    """
    entry = {"type": "command", "command": command}
    if shell is not None:
        entry["shell"] = shell
    hooks_json_path = hooks_dir / "hooks.json"
    hooks_json_path.write_text(
        json.dumps({"hooks": {"SessionStart": [{"hooks": [entry]}]}})
    )
    return hooks_json_path


@pytest.mark.parametrize("script_name", [CHECK_SCRIPT.name])
def test_check_portable_invocation_passes_on_shipped_hooks_json(script_name):
    assert CHECK_SCRIPT.is_file(), f"{script_name} moved or was renamed out of tests/hooks/"
    assert HOOKS_JSON.is_file(), f"shipped hooks.json not found at {HOOKS_JSON}"

    result = _run_check(HOOKS_JSON)
    assert result.returncode == 0, (
        f"{script_name} rejected the shipped hooks.json (exit {result.returncode}):\n"
        f"{result.stdout}{result.stderr}"
    )


# --- Rule 3: "shell": "bash" -------------------------------------------------------------


def test_rejects_missing_shell_bash(tmp_path):
    """Rule 3: an entry with no "shell": "bash" must be rejected, not silently accepted.

    Isolated: both the dispatcher and its target script exist on disk, so nothing else about
    this entry can fail — the one violation can only be rule 3.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    (hooks_dir / "script").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(hooks_dir, f"{DISPATCHER_CMD} script", shell=None)

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "rule 3" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


# --- Rule 2: cross-platform dispatcher, and that dispatcher must exist --------------------


def test_rejects_non_dispatcher_command(tmp_path):
    """Rule 2: a bare interpreter prefix (no .cmd dispatcher) must be rejected.

    Isolated: the target script exists on disk and is extensionless, so the only possible
    violation is the missing dispatcher (the on-disk existence checks below only apply once a
    dispatcher is recognized at all, so a non-dispatcher first token can't trip them).
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "script").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(hooks_dir, "bash script")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "rule 2" in result.stdout, result.stdout
    assert "is not invoked through a cross-platform dispatcher" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


def test_rejects_dispatcher_missing_from_disk(tmp_path):
    """A dispatcher named correctly in hooks.json (recognized by its `.cmd` extension) but not
    actually present on disk must be rejected — the real invocation exits 127, not the posture
    this check exists to guarantee.

    Isolated: the target script exists on disk, so the only possible violation is the
    dispatcher's own absence.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "script").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(hooks_dir, f"{DISPATCHER_CMD} script")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "invokes a dispatcher that is not on disk" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


# --- Rule 1: extensionless target, one is required, and it must exist ---------------------


def test_rejects_extensioned_target_script(tmp_path):
    """Rule 1: a target script carrying a suffix (e.g. .sh) must be rejected.

    Isolated two ways: the dispatcher exists on disk (so it can't also fail the dispatcher
    existence check), and the extensioned target itself exists on disk too — proving the
    violation is the extension, not a missing file that would fail for an unrelated reason and
    happen to share the phrase "rule 1". The assertion is on "carries a", a fragment unique to
    this one violation message (unlike "rule 1", which more than one message contains).
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    (hooks_dir / "script.sh").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(hooks_dir, f"{DISPATCHER_CMD} script.sh")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "carries a" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


def test_rejects_dispatcher_with_no_script_argument(tmp_path):
    """A dispatcher invoked with no script argument at all is exactly as broken as one invoked
    with a bad one — its Unix half execs an empty path.

    Isolated: the dispatcher itself exists on disk, so the only possible violation is the
    missing argument.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    hooks_json_path = _write_hooks_json(hooks_dir, DISPATCHER_CMD)

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "invoked with no script argument" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


def test_rejects_target_missing_from_disk(tmp_path):
    """Rule 1 blind spot: a target named correctly (extensionless, no shell metacharacters) but
    not actually present on disk must be rejected — a renamed or deleted script with hooks.json
    left unchanged is invisible to every other check and runs silently until the real
    invocation fails.

    Isolated: the dispatcher exists on disk, so the only possible violation is the target's
    absence.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    hooks_json_path = _write_hooks_json(hooks_dir, f"{DISPATCHER_CMD} script")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "hooks.json names a target that is not on disk" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


# --- Tokenizer: unparseable input, comment-character truncation, chained commands ---------


def test_rejects_unparseable_command(tmp_path):
    """A command this check's tokenizer cannot parse (unbalanced quoting) must itself be a
    violation, not silently re-parsed by a more permissive fallback that could still certify
    it — a command a real shell would refuse to run is not a shape this check may certify.
    """
    hooks_dir = _hooks_dir(tmp_path)
    hooks_json_path = _write_hooks_json(
        hooks_dir, '"${CLAUDE_PLUGIN_ROOT}/hooks/dispatch.cmd script'
    )

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "could not be parsed" in result.stdout, result.stdout


def test_hash_does_not_truncate_command(tmp_path):
    """A bare '#' in a command must not be treated as a shell comment marker. `shlex`'s default
    `commenters` would otherwise drop everything from the '#' onward before any rule ever saw
    it — here, that would silently delete the target argument entirely, changing this from an
    extensioned-target violation into a missing-argument one (or, worse, no violation at all).
    Asserting on "carries a" (unique to the extension violation) catches either regression.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    hooks_json_path = _write_hooks_json(hooks_dir, f"{DISPATCHER_CMD} #script.sh")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "carries a" in result.stdout, result.stdout


def test_rejects_chained_second_command(tmp_path):
    """A command chained onto a valid entry with ';'/'&'/'|' is a second command, not
    decoration on the first, and must be held to the same rules as the first.

    Isolated: the primary invocation (dispatcher + extensionless target, both on disk) is
    fully valid, so the only violation possible is on the chained segment — proving the
    checker actually inspects tokens past the first two, not just that *some* violation fires.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    (hooks_dir / "script").write_text("#!/bin/bash\n")
    command = (
        f'{DISPATCHER_CMD} script ; bash "${{CLAUDE_PLUGIN_ROOT}}/hooks/session-start.sh"'
    )
    hooks_json_path = _write_hooks_json(hooks_dir, command)

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "chained command" in result.stdout, result.stdout
    assert "rule 2" in result.stdout, result.stdout


# --- Entry- and file-level shape: missing "type", malformed structure, empty file ---------


def test_rejects_missing_type_key(tmp_path):
    """A hook entry missing the "type" key entirely must be rejected — a command hook must
    declare its type."""
    hooks_dir = _hooks_dir(tmp_path)
    hooks_json_path = hooks_dir / "hooks.json"
    hooks_json_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {"hooks": [{"command": f"{DISPATCHER_CMD} script", "shell": "bash"}]}
                    ]
                }
            }
        )
    )

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert 'missing required "type" key' in result.stdout, result.stdout


@pytest.mark.parametrize("hooks_value", [[], "not-an-object", 5])
def test_rejects_malformed_hooks_value(tmp_path, hooks_value):
    """"hooks" must be an object keyed by event name; a list/string/number must fail loudly
    with a named reason, not an uncaught traceback."""
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(json.dumps({"hooks": hooks_value}))

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "malformed hooks.json structure" in result.stdout, result.stdout


def test_rejects_no_command_hooks_found(tmp_path):
    """A hooks.json with no type:command entry anywhere (an emptied "hooks" object) must fail —
    certifying a file that was never actually validated is the defect this whole check exists
    to remove."""
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(json.dumps({"hooks": {}}))

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "no command hooks found" in result.stdout, result.stdout


def test_rejects_non_object_top_level(tmp_path):
    """A hooks.json whose top level isn't an object at all (the wrong file entirely) must fail,
    named as exactly that rather than as a generic parse error."""
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(json.dumps([1, 2, 3]))

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "top level is not an object" in result.stdout, result.stdout


def test_rejects_unparseable_json(tmp_path):
    """A hooks.json that isn't valid JSON at all must fail with a clean, named message, not an
    uncaught traceback."""
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text("{not valid json")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "could not parse" in result.stdout, result.stdout
