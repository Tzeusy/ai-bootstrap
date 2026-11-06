# Early independent verification

Early review helps find wrong source assumptions before a final landing diff
accumulates. It is the package's independent review, not another mandatory
pre-PR ceremony. Use a fresh native reviewer when independent judgment is needed;
continue it through corrections when independence holds. Do not run an early
verifier and then force another duplicate full review of unchanged content.

Give the reviewer a realistic request, current packet/member acceptance, governing
reference locators, published diff/base and relevant gate logs. Do not provide your
expected conclusions. Keep its worktree separate and restrict the evaluation to
read-only checks unless its explicit review contract authorizes remote comments.

Ask it to map each criterion to observable code/check evidence, investigate callers,
failure paths and scope/authority conflicts, and report every evidenced finding
with severity, confidence and reproduction. Met, unmet and unverifiable are
separate results. The owner's implementation summary is not proof.

Record relevant content/base assumptions and substantive findings in the same
canonical package review record used for final readiness. The owner corrects
ordinary defects and returns changed content; reviewer rechecks that delta and
invalidated assumptions. Required hosted/final-tree checks and fresh merge authority
remain separate. A passing source review never claims deployed activation.

The [delivery model](../../../references/delivery-model.md) defines evidence reuse;
[craft-and-care](../../../references/craft-and-care-gate.md) and
[test growth](../../../references/test-growth-gate.md) define applicable standards.
