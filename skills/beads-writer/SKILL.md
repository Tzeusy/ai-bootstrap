---
name: beads-writer
description: This skill should be used when writing beads issues (bd create) for a project. It guides research, decomposition, and crafting of well-structured, actionable beads with proper fields, dependencies, and acceptance criteria. Use when the user asks to create issues, plan work, break down a feature, write bugs, or populate a backlog.
---

# Beads Writer

## Overview

This skill produces high-quality beads issues through structured research and deliberate field selection. Rather than firing off a quick `bd create` with just a title, follow the workflow below to produce issues that are immediately actionable, properly scoped, and well-connected to existing work.

## When to Use This Skill

- A user asks to create one or more beads issues for a piece of work
- A user describes a feature, bug, or task and wants it captured as beads
- A user wants to break down a large ask into an epic with children
- A user wants to populate or groom a backlog
- A discovered issue needs to be written up properly (not just a quick `bd create`)

## Research-First Workflow

### Phase 1: Understand the Ask

Before writing any bead, gather enough context to write it well:

1. **Clarify scope** — Ask the user what outcome they want. A vague ask ("improve auth") produces vague issues. Push for specifics: what should change, for whom, and why.
2. **Survey the codebase** — Read relevant source files to understand current behavior, naming conventions, and architecture. Issues grounded in the actual code are more actionable.
3. **Check existing issues** — Run `bd list --status open` and `bd search "<keywords>"` to find related or duplicate work. Link rather than duplicate.
4. **Identify dependencies** — Determine what blocks this work or what this work blocks. Check `bd blocked` for context.

### Phase 2: Decompose

Decide the right granularity:

| Signal | Action |
|--------|--------|
| Work can be done in a single focused session | Write one issue |
| Work has 2-5 distinct deliverables | Write separate issues, optionally under an epic |
| Work spans multiple components or >1 day | Write an epic with children |
| Work touches an area with existing open issues | Link via dependencies, don't re-scope existing issues |

**Single-responsibility rule**: Each issue should produce one testable outcome. If the acceptance criteria contain unrelated items, split the issue.

#### Per-Bead Overhead Budget

Every sub-bead carries fixed costs that are invisible at planning time but compound fast:

- **Worktree creation & teardown** — isolated git worktree per worker
- **CI/CD pipeline run** — lint, build, test suite per branch/PR
- **PR creation & review cycle** — reviewer agent context-load, comment round-trips
- **Context switching** — each bead requires the worker to re-orient in the codebase
- **Merge coordination** — rebase/conflict resolution grows with concurrent branches

These costs mean 10 trivial one-liner beads is significantly more expensive than 3 focused beads that cover the same work. Conversely, a single mega-bead that touches 15 files across 4 subsystems is unreviewable and un-revertable.

**Target sweet spot: 3-7 children per epic.** Each child should represent a coherent unit of work that:
- Takes a worker 30-120 minutes of focused implementation
- Touches a bounded set of files (ideally ≤8-10 files)
- Produces a PR that a reviewer can evaluate in one pass (≤300 lines changed)
- Has a clear "done" signal without requiring cross-bead coordination

**When tempted to split further**, ask: "Does this split reduce review complexity, or just create more reviews?" If a bead is small but tightly coupled to a sibling (e.g., "add field to model" + "add field to serializer"), merge them — the overhead of two PRs outweighs the cleanliness of separation.

**When tempted to merge**, ask: "Can a reviewer hold the full diff in their head?" If the bead requires scrolling through unrelated changes to review, split it.

**Epic reconciliation rule**: Every epic **must** end with a final child bead for spec-to-code reconciliation (gen-1). This bead is created last (after all implementation children) and ensures nothing from the original spec was missed. If gaps are found, the reconciliation bead creates fix beads and a gen-2 follow-up reconciliation (up to gen-3 max). See Phase 3 → Reconciliation Bead for the template.

### Phase 3: Craft Each Issue

For each issue, fill fields deliberately. Consult `references/fields-and-examples.md` for the full field schema, type selection guide, priority calibration, and exemplary beads.

#### Title (required)
- Imperative verb-first: "Add", "Fix", "Upgrade", "Remove", "Refactor"
- Specific enough to understand without reading the description
- Under 72 characters
- Bad: "Auth stuff" / Good: "Add JWT refresh token rotation on expiry"

#### Type (required)
Select based on the nature of the work:
- `task` — general implementation work
- `bug` — broken behavior that needs fixing
- `feature` — new user-facing capability
- `chore` — maintenance, upgrades, cleanup
- `epic` — umbrella for multiple related issues

#### Priority (required)
Use the numeric scale 0-4. Never use words like "high" or "low". Default to P2 unless there's a clear reason to deviate. Refer to the priority calibration table in the reference doc.

#### Description (required for non-trivial issues)
Structure the description to answer:
- **What** needs to change
- **Why** it matters (impact, user pain, technical debt)
- **Context** that a developer picking this up would need

For bugs, include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (browser, OS, version) when relevant

For features, include:
- The user problem being solved
- Any constraints or non-goals

Avoid prescribing implementation details in the description — that belongs in the `design` field.

#### Acceptance Criteria (recommended)
Write testable, enumerated conditions:
```
1. API responds in <200ms for 10k records
2. Error response follows RFC 7807 format
3. Existing clients without pagination params still work
```

Avoid vague criteria like "works correctly" or "is fast enough."

#### Design (when the approach matters)
Use for architectural decisions, API contracts, data model changes, or algorithm choices. Keep it concise — link to external docs for lengthy designs.

#### Notes (optional)
Implementation hints, relevant links, caveats, prior art. Not for the "what" — for the "by the way."

#### Labels
Tag by component and concern. Reuse existing labels (check `bd label list`). Avoid one-off labels.

#### Dependencies
- `--parent <epic-id>` for hierarchical children
- Use `bd dep add <issue> <depends-on>` after creation for dependency wiring
- **Do NOT use `--deps discovered-from:<id>` or `--deps blocks:<id>` in
  `bd create`** — these flags can cause a SIGSEGV panic in the beads CLI.
  Create the bead first, then add dependencies separately with `bd dep add`.

#### Estimate (when useful)
Minutes of focused implementation time. Helps with planning but don't over-invest in accuracy — round to 30/60/120/240.

#### Reconciliation Bead (required for epics)

Every epic **must** include a final child bead that performs a deep-dive spec-to-code reconciliation review. This bead is always created **last**, after all implementation children, and depends on all of them.

**Purpose**: Verify that every requirement from the original spec/feature request has been addressed by the implementation beads. If any features, edge cases, or acceptance criteria were missed, this bead's executor must investigate the gap and create new implementation/fix child beads under the same epic to cover the missing work.

**Template**:
- **Title**: `Reconcile spec-to-code coverage for <epic summary>`
- **Type**: `task`
- **Priority**: Same as the epic
- **Description**:
  ```
  Deep-dive review: compare the original spec/requirements (see epic description)
  against the implementation delivered by sibling beads under this epic.

  Workflow:
  1. Re-read the epic description and all sibling bead descriptions/acceptance criteria.
  2. Audit the codebase changes delivered by each sibling bead.
  3. Produce a checklist mapping every spec requirement to its implementing bead.
  4. For any requirement NOT covered (or only partially covered):
     a. Create a new child bead under this epic describing the missing work.
     b. Set appropriate priority and link dependencies.
  5. If gap beads were created in step 4, create a follow-up reconciliation bead
     (gen-2) that depends on ALL the new gap beads. The gen-2 bead re-runs this
     same workflow to catch anything still missing after the gaps are filled.
     - A gen-2 reconciliation bead may spawn one final gen-3 reconciliation bead
       using the same pattern. Gen-3 is the hard limit — it must NOT spawn further
       reconciliation beads.
     - Tag the title with generation: "Reconcile spec-to-code (gen-N) for ..."
  6. Keep this reconciliation bead open (or blocked) until all newly created
     gap beads (and any follow-up reconciliation bead) are closed.
  7. Re-run the requirement-to-bead checklist and close this bead only when all
     requirements show full coverage.
  ```
- **Acceptance Criteria**:
  ```
  1. Every requirement in the epic spec has a corresponding implementation bead
  2. Any gaps found result in new child beads created under the same epic
  3. If gaps were found, a follow-up reconciliation bead (next gen) was created
  4. Reconciliation summary is recorded in the close reason
  ```
- **Dependencies**: Add dependencies from the reconciliation bead to all other children (`bd dep add <recon-id> <child-id>`) so it runs last.

### Phase 4: Pre-Flight — Verify Dolt DB

Before creating any beads, confirm the Dolt backend is healthy:

1. **Check DB health**: `bd doctor` to verify the database is in good shape before large issue-creation batches.
2. **Quick check**: `bd vc status` should show no unresolved conflicts.
3. **Branch hygiene**: `.beads/` is gitignored; it should never appear in code branch diffs.

### Phase 5: Create

Use `bd create` with all relevant flags. For multiple issues:
- Create in dependency order (parents/blockers first)
- Use `bd create --json` and parse the `id` field to capture IDs for subsequent `--parent` or `bd dep add` calls
- **Do NOT use `bd q` with `-d`/`--description`** — `bd q` is a quick-create command with a limited flag set (only `-t`, `-p`, `-l`). Always use `bd create` when a description is needed.
- Confirm DB health with `bd doctor` after creation

**Rig routing:** `bd create` targets whichever `.beads/` DB is discovered from
`$PWD`. If you're running from outside the target project (e.g., from the mayor
or town root), you **must** pass `--rig <rig>` to file the bead in the correct
project database. Similarly, use `--rig` on `bd list` and `bd ready` when
querying a different rig. Commands that accept an existing bead ID (`bd update`,
`bd close`, `bd dep add`) auto-route via the ID prefix and do not need `--rig`.
**Note:** `bd search`, `bd blocked`, `bd count`, and `bd query` do **not**
support `--rig`. To search cross-rig, use `bd list --rig <rig>` with filters
or `cd` into the rig's workspace directory first.

**Efficient bulk creation pattern:**
```bash
# Epic first — capture ID from JSON output
EPIC=$(bd create --title="User authentication system" --type=epic --priority=1 \
  --description="Replace session-cookie auth with JWT-based authentication." \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Children (create sequentially to capture IDs for dependencies)
HASH_ID=$(bd create --title="Implement password hashing" --type=task --priority=1 --parent=$EPIC \
  --description="Replace bcrypt with Argon2id. Lazy migration on login." \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

JWT_ID=$(bd create --title="Add JWT middleware" --type=task --priority=1 --parent=$EPIC \
  --description="RS256-signed JWTs. Access 15min, refresh 7d." \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

bd create --title="Build login UI" --type=task --priority=2 --parent=$EPIC \
  --description="Update login form for JWT flow. Silent token refresh."

bd create --title="Write auth integration tests" --type=task --priority=2 --parent=$EPIC \
  --description="E2E tests: login, refresh, expiry, migration."

# Add cross-dependencies (NEVER use --deps flags in bd create — use bd dep add)
bd dep add $JWT_ID $HASH_ID

# ALWAYS end an epic with a reconciliation bead (depends on all siblings)
RECON_ID=$(bd create --title="Reconcile spec-to-code coverage for auth system" --type=task --priority=1 --parent=$EPIC \
  --description="Deep-dive review: compare the original spec/requirements (see epic description) against the implementation delivered by sibling beads. Audit codebase changes, produce a checklist mapping every spec requirement to its implementing bead. For any requirement NOT covered, create new child beads under this epic. If all covered, close with a coverage summary." \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Reconciliation bead depends on all implementation children
bd dep add $RECON_ID $HASH_ID
bd dep add $RECON_ID $JWT_ID
# ... add dep for every other child
```

### Phase 6: Verify

After creating issues, verify quality:

1. **Run `bd show <id>`** for each issue — confirm all fields rendered correctly
2. **Run `bd dep tree <epic-id>`** for epics — confirm dependency graph is correct
3. **Run `bd ready`** — confirm the right issues are unblocked
4. **Run `bd lint`** — check for missing template sections
5. **For each new epic** — confirm there is exactly one terminal reconciliation child and it depends on every other child

Present the created issues to the user for review. Include the ID, title, type, and priority of each.

## Quality Checklist

Before finalizing any bead, verify:

- [ ] Title is imperative, specific, and <72 characters
- [ ] Type matches the nature of the work
- [ ] Priority is calibrated (not everything is P0)
- [ ] Description answers what, why, and context
- [ ] Acceptance criteria are testable and enumerated
- [ ] No duplicate of existing open issues
- [ ] Dependencies are linked (parent, blocks, discovered-from)
- [ ] Labels use existing taxonomy (not one-off tags)
- [ ] Single responsibility — one testable outcome per issue
- [ ] Epics include a final reconciliation bead that depends on all siblings
- [ ] Reconciliation beads include generation tag (gen-1/gen-2/gen-3) and never exceed gen-3

## 🚨 MANDATORY: Persist Beads at Session End

**You MUST persist beads changes after creating or modifying any beads.** This is non-negotiable.

Beads data is persisted in the Dolt database (`.beads/dolt/`). Writes go directly to Dolt via the auto-started sql-server. No manual file commits are needed.

### Required checks

```bash
# 1) Optionally push Dolt commits to a remote (if configured)
bd dolt push
```

If checks fail, run `bd doctor --fix --yes` and fix the persistence path before ending the session.

## Common Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Vague title ("Fix stuff") | Be specific ("Fix login timeout on mobile Safari") |
| Missing description | Always explain what and why |
| Everything is P0 | Calibrate against the priority table |
| Mega-issue with 10 acceptance criteria | Split into focused children under an epic |
| Prescribing implementation in description | Move to `design` field |
| Orphaned issues (no links) | Use `discovered-from`, `parent`, or `blocks` |
| Duplicate of existing issue | Search first with `bd search` and `bd list` |
| Using "high"/"medium"/"low" for priority | Use numeric 0-4 only |
| Too many tiny sub-beads (>7 per epic) | Merge tightly-coupled work; each bead should be 30-120 min of focused work |
| Epic without reconciliation bead | Always add a final spec-to-code reconciliation child |
| Reconciliation bead exceeds gen-3 | Gen-3 is the hard limit; close with remaining gaps documented |

## Resources

### references/
- `fields-and-examples.md` — Complete field schema, type selection guide, priority calibration table, and exemplary beads for every issue type. Read this when crafting issues to ensure proper field usage.
