# Launch-Gate Parameter Review v1.4

**Date:** 2026-08-10  
**Reviewed candidate commit:** `383a690899ce591c439de4103f5e0fd004a246db`  
**Reviewed candidate tree:** `a84fa4c003d358a257fa4ab0f384be41f02b806f`  
**Required tier:** small change — one fresh review plus one separate fresh
confirmation

## Scope

The review bound the launch-gate v1.1 parameter requirements, the exact fixed
materials, thesis/resource operationalizations, P1–P6, first-capability
granularity and independent acceptance, and five newly sealed E4 candidates.
Prior parameter history, gate records, trend, and review results were withheld.

## Independent passes

| Pass | Context | Verdict |
|---|---|---|
| Review | Fresh reviewer at `383a690` | `PASS` |
| Confirmation | Separate fresh reviewer at `383a690` | `PASS` |

Both reviewers confirmed all required bindings; 17/17 unique shape-corpus files
existed; OpenSpec remained absent; A2 and A6 carried falsifiers, timing,
resource unknowns, and a stop condition; and P1–P6 derived only from the adopted
vision. Neither reviewer administered the gate.

Each reviewer independently fixed E4 classifications before opening the key:
`Shape`, `Shape`, `Spec`, `Spec`, `Borderline`. Both matched the external key's
2/2/1 routing after its exact SHA-256
`0fff71d85d4d599989a704313bedd9996e52ae696edabfaa523a2d1967366f6b`
was verified. No key title, nonce, routing, or file path exists in the reviewed
commit.

## Digest binding

| Artifact | SHA-256 |
|---|---|
| Reviewed candidate `parameters.md` | `0e2c2df374326e23a568cd4549075c7160a6751aeacfbabc54df8e5d63846daa` |
| Accepted `parameters.md` | `bdc2d0795065d7ef07ce692b6b431af43a8b8d33dd36a0bb51bdc72bb628d2c2` |
| Administrator-held E4 key | `0fff71d85d4d599989a704313bedd9996e52ae696edabfaa523a2d1967366f6b` |

The accepted parameter digest differs only in the status/prerequisite lines
that record these completed passes. The question series, fixed materials,
bindings, candidates, and key commitment are byte-identical to the reviewed
candidate.

**Verdict:** `PASS`. Parameters v1.4 may be committed and administered at a new
named commit. This review is withheld from the administrator and does not
itself produce `READY` or an owner acceptance.
