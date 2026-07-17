---
name: context7
description: Semantic search over Appian documentation via the context7 MCP. Use this as the FIRST stop whenever you need to look up how an Appian feature, SAIL function, component, or platform behaviour works — "how do I…", "what's the function for…", "does Appian support…". Reach for it before answering an Appian docs question from memory, and confirm version-sensitive answers against the authoritative docs.appian.com via the /appian skill.
---

# context7 — Appian documentation search

`context7` is a documentation-search MCP. Its Appian index holds tens of thousands of ranked snippets from the Appian Suite help site, so it answers open-ended "how does X work in Appian" questions far better than reading raw HTML docs page-by-page. Use it to ground answers and plans in what Appian actually documents, instead of guessing from memory.

## When to reach for it

- A developer asks how an Appian feature, SAIL function, component, record-type behaviour, or platform capability works.
- You're about to recommend a function or pattern and want to confirm it exists and is used correctly.
- You need example usage or the shape of a configuration you don't have memorised.

This is a **read-only** lookup — it retrieves documentation, it changes nothing.

## How to use the MCP

The context7 server exposes two tools (exact prefix depends on config; look for these names):

1. **`resolve-library-id`** — find the Appian documentation library. Search for `appian` and pick the Appian Suite help entry (e.g. an id like `/websites/appian_suite_help_26_6`). Prefer the version closest to the project's configured Appian version (26.6).
2. **`query-docs`** — fetch documentation for that library id, passing the topic you're researching (e.g. "a!queryRecordType", "record type security", "interface component grid"). Narrow the topic so the returned snippets are relevant.

Read the returned snippets, then answer with a citation to the doc they came from.

## The authority hierarchy — context7 first, docs.appian.com to confirm

context7 is the fast **discovery** layer; it is **not** the source of truth. Its index is:

- **a subset** of the full Appian docs, and
- **pinned to whatever version was indexed** (which may lag the project's actual Appian environment).

So use it in this order:

1. **Search context7 first** to find the relevant behaviour, function, or pattern quickly.
2. **Confirm against `docs.appian.com`** — via the `/appian` skill's version-specific documentation lookup — whenever the answer is **version-sensitive** (function signatures, availability, deprecations), whenever you're about to give a firm recommendation, or whenever context7 comes back thin or empty. `docs.appian.com`, at the project's configured version, is authoritative; context7 is not.

If context7 and `docs.appian.com` disagree, `docs.appian.com` wins — and note the discrepancy (usually a version gap between context7's index and the live environment).
