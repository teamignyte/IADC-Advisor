# The polyglot hook dispatcher — how to adopt it in another repo

Dev doc, never shipped (only `iadc-advisor/` ships — see this repo's `CLAUDE.md`). This is the
mechanism family [ADR 0011](https://github.com/teamignyte/IADC/blob/main/docs/adr/0011-scripts-replace-prose-once-a-check-clears-a-viability-test.md)
and this repo's own [ADR 0012](adr/0012-hook-invocation-goes-through-a-polyglot-dispatcher.md)
point at. Read it before wiring a hook in a second plugin (`iadc-tester`, or any future one) —
the goal is that you copy the file and this explanation, not re-derive the trick.

> **Authoritative source: `iadc-advisor/hooks/run-hook.cmd` itself.** This doc explains it; if
> the two ever disagree, the file is right and this doc is stale — the same rule the reference
> implementation states for its own copy of this doc.

## The problem this solves

Claude Code runs a hook's `command` through a shell: bash/sh on macOS and Linux, Git Bash on
Windows when it's installed, PowerShell otherwise. A command string built for bash — a leading
quoted path, `$VAR` expansion — is not valid PowerShell or CMD, so a plugin whose hook command
is `bash "${CLAUDE_PLUGIN_ROOT}/hooks/foo.sh"` with no further declaration breaks on a Windows
client with no Git Bash, and breaks differently (auto-prepended `bash`, since the path contains
`.sh`) even when Git Bash *is* present.

Three things fix it together — one alone doesn't:

1. **Declare `"shell": "bash"` on the command entry.** This forces Claude Code to route the
   command through Git Bash on Windows rather than falling through to PowerShell, and — when
   Git Bash isn't installed at all — surfaces an actionable "install Git for Windows" error at
   the Claude Code layer instead of a shell-parser failure inside your own command string.
2. **Make the invoked script extensionless.** Claude Code's Windows launcher auto-prepends
   `bash` to any command whose path contains `.sh`. A command that already starts with `bash`
   (or, as here, ends up inside a dispatcher file bash itself will run) collides with that
   auto-prepend. Naming the real script `session-start` instead of `session-start.sh` removes
   the trigger.
3. **Invoke through a dispatcher file, not a bare interpreter prefix.** This is `run-hook.cmd`,
   described below.

**`"shell": "bash"` has a version floor.** The reference implementation documents this key as
supported since Claude Code **2.1.81**; an older CLI silently ignores it rather than erroring, so
the Windows fix degrades to extensionless-filename-plus-dispatcher only — no Git-Bash routing —
on a client running an older CLI. No floor is currently declared or enforced anywhere in this
repo (`plugin.json` states none), so treat the Git-Bash routing above as conditional on a modern
CLI, not unconditional, until this repo has a place to declare a minimum Claude Code version.

## `run-hook.cmd`: one file, two readers

`run-hook.cmd` is a **polyglot**: the same bytes are a valid bash script and a valid Windows
batch file, and each interpreter reads only the half meant for it.

```
: << 'CMDBLOCK'
@echo off
... batch commands ...
CMDBLOCK

# Unix body
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_NAME="$1"
shift
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
```

- **On Unix**, `bash` reads the whole file top to bottom. `: << 'CMDBLOCK'` is bash's no-op
  builtin (`:`) fed a heredoc; bash consumes everything up to the `CMDBLOCK` terminator as the
  heredoc's operand and discards it, so the entire `@echo off` section is invisible to it. Bash
  then executes the four lines after the marker: resolve the dispatcher's own directory, take
  the first argument as the script name, `shift` it off, and `exec` the named script from that
  directory with any remaining arguments.
- **On Windows**, `hooks.json` declares `"shell": "bash"`, so Claude Code launches Git Bash to
  run the command line. Git Bash executing a path ending in `.cmd` hands it to Windows' own
  file-type association rather than interpreting it itself — that association runs it through
  `cmd.exe`. The `cmd.exe` process that results is a **sibling** of the Git Bash that spawned it,
  not a child shell inside it, so it cannot assume bash is already on its own `PATH`. That's why
  the batch section re-locates bash rather than trusting inheritance:
  1. Try the two standard Git for Windows install paths (`C:\Program Files\Git\bin\bash.exe`,
     the `(x86)` variant).
  2. Fall back to `where bash` (a user-installed Git Bash, MSYS2, or Cygwin on `PATH`).
  3. If neither is found, exit `0` silently rather than error — this double-failure (Claude
     Code already routed us through `"shell": "bash"`, yet no bash is reachable from the spawned
     `cmd.exe`) means only that this one plugin loses its context-injection hook for the
     session; it should not block the plugin from working otherwise.

## Hook scripts stay extensionless and pure

The real hook logic (`session-start`, no extension) is a plain bash script invoked by
`run-hook.cmd`'s `exec` line. Nothing about *it* needs to be polyglot — only the dispatcher does,
because only the dispatcher's own filename is what Claude Code's command string names directly.

## Adopting this in a second plugin

1. Copy `iadc-advisor/hooks/run-hook.cmd` **and** `iadc-advisor/hooks/LICENSE` verbatim into the
   new plugin's `hooks/` directory. The `.cmd` file has no `iadc-advisor`-specific content; the
   `LICENSE` carries the MIT attribution for it (adapted from the `superpowers` plugin's
   reference dispatcher, Copyright (c) 2025 Jesse Vincent) and must travel with it into whatever
   ships to a client — see "License" below.

   **Two silent, zero-stdout preconditions on `run-hook.cmd` itself**, verified directly (not
   carried): it is the file Claude Code's shell names and execs on the command line, so unlike
   the hook script it invokes, its own **executable bit** and **line endings** matter. Mode `644`
   (not executable): `bash: .../run-hook.cmd: Permission denied`, exit **126**. CRLF line
   endings: exit **127**. The heredoc terminator match on `CMDBLOCK` is *not* what breaks (`bash
   -n` parses a CRLF copy cleanly, and `bash -x` shows the parser finding the marker and moving
   into the Unix body regardless) — the actual damage is per-line: a blank line becomes a lone
   `\r` token that bash tries to run as a command (`line N: $'\r': command not found`), and a
   trailing `\r` glues onto the last word of the lines around it, turning `shift` into the
   unrecognized command `shift\r` and, since that failed command is never trapped, leaving the
   original argument un-shifted and passed a second time into a corrupted, `\r`-suffixed exec
   path. `git mv`/`cp` preserve the executable bit; a `*.cmd text eol=lf` line in the new repo's
   own `.gitattributes` protects `run-hook.cmd` at any depth and survives a `git subtree`-style
   copy. The hook script itself needs a second, separate line, because it's extensionless and so
   can't be matched by a glob: `<name> text eol=lf` — but a gitattributes pattern containing a
   slash is anchored to the `.gitattributes` file's own directory, not matched at any depth, so
   if the new plugin's `hooks/` sits below the repo root (as this repo's does), the pattern needs
   the **full path from the adopting repo's root** to the hook file, e.g. this repo's own
   `iadc-advisor/hooks/session-start text eol=lf` — not the shorter `hooks/session-start`, which
   matches nothing when the plugin isn't at the repo root.
2. Name your hook script extensionless (`hooks/<name>`, not `hooks/<name>.sh`). Its own execute
   bit does not matter — `run-hook.cmd`'s Unix half invokes it as `bash "<path>"`, an explicit
   interpreter call that only needs read permission — but CRLF still breaks it, differently: a
   `set -eu` (or any option-parsing line) ending in `\r` is `set -eu$'\r'`, an invalid option,
   verified to exit **2** with the shell's own usage message on stderr, not a silent failure.
3. Point `hooks.json`'s command at the dispatcher, passing the script name as an argument, and
   declare `"shell": "bash"`:

   ```json
   {
     "type": "command",
     "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" <name>",
     "shell": "bash"
   }
   ```

   Write both paths as literals, as above: `${CLAUDE_PLUGIN_ROOT}` is the only variable the
   portability check substitutes, and it expands no wildcards. A path carrying any other variable
   or a `*`/`?` glob names no one file the check can look for, so it is reported as a violation
   rather than passed — the check refuses to certify a path it cannot resolve, on the grounds that
   "could not look" and "looked and found it" must not share an exit code.

   Keep the script argument a **bare name relative to the dispatcher's own directory**, as in the
   example above, rather than a `${CLAUDE_PLUGIN_ROOT}`-rooted path of its own. The dispatcher
   joins whatever it is handed onto that directory unconditionally, so an absolute argument
   becomes `<hooks-dir>//absolute/path` and the hook exits **127** — verified by running the real
   dispatcher both ways. The portability check reports an absolute script argument as a rule 1
   violation for that reason. The dispatcher path is the opposite case: it is what the shell execs
   directly, so `${CLAUDE_PLUGIN_ROOT}`-rooted is exactly right there.

   The Unix and Windows halves are **not equivalent** in one respect: the Unix `exec bash ...
   "$@"` line forwards an unlimited number of arguments with quoting preserved, while the batch
   half hardcodes `%2 %3 %4 %5 %6 %7 %8 %9` — a cap of 8 forwarded arguments, silently truncated
   beyond that, with no re-quoting. Fine for a hook invoked with a handful of static args; do not
   assume it scales past that on Windows.
4. Decide the `matcher` on its own merits for that hook — see this repo's
   [ADR 0012](adr/0012-hook-invocation-goes-through-a-polyglot-dispatcher.md) for the reasoning
   this plugin applied (`startup|clear|compact`, excluding `resume`/`fork` to avoid duplicate
   context injection); a hook with different content or purpose may reasonably choose
   differently.
5. Copy `tests/hooks/check-portable-invocation.py` (copy, don't share the file across repos — the
   family placement rule is one authored copy per repo whose test suite guards it) and point it
   at the new plugin's `hooks.json`. It already takes that path as its one argument and needs no
   adaptation beyond that — confirm it fails on the pre-fix invocation string before trusting it
   to guard the fixed one.

## License

`run-hook.cmd` is adapted from the `superpowers` plugin's reference dispatcher, byte-identical on
every executable line, and MIT-licensed (Copyright (c) 2025 Jesse Vincent). `iadc-advisor/hooks/`
carries the attribution two ways: a `LICENSE` file alongside `run-hook.cmd`, and a header comment
in the file itself pointing at it — both ship to a client (only `iadc-advisor/` ships; see this
repo's `CLAUDE.md`), which is the point, since `docs/` does not. Carry both when adopting this
into a second plugin, the same way `iadc-advisor/skills/appian/LICENSE` is carried for that
vendored skill.

## What is and isn't verified from this repo

This repo has no Windows host and no `claude` binary that can run a real session. Everything
about the Unix code path above — the heredoc skip, `run-hook.cmd`'s `exec`, the resulting
stdout — was run and observed on this machine. The Windows code path (the `.cmd`-via-Git-Bash
association, the three-location bash search, PowerShell's shell-string failure on the old
command, the "install Git for Windows" error `"shell": "bash"` produces) is **carried from the
reference implementation's documentation and its own comments**, not independently observed
here — state this distinction the same way if you adopt this file, rather than asserting a
Windows behavior no one on the family has actually run.
