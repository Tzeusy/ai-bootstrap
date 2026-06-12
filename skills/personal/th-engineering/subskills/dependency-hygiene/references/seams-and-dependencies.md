# Seams, Depth, and Dependency Categories

Read this when judging whether a module or wrapper earns its existence, where
to place a seam around a dependency, or how to test code that touches one.

## Dependency Categories

Classify each dependency before deciding seam placement and test strategy:

| Category | Definition | Seam policy | Test strategy |
|---|---|---|---|
| **In-process** | Your own modules, same deployable | No seam; call directly | Test through the public interface; never mock (test-rigor bar 5) |
| **Local-substitutable** | Owned infra with a faithful local stand-in (SQLite for Postgres, tmpdir for object store) | Thin constructor-level substitution, not an abstraction layer | Run tests against the local substitute |
| **Remote-owned** | Services you own across a network boundary | Port owned by the caller; adapter per transport (ports & adapters) | Test the port with a fake; contract-test the adapter |
| **True-external** | Third-party APIs you don't control | Owned interface at the boundary, shaped by *your* use, not their API surface | Mock the owned interface; one thin integration test against a sandbox if available |

## Seam Discipline

- **One adapter is a hypothetical seam; two adapters make a real one.** Do
  not build the port/adapter machinery for a second implementation that does
  not exist — note where the seam *would* go and move on.
- **The interface is the test surface.** If testing a module forces you past
  its interface into internals, the module boundary is wrong — fix the shape
  rather than reaching deeper with mocks.
- **SDK-style boundary functions.** Give each external operation its own
  named function (`fetchInvoice(id)`, `placeOrder(req)`) instead of one
  generic fetcher with conditionals; specific functions mock cleanly and
  read as a contract.

## The Deletion Test

To decide whether a module, wrapper, or layer earns its keep, imagine
deleting it:

- If the complexity it held simply **vanishes**, it was a pass-through —
  delete it for real ([cruft-cleanup](../../cruft-cleanup/SKILL.md)).
- If the complexity **reappears in every caller**, the module is doing real
  work — keep it, and consider deepening it (move more of the repeated
  caller burden behind the same interface).

A module is *deep* when its interface is small relative to the work it hides;
deep modules are the payoff of good dependency hygiene.

## Rejected Framings

- **"Depth = implementation lines ÷ interface lines."** Wrong frame: a long
  pass-through is not deep. The frame is *leverage* — how much caller burden
  one small interface removes.
- **"Wrap every third-party library."** Wrapping stable, idiomatic
  dependencies adds a pass-through layer that fails the deletion test. Wrap
  what is volatile, heavy, or likely to be substituted (SKILL.md bar 5).
- **"We might need to swap databases someday."** A hypothetical second
  implementation does not justify a seam today; seams are added when the
  second adapter arrives.

## Provenance

Categories, seam rules, and the deletion test are adapted from
`skills/mattpocock-skills/skills/engineering/improve-codebase-architecture/`
(LANGUAGE.md, DEEPENING.md) and `tdd/mocking.md` in the same package.
