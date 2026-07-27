---
name: "office"
description: "Read Microsoft 365 context — SharePoint/OneDrive documents (requirements, specs, process docs) and Teams/Outlook discussion — through the Microsoft 365 connector, to ground the Appian advisor's planning and answers in source-of-truth documents. Read-only: inspect and cite, never send, upload, edit, or delete. Load when the architect needs to find or read a spec, requirements doc, or a decision recorded in Teams/Outlook. Verbs: read the spec, find requirements, what does the doc say, SharePoint doc, Teams thread, meeting notes."
---

Pull **context from Microsoft 365** to ground the Appian advisor. Like the Jira
board, this surface is **human-first and read-only**: your job is to **find and
read** source-of-truth documents and discussion — via the Microsoft 365
connector — so planning and answers rest on what the spec actually says, not
memory. You never send, upload, edit, move, or delete anything.

Access is through the **Microsoft 365 Claude connector** (OAuth), not `.mcp.json`
— there are no tokens or env vars to configure here. If the connector isn't
connected, tell the user to enable it in their client's connector settings
(`/setup` covers this) and fall back to what they can paste in or point you at.

## What this is for

- **Ground planning in requirements.** Before interrogating a plan or writing a
  spec, find and read the SharePoint/OneDrive docs that state the requirements,
  and answer "what did the spec say" from the document, not recollection.
- **Recover decisions from discussion.** Pull the relevant Teams thread or
  Outlook exchange where a decision or constraint was recorded, and bring it
  into the conversation — cited.

The ticket-first flow consumes this: `/pressure-test` grounds every question against
these docs (searching SharePoint by the ticket key), and `/interrogate-with-docs`
pulls requirements before sharpening a plan.

## Configuration

The advisor searches a **pinned source-of-truth folder** first, rather than scanning the
whole tenant. Read the **`Office source of truth`** entry from the ambient
**Project configuration** (from `docs/agents/project.md`, written by `/setup`), after
applying any **Personal overrides**: one **row per prospect**, each carrying that
prospect's site + pinned folder, with the **`Active prospect`** line naming which row is
live. Tracking several prospects in this one repo? Add a row per prospect and switch by
changing the **Active prospect** line — that single edit is the whole toggle.

Then test whether it is configured — **in this order, first match wins:**

1. **Unfilled ⇒ not configured.** If the **`Office source of truth`** value — or the
   **`Active prospect`**'s site/folder — is missing, empty, or still an
   **unfilled angle-bracket placeholder** (e.g. `<pinned folder>`), nothing is configured yet.
   Judge this by the **token, not the wording: angle brackets present ⇒ unfilled**, whatever
   words sit inside them — placeholder text may itself mention `none`, which is *not* an answer.
   Ask the user for the site/folder (or search the tenant), read from there, and offer to record
   it via `/setup`.
2. **A bare `none` ⇒ deliberate.** Only when the value is the bare word `none`, with no angle
   brackets around it, does this project have **no M365 source documents**: say so, and
   **do not search SharePoint/OneDrive** for source documents. Do **not** offer to configure
   a folder — `none` is a deliberate answer, not a missing one.
   This stops **SharePoint/OneDrive document search only**.
   **Teams and Outlook lookups are unaffected** — recovering a decision from Teams or Outlook
   discussion works exactly as it does on any other project.

**How to reach it:** prefer `sharepoint_search` with a **content** query (words from the
project or plan title) over `sharepoint_folder_search` by name — folder-name search is
unreliable when the folder isn't named after the project. Filter results to the pinned folder
on the **Active prospect**'s row, and confirm the path is still current if searches stop
returning it (docs can move).

## Reading (the only mode)

Use only the connector's **read** tools:

- **SharePoint / OneDrive** — `sharepoint_search`, `sharepoint_folder_search`
  to locate a site/drive/document; `read_resource` to read its contents.
- **Outlook** — `outlook_email_search`, `outlook_calendar_search` for email
  threads and meeting context.
- **Teams** — `teams_list_chats`, `chat_message_search` for discussion.

Summarize what's relevant back into the conversation and **cite the document
title or thread** so the architect can trace it.

## Never write

This surface is strictly read-only. Do **not** call any tool that sends,
creates, uploads, updates, moves, copies, renames, or deletes — e.g.
`outlook_send_mail`, `outlook_create_*`, `sharepoint_upload_file`,
`sharepoint_update_file`, `sharepoint_delete_item`, `sharepoint_move_item`,
`sharepoint_create_folder`. If a user asks the architect to send mail or edit a
document, decline: that's execution, outside this advisory bundle. Reading and
citing is the whole job.
