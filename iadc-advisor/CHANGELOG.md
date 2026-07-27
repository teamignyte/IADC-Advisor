# Changelog — iadc-advisor

## 1.0.0 — 2026-07-23

First release as a Claude Code plugin (previously installed by copying files into the
app repo — no migration path; this is a clean break).

- Install from the `ignyte` marketplace at **project scope**, per Appian-app repo.
- Session hook injects the operating posture + `docs/agents/project.md`
  (+ personal `project.local.md` override — per-person Audience).
- `/setup` now materializes all per-project state: `.mcp.json`, project configuration,
  tracker/domain docs, `outputs/`, `.gitignore` entries.
- No per-project values live in skill files anymore.
