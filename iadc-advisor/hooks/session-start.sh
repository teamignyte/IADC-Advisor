#!/usr/bin/env bash
# iadc-advisor SessionStart hook — the plugin's replacement for a shipped CLAUDE.md
# (plugins cannot load one; see workshop ADR 0009). Injects the operating posture,
# then this project's configuration, with the gitignored per-person override last
# so its values take precedence (ADR 0010).
set -eu

plugin_root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
project_dir="${CLAUDE_PROJECT_DIR:-.}"
project_root=$(cd "$project_dir" 2>/dev/null && pwd -P) || project_root=""

# True only for a plain file that really lives inside the project directory.
# Everything this hook cats goes straight into the session context, so a config
# path that is a symlink — or that resolves outside the project — would paste
# whatever it points at (say, the gitignored .mcp.json and its credentials) into
# every session. Refuse to follow one; the caller then takes its not-configured
# path instead of aborting the hook.
safe_project_file() {
  if [ -z "$project_root" ]; then
    return 1
  fi
  if [ -L "$1" ] || [ ! -f "$1" ]; then
    return 1
  fi
  file_dir=$(cd "$(dirname "$1")" 2>/dev/null && pwd -P) || return 1
  case "$file_dir" in
    "$project_root" | "$project_root"/*) return 0 ;;
  esac
  return 1
}

cat "$plugin_root/hooks/posture.md"

if safe_project_file "$project_dir/docs/agents/project.md"; then
  printf '\n## Project configuration (from docs/agents/project.md — written by /setup)\n\n'
  cat "$project_dir/docs/agents/project.md"
else
  printf '\n## Project configuration\n\nNot configured yet — run /setup to wire the MCP servers and project values.\n'
fi

if safe_project_file "$project_dir/docs/agents/project.local.md"; then
  printf '\n## Personal overrides (from docs/agents/project.local.md — gitignored; these values OVERRIDE the project configuration above)\n\n'
  cat "$project_dir/docs/agents/project.local.md"
fi
