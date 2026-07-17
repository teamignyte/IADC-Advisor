---
name: groundwork
description: Plan how to build a specific, already-defined piece of Appian work — a Jira ticket or a described task — by getting oriented in the actual application (what it touches, its blast radius, the objects involved, the platform how-to) and sharpening the approach through interview, ending in a short implementation note. Use this whenever a developer has a ticket or a concrete task in hand and needs to work out HOW to implement it in this app ("how do I build this", "where do I start on TICKET-123", "what's my approach for adding X"), even when they don't name a flow. Do NOT use it for general Appian *platform* how-to with no task attached (that's /context7 + docs.appian.com), for merely understanding how an existing part of this app already works with no build in view (that's /iadc-graph + /appian), or for shaping fuzzy, undefined, or net-new work into specs and tickets (that's the greenfield flow — /interrogate-with-docs → /to-spec → /to-tickets, or /wayfinder).
---

# Groundwork

A developer has a piece of work — a Jira ticket, or a plain description of a task — and
needs to figure out **how** to build it in this Appian application. Groundwork gets them
oriented in the app and sharpens the approach. It does **not** build anything; execution
happens outside this bundle.

The flow is **orient-led**: ground the developer in the app *first*, then interrogate the
approach. Interrogation is how a plan gets hardened — it isn't the opening move, because
a developer (especially one new to the app) often has nothing to interrogate yet.

Run it **adaptively**. The floor is three things that always happen — Frame (step 1), a
blast-radius check (step 2), and Capture (step 5); scale everything else to the size and
risk of the work. A one-line label change gets a fast pass. A change whose blast radius
fans across the app, or one in unfamiliar territory, earns the full treatment. Running
the whole pipeline on trivial work just trains people to skip the skill.

Load the domain skills as you reach for them — all are read-only: `/appian` before the
Appian MCP, `/iadc-graph` before the graph MCP, `/context7` for docs, `/jira` to read the
board.

## Process

### 1. Frame the work

- Take the input. If it's a **ticket**, read it via `/jira` — title, description,
  acceptance criteria, comments, linked issues. If it's a **description**, work from that.
- Gather the surrounding context: requirements and design docs (SharePoint / OneDrive),
  intent and decisions captured in conversation (Teams / Outlook). *The Office MCP isn't
  built yet — until it is, ask the developer to paste or point you at the relevant docs
  rather than silently skipping this.*
- Restate, in your own words, what's being asked and what "done" looks like, and confirm
  that restatement with the developer — one question, plain language — before going on.
  A wrong understanding here wastes the whole session.
- Ask whether they already have an approach in mind. This decides how step 4 runs.

### 2. Locate & assess in *this app*

This step is about the specific application, not the platform — you're finding where the
work lands in the code that's actually there.

- Identify the Appian objects the work concerns. Resolve their **names to UUIDs** via the
  `/appian` MCP first — the graph takes a node id, never a display name.
- With the node id(s), run the **blast-radius check** via `/iadc-graph` (always — it's
  cheap, and it's the whole reason the graph exists): what calls these objects, what they
  depend on, the record model around them. This is what tells you the true size of the
  change, so a "small" ticket that turns out to touch everything can't ambush you later.
- Scale from here. Small and contained → note it and move on. Wide, or unfamiliar → open
  the actual objects with `/appian` (record types, expression rules, interfaces, process
  models) so the approach rests on what's really there rather than an assumption.

### 3. Appian *platform* how-to

Distinct from step 2: here you're answering "how does Appian *the platform* do this?",
not "how does *our app* work?".

- For the techniques the work needs — a SAIL pattern, a function, a component, a security
  or data-modeling question — search `/context7` first.
- Confirm anything version-sensitive against the authoritative docs.appian.com at the
  project's version, via `/appian`. Prefer the graph, the live environment, and the docs
  over memory, and cite what you rely on so the developer can check it.
- Skip this step when the work only uses patterns the developer already knows.

### 4. Sharpen the approach

- Now interrogate — one question at a time, plain language (the `/interrogating`
  discipline). One compound question buries the point you're trying to sharpen.
- If the developer **has** an approach, stress-test it against what steps 2–3 surfaced:
  does it account for the blast radius? Does it fit how Appian actually works here? Where
  would it break?
- If they **don't**, co-develop one — propose a shape grounded in the objects and
  patterns you found, then pressure-test that.
- Watch for a **hard-to-reverse decision** surfacing (a genuine trade-off with real
  alternatives). If one does, flag it — it's a candidate for an ADR in step 5.

### 5. Capture

Draft a short **implementation note** from the developer's perspective. Avoid file paths
and code snippets, which go stale fast; keep it to the decision-rich shape (a state model
or schema may be inlined if it pins a decision more precisely than prose can).

<implementation-note>
**What & where:** the piece of work, and where in the app it lives.
**Touches / blast radius:** the objects affected and what depends on them.
**Approach:** the steps to build it, in order, in the project's vocabulary.
**Appian notes:** the patterns / functions / gotchas that apply (cite docs).
**Open questions:** anything unresolved for the ticket author or reviewer.
</implementation-note>

Then place it:

- **Entry was a ticket** → offer to post the note as a **comment** on that ticket. Show
  the draft, get an explicit yes, then post via `/jira`. Never automatic; the default is
  draft-local, offer-to-attach.
- **Entry was a description** (no ticket) → keep the note local. There's nothing to attach
  to, and groundwork does not create a ticket.

If a real decision surfaced in step 4, **offer to record an ADR** in `docs/adr/` — only
when it's hard to reverse, surprising without context, and a genuine trade-off. Most runs
won't produce one, and that's fine.

If the developer only wanted orientation, **stop**. No artifact is a perfectly good ending.

## Boundaries

- Groundwork advises; it does not build. No application code, no mutating Appian objects.
  The Appian and graph MCPs are read-only by design.
- Jira is human-first. The **only** write groundwork makes is the note-as-comment, gated
  and proposed. It does **not create** tickets — if the work needs splitting, or a
  prerequisite isn't tracked, say so and offer to hand off to `/to-tickets`. It does
  **not modify** tickets — a rescope or clearer acceptance criteria are called out for a
  human, with the clarified understanding left in the note.
- If this turns out to be net-new *shaping* rather than a defined build, route to the
  greenfield flow: `/interrogate-with-docs` → `/to-spec` → `/to-tickets`, or `/wayfinder`
  if it's huge and foggy.
