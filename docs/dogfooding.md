# Dogfooding the plugin — test as a client sees it

Run the plugin from a scratch client repo, never from this one (`CLAUDE.md` §Working here owns
the never-install rule; this file owns the loop).

Create the scratch repo once, as a sibling **outside** this repo:

```bash
mkdir ../iadc-dogfood && git -C ../iadc-dogfood init
```

Add the **family catalog** as a marketplace — a local path while you are iterating, the git URL
to test what a client gets:

```bash
claude plugin marketplace add <path-to-IADC-Marketplace>
```

Then from `../iadc-dogfood`:

```bash
claude plugin install iadc-advisor@ignyte --scope project
```

open Claude there, and run `/iadc-advisor:setup`. The session hook, namespaced skills, and
per-project state behave exactly as they will for the client — including `iadc-graph` arriving
as a dependency, which is the part a local edit here cannot fake.

After editing the plugin, refresh **from `../iadc-dogfood`** (project scope is keyed to the
working directory) and start a fresh session:

```bash
claude plugin marketplace update ignyte && claude plugin update iadc-advisor@ignyte --scope project
```

> The catalog fetches this plugin from **`teamignyte/IADC-Advisor`**, not from your working
> tree, so an uncommitted edit will not appear in the dogfood repo. Push first, then refresh.
