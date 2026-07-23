# Store the application identity in the graph skill; seed from it, don't resolve it live

`/pressure-test` and `/orient` seed the `iadc` graph from a whole-application export, which
needs the Appian **application UUID**. Rather than resolve that UUID live through the
Appian MCP on every run, `/setup` captures the application name, nicknames, and UUID once
and writes them into a **Configuration block in `iadc-graph/SKILL.md`**; seeding reads the
UUID from there. Name, nicknames, and UUID live **together in that one block**, so a
nickname resolves to a UUID in a single lookup with no cross-file join.

## Consequences

- Seeding the graph needs no live Appian-MCP call. The Appian MCP is used only to inspect
  object internals, and — optionally, once — to resolve the UUID at setup time.
- The identity is per-project config: placeholders in the template, filled by `/setup` in
  the adopter's copy (the same pattern as the Appian version in `appian/SKILL.md`).
- Nicknames live here, not in `CONTEXT.md`, so the nickname→UUID mapping stays in one
  place. `CONTEXT.md` may still carry the application's name as domain vocabulary.
