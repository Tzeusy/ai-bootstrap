# Quality Bar

Use this reference for the judgment-level review criteria. Run
[`scripts/audit_skill.py`](../scripts/audit_skill.py) first for the
mechanical checks (frontmatter, limits, links, PEP 723, layout); this
document covers what the script cannot decide.

## 1. Follow The Agent Skills Spec

Every skill follows the open `agentskills.io` package model
(https://agentskills.io/specification):

- `SKILL.md` begins with valid YAML frontmatter; `name` and `description`
  are required.
- Spec limits: `name` ≤ 64 chars, lowercase letters, digits, and hyphens;
  `description` ≤ 1024 chars. Optional standard fields: `license`,
  `compatibility`, client-specific `metadata`.
- The `description` is trigger-oriented. It explains when to use the skill,
  not the full workflow. Every installed skill's description is loaded into
  the catalog of every session — each character has a recurring context
  cost, so spend it on activation signals, not process summary.
- The body stays lean and acts as guidance or routing, not a giant duplicate
  of all related documentation.
- Write valid, portable YAML. Do not rely on client-specific parser quirks.
- Tool-specific adapter files (such as `agents/openai.yaml` for Codex) are
  not part of the open spec. They are optional; when present, keep them in
  sync with the `SKILL.md` description and actual purpose.

## 2. Ground Project-Specific Skills In Project Shape

If the skill is specific to one repository or product, it must align with that
project's documented source of truth.

- Read the relevant project-shape pillars first when they exist (route via
  `/th-projects`): `about/heart-and-soul/`, `about/legends-and-lore/`,
  `openspec/`, `about/lay-and-land/`, and `about/craft-and-care/`.
- Treat the skill as a navigation and execution layer over those docs, not a
  competing doctrine.
- If the skill and the project docs disagree, fix the inconsistency. Do not let
  the skill become a third truth source.
- Project-local terminology, boundaries, and quality expectations should match
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

- One skill should solve one coherent class of problems.
- The title and description should help the agent find the skill from real
  symptoms, user phrasing, and task context. Write 3–5 sample user phrasings
  that should trigger the skill and check the description against them; keep
  the samples in `SKILL.md` so future reviews can re-verify.
- Include clear "use when" boundaries and, where helpful, brief "do not use
  when" guidance.
- Check the description against sibling skills in the catalog: if two
  installed skills would both plausibly match the same phrasing, sharpen one
  or both descriptions to disambiguate.
- Avoid vague umbrella skills unless they are intentionally routing skills.

## 5. Skills Have Two Valid Shapes

Every package should be either a standard `skill` or a `superskill`.

- A `skill` follows the agentskills.io package model: one top-level
  `SKILL.md`, optional `references/`, `scripts/`, and `assets/`, and no
  internal `subskills/` tree.
- A `superskill` is a router package: one top-level `SKILL.md` plus
  `subskills/`, where each subskill follows the standard skill shape.
- **`subskills/` is a local extension, not part of the agentskills.io spec.**
  Portable consumers will ignore it; this repo's `bootstrap.sh` deliberately
  prunes `subskills/` when installing so subskill metadata never enters the
  global catalog. Treat that prune as part of the contract.
- A superskill is a top-level router whose frontmatter is the only metadata
  that should load into the global skill catalog. Internal subskills live
  under `subskills/<workflow>/SKILL.md` and are discovered lazily.
- The router should provide concise selection rules and a cheap way to inspect
  subskill frontmatter. It should not duplicate every subskill body.
- Subskills must remain independently coherent after selection: valid
  frontmatter, trigger-oriented descriptions, direct links to support files,
  and no hidden dependency on unrelated sibling content.
- Use [`superskills.md`](./superskills.md) when deciding whether a broad skill
  should become a superskill or be split into independent top-level skills.

## 6. Progressive Disclosure And Context Discipline

- Emphasize progressive discovery, not just brevity. `SKILL.md` should help the
  agent decide what to load next rather than trying to carry the whole skill in
  one file.
- Budgets: keep `SKILL.md` under ~150 lines for an ordinary skill; treat 500
  lines as a hard ceiling that forces fan-out. A reference file should cover
  one task slice so a typical task loads `SKILL.md` plus one or two support
  files, not the whole package.
- Fan heavy or domain-specific reference material into `references/`,
  deterministic helpers into `scripts/`, and output-only resources into
  `assets/`.
- A `tests/` directory for skill self-tests and fixtures is allowed and
  encouraged for skills with executable helpers; it is never loaded as agent
  context and is exempt from linking requirements.
- Link every important support file from `SKILL.md` with explicit selection
  guidance: say what question the file answers and when to load it. A bare
  link list is not a routing layer.
- Avoid deep reference chains. Important support files should usually be
  linked directly from `SKILL.md`, not discovered through multiple hops.
- Prefer several narrow supporting files over one monolithic support document
  when the subject naturally splits by task, framework, domain, or workflow
  step.

## 7. Evidence Over Generic Prose

- Skills should capture proven workflows, recurring failure modes, or durable
  repo knowledge.
- Prefer concrete heuristics, checklists, and commands over abstract advice.
  Never point at "the validator" or "the usual process" without naming the
  command or file.
- Do not write a skill as a narrative of one session.
- Do not preserve stale workaround text after the underlying problem or tooling
  has changed.

## 8. Script Repeated Or Complex Workflows

The decision rule is context economics: any procedure an agent would
otherwise re-derive in its context window each session belongs in a script.
A script invocation costs a few dozen tokens and is deterministic;
re-deriving the same workflow from prose costs thousands of tokens and
drifts. When a workflow is complex, fragile, repeated, or expensive to
reconstruct, encapsulate it.

- Well-documented scripts let future agents reuse a known-good workflow
  instead of reinventing it from scratch.
- Python is a strong default for these helpers unless another language is
  clearly a better fit for the environment.
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
- Scripts should include a short purpose statement, clear usage examples, and
  stable flags so agents can invoke them correctly without rereading large
  docs. Link each script from `SKILL.md` (or the relevant reference) with a
  one-line statement of when to run it.

## 9. Safe And Explicit Operational Boundaries

- State prerequisites, destructive edges, and hard stops clearly.
- Fail closed when the environment is missing required tools, auth, or context.
- Do not hide risky actions inside broad workflow language.
- Do not create misleading or surprise behavior relative to the skill's stated
  purpose.
