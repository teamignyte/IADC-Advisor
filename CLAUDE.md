# Appian Architect-in-a-Box — Workshop

This is the **workshop**: the development environment for the Appian Architect-in-a-Box bundle. You are working *on the product here, not with it*.

## The deliverable is `deliverable/` — and only `deliverable/` ships

Everything the client receives lives under [`deliverable/`](deliverable/) — its `CLAUDE.md`, `README.md`, `.claude/skills/`, `.mcp.json.example`, and `.gitignore`. On install those contents flatten to the client's repo root. Shipping is an **allowlist**: if it's outside `deliverable/`, it does not ship. See [docs/adr/0001](docs/adr/0001-deliverable-lives-in-a-subfolder.md).

## Dev docs live here at the root (never shipped)

- `CONTEXT.md` — **maintainer** vocabulary for how the bundle is built and reasoned about. This is *not* a client Appian app's glossary; the bundle's own skills would misread it as one, which is exactly why they live in `deliverable/`, not here.
- `docs/adr/` — decisions about building the bundle.
## Working here

- **Develop the bundle** by editing files under `deliverable/`.
- **Dogfood / test it as a client sees it** by opening Claude with **`deliverable/` as the working directory** — then `deliverable/CLAUDE.md` and `deliverable/.claude/skills/` load as root, exactly as they will for the client.
- **The advisory posture holds even in the workshop:** this repo produces docs, decisions, and configuration — it does not build client Appian objects or write application code.

## Deploying

Push this workshop repo with the **PAT in `.secrets/git-credentials`** (gitignored; never committed) — that PAT is the deploy identity. Don't fall back to ambient GitHub or `gh` auth. It needs `repo` scope and must be SSO-authorized for the `teamignyte` org; refresh it there when it expires.

## Extending the bundle

Author or edit skills with the **`skill-creator`** skill — it carries the frontmatter conventions, progressive-disclosure structure, and description-triggering guidance, and can run eval loops to harden a new skill. When you add or rename a skill, update **`which-skill`** (the router) and the skill map in `deliverable/CLAUDE.md` to match.

Keep new skills **advisory** — the bundle is deliberately execution-free (no code-writing or triage skills; it plans and hands off). Record hard-to-reverse build decisions as ADRs in `docs/adr/`.
