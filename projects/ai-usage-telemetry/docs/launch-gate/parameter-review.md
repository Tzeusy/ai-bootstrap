# Launch-Gate Parameter Review

**Date:** 2026-08-10  
**Scope:** [`parameters.md`](./parameters.md), before the first administration  
**Required tier:** small change — one fresh review pass plus one fresh
confirming pass

## Convergence record

The first confirming falsifier rejected the candidate because it exposed the
E4 routing, offered weak near-misses, omitted accepted topology from the shape
corpus, left the absent spec directory unwaived, and gave the first capability
too many outcomes. The binding was revised rather than waived.

The next confirming falsifier found two remaining blockers: wording appeared to
defer RFC-required capabilities beyond the first OpenSpec changeset, and an E4
answer file inside the reviewer-readable repository was not actually sealed.
The binding was revised again. It now distinguishes one first capability from
the complete initial changeset, and commits only a nonce-bound SHA-256 of an
administrator-held key that is absent from the repository until comparison.

Two sequential fresh-context reviewers then independently returned `PASS` on
the final bytes. They confirmed:

- every section 7 binding is present and coherent;
- A3, D2, E1, prerequisites, authority, and P1–P5 are falsifiable and bounded;
- the first capability and RFC-required initial changeset do not conflict; and
- the external E4 key's exact-byte digest matches `parameters.md`, while the key
  and routing are absent from the administration materials.

## Final binding

| Artifact | SHA-256 |
|---|---|
| `parameters.md` | `d1b7c07e20168e1c7ec5c747e3d355b43df4ab9d7297129eaa8d454b62df1fdd` |
| Administrator-held E4 key bytes | `4f38f814de67238ddc4d84518149ebcc7344b148a35c4e15ce9bb38fe36ac610` |

**Verdict:** `PASS`. The parameter block may be committed and administered at a
named commit. This review does not itself administer the launch gate or reveal
the sealed E4 answer.
