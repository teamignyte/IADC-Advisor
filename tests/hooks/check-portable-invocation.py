#!/usr/bin/env python3
"""Discriminating control for the Windows hook-portability convention.

Family ADR 0011 (docs/adr/0011-scripts-replace-prose-once-a-check-clears-a-viability-test.md,
umbrella repo) and docs/agents/skill-scripts.md state three portability rules for a hook
command declared in a plugin's hooks.json:

  1. The invoked script is extensionless (no .sh/.py/... suffix on the path Claude Code sees).
  2. Invocation goes through a cross-platform dispatcher, never a bare interpreter prefix or a
     hardcoded interpreter path.
  3. "shell": "bash" is declared on the command entry.

Each rule clears the viability test in docs/agents/skill-scripts.md: deterministic, a fixed
pass/fail outcome, testable with a fixture and no model in the loop, every input (the JSON,
the filenames on disk) observable from this subprocess, and worth the cost because a violation
is a silent Windows-only failure mode nobody exercises by hand.

Rules 2 and 3 are checked structurally, not by scanning the command string for known
substrings: the dispatcher is identified positively as the command's first real token (after
skipping any leading `VAR=value` shell assignments) — that token must itself carry a
recognized dispatcher extension (`.cmd`). Nothing exempts a token from this by matching a
filename or directory substring, so a deleted dispatcher, a re-added interpreter prefix, and a
hardcoded interpreter path (`/bin/bash`, `env bash`, ...) all fail by construction rather than
by enumeration. Rule 1 is inverted the same way: any dotted suffix on the token immediately
following the dispatcher is a violation, not just a suffix drawn from a fixed allowlist — an
unlisted extension is not evidence of safety.

A hooks.json with no `type: command` entry anywhere (wrong file, emptied hooks, every entry
missing or non-command) is its own failure: a checker that certifies a file it never actually
validated would be a check that cannot fail, which is worse than no check at all.

Usage: check-portable-invocation.py <path-to-hooks.json>

Exit code is the machine-readable result: 0 if every command entry in every hook array
satisfies all three rules, 1 if any violation is found (including "no command hooks found" and
a malformed/unparseable file), 2 on a usage error (wrong argument count). Stdout is the
human-readable reason, one line per violation, naming the rule that failed.
"""
import json
import os
import re
import sys

# The dispatcher's own file extension — the structural marker that Windows hands a ".cmd" path
# to its own file-type association (cmd.exe), which is the entire reason the polyglot trick
# works. Identifying the dispatcher this way, rather than by name or substring, means a second
# plugin's differently-named dispatcher is recognized too, and a same-named non-dispatcher isn't.
DISPATCHER_EXTENSIONS = (".cmd",)

# A leading `NAME=value` shell assignment (e.g. `FOO=1 bash ...`) is not itself the invoked
# command — skip over it when looking for the token that must be the dispatcher.
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def tokenize(command):
    """Split a hooks.json command string into shell-like tokens.

    Handles single and double quotes, any run of whitespace (space or tab), and splits a
    trailing control character (`;`, `&`, `|`) into its own token instead of leaving it glued
    onto the preceding word — the same rule a real shell applies before it ever looks at
    quoting. `shlex` is used in preference to `str.split()` + ad hoc quote-stripping because the
    latter only ever stripped double quotes, leaving a single-quoted path invisible to every
    later check.
    """
    import shlex

    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        # Unbalanced quoting or similar — fall back to a plain split so the caller still gets
        # *some* tokens to reason about rather than crashing.
        return command.split()


def check_command_entry(hooks_json_path, event_name, group_index, entry_index, entry):
    """Return a list of violation strings for one hooks.json entry.

    An entry missing the "type" key entirely is itself a violation (a command hook must declare
    its type); an entry whose "type" is present but not "command" is out of scope for this
    convention and is silently skipped (e.g. a "prompt" hook).
    """
    where = f"{event_name}[{group_index}].hooks[{entry_index}]"
    violations = []

    if "type" not in entry:
        violations.append(f'{where}: missing required "type" key on a hook entry')
        return violations
    if entry.get("type") != "command":
        return violations  # only command-type entries carry this convention

    command = entry.get("command", "")

    # Rule 3: shell: bash must be declared on the entry.
    if entry.get("shell") != "bash":
        violations.append(
            f'{where}: missing "shell": "bash" (rule 3 — Windows falls through to '
            f"PowerShell/CMD, neither of which can parse this command)"
        )

    tokens = tokenize(command)

    # Find the first real token: skip leading `VAR=value` assignments, which are not the
    # invoked command.
    idx = 0
    while idx < len(tokens) and ASSIGNMENT_RE.match(tokens[idx]):
        idx += 1
    command_token = tokens[idx] if idx < len(tokens) else ""
    command_ext = os.path.splitext(os.path.basename(command_token))[1].lower()
    is_dispatcher = command_ext in DISPATCHER_EXTENSIONS

    # Rule 2: the command's first real token must itself be a dispatcher. This is a positive
    # requirement, not a substring scan — a deleted dispatcher, a bare `bash`/`sh`/`python3`
    # prefix (with or without a leading `env` or `VAR=value`), and a hardcoded interpreter path
    # like `/bin/bash` all fail here because none of them end in a dispatcher extension, not
    # because any one of them is individually enumerated.
    if not is_dispatcher:
        violations.append(
            f"{where}: command is not invoked through a cross-platform dispatcher — first "
            f"token {command_token!r} is a bare interpreter or hardcoded interpreter path, "
            f"not a dispatcher (rule 2): {command!r}"
        )

    # Rule 1: the token immediately after the command's first real token — the script name the
    # dispatcher (or, if rule 2 already failed, the bare interpreter) is handed — must be
    # extensionless. Any dotted suffix is a violation; there is no allowlist of "known" script
    # extensions to fall outside of.
    target_index = idx + 1
    if target_index < len(tokens):
        target = tokens[target_index]
        target_base = os.path.basename(target)
        _, target_ext = os.path.splitext(target_base)
        if target_ext:
            violations.append(
                f"{where}: invoked script {target_base!r} carries a {target_ext!r} suffix "
                f"(rule 1 — Claude Code's Windows launcher auto-prepends bash to any .sh path, "
                f"and an extension outside any fixed list is not a safe assumption otherwise): "
                f"{command!r}"
            )
        elif is_dispatcher and not any(c in target for c in "$*?"):
            # The target names a plain file, not a shell variable or glob — this is exactly
            # the shape a dispatcher argument takes in this repo's convention (a bare filename
            # resolved relative to hooks.json's own directory, the same directory the
            # dispatcher resolves it from at runtime). Verify it actually exists: a renamed
            # on-disk file with hooks.json left unchanged is invisible to every check above and
            # is the exact blind spot this assertion exists to close.
            script_dir = os.path.dirname(os.path.abspath(hooks_json_path))
            candidate = os.path.join(script_dir, target)
            if not os.path.isfile(candidate):
                violations.append(
                    f"{where}: invoked script {target!r} does not exist at {candidate} — "
                    f"hooks.json names a target that is not on disk (rule 1 blind spot: a "
                    f"renamed or deleted file with hooks.json left unchanged runs silently "
                    f"until it fails at the real invocation)"
                )

    return violations


def main(argv):
    if len(argv) != 2:
        print("usage: check-portable-invocation.py <path-to-hooks.json>", file=sys.stderr)
        return 2

    hooks_json_path = argv[1]
    try:
        with open(hooks_json_path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: could not parse {hooks_json_path}: {e}")
        return 1

    if not isinstance(data, dict):
        print(f"FAIL: no command hooks found in {hooks_json_path} (top level is not an object)")
        return 1

    all_violations = []
    command_entry_count = 0
    hooks = data.get("hooks", {})

    try:
        if not isinstance(hooks, dict):
            raise TypeError(f'"hooks" is {type(hooks).__name__}, not an object')
        for event_name, groups in hooks.items():
            if not isinstance(groups, list):
                raise TypeError(f'"{event_name}" is {type(groups).__name__}, not an array')
            for group_index, group in enumerate(groups):
                if not isinstance(group, dict):
                    raise TypeError(
                        f"{event_name}[{group_index}] is {type(group).__name__}, not an object"
                    )
                group_hooks = group.get("hooks", [])
                if not isinstance(group_hooks, list):
                    raise TypeError(
                        f"{event_name}[{group_index}].hooks is "
                        f"{type(group_hooks).__name__}, not an array"
                    )
                for entry_index, entry in enumerate(group_hooks):
                    if not isinstance(entry, dict):
                        raise TypeError(
                            f"{event_name}[{group_index}].hooks[{entry_index}] is "
                            f"{type(entry).__name__}, not an object"
                        )
                    if entry.get("type") == "command":
                        command_entry_count += 1
                    all_violations.extend(
                        check_command_entry(
                            hooks_json_path, event_name, group_index, entry_index, entry
                        )
                    )
    except TypeError as e:
        print(f"FAIL: malformed hooks.json structure in {hooks_json_path}: {e}")
        return 1

    # A file with no command hooks at all — the wrong path entirely, an emptied "hooks" object,
    # or a "hooks" tree with no command-type entry anywhere — is not a pass. Certifying a file
    # that was never actually validated is the defect this whole check exists to remove. This is
    # folded into all_violations (not an early return) so it never hides a more specific
    # per-entry violation (e.g. a missing "type" key) that was already found on the same file.
    if command_entry_count == 0:
        all_violations.append(f"no command hooks found in {hooks_json_path}")

    if all_violations:
        for v in all_violations:
            print(f"FAIL: {v}")
        print(f"{len(all_violations)} violation(s) in {hooks_json_path}")
        return 1

    print(f"PASS: {hooks_json_path} — all command hooks satisfy the portability rules")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
