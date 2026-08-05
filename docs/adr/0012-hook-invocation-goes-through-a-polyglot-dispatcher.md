# The SessionStart hook is invoked through a polyglot dispatcher, not a bare `bash` prefix

`iadc-advisor/hooks/hooks.json` used to run the plugin's only shipped executable as
`bash "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"`, declaring no `shell` key. Both are
documented Windows failure modes, and this hook is the plugin's replacement for a shipped
`CLAUDE.md` (ADR 0009) — plugins cannot load one — so a client whose command line fails here
silently gets **no operating posture at all**, invisible to them and to us.

Claude Code runs a hook's `command` through a shell: bash/sh on macOS and Linux, Git Bash on
Windows when it's installed, PowerShell otherwise. Neither Windows fallback can parse the old
command — PowerShell reads the leading quoted path as a string expression and errors on the
next bareword; CMD's quoting strips the outer quotes once the path contains a metacharacter.
Separately, Claude Code's Windows launcher auto-prepends `bash` to any command whose path
contains `.sh`, which collides with a dispatcher that already starts with `bash`.

## Decision

Adopt the pattern documented for Claude Code plugins generally (concretely: the `superpowers`
plugin's `hooks/run-hook.cmd` + `docs/windows/polyglot-hooks.md`, MIT-licensed, present in this
machine's plugin cache) rather than re-deriving it:

- **The shipped script is extensionless** (`hooks/session-start`, moved with `git mv` so history
  follows it) — an extension is exactly what triggers the Windows auto-prepend above.
- **Invocation goes through `hooks/run-hook.cmd`**, a single polyglot file: bash and cmd.exe each
  read only the half of it meant for them (see
  [`docs/hooks-dispatcher.md`](../hooks-dispatcher.md) for the mechanism, and read
  `iadc-advisor/hooks/run-hook.cmd` itself before changing it — trust the code over any doc,
  this one included, per the reference's own rule).
- **`hooks.json` declares `"shell": "bash"`** on the command entry, which forces the Git Bash
  route on Windows and turns a missing Git Bash into an actionable install error at the Claude
  Code layer, rather than a shell-parser failure inside our own command string.
- **`hooks.json` declares `"matcher": "startup|clear|compact"`**, where it previously declared
  none (firing on every `SessionStart` source: `startup`, `resume`, `clear`, `compact`, `fork`).
  This is a deliberate, separate behavior change bundled with the portability fix, not a
  side-effect of it — see below.

## The matcher: owed, not carried over unexamined

The hook exists to make the operating posture and project configuration ambient, standing in
for a `CLAUDE.md` the plugin cannot ship. On `resume` and `fork`, the resumed/forked session's
transcript already contains whatever this hook injected at the `startup` (or last `clear`/
`compact`) that preceded it — refiring adds a second copy of the same posture and config text to
context on every resume, and that cost compounds on a long-lived session resumed repeatedly. On
`clear` and `compact`, the prior context is gone or summarized away, so re-injection is exactly
what restores the posture; `startup` is the first injection. There is nothing about *this*
hook's payload that argues for diverging from the reference plugin's choice for the same
shape of problem (a large, mostly-static context injection), and the token-bloat argument is if
anything stronger here, since this hook's payload (posture + project config + personal overrides)
is larger than a single skill file.

The trade-off is real, not free: if `docs/agents/advisor.md` changes between a session's
`startup` and a later `resume` of it, the resumed session keeps the stale copy until the next
`clear`/`compact`/fresh `startup`. That is judged acceptable — config changes are rare relative
to resumes, and a user who just changed project configuration and wants it picked up immediately
can start a fresh session or run `/clear`.

## No change to what the hook injects

This ADR changes how the script is invoked, not what it says. `iadc-advisor/hooks/session-start`
is byte-identical to the pre-move `session-start.sh` (a pure `git mv`, no edits to the body).
Verified by running both the pre-fix invocation (`bash session-start.sh` at the prior commit)
and the post-fix one (`run-hook.cmd session-start`, current tree) against the same fixture
project directory: their stdout is byte-identical.

## Considered options

- **Keep the bare `bash "..."` prefix, add only `"shell": "bash"`.** Rejected: `"shell": "bash"`
  fixes the shell-selection problem but not the `.sh`-extension auto-prepend, which still
  collides with a command that already starts with `bash`.
- **Drop the matcher, keep firing on every `SessionStart` source.** Considered and rejected
  above — it is the higher-cost default (duplicate injection on every resume/fork), not a
  neutral one, and nothing in this hook's purpose argues for the plugin needing resume-time
  refresh badly enough to pay that cost on every resumed session.
- **Write a bespoke dispatcher instead of adopting the reference's polyglot trick.** Rejected:
  the trick (a shared file that is simultaneously a valid no-op-prefixed bash script and a valid
  cmd.exe batch file) is the hard-won, already-tested part; re-deriving it risks a subtly wrong
  variant no one has run on real Windows, which is precisely the failure mode this ticket exists
  to close.

## Consequences

- A second plugin (`iadc-tester`, or a future one) can copy `iadc-advisor/hooks/run-hook.cmd`
  and `docs/hooks-dispatcher.md`'s explanation into its own repo without re-deriving the
  polyglot mechanism — each repo authors its own copy per family
  [ADR 0011](https://github.com/teamignyte/IADC/blob/main/docs/adr/0011-scripts-replace-prose-once-a-check-clears-a-viability-test.md)'s
  placement rules (a script lives in the repo whose test suite guards it; there is no shared
  cross-plugin script path).
- `tests/hooks/check-portable-invocation.py` is a permanent regression guard: it reads
  `hooks.json` and fails the same way this defect would have failed it, naming which of the
  three portability rules broke. It is dev-only (root `tests/`, not `iadc-advisor/`), so it
  never ships to a client.
- Windows behavior itself — that Git Bash actually receives and correctly dispatches this file,
  that the `.cmd`-via-Git-Bash association behaves as documented — is **not** verified by
  running anything in this environment (no Windows host available); it is carried from the
  reference implementation's tested behavior and its documentation. Only the Unix code path and
  the static structure of `hooks.json` were actually run and observed here.
