# Craft and Care — Engineering Standards Layer Guide

## Purpose

The engineering standards layer answers **HOW SHOULD WORK BE EXECUTED WELL?** It defines the
quality bar for implementation, verification, review, observability, compatibility, security
hygiene, documentation, and maintainability. It is not product doctrine, not subsystem design,
not feature requirements, and not topology. It is the project's explicit answer to what good
engineering work looks like here.

This pillar should express stack-neutral principles and reviewable expectations. It should tell
humans and agents what evidence, discipline, and care are required, without prescribing vendors,
frameworks, or tools unless the project has separately standardized those choices elsewhere.

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

### `testing-and-verification.md`

Must answer:
- What evidence is required for different classes of change?
- What regression protection is expected for bug fixes and risky refactors?
- What must be verified before merge or release?

### `review-and-documentation.md`

Must answer:
- What kind of review feedback should block a merge?
- What are the obligations of the author versus the reviewer?
- When behavior changes, what documentation must be updated?

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

### Don't

- Write generic "follow best practices" filler
- Turn this pillar into a dumping ground for all engineering opinions
- Prescribe tools when the real requirement is an outcome
- Re-state product requirements or architecture details
- Confuse standards with detailed operating procedures

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
