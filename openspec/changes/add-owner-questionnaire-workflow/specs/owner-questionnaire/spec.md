## ADDED Requirements

### Requirement: Genuine Owner-Gate Admission

The questionnaire workflow MUST admit only decisions that the target project's autonomy policy reserves for a human owner and MUST leave ordinary evidence-backed engineering judgment with agents.

ID: REQ-owner-questionnaire-001
Source: heart-and-soul/vision.md rules 1 and 7; th-projects autonomy contract; aib-38p owner-approved scope
Scope: v1-mandatory

#### Scenario: Ordinary engineering judgment stays autonomous

- **WHEN** doctrine, specifications, evidence, and the engineering bar determine an implementation choice within an agent's authority
- **THEN** the workflow does not add that choice to the owner questionnaire

#### Scenario: Genuine owner act is admitted

- **WHEN** a decision adopts policy or scope, chooses materially different user outcomes without governing authority, supplies owner-only information, or records an operation that requires separate owner authorization
- **THEN** the workflow may admit one bounded decision with canonical provenance

### Requirement: Independently Vetted Decision Framing

Before an item becomes review-ready, the workflow MUST obtain an independent subagent's separate passing verdicts for the problem scope and recommendation against the target project's `th-projects` shape and applicable `th-engineering` bar.

ID: REQ-owner-questionnaire-002
Source: aib-38p acceptance criterion 3; owner request 2026-08-13
Scope: v1-mandatory

#### Scenario: Independent review passes both dimensions

- **WHEN** a fresh subagent verifies the genuine gate, scope, evidence, options, recommendation, and authority boundary on the current artifact
- **THEN** the packet records the reviewer identity, date, scope pass, recommendation pass, corrections, and freshness before marking the item review-ready

#### Scenario: Material review correction remains blocked

- **WHEN** either verdict is revise or reject, or a material correction changes framing, options, recommendation, or authority
- **THEN** the item remains needs-rework until an independent subagent passes both dimensions on the corrected artifact

### Requirement: Comprehensive and Concise Asynchronous Packet

The workflow MUST accumulate stable-ID decisions in a local ignored Markdown packet that provides complete choice context while supporting one concise owner decision at a time.

ID: REQ-owner-questionnaire-003
Source: heart-and-soul/vision.md rules 5 and 7; owner request 2026-08-13
Scope: v1-mandatory

#### Scenario: Review-ready decision item

- **WHEN** an item is prepared for asynchronous owner review
- **THEN** it includes freshness-labeled background, two to four distinct options with pros and cons, one grounded recommendation, an explicit authorization boundary, adversarial review evidence, and refreshable source references

#### Scenario: One-question walkthrough resumes

- **WHEN** the owner returns to a packet containing multiple decisions
- **THEN** the workflow refreshes drift-prone evidence and presents exactly one item in priority and dependency order before advancing

#### Scenario: Local packet privacy

- **WHEN** a packet records evidence or owner-answer provenance
- **THEN** it remains local and ignored and contains no secrets, credentials, or owner-private values

### Requirement: Exact Owner-Decision Record

The workflow MUST preserve the owner act as a distinct record containing safe actor/channel provenance, timestamp, selected or edited choice, owner edits, post-answer review status, final authorization boundary, destination workflow, and routing evidence.

ID: REQ-owner-questionnaire-004
Source: aib-38p acceptance criterion 4; owner request 2026-08-13
Scope: v1-mandatory

#### Scenario: Existing option is agreed

- **WHEN** the owner selects one presented option without material edits
- **THEN** the workflow records the exact choice and boundary as agreed without treating the answer as already applied

#### Scenario: Owner materially edits an option

- **WHEN** the owner changes the option outcome or broadens its authorization boundary
- **THEN** the item returns to needs-rework and cannot be routed until the edited artifact receives fresh independent scope and recommendation passes

#### Scenario: Owner defers or rejects

- **WHEN** the owner defers the decision or declines the presented scope
- **THEN** the workflow records a held or rejected state without inferring approval

### Requirement: Authority-Safe Signoff Routing

The questionnaire workflow MUST only record and route signoffs through the canonical owning workflow and MUST NOT directly mutate project artifacts, trackers, runtimes, credentials, deployments, or external systems.

ID: REQ-owner-questionnaire-005
Source: heart-and-soul/vision.md rules 1, 5, and 7; aib-38p non-goals
Scope: v1-mandatory

#### Scenario: Signoff is routed to its owning workflow

- **WHEN** the owner explicitly asks to apply recorded decisions
- **THEN** the questionnaire refreshes current dependencies and hands the exact record to the project-shape, feature-request/OpenSpec, direction/Beads, or relevant operational workflow

#### Scenario: External action remains separately gated

- **WHEN** a decision concerns live, privileged, destructive, costly, deployment, credential, or third-party action
- **THEN** the packet does not release or perform that action and the owning operational workflow must obtain and enforce its own explicit authorization

### Requirement: Fail-Closed Packet Validation

The workflow MUST mechanically reject packets that are structurally incomplete, internally inconsistent, unvetted, or missing required owner-decision provenance for their state.

ID: REQ-owner-questionnaire-006
Source: craft-and-care/engineering-bar.md; aib-38p acceptance criteria 5 and 7
Scope: v1-mandatory

#### Scenario: Review-ready packet passes validation

- **WHEN** every item has a known state, complete non-empty sections, two to four distinct options, a recommendation selecting an existing option, matching reviewer identity, exact passing verdicts, corrections, freshness, and required answer fields
- **THEN** the deterministic validator exits successfully

#### Scenario: Bypass attempt fails validation

- **WHEN** a packet uses a pass-prefix value, reserved or mismatched reviewer, missing review field, duplicate or blank option, absent recommended option, empty evidence, unknown state, duplicate ID, unresolved placeholder, or incomplete agreed record
- **THEN** the validator exits nonzero and identifies every detected defect
