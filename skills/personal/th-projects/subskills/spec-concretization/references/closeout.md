# Closeout

Step 6. Output: the run report, an appended convergence record, and — when
owner gates exist — one reviewed questionnaire packet. A run that cannot be
re-run without duplicating its own work is not done.

## Audit-key

Every bead this skill creates carries, in `design`:

```
Audit-key: spec:<sub-kind>:<capability>[:<surface-id>]
Requirements: REQ-<capability>-NNN[, …]   # or: none (code-ahead <surface-id>)
```

`<sub-kind>` is `missing`, `partial`, `unverified`, `defect`, `remove` (owner-approved removal), `docs` (documentation correction),
`deprecate`, `investigate`, or `closeout` (the reusable verification path,
which carries `Verifies:` instead of `Requirements:`). Requirement-backed beads key on the
capability and list their IDs; code-ahead beads have no ID yet, so they add
the row's surface-id ([code-ahead.md](code-ahead.md) defines the format).
Keys name surfaces, not lines, so they survive refactors. The
`Requirements:` line is the join key for ownership; audit-keys group beads
and link them to a capability, and need not be unique.

## Run report

Written for a cold reader: outcome first, complete sentences, terms defined.
Always save it to `docs/reviews/<date>-spec-concretization.md`, creating the
directory if the project has none (audit mode excepted: it reports inline).
The ledger and direction's receiver protocol reads the last convergence record from
there; an inline-only report makes the next run start over as a first run.

```markdown
# Spec concretization <date>

## Outcome
<2-4 sentences: concrete share, what moved this run, what is now owned,
what waits on the owner.>

## Mapping summary
<count per class and sub-kind; per-capability table or link>

## Code ahead — landed and gated
<bookkept requirements (ID, spec path, doctrine cited); defects filed;
immaterial rows; owner items>

## Spec ahead — reconciliation and plan
<coverage matrix; per-row and per-bead state per spec-ahead.md § 3; epic and
bead IDs with ordering>

## Escalations
<handoffs to project-direction or feature-request, each with its reason>

## Unknowns
<each with the evidence that would decide it and its investigation bead>

<convergence record>
```

## Convergence record

Appended at the end of the report:

```
Concretized: <sha> on <date>
Rows: <n> — concrete <a> · spec-ahead <b> · code-ahead <c> · divergent <d> · unknown <e>
Actions: specs bookkept <f> · beads new <g> · attached <h> · extended <i> · superseded <j> · reopened <k> · regressed <r> · closed <l>
Notes: owned <u> · held <n> · drifted <o> · orphans <p> · merged <t> · foreign <q> · escalated <s>
Owner gates: <m> — packet <path or "none">
```

The ledger prints the last record; the next run cites the previous SHA and
reports movement. Same head → zero actions and zero new notes (notes are
skipped when the bead already carries one at that SHA). Remediated head → `new 0 ·
reopened 0` and spec-ahead/code-ahead counts at or near zero: report that as
the loop closing, not as "nothing found".

## Owner dossier

Owner gates from both flows (`concretize:adopt`, `concretize:conflict`,
`concretize:horizon`, `concretize:deprecate`, `concretize:verdict`,
`concretize:diverge`) become one packet, built with
[user-questionnaire](../../user-questionnaire/SKILL.md) steps 2-7 — draft,
fresh-subagent adversarial review, validate, serve — after the convergence
record is written:

```bash
Q="<th-projects>/subskills/user-questionnaire/scripts"
PACKET=~/.tmp/user-questionnaire/<repo>-<date>-spec-concretization/packet.md
uv run "$Q/validate_questionnaire.py" "$PACKET" --require-review-ready
uv run "$Q/questionnaire_web.py" serve "$PACKET"      # last line: QUESTIONNAIRE_URL=…
```

Each item's evidence cites the report and `file:line` at the audited SHA, and
carries the draft requirement or delta text so the owner decides on exact
wording. Decision IDs reuse the audit vocabulary, so re-runs dedupe: an item
answered in a prior packet (`Agreed`, `Rejected`, `Held` with its trigger
unmet) is not re-asked unless its evidence changed; the ledger prints prior
decision IDs with their states.

The report ends with the `QUESTIONNAIRE_URL=` line. The next session runs
`questionnaire_web.py ingest "$PACKET"` first, and routes `Agreed` items only
when the answers carry `apply_now: true` or the owner asks
(user-questionnaire's routing rule), each through its owning path: adopt → bookkeeping (flow A § 4); remove → a
`spec:remove:<capability>` bead; amend doctrine → project-shape's amendment
path; amend spec → feature-request amendment, then flow B for the code side.

No owner gates → write `Owner gates: 0` and publish nothing.

## Session close

Bead mutations land in the shared tracker as you make them; follow the target
repository's session-close protocol for mirroring and pushing spec edits and
the report.
