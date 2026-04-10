# Craft and Care — Engineering Character and Standards Layer Guide

## Purpose

The engineering-character layer answers **WHO ARE WE WHEN WE BUILD?** It defines the quality bar
for implementation, verification, review, observability, compatibility, security hygiene,
documentation, and maintainability. It is not product doctrine, not subsystem design, not feature
requirements, and not topology. It is the project's explicit answer to what kind of engineer this
codebase expects in practice.

This pillar should express stack-neutral principles and reviewable expectations. It should tell
humans and agents what evidence, discipline, posture, and care are required, without prescribing
vendors, frameworks, or tools unless the project has separately standardized those choices
elsewhere. `heart-and-soul` defines who the project is in purpose; `craft-and-care` defines who we
must be when we change it.

## Default Engineering Biases

Unless a project explicitly overrides them, `craft-and-care` should default to these engineering
biases:

1. **Prefer cleanup over same-repo compatibility cruft** — Follow `/cruft-cleanup` principles
   wherever possible. When a refactor, rename, or migration can be completed atomically inside the
   same repo, prefer deleting retired wrappers, aliases, fallback branches, dead flags, and unused
   paths over preserving them "just in case." Preserve backward compatibility only when there is a
   verified external consumer or a real cross-repo migration constraint.
2. **Prefer readability and simplicity over cleverness** — When two approaches can achieve the
   same correctness and reliability, prefer the simpler and more readable one. Dense, overly
   abstract, or surprising code needs a strong justification.
3. **Bias toward observability** — Failure paths should be diagnosable. At minimum, logs should be
   instrumented so exceptions can be investigated quickly, with enough structured context to narrow
   plausible causes rather than merely report that something failed.
4. **Prefer durable fixes over expedient patches** — Do not optimize for "clear the error for now"
   when a correct, maintainable fix is tractable. Assume engineering time is available; optimize
   for correctness, reliability, and long-term maintainability instead.
5. **Prefer explicitness over magic** — Prefer visible control flow, explicit data movement, and
   obvious invariants over hidden side effects, surprising framework behavior, or implicit coupling.
6. **Prefer fail-fast over silent fallback** — Unless graceful degradation is explicitly required by
   doctrine, specs, or design contracts, surface incorrect assumptions and invalid states clearly
   rather than masking them behind quiet fallback behavior.
7. **Prefer same-change documentation and contract updates** — When behavior, assumptions,
   interfaces, or standards change, update the relevant docs, specs, RFCs, or standards in the
   same change rather than relying on follow-up cleanup.
8. **Prefer verification depth over throughput** — Quality beats quantity. For non-trivial work,
   verification should be deliberate and risk-scaled. Re-check important changes before merge
   rather than assuming the first pass was sufficient.
9. **Take pride in the work, but evaluate feedback on merit** — Good engineering work should be
   defended with rigor, not ego. Incorporate valid feedback quickly, stay humble about blind spots,
   and push back clearly on incorrect, weak, or scope-distorting claims.

## Recommended Structure

```text
about/craft-and-care/
├── README.md                          # Index, scope boundary, reading order
├── engineering-bar.md                # Definition of done, maintainability, clarity, change hygiene
├── testing-and-verification.md       # Evidence standards, regression discipline, verification expectations
├── observability-and-operations.md   # Logging, metrics, tracing, readiness, rollback, operational care
├── interfaces-and-dependencies.md    # API/interface hygiene, compatibility, deprecation, dependency policy
├── review-and-documentation.md       # Review quality, author/reviewer duties, doc update expectations
├── security-and-secrets.md           # Least privilege, secret handling, unsafe-default hygiene
└── performance-discipline.md         # Measurement rules, regression standards, benchmark discipline
```

## Core Files

### `engineering-bar.md`

Must answer:
- What makes a change complete here?
- What clarity and maintainability standards are non-negotiable?
- What kinds of hidden complexity, unclear naming, dead paths, or partial fixes are unacceptable?
- Which cleanup-vs-compatibility, simplicity-vs-cleverness, explicitness-vs-magic, fail-fast-vs-fallback, verification-depth, review-posture, and durable-fix biases are expected by default?

### `testing-and-verification.md`

Must answer:
- What evidence is required for different classes of change?
- What regression protection is expected for bug fixes and risky refactors?
- What must be verified before merge or release?
- What observability evidence or diagnostic instrumentation is required for failure-prone paths?
- When should the system fail loudly versus degrade gracefully?
- How should verification depth scale with change risk?

### `review-and-documentation.md`

Must answer:
- What kind of review feedback should block a merge?
- What are the obligations of the author versus the reviewer?
- When behavior changes, what documentation must be updated?
- Which docs, contracts, or specs must be updated in the same change rather than deferred?
- How should valid feedback be incorporated, and what kind of feedback deserves principled pushback?

## Situational Files

Add when the project's risk profile justifies them:

| File | Add when... |
|------|-------------|
| `observability-and-operations.md` | Runtime behavior, production diagnosis, rollback, or on-call health matters |
| `interfaces-and-dependencies.md` | Public interfaces, compatibility, external dependencies, or deprecations matter |
| `security-and-secrets.md` | Sensitive data, privilege boundaries, or secret handling matter |
| `performance-discipline.md` | Hot paths, performance regressions, or capacity planning matter materially |

## Belongs Here

- Definition of done for non-trivial changes
- Test and verification discipline
- Review quality expectations
- Documentation update expectations
- Observability and operational readiness standards
- Cleanup expectations for dead internal code paths and same-repo migrations
- Explicitness and anti-magic expectations
- Fail-fast and fallback discipline
- Verification-depth expectations
- Review posture and feedback-handling expectations
- API/interface change hygiene
- Dependency admission and upgrade standards
- Maintainability and clarity expectations
- Security hygiene
- Performance discipline as an engineering practice

## Does Not Belong Here

- Mission, identity, philosophy, and non-goals: those belong in `heart-and-soul`
- Wire-level contracts, state machines, schemas, and RFC decisions: those belong in `law-and-lore`
- Normative feature behavior: that belongs in `spec-and-spine`
- Component maps, boundaries, deployment, and data-flow topology: that belongs in `lay-and-land`
- Tool recipes, CI commands, or vendor-specific runbooks: link to them from here if needed, but keep this pillar standards-level

## Writing Standards Docs

### Do

- State standards as reviewable expectations with clear violation cases
- Keep language stack-neutral and durable
- Prefer evidence questions over slogans
- Explain the reason for each standard when it is not obvious
- Cross-link the other pillars where the standards apply
- Make cleanup, simplicity, explicitness, fail-fast, observability, verification-depth, feedback-handling, same-change-doc-update, and durable-fix expectations explicit enough that a reviewer can reject a change for violating them

### Don't

- Write generic "follow best practices" filler
- Turn this pillar into a dumping ground for all engineering opinions
- Prescribe tools when the real requirement is an outcome
- Re-state product requirements or architecture details
- Confuse standards with detailed operating procedures
- Preserve dead internal compatibility layers, clever abstractions, or under-instrumented failure paths by default unless the project explicitly says to
- Normalize silent fallback behavior, undocumented behavioral changes, or "we'll update the docs later" as the default way of working

## Maturity Levels

| Level | Signal |
|-------|--------|
| Absent | Execution standards live only in PR comments, tribal memory, or CI folklore |
| Nascent | Some quality guidance exists but is scattered or generic |
| Structured | `about/craft-and-care/` exists with an authored engineering bar and verification discipline |
| Mature | Standards are project-specific, cross-linked, maintained, and actively used in review and implementation |

## Evolution

This pillar should evolve more slowly than code but faster than doctrine. Update it when:

1. Repeated review findings reveal an implicit standard that should be made explicit
2. Operational incidents expose missing care requirements
3. The project's scale or risk profile changes
4. The team decides a previously informal quality bar is now mandatory
