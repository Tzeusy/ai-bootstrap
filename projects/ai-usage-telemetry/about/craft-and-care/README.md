# Craft and Care

Engineering standards for `ai-usage-telemetry`.

**Status:** Adopted through Owner Decision 0001 with RFC 0001 acceptance. See
the central [lifecycle matrix](../README.md#lifecycle-status). The launch gate
has recorded `READY`; the active OpenSpec change is a complete authored
candidate awaiting four improvement cycles and conditional owner acceptance,
not an owner-accepted capability set.

This pillar supplements the repository-wide
[`ai-bootstrap` engineering bar](../../../../about/craft-and-care/engineering-bar.md).
It records only the extra care required for a system that reads local usage
records, keeps an indefinite accounting ledger, and delivers telemetry to
independent sinks. The root bar remains the default; this pillar introduces no
override to it.

Read these standards before changing an adapter, normalized event, ledger,
checkpoint, metadata policy, sink, container boundary, or dependency:

1. [`engineering-bar.md`](./engineering-bar.md) defines project-specific
   completion and merge-blocking conditions.
2. [`testing-and-verification.md`](./testing-and-verification.md) defines
   risk-scaled evidence and the mandatory regression corpus.
3. [`security-and-privacy.md`](./security-and-privacy.md) defines the content,
   credential, metadata, and runtime privilege boundaries.
4. [`review-and-documentation.md`](./review-and-documentation.md) defines
   author evidence, independent blocking review, RFC review records, and
   same-change documentation duties.
5. [`observability-and-operations.md`](./observability-and-operations.md)
   defines truthful health reporting, partial-failure behavior, and recovery
   evidence.
6. [`interfaces-and-dependencies.md`](./interfaces-and-dependencies.md)
   defines adapter, ledger, sink, and dependency change discipline.

Detailed event identity, checkpoint, ledger, and delivery semantics belong in
[`RFC 0001`](../legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md).
The current normative candidate follows the active change's
[`proposal`](../../openspec/changes/establish-ai-usage-telemetry-v1/proposal.md) →
[`design`](../../openspec/changes/establish-ai-usage-telemetry-v1/design.md) →
[`specifications`](../../openspec/changes/establish-ai-usage-telemetry-v1/specs/) →
[`tasks`](../../openspec/changes/establish-ai-usage-telemetry-v1/tasks.md) route.
Deployment topology belongs in `about/lay-and-land/`. These files define the
evidence and engineering posture required to implement the contracts safely
after the remaining review and acceptance gates.

## Doctrine trace

The standards apply these project principles:

- **Local Facts Become User-Owned History**
- **Content and Credentials Stay Outside**
- **Accounting Is Eventually Exact**
- **Partial Failure Is Explicit**
- **Normalization Preserves Meaning**
- **The Runtime Boundary Is Portable and Narrow**
- **Simplicity Serves the Contract**

A change that cannot explain how it preserves the applicable principles is not
ready for review.
