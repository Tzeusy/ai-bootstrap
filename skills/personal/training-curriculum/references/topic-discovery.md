# Topic Discovery

This file helps decide which prerequisite topics belong in the curriculum and how deep each topic needs to go.

## Inclusion Test

Keep a topic only if at least one statement is true:

- Without this topic, a reader will misread the repository's core architecture
- Without this topic, a contributor cannot safely reason about important changes
- Without this topic, the project's vocabulary, invariants, or failure modes stay opaque

If a topic is merely adjacent, interesting, or future-facing, move it to "nice to know later" or omit it.

## Signal Families

Do not treat prerequisite discovery as a hardcoded lookup table. Start from repository evidence, identify the kinds of technical signals present, then infer the smallest background knowledge that would make those signals legible.

Use the families below as heuristics, not as an exhaustive catalog.

| Signal family | What to look for in the repo | Likely prerequisite areas |
|---------------|------------------------------|---------------------------|
| transport and protocol signals | protocol names, wire formats, connection setup flows, retry behavior, timeout tuning, streaming APIs | network transport, latency vs throughput, ordering, reliability, backpressure, schema or contract evolution |
| concurrency and coordination signals | heavy async code, worker pools, queues, schedulers, cancellation logic, locks, background jobs | concurrency models, scheduling, coordination, retries, idempotency, failure propagation |
| state and storage signals | migrations, indexes, caches, TTLs, transactions, snapshot logic, persistence adapters | data modeling, consistency, isolation, invalidation, durability, query behavior |
| trust and security signals | auth middleware, token handling, certificates, RBAC policies, audit trails, secret access | identity, authorization, trust boundaries, credential lifecycles, threat surfaces |
| observability and operations signals | tracing, metrics, alerts, health checks, SLOs, deploy tooling, incident docs | telemetry, production debugging, operability, service health, rollout and recovery mechanics |
| domain pipeline signals | staged data or media flows, model-serving layers, compiler passes, rendering loops, control systems | the core domain model, pipeline stages, performance constraints, domain-specific failure modes |
| environment and platform signals | browser APIs, kernel or OS hooks, GPU usage, mobile-specific code, container orchestration | platform constraints, runtime behavior, resource limits, deployment environment assumptions |

## Discovery Procedure

Do prerequisite discovery across several independent deep-dive passes, not one monolithic sweep. Use the mandatory protocol in `deep-dive-passes.md`, then use this file to structure what each pass notices.

Within a given pass, inspect these evidence surfaces:

- dependency manifests and lockfiles
- config files and environment variable names
- protocol, schema, and API definitions
- deployment, CI, and runtime orchestration files
- tests that reveal invariants, failure handling, or domain vocabulary
- error messages, logging keys, and observability terminology
- architecture docs, RFCs, and diagrams

Then ask:

1. What kinds of systems is this repo interacting with?
2. What kinds of failure modes does the code seem designed around?
3. Which concepts would make the architecture, logs, and tests understandable to a new contributor?
4. Which of those concepts require only vocabulary, and which require working or contribution-ready understanding?

After all passes complete, ask one more reconciliation question:

5. Which concept clusters appeared repeatedly across passes, and which only surfaced in one angle of analysis?

## Illustrative Examples

These examples are intentionally non-normative. They show how to apply the signal families without turning them into a fixed menu.

- If a repo contains realtime session setup, codec configuration, and packet-oriented terminology, infer prerequisites around transport behavior, latency, and media/session models rather than simply "learn every networking topic."
- If a repo contains background workers, retry queues, and deduplication logic, infer prerequisites around concurrency, delivery semantics, and idempotency.
- If a repo contains migrations, query tuning, and cache invalidation logic, infer prerequisites around state modeling, consistency, and performance trade-offs.

## Depth Calibration

Assign the lightest depth that still unlocks the repo:

- `glossary`
  Use when the learner mostly needs vocabulary and rough mental models.
- `working`
  Use when the learner must follow code paths, logs, or architectural trade-offs.
- `implementation`
  Use when safe contribution requires understanding invariants, failure modes, or performance implications.

Escalate to `implementation` only when the repo clearly exposes those trade-offs to contributors.

## Topic Classes

Keep the curriculum explicit about which class a topic belongs to:

- `foundation`
  General concepts that exist outside the repo, such as TCP vs UDP or transaction isolation.
- `system-model`
  Domain models that explain how the project category behaves, such as WebRTC session setup or event-stream processing.
- `repo-orientation`
  Concepts unique to this codebase, such as subsystem names, internal jargon, or contribution boundaries.

The curriculum should usually move through those classes in that order.

## Evidence Rules

For every topic, preserve at least one concrete anchor from the repository:

- file paths
- config keys
- dependency names
- protocol terms
- test names
- architecture document titles

If the evidence is indirect, say so. Example: "Inferred from `docker-compose.yml`, `TURN` env vars, and RTP-related dependency names."

## Confidence Levels

Use these labels consistently in the evidence map:

- `direct`
  The repo explicitly names or documents the concept, protocol, subsystem, or requirement.
- `strong-inference`
  Multiple independent signals point to the prerequisite even if the repo does not state it outright.
- `weak-inference`
  The prerequisite is plausible but under-supported. Treat it as a question, caveat, or deferable topic instead of a firm requirement.

Convergence across passes should influence confidence. A topic that appears independently in multiple passes usually deserves higher confidence than one that appeared only once.

## Scope Control

When a repo suggests a very broad domain, tighten the curriculum to what the codebase actually needs.

Examples:

- Do not teach "all of distributed systems" for a queue-backed worker repo. Teach the queue semantics, retry model, idempotency, and failure handling that appear in this project.
- Do not teach "all of databases" for a Postgres-backed web app. Teach schema design, migrations, indexing, transactions, and the query patterns visible here.
- Do not teach "all of media engineering" for a conferencing tool. Teach realtime transport, session setup, codec basics, and the observability signals this repo uses.
