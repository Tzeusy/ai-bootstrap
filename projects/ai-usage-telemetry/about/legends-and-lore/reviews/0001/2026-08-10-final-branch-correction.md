# Final-Branch Correction Review

**Date:** 2026-08-10
**Accepted predecessor:** `4238391c6e4ab276719a575c8ff9267b310abd6d`
**First correction commit reviewed:**
`ead6fa583002851456004f9fd24c9b700a407afb`
**First correction verdict:** `NOT APPROVED`
**Current status:** Bounded candidate corrections applied; fresh exact-head
confirmation and successor owner acceptance required

## Authority boundary

Decision 0002 remains immutable and authoritative only for the exact R5 bytes
it names. This record does not amend that decision, accept the current RFC or
synthetic vectors, accept any replacement capability row, implement a
capability, activate a profile, authorize a real source or destination, archive
the active change, or authorize packaging or release.

The current candidate is fail-closed: seven unchanged capability specs still
match Decision 0002; corrected current bytes for
`source-adapter-profiles`, `event-identity-and-normalization`,
`postgresql-history-projection`, and `release-profile-governance` are
`unknown`. Task 2.1 therefore blocks all non-synthetic production work until a
fresh review approves one exact HEAD and a successor owner decision binds the
four replacements.

## Findings that initiated the correction

The post-promotion final branch review found four important and two minor gaps:

1. all five project-shape pillars existed, but their required project-local
   navigation skills were absent;
2. PostgreSQL `timestamptz` could not preserve the accepted nanosecond semantic
   time contract;
3. RFC 8785 JSON-number use could not preserve every accepted signed-64-bit
   amount/counter value across the interoperable number boundary;
4. the E4 answer-key commitments depended on temporary files rather than
   durable exact bytes;
5. the reconciliation ledger's bare whitespace-gate claim lacked a reproducible
   range and Markdown exception contract; and
6. an immutable administration packet's historical relative spec-format link
   no longer resolved.

The first correction commit fixed those surfaces, but its independent exact-
head review correctly rejected promotion because current navigation still
claimed the changed hashes were accepted. It also found two scanner
false-positive paths, a task-order dependency on a not-yet-implemented integer
codec, a missing current correction-range whitespace gate for the two immutable
key blobs, and over-broad wording about optional Git whitespace classes.

## Bounded candidate corrections

- Five thin project-local skills now route agents to doctrine, design contracts,
  capability specs, topology, and project engineering standards. The scanner
  counts only valid skills and only numbered list/heading rules inside the
  explicit non-negotiable doctrine section; false-positive fixtures cover
  roadmap headings and invalid present skill files.
- One domain-owned canonical non-negative signed-64-bit decimal-string codec
  crosses RFC 8785 amount/counter/profile-bound boundaries. Internal arithmetic
  and SQL amount columns remain exact integers. Profile foundation tasks use an
  injected fake port until the domain task implements the real codec.
- PostgreSQL source, collection, and reset instants use authoritative checked
  `bigint` UTC Unix nanoseconds. Only operational checkpoint `updated_at`
  remains `timestamptz` and is excluded from fact equality.
- The two revealed E4 keys are durable exact-byte artifacts whose 1114/1122
  byte sizes and filename SHA-256 values reproduce. The addendum defines exact
  historical and correction-range whitespace gates and narrows its claim to
  default-enabled Git whitespace classes.
- A compatibility forwarding document repairs the immutable packet's relative
  link without rewriting the packet.
- Current lifecycle and acceptance routes now mark the corrected RFC/evidence
  and four spec rows pending/unknown rather than silently inheriting Decision
  0002 authority.

## Current candidate bindings

| Artifact | Candidate SHA-256 | State |
|---|---|---|
| RFC 0001 | `4497a61f85b728c8ee31129392a81af40de717d9a1329cd8d8512bb83b8edce4` | Pending |
| Source/bounds evidence | `2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d` | Unchanged accepted predecessor |
| Synthetic vectors | `22f30ac862e29662a0b17ad0047f463adebff97a4a3b70f4293a6346732656dc` | Pending |
| Provenance | `dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0` | Unchanged accepted predecessor |
| `source-adapter-profiles` | `e1d13becbc66431332d484409c0263efe6e08046c0726c0373126764022c6696` | Pending replacement row |
| `event-identity-and-normalization` | `e788522cce1d7e676cc03acae923462ab80b13236d887c78d7444a862e07966f` | Pending replacement row |
| `postgresql-history-projection` | `724a4665536c4794ad7c13560f6f71091724908c4d2e15b1d47b99f34af85673` | Pending replacement row |
| `release-profile-governance` | `6fe03a370a5b7f1abf772acacc27001f0a14dac8033503c1b4c22b6560e1a03f` | Pending replacement row |

## Required confirmation

A fresh reviewer must bind its result to the exact committed candidate HEAD,
re-read the complete correction series and current authority routes, reproduce
the hashes above, and return no Critical, Important, or Minor finding. It must
also rerun strict OpenSpec validation, authoring trace, exact
`11 / 100 / 249 / 77` cardinalities, project-shape maturity and skill validity,
project-skill regression gates, active links, E4 exact-byte proof, and the
documented whitespace gates.

Only after that result may a successor decision replace the four named
Decision 0002 rows and promote the corrected RFC/synthetic hashes. The seven
unchanged rows remain independently accepted throughout.
