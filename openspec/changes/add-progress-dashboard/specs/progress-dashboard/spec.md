## ADDED Requirements

### Requirement: Reusable Session-Owned Progress Workspace

The shared progress-dashboard skill MUST own its implementation independently of any execution subskill and MUST maintain one identity-bound local workspace with current in-progress, todo and complete Markdown projections plus a separately controlled handover document.

ID: REQ-progress-dashboard-001
Source: owner request 2026-11-14; about/heart-and-soul/vision.md rules 1, 5 and 7
Scope: v1-mandatory

#### Scenario: A workflow launches or resumes its view

- **WHEN** a workflow initializes a stable slug with its actor and repository
- **THEN** it gets a private local workspace with four readable Markdown files, repeat initialization preserves existing content, and a conflicting actor/repository is refused

#### Scenario: A checkpoint updates current work

- **WHEN** a validated partial snapshot has the expected current revision
- **THEN** the helper commits the display state and regenerates the three progress projections without mutating the owning tracker, while stale revisions refuse overwrite

### Requirement: Explicit Manual Handover

The helper MUST update handover.md only through a separate command carrying an explicit manual owner request, and MUST NOT change it during ordinary progress, usage, feedback, resume, compaction or stop operations.

ID: REQ-progress-dashboard-002
Source: owner request 2026-11-14 item 1
Scope: v1-mandatory

#### Scenario: Automatic activity leaves handover untouched

- **WHEN** a session publishes progress, receives feedback, resumes or stops
- **THEN** the existing handover content remains unchanged

#### Scenario: The owner asks for a handover

- **WHEN** the parent invokes the dedicated handover command with the explicit request and prepared content
- **THEN** the helper updates the document and records the request provenance separately

### Requirement: Token-Efficient Background Visibility

The dashboard MUST use fixed scaffolded assets and scripts for rendering, lifecycle, telemetry and feedback, and MUST NOT require model-driven refresh cycles, per-run generated web infrastructure, or extra model calls to summarize child transcripts.

ID: REQ-progress-dashboard-003
Source: owner request 2026-11-14 item 3 and explicit token-efficiency emphasis
Scope: v1-mandatory

#### Scenario: The owner watches progress

- **WHEN** the browser refreshes while the parent or its agents work
- **THEN** the background server serves current work, findings, agent summaries, optional rendered visuals and available usage without waking a model or querying the workflow's tracker

#### Scenario: A parent reaches an existing checkpoint

- **WHEN** a substantive workflow event changes progress or the parent needs pending steering
- **THEN** the parent publishes only changed fields or requests compact status/inbox data, retaining its existing wake cadence

### Requirement: Honest Incremental Usage and Agent Overview

The dashboard MUST summarize parent and child-agent observations with source freshness, MUST collect supported explicitly attached usage logs incrementally, and MUST distinguish measured, partial, unknown and errored counters without fabricating estimates or double-counting cached input.

ID: REQ-progress-dashboard-004
Source: owner refinement 2026-11-14 progress, tokens and subagents in one visual layer
Scope: v1-mandatory

#### Scenario: Supported logs append usage records

- **WHEN** explicitly attached Codex or Claude logs receive complete valid usage records
- **THEN** bounded background reads update per-agent counters, deduplicate cumulative/streamed records, persist offsets for restart, and aggregate measured coverage separately from reported agent status

#### Scenario: Usage is unavailable or still catching up

- **WHEN** a source is missing, malformed, unsupported or not fully consumed
- **THEN** the page displays its unknown/error/partial state and excludes unmeasured rows from aggregate coverage rather than representing them as measured zero

### Requirement: Durable Authority-Safe Steering

The browser MUST persist optional feedback with its viewed revision and stable retry identity, MUST preserve unsent drafts across refresh/failure, and MUST leave disposition and all operational authority with the parent workflow at its next safe checkpoint.

ID: REQ-progress-dashboard-005
Source: owner request 2026-11-14 item 2; existing user-questionnaire authority boundary
Scope: v1-mandatory

#### Scenario: Feedback is submitted or retried

- **WHEN** the owner submits steering through the session page, including a retry after a lost response
- **THEN** one durable pending item is recorded, reads do not consume it, and the parent's explicit acknowledgement records the disposition visible in the browser

#### Scenario: A message concerns a hard owner gate

- **WHEN** feedback asks for a gated merge, deployment, policy or destructive action
- **THEN** it remains input to the owning workflow's existing gate and does not itself execute commands, mutate the tracker or confer new authority

### Requirement: Bounded Local Server Lifecycle

The helper MUST isolate each session's server and content, default to a private loopback listener, constrain served artifacts to explicitly published files, and verify server identity before reusing or stopping a process.

ID: REQ-progress-dashboard-006
Source: owner request 2026-11-14 pre-scaffolded parallel server; about/heart-and-soul/vision.md runtime boundary
Scope: v1-mandatory

#### Scenario: An existing session launches again

- **WHEN** a verified server is already running for its workspace
- **THEN** the helper reuses it without a second process and preserves feedback, while a stale PID alone cannot authorize stopping another process

#### Scenario: Unrelated content or cross-site writes are requested

- **WHEN** a request lacks the private URL, has an invalid host/origin, traverses artifact paths or targets an unpublished file
- **THEN** the server refuses it without exposing unrelated local content or recording feedback
