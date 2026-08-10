# Decision 0003: Accept the Final-Branch Contract Corrections

**Status:** Activated owner decision
**Owner:** Tze, repository owner
**Date:** 2026-08-10

## Authority and reviewed basis

Owner Decision 0001 supplies the standing explicit direction to apply reviewed
quality-gate corrections and publish the converged documentation/specification
result. Decision 0002 makes each capability row independently amendable only
through a successor owner decision that identifies the replacement bytes.

The final-branch correction series was reviewed at exact clean HEAD
`5ec37f50de23c4eb36177ba8742ae9db54cdaf94`. The independent confirmation
returned `APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`, reproduced every
artifact binding, and passed the strict OpenSpec, authoring-trace, project-shape,
project-skill, link, E4 exact-byte, whitespace, numeric-representation, task-
ordering, and authority gates recorded in the
[final-branch correction review](../../legends-and-lore/reviews/0001/2026-08-10-final-branch-correction.md).

## Corrected artifact decisions

This decision promotes the corrected RFC and synthetic-vector bytes. The
source/bounds and provenance annexes remain byte-identical to the Decision 0002
artifact set and retain that authority.

| Artifact | Current SHA-256 | Authority |
|---|---|---|
| RFC 0001 | `1ffe8e796372ff56bdd7e81be4c25fdbf726fb51585cf53041e027857b6a5593` | Accepted by this decision |
| Source/bounds evidence | `2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d` | Unchanged Decision 0002 artifact |
| Synthetic vectors | `f78ece2be675b40ea0b0ae7efe20add6c3ab5036e419fa2d5ccc656842a94871` | Accepted by this decision |
| Provenance | `dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0` | Unchanged Decision 0002 artifact |

## Replacement capability decisions

This decision replaces exactly four Decision 0002 rows. It does not rewrite or
implicitly re-decide any sibling row.

| Canonical capability | State | Replacement `spec.md` SHA-256 binding |
|---|---|---|
| `source-adapter-profiles` | `accepted` | `e1d13becbc66431332d484409c0263efe6e08046c0726c0373126764022c6696` |
| `event-identity-and-normalization` | `accepted` | `e788522cce1d7e676cc03acae923462ab80b13236d887c78d7444a862e07966f` |
| `postgresql-history-projection` | `accepted` | `724a4665536c4794ad7c13560f6f71091724908c4d2e15b1d47b99f34af85673` |
| `release-profile-governance` | `accepted` | `6fe03a370a5b7f1abf772acacc27001f0a14dac8033503c1b4c22b6560e1a03f` |

## Composed current contract set

The current eleven-row authority is the following composition. The seven
unchanged rows retain their exact Decision 0002 bindings; the four corrected
rows use only the replacements above.

| Canonical capability | State | Decision | Current `spec.md` SHA-256 binding |
|---|---|---|---|
| `synthetic-usage-spine` | `accepted` | 0002 | `fc05078b0f616954b090ba24b1e272646bc6f8cae0f1752745885687eccd3584` |
| `source-adapter-profiles` | `accepted` | 0003 | `e1d13becbc66431332d484409c0263efe6e08046c0726c0373126764022c6696` |
| `event-identity-and-normalization` | `accepted` | 0003 | `e788522cce1d7e676cc03acae923462ab80b13236d887c78d7444a862e07966f` |
| `stream-reconciliation-and-health` | `accepted` | 0002 | `9ab1d97d3f25418bb2954495ba55443c36a0ca9d609d1d0274162d123d8a0af9` |
| `durable-local-ledger` | `accepted` | 0002 | `89de679c4983d0b48cc85c11d212b8383f2cc658a762328c58a6b1ef91fab988` |
| `quota-snapshot-semantics` | `accepted` | 0002 | `c18379dea24116144f837f7873b4ecca6bdc40377796c19de10686b793c9c464` |
| `local-query-contract` | `accepted` | 0002 | `f1f5ebcae0a0c29c4dbdec0f98c6afa0da8d65ac2d27cf1b79a380ca0e14f22a` |
| `otlp-metrics-projection` | `accepted` | 0002 | `2356bd1d02b19ce9ec88ccc99e6debdbffcf64c05aa58fe2816697fa25f74359` |
| `postgresql-history-projection` | `accepted` | 0003 | `724a4665536c4794ad7c13560f6f71091724908c4d2e15b1d47b99f34af85673` |
| `release-profile-governance` | `accepted` | 0003 | `6fe03a370a5b7f1abf772acacc27001f0a14dac8033503c1b4c22b6560e1a03f` |
| `portable-runtime-and-release` | `accepted` | 0002 | `71c524a319a58d2f94b76e0c206bf997c92a832ec115c74b4c342fee413c9aad` |

Each row remains independently amendable only through another successor owner
decision naming that capability and its replacement bytes.

## Acceptance boundary

This decision accepts corrected contracts and supporting design/evidence bytes;
it does not claim that any capability is implemented. It records no measured
release-profile value, activates no profile, authorizes no real source mount or
non-synthetic fact, opens no sink or destination, creates no production package
or image, archives no OpenSpec change, and authorizes no release or publication.

Task 2.1 may verify this eleven-row composition as one prerequisite, but remains
unchecked until an implementation session executes its full side-effect-free
gate. Every later task, evidence, privacy, runtime, sink, native-parity,
packaging, archive, and release condition remains independently binding.
