Edit these values in place (or re-run `/setup`); this file is committed and shared with the team, so per-person overrides go in `docs/agents/project.local.md` (gitignored, same field names — its values win). To track more than one prospect, duplicate the entire `- **Row:**` line once per prospect, keeping each prospect name distinct, then name the live one on the `Active prospect` line.

- **Audience:** `developer` — one of `developer` | `lead` | `architect`
- **Appian version:** `<Appian version — used for version-exact docs.appian.com lookups>`
- **Application:** `<full application name>`
  - **Nicknames:** `<e.g. CMS, "the case app"; optional>`
  - **UUID:** `<application UUID — the iadc graph seed target>`
- **Escalation:** `<Slack | Jira comment | hand-off>`
  - **Project lead:** `<Slack channel/handle, or Jira account>`
- **Office source of truth:** `rows below` — keep `rows below` and fill in the lines beneath it; if this project has no M365 source documents, replace `rows below` with `none` **and delete the `Row` and `Active prospect` lines below**
  - **Row:** `<prospect name>` — site `<SharePoint site>`, folder `<pinned folder>`
  - **Active prospect:** `<prospect name — must match one of the Row names>` — picks which Row above is live
