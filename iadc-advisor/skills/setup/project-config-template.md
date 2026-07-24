Edit these values in place (or re-run `/setup`); per-person overrides go in `docs/agents/project.local.md` (gitignored, same field names — its values win).

- **Audience:** `developer` — one of `developer` | `lead` | `architect`
- **Appian version:** `<e.g. 26.6 — used for version-exact docs.appian.com lookups>`
- **Application:** `<full application name>`
  - **Nicknames:** `<e.g. CMS, "the case app"; optional>`
  - **UUID:** `<application UUID — the iadc graph seed target>`
- **Escalation:** `<Slack | Jira comment | hand-off>`
  - **Project lead:** `<Slack channel/handle, or Jira account>`
- **Office source of truth:** one row per prospect below, or `none`
  - **Row:** `<prospect name>` — site `<SharePoint site>`, folder `<pinned folder>`
  - **Active prospect:** `<prospect name — selects which row above is live>`
