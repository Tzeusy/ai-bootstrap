# Launch-Gate Evidence Reproducibility Addendum

**Date:** 2026-08-10
**Status:** Post-administration evidence repair

## Scope and authority boundary

The immutable launch-gate administrations at
[`2026-08-10-389c4aa.md`](../2026-08-10-389c4aa.md) and
[`2026-08-10-96ba99d.md`](../2026-08-10-96ba99d.md), and the immutable
[`R1-R5 reconciliation ledger`](../../../about/legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md),
remain unchanged. This addendum supersedes only the earlier non-reproducible
temporary-path/key-verification wording and the ledger's under-specified bare
`git diff --check` wording. It does not change any E4 candidate,
classification, comparison, verdict, count, owner decision, accepted contract,
or promotion boundary.

## Durable post-reveal E4 key bytes

The answer keys were intentionally withheld from the reviewers until their E4
classifications were fixed. They were absent from the named review commits and
are committed here only after both administrations revealed their nonce and
routing. Their later durable publication does not claim that reviewers could
read them or that the bytes were repository materials during administration.

| Administration | Durable exact-byte artifact | Bytes | SHA-256 |
|---|---|---:|---|
| Initial v1.0 administration | [`4f38f814...610.md`](./4f38f814de67238ddc4d84518149ebcc7344b148a35c4e15ce9bb38fe36ac610.md) | 1114 | `4f38f814de67238ddc4d84518149ebcc7344b148a35c4e15ce9bb38fe36ac610` |
| READY v1.4 administration | [`0fff71d8...f6b.md`](./0fff71d85d4d599989a704313bedd9996e52ae696edabfaa523a2d1967366f6b.md) | 1122 | `0fff71d85d4d599989a704313bedd9996e52ae696edabfaa523a2d1967366f6b` |

Each linked artifact is a byte-for-byte copy of its administrator-held,
post-reveal key file, including its final blank line. Hashing the committed
artifact now reproduces the corresponding pre-administration commitment
without relying on `/tmp` or an undocumented Markdown serialization.

## Reproducible `git diff --check` semantics

The reconciliation ledger's bare `git diff --check` entry did not record its
range. The two bounded deltas described by “the converged candidate and this
promotion bookkeeping” each pass the ordinary command:

```sh
git diff --check \
  4de3697c1d61d4bc3404105c7771ae0ce2336bfd \
  e2bb9ea78984878c6e06a9e37946f923032150f9
git diff --check \
  e2bb9ea78984878c6e06a9e37946f923032150f9 \
  4238391c6e4ab276719a575c8ff9267b310abd6d
```

For the complete reviewed series, the exact range is:

```sh
BASE=5d86eb489e89ca698909c431225995f30ed84601
HEAD=4238391c6e4ab276719a575c8ff9267b310abd6d
```

Plain `git diff --check "$BASE" "$HEAD"` reports 195 added Markdown lines,
all ending in exactly two ASCII spaces used as Markdown hard breaks. The
full-range gate therefore checks non-Markdown files normally, checks all other
Git whitespace classes in Markdown, and then permits only that exact two-space
suffix:

```sh
git diff --check "$BASE" "$HEAD" -- . ':(exclude,glob)**/*.md'
git -c core.whitespace=-blank-at-eol \
  diff --check "$BASE" "$HEAD" -- ':(glob)**/*.md'
git diff --unified=0 "$BASE" "$HEAD" -- ':(glob)**/*.md' |
  awk '
    /^\+\+\+ / { next }
    /^\+/ {
      line = substr($0, 2)
      if (match(line, /[ \t]+$/)) {
        suffix = substr(line, RSTART, RLENGTH)
        if (suffix != "  ") bad = 1
      }
    }
    END { exit bad }
  '
```

All three Markdown-aware full-range commands exit zero for the exact range
above. This clarification preserves the historical reconciliation result while
making its mechanical whitespace evidence independently reproducible.
