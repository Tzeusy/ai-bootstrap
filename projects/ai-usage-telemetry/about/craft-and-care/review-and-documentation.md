# Review and Documentation

Review is evidence-bearing design work, not a ceremonial approval. These
standards are adopted through the project lifecycle gate.

## Author evidence

Before requesting review, the author records:

- the governing doctrine principle, RFC section, OpenSpec requirement when one
  exists, and affected topology/standard;
- the change-risk class, assumptions, and unresolved boundaries;
- the exact commands or harnesses run, synthetic fixtures exercised, and
  relevant output or artifact locations;
- failure-path, replay/restart, migration, privacy, and multi-architecture
  evidence required by the affected surface; and
- every document or contract changed in the same patch.

An assertion that a process started, a sink accepted one request, or a test suite
was green without the applicable boundary evidence is insufficient.

## Independent blocking review

A reviewer other than the author applies coherence and adversarial lenses to
the stable change. Review blocks integration while any finding could permit
content/credential exposure, lost or duplicate accounting, cursor advance past
unknown or malformed data, masked stream degradation, incompatible persisted
state, ambiguous sink checkpoint ownership, or unsupported runtime behavior.

The author does not resolve a finding by assertion. Each finding receives one
of these explicit dispositions:

- **Accepted:** corrected in a named revision with a concise reason and new
  evidence;
- **Wontfix:** retained with a technical reason, affected risk, and the owner or
  delegated authority who accepted that risk; or
- **Deferred:** linked to an authorized follow-up and blocked from the current
  change whenever the finding is required for its safety or contract.

Unanswered, hidden, or merely acknowledged blocking findings remain blockers.

## Privacy and security review

Independent privacy/security review is mandatory for changes to source mounts,
field projection, extraction or admission registries, identity/fingerprints,
diagnostics, SQLite views, PostgreSQL projection, OTLP attributes/vocabularies,
sink secrets, runtime privilege, or dependency supply chain. The review checks
both non-materialization inside the parser and non-egress across logs, ledger,
views, fingerprints, diagnostics, and both sinks; an output-only check is not
enough.

## RFC review records

RFC review findings and author responses live under
`about/legends-and-lore/reviews/<rfc-number>/`. Each round records reviewer,
date, exact draft revision, section-scoped findings, author response, evidence,
and disposition. An RFC remains Draft until all blocking findings have explicit
dispositions, the revised draft is rechecked, and the human owner records
acceptance. Review conversation outside that record is context, not the
authority trail.

## Same-change documentation

Observable behavior changes update the governing OpenSpec requirement in the
same change once OpenSpec exists. Design-contract changes update the RFC and its
review record; component, data-flow, mount, or deployment changes update
lay-and-land; engineering-expectation changes update craft-and-care. A doctrine
change follows the owner-adoption process and reconciles every affected
downstream artifact before implementation continues.

"Update the docs later" is not an acceptable disposition for a change whose
behavior, boundary, failure mode, or operating contract changed now.

## Governance Artifact Lifecycle

Ownership and retirement are class-based so every artifact has a route without
adding per-file ceremony:

| Artifact class | Accountable owner | Retirement or supersession path |
|---|---|---|
| `about/heart-and-soul/` doctrine and decisions | Tze | Replace doctrine only through an owner decision; keep superseded decisions immutable and remove them from the default route. |
| `about/legends-and-lore/rfcs/` | Tze | Supersede through an accepted successor or amendment with downstream reconciliation; banner and remove the old RFC from the default route, retaining its evidence trail. |
| `about/legends-and-lore/evidence/` and `reviews/` | Tze; maintenance may be delegated | Retain while they support an active contract; when superseded, keep immutable history off the default route and point the active RFC to replacement evidence. |
| `about/lay-and-land/` docs and assets | Tze; maintenance may be delegated | Update or delete in the same change that removes the mapped component, flow, trust boundary, or deployment; archive only useful history off the default route. |
| `about/craft-and-care/` standards | Tze; maintenance may be delegated under adopted doctrine | Consolidate or delete when the project-specific constraint disappears or returns to the repository-wide default, updating every reading route in the same change. |
| `about/README.md` and pillar READMEs | Tze; maintenance may be delegated | Keep only as active routing/status surfaces; update with their sources, and remove when their routed surface is retired. |
| `docs/launch-gate/parameters.md` and `trend.md` | Tze; maintenance may be delegated | Amend parameters with a changelog and fresh parameter review. Freeze the first-spec gate after `READY`; retain its trend as evidence off the ordinary implementation path. |
| Immutable gate/review records | Tze; recording may be delegated | Never rewrite; supersede with a new named-commit record and keep outside the default reading route once its decision is historical. |
| OpenSpec capability and change artifacts | Tze; curation may be delegated | Follow the OpenSpec change/archive process; replace or retire only through a traced delta that updates affected implementation and routes. |

The default path remains the project overview plus one overview per pillar.
Before adding a governance artifact, the author must name its class, reader,
and retirement rule above. A repair should amend an existing owner when that is
clearer; it must not create a new report or validator merely to restate one
finding. Reviews sweep for orphaned routes and compare normative versus meta-
artifact growth so evidence records do not outgrow the contracts they protect.
