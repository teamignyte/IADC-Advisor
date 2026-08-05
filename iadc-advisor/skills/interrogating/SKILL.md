---
name: interrogating
description: The stateless interrogation primitive — a relentless, one-question-at-a-time interview that saves nothing locally. Invoked by /iadc-advisor:interrogate-with-docs and /iadc-advisor:interrogate-me, or explicitly when you want a bare stateless session. For a normal "interrogate my plan" request, prefer /iadc-advisor:interrogate-with-docs (the stateful, paper-trail default).
disable-model-invocation: true
---

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one.

Ask **Socratically**: pose questions that draw out my own reasoning and expose gaps, contradictions, and unexamined assumptions. Do **not** offer your own recommendation or answer — the point is to sharpen *my* thinking, not to hand me yours. When you spot a weakness, surface it with a question, not a verdict.

**Number your questions** (1, 2, 3, …) and ask them **one at a time**, waiting for my answer before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding. And if I end early — before we get there — don't just stop: surface any unresolved contradiction among the decisions we reached so I can settle it, and make sure everything I did decide is preserved by whatever's carrying state (in a `/iadc-advisor:interrogate-with-docs` session, written to `outputs/CONTEXT.md` / ADRs under `outputs/adr/`; in a bare stateless session, summarized back to me). Never leave decisions that still contradict each other.
