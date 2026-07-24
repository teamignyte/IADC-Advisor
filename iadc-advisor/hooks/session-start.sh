#!/usr/bin/env bash
# iadc-advisor SessionStart hook — the plugin's replacement for a shipped CLAUDE.md
# (plugins cannot load one; see workshop ADR 0009). Injects the operating posture,
# then this project's configuration, with the gitignored per-person override last
# so its values take precedence (ADR 0010).
set -eu

plugin_root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
project_dir="${CLAUDE_PROJECT_DIR:-.}"

cat "$plugin_root/hooks/posture.md"

if [ -f "$project_dir/docs/agents/project.md" ]; then
  printf '\n## Project configuration (from docs/agents/project.md — written by /setup)\n\n'
  cat "$project_dir/docs/agents/project.md"
else
  printf '\n## Project configuration\n\nNot configured yet — run /setup to wire the MCP servers and project values.\n'
fi

if [ -f "$project_dir/docs/agents/project.local.md" ]; then
  printf '\n## Personal overrides (from docs/agents/project.local.md — gitignored; these values OVERRIDE the project configuration above)\n\n'
  cat "$project_dir/docs/agents/project.local.md"
fi
