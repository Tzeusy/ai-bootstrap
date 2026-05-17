# Review Checklist

Use this reference when updating or approving a skill package.

## Update Discipline

When updating a skill:

1. Read the current `SKILL.md`, `agents/openai.yaml`, and any referenced helper
   files before editing.
2. Remove stale guidance instead of only appending new text.
3. Re-check trigger wording, related-skill references, metadata, and
   compatibility notes.
4. Verify that referenced files, commands, and paths still exist.
5. Keep examples, scripts, and UI metadata synchronized with the revised skill.
6. For superskills, keep the router and every internal subskill aligned.

## Verification Before Calling It Done

- Test the skill against at least one realistic "should trigger" case.
- If scope is subtle, test one "should not trigger" case too.
- For updates, verify the revised skill still matches the package layout and
  referenced files.
- For superskills, test router selection against at least one matching subskill
  and one no-fit or router-only case.
- If the skill contains executable helpers, verify the documented invocation is
  still correct.

## Recommended Pre-Ship Checklist

1. Is the description about activation, not workflow summary?
2. Is the skill grounded in the right source of truth?
3. Does `SKILL.md` route well, or should more content fan out into
   `references/` or `scripts/`?
4. If the skill is broad, should it become a superskill with internal
   subskills instead of a monolith or many global skills?
5. Should any repeated or fragile workflow be turned into a standardized
   script?
6. Are metadata, authorship, and compatibility fields clear and factual?
7. Are related files and `agents/openai.yaml` aligned with the current skill?
8. Does the skill define boundaries, prerequisites, and failure modes?
9. Would another agent find this skill from the way a real user asks for help?

## Anti-Patterns

- Bloated `SKILL.md` files that duplicate reference docs
- Treating progressive discovery as optional instead of as the default design
  pattern
- Re-explaining the same complex workflow in prose instead of encapsulating it
  in a reusable script
- Descriptions that summarize the process instead of describing triggers
- Broad router skills that flatten internal subskills into the global catalog
- Project-specific rules invented without checking project-shape docs
- Skills with no accountable owner or review date
- Stale references, dead scripts, or mismatched `agents/openai.yaml`
- Session stories disguised as reusable guidance
