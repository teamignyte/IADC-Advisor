: << 'CMDBLOCK'
@echo off
REM Cross-platform dispatcher for a Claude Code plugin's hook scripts. Has no
REM iadc-advisor-specific content — safe to copy verbatim into another
REM plugin's hooks/ directory (see docs/hooks-dispatcher.md in this repo).
REM
REM Adapted from the superpowers plugin's reference dispatcher (MIT License,
REM Copyright (c) 2025 Jesse Vincent). See the LICENSE file alongside this one.
REM
REM This file is a polyglot: cmd.exe and bash each read only the half meant
REM for them and ignore the other.
REM
REM   - On Unix, Claude Code's shell (bash) reads this whole file as a bash
REM     script. The block you are reading now is the operand of a no-op
REM     heredoc fed to the ":" builtin at the top of this file (line 1), so
REM     bash skips straight past it to the real Unix body after the
REM     CMDBLOCK marker.
REM   - On Windows, "hooks.json" declares "shell": "bash" so Claude Code
REM     launches Git Bash to run the command line. Git Bash executing a
REM     ".cmd" path hands it to Windows' own file-type association, which
REM     runs it through cmd.exe -- landing here, in the @echo off section,
REM     as a fresh cmd.exe process that is a sibling of Git Bash, not a
REM     child shell inside it. That's why this section re-locates bash
REM     itself rather than assuming it's already on PATH.
REM
REM Hook scripts invoked through this dispatcher are extensionless (e.g.
REM "session-start", never "session-start.sh"): Claude Code's Windows
REM launcher auto-prepends "bash" to any command whose path contains ".sh",
REM which would collide with the dispatch this file performs.
REM
REM Usage: run-hook.cmd <script-name> [args...]

if "%~1"=="" (
    echo run-hook.cmd: missing script name >&2
    exit /b 1
)

set "HOOK_DIR=%~dp0"

REM Standard Git for Windows install locations.
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM A user-installed Git Bash, MSYS2 or Cygwin bash reachable on PATH.
where bash >nul 2>nul
if %ERRORLEVEL% equ 0 (
    bash "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM No bash found despite "shell": "bash" routing us here (e.g. Git for
REM Windows installed somewhere nonstandard and not on PATH). Exit clean
REM rather than surface a cryptic failure: the plugin still installs and
REM runs, it just loses SessionStart context injection for this session.
exit /b 0
CMDBLOCK

# --- Unix body: bash reaches this line having skipped the block above. ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_NAME="$1"
shift
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
