---
name: cruft-cleanup
description: >
  Use when reviewing or writing refactors, renames, or migrations where old interfaces may
  linger as aliases, re-exports, wrappers, fallback branches, deprecated flags, or other
  compatibility cruft. Especially relevant when changed code keeps both old and new paths
  alive inside the same repo.
---

# Cruft Cleanup

LLMs tend to preserve old interfaces "just in case." In same-repo refactors, that usually produces dead wrappers, aliases, and fallback paths instead of a finished migration.

When refactoring, migrating, or renaming code, leave **only the new code path** unless backward compatibility is explicitly required.

## When to Use

Use this skill when:

- A function, module, type, flag, config key, or CLI option was renamed, moved, or replaced
- A diff keeps both old and new interfaces alive in the same repo
- A refactor adds aliases, re-exports, wrappers, or fallback branches "for compatibility"
- LLM-generated code says some variant of "old path still works"
- Tests were updated incompletely and still exercise the retired interface

Do not use this skill as a blanket rule for:

- Published APIs with real downstream consumers
- Cross-repo migrations that cannot be completed atomically
- Temporary compatibility layers with a verified owner and removal date

## The Core Rule

**If you changed it, finish the job.** Every callsite, import, reference, and test must use the new interface. The old one is deleted — not deprecated, not re-exported, not aliased.

If you catch yourself writing a compatibility alias, wrapper, or fallback, stop and update the callers instead.

## Anti-Patterns to Eliminate

### 1. Ghost Re-exports and Type Aliases

```python
# BAD — old name kept "for compatibility"
from auth.tokens import create_jwt
generate_token = create_jwt  # legacy alias
```
```typescript
// BAD — type alias preserving old name
type UserRecord = UserProfile;  // just use UserProfile everywhere
export { UserProfile as UserRecord };  // re-export under old name
```
```python
# BAD — old module re-exports from new location
# old_module/__init__.py
from new_module import *  # so old imports still work
```

Delete the alias/re-export. Update all callers to use the new name directly.

### 2. Dead Compatibility Branches

```python
# BAD — branching on a flag that is always true after migration
if use_new_engine:
    result = new_engine.run(query)
else:
    result = old_engine.run(query)  # dead path

# GOOD — the migration is done, remove the branch
result = new_engine.run(query)
```

### 3. Wrapper Shims

```typescript
// BAD — wrapper exists only to map old signature to new
function getUser(id: string) {
  return fetchUserById({ userId: id }); // just call the new one directly
}

// GOOD — update callers to use fetchUserById, delete getUser
```

### 4. Tombstone Artifacts

Any code that exists solely to mark where removed code used to live:

```python
# BAD
_old_handler = None  # removed, kept for backward compat
# REMOVED: process_legacy_queue()
# TODO: delete after v3 migration (the migration finished 6 months ago)

# GOOD — delete the lines entirely
```

### 5. Defensive Fallbacks to Removed Behavior

```python
# BAD — catching errors from code paths that no longer exist
try:
    result = new_api.fetch(resource)
except LegacyAPIError:  # this error can't happen anymore
    result = old_api.fetch(resource)

# GOOD
result = new_api.fetch(resource)
```

### 6. Config and Environment Tombstones

```yaml
# BAD — env var for a mode that no longer exists
USE_LEGACY_AUTH=false  # always false, never toggled

# BAD — config key preserving old behavior as an option
engine:
  mode: "v2"           # v1 was removed, "v2" is the only mode
  legacy_fallback: false
```

Delete the dead config keys, env vars, and CLI flags. If a config field has exactly one valid value, it's not configuration — it's a constant. Inline it and remove the option.

## Quick Audit Flow

1. Read the diff and list every renamed, moved, or replaced interface.
2. Grep for old names, module paths, flags, and config keys.
3. Delete aliases, wrappers, re-exports, fallback branches, and tombstones.
4. Update all callsites and tests to the new interface.
5. Re-grep to confirm the old interface is gone.

## Audit Checklist

When reviewing changed code, verify:

- [ ] No re-exports, aliases, or type aliases mapping old names → new names
- [ ] No old module paths that just re-export from the new location
- [ ] No feature flags or conditionals guarding fully-migrated paths
- [ ] No wrapper functions whose only purpose is signature translation
- [ ] No tombstone comments (`# removed`, `# deprecated`, `# legacy`, `# TODO: delete after migration`)
- [ ] No unused `_var` assignments kept "in case something imports them"
- [ ] No try/except blocks catching errors from removed code paths
- [ ] No default parameter values that exist only to match an old interface
- [ ] No dead config keys, env vars, or CLI flags for removed modes
- [ ] All tests exercise the new interface directly (no tests for the old one)
- [ ] Imports across the codebase use the new module/function names

## When Backward Compatibility Is Legitimate

Preserve old interfaces **only** when ALL of these are true:

1. There is a **verified external consumer** (published API, public package, external service)
2. That consumer **cannot be updated** in this change (different repo, different team, SLA)
3. A **deprecation timeline** exists with a concrete removal date

Internal code, private APIs, and same-repo consumers do not qualify. Update them in the same PR.

## Applying This Skill

**Proactive (you're writing the refactor):**
- Update every consumer in the same change — do not leave old callsites "for a follow-up"
- When you feel the urge to add a compatibility shim, that's the signal to grep and update callers instead
- If updating all callers makes the PR too large, the issue decomposition is wrong — split by component, not by "migrate then clean up"

**Reactive (auditing existing changes):**
1. Read the diff for every renamed, moved, or restructured interface
2. Grep for every remaining reference to the pre-refactor interface
3. Migrate or delete each reference
4. Run tests and fix them to use the new interface
5. Re-grep until old references are gone
