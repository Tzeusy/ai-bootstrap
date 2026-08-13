# Interaction and Application

Use this reference when the owner starts answering or asks agents to apply the
recorded decisions.

## Asynchronous handoff

At handoff, report the packet path, item count, evidence snapshot, unresolved
unknowns, and validation result. Do not paste the whole packet into chat. The
document must be sufficient for a fresh agent to resume without author-only
context.

## One-question walkthrough

For each item, present:

1. the decision needed and why now;
2. the recommendation in one sentence;
3. 2-5 bullets of decisive background;
4. options labeled A-D, each with concise pros and cons; and
5. a direct request for the letter, an edited choice, defer, or reject.

Ask exactly one decision per turn. Record the answer in the packet immediately,
including authenticated channel, timestamp, normalized choice, any owner edit,
final authorization boundary, and canonical destination. Then restate the
recorded decision in one sentence and advance.

At the start of each walkthrough session, and before presenting an item whose
drift-prone evidence may have changed, refresh its tracker/dependency/current-head
facts. If framing changed, return it to `Draft` and re-review it.

An ambiguous answer is not approval. Ask one narrow clarification if multiple
interpretations would cause materially different changes. A request for more
evidence keeps the item `Held`; refresh it before asking again.

A materially edited option or broadened boundary is a new decision artifact:
record it, set `Needs-rework`, and obtain fresh scope and recommendation passes
before routing it. A plain selection of an existing option needs no post-answer
review. An explicit rejection becomes `Rejected`.

## Applying decisions

Explicit permission to "apply", "update the beads/specs", or equivalent is a
separate routing gate. The questionnaire records and transports the signoff; it
does not mutate canonical project or external/live state itself. Before handing
off to the owning workflow:

- re-read every `Agreed` item and its exact authorization boundary;
- refresh tracker status, dependencies, current commit/base, active PRs, and
  overlapping ownership;
- stop if the governing artifact changed enough to invalidate the choice;
- identify and invoke the canonical owning protocol—project-shape doctrine
  amendment, project-feature-request/OpenSpec, project-direction/Beads, or the
  relevant operational workflow—and provide the exact decision record;
- require that workflow to remove only blockers actually satisfied by the
  recorded decision;
- retain every external, runtime, privileged, destructive, data-policy,
  deployment, and merge gate; the owning workflow must obtain any required
  explicit authorization separately from the questionnaire packet;
- validate the resulting tracker/spec graph; and
- record exact routing and downstream evidence in the packet.

For Beads, owner input can satisfy an owner-decision dependency without making
an implementation leaf runnable. A leaf is runnable only when its packet is
complete, all dependencies clear, no ownership overlap exists, and no other
gate remains.

## State transitions

```text
Draft -------------> Review-ready -> Agreed -> Applied
  |                       |            |
  +-> Needs-rework <------+            +-> Held
Review-ready -> Held | Rejected | Superseded
```

Never collapse `Review-ready` into `Agreed`, or `Agreed` into `Applied`.

## Final reconciliation

Report separately:

- canonical owning workflows invoked and artifacts they report updated;
- items unblocked and why;
- items still blocked and the remaining exact gate;
- items held/superseded;
- validation commands and outcomes; and
- external actions intentionally not taken.

If applying many decisions, use a table keyed by stable ID. Avoid claiming the
whole packet is complete when even one authorization boundary remains open.
