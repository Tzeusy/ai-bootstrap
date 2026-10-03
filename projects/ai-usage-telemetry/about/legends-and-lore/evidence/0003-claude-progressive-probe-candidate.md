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

The helper starts its mock only on loopback and deliberately never calls `recv`: target request headers and bodies are not materialized by the mock. It proves a positive loopback canary before any target start, requires no non-loopback interface/default route, discards target stdout/stderr to the nested target envelope's `/dev/null`, and lets only a schema-checked summary cross the boundary. That summary allows build pin, path classes, type/count/equality/direction assertions, control totals, and one disposition; it rejects raw-output-like keys or unregistered nested fields.

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

After the fail-closed result, a unit-only hardening change replaced the never-reached target argument with an empty argument and added its non-launching regression test. It did not invoke Bubblewrap, start the target, inspect a source, or retry the probe. The recorded execution result remains the same unresolved no-target result.

## P1-P9 containment, accounting, control-evidence, analysis-consistency, and structural-projection corrections before renewed review

These corrections are unit-only and did not execute Bubblewrap, the target, the loopback canary, a socket, a session source, or a credential. They repair the reviewer-identified boundaries without creating a second producer attempt:

- The target now starts only under a second Bubblewrap user and **nested PID namespace** with a fresh `/proc`. It is the nested namespace init, inherits only `stdin`, `stdout`, and `stderr` redirected to `/dev/null`, and `close_fds=True` closes every other descriptor. The outer reporter and the summary-writing parent are outside that PID namespace, so the target cannot reopen their descriptors through procfs or another inherited-descriptor path.
- The host launcher no longer accumulates `subprocess.run(..., stdout=PIPE)` output. It reads at most one **16,385-byte** bounded safe-summary envelope (16,384 bytes of permitted summary plus one overflow sentinel) in fixed chunks. A timeout, nonzero exit, malformed JSON, oversized envelope, or schema-validation failure returns only the validated, content-free `unresolved` summary.
- Nested target completion now requires a zero exit. A nonzero exit or timeout-after-kill returns `target_started=1`, `target_completed=0` and stops before home inspection or classification; malformed or incomplete structural analysis likewise cannot confirm either contract outcome.
- Every skipped source JSON value now receives complete bytewise JSON grammar validation before it can contribute to an observation: legal string escapes and UTF-8, full numeric grammar (including no leading zero), literals, arrays, and objects. An invalid skipped value is malformed, creates no observation, and cannot confirm either contract outcome.
- The bounded summary reader now feeds an allowlisted bytewise admission scanner rather than whole-document `json.loads`. It admits only the predeclared keys, fixed string literals, bounded nonnegative counters, and disposition bytes. An unregistered key is rejected before its value is parsed, and an opaque or hostile summary value is never decoded or copied into the safe summary object.
- A host-derived confirmation now binds the untrusted summary enum to primitive evidence. The host retains `confirmed-contract-gap` only when target start and completion are exactly one, loopback/mock and canary controls are present, every non-loopback/default-route control is zero, analysis has no malformed or incomplete record, and the complete-observation, same-pair, changed-timestamp, and monotone/progressive counts have the exact relationships produced by the inner analyzer. Any zero-evidence, malformed, incomplete, inconsistent, unsupported `confirmed-current-contract`, or enum-mismatched summary becomes the all-empty schema-valid `unresolved` result. There is no negative-oracle primitive in this candidate, so host-side `confirmed-current-contract` fails closed.
- The host now also requires the exposed analysis aggregate relationships to be inner-classifier reachable: exact-replay groups exit before changed-timestamp, decreasing, nonconforming-reuse, or progressive counters; progressive groups require a changed timestamp and cannot overlap decreasing or nonconforming-reuse groups. A forged aggregate that violates any of those exclusion or coverage relationships becomes the all-empty schema-valid `unresolved` result, even if its enum and independent scalar bounds are valid.
- The proposed aggregate cardinality premise was false: the unique-key `O=4`, `S=2`, `P=1`, `E=0`, `C=1`, `D=0`, `N=0` vector is reachable when a second same-native-pair group has two same-timestamp records with a changing counter. A no-target characterization regression preserves its existing `confirmed-contract-gap` disposition. No host cardinality floor or inner-classifier semantic change is made.
- Both host and inner structural scanners now recognize a JSON-escaped spelling that semantically matches a projected key or projected-prefix key. A literal followed by that escaped semantic duplicate fails before its second projected value is parsed; an escaped projected spelling encountered first also fails before its value is parsed. Escaped unprojected names remain grammar-checked skip-only keys. Every such projected-key ambiguity is malformed, creates no observation, and cannot produce a candidate confirmation.
- Bubblewrap has a fixed, SHA-256-pinned `/usr/bin/bwrap` identity which is mounted read-only at that exact in-sandbox path. Neither the outer containment wrapper nor the nested target wrapper resolves `bwrap` from inherited `PATH`.
- `runtime/attempt_gate_0003.json` is a digest-bound, code-owned consumed-attempt record. The launcher checks it before resolving the target or Bubblewrap and rejects every later `--execute` fail-closed as the validated, content-free `unresolved` result; it opens neither wrapper nor target. A future candidate run needs fresh owner authorization and replacement candidate bytes, not a mutation or removal of this gate.
- Both source-counter decoders now admit only the inclusive signed-64 range `0..9223372036854775807`. They reject `9223372036854775808` and larger values while incrementally decoding the projected counter, so an out-of-range record is malformed before it can create an observation, a progressive group, or any confirmed disposition.

The new hostile-boundary regressions use mocked no-target processes only. They prove the nested descriptor boundary, nonzero/timeout completion gate, inspection bypass, malformed/incomplete-analysis closure, invalid skipped escape/UTF-8/numeric rejection, literal/escaped semantic projected-key and projected-prefix rejection before a second value decode, signed-64 source-counter admission/rejection, host-derived confirmation versus forged zero/control/inconsistent or inner-classifier-unreachable aggregate evidence, the reachable unique-key O4 characterization, allowlisted hostile-summary rejection, fixed-wrapper identity despite a shadowed `PATH`, and consumed-attempt retry denial. The following digests identify the corrected review artifact, not a second producer attempt.

## Artifact digests

All hashes below are for code-owned candidate artifacts, not source records.

| Artifact | SHA-256 | Purpose |
|---|---|---|
| `0003/fixture_0003.json` | `11bc385d4dbb5fb59aea2e53bd3134b42a6aea351ab39146388de3bf6d531b4e` | Fully synthetic structural matrix |
| `0003/verify_0003_structural_oracle.py` | `2585565d1853e9489664eb5e22fa172f0fe0178447f2bebcd7a946d972860caa` | Independent fixture oracle and mutation checks |
| `0003/claude_progressive_probe_0003.py` | `3aeff02535c00704d561b7c28f92f12a3e5eff2aa1a4f141e1a2ff253746f491` | Bounded fail-closed host launcher, source-counter range, semantic control-evidence and inner-analysis aggregate binding, literal/escaped semantic projected-key rejection, wrapper identity, attempt gate, and allowlisted summary admission |
| `0003/runtime/inner_probe_0003.py` | `128e0d800bcdba78c13efe6d02eddec50980b1656b520c4737103d02eec089fc` | Nested-PID in-namespace loopback/control/grammar-complete, signed-64-bounded structural helper with literal/escaped semantic projected-key rejection |
| `0003/runtime/attempt_gate_0003.json` | `296d9c192435acb6a65ce0c18766916e329a916f515fb41bb39c4a96b5eb3fec` | Digest-bound consumed-attempt record that denies retries before launch |
| `0003/exercise_capture_controls_0003.py` | `468d099363596a22708a4f4657d866bd4c87c3e83832663ca588bc27a0c8bc41` | Executed containment-mutation controls |

## Accepted-byte integrity

The following accepted surfaces were sha256-checked from this branch and remain outside the candidate patch: RFC 0001; all three accepted 0001 evidence files; Decisions 0002, 0003, and 0004; the active OpenSpec design; and the active `source-adapter-profiles` and `event-identity-and-normalization` specifications. The final diff must contain only `about/legends-and-lore/evidence/0003-...` and `about/legends-and-lore/evidence/0003/...` paths.

## Evidence Run Ledger

All commands below were run from `projects/ai-usage-telemetry` unless noted. They are listed to make the safe result reproducible; no command passes a host home, source, credential, workspace, proxy, session, sink, or network endpoint to the target.

The host path for the resolved executable is deliberately not retained. In the command grammar below, angle-bracketed source terms are audited **path classes**, not stored paths or identities. The launcher builds this fixed Bubblewrap envelope before executing the in-sandbox helper:

```text
/usr/bin/bwrap --die-with-parent --new-session --unshare-user --unshare-pid --unshare-net --uid 1000 --gid 1000 --clearenv --proc /proc --dev /dev --tmpfs /tmp --chmod 1777 /tmp --tmpfs /sandbox-home --chmod 0777 /sandbox-home --tmpfs /sandbox-work --chmod 0777 /sandbox-work --tmpfs /sandbox-output --chmod 0777 /sandbox-output --dir /opt --dir /opt/claude --dir /probe --dir /usr --dir /usr/bin --ro-bind <standard-runtime:/bin> /bin --ro-bind <standard-runtime:/lib> /lib --ro-bind <standard-runtime:/lib64> /lib64 --ro-bind <standard-runtime:/usr/bin/python3> /usr/bin/python3 --ro-bind <trusted-bwrap:/usr/bin/bwrap> /usr/bin/bwrap --ro-bind <standard-runtime:/usr/lib> /usr/lib --ro-bind <standard-runtime:/usr/lib64> /usr/lib64 --ro-bind <pinned-executable> /opt/claude/claude --ro-bind <candidate-probe-code> /probe/runtime --setenv <six-synthetic-allowlisted-pairs> --chdir /sandbox-work -- /usr/bin/python3 /probe/runtime/inner_probe_0003.py
```

| Command | Expected safe result | Actual safe result |
|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s about/legends-and-lore/evidence/0003/tests -p 'test_claude_progressive_probe_0003.py' -v` | Host containment and closed safe-summary tests pass without target launch. | Pass; 44 host-safe tests, including host-derived confirmation with mocked forged zero/control/inconsistent or inner-classifier-unreachable aggregate evidence normalized to all-empty unresolved; the reachable unique-key O4 aggregate remains admitted; literal/escaped semantic projected key and prefix records are malformed before their second value is decoded; and escaped unprojected keys remain skip-only. The suite also covers all-empty unresolved admission, inclusive signed-64 source-counter admission and one-past rejection, grammar-complete skipped JSON, bounded/allowlisted hostile-summary admission, shadowed-wrapper rejection, consumed-attempt denial, and malformed/oversized/schema-invalid/nonzero/timeout safe-summary regressions. All target-launch assertions in containment controls were zero. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s about/legends-and-lore/evidence/0003/tests -p 'test_0003_structural_oracle.py' -v` | Candidate record, fixture oracle, and digest checks pass without target launch. | Pass; five structural-oracle tests. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s about/legends-and-lore/evidence/0003/tests -p 'test_inner_probe_0003.py' -k incomplete_tail -k malformed_or_incomplete -k network_state -k persisted_same_pair -k reachable_unique_key_o4 -k target_ -k unknown_content -k invalid_skip_only -k signed_64 -k malformed_analysis -k incomplete_analysis -k duplicate_projected -k escaped -v` | Safe inner-helper tests pass without a loopback packet or target launch. | Pass; twenty-one safe inner-helper tests, including literal/escaped semantic projected-key malformed closure before its second value decode, escaped-unprojected skip-only preservation, duplicate projected-key malformed closure, and the reachable unique-key O4 characterization; plus inclusive signed-64 source-counter admission and one-past closure, grammar-complete invalid skipped JSON, nested-PID descriptor containment, nonzero/timeout completion closure, inspection bypass, and raw-stdio discard. Excluded exactly `test_inner_probe_0003.InnerProbeTests.test_loopback_mock_positive_control_accepts_without_reading_request_values` because it opens a loopback client connection, which this correction must not create. |
| `PYTHONDONTWRITEBYTECODE=1 python3 about/legends-and-lore/evidence/0003/verify_0003_structural_oracle.py` | Eight predeclared synthetic cases and four mutations are validated without a target. | Pass; eight cases and four mutations rejected. |
| `PYTHONDONTWRITEBYTECODE=1 python3 about/legends-and-lore/evidence/0003/exercise_capture_controls_0003.py` | Every containment mutation rejects before target launch. | Pass; seven mutations rejected and zero target launches. |
| `python3 -m json.tool about/legends-and-lore/evidence/0003/fixture_0003.json >/dev/null` | Fixture JSON is valid and emits no values. | Pass. |
| `PYTHONPYCACHEPREFIX=<empty-tempdir> python3 -m py_compile about/legends-and-lore/evidence/0003/*.py about/legends-and-lore/evidence/0003/runtime/*.py about/legends-and-lore/evidence/0003/tests/*.py` | Candidate Python files compile without writing into the worktree. | Pass. |
| launcher-generated Bubblewrap envelope above | Exact mount plan, clear environment, tmpfs paths, and read-only probe code are available before target launch. | Constructed only after pin and containment assertions; no host home/config/source/output class was admitted. |
| `/bin/ip link set lo up` inside the envelope | Loopback canary prerequisite must be available before target launch. | Fail-closed: loopback setup failed and no target was started. |
| `socket.create_connection(("127.0.0.1", 18080))` inside the envelope | The loopback canary must connect before any target start. | Not reached because loopback setup failed. |
| `/opt/claude/claude -p '' --output-format json --permission-mode plan` inside the envelope | The only target command can start only after all network controls pass. | Not reached; `target_started=0`, `target_completed=0`. |
| `python3 about/legends-and-lore/evidence/0003/claude_progressive_probe_0003.py --execute` | One Bubblewrap-only target-capable probe; success requires loopback canary and no external route/interface before target start. | The historic one invocation completed safely as `unresolved`; the guard prevented target launch (`0 / 0` starts/completions). The durable consumed-attempt gate now rejects every later invocation before wrapper or target resolution. This command was not rerun. |
| `openspec validate --all --strict` | Active change validates with zero failures. | Pass; 1 item passed, 0 failed. |
| `UV_OFFLINE=1 uv run ../../skills/personal/th-projects/scripts/spec-trace-check.py . --authoring` | Authoring trace has zero errors and warnings. | Pass; 100 requirements, 100 IDs, 0 errors, 0 warnings. |
| `bash ../../skills/personal/th-projects/subskills/project-shape/scripts/shape-scan.sh .` | Product shape/link route remains mature and candidate-only addition does not break it. | Pass; `MATURE_TRACEABILITY_GATE=PASS`. |
| candidate-local-link, `git diff --check`, and accepted-surface SHA-256 checks | Links resolve, no whitespace errors, and all accepted/active bytes match the baseline. | Pass; candidate-local links resolved, no whitespace errors, and accepted/active byte integrity passed. |

## Review and successor gate

This candidate requires a fresh **different** independent high-risk privacy/accounting review at the exact draft PR head. Review must verify the no-materialization claim at the source and summary scanner boundaries, literal/escaped semantic projected-key rejection before the second value decode, the host-derived confirmation predicate, the inner-classifier-reachable aggregate relationships and reachable unique-key O4 characterization, and all-empty normalization, every mount/environment/network/attempt guard, the fixed Bubblewrap identity, the safe-summary schema, the one-run ledger, and the explicit unresolved disposition. It must not treat a green harness suite, a running Bubblewrap process, or absence of a session record as producer confirmation.

No review thread is resolved here. No merge is authorized. A later owner may authorize a new isolated run only after deciding how to make the loopback positive control available without broadening mounts, privileges, environment, or data access.
