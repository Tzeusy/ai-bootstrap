# Condensation Classification

Load only during a condensation pass — the "Classify" step of
[suite-discipline](suite-discipline.md). Not needed for writing or
reviewing individual tests.

Decides keep / delete / rewrite for every test in scope. Generalized from
a multi-phase condensation of a heavily LLM-developed suite (13,675 →
2,196 tests); the litmus in §1 exists because a 22-auditor verification
pass found the naive version of the rule produced mass false positives.

## Decision Tree

Walk each test through, top to bottom; first match wins:

1. **Asserts on a mock call** (`assert_called*`, `assert_not_called`,
   `call_count`)? → NOT auto-delete. Apply the plumbing-vs-contract
   litmus (§1).
2. **Asserts an error-message string** (not exception type)? → rewrite to
   assert the exception type or error code. Message strings are brittle
   letter-tests; the type is the contract.
3. **Imports private internals** (underscore helpers, non-public
   modules)? → if the behavior is pinned through a public interface
   elsewhere, delete; otherwise rewrite the test through the public
   interface (test-rigor bar 1).
4. **Pins a documented invariant, wire contract, or spec scenario through
   the public surface?** → keep. Add the provenance docstring if missing
   (suite-discipline: growth governance).
5. **Tests a pure helper?** → complex logic (branching, >10 lines): keep,
   but consolidate scattered cases into one parametrized test. Trivial
   (<5 lines, no branches): delete — callers cover it implicitly.
6. **None of the above** → delete.

## §1. Plumbing vs. Contract (mock-call assertions)

The most error-prone node. A blanket "delete all mock-call assertions"
rule reads as obviously right — call assertions restate implementation
(bar 1) — and is wrong often enough to red real regressions:
`assert_not_called` and `call_count` frequently encode invariants that
have **no observable return value** to assert instead.

**Litmus:** delete the call assertion in thought. *Does any surviving
assertion still fail when the invariant is violated?*

- **Yes** → it was plumbing: the behavioral result was already asserted
  and the call assertion re-checked internal wiring. Delete it.
- **No** → it is the contract: the call / no-call / count is the only
  proof. Keep it. **When unsure, keep.**

```python
# PLUMBING — the result assertion already proves the fetch happened:
msgs = await connector.fetch_messages()
assert len(msgs) == 2                                  # keep — behavioral
mock_api.list.assert_called_once_with(max=100)         # delete — plumbing
```

**Contract archetypes** — call assertions that ARE the invariant:

- **Idempotency / no-double-write** — second invocation must not repeat
  the effect: `mock_insert.assert_called_once()` after two calls is the
  only proof of no duplicate write.
- **Retry / delivery cadence** — `call_count == 3` proves the retry
  schedule; no return value shows it.
- **Bypass proof** — a path that must SKIP a collaborator:
  `resolver.assert_not_called()` is the bypass evidence.
- **Side effect NOT emitted (safety)** — `send.assert_not_awaited()`
  after revoked auth proves nothing left the system; an un-sent message
  has no inspectable result.
- **Layering boundary** — `inner_store.assert_not_called()` proves an
  interceptor handled the case before delegation; the no-call IS the
  architectural boundary.

```python
# CONTRACT — deleting the count assertion hides a real regression:
await bootstrap_owner(pool)
await bootstrap_owner(pool)              # second run
assert pool.execute.call_count == 1      # idempotency proof — keep
```

## Structural vs. Behavioral Assertions

Match assertion precision to what the spec pins:

- Spec is **structural** ("returns a list of facts", "responds with the
  envelope schema") → assert structure: non-None, type, non-empty,
  schema-validates. Not exact strings, counts, or ordering.
- Spec is **behavioral** ("rejects expired tokens", "transitions
  accepted → processing") → assert the exact outcome.

Over-precise assertions on structurally-specified behavior are the
letter-testing failure mode LLM sessions commit most: they weld tests to
incidental output and break on every harmless change.

## Rewrite Target

When step 3 says rewrite, the replacement goes through the component's
public surface (tool interface, public API, endpoint client) with a real
local substitute for owned infrastructure — not a mocked pool — per the
mock ladder in [suite-discipline](suite-discipline.md). One rewritten
public-surface test typically replaces several private-helper tests; that
consolidation is where condensation's test-count reduction actually
comes from.
