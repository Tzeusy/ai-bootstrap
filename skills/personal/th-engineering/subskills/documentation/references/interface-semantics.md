# Interface Semantics Card

The fixed vocabulary for documenting an interface's behavioral contract —
what a caller must know that the signature cannot say. A card is a few
labeled lines placed **adjacent to the interface** (docstring, OpenAPI
`description`, CLI help text, header comment), never in a distant prose doc.

Cards are contract-level by construction: every line states something a
caller can observe, so a behavior-preserving refactor cannot invalidate one.
When behavior changes, the card changes in the same commit (engineering-bar
bias 7). A wrong card is worse than no card.

## Fields

| Field | States | Example values |
|---|---|---|
| `Side effects` | Everything beyond the return value: writes, emits, deletes, external calls. | `inserts into orders; emits OrderPlaced` · `none (pure)` |
| `State` | What it holds, caches, or depends on across calls. | `stateless` · `module-level connection pool` · `reads config at startup` |
| `Idempotency` | Whether a retry is safe, and what makes it so. | `yes — keyed by request_id` · `no — caller must dedupe` |
| `Failure` | Error modes a caller must handle; partial-failure behavior. | `409 on duplicate; transactional — no partial writes` · `best-effort; may partially apply` |
| `Concurrency` | Only when it matters: thread-safety, ordering, locking. | `not thread-safe; callers serialize` · `safe for concurrent readers` |

Rules:

- One line per field; if a line needs a paragraph, the interface — not the
  doc — probably needs simplification.
- `Side effects` and `Idempotency` are mandatory for anything that mutates
  state or crosses a process boundary. `none (pure)` is a valuable answer —
  it is a promise, not filler.
- Omit a field only when genuinely inapplicable. When a caller might
  reasonably wonder, an explicit `none` beats omission.
- No internals: name what is observable (tables, events, error codes,
  retry keys), not which helper performs it.

## Which interfaces get a card

Write a card when the interface is any of: exported from its module/package,
exposed over a process boundary (endpoint, queue consumer, CLI, job), mutates
state, or is retried by infrastructure. Skip private helpers and trivially
pure functions — a card there is noise (bar 7).

## Placements

Docstring:

```python
def place_order(req: OrderRequest) -> OrderId:
    """Create an order from a validated request.

    Side effects: inserts into `orders`; emits OrderPlaced to the event bus.
    State: stateless; uses the module-level connection pool.
    Idempotency: yes — keyed by req.request_id; duplicates return the original OrderId.
    Failure: raises DuplicateOrder on request_id reuse with different payload;
        transactional — no partial writes.
    """
```

OpenAPI `description` (renders as prose in doc sites):

```yaml
post:
  summary: Place an order
  description: |
    Side effects: inserts into `orders`; emits `OrderPlaced`.
    Idempotency: yes — keyed by `Idempotency-Key` header; duplicates return the original order.
    Failure: `409` on key reuse with a different payload; transactional — no partial writes.
```

CLI help / header comment: same labeled lines, same order.
