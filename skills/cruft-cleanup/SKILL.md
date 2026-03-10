---
name: cruft-cleanup
description: >
  Eliminate backward-compatibility shims, dead legacy code paths, and cruft during refactors
  or migrations. Use when reviewing or writing code that touches refactored, renamed, or
  migrated interfaces — especially when LLM-generated code introduces unnecessary shims,
  re-exports, compatibility wrappers, or "old path still works" fallbacks. Invoke explicitly
  with /cruft-cleanup to audit changed code, or as a post-refactor pass.
---

# Cruft Cleanup

**Why this skill exists:** LLMs are trained on codebases that value backward compatibility — published libraries, versioned APIs, multi-team monorepos. This biases LLM-generated code toward preserving old interfaces "just in case," even when the old interface is internal, has zero external consumers, and every callsite is in the same repo. Left unchecked, this instinct layers shim upon shim until the codebase is more glue than logic.

When refactoring, migrating, or renaming code, leave **only the new code paths**. Do not preserve old interfaces, shim layers, or backward-compatibility wrappers unless there is a verified external consumer that cannot be updated in the same change.

## The Core Rule

**If you changed it, finish the job.** Every callsite, import, reference, and test must use the new interface. The old one is deleted — not deprecated, not re-exported, not aliased.

**When you are the author of a refactor:** Do not introduce the shim in the first place. Update every consumer in the same change. If you catch yourself writing a compatibility alias, wrapper, or fallback — stop and update the callers instead.

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
1. **Read the diff** — identify all renamed, moved, or restructured interfaces
2. **Grep for old names** — find every remaining reference to the pre-refactor interface
3. **Update or delete** — migrate each reference to the new interface; delete the old one
4. **Run tests** — if a test breaks, fix the test to use the new interface (do not re-add the shim)
5. **Re-grep** — verify zero remaining references to old names
