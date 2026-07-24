# Project configuration — iadc-advisor

Written by `/setup`; injected into every session by the plugin's session hook. Committed —
team-shared defaults. Personal overrides go in `docs/agents/project.local.md` (gitignored,
same field names; its values win).

- **Audience:** developer <!-- developer | lead — who the advisor is talking to -->
- **Appian version:** <e.g. 26.6 — used for version-exact docs.appian.com lookups>
- **Application:** <full application name>
  - **Nicknames:** <e.g. CMS, "the case app"; optional>
  - **UUID:** `<application UUID — the iadc graph seed target>`
- **Escalation:** <Slack | Jira comment | hand-off>
  - **Project lead:** <Slack channel/handle, or Jira account>
- **Office source of truth:** <SharePoint site + pinned folder, or "none">
  - **Active prospect:** <profile name, if managing several from one instance>
