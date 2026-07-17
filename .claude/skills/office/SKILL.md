---
name: office
description: "[PLACEHOLDER — NOT YET IMPLEMENTED] Intended to read Microsoft Office / SharePoint / OneDrive documents and Teams / Outlook context so the architect can ground planning in requirements and design docs. The MCP server and this skill's real content have not been built yet. Do not attempt to use it — there is no Office/SharePoint MCP connected."
---

# office — placeholder (not yet implemented)

**This is a stub.** The Microsoft Office / SharePoint integration for this bundle has **not been built**. There is no Office/SharePoint MCP server connected, and this skill has no working content. Do not attempt to call Office/SharePoint/Teams/Outlook tools — they do not exist in this bundle.

If a user asks the architect to read a SharePoint document, a OneDrive file, or Teams/Outlook context, tell them this capability is planned but not yet available, and fall back to what they can paste in or point you at directly.

## Intended purpose (when built)

The design intent — captured here so whoever implements it knows the target:

- **Read-only** access to SharePoint sites and OneDrive documents (Word, Excel, PDF) holding requirements, design specs, and process docs — so the architect can ground planning and answer "what did the spec say" from source-of-truth documents.
- Plus **collaboration context**: Teams messages and Outlook threads (meeting notes, decisions, email discussions), also read-only.
- **Consumed by `/groundwork`.** The main flow's context-gathering step (Frame) is designed to pull requirements and design context from SharePoint/OneDrive and Teams/Outlook. Until this MCP exists, `/groundwork` falls back to asking the developer to paste or point at those docs.

## To implement

1. Choose and connect a Microsoft 365 / SharePoint MCP server (e.g. a Microsoft Graph-based server), wired into `.mcp.json` with read scopes and literal secrets like the other servers (and a placeholder entry in `.mcp.json.example`).
2. Replace this stub with a real skill: the tool names, auth/permission model, how to locate a site/drive/document, and the read-only usage patterns.
3. Update `CLAUDE.md` and `which-skill` to route to it, wire it into `/groundwork`'s Frame step (and drop the "paste the docs" fallback there), and drop the "not built" callout from `for_liam.md`.

See `for_liam.md` at the repo root for why this was deferred.
