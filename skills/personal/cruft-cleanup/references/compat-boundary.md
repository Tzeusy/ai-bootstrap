# Compatibility Boundary

Preserve old interfaces only when all of the following are true:

1. There is a verified external consumer such as a published API, public package, or external service.
2. That consumer cannot be updated in the same change.
3. There is a concrete deprecation or removal plan with an owner and date.

Internal code, private APIs, and same-repo consumers do not qualify. Update them in the same PR.

## Hard Stops

- Do not invent compatibility layers "just in case."
- Do not preserve dead paths because an LLM feels safer keeping both.
- Do not treat same-repo callers as if they were third-party consumers.

If compatibility is genuinely required, it should be explicit, time-bounded, and owned. Otherwise finish the migration and delete the old path.
