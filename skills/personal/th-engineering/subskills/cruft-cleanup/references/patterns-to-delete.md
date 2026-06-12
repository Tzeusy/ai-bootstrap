# Patterns To Delete

These are the common forms of migration cruft this skill is meant to eliminate.

## Ghost Re-exports And Type Aliases

```python
# BAD — old name kept "for compatibility"
from auth.tokens import create_jwt
generate_token = create_jwt
```

```typescript
// BAD — type alias preserving old name
type UserRecord = UserProfile;
export { UserProfile as UserRecord };
```

```python
# BAD — old module re-exports from new location
from new_module import *
```

Delete the alias or re-export and update all callers to use the new name directly.

## Dead Compatibility Branches

```python
# BAD
if use_new_engine:
    result = new_engine.run(query)
else:
    result = old_engine.run(query)

# GOOD
result = new_engine.run(query)
```

If the migration is complete, the branch is dead code.

## Wrapper Shims

```typescript
// BAD
function getUser(id: string) {
  return fetchUserById({ userId: id });
}
```

Delete the wrapper and update callers to use the new interface.

## Tombstone Artifacts

```python
# BAD
_old_handler = None
# REMOVED: process_legacy_queue()
# TODO: delete after v3 migration
```

Delete code that exists only to mark where removed behavior used to live.

## Defensive Fallbacks To Removed Behavior

```python
# BAD
try:
    result = new_api.fetch(resource)
except LegacyAPIError:
    result = old_api.fetch(resource)
```

If the legacy path is gone, the fallback should be gone too.

## Config And Environment Tombstones

```yaml
# BAD
USE_LEGACY_AUTH=false

engine:
  mode: "v2"
  legacy_fallback: false
```

If a setting has only one valid value after the migration, it is no longer configuration. Inline the constant and delete the option.
