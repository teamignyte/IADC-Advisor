---
status: accepted
---

# Share rules across applications by reference, not by copy

## Context

IV-207 asks to let Admins relate applications so they don't manually re-add the same
rules (automated tests, `IADC Object Test`) to each app. The ticket's AC #4 and the
app's existing `Clone Test Rules` action both imply **copying** rules to related apps.
Interrogation of the assignee established the opposite intent: there should be **one
shared rule record** that applies to several applications, edited in one place. So a
shared rule is a single `IADC Object Test` **associated with many applications**, not a
per-app duplicate.

## Decision

- A rule is **shared by reference**: one `IADC Object Test` record, associated with one
  or more Applications. No copies.
- This makes **Rule ↔ Application many-to-many.** Today it is one-to-many
  (`IADC Object Test.application`, MANY_TO_ONE → `IADC Application`); we introduce a
  junction (Rule Association) and migrate existing rules into it.
- Associations are created **per rule, opt-in**, via the Add-Rule prompt; the Admin picks
  which related apps. The App↔App "related" link is **symmetric** and only a *gate* that
  makes apps eligible to be offered — it shares nothing on its own.
- **Lifecycle:** editing a shared rule changes it for every associated app (v1 shows a
  warning naming them). "Delete from an app" **detaches** that association; the record
  survives while ≥1 association remains. Un-relating two apps does **not** strip existing
  associations.
- **Rejected — copy/clone** (the `Clone Test Rules` mechanism): produces duplicates that
  drift apart, and contradicts "edit once, applies everywhere." Not reused for this feature.
- **Rejected — keep one-to-many:** cannot express a rule that applies to multiple apps.

## Consequences

- **Large blast radius.** `IADC Object Test` has **118 transitive dependents** in the
  graph. Anything that selects "the tests for application X" via the current
  `application`/`iadcObjectTest` FK must move to the junction. The highest-risk consumers:
  the review engine (`IADC Run Deterministic Tests`, `IADC Run Deterministic Checks with
  Export`), test-selection/query rules (`IADC_qrtObjectTest`, `IADC_mapTestsToObjects`,
  `IADC_assertObjectTest`), the parity Web APIs (`IADC Test`, `IADC Get Parity Review
  Results`), and the Object Test grids/dashboards.
- **Data migration required:** backfill one association row per existing `IADC Object Test`
  from its current `application` value before switching reads to the junction.
- **Regression risk on the code-review engine** is the main thing to test — the app's own
  deterministic-test harness should cover the changed selection logic.

## Deferred (out of scope for this build)

- **Fork-on-edit:** an option to "not apply this change to the other apps" that auto-creates
  a private copy.
- **Bulk-associating** an existing rule library when relating apps — v1 shares rules only
  going forward, one at a time.
