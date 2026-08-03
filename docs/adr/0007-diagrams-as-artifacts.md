# A `to-diagram` primitive renders diagrams saved locally and, optionally, published as artifacts

The plugin explained everything in prose and lists, with one exception — `orient` inlined a Mermaid
ERD. Visual explanations (app topology, blast radius, record models, build-step order, ticket
dependency graphs, status lifecycles) carry more than prose, so the plugin gains a shared
**`to-diagram`** skill: a rendering primitive that picks the right Mermaid type, gets the syntax
right, and is pulled in by `/orient`, `/pressure-test`, `/to-spec`, and `/to-tickets` (and is
invocable directly). It is advisory — a diagram is a document, not a build.

`to-diagram` introduces two firsts for the plugin, recorded here because they touch its posture:

1. **Diagrams persist as files.** Saved — gated, on approval — into the gitignored `outputs/`
   workspace: embedded in the artifact they belong to (a `to-spec` spec, a `pressure-test`
   `decisions.md`), or a standalone `outputs/[<TICKET-KEY>/]diagrams/<slug>.md`.
2. **Diagrams may leave the local machine.** They are always emitted inline as a fenced
   ` ```mermaid ` block, and — where the environment supports it — *also* published as a claude.ai
   **Artifact** for a rendered view. An Artifact is default-private but **hosted off-box**, a
   departure from the plugin's otherwise strictly-local, gitignored, read-only posture.

## Why

- **A picture is the most reusable artifact.** `orient` already found this — its ERD is "the single
  most reusable artifact this skill produces." Generalizing that into a shared primitive keeps
  Mermaid know-how (type choice, syntax gotchas) in one place instead of copied into every skill.
- **Present *and* save, with a local fallback.** Publishing as an Artifact gives the reader the
  picture, not the source; saving keeps a durable copy; the inline fenced block guarantees the
  diagram survives anywhere Mermaid renders — no environment dead-ends.

## Consequences

- **The off-box publish is the trade-off.** Rendering/shareability is bought against the local-only
  privacy posture. The skill flags this and keeps the inline block + saved file as the always-local
  path; for a sensitive client's architecture, skip the hosted Artifact.
- Saving follows the plugin's **gated, never-auto-write** rule — offer, then write on approval.
- `to-diagram` is registered in `which-skill` (the router), and carries
  full-coverage Mermaid reference files under `references/` (progressive disclosure — read the
  matching file before generating a non-trivial diagram of that type).
