# Health-Summary Authority Re-sweep

**Date:** 2026-08-11
**Exact candidate commit:** `ff19bbd2fd4eab11327194fe8519afcb8a3f5a8d`
**Review:** Independent `th-engineering` semantic and authority lanes
**Result:** `APPROVE`
**Artifact class:** Immutable gate/review record

## Scope and authority boundary

This re-sweep evaluated the `aib-2ct` product-boundary and health-summary
correction at one exact clean candidate HEAD. It confirms that the root
repository can discover independently shaped offerings under `projects/` and
that the child correction is coherent with the accepted stream and local-query
contracts.

This record is evidence, not an authority grant. Before the linked successor
decision, the corrected RFC, vectors, and design were candidate bytes; this
record did not accept a capability row, implement a capability, activate a
profile, authorize a source, sink, mount, package, archive, release, or
publication.

## Exact binding

| Artifact | SHA-256 | Review disposition |
|---|---|---|
| RFC 0001 | `f17a85ddd20c7c3c7998ea2a8d0d2f425b84cc57363ec942f5ea554b8cefaab8` | Candidate reviewed |
| Synthetic vectors | `4808a21a78997c7886b220c29f7bb477b6ca6bd604dcb1afd0a8bf95eacc19f6` | Candidate reviewed |
| Active OpenSpec design | `13229d7e540f41dbf23ff8ae741983cbf4af7feebe15aa48391bba4e78afa21f` | Candidate reviewed |
| Source/bounds evidence | `2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d` | Unchanged Decision 0002 artifact |
| Provenance | `dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0` | Unchanged Decision 0002 artifact |

The review confirmed that all eleven current capability `spec.md` bindings are
unchanged from the Decision 0002/0003 composition. No capability replacement
was in scope.

## Semantic findings and disposition

The reviewed correction resolves the previously detected authority conflicts:

- `reconciliation_overdue` and `source_envelope_exceeded` are stream-local;
  family/global summaries express their effect as `degraded`.
- `disabled` remains component/summary-only, never a stream state, cursor, or
  fact; all-disabled components yield a disabled source summary.
- Synthetic vectors independently assert the summary oracle for latch states,
  quarantine, storage, retention, tail, coverage, unsupported components, and
  disabled exclusion.
- The RFC, synthetic vectors, and active design agree with the accepted stream
  and local-query specifications. The accepted specification bytes themselves
  remain unchanged.

Both independent lanes returned `APPROVE` for the exact candidate above.

## Reproduced checks

The review reproduced the following clean-candidate checks:

- `git diff --check` passed.
- Root and child strict OpenSpec validation passed.
- Root authoring trace returned `11 requirements, 11 IDs, 0 errors` (with the
  existing nine minimal-coverage warnings); child authoring trace returned
  `100 requirements, 100 IDs, 0 errors, 0 warnings`.
- The repository contract and skill-link regression tests passed.
- Root project-shape maturity was `SHAPED` with its mature-traceability gate
  passing; immediate offering navigation was complete.
- A range check showed zero changed child capability `spec.md` files.

## Promotion disposition

[Owner Decision 0004](../../../heart-and-soul/decisions/0004-accept-health-summary-contract-correction.md)
promotes only the three reviewed corrected artifact bytes. Decisions 0002 and
0003 retain the eleven capability-row bindings, and every implementation and
release boundary remains closed.
