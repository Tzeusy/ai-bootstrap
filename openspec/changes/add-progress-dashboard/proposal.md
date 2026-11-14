## Why

A running workflow should expose its progress, findings, child-agent work and
observed usage in one place. Repeatedly navigating agent conversations or asking
the parent for status spends attention and tokens. Browser steering should be
durable without adding model polling cycles or a second task authority.

## Authority and scope

Sign-off: owner request in this session, 2026-11-14, including the explicit
refinement to a reusable `th-projects/subskills/progress-dashboard` skill and the
requirement to emphasize token efficiency. This records that bounded request;
it does not adopt new doctrine or authorize production/network changes.

Implementation and verification are tracked by aib-dwp. The shared skill owns
workspace persistence, server lifecycle, UI assets, incremental usage adapters
and feedback transport. Beads loopers call it through a thin instruction after
the standalone helper is verified. Other workflows can use it directly.

## Impact

Adds a stdlib-only per-session helper and static browser assets. Runtime data
lives in `~/.tmp/<slug>/`, outside tracked source. The server runs only for the
session's lifecycle, defaulting to loopback; it is not a shared service/control
plane. Existing claims, acceptance, independent review and owner gates remain
with the owning workflow. No global runtime hooks or hosted service are added.
