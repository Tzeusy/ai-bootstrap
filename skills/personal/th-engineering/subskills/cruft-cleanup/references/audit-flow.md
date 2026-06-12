# Cruft Cleanup Audit Flow

Use this reference when applying the skill to a real refactor, rename, or migration.

## Quick Audit Flow

1. Read the diff and list every renamed, moved, or replaced interface.
2. Grep for old names, module paths, flags, config keys, and env vars.
3. Delete aliases, wrappers, re-exports, fallback branches, and tombstones.
4. Update all callsites and tests to the new interface.
5. Re-grep to confirm the old interface is gone.

## Review Checklist

- [ ] No re-exports, aliases, or type aliases mapping old names to new names
- [ ] No old module paths that only re-export from the new location
- [ ] No feature flags or conditionals guarding fully migrated paths
- [ ] No wrapper functions whose only purpose is signature translation
- [ ] No tombstone comments such as `removed`, `deprecated`, `legacy`, or `TODO: delete after migration`
- [ ] No unused `_var` assignments kept "in case something imports them"
- [ ] No try/except or fallback blocks catching errors from removed code paths
- [ ] No default parameter values kept only to match an old interface
- [ ] No dead config keys, env vars, or CLI flags for removed modes
- [ ] All tests exercise the new interface directly
- [ ] Imports across the codebase use the new module or function names

## Applying The Skill

### Proactive

When you are writing the refactor:

- Update every same-repo consumer in the same change.
- Treat the urge to add a compatibility shim as a signal to grep and update callers instead.
- If updating all callers makes the change too large, split the work by component boundary, not into "migrate now, clean up later."

### Reactive

When you are reviewing an existing change:

1. Read the diff for every renamed, moved, or restructured interface.
2. Grep for every remaining reference to the pre-refactor interface.
3. Migrate or delete each reference.
4. Run the relevant verification so tests use the new interface.
5. Re-grep until the old references are gone.
