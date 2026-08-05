"""Committed baseline for the skill-prose command ratchet in test_skill_command_ratchet.py.

WHAT IS COUNTED
---------------
COUNTS holds one entry per markdown file sitting directly inside a skill directory --
iadc-advisor/skills/<skill>/*.md. Every entry is present, including the zeros, because the guard
compares this set against the tree on every run and a discovered file with no entry is a failure
rather than a skip.

The counter, in test_skill_command_ratchet.py, works in four steps:

1. Collect every code span. Three kinds, matching the three ways markdown carries code: one span
   per non-blank line of a fenced block, one per non-blank line of an indented code block, and
   one per backtick-delimited inline span in the prose around them.
2. Strip a leading "$ " or "> " prompt, then split on &&, ||, | and ; outside quotes, so a
   pipeline counts once per stage and appending one is not free.
3. Keep a segment only if it has two or more whitespace-separated tokens -- a lone word in
   backticks is a name, not an invocation -- and its first token matches one of four recognised
   head shapes: an explicit relative script path (./...); a bare lowercase program name
   ([a-z][a-z0-9+-]*); any token carrying a path separator or an assignment (bin/jira,
   /usr/bin/grep, .venv/bin/python, VAR=value); or a hyphen- or underscore-joined identifier of
   any case (Get-Content, TEST_BROWSER).
4. A relative script path counts on sight. Every other recognised head goes to LEXICON, which
   decides. Nothing recognised is discarded without one or the other happening to it.

The method is deterministic: it reads bytes and nothing else. No PATH lookup, no shell, no clock,
so the same file yields the same number on any machine.

LEXICON classifies every head the counter meets in this tree that is not a ./ path. It is checked
against the tree on every run, and a head with no entry fails the suite. That is what keeps it
from rotting: a verb nobody anticipated cannot be silently counted as zero, it has to be
classified deliberately. True means the token names something a shell executes -- a program, a
builtin, a shell assignment, or a git subcommand written without its "git" prefix, which this
repo's prose does often. False means it merely looks like one: a mermaid keyword, a JQL clause,
an API operation named in a table, a line of an output template, or a fragment of an English
sentence someone wrapped in backticks. Entries for tokens no longer on disk are harmless; the
printer drops them.

A slash-command skill invocation (`/iadc-advisor:reconcile <TICKET-KEY>`) is classified False.
It is not a shell command, and delegating to a skill is the move family ADR 0011 asks for rather
than the one it discourages -- counting it would put a cost on the right answer.

WHAT IS OUT OF SCOPE, ALL OF IT DELIBERATE
------------------------------------------
Four boundaries. Each is a place command prose could be put without moving a number, and each is
named here rather than left to be discovered:

- **Subdirectories.** references/ under skills/appian/ and skills/to-diagram/ holds bundled
  reference material -- Appian SAIL samples and mermaid diagram syntax -- whose code blocks are
  not shell commands and would swamp the signal by roughly six hundred segments.
- **Files that are not .md.** A skill directory also holds licences, JSON templates and scripts.
  Those are data and code, not prose a model reads as instructions, so they are not counted --
  but a .txt full of commands beside a SKILL.md would not be seen either.
- **Commands written as running prose.** The counter reads code spans. A command in an ordinary
  sentence with no backticks around it has never been counted, at any indentation. This includes
  a line indented under a list item, which CommonMark renders as continuation text rather than as
  a code block; only a line indented four columns past its list item's own content column is code.
- **Head shapes outside the four above.** A head led by punctuation (`#`, `--flag`, `<x>`) or a
  plain capitalised word with no separator in it (`Test site URL`) is not read as an invocation at
  all. Neither form appears as a real command anywhere in this tree today, and admitting them
  would pull in several dozen table cells and output-template lines that are not commands.

WHAT THE NUMBER MEANS, AND WHAT IT DOES NOT
-------------------------------------------
It is a proxy, and it should be read as one. It counts commands, not judgment, so it is wrong in
both directions. Prose walking a model through a decision no subprocess can make -- asking a
person for consent, choosing between documentation tiers -- counts exactly the same as prose
reimplementing a script that already exists, and family ADR 0011 says those two are not alike at
all. A file can also carry a great deal of untestable procedural prose and score zero, because
none of it is written as a command. A count that rises is a reason to read the diff, not a verdict
on it; a count that stays flat is not a certificate.

What the ratchet does buy is that the number cannot move without someone editing this file, in the
same commit, in view of a reviewer.

ONE AXIS, DELIBERATELY
----------------------
Command density is the only thing counted here. A second axis was weighed and left out: counting
whole-file substring assertions in the test suite -- `literal in path.read_text()` -- which stay
green while the specific rule they name is broken, because some other line in the file satisfies
the substring. Such assertions are countable; an AST walk finds them. What disqualifies them is
direction, and direction is the whole of what a ratchet reads.

Command density moves with the thing being guarded: command prose grows, the number grows. A
substring-assertion count would move with unrelated test growth and unrelated test deletion, so a
rise could mean the suite got weaker or that somebody added forty sound assertions, and a fall
could mean the assertions were repaired or that a module was deleted. The sound form and the
defective form are also syntactically identical -- `token in text` is right when the token occurs
once and the assertion is anchored to that occurrence, and empty when four other occurrences
satisfy it -- so no threshold separates them either. A ratchet over such a number would report a
bar that is not being held, which is worse than no number, because it reads like one.

What finds such an assertion is breaking the rule it names and watching whether it notices. That
is not a count and does not belong in a ratchet.

UPDATING
--------
`python3 tests/test_skill_command_ratchet.py` prints COUNTS as the working tree yields it, in the
form below, and names any token still needing a LEXICON entry and any entry that has gone stale.
A count that moved in either direction fails:

- Up: command prose grew. Invoke a script instead. If the prose really is irreducible under family
  ADR 0011's five conditions, raise the number here in the same commit and say in the message which
  condition it fails.
- Down: a conversion landed. Lower the number here in the same commit, so the bar stays where the
  conversion put it instead of leaving headroom for the prose to come back.
"""
from __future__ import annotations

COUNTS: dict[str, int] = {
    "iadc-advisor/skills/appian/SKILL.md": 14,
    "iadc-advisor/skills/context7/SKILL.md": 0,
    "iadc-advisor/skills/domain-modeling/ADR-FORMAT.md": 0,
    "iadc-advisor/skills/domain-modeling/CONTEXT-FORMAT.md": 0,
    "iadc-advisor/skills/domain-modeling/SKILL.md": 0,
    "iadc-advisor/skills/handoff/SKILL.md": 0,
    "iadc-advisor/skills/interrogate-me/SKILL.md": 0,
    "iadc-advisor/skills/interrogate-with-docs/SKILL.md": 0,
    "iadc-advisor/skills/interrogating/SKILL.md": 0,
    "iadc-advisor/skills/jira/SKILL.md": 0,
    "iadc-advisor/skills/office/SKILL.md": 0,
    "iadc-advisor/skills/orient/SKILL.md": 0,
    "iadc-advisor/skills/pressure-test/SKILL.md": 0,
    "iadc-advisor/skills/reconcile/SKILL.md": 0,
    "iadc-advisor/skills/research/SKILL.md": 0,
    "iadc-advisor/skills/setup/SKILL.md": 67,
    "iadc-advisor/skills/setup/domain.md": 0,
    "iadc-advisor/skills/setup/issue-tracker-github.md": 18,
    "iadc-advisor/skills/setup/issue-tracker-gitlab.md": 21,
    "iadc-advisor/skills/setup/issue-tracker-jira.md": 0,
    "iadc-advisor/skills/setup/issue-tracker-local.md": 0,
    "iadc-advisor/skills/setup/outputs-readme.md": 0,
    "iadc-advisor/skills/setup/project-config-template.md": 0,
    "iadc-advisor/skills/setup/triage-labels.md": 0,
    "iadc-advisor/skills/to-diagram/SKILL.md": 0,
    "iadc-advisor/skills/to-spec/SKILL.md": 0,
    "iadc-advisor/skills/to-tickets/SKILL.md": 0,
    "iadc-advisor/skills/wayfinder/SKILL.md": 0,
    "iadc-advisor/skills/which-skill/SKILL.md": 0,
}

LEXICON: dict[str, bool] = {
    "===": False,  # `=== STEP 4A VERIFICATION COMPLETE ===`, a banner in an output template
    "/blocked_by": False,  # a GitLab quick action typed into an issue comment, not a shell
    "/iadc-advisor:reconcile": False,  # a skill invocation; see the note under WHAT IS COUNTED
    "Anti-hallucination": False,  # a checklist line in an output template
    "CASE_TYPE": False,  # a mermaid entity-relationship line
    "DOC_PATH=$(jq": True,  # a shell assignment running jq
    "Non-existent": False,  # a checklist line in an output template
    'VERSION="<Appian': True,  # a shell assignment, inside a ```bash block
    "outputs/<TICKET-KEY>/<TICKET-KEY>": False,  # a file path, not an invocation
    "add": False,  # "add comment", an issue-tracker operation named in a table
    "case": False,  # shell keyword, not an invocation
    "cat-file": True,  # git subcommand written without its prefix
    "checkout": True,  # git subcommand written without its prefix
    "create": False,  # "create issue", an issue-tracker operation named in a table
    "curl": True,
    "echo": True,
    "edit": False,  # "edit issue", an issue-tracker operation named in a table
    "every": False,  # English, inside a placeholder
    "exit": True,  # shell builtin
    "flowchart": False,  # mermaid keyword
    "get": False,  # "get issue", an issue-tracker operation named in a table
    "gh": True,
    "git": True,
    "glab": True,
    "grep": True,
    "hand": False,  # "hand off", English
    "if": False,  # shell keyword, not an invocation
    "int": False,  # mermaid entity-relationship column type
    "jq": True,
    "ls-files": True,  # git subcommand written without its prefix
    "participant": False,  # mermaid keyword
    "project": False,  # a JQL clause, e.g. `project = <KEY> AND ...`
    "rows": False,  # "rows below", English
    "search": False,  # "search (JQL)", an issue-tracker operation named in a table
    "skills": False,  # English, inside a placeholder
    "skipped": False,  # English
    "standing": False,  # English, inside a placeholder
    "string": False,  # mermaid entity-relationship column type
    "subgraph": False,  # mermaid keyword
    "superseded": False,  # "superseded by ADR-NNNN", English
    "ticket": False,  # a workflow arrow, e.g. `ticket -> /iadc-advisor:pressure-test`
    "transition": False,  # "transition issue", an issue-tracker operation named in a table
}
