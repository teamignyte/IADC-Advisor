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
  then executes the three lines after the marker: resolve the dispatcher's own directory, take
  the first argument as the script name, and `exec` the named script from that directory with
  any remaining arguments.
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

1. Copy `iadc-advisor/hooks/run-hook.cmd` verbatim into the new plugin's `hooks/` directory —
   it has no `iadc-advisor`-specific content.
2. Name your hook script extensionless (`hooks/<name>`, not `hooks/<name>.sh`).
3. Point `hooks.json`'s command at the dispatcher, passing the script name as an argument, and
   declare `"shell": "bash"`:

   ```json
   {
     "type": "command",
     "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" <name>",
     "shell": "bash"
   }
   ```
4. Decide the `matcher` on its own merits for that hook — see this repo's
   [ADR 0012](adr/0012-hook-invocation-goes-through-a-polyglot-dispatcher.md) for the reasoning
   this plugin applied (`startup|clear|compact`, excluding `resume`/`fork` to avoid duplicate
   context injection); a hook with different content or purpose may reasonably choose
   differently.
5. Adapt `tests/hooks/check-portable-invocation.py` (copy, don't share the file across repos —
   the family placement rule is one authored copy per repo whose test suite guards it) to run
   against the new plugin's `hooks.json`, and confirm it fails on the pre-fix invocation string
   before trusting it to guard the fixed one.

## What is and isn't verified from this repo

This repo has no Windows host and no `claude` binary that can run a real session. Everything
about the Unix code path above — the heredoc skip, `run-hook.cmd`'s `exec`, the resulting
stdout — was run and observed on this machine. The Windows code path (the `.cmd`-via-Git-Bash
association, the three-location bash search, PowerShell's shell-string failure on the old
command, the "install Git for Windows" error `"shell": "bash"` produces) is **carried from the
reference implementation's documentation and its own comments**, not independently observed
here — state this distinction the same way if you adopt this file, rather than asserting a
Windows behavior no one on the family has actually run.
