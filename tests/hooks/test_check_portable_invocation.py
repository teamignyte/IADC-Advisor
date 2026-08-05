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
the script would reject an invalid one. Almost every test after it builds a minimal hooks.json
(and, for most, a `hooks/` directory alongside it — the checker resolves a dispatcher and its
script argument against real files on disk, not just the command string) that violates exactly one
of the script's own predicates, and asserts both that the script exits 1 and that its stdout
carries a message fragment unique to that predicate — so a checker that stopped enforcing one rule
(returns success unconditionally, or falls through to a different check that happens to share the
same generic wording) is caught, not just a checker that stopped running entirely.

The exceptions are the handful of tests named `test_accepts_*`, which assert the opposite bound:
that a shape the checker is *not* meant to refuse still passes. A rule tightened until it rejects
everything passes every rejection fixture in this file, so the rejection fixtures alone cannot tell
a discriminating check from an indiscriminate one.

**Isolation matters more than exit code.** A fixture that merely deletes the file its own target
names, without also creating the dispatcher, can still fail for the *wrong* reason (a missing
dispatcher, not the rule under test) and still pass its assertions if the two violation messages
happen to share a substring — a discriminating fixture proves nothing if it never isolates the one
predicate it claims to guard. Every fixture below that exercises an on-disk check creates every
*other* file the checker might otherwise stumble on, so exactly one violation fires, asserted by
`FAIL:`-line count where that matters. Every test/rule pairing here was verified directly: disable
the predicate in a scratch copy of the script, confirm the corresponding test then fails, restore
the script, confirm the suite passes again.

Every way this script can refuse a hooks.json has an isolated fixture below. Refusal is the
property to check that claim against — an input the script answers with anything other than its
one `PASS:` line and exit 0 — and not any particular spelling of it: refusals reach stdout by four
different routes (a violation collected into the list, a structural `TypeError` the top-level
handler prints, a direct `print` + `return 1` in `main`, and the usage `return 2`), so a walk that
enumerates spellings silently omits whichever route it did not think to name. Walk the script for
the property rather than trusting this sentence, which is exactly the kind of hand-kept enumeration
that goes stale. The one deliberate exception is `test_rejects_malformed_hooks_value`'s three
parameters: they exercise a single branch (`"hooks"` not a dict) with three differently-typed
payloads to prove the check is type-generic, not three distinct predicates.
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
        # The checker reads one file and touches no network, so it has no reason to take
        # seconds. A bound turns any future input that makes it wait on something — stdin, most
        # plausibly, which is where a tokenizer handed a non-string would go looking — into a
        # failed test rather than a suite that never finishes and reports nothing at all.
        timeout=60,
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


def test_accepts_a_dollar_sign_path_that_resolves(tmp_path):
    """A `$` in a path is not itself the defect — `${CLAUDE_PLUGIN_ROOT}` is how this repo's own
    convention writes every hook path, and it substitutes to a real directory. This is the upper
    bound on the unresolvable-path rejections below: they must fire on a token that still names a
    variable *after* substitution, never on the presence of a metacharacter.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    (hooks_dir / "script").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(
        hooks_dir, f'{DISPATCHER_CMD} "${{CLAUDE_PLUGIN_ROOT}}/hooks/script"'
    )

    result = _run_check(hooks_json_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS:" in result.stdout, result.stdout


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


@pytest.mark.parametrize(
    "command",
    ["", "   ", ";", "&"],
    ids=["empty", "whitespace-only", "semicolon-only", "ampersand-only"],
)
def test_rejects_command_with_no_invokable_segment(tmp_path, command):
    """A command that tokenizes to no segment at all — empty, whitespace-only, or made only of
    a control operator — invokes nothing. The loop over segments would never run for any of
    these, so the entry (already counted toward "no command hooks found") would be certified
    without a single rule ever evaluating it — the same failure mode the module docstring
    describes for a whole file, one level down, inside a single entry.

    Isolated: no dispatcher or target file is created, and none is needed — the violation fires
    before any on-disk check runs.
    """
    hooks_dir = _hooks_dir(tmp_path)
    hooks_json_path = _write_hooks_json(hooks_dir, command)

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "nothing to invoke" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


def test_rejects_missing_command_key(tmp_path):
    """An entry with no "command" key at all must be rejected the same way an empty one is.
    `entry.get("command", "")` makes a missing key indistinguishable from an empty string by
    construction, so this proves the fix covers the key's absence, not just its presence with an
    empty value.
    """
    hooks_dir = _hooks_dir(tmp_path)
    hooks_json_path = hooks_dir / "hooks.json"
    hooks_json_path.write_text(
        json.dumps(
            {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "shell": "bash"}]}]}}
        )
    )

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "nothing to invoke" in result.stdout, result.stdout


def test_rejects_command_that_is_only_an_assignment(tmp_path):
    """A command consisting solely of a shell variable assignment ("IADC=1") sets an
    environment variable and invokes nothing — a different code path from an empty command:
    `tokenize()` returns one real token, so `split_segments()` does not see an empty segment
    list. `check_invocation()` itself must recognize that stripping the leading assignment
    leaves nothing to check and treat that as a violation, not silently return none.
    """
    hooks_dir = _hooks_dir(tmp_path)
    hooks_json_path = _write_hooks_json(hooks_dir, "IADC=1")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "rule 2" in result.stdout, result.stdout
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


@pytest.mark.parametrize(
    "dispatcher_token",
    ['"$UNRESOLVED/dispatch.cmd"', '"*.cmd"', '"dispatch?.cmd"'],
    ids=["unresolved-variable", "star-glob", "question-glob"],
)
def test_rejects_unresolvable_dispatcher_path(tmp_path, dispatcher_token):
    """A dispatcher token that still names a shell variable or a glob after
    `${CLAUDE_PLUGIN_ROOT}` substitution points at no one file. The checker runs no shell and
    expands no wildcard, so it can neither confirm nor deny that the dispatcher is there — and
    "could not look" must not be reported as "looked and found it", which is what skipping the
    on-disk check quietly does.

    Isolated: a real `dispatch.cmd` and a real `script` both exist in `hooks/`, so a checker that
    resolved these tokens some other way would find files rather than a second violation. The one
    violation can only be the unresolvable dispatcher itself.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    (hooks_dir / "script").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(hooks_dir, f"{dispatcher_token} script")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "dispatcher" in result.stdout, result.stdout
    assert "cannot be resolved to a path on disk" in result.stdout, result.stdout
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


@pytest.mark.parametrize(
    "target_token",
    ['"$OTHER/script"', '"scr*"', '"scrip?"'],
    ids=["unresolved-variable", "star-glob", "question-glob"],
)
def test_rejects_unresolvable_target_path(tmp_path, target_token):
    """The same reasoning as the dispatcher case, one token to the right: a script argument that
    still names a variable or a glob after substitution cannot be looked for, so rule 1's on-disk
    check cannot run — and an entry it did not run on is not an entry it certified.

    Isolated: the dispatcher exists on disk and resolves cleanly, so the only violation possible
    is the target's own unresolvable token.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    (hooks_dir / "script").write_text("#!/bin/bash\n")
    hooks_json_path = _write_hooks_json(hooks_dir, f"{DISPATCHER_CMD} {target_token}")

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "invoked script" in result.stdout, result.stdout
    assert "cannot be resolved to a path on disk" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


# --- Tokenizer: unparseable input, comment-character truncation, chained commands ---------


@pytest.mark.parametrize(
    "command",
    [None, 123, 1.5, True, [], {}],
    ids=["null", "int", "float", "bool", "array", "object"],
)
def test_rejects_non_string_command(tmp_path, command):
    """A "command" that is not a string is not command text at all, so no rule can be applied to
    it, so it must be refused by name.

    Left to reach the tokenizer, each of these answers from somewhere other than the file under
    test: `shlex` reads a non-string as a *stream*, so JSON `null` sends it to this process's
    stdin (a hang against an open one, an empty command against a closed one) and every other
    type raises AttributeError from inside the lexer — an exit 1 with empty stdout and no named
    reason, which reads as a violation whose message went missing.
    """
    hooks_dir = _hooks_dir(tmp_path)
    (hooks_dir / "dispatch.cmd").write_text("echo dispatcher\n")
    hooks_json_path = _write_hooks_json(hooks_dir, command)

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "not a string" in result.stdout, result.stdout
    assert result.stdout.count("FAIL:") == 1, result.stdout


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


# --- The remaining structural TypeError sites, and the usage-error exit code --------------
#
# check_command_entry's fixtures above cover every FAIL: this script can name on a *value*
# it recognizes. These four cover the structural shapes one level up — an event, a group, a
# group's "hooks", or an entry that is present but is not the type the walk over hooks.json
# assumes — the same class of defect as `test_rejects_malformed_hooks_value` above, one level
# deeper into the tree each time. None of the four can be deleted without collapsing the walk
# into an uncaught AttributeError instead of a named FAIL:, which is why each gets its own
# isolated fixture rather than being left to the reader to infer from the script.


def test_rejects_event_value_not_a_list(tmp_path):
    """An event's value (e.g. "SessionStart") must be an array of hook groups; anything else
    must fail loudly with a named reason, not an uncaught traceback."""
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(json.dumps({"hooks": {"SessionStart": "not-an-array"}}))

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "malformed hooks.json structure" in result.stdout, result.stdout
    assert '"SessionStart" is str, not an array' in result.stdout, result.stdout


def test_rejects_group_not_an_object(tmp_path):
    """A hook group — one entry in an event's array — that isn't itself an object must fail
    loudly, not raise when the checker calls .get("hooks", []) on it.

    Isolated from the entry-level version below by index: this fixture's violation is at
    SessionStart[0], the entry-level one is at SessionStart[0].hooks[0].
    """
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(json.dumps({"hooks": {"SessionStart": ["not-an-object"]}}))

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "malformed hooks.json structure" in result.stdout, result.stdout
    assert "SessionStart[0] is str, not an object" in result.stdout, result.stdout


def test_rejects_group_hooks_not_a_list(tmp_path):
    """A group's "hooks" value that isn't an array must fail loudly, not raise when the checker
    tries to enumerate it."""
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(
        json.dumps({"hooks": {"SessionStart": [{"hooks": "not-an-array"}]}})
    )

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "malformed hooks.json structure" in result.stdout, result.stdout
    assert "SessionStart[0].hooks is str, not an array" in result.stdout, result.stdout


def test_rejects_entry_not_an_object(tmp_path):
    """A hook entry inside a group's "hooks" array that isn't itself an object must fail
    loudly, not raise when the checker calls .get("type") on it.

    Isolated from the group-level version above by index: this fixture's violation is at
    SessionStart[0].hooks[0], the group-level one is at SessionStart[0].
    """
    hooks_json_path = tmp_path / "hooks.json"
    hooks_json_path.write_text(
        json.dumps({"hooks": {"SessionStart": [{"hooks": ["not-an-object"]}]}})
    )

    result = _run_check(hooks_json_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "malformed hooks.json structure" in result.stdout, result.stdout
    assert "SessionStart[0].hooks[0] is str, not an object" in result.stdout, result.stdout


def test_rejects_wrong_argument_count():
    """Called with the wrong number of arguments, the script must exit 2 — a usage error,
    distinct from exit 1 (a violation was found) — so a caller checking specifically for a
    certified violation doesn't conflate the two."""
    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "usage:" in result.stderr, result.stderr
