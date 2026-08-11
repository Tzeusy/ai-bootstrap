# Decision 0004: Accept the Health-Summary Contract Correction

**Status:** Activated owner decision
**Owner:** Tze, repository owner
**Date:** 2026-08-11

## Authority and reviewed basis

The owner approved the `aib-2ct` reshape/correction as the accepting owner on
2026-08-11. This decision applies that approval only to the independently
reviewed health-summary correction; it does not broaden any implementation or
operational authority.

Independent `th-engineering` semantic and authority lanes reviewed exact clean
candidate HEAD `ff19bbd2fd4eab11327194fe8519afcb8a3f5a8d` and returned
`APPROVE`. The immutable
[health-summary authority re-sweep](../../legends-and-lore/reviews/0001/2026-08-11-health-summary-authority-resweep.md)
records the candidate, evidence, checks, and boundary.

Decision 0002 remains authoritative for seven capability rows, and Decision
0003 remains authoritative for its four replacement rows. Neither decision is
rewritten here.

## Corrected artifact decisions

This decision promotes the exact corrected RFC, synthetic-vector evidence, and
supporting active OpenSpec design. Source/bounds evidence and provenance remain
byte-identical to the Decision 0002 artifact set and retain that authority.

| Artifact | Current SHA-256 | Authority |
|---|---|---|
| RFC 0001 | `f17a85ddd20c7c3c7998ea2a8d0d2f425b84cc57363ec942f5ea554b8cefaab8` | Accepted by this decision |
| Source/bounds evidence | `2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d` | Unchanged Decision 0002 artifact |
| Synthetic vectors | `4808a21a78997c7886b220c29f7bb477b6ca6bd604dcb1afd0a8bf95eacc19f6` | Accepted by this decision |
| Provenance | `dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0` | Unchanged Decision 0002 artifact |
| Active OpenSpec design | `13229d7e540f41dbf23ff8ae741983cbf4af7feebe15aa48391bba4e78afa21f` | Accepted supporting design by this decision |

## Corrected health-summary contract

- `reconciliation_overdue` and `source_envelope_exceeded` remain
  stream-local health codes. A family or global summary represents an affected
  usable stream as `degraded`; it does not copy either stream-local code.
- `disabled` is a component/summary state only. It is not a stream state and
  produces no disabled stream, cursor, or fact. A source whose components are
  all disabled has a `disabled` summary.
- The synthetic-vector oracle covers the stream latches, summary folding,
  quarantine/storage/retention/tail/coverage states, unsupported components,
  and disabled exclusion.

## Retained capability contracts

No capability `spec.md` changed in the reviewed range. All eleven current
bytes remain exactly the composed set named by Decisions 0002 and 0003: seven
unchanged Decision 0002 bindings and four Decision 0003 replacements. This
decision accepts no replacement capability row and does not infer a change to
any sibling contract.

## Acceptance boundary

This decision accepts the bounded documentation/design correction only. It
does not claim that a capability is implemented, complete task 2.1, activate a
profile, authorize a real mount or non-synthetic source, open a sink or other
destination, create a package or image, archive the active OpenSpec change, or
authorize release or publication. Every later implementation, evidence,
privacy, runtime, sink, native-parity, packaging, archive, and release gate
remains independently binding.
