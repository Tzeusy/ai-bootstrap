---
name: documentation
description: >
  Use when creating, reviewing, or auditing a codebase's documentation — README and docs/
  trees, architecture/workflow diagrams, API references, formal doc sites (OpenAPI, MkDocs,
  Sphinx, ReadTheDocs) — and you need the bar for accessibility (concise synthesis,
  diagrams where structure beats prose) and accuracy over time (code-cited facts under an
  explicit maintenance contract).
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
---

# Documentation

Documentation is how a codebase stays accessible to human reviewers and
future maintainers — in a spec-driven workflow it is load-bearing, not
decoration. Its failure mode is not absence but rot: confident prose that no
longer matches the code. This subskill holds docs to two standards at once:
**accessible** (a newcomer orients in minutes) and **maintainable** (every
claim can be re-verified against the code it describes).

## Use This Skill When

- Writing or restructuring a project's README, docs/ tree, or doc site
- Reviewing whether a change's documentation is adequate and current
- Auditing existing docs for staleness, missing synthesis, or missing diagrams
- Documenting an interface's behavioral contract — side effects, statefulness,
  idempotency, failure semantics — in docstrings or endpoint descriptions
- Setting up or judging formal doc tooling output (OpenAPI, MkDocs, Sphinx,
  ReadTheDocs, docstring-generated references)

## Do Not Use This Skill For

- Project knowledge architecture — the five-pillar shape model (doctrine,
  design contracts, specs, topology, standards) belongs to `/th-projects`
  (project-shape). This subskill governs documentation *craft*: the everyday
  READMEs, guides, references, and diagrams of any repo, shaped or not.
- Skill packages (`SKILL.md` and friends) —
  [skill-standards](../skill-standards/SKILL.md)
- Code comments — [code-readability](../code-readability/SKILL.md)

## Core Rule

**Document the contract; cite the code.** Every documented fact is a claim
about the code: couple it to the location it derives from, and state it at
an altitude where only a behavior change — never a behavior-preserving
refactor — can falsify it. A future maintainer must be able to
reverse-engineer where a claim came from and check whether it is still true.
A doc that cannot be re-verified is already rotting; a doc that narrates
internals re-rots on every refactor.

## The Bar

Reviewable expectations — cite the one violated, with doc and code evidence:

1. **A concise synthesis exists and orients first** — Either the top of
   `README.md` or the introductory doc under `docs/` states, in a screenful:
   what the project does, who it is for, its goals and non-goals, and how the
   major pieces fit. A newcomer reads it before any code. Missing, buried, or
   bloated synthesis is the highest-severity documentation finding.
2. **Diagrams wherever structure beats prose** — Service/component
   architecture, the happy-path data workflow, error-handling and failure
   paths, and lifecycle/state machines each get a diagram when the project
   has meaningful structure there. Generate via
   [excalidraw-diagram](../excalidraw-diagram/SKILL.md) (commit the
   `.excalidraw` source plus rendered SVG next to the doc that embeds it);
   fall back to Mermaid when the renderer is unavailable. Diagrams obey the
   citation rule too: real component, event, and endpoint names — never
   generic boxes.
3. **Facts carry citations to interface sites** — Each claim links the
   relative code location that makes it true: a path,
   `path/to/file.py:Symbol`, or a relative repo link. Cite definition and
   interface sites — the module, the endpoint handler, the schema — never
   internal call chains or private helpers: the citation is a verification
   anchor, not an invitation to narrate internals. Prefer stable anchors
   (module/function/class names) over raw line numbers, which rot fastest.
   An uncited claim is a finding; so is a citation that no longer matches
   the code.
4. **Claims survive behavior-preserving refactors** — Docs describe the
   observable contract. If a refactor that preserves behavior would falsify
   a claim, the claim documents internals and sits at the wrong altitude:
   raise it to what callers can observe, or delete it. (The doc-side twin
   of test-rigor's "assert behavior, not implementation".)
5. **Public interfaces carry a semantics card** — Every public endpoint,
   exported function, job, or CLI command documents its behavioral contract
   in the fixed, compact vocabulary of
   [`references/interface-semantics.md`](./references/interface-semantics.md):
   side effects, state, idempotency, failure semantics, and concurrency
   where it matters. A few labeled lines adjacent to the interface
   (docstring, OpenAPI description, header comment) — not paragraphs in a
   distant prose doc. This is what makes code understandable from the
   outside without coupling docs to its internals.
6. **Docs operate under a maintenance contract** — The docs entry point
   states the contract explicitly: behavior changes update affected docs in
   the same change (engineering-bar bias 7); whoever finds a stale claim
   fixes it or marks it `STALE` with evidence — never leaves it silently;
   citations are the mechanism that makes both possible. Living catalogs
   (error lists, environment inventories, compatibility matrices) open with
   their own write-back contract, per the same principle skill-standards
   applies to stateful reference docs.
7. **Prose earns its place** — Types, names, signatures, and defaults are
   already documentation; prose states only what they cannot: semantics,
   invariants, units, the why. Every doc and section has a nameable reader
   and a question it answers — if you cannot name both, delete or merge it.
   Restating the signature in sentences is the doc-site twin of comments
   that narrate the next line.
8. **Formal doc tooling serves human readers** — OpenAPI specs, MkDocs/
   Sphinx/ReadTheDocs sites, and docstring-generated references are judged
   as prose: every exposed endpoint/module has a summary a human would
   write, descriptions explain intent and failure modes (not just types),
   and examples cover the happy path. Schema dumps, empty autogenerated
   stubs, and boilerplate padding are findings. Concise beats complete:
   document what a consumer needs, link the code for the rest.
9. **Content lives at the right distance from its subject** — Structure
   mirrors the reader's journey (orientation → how to run it → how it works,
   where the diagrams live → how to change it → reference), and placement
   follows a gradient: interface semantics sit adjacent to the interface;
   cross-cutting architecture and data flow live in `docs/` with the
   diagrams; the synthesis lives in the README. Content at the wrong
   distance rots fastest and duplicates worst — interface details in distant
   prose docs are a finding, as is any content with two homes.

## Workflow

1. **Inventory** — Locate README, docs/ tree, doc-site config (`mkdocs.yml`,
   `conf.py`, `openapi.*`), and embedded diagrams. Note what exists, what is
   generated, and what claims to be current.
2. **Check the synthesis** (bar 1) — If missing or buried, draft it first;
   it frames every other judgment. Keep it under a screenful.
3. **Map structure to diagrams** (bar 2) — List the architecture, happy-path
   data flow, and error-handling shapes the project actually has; generate
   the missing high-value diagrams via
   [excalidraw-diagram](../excalidraw-diagram/SKILL.md) and embed them where
   the prose discusses that structure.
4. **Citation and altitude audit** (bars 3–4, 6) — Sample claims (all of
   them in review scope; a representative sample in a repo audit), trace
   each to code, and label: cited-and-true, cited-but-stale, uncited, or
   wrong-altitude (a behavior-preserving refactor could falsify it). Fix
   stale and uncited claims in scope, rewrite wrong-altitude claims at
   contract level, and add the maintenance contract to the docs entry point
   if absent.
5. **Semantics-card audit** (bar 5) — List the public interfaces in scope.
   For each, check a card exists adjacent to the definition and that its
   claims (side effects, idempotency, failure behavior) match the code —
   a wrong card is worse than no card. Write missing cards from
   [`references/interface-semantics.md`](./references/interface-semantics.md).
6. **Judge the rendered output** (bars 7–9) — Read the doc site or API
   reference as its intended consumer would. Flag schema dumps,
   signature-restating prose, empty stubs, journey-breaking structure, and
   wrong-distance content; fix what is in scope.
7. **Verify** — Build the doc site if one exists (broken builds and dead
   links are findings), and re-read the synthesis end-to-end after edits.

## Trigger Sanity Check

- Should trigger: "Document this service so a reviewer can understand the
  data flow", "audit docs/ for stale claims", "our Sphinx site is a schema dump".
- Should not trigger: "Bootstrap the five-pillar knowledge architecture"
  (`/th-projects` project-shape) or "review this SKILL.md" (skill-standards).
