# Quality Bar

Judgment-level review criteria. Run
[`scripts/audit_skill.py`](../scripts/audit_skill.py) first for mechanical
checks (frontmatter, limits, links, PEP 723, layout); this document covers
what the script cannot decide.

## 1. Follow The Agent Skills Spec

Every skill follows the open `agentskills.io` package model
(https://agentskills.io/specification):

- `SKILL.md` begins with valid YAML frontmatter; `name` and `description`
  required.
- Spec limits: `name` ≤ 64 chars, lowercase letters, digits, hyphens;
  `description` ≤ 1024 chars. Optional standard fields: `license`,
  `compatibility`, client-specific `metadata`.
- The `description` is trigger-oriented: when to use the skill, not the full
  workflow. Every installed skill's description loads into every session's
  catalog — each character has a recurring context cost, so spend it on
  activation signals, not process summary.
- The body stays lean — guidance or routing, not a giant duplicate of all
  related documentation.
- Write valid, portable YAML. Do not rely on client-specific parser quirks.
- Tool-specific adapter files (such as `agents/openai.yaml` for Codex) are
  not part of the open spec. They are optional; when present, keep them in
  sync with the `SKILL.md` description and actual purpose.

## 2. Ground Project-Specific Skills In Project Shape

A skill specific to one repository or product must align with that project's
documented source of truth.

- Read the relevant project-shape pillars first when they exist (route via
  `/th-projects`): `about/heart-and-soul/`, `about/legends-and-lore/`,
  `openspec/`, `about/lay-and-land/`, and `about/craft-and-care/`.
- Treat the skill as a navigation and execution layer over those docs, not a
  competing doctrine.
- If the skill and project docs disagree, fix the inconsistency. Do not let
  the skill become a third truth source.
- Project-local terminology, boundaries, and quality expectations must match
  the project's own shape docs exactly.

## 3. Require Clear Metadata And Authorship

Every skill should make ownership obvious.

- Required loader metadata: `name`, `description`
- Recommended local metadata:
  - `metadata.owner`: accountable human owner
  - `metadata.authors`: who authored or substantially revised it
  - `metadata.status`: `active`, `draft`, or `deprecated`
  - `metadata.last_reviewed`: last substantive review date (ISO `YYYY-MM-DD`)
- Add `compatibility` only when runtime requirements or environment assumptions
  materially affect use.

## 4. Sharp Scope And Trigger Quality

- One skill solves one coherent class of problems.
- Title and description should help the agent find the skill from real
  symptoms, user phrasing, and task context. Check it against realistic
  positive, negative, and ambiguous phrasings. Keep examples out of runtime
  prose when unloaded eval data can preserve them.
- Include clear "use when" boundaries and, where helpful, brief "do not use
  when" guidance.
- Check the description against sibling skills in the catalog: if two
  installed skills would both plausibly match the same phrasing, sharpen one
  or both to disambiguate.
- Avoid vague umbrella skills unless they are intentionally routing skills.

## 5. Skills Have Two Valid Shapes

Every package is either a standard `skill` or a `superskill`.

- A `skill` follows the agentskills.io package model: one top-level
  `SKILL.md`, optional `references/`, `scripts/`, and `assets/`, no internal
  `subskills/` tree.
- A `superskill` is a router package: one top-level `SKILL.md` plus
  `subskills/`, where each subskill follows the standard skill shape.
- **`subskills/` is a local extension, not part of the agentskills.io spec.**
  Portable consumers ignore it; this repo's `bootstrap.sh` deliberately prunes
  `subskills/` when installing so subskill metadata never enters the global
  catalog. Treat that prune as part of the contract.
- A superskill is a top-level router whose frontmatter is the only metadata
  that should load into the global skill catalog. Internal subskills live
  under `subskills/<workflow>/SKILL.md`, discovered lazily.
- The router provides concise selection rules and a cheap way to inspect
  subskill frontmatter. It does not duplicate every subskill body.
- Subskills must stay independently coherent after selection: valid
  frontmatter, trigger-oriented descriptions, direct links to support files,
  no hidden dependency on unrelated sibling content.
- Use [`superskills.md`](./superskills.md) when deciding whether a broad skill
  should become a superskill or split into independent top-level skills.

## 6. Progressive Disclosure And Context Discipline

- Emphasize progressive discovery, not just brevity. `SKILL.md` should help
  the agent decide what to load next rather than carry the whole skill in one
  file.
- Budgets: keep `SKILL.md` under ~150 lines for an ordinary skill; treat 500
  lines as a hard ceiling that forces fan-out. A reference file covers one
  task slice so a typical task loads `SKILL.md` plus one or two support files,
  not the whole package.
- Fan heavy or domain-specific reference material into `references/`,
  deterministic helpers into `scripts/`, output-only resources into `assets/`.
- `tests/` (self-tests and fixtures) and `evals/` (trigger/eval datasets) are
  allowed and encouraged for skills with executable helpers; they never load
  as agent context and are exempt from linking requirements.
- Superskills should keep routing cases in `evals/routing.json`: schema version
  1, the router name, and cases with unique `id`, `query`, `kind`, and
  `expected_routes` containing subskill directory names. Positive cases name
  exactly one route, negative cases none, and ambiguous cases at least two.
  Cover every subskill with one positive case. The mechanical audit validates
  schema and coverage without pretending to run a model.
- Link every important support file from `SKILL.md` with explicit selection
  guidance: what question the file answers and when to load it. A bare link
  list is not a routing layer.
- Only real markdown links count as routing. Links inside fenced code blocks
  or inline code spans are illustrative examples (templates, target-project
  skeletons) and are ignored by the audit — fence your templates, and never
  rely on a fence-quoted path to make a support file discoverable.
- Avoid deep reference chains. Important support files should usually link
  directly from `SKILL.md`, not surface through multiple hops.
- Prefer several narrow support files over one monolithic document when the
  subject naturally splits by task, framework, domain, or workflow step.

## 7. Evidence Over Generic Prose

- Skills capture proven workflows, recurring failure modes, or durable repo
  knowledge.
- Prefer concrete heuristics, checklists, and commands over abstract advice.
  Never point at "the validator" or "the usual process" without naming the
  command or file.
- Do not write a skill as a narrative of one session.
- Do not preserve stale workaround text after the underlying problem or tooling
  has changed.
- Sacrifice grammar for concision. Keep every line sharp and focused on its
  core message; drop articles, connectives, and flowery phrasing when they add
  words without meaning. Terseness must not cost clarity — cut the decoration,
  never the point.

## 8. Script Repeated Or Complex Workflows

The decision rule is context economics: any procedure an agent would
otherwise re-derive in its context window each session belongs in a script.
A script invocation costs a few dozen tokens and is deterministic;
re-deriving the same workflow from prose costs thousands of tokens and
drifts. Encapsulate any workflow that is complex, fragile, repeated, or
expensive to reconstruct.

- Well-documented scripts let future agents reuse a known-good workflow
  instead of reinventing it.
- Python is a strong default for these helpers unless another language fits
  the environment better.
- **Every Python helper script MUST carry PEP 723 inline script metadata** so
  it runs environment-agnostically via `uv run`, declaring its own Python
  requirement and dependencies:

  ```python
  #!/usr/bin/env -S uv run --script
  # /// script
  # requires-python = ">=3.9"
  # dependencies = [
  #   "requests<3",
  # ]
  # ///
  ```

  Initialize or maintain the block with `uv init --script` and
  `uv add --script`; run with `uv run`. A script with no third-party
  dependencies still carries the block (empty `dependencies = []`). When
  reviewing or updating any skill, bring its non-compliant Python scripts
  into compliance as part of the change — `audit_skill.py` reports these as
  errors, not warnings. The mandate covers entry points only: library
  modules under `scripts/` (packages, `__init__.py`, helpers with no shebang
  or `__main__` guard) are exempt, since PEP 723 applies to standalone
  scripts, not importable modules.
- If reproducibility matters, use `uv lock --script` and commit the adjacent
  lockfile when the repository wants locked script environments.
- Scripts include a short purpose statement, clear usage examples, and stable
  flags so agents invoke them correctly without rereading large docs. Link
  each script from `SKILL.md` (or the relevant reference) with a one-line
  statement of when to run it.

## 9. Prescribed Commands Spend The Consumer's Tokens

Sections 1 and 6 cap what a skill costs to *load*. This section caps what a
skill costs to *follow*: every command a skill prescribes runs in the
consuming agent's context window, and a workflow executed hundreds of times
(orchestration loops, dispatched workers) multiplies every wasted byte.
Exemplar doctrine: `beads-orchestration/references/token-efficiency.md`.

- Write prescribed commands pre-projected. A command that emits structured
  output names its fields (`--json <fields>`, `| jq '{...}'`) in the skill
  text itself; never prescribe a bare `--json` dump and rely on the agent to
  cope with the flood.
- Prescribe log-file routing for verbose invocations (tests, builds,
  installs): redirect to a file, read back exit status plus the failure tail,
  never the full log.
- Verification workflows prescribe targeted iteration: run the subset covering
  the change while iterating, the full defined gate exactly once before
  completion (quiet flags). The subset never substitutes for the gate.
- Loop or polling workflows batch each cycle's checks into one composite
  command emitting a compact summary, and gate any status report on actual
  state change.
- Include execution policy only when it is a domain-specific invariant;
  baseline runtime advice does not belong in skill prose.
- Large catalogs and appendix docs are consumed grep-first: the skill tells
  the agent to `rg` the symptom and read the matching section, not to load
  the whole file (see section 11 for the write-back side).

When reviewing, read each prescribed command and ask what its output looks
like at realistic scale; a command that is fine on a toy repo may dump
thousands of lines in a real one.

## 10. Safe And Explicit Operational Boundaries

- State prerequisites, destructive edges, and hard stops clearly.
- Fail closed when the environment is missing required tools, auth, or context.
- Do not hide risky actions inside broad workflow language.
- Do not create misleading or surprise behavior relative to the skill's stated
  purpose.

## 11. Stateful Reference Docs Carry A Maintenance Contract

Some reference docs are living state, not static guidance: catalogs of known
errors or quirks, inventories of projects or environments, compatibility
matrices, theme or template registries. These rot silently unless the agents
that consume them also write back.

- Every stateful reference doc must open with an explicit **maintenance
  contract**: a short section telling the consuming agent when and how to
  update the doc during normal use. The exemplar is
  `beads-orchestration/references/known-errors.md` ("Maintenance contract
  (read this first)").
- The contract covers at least: append an entry when a new class of item
  surfaces during use (new error, new project, new quirk); update an entry
  when its facts change; remove an entry when disproved or fixed upstream —
  note the disproving evidence or version first, drop the entry one revision
  later.
- Entries follow a stable format and carry the evidence needed to trust or
  retire them later: date observed, tool version, symptom verbatim.
- Write back in the same change that surfaced the new fact, not as follow-up
  work. A skill whose workflow can surface catalog-worthy facts should say so
  in its workflow steps, not rely on agent goodwill.
- When reviewing a skill, treat a stateful reference doc with no maintenance
  contract as a finding: add the contract, or convert the doc to static
  guidance if it need not live.
