# Review Veracity Gate

**Phase 3.5** procedure for `project-review`. Run this before Phase 4 delivery.
Gate every Critical/High/P0/P1 finding and the top roadmap items. Nothing below
`[Confirmed]` enters the risk register or planning handoff.

---

## What Gets Gated

Gate **all** of the following before delivery:

- Every finding classified Critical or High severity
- Every P0 or P1 recommendation
- Every top-roadmap item (the first three items in each roadmap tier)
- Any claim about existing files, paths, scripts, or process that informs the verdict

Lower-severity findings (P2/P3/Medium/Low) may pass without a full gate pass,
but must be demoted immediately if contradictory evidence surfaces while
checking higher-severity claims.

---

## Six-Step Procedure Per Claim

Run all six steps for every gated claim. Do not skip steps because a claim
sounds plausible.

### Step 1 — Re-open the named file/path

Open the exact file named in the claim. If the claim does not name a specific
file, identify the most authoritative source (SKILL.md, script, config, spec)
and open that.

- If the path does not exist: classify `[Incorrect]` (path nonexistent).
- If the file exists but has moved: classify `[Overstated]` and note the
  canonical location.

### Step 2 — Search for contradictory evidence

Using **exact terms from the claim**, search the opened file for:
- Explicit statements that contradict the claim
- Behavior, configuration, or instructions that make the claim impossible
- Context that limits what the claim says is unlimited, or vice versa

Record what you searched for and what you found (or did not find).

### Step 3 — Verify referenced paths exist

For every path the claim names:
1. Confirm it exists in the repository (not just referenced in docs).
2. Confirm it is the path stated (not a similar-looking one).
3. Confirm the relevant content is at the stated path (not a stub or redirect).

Nonexistent paths → `[Incorrect]`. Stale paths → `[Overstated]`.

### Step 4 — Verify process claims against actual artifacts

For claims about workflows, scripts, signoff, or conventions:
- Check the actual SKILL.md, script, config, or CI file — not the README or
  an external reviewer's description of it.
- Confirm the claim matches what the artifact actually says.

Process claim not supported by any artifact → `[Unverifiable]`.
Process claim contradicted by an artifact → `[Incorrect]`.

### Step 5 — Classify

Assign exactly one label:

| Label | When to use |
|-------|-------------|
| `[Confirmed]` | Supported by artifact evidence; no meaningful contradictory evidence found |
| `[Overstated]` | Partially true but exaggerated in scope, severity, or prevalence |
| `[Incorrect]` | Contradicted by evidence, or a stated path/file does not exist |
| `[Unverifiable]` | Cannot be checked without runtime execution or local-checkout evidence not available in this session |

### Step 6 — Act on the classification

| Classification | Required action |
|----------------|-----------------|
| `[Confirmed]` | Keep in risk register / roadmap. Add both supporting and contradictory evidence checked to the finding body. |
| `[Overstated]` | Demote severity by at least one tier. Rewrite the claim to reflect actual scope. Keep in risk register at lower severity. |
| `[Incorrect]` | Remove from risk register and roadmap. Add to Veracity Ledger with invalidating evidence. |
| `[Unverifiable]` | Remove the unproven claim from risk register/roadmap. Add it to the Veracity Ledger and, when plausible impact is material, to an Evidence Gaps lane with evidence target, owner, blocking status, bounded investigation, and revisit trigger. |

---

## Special Evidence Rules

### Formatting, line-length, and script-invocation claims

These claims require **one of**:
- Local-checkout evidence: you ran the file locally and observed the behavior
- GitHub-blob evidence: you read the raw file bytes at a specific commit SHA
  via the GitHub blob API or `git show`

**Raw web rendering, parser output, or preview renderers are insufficient.**
GitHub renders Markdown differently from raw bytes; line wrapping in previews
does not reflect actual file line lengths. If you cannot produce local-checkout
or blob evidence, classify the claim `[Unverifiable]`.

### P0/P1 survivability requirement

A P0 or P1 that survives the gate **must** include in its finding body:

```
Supporting evidence: <file:section or command output>
Contradictory evidence checked: <what was searched, what was not found>
```

A P0/P1 without both fields fails the gate.

---

## Veracity Ledger

Every invalidated claim goes into the Veracity Ledger (Appendix D of
`report-template.md`). The ledger:

- records what the original claim said
- records its final classification
- records the invalidating evidence or reason for unverifiability
- is **excluded** from the risk register, roadmap, and handoff packet

The ledger is included in the delivered report as an audit trail. Reviewers
and project-direction planners must not treat the invalidated claim as fact.
An explicitly separated Evidence Gaps lane may be planning input only for the
investigation needed to obtain evidence, never for the claimed remediation.

### Evidence gap entry format

```markdown
| Unknown | Why material | Evidence sought | Owner | Blocking? | Investigation | Revisit trigger |
|---------|--------------|-----------------|-------|-----------|---------------|-----------------|
```

### Ledger entry format

```
| Prior claim | Classification | Invalidating evidence / reason |
|-------------|----------------|-------------------------------|
| {exact claim text} | [Incorrect] / [Overstated] / [Unverifiable] | {file, section, search term, or reason} |
```

---

## Gate Completion Criteria

The gate is complete when:

1. Every gated claim has a classification label.
2. Every `[Incorrect]` and `[Unverifiable]` claim is absent from the risk
   register and roadmap.
3. Every `[Overstated]` claim has been demoted and rewritten.
4. Every surviving P0/P1 includes supporting + contradictory-evidence-checked
   fields.
5. The Veracity Ledger contains all invalidated claims.

If the gate removes every P0/P1 finding, the verdict must be revised downward
accordingly and the removal noted in the Executive Summary.

---

## Fixture Reference

`tests/fixtures/third-party-overclaims/` contains a worked example of a flawed
third-party review with nonexistent paths, overclaimed routing conflicts,
raw-render formatting claims, missing-signoff claims contradicted by files, and
P0s that must demote. Read it as a calibration example before running the gate
on an unfamiliar review.
