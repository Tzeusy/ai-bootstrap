# Compatibility Boundary

Preserve old interfaces only when all of the following are true:

1. A verified external consumer exists — published API, public package, or external service.
2. That consumer cannot be updated in the same change.
3. A concrete deprecation or removal plan exists, with owner and date.

Internal code, private APIs, and same-repo consumers do not qualify. Update them in the same PR.

## Hard Stops

- Do not invent compatibility layers "just in case."
- Do not preserve dead paths because an LLM feels safer keeping both.
- Do not treat same-repo callers as if they were third-party consumers.

If compatibility is genuinely required, make it explicit, time-bounded, and owned. Otherwise finish the migration and delete the old path.
