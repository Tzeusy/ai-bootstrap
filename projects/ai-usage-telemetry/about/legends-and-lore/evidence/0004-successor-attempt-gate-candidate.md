# Candidate Evidence 0004: Successor Attempt Gate

**Status:** Candidate-only, non-normative, and not accepted
**Scope:** `aib-g0k` only
**Artifact class:** `about/legends-and-lore/evidence/` candidate verification package
**Reader:** accepting owner, successor-change author, and independent high-risk privacy/accounting reviewer
**Retirement:** Retain this record and its predecessor binding unchanged until a successor owner decision accepts or rejects a later candidate. This record does not rewrite, replace, or reinterpret any accepted contract bytes.

This package binds only the already consumed `aib-alo` candidate gate. It does
not modify PR #22, accepted RFC/OpenSpec/decision bytes, candidate 0002, or
`aib-tvp`; it creates no profile, adapter, ledger, sink, mount, credential,
network control, or execution authority.

## Immutable predecessor binding

The fixed predecessor is PR #22 (`aib-alo`) at exact head
`62829a9f65f4527a1a07e29b673666d8bb224935`. Its candidate record digest is
`6126f3e18d7bf8ded6d788143b5857fcb628442759f701f04e1a68ff8a51b9c0`.
The successor gate also pins the five code-owned predecessor artifact digests
in `PREDECESSOR_GATE`:

- `11bc385d4dbb5fb59aea2e53bd3134b42a6aea351ab39146388de3bf6d531b4e`
- `2585565d1853e9489664eb5e22fa172f0fe0178447f2bebcd7a946d972860caa`
- `3aeff02535c00704d561b7c28f92f12a3e5eff2aa1a4f141e1a2ff253746f491`
- `128e0d800bcdba78c13efe6d02eddec50980b1656b520c4737103d02eec089fc`
- `468d099363596a22708a4f4657d866bd4c87c3e83832663ca588bc27a0c8bc41`

The bound state is immutable within the protocol: `attempt_consumed=True`,
`disposition="unresolved"`, `starts=0`, and `completions=0`. A request is
accepted only when its complete frozen predecessor value is equal to that
fixed record and its gate ID is exactly
`aib-g0k-successor-attempt-gate-0004`. Any changed head, digest, consumed flag,
result, count, or identifier raises `PredecessorBindingRejected`. The protocol
therefore cannot reset, replace, or bypass the consumed predecessor attempt.

## Candidate-only decision

`bind_successor_attempt_gate()` is a pure in-memory function. It accepts only
the fixed binding and produces one safe result:

| Result field | Fixed value |
|---|---|
| `status` | `candidate-review-required` |
| `execution_authority` | `none` |
| `required_next_gate` | `fresh-independent-high-risk-privacy-accounting-review` |

There is deliberately no command-line entrypoint, process control, filesystem
inspection, source access, credential handling, socket use, or target-launch
surface. The decision is a review prerequisite only; it does not authorize a
new attempt or confer any authority to act on a target.

## Test-first, no-target verification

The focused test was written before the module existed and was observed to
fail with `FileNotFoundError` for
`0004/successor_attempt_gate_0004.py`. After the minimal pure implementation,
the same four fake-data tests passed:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  projects/ai-usage-telemetry/about/legends-and-lore/evidence/0004/tests/test_successor_attempt_gate_0004.py -v
```

The tests prove exact predecessor binding, rejection of a consumed-flag reset,
rejection of a different predecessor head or gate ID, and the absence of
process/socket/target execution surfaces. They use only in-memory frozen values
and this candidate package's source text. No predecessor artifact, target,
source, credential, sink, namespace, loopback endpoint, or external control
was invoked while producing this package.

## Review hold

Before any later disposition, a fresh independent high-risk privacy/accounting
review must examine the exact draft PR head. The reviewer must verify that the
predecessor pins are complete and immutable, every mismatch fails closed, the
returned decision cannot be treated as authority, the candidate patch remains
limited to this 0004 package, and no accepted or existing candidate surface was
changed. Green local tests do not authorize merge, promotion, or any future
action.
