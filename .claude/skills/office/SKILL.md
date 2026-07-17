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

## Pinned source of truth (IADC)

The canonical IADC planning documents live in a single SharePoint folder — start
here rather than searching the whole tenant:

- **Site:** `netorg189334.sharepoint.com` (Ignyte tenant)
- **Folder:** `Shared Documents / Internal Projects / Appian / Appian Center of Excellence / Automated Code Review /`
  - **`v2/`** — **current.** The Appian-native rebuild that matches the live
    application and the in-flight parity/Epic-1 work. Default here.
    Base URL: `https://netorg189334.sharepoint.com/Shared Documents/Internal Projects/Appian/Appian Center of Excellence/Automated Code Review/v2/`
  - `v1/` — historical: original requirements, working-session notes, and user
    guides. Read for decision history, not current behavior.

**How to reach it:** use `sharepoint_search` with a **content** query (e.g.
`"IADC v2 Project Plan"`, `"Automated Code Review"`) — `sharepoint_folder_search`
by name does **not** find it, because the folders are named "Automated Code
Review / v1 / v2", not "IADC". Filter results to the pinned path above, and
prefer the `v2/` folder unless the user asks about history. Confirm the path is
still current if searches stop returning it (docs can move).

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
