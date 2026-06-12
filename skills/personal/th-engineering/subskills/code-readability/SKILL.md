---
name: code-readability
description: >
  Use when judging or improving how readable and maintainable code is — naming, function
  shape, abstraction altitude, comment discipline, and simplicity-over-cleverness — in a
  diff, module, or review, especially when code works but is hard to follow.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
---

# Code Readability

Code is read far more often than it is written. This subskill judges whether a
future reader — human or agent, without the author present — can reconstruct
intent, predict behavior, and change the code safely.

## Use This Skill When

- Reviewing a diff or module for clarity, naming, or structure
- A working implementation "feels dense" and needs simplification before merge
- Deciding whether an abstraction earns its keep
- Asked "is this readable", "simplify this", "review naming and structure"

## Do Not Use This Skill For

- Correctness or test review — [test-rigor](../test-rigor/SKILL.md)
- Leftover compatibility shims — [cruft-cleanup](../cruft-cleanup/SKILL.md)
- Module boundaries and import structure —
  [dependency-hygiene](../dependency-hygiene/SKILL.md)
- Pure formatting that a linter/formatter already owns

## Core Rule

**Optimize for the reader's first pass.** If understanding a unit requires
jumping files, holding hidden state in your head, or decoding a clever trick,
the code is wrong even when it works. Simplicity needs no justification;
cleverness does.

## The Bar

Reviewable expectations — cite the one violated, with file:line evidence:

1. **Names state intent, at the right altitude** — A name says what the thing
   means in the domain, not how it is computed (`overdue_invoices`, not
   `filtered_list2`). One concept gets one name across the codebase; renaming
   half the occurrences is worse than not renaming.
2. **Functions do one thing at one altitude** — A function body mixes
   abstraction levels (business policy next to byte-twiddling) only with
   strong justification. Extract when a block needs a comment to say what it
   does; inline when an indirection exists only to be called once and hides
   the flow.
3. **Control flow is followable top-to-bottom** — Early returns over nested
   conditionals. No action-at-a-distance: a reader should not need to know
   about a decorator, hook, or global to predict what a call does.
4. **Abstractions earn their keep** — An interface, base class, generic
   parameter, or config knob with one real implementation/value is
   speculation, not design. Duplicate twice before abstracting once; the
   third occurrence reveals the real shape.
5. **Comments state constraints, not narration** — A comment says what the
   code cannot: the invariant, the external quirk, the why-not-the-obvious-way.
   Comments that restate the next line, or that talk to a reviewer about the
   change ("updated to fix…"), get deleted.
6. **Consistency beats local preference** — Match the surrounding file's
   idiom, naming style, and comment density even when you'd choose otherwise
   in a vacuum. A diff that switches styles mid-module adds permanent
   reading cost for transient taste.
7. **State is scoped as tightly as possible** — Mutable state lives in the
   narrowest scope that works; data flows through parameters and return
   values, not through fields or globals reached around the call graph.

## Workflow

1. Read the change as a stranger: top of the diff to the bottom, no author
   context. Note every place you had to stop, re-read, or jump.
2. For each stall point, name the violated expectation (1–7 above) and draft
   the minimal fix — rename, extract, inline, delete the comment, hoist the
   early return.
3. Prefer fixes that shrink the diff's concept count over fixes that add
   structure. Deleting an abstraction is usually a better outcome than
   documenting it.
4. Apply in-scope fixes directly; report only what genuinely needs the
   author's intent to resolve.
5. Re-read the result end-to-end once — readability fixes can themselves
   introduce stall points.

## Trigger Sanity Check

- Should trigger: "This works but I had to read it three times — tighten it up."
- Should not trigger: "Run the formatter" or "find the bug in this function."
