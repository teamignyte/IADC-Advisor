Edit these values in place (or re-run `/iadc-advisor:setup`); this file is committed and shared with the team, so per-person overrides go in `docs/agents/advisor.local.md` (gitignored where `/iadc-advisor:setup`'s ignore rules were accepted; same field names — its values win).

**How to fill these in.** The data lines below carry **bare values** — every rule for choosing one is stated here, above the data, and never as a trailing note on the line itself. **Audience** takes one of `developer` | `lead` | `architect`. **Office source of truth** keeps its shipped value, `rows below`, whenever this project has M365 source documents: fill in the `Row:` and `Active prospect:` lines beneath it, and to track more than one prospect duplicate the entire `- **Row:**` line once per prospect, keeping each prospect name distinct, then name the live one on the `Active prospect` line. A project with **no M365 source documents** instead sets **Office source of truth** to `none` and **deletes the `Row:` and `Active prospect:` lines**.

- **Audience:** `developer`
- **Appian version:** `<Appian version — used for version-exact docs.appian.com lookups>`
- **Application:** `<full application name>`
  - **Nicknames:** `<e.g. CMS, "the case app"; optional>`
  - **UUID:** `<application UUID — the iadc graph seed target>`
- **Escalation:** `<Slack | Jira comment | hand-off>`
  - **Project lead:** `<Slack channel/handle, or Jira account>`
- **Office source of truth:** `rows below`
  - **Row:** `<prospect name>` — site `<SharePoint site>`, folder `<pinned folder>`
  - **Active prospect:** `<prospect name — must match one of the Row names>`
