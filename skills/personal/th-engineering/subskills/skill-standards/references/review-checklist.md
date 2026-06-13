# Review Checklist

Procedure for updating or approving a skill package. Criteria live in
[`quality-bar.md`](./quality-bar.md); this file is steps only.

## Step 1: Mechanical Audit

```bash
uv run <skill-standards>/scripts/audit_skill.py <target-skill-dir>
# add --strict to fail on warnings, --stale-days N to tune the review-age check
# batch/CI: --all <skills-root> [--skip NAME] [--json]
```

CI runs the same audit over `skills/personal/` in `--strict` mode on every
push and PR (`.github/workflows/skill-audit.yml`) — errors AND warnings
block. The tree is warning-free; a change introducing either does not merge.
Links inside fenced code blocks are treated as illustrative examples and
ignored — fence your templates.

- Fix every ERROR: invalid/missing frontmatter, spec-limit violations,
  placeholder descriptions, broken links, missing routing-table entries,
  invalid adapter YAML, and Python scripts without PEP 723 inline metadata.
- PEP 723 errors in the target skill are in scope for the current change:
  add the `# /// script` block to each flagged script now (quality-bar
  section 8 has the required header); do not defer.
- Triage every WARN: fix it or state why it stays.

## Step 2: Judgment Review

Against [`quality-bar.md`](./quality-bar.md), answer:

1. Is the description about activation, not workflow summary? Does it match
   3–5 realistic user phrasings, and do those samples live in `SKILL.md`?
2. Would the description collide with a sibling skill in the catalog?
3. Is the skill grounded in the right source of truth (project-shape docs
   for project-specific skills)?
4. Does `SKILL.md` route well — does every support-file link say what
   question it answers and when to load it?
5. If the skill is broad, should it become a superskill (see
   [`superskills.md`](./superskills.md)) instead of a monolith or many
   global skills?
6. Should any repeated or fragile workflow become a script instead of prose?
7. Does the skill define boundaries, prerequisites, and failure modes?
8. Does any reference doc hold living state (error catalogs, project
   inventories, compatibility matrices)? If so, does it open with a
   maintenance contract (quality-bar section 10), and does the skill's
   workflow tell agents to write back when they surface new facts?

## Step 3: Update Discipline

When changing an existing skill:

1. Read the current `SKILL.md`, any tool adapter files, and referenced helper
   files before editing.
2. Tighten trigger wording before expanding workflow prose.
3. Remove stale guidance instead of only appending new text.
4. Keep examples, scripts, and adapter metadata synchronized with the revised
   skill.
5. For superskills, keep the router table and every subskill aligned.

## Step 4: Verification Before Calling It Done

- Re-run `audit_skill.py` on the final package; it must PASS.
- Check the description against the skill's sample trigger phrasings; if scope
  is subtle, also check one phrasing that should NOT trigger it.
- For superskills, walk the routing table against one matching-subskill case
  and one no-fit or router-only case.
- If the skill has executable helpers, run each documented invocation (at
  minimum `--help`) and confirm it works via `uv run`.

## Anti-Patterns

- Bloated `SKILL.md` files that duplicate reference docs
- Treating progressive discovery as optional instead of as the default design
  pattern
- Re-explaining the same complex workflow in prose instead of encapsulating it
  in a reusable script
- Python helper scripts without PEP 723 inline metadata, or runnable only in
  one machine's environment
- Descriptions that summarize the process instead of describing triggers
- Broad router skills that flatten internal subskills into the global catalog
- Project-specific rules invented without checking project-shape docs
- Skills with no accountable owner or review date
- Stale references, dead scripts, or mismatched tool adapter files
- Stateful catalogs without a write-back maintenance contract, so entries rot
  silently
- Session stories disguised as reusable guidance
