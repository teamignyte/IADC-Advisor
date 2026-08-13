## Purpose

This skill enables accessibility auditing of Appian interfaces done **from source** — reading the
SAIL expression itself, since there is no live Appian connection here to render a component tree
with. It covers the SAIL Testing checks that can be performed by examining SAIL parameters rather
than requiring manual browser testing or screen reader verification.

## How It Works

1. **Find the interface** — use `find_nodes(session_id, query=<name>)` (or `list_nodes` filtered
   to `kind="artifact", object_type="interface"`) against the `iadc` graph to resolve its `node_id`
2. **Retrieve the SAIL source** — `get_sail(session_id, node_id)` returns the interface's own
   `sail_strings`, in source order
3. **Evaluate the source directly** — walk the SAIL, parameter by parameter, checking each
   component against the rules in `component-checks.md`. There is no rendered component tree to
   inspect (never was, with or without a live Appian connection) — every check here works from
   the SAIL text itself
4. **Report findings** — list each violation with the component path (as written in the SAIL),
   the rule violated, and the fix

When auditing, read every conditional branch of the SAIL — the `if()`/`a!match()` cases and the
`showWhen` guards — so a component that only renders in one state (create vs. edit, expanded vs.
collapsed) isn't missed. There is no way to evaluate a state and see only what that state renders,
the way rendering would; reading the source means reading every branch by hand.

## Rule Categories

The complete rules with Rule IDs, applicable components, and specific checks are in `component-checks.md`. Here is what each category covers:

| Category | What to Check |
|---|---|
| **Form Inputs** | `label` set on all inputs, `labelPosition` handling, duplicated control context, `choiceLabels`, `inputPurpose`, toggle labels |
| **Validations** | `required: true` on mandatory fields, OOTB validation params used, input name included in error text |
| **Instructions** | Format/range guidance via `instructions` parameter, not separate rich text |
| **Grids** | Grid `label`, column headers, `rowHeader`, no empty spacer columns, instructions say "table" not "grid", selection `accessibilityText` |
| **Headings** | Semantic headings via `a!headingField` or `labelHeadingTag`, appropriate levels (H1–H6) |
| **Lists** | Visual lists use `a!richTextBulletedList`/`a!richTextNumberedList` |
| **Section/Box Layouts** | Expandable sections/boxes have `label` + `labelHeadingTag` |
| **Tabs** | Each `a!tabItem` has a `label` |
| **Panes** | `accessibilityText` set, no reserved words (pane, main, navigation, etc.) |
| **Cards** | Linked cards have no nested controls, no link label, selection state via `accessibilityText` |
| **Card Choice/Group** | `label` set when multiple cards in group |
| **Links** | `linkStyle: "INLINE"` for links embedded in text |
| **Icons** | `altText`/`caption` rules for standalone vs. with-text, in links vs. buttons, decorative icons null |
| **Progress Bar** | `label` set |
| **File Upload** | `label` and `instructions` set |
| **Charts** | `label` set |
| **Forms** | `focusOnFirstInput: false` when info precedes inputs, required-field legend present |
| **Modal Dialog** | `focusOnFirstInput: false` in dialogs with preceding content |
| **Stamps** | `tooltip`/`helpTooltip` must be null |
| **Prohibited** | `a!dateTimeField` must not be used |
| **Dynamic Content** | `a!messageBanner` with `announceBehavior`, content order after trigger |
| **Pagination** | Inactive links have null `accessibilityText`/`altText`/`caption` |
| **Simulated Grids** | Layout-based grids need `accessibilityText` per cell (flag for review) |
| **Signature** | Keyboard alternative alongside `a!signatureField` (flag for review) |
| **Images** | No embedded text in images (flag for review) |
| **Breadcrumbs** | `accessibilityText` identifies breadcrumb and current page |

## Audit Workflow

### Full Interface Audit

1. Resolve the interface's `node_id` (`find_nodes` against the `iadc` graph, or provided by the user)
2. Retrieve its SAIL source with `get_sail`
3. Walk the SAIL source and check each component against the rules in `component-checks.md` —
   read every conditional branch by hand (see "How It Works" above); there is no rendered tree
   that would show you only what one state renders
4. Compile findings into a table: Rule ID | Component Path | Issue | Recommended Fix

### Quick Checks (Single Component Type)

When the user asks about a specific component or rule:
1. Search the SAIL source for that component type
2. Check only the relevant rules from the component-checks reference
3. Report pass/fail with specifics

### Writing Accessible Interfaces

When creating new interfaces, apply these rules proactively:
- Set `label` on every input, grid, progress bar, file upload, and chart
- Set `accessibilityText` on panes and grids with row-selection behavior
- Use `a!headingField` or `labelHeadingTag` for headings — never styled rich text
- Use `a!richTextBulletedList`/`a!richTextNumberedList` for lists
- Provide `instructions` on inputs that need format guidance
- Set `altText` or `caption` on icons used standalone in links/buttons
- Never use `a!dateTimeField`
- Set `required: true` on mandatory inputs
- Use OOTB validation parameters instead of custom error display
- Include the input name in all validation/error messages
- Add a required-field legend when any inputs use `required: true`
- Ensure dynamically revealed content appears after its trigger in DOM order
- Set `accessibilityText` on breadcrumb rich text to identify it and the current page
- Provide a keyboard alternative alongside `a!signatureField`
- Set inactive pagination link parameters (`accessibilityText`, `altText`, `caption`) to null

## Limitations

These SAIL Testing checks cover what can be verified by inspecting component parameters. They do NOT cover:

- **Color contrast** — requires visual rendering and color analysis tooling
- **Target size** (24x24px minimum) — requires DOM measurement
- **Keyboard navigation order** — requires runtime keyboard testing
- **Screen reader announcements** — requires assistive technology testing
- **Visual inspection items** — placeholder text usage, focus visibility, content reflow at 200%/400% zoom

For complete WCAG 2.2 compliance, these programmatic checks must be supplemented with manual testing. See `accessibility-reference.md` for the full checklist including manual testing categories.

## Reference: Accessibility Checklist

The full accessibility checklist including manual testing categories is available in `accessibility-reference.md`.
