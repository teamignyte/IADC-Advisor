# IADC — Ignyte Appian Developer Copilot

The domain of an Appian application that automates code review of Appian objects.
Per-application **rules** evaluate objects during a **code review** and produce results.

## Language

**Application**:
An Appian application registered in IADC for automated code review — the unit that
rules are attached to and that code reviews run against.
_Avoid_: project.

**Rule**:
An automated code-review test evaluated against an Application during a code review.
"Rule" and "automated test" are the same concept. A single rule may apply to more than
one Application (see Rule Association) — it is one shared rule, not per-app copies.
_Avoid_: check. _(Canonical term provisional — Admins say both "rule" and "test".)_

**Related Applications**:
Two Applications made **eligible to share rules**. Relating them shares nothing on its
own; it makes each a candidate so that, per rule, an Admin can choose to associate that
rule with the other. It is *not* a general association (same program, one-calls-the-other).
_Avoid_: linked applications (when you mean a general, non-rule-sharing association).

**Rule Association**:
The link that makes a Rule apply to an Application. A rule may be associated with several
applications at once; there is still only **one** rule record, so editing it affects every
associated Application. An association is created **explicitly, per rule** (the Admin opts
in via the prompt) — never automatically for all related apps.
_Avoid_: clone, copy (those would create a second rule, which this is not).
