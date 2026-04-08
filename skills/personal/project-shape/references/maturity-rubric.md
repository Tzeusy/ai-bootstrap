# Project Shape Maturity Rubric

This rubric defines the scanner's intended thresholds. Prefer conservative scoring. If a project looks partly mature and partly scaffolded, score the lower state.

## Levels

### Unshaped

- Zero pillars detected
- Knowledge about the project lives only in README fragments, tickets, or code comments

### Nascent

- Exactly one pillar exists, or the project has scattered philosophy/design notes without a stable home
- No reliable agent navigation

### Structured

- Two or three pillars exist
- Some authored content is present
- Traceability is partial or absent

### Shaped

All of the following:

- Four pillars exist in canonical or recognized legacy locations
- Core content is authored, not just scaffolded
- Local skills exist or are close to installation

Any of the following keeps a project in `shaped` rather than `mature`:

- Scaffold markers or placeholder tables remain
- Local skills are still generic templates
- Doctrine has no explicit non-negotiable rules
- RFCs do not reference doctrine
- Specs do not cite sources or scenarios
- Topology docs do not cross-link the other pillars

### Mature

All of the following:

- Four pillars are authored and maintained
- Local skills are installed and customized
- Doctrine contains explicit numbered rules
- Every authored RFC references doctrine or principles
- Every authored spec includes source traceability and scenarios
- Topology docs describe boundaries and cross-link doctrine/RFC/spec context
- The project can be navigated by an unfamiliar human or LLM without guesswork

## Traceability Heuristics

The scanner currently uses conservative text heuristics rather than full semantic parsing:

- **Doctrine rules**: numbered items in authored `vision.md`
- **RFC doctrine references**: mentions of doctrine, principles, `heart-and-soul`, or `vision.md`
- **Spec source references**: `Source:` lines in `spec.md`
- **Spec scenarios**: `Scenario:` sections or `WHEN/THEN` scenario bullets
- **Topology cross-links**: mentions of RFCs, doctrine, specs, or pillar names in topology docs

These heuristics are intentionally strict. False negatives are preferable to flattering false positives.
