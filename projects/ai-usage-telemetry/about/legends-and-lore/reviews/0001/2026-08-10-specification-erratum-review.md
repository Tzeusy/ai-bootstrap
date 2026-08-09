# RFC 0001 Specification-Authoring Erratum Review

**Date:** 2026-08-10

**Candidate RFC SHA-256:** `126fc0214abb76f1a2f207bed1c3baf629757a3b281abf9d0e4a92b52b7e0117`

**Prior accepted RFC SHA-256:** `90f85ab1e5c50ee28ad51f6efeae3245f9908187985c2a12e1ba237db49f3f11`

**Review result:** PASS — no behavior change; no launch-gate rerun required

## Erratum

RFC 0001 said the image had four canonical filesystem targets after the
privacy remediation had removed the fourth table row: the rejected Claude
quota-cache mount. The current table, V1 scope, and topology all retain exactly
three canonical source/state targets: the read-only Claude sessions target,
the read-only Codex sessions target, and writable `/data`.

The correction changes `four` to `three canonical source/state` and clarifies
that the read-only TOML file is a separate configuration surface whose exact
path and preflight contract belong to `portable-runtime-and-release`. It also
clarifies that `/tmp` is ephemeral container scratch, not a canonical
host-backed source/state target.

## Evidence and review

- Repository history at `fca9b6e^` contained the fourth Claude quota-cache row;
  `fca9b6e` removed that row and the matching topology entry after privacy
  review but left the stale numeral.
- RFC 0001 continues to make Claude quota unavailable, forbids speculative
  quota/cache and authentication-store mounts, and permits no credential-backed
  quota lookup.
- `about/lay-and-land/deployment.md` independently distinguishes the three
  source/state surfaces from the read-only TOML configuration surface.
- A fresh-context reviewer compared the candidate against the history, current
  RFC, topology, configuration contract, V1 scope, and immutable READY record.
  It found no reopened doctrine, privacy, retention, source, or runtime
  behavior and confirmed the candidate digest above.

The immutable READY administration at `96ba99d` remains evidence that the
accepted shape was ready to enter specification. This erratum follows the
already-adopted same-change propagation path; it neither rewrites that gate
record nor invents a new gate verdict.

## Disposition

Accepted as a reviewed no-behavior-change erratum under Owner Decision 0001's
standing direction to apply quality-gate fixes and publish the converged
project shape and specifications. The corrected RFC digest supersedes only the
stale accepted-byte digest; every substantive boundary remains unchanged.
