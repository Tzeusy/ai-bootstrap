## Why

Owner decisions currently arrive through transient chat or ad hoc dossiers,
making comprehensive asynchronous review, independent challenge, resumption,
and safe downstream routing inconsistent. The shared workflow library needs one
bounded transport for genuine human gates without creating another doctrine,
specification, planning, tracker, or operational authority.

## What Changes

- Add a `th-projects` subskill that accumulates genuine owner decisions in a
  concise local Markdown packet and walks the owner through one item at a time.
- Require an independent subagent to pass every problem scope and recommendation
  against the target project's shape and engineering bar before presentation.
- Record exact owner-answer provenance and authorization boundaries, then route
  signoffs through the canonical owning workflow rather than mutating project or
  external state directly.
- Add a fail-closed packet validator, template, focused regression tests, and
  package-level governance checks.

## Capabilities

### New Capabilities

- `owner-questionnaire`: Asynchronous, independently vetted owner-decision
  packets, one-question walkthroughs, exact signoff records, and authority-safe
  routing.

### Modified Capabilities

None.

## Impact

- Affects `skills/personal/th-projects/` routing, documentation, validation, and
  one internal subskill package.
- Adds no runtime service, external integration, credential access, or live
  mutation path.
- Requires `uv` and Python 3.11+ only for deterministic packet validation.
