## ADDED Requirements

### Requirement: [TARGET-STATE] Qualified Synthetic Claude Input
MUST accept only the version-pinned, qualified synthetic Claude fixture whose manifest, digest, structural fields, types, and expected content-free outputs are members of the accepted synthetic evidence inventory, and MUST reject every fixture that does not satisfy the accepted Claude extraction manifest.

ID: REQ-synthetic-usage-spine-001
Source: RFC 0001 § Specification and Doctrine Boundary → Required before implementation or release OpenSpec; § Source-Specific V1 Attribution → Claude Code sessions
Scope: v1-mandatory

#### Scenario: Qualified fixture is accepted
- **WHEN** the disposable thesis harness receives the version-pinned qualified Claude fixture with its expected digest and manifest
- **THEN** the fixture is eligible for the synthetic record transaction
- **AND** no real-source capability is activated by that acceptance

#### Scenario: Nonconforming fixture is held
- **WHEN** the thesis harness receives a synthetic Claude record with a missing `requestId`, a digest mismatch, or an unregistered field type
- **THEN** it holds the record and produces no accepted fact
- **AND** it reports only a content-free code-owned failure state

### Requirement: [TARGET-STATE] Atomic Synthetic Contribution
SHALL commit one qualified synthetic Claude usage record as exactly one `UsageEvent`, its registered amount rows, one first-seen logical-request contribution, one newly allocated `ledger_seq`, the resulting aggregates and enabled synthetic obligations, and the matching complete cursor advancement in one SQLite transaction.

ID: REQ-synthetic-usage-spine-002
Source: RFC 0001 § SQLite Ledger and Atomicity; Proposal § New Capabilities → synthetic-usage-spine
Scope: v1-mandatory

#### Scenario: Qualified record commits as one contribution
- **WHEN** the qualified synthetic Claude record is processed against an empty disposable ledger
- **THEN** exactly one event and one first-seen request contribution are visible at one new ledger sequence
- **AND** all registered amounts, aggregates, obligations, and the cursor describe the same committed record

#### Scenario: Mid-transaction failure rolls everything back
- **WHEN** the transaction fails after amount insertion but before cursor advancement
- **THEN** no fact, amount, aggregate, request contribution, sequence, obligation, or cursor change remains committed
- **AND** retry begins from the same record

### Requirement: [TARGET-STATE] Content-Free Synthetic Boundary
MUST keep the committed synthetic contribution and every diagnostic, inspection, query, log, exception, crash output, storage artifact, and attempted projection content-free and credential-free, and MUST never decode, materialize, fingerprint, log, retain, or emit forbidden sentinel values or their digests.

ID: REQ-synthetic-usage-spine-003
Source: RFC 0001 § Mixed-Content Streaming Field Projection; about/heart-and-soul/vision.md § Non-Negotiable Principles → 2. Content and Credentials Stay Outside
Scope: v1-mandatory

#### Scenario: Permitted fields remain legible
- **WHEN** the qualified fixture contains only synthetic identities, attribution, timestamps, and registered amounts at projected paths
- **THEN** the stable query views expose the expected normalized content-free contribution

#### Scenario: Sentinels never cross the application boundary
- **WHEN** content sentinels occur in nested, escaped, malformed, and oversized skipped fields
- **THEN** none of the sentinel bytes or their digests appear in application values, output, logs, exceptions, crash output, SQLite, a sink payload, or network capture
- **AND** parser instrumentation records zero forbidden decoder, materializer, and fingerprint invocations
- **AND** every application-value, parser-instrumentation, log, exception, crash, SQLite, sink, image, environment, and network capture first observes its distinct harmless positive-control canary, while deliberate test-only sentinel-leak, forbidden-decoder/materializer/fingerprint, and unexpected-network mutations each make the harness fail without real sensitive data

### Requirement: [TARGET-STATE] Replay and Collision Outcome
SHALL leave fact, amount, request, aggregate, and sink-obligation counts unchanged when the identical qualified fixture is replayed, and MUST quarantine the synthetic stream without overwriting history when the same native identity has a changed accounting fingerprint.

ID: REQ-synthetic-usage-spine-004
Source: RFC 0001 § UsageEvent; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Exact replay is neutral
- **WHEN** the identical qualified record is replayed across a line, file, process restart, and full rescan
- **THEN** the durable cursor may advance but the fact, amount, request, aggregate, sequence, and obligation counts remain unchanged

#### Scenario: Identity mutation quarantines
- **WHEN** an A/B/A synthetic vector reuses a native request identity with a changed source time, message identity, model, or amount
- **THEN** the conflicting record is not committed and the stream reports `identity_collision`
- **AND** the original fact remains immutable

### Requirement: [TARGET-STATE] Bounded Human-Legibility Exercise
SHALL provide a documented exercise in which one developer who has not inspected private ledger tables starts from the qualified empty-harness fixture and, within ten minutes and no more than six read-only inspection or query commands after the single documented setup command, identifies the tool, source time, known-or-unknown model and project state, every category and amount, the single logical-request contribution, replay-neutral counts, and the health outcome using only the stable v1 views and versioned health JSON; passing requires every answer to match the fixture oracle without private-table access.

ID: REQ-synthetic-usage-spine-005
Source: Proposal § New Capabilities → synthetic-usage-spine; RFC 0001 § Health and Freshness State; about/heart-and-soul/vision.md § What Success Looks Like
Scope: v1-mandatory

#### Scenario: Developer completes the bounded exercise
- **WHEN** an eligible developer follows the documented setup and uses at most six read-only commands within ten minutes
- **THEN** every required answer exactly matches the synthetic fixture oracle
- **AND** the evidence records elapsed time, command count, answers, and the absence of private-table queries

#### Scenario: Legibility checkpoint fails visibly
- **WHEN** the exercise exceeds either bound, requires a private base-table query, omits a required answer, or cannot distinguish the accepted contribution from its replay
- **THEN** the human-legibility checkpoint fails
- **AND** the synthetic capability is not accepted on that evidence

### Requirement: [TARGET-STATE] Synthetic-Only Authorization Exception
SHALL confine authorization from independent acceptance of this capability to a disposable synthetic-only harness that reads no personal source mount, creates no network path, publishes no production package, and authorizes no real collection, non-synthetic fact, sink delivery, reusable production shortcut, or v1 release.

ID: REQ-synthetic-usage-spine-006
Source: RFC 0001 § Specification and Doctrine Boundary → Required before implementation or release OpenSpec
Scope: v1-mandatory

#### Scenario: Accepted spine starts only the restricted harness
- **WHEN** this capability has an explicit independent acceptance while one or more sibling capabilities remain unaccepted
- **THEN** runtime authorization permits only the disposable fixture-backed harness
- **AND** all real source, remote sink, package publication, and release paths remain disabled

#### Scenario: Broader configuration fails before side effects
- **WHEN** the harness is configured with a personal source path, non-synthetic input, enabled sink, network interface, or publish target
- **THEN** it refuses to start before opening the path, network, credential reader, destination, or registry
