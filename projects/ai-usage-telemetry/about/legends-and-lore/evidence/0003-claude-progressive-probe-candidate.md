# Candidate Evidence 0003: Claude Code 2.1.227 Progressive-Observation Probe

**Status:** Candidate evidence; non-normative and not accepted
**Date:** 2026-08-13
**Scope:** `aib-alo` only
**Artifact class:** `about/legends-and-lore/evidence/` candidate evidence
**Reader:** accepting owner, successor-change author, and independent high-risk privacy/accounting reviewers
**Retirement:** Retain immutable history until a successor owner decision accepts replacement evidence/contract bytes or rejects this candidate. Do not rewrite this record; link a successor decision instead.

This is a separate candidate-evidence lane. It does not edit, replace, or reinterpret accepted RFC 0001, accepted 0001 evidence, Decisions 0002-0004, the active OpenSpec change, candidate 0002, or `aib-tvp`. It activates no profile, proposes no replacement contract bytes, and does not authorize an adapter, ledger, sink, release, or merge.

## Disposition

**Unresolved.** The one authorized Bubblewrap probe attempt stopped before the pinned Claude target was launched. The in-namespace loopback preparation did not establish the positive control, so the fail-closed network guard emitted a safe unresolved summary with `target_started=0`, `target_completed=0`, and `loopback_mock_connections=0`.

The safe summary's nonzero `default_route_count=1` is a deliberately conservative control-failure marker from the loopback-setup failure. It is not a claim that a routable external default route was observed. No target stdout, stderr, request body, response body, header, session record, or scalar native identity left sandbox tmpfs. No fallback executable, host target run, retry, or guard relaxation occurred.

A non-observation can become `confirmed-current-contract` only after a future authorized run proves every predeclared negative oracle and containment control. This attempt did not meet that threshold and must not be read as negative producer evidence.

| Subject | Result | Effect on current accepted contract |
|---|---|---|
| Claude Code 2.1.227 repeated usage-bearing observations under one native `(sessionId, requestId)` | **Unresolved**: no target process launched because the loopback positive control was unavailable. | No contract change or profile activation is justified. |
| Candidate 0003 containment harness | **Executed fail-closed**: seven deliberate containment mutations rejected before launch; the one actual probe attempt stopped before target launch. | Candidate-only harness evidence; it does not prove a production parser, source mount, or provider protocol. |

## Exact build and evidence boundary

The launcher resolves one local `claude` executable internally and verifies the following pin before it constructs the target command. It exports the build identity only, never the resolved host path.

| Build field | Required value | Result |
|---|---|---|
| Supported build | `2.1.227` | Pass before the one probe attempt |
| SHA-256 | `6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6` | Pass before the one probe attempt |
| Fallback executable or host invocation | prohibited | None used |

The build pin identifies only the tested local executable. It is not a vendor format promise and it does not make a private on-disk record format accepted.

## Predeclared synthetic matrix and independent oracle

[`fixture_0003.json`](./0003/fixture_0003.json) is wholly synthetic. It stores only case labels, relation classes, the build pin, and the safety contract. It contains no prompt, response, credential, real path, account identifier, raw session JSONL, or native scalar identity.

The independent [`verify_0003_structural_oracle.py`](./0003/verify_0003_structural_oracle.py) requires all eight cases and rejects four deliberate mutations. It establishes the predeclared classification rules; it does not assert that any producer record was observed.

| Synthetic case | Required structural relation | Expected oracle disposition |
|---|---|---|
| exact replay | same pair, timestamp, message, model, and amounts | `duplicate` |
| one-request progressive stream | same pair, changed timestamp, stable message/model, monotone increase | `confirmed-contract-gap` if a real complete persisted observation proves it |
| changed timestamp | same pair with changed timestamp and no monotone evidence | `identity-collision` |
| monotone counter | same pair, changed timestamp, stable message/model, monotone increase | `confirmed-contract-gap` if real producer evidence proves it |
| decreasing counter | same pair with a decrease | `identity-collision` |
| malformed record | malformed structural form | `recognized-malformed` |
| incomplete record | incomplete tail | `incomplete-tail` |
| nonconforming identity reuse | same pair but changed message/model | `identity-collision` |

`confirmed-contract-gap` is intentionally narrow: a future authorized producer run would need at least two complete persisted usage-bearing observations with the same native pair and the predeclared monotone semantics. It would identify, but not replace, the candidate impact surfaces: RFC 0001 `§ Evidence Baseline` and `§ Source-Specific V1 Attribution → Claude Code sessions`, plus `REQ-source-adapter-profiles-005` and `REQ-source-adapter-profiles-006`. A successor owner decision would still have to select and accept any replacement bytes.

## Containment design and capture controls

The host launcher is [`claude_progressive_probe_0003.py`](./0003/claude_progressive_probe_0003.py). It admits only a plan with Bubblewrap user, PID, and network namespaces; a cleared environment containing exactly a synthetic mock credential/config; and the following path classes:

| In-sandbox class | Access | Boundary |
|---|---|---|
| Standard loader/runtime paths | read-only | Required shell, Python, loader, and shared libraries only |
| Pinned executable | read-only at a synthetic target path | The exact verified target only |
| Candidate probe/mock code | read-only | This 0003 runtime directory only |
| Synthetic home, work, output, and temporary locations | empty tmpfs | No host home/config/session/workspace/output bind |

The helper starts its mock only on loopback and deliberately never calls `recv`: target request headers and bodies are not materialized by the mock. It proves a positive loopback canary before any target start, requires no non-loopback interface/default route, captures target stdout/stderr only under sandbox tmpfs, and lets only a schema-checked summary cross the boundary. That summary allows build pin, path classes, type/count/equality/direction assertions, control totals, and one disposition; it rejects raw-output-like keys or unregistered nested fields.

[`exercise_capture_controls_0003.py`](./0003/exercise_capture_controls_0003.py) ran every deliberate mutation without launching a target. It rejected exactly:

1. missing network namespace;
2. host-home/config bind;
3. broad source bind;
4. inherited proxy environment;
5. non-loopback route declaration;
6. host raw-output capture; and
7. build-pin mismatch.

The result was **seven mutations rejected and zero target launches**. Focused tests additionally prove unknown or content-bearing subtrees cannot re-enter the fixed projection paths, and that content values are scanned bytewise rather than decoded or sliced into application strings.

## One executed probe attempt

The one target-capable invocation was run through the host launcher exactly once. Its safe summary was:

| Safe summary category | Result |
|---|---|
| Build pin | required version and SHA-256 |
| Path classes | synthetic executable; read-only candidate code; tmpfs home/work/output; loopback-only network |
| Structural projection type | explicit safe fields only |
| Target starts/completions | `0 / 0` |
| Loopback canary/mock connections | `0 / 0` |
| Complete usage observations | `0` |
| Same-native-pair/progressive groups | `0 / 0` |
| Malformed/incomplete counts | `0 / 0` |
| Non-loopback interface/connection totals | `0 / 0` |
| Default-route control total | `1` fail-closed marker |
| Disposition | `unresolved` |

Afterward, harmless no-target namespace diagnostics showed that loopback could not be brought up in that exact unprivileged containment setup. They did not open the target, a session source, a credential store, a host home, or an external network path. This is a containment/environment limitation to resolve only through a fresh owner-authorized candidate run; it is not permission to alter the guard in this evidence lane.

After the fail-closed result, a unit-only hardening change replaced the never-reached target argument with an empty argument and added its non-launching regression test. It did not invoke Bubblewrap, start the target, inspect a source, or retry the probe. The recorded execution result remains the same unresolved no-target result; the following digests identify the final review artifact, not a second producer attempt.

## Artifact digests

All hashes below are for code-owned candidate artifacts, not source records.

| Artifact | SHA-256 | Purpose |
|---|---|---|
| `0003/fixture_0003.json` | `11bc385d4dbb5fb59aea2e53bd3134b42a6aea351ab39146388de3bf6d531b4e` | Fully synthetic structural matrix |
| `0003/verify_0003_structural_oracle.py` | `2585565d1853e9489664eb5e22fa172f0fe0178447f2bebcd7a946d972860caa` | Independent fixture oracle and mutation checks |
| `0003/claude_progressive_probe_0003.py` | `4d74adc92603674cf2b98f42ec221f963a157c95a9ef13bddc145df99e47f57d` | Fail-closed host launcher and summary validator |
| `0003/runtime/inner_probe_0003.py` | `3ac1e51d1c0d4f30363f4f46efb21f32bc920e2da9edbcc5f8679e34fa449197` | In-namespace loopback/control/structural helper |
| `0003/exercise_capture_controls_0003.py` | `468d099363596a22708a4f4657d866bd4c87c3e83832663ca588bc27a0c8bc41` | Executed containment-mutation controls |

## Accepted-byte integrity

The following accepted surfaces were sha256-checked from this branch and remain outside the candidate patch: RFC 0001; all three accepted 0001 evidence files; Decisions 0002, 0003, and 0004; the active OpenSpec design; and the active `source-adapter-profiles` and `event-identity-and-normalization` specifications. The final diff must contain only `about/legends-and-lore/evidence/0003-...` and `about/legends-and-lore/evidence/0003/...` paths.

## Evidence Run Ledger

All commands below were run from `projects/ai-usage-telemetry` unless noted. They are listed to make the safe result reproducible; no command passes a host home, source, credential, workspace, proxy, session, sink, or network endpoint to the target.

The host path for the resolved executable is deliberately not retained. In the command grammar below, angle-bracketed source terms are audited **path classes**, not stored paths or identities. The launcher builds this fixed Bubblewrap envelope before executing the in-sandbox helper:

```text
bwrap --die-with-parent --new-session --unshare-user --unshare-pid --unshare-net --uid 1000 --gid 1000 --clearenv --proc /proc --dev /dev --tmpfs /tmp --chmod 1777 /tmp --tmpfs /sandbox-home --chmod 0777 /sandbox-home --tmpfs /sandbox-work --chmod 0777 /sandbox-work --tmpfs /sandbox-output --chmod 0777 /sandbox-output --dir /opt --dir /opt/claude --dir /probe --dir /usr --dir /usr/bin --ro-bind <standard-runtime:/bin> /bin --ro-bind <standard-runtime:/lib> /lib --ro-bind <standard-runtime:/lib64> /lib64 --ro-bind <standard-runtime:/usr/bin/python3> /usr/bin/python3 --ro-bind <standard-runtime:/usr/lib> /usr/lib --ro-bind <standard-runtime:/usr/lib64> /usr/lib64 --ro-bind <pinned-executable> /opt/claude/claude --ro-bind <candidate-probe-code> /probe/runtime --setenv <six-synthetic-allowlisted-pairs> --chdir /sandbox-work -- /usr/bin/python3 /probe/runtime/inner_probe_0003.py
```

| Command | Expected safe result | Actual safe result |
|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s about/legends-and-lore/evidence/0003/tests -p 'test_*.py' -v` | Containment, summary, fixture, projection, and inner-helper tests pass without target launch. | Pass; 29 focused tests. All target-launch assertions in containment controls were zero. |
| `PYTHONDONTWRITEBYTECODE=1 python3 about/legends-and-lore/evidence/0003/verify_0003_structural_oracle.py` | Eight predeclared synthetic cases and four mutations are validated without a target. | Pass; eight cases and four mutations rejected. |
| `PYTHONDONTWRITEBYTECODE=1 python3 about/legends-and-lore/evidence/0003/exercise_capture_controls_0003.py` | Every containment mutation rejects before target launch. | Pass; seven mutations rejected and zero target launches. |
| `python3 -m json.tool about/legends-and-lore/evidence/0003/fixture_0003.json >/dev/null` | Fixture JSON is valid and emits no values. | Pass. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile about/legends-and-lore/evidence/0003/*.py about/legends-and-lore/evidence/0003/runtime/*.py about/legends-and-lore/evidence/0003/tests/*.py` | Candidate Python files compile. | Pass; generated bytecode was removed before staging. |
| launcher-generated Bubblewrap envelope above | Exact mount plan, clear environment, tmpfs paths, and read-only probe code are available before target launch. | Constructed only after pin and containment assertions; no host home/config/source/output class was admitted. |
| `/bin/ip link set lo up` inside the envelope | Loopback canary prerequisite must be available before target launch. | Fail-closed: loopback setup failed and no target was started. |
| `socket.create_connection(("127.0.0.1", 18080))` inside the envelope | The loopback canary must connect before any target start. | Not reached because loopback setup failed. |
| `/opt/claude/claude -p '' --output-format json --permission-mode plan` inside the envelope | The only target command can start only after all network controls pass. | Not reached; `target_started=0`, `target_completed=0`. |
| `python3 about/legends-and-lore/evidence/0003/claude_progressive_probe_0003.py --execute` | One Bubblewrap-only target-capable probe; success requires loopback canary and no external route/interface before target start. | Completed safely as `unresolved`; the guard prevented target launch (`0 / 0` starts/completions). This command must not be rerun in this candidate lane. |
| `openspec validate --all --strict` | Active change validates with zero failures. | Pass; 1 item passed, 0 failed. |
| `UV_OFFLINE=1 uv run ../../skills/personal/th-projects/scripts/spec-trace-check.py . --authoring` | Authoring trace has zero errors and warnings. | Pass; 100 requirements, 100 IDs, 0 errors, 0 warnings. |
| `bash ../../skills/personal/th-projects/subskills/project-shape/scripts/shape-scan.sh .` | Product shape/link route remains mature and candidate-only addition does not break it. | Pass; `MATURE_TRACEABILITY_GATE=PASS`. |
| candidate-local-link, `git diff --check`, and accepted-surface SHA-256 checks | Links resolve, no whitespace errors, and all accepted/active bytes match the baseline. | Pass; candidate-local links resolved, no whitespace errors, and accepted/active byte integrity passed. |

## Review and successor gate

This candidate requires a fresh independent high-risk privacy/accounting review at the exact draft PR head. Review must verify the no-materialization claim at the scanner boundary, every mount/environment/network guard, the safe-summary schema, the one-run ledger, and the explicit unresolved disposition. It must not treat a green harness suite, a running Bubblewrap process, or absence of a session record as producer confirmation.

No review thread is resolved here. No merge is authorized. A later owner may authorize a new isolated run only after deciding how to make the loopback positive control available without broadening mounts, privileges, environment, or data access.
