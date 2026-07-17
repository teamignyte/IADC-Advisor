# Appian Architect-in-a-Box — Bundle Design

The working vocabulary for building and maintaining this bundle *itself* — how the
product is structured, shipped, and reasoned about. This is maintainer vocabulary; it
is **not** the domain language of any client's Appian application. That lives in the
client's own `CONTEXT.md`, in the client's repo (see `docs/adr/0001`).

## Language

### Product and repository

**Bundle**:
The reusable Claude Code configuration — a `CLAUDE.md`, the skills, and MCP config —
that turns Claude into an advisory Appian architect. The product this repo produces.
_Avoid_: tool, app, plugin

**Deliverable**:
The subset of the repo that ships to a client: everything under `bundle/`, and only
that. Its contents flatten to the client's repo root on install.
_Avoid_: release, dist

**Workshop**:
This repo, where the bundle is developed. Its root is the maintainer's dev
environment — auto-discovered by Claude Code — and is never shipped.

**Dev docs**:
Design docs about *building the bundle* — this `CONTEXT.md`, `docs/adr/`, and
`for_liam.md`. They sit at the workshop root, are shared among the bundle's
maintainers, and are never shipped.

**Usage docs**:
The `CONTEXT.md` and ADRs a *client* produces when they use the bundle on their own
Appian app. They live in the client's repo and describe the client's project; the
bundle never ships them.

### Flow and posture

**Spine** (a.k.a. the main flow):
The primary path most work travels through the skills. Per `docs/adr/0002`, the spine
starts from a defined unit of work — a ticket or a description of it — and produces
implementation guidance.

**Groundwork** (`/groundwork`):
The skill that *is* the spine's entry point — from a ticket or a description of the work it gathers
context, inspects the Appian app, sharpens the developer's approach, and yields
implementation guidance. A thin orchestrator over the inspection and interrogation
skills.

**On-ramp**:
A starting situation that generates planning work and then merges onto the spine —
e.g. `wayfinder` for a huge, foggy effort.

**Handoff point**:
The moment advisory output leaves the bundle for execution elsewhere. The bundle plans
up to this point and stops.

**Advisory posture**:
The house rule that the bundle only inspects, reasons, plans, and hands off — it never
writes application code or mutates Appian design objects.
_Avoid_: read-only (that's the MCP mode, narrower than the posture)
