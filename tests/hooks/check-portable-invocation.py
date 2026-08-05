#!/usr/bin/env python3
"""Discriminating control for the Windows hook-portability convention.

Family ADR 0011 (docs/adr/0011-scripts-replace-prose-once-a-check-clears-a-viability-test.md,
umbrella repo) and docs/agents/skill-scripts.md state three portability rules for a hook
command declared in a plugin's hooks.json:

  1. The invoked script is extensionless (no .sh/.py/... suffix on the path Claude Code sees).
  2. Invocation goes through a cross-platform dispatcher, never a bare interpreter prefix.
  3. "shell": "bash" is declared on the command entry.

Each rule clears the viability test in docs/agents/skill-scripts.md: deterministic, a fixed
pass/fail outcome, testable with a fixture and no model in the loop, every input (the JSON,
the filenames on disk) observable from this subprocess, and worth the cost because a violation
is a silent Windows-only failure mode nobody exercises by hand.

Usage: check-portable-invocation.py <path-to-hooks.json>

Exit code is the machine-readable result: 0 if every command entry in every hook array
satisfies all three rules, 1 otherwise. Stdout is the human-readable reason, one line per
violation, naming the rule that failed.
"""
import json
import os
import sys

DISPATCHER_MARKERS = (".cmd", "run-hook")
SCRIPT_EXTENSIONS = (".sh", ".bash", ".py", ".js", ".ps1")


def check_command_entry(hooks_json_path, event_name, group_index, entry_index, entry):
    """Return a list of violation strings for one {"type": "command", ...} entry."""
    violations = []
    if entry.get("type") != "command":
        return violations  # only command-type entries carry this convention

    where = f"{event_name}[{group_index}].hooks[{entry_index}]"
    command = entry.get("command", "")

    # Rule 3: shell: bash must be declared on the entry.
    if entry.get("shell") != "bash":
        violations.append(
            f'{where}: missing "shell": "bash" (rule 3 — Windows falls through to '
            f"PowerShell/CMD, neither of which can parse this command)"
        )

    # Rule 2: invocation must go through a dispatcher, not a bare interpreter prefix.
    # A bare prefix looks like `bash "<path>"` or `sh "<path>"` with no dispatcher in between.
    stripped = command.strip()
    is_bare_interpreter_prefix = stripped.startswith(("bash ", "sh "))
    goes_through_dispatcher = any(marker in command for marker in DISPATCHER_MARKERS)
    if is_bare_interpreter_prefix and not goes_through_dispatcher:
        violations.append(
            f"{where}: command is a bare interpreter prefix ({stripped.split()[0]!r}), "
            f"not a cross-platform dispatcher (rule 2): {command!r}"
        )

    # Rule 1: the script name the command ultimately names must be extensionless.
    # Take the last whitespace-separated token; a dispatcher path itself (run-hook.cmd)
    # is exempt, everything it is handed as an argument is not.
    tokens = stripped.split()
    target_tokens = [
        t.strip('"') for t in tokens if not any(m in t for m in DISPATCHER_MARKERS)
    ]
    for tok in target_tokens:
        base = os.path.basename(tok)
        _, ext = os.path.splitext(base)
        if ext.lower() in SCRIPT_EXTENSIONS:
            violations.append(
                f"{where}: invoked script {base!r} carries a {ext!r} extension (rule 1 — "
                f"Claude Code's Windows launcher auto-prepends bash to any .sh path): {command!r}"
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

    all_violations = []
    hooks = data.get("hooks", {})
    for event_name, groups in hooks.items():
        for group_index, group in enumerate(groups):
            for entry_index, entry in enumerate(group.get("hooks", [])):
                all_violations.extend(
                    check_command_entry(hooks_json_path, event_name, group_index, entry_index, entry)
                )

    if all_violations:
        for v in all_violations:
            print(f"FAIL: {v}")
        print(f"{len(all_violations)} violation(s) in {hooks_json_path}")
        return 1

    print(f"PASS: {hooks_json_path} — all command hooks satisfy the portability rules")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
