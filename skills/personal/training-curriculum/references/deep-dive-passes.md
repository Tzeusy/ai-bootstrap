# Deep-Dive Passes

Comprehensive prerequisite discovery is not a single repo sweep. This skill requires a hard minimum of 3 deep-dive passes performed by independent subagents so each pass can surface concepts without being anchored by the others.

## Hard Requirement

- Run at least 3 prerequisite-discovery passes.
- Each pass must be performed by an independent subagent.
- Each subagent should have isolated task context. Do not preload prior pass conclusions into later passes.
- Reconcile the three outputs only after all passes complete.

If the environment cannot support independent subagents, fail closed and report that the curriculum cannot be called comprehensive under this skill's contract.

## Pass Design

Each pass should answer the same core question:

> What does someone need to know before this repository's code, tests, logs, and architecture will make sense or be safe to change?

But each pass should interrogate the repo from a different angle.

### Pass 1: Surface And Topology Pass

Focus on:

- top-level docs and contributor docs
- directory structure and subsystem boundaries
- manifests, dependencies, generated code boundaries
- architecture docs, RFCs, diagrams, deployment surfaces

Primary goal:

- surface the obvious domain, architecture, and platform prerequisites

### Pass 2: Runtime And Failure-Mode Pass

Focus on:

- tests
- configs and environment variables
- runtime orchestration
- logging, metrics, tracing, alerts
- retries, timeouts, concurrency, storage, networking, auth, and other failure-handling code paths

Primary goal:

- surface hidden operational, systems, and reasoning prerequisites that are not obvious from the docs alone

### Pass 3: Contribution-Hazard And Hidden-Concept Pass

Focus on:

- the kinds of changes a newcomer might try to make
- invariants that would be easy to violate without background knowledge
- vocabulary or mental models implicitly assumed by the code
- advanced or adjacent concepts that appear repeatedly enough to block contribution if omitted

Primary goal:

- catch prerequisite concepts that the first two passes under-emphasized and identify what must be learned before safe modification

## Reconciliation

After all 3 passes complete:

1. union the candidate concept lists
2. dedupe near-synonyms and collapse overlapping concepts
3. note which pass or passes discovered each concept
4. increase confidence when multiple passes converge on the same prerequisite
5. preserve disagreement or uncertainty in `open-questions.md` instead of forcing false certainty

If reconciliation keeps uncovering major new topic clusters, run additional passes. The minimum is 3, not the ceiling.

## Required Output Artifact

Summarize the research process in `curriculum/research-ledger.md`:

- what each pass focused on
- the major concept clusters each pass surfaced
- overlaps across passes
- concepts that appeared late and changed the curriculum shape
- unresolved disagreements or weakly supported topics

This ledger is not optional. It is the audit trail that shows the curriculum was researched comprehensively rather than assembled from one sweep.

## Anti-Patterns

- one agent doing three nominal "passes" in the same context window
- later passes inheriting earlier pass conclusions as assumptions
- treating pass 1 as enough because the repo looks well documented
- reconciling by deleting anything surprising instead of checking whether it reveals a hidden prerequisite
