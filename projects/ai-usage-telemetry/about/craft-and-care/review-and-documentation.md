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
