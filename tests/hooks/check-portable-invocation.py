#!/usr/bin/env python3
"""Discriminating control for the Windows hook-portability convention.

Family ADR 0011 (docs/adr/0011-scripts-replace-prose-once-a-check-clears-a-viability-test.md,
umbrella repo) and docs/agents/skill-scripts.md state three portability rules for a hook
command declared in a plugin's hooks.json:

  1. The invoked script is extensionless (no .sh/.py/... suffix on the path Claude Code sees),
     and there is one: a dispatcher invoked with no script argument is as broken as one invoked
     with a bad one.
  2. Invocation goes through a cross-platform dispatcher, never a bare interpreter prefix or a
     hardcoded interpreter path — and the dispatcher named must actually be on disk, not merely
     named in a way that looks right.
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

Recognizing the dispatcher is extension-based only — this check never reads the dispatcher
file's contents, so it certifies "names a `.cmd` path", not "is provably a working polyglot
dispatcher". What it does verify on disk: the dispatcher file exists, a script argument is
present, and that script exists too — each resolved against the directory it actually
resolves from at runtime (`${CLAUDE_PLUGIN_ROOT}` substituted from hooks.json's own location,
then the script argument resolved against the *dispatcher's* directory, matching
`run-hook.cmd`'s own `SCRIPT_DIR="$(dirname "$0")"`), not against hooks.json's directory —
those two directories only coincide because this repo's convention keeps them together.

A command chained with `;`, `&`, or `|` is not one command but several; every segment is held
to rules 1 and 2 independently; rule 3 ("shell": "bash") is an entry-level property and is
still checked once.

A command this check's tokenizer cannot parse (e.g. unbalanced quoting) is itself a violation
— it is not re-parsed by a more permissive fallback, because a command a real shell would
refuse to run is not a shape this check may certify.

A hooks.json with no `type: command` entry anywhere (wrong file, emptied hooks, every entry
missing or non-command) is its own failure: a checker that certifies a file it never actually
validated would be a check that cannot fail, which is worse than no check at all.

The same failure mode exists one level down, inside a single entry: a `command` that tokenizes
to nothing invokable — empty, whitespace-only, only a control operator, or only a shell variable
assignment with nothing after it — still counts toward `command_entry_count`, so it must be
named as a violation rather than certified as satisfying rules it was never actually held to.

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
# plugin's differently-named dispatcher is recognized too. This is purely extension-based: the
# check never reads the file, so a `.cmd`-named file that is not actually a polyglot dispatcher
# satisfies it just the same — recognition here means "looks like a dispatcher path", not "is
# provably one"; the on-disk checks below narrow that to "and something is actually there".
DISPATCHER_EXTENSIONS = (".cmd",)

# A leading `NAME=value` shell assignment (e.g. `FOO=1 bash ...`) is not itself the invoked
# command — skip over it when looking for the token that must be the dispatcher.
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# Shell control operators that separate one command from the next. shlex's punctuation_chars
# splits each into its own single-character token; anything on the far side of one is a second
# (or third, ...) invocation and gets the same scrutiny as the first.
CONTROL_OPERATORS = (";", "&", "|")


def tokenize(command):
    """Split a hooks.json command string into shell-like tokens.

    Handles single and double quotes, any run of whitespace (space or tab), and splits a
    control character (`;`, `&`, `|`) into its own token instead of leaving it glued onto the
    preceding word. `shlex` is used in preference to `str.split()` + ad hoc quote-stripping
    because the latter only ever stripped double quotes, leaving a single-quoted path invisible
    to every later check.

    A `#` is not a comment marker here — a hooks.json command string has no shell script
    semantics where `#` starts a comment, and treating it as one would let text after a `#`
    vanish before any rule ever sees it.

    Raises ValueError when `command` is a string shlex cannot tokenize (e.g. unbalanced
    quoting) — the caller treats that as a violation, not a shape to fall back and re-parse
    more permissively. A `command` that is not a string at all (a JSON `null`, for example) is
    a different case this function does not guard against: `shlex.shlex` treats a non-string
    argument as a stream to read from and blocks on stdin instead of raising, and the caller
    does not catch that either. That gap predates this docstring; the claim here is narrowed to
    what `tokenize` actually raises for a string `command`.
    """
    import shlex

    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def split_segments(tokens):
    """Split a token stream at `;`/`&`/`|` control-operator tokens into separate commands.

    A run of punctuation characters (`shlex`'s own grouping, when `punctuation_chars` is set)
    comes back as *one* token — `&&` is the single token `'&&'`, not two `'&'` tokens — so the
    boundary test is "every character in the token is a control operator", not an exact match
    against `;`/`&`/`|` individually; an exact match silently misses `&&`/`||`/`;;`.

    Each resulting segment is itself checked as a full invocation (rules 1 and 2) — a command
    appended after a control operator is a second command, not decoration on the first, and
    must be held to the same rules. Empty segments (a trailing separator, or two separators in
    a row) are dropped: there is nothing to check in an empty segment. If dropping empty
    segments leaves none at all — the whole command was empty, whitespace-only, or made only of
    control operators — the caller treats that as its own violation instead of certifying an
    entry no segment was ever checked against.
    """
    segments = []
    current = []
    for token in tokens:
        if token and all(c in CONTROL_OPERATORS for c in token):
            segments.append(current)
            current = []
        else:
            current.append(token)
    segments.append(current)
    return [segment for segment in segments if segment]


def plugin_root(hooks_json_path):
    """The directory `${CLAUDE_PLUGIN_ROOT}` expands to at runtime.

    Claude Code's own plugin layout convention is `<plugin-root>/hooks/hooks.json`, so the
    plugin root is one directory above hooks.json's own directory — computed from hooks.json's
    location, not assumed to be this repo's layout.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(hooks_json_path)))


def resolve_plugin_path(token, hooks_json_path):
    """Resolve a command token to an absolute filesystem path, or None if it can't be resolved
    without a shell (it still names a variable other than `${CLAUDE_PLUGIN_ROOT}`, or a glob).
    """
    resolved = token.replace("${CLAUDE_PLUGIN_ROOT}", plugin_root(hooks_json_path))
    if any(c in resolved for c in "$*?"):
        return None
    if not os.path.isabs(resolved):
        resolved = os.path.join(plugin_root(hooks_json_path), resolved)
    return os.path.normpath(resolved)


def check_invocation(tokens, hooks_json_path, where, command):
    """Return violation strings for one command segment (rules 1 and 2 only — rule 3 is an
    entry-level property, checked once by the caller).
    """
    violations = []

    idx = 0
    while idx < len(tokens) and ASSIGNMENT_RE.match(tokens[idx]):
        idx += 1
    if idx >= len(tokens):
        # Nothing left after stripping leading assignments — a bare "FOO=1" segment sets an
        # environment variable and invokes nothing at all. That is not a pass: no dispatcher
        # was named, so this is rule 2 violated by omission, not a shape with nothing to check.
        violations.append(
            f"{where}: command is not invoked through a cross-platform dispatcher — there is "
            f"nothing left to invoke once any leading assignment(s) are stripped (rule 2): "
            f"{command!r}"
        )
        return violations

    command_token = tokens[idx]
    command_ext = os.path.splitext(os.path.basename(command_token))[1].lower()
    is_dispatcher = command_ext in DISPATCHER_EXTENSIONS

    # Rule 2: the segment's first real token must itself be a dispatcher, and that dispatcher
    # must actually exist on disk. Both are positive requirements, not a substring scan or a
    # command-string-only check — a deleted dispatcher, a bare `bash`/`sh`/`python3` prefix
    # (with or without a leading `env` or `VAR=value`), a hardcoded interpreter path like
    # `/bin/bash`, and a dispatcher that is named correctly but not actually present all fail
    # here, none of them individually enumerated.
    if not is_dispatcher:
        violations.append(
            f"{where}: command is not invoked through a cross-platform dispatcher — first "
            f"token {command_token!r} is a bare interpreter or hardcoded interpreter path, "
            f"not a dispatcher (rule 2): {command!r}"
        )
    else:
        dispatcher_path = resolve_plugin_path(command_token, hooks_json_path)
        if dispatcher_path is not None and not os.path.isfile(dispatcher_path):
            violations.append(
                f"{where}: dispatcher {command_token!r} does not exist at {dispatcher_path} — "
                f"hooks.json invokes a dispatcher that is not on disk (rule 2: a deleted or "
                f"renamed dispatcher with hooks.json left unchanged runs silently until it "
                f"fails at the real invocation, exit 127): {command!r}"
            )

    # Rule 1: the token immediately after the segment's first real token — the script name the
    # dispatcher (or, if rule 2 already failed, the bare interpreter) is handed — must exist and
    # be extensionless. There is no allowlist of "known" script extensions to fall outside of,
    # and a dispatcher with no script argument at all is exactly as broken as one with a bad one
    # (its Unix half execs an empty path).
    target_index = idx + 1
    if target_index >= len(tokens):
        if is_dispatcher:
            violations.append(
                f"{where}: dispatcher {command_token!r} is invoked with no script argument — "
                f"its Unix half execs an empty path and fails at runtime (rule 1: a dispatcher "
                f"must be handed a target script to run): {command!r}"
            )
        return violations

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
        # The target names a plain file, not a shell variable or glob — this is exactly the
        # shape a dispatcher argument takes in this repo's convention. Verify it actually
        # exists, resolved against the *dispatcher's* own directory (matching run-hook.cmd's
        # own `SCRIPT_DIR="$(dirname "$0")"` at runtime) rather than hooks.json's directory —
        # those coincide here only because this repo keeps hooks.json and its scripts together.
        # A renamed on-disk file with hooks.json left unchanged is invisible to every check
        # above and is the exact blind spot this assertion exists to close.
        dispatcher_path = resolve_plugin_path(command_token, hooks_json_path)
        if dispatcher_path is not None:
            script_dir = os.path.dirname(dispatcher_path)
            candidate = os.path.join(script_dir, target)
            if not os.path.isfile(candidate):
                violations.append(
                    f"{where}: invoked script {target!r} does not exist at {candidate} — "
                    f"hooks.json names a target that is not on disk (rule 1 blind spot: a "
                    f"renamed or deleted file with hooks.json left unchanged runs silently "
                    f"until it fails at the real invocation): {command!r}"
                )

    return violations


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

    # Rule 3: shell: bash must be declared on the entry. Entry-level, checked once — unlike
    # rules 1 and 2 it is not a per-segment property.
    if entry.get("shell") != "bash":
        violations.append(
            f'{where}: missing "shell": "bash" (rule 3 — Windows falls through to '
            f"PowerShell/CMD, neither of which can parse this command)"
        )

    try:
        tokens = tokenize(command)
    except ValueError as e:
        violations.append(
            f"{where}: command could not be parsed as a shell command ({e}) — an unparseable "
            f"or ambiguously-quoted command is not a shape this check may certify: {command!r}"
        )
        return violations

    segments = split_segments(tokens)
    if not segments:
        # An empty command, one that is only whitespace, or one that is only a stray control
        # operator all tokenize to no segments at all. The loop below would never run, and this
        # entry — already counted in command_entry_count — would be certified without a single
        # rule ever evaluating it.
        violations.append(
            f"{where}: command is not invoked through a cross-platform dispatcher — the "
            f"command is empty or carries nothing to invoke (rule 2): {command!r}"
        )
        return violations

    for segment_index, segment in enumerate(segments):
        segment_where = (
            where if segment_index == 0 else f"{where} (chained command {segment_index + 1})"
        )
        violations.extend(check_invocation(segment, hooks_json_path, segment_where, command))

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
