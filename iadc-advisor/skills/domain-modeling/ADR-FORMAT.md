# ADR Format

ADRs live in the **`outputs/adr/`** workspace (git-ignored where `/iadc-advisor:setup`'s ignore rules were accepted) and use **project-wide sequential numbering** — `0001-slug.md`, `0002-slug.md`, … — assigned in the order decisions are made. That single ascending sequence **is the chronological history of every decision on the project**, across all tickets. (Per-ticket `decisions.md` files roll these up and link back to them by number — the ADRs are the durable record; `decisions.md` is the index.)

Create the `outputs/adr/` directory lazily — only when the first ADR is needed.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections.

## Optional sections

Only include these when they add genuine value. Most ADRs won't need them.

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`) — useful when decisions are revisited
- **Considered Options** — only when the rejected alternatives are worth remembering
- **Consequences** — only when non-obvious downstream effects need to be called out

## Numbering

Scan the target `adr/` folder for the highest existing number and increment by one.

## When to write an ADR — every substantive decision

Write an ADR for **each substantive decision, as it is made** — so the `outputs/adr/` sequence
becomes a complete chronological record. A "substantive decision" is any resolved choice that had a
real alternative: what was put to the developer or the lead, each resolved escalation, and any
design call that shapes the build. When in doubt, write it — a lightweight one-paragraph ADR is
cheap, and the value is the *history*.

**The one exclusion:** trivial **advisor's-call mechanics** with no real alternative — "use the
existing `LARGE` batch-size constant", "name the field to match the column" — don't each need an
ADR. Note those in the ticket's `decisions.md` and move on. If it had a genuine fork, it's a
decision; if it was the obvious mechanical way, it isn't.

### What a substantive decision looks like

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library — just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and picked REST for subtle reasons, record it — otherwise someone will suggest GraphQL again in six months.
