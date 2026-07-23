---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

These are **generated project artifacts, not committed bundle source** — they live in the
**git-ignored `outputs/` workspace** (see `outputs/README.md`). Most projects have a single
context:

```
outputs/
├── CONTEXT.md                        ← the project glossary
├── adr/                              ← chronological history: one ADR per substantive decision
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── <TICKET-KEY>/                     ← per-ticket rollup: decisions.md (links its ADRs) + build spec
```

If a `CONTEXT-MAP.md` exists at the workspace root, the project has multiple contexts. The
map points to where each one lives:

```
outputs/
├── CONTEXT-MAP.md
├── adr/                              ← system-wide decisions
├── ordering/
│   ├── CONTEXT.md
│   └── adr/                          ← context-specific decisions
└── billing/
    ├── CONTEXT.md
    └── adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create
one under `outputs/` when the first term is resolved; create an `adr/` folder when the first ADR
is needed. (The `outputs/` base is git-ignored by default — see `outputs/README.md` to change
that if your team wants the model version-controlled.)

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Don't persist a contradiction — and capture before the session ends

Write a decision or term only once it's consistent with what's already captured. If something the user says conflicts with an existing `CONTEXT.md` entry or an ADR, surface the contradiction and let them resolve it *before* you write — never quietly append a second, conflicting version. And if the interview ends early, do a final pass before you stop: capture anything decided but not yet written, and flag any contradiction still open — so the docs are never left half-written or internally inconsistent.

### Write an ADR for each substantive decision

Record **every substantive decision as its own ADR**, as it's made — the `outputs/adr/` sequence is
the project's chronological decision history. A substantive decision is any resolved choice that had
a real alternative (what was put to the developer or the lead, each resolved escalation, a design
call that shapes the build). Keep each ADR lightweight — a paragraph is fine; the value is that the
decision and its *why* are on the record. The only thing you skip is a trivial advisor's-call
mechanic with no real alternative (note it in `decisions.md` instead). Use the format in
[ADR-FORMAT.md](./ADR-FORMAT.md).
