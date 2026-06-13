# Subagent Dispatch Template

Use when dispatching investigation subagents for project direction analysis.

---

## Agent Roles

| Agent | Role | Depends on | Output |
|-------|------|-----------|--------|
| A | Doctrine/spec intent validation | Phase 1 baseline + scan output + specs | Intent model, mandate checks, requirement fidelity |
| B | Spec adherence & workflow completeness | Scan output + spec inventory | Spec drift report, workflow assessment |
| C | Implementation fitness | Scan output + code | Test confidence, observability, delivery readiness, architectural fitness |
| D | Alignment review & gap analysis | A + B + C findings (+ review-packet constraints) | Alignment matrix, classification, gaps, push-back list, spec deltas |

**Dispatch strategy**:
- Launch A, B, C in parallel (B starts with scan output; doesn't need A's full output to read specs).
- Launch D after A, B, C complete (it synthesizes their findings).
- Handoff Output (direction report + beads handoff) is assembled by the orchestrator from all agent outputs; not a numbered phase.
- **Receiver protocol**: fresh `../../project-review/` packet exists → Agent C's dispatch must explicitly list the dimensions to SKIP (review-scored: typically test confidence, observability, delivery readiness) and narrow C to architectural fitness for the proposed direction.

---

## Template

```
You are investigating {ROLE} for a project direction analysis.

Project: {project_name}
Type: {type} | Maturity: {maturity} | Users: {users}

## Scan output
{paste full scan output from spec-scan.sh}

## Your task
{Paste the relevant section from the appropriate reference file:
  - Agent A: direction-model.md Section 1 (project spirit, requirements, reality check) + Section 2.1 (spec-intent fidelity); plus the Phase 1 doctrine baseline
  - Agent B: direction-model.md Sections 2.1-2.2 (spec adherence, workflow completeness)
  - Agent C: direction-model.md Sections 2.3-2.6 (test confidence, observability, delivery readiness, architectural fitness)
  - Agent D: alignment-review.md (full file)}

## Investigation rules
- Search for files and content with the harness's structured tools where available (Glob + Grep in Claude Code/Codex), else `rg`/`find` shell-side — not unstructured one-offs that silently miss files
- Cite specific files and line numbers: `path/to/file.ts:42` or `spec/feature.md:§3.2`
- Label claims: [Observed], [Inferred], [Unknown]
- Specifications are source of truth unless user says otherwise
- If requirements are ambiguous or contradictory, flag the conflict — do not guess the intent
- Do NOT hallucinate architecture, team process, or roadmap intent
- Be blunt about overreach, misalignment, and infeasibility

## Depth limits
- Read spec documents fully (they are the source of truth)
- For code, examine at most 30 files in detail per agent
- For large codebases: focus on entry points, core modules, and areas referenced by specs
- Target 500-800 words per assessment dimension

## Output format
Return a structured report matching the deliverable section from your reference file.
Include a "Key Findings" section at the top with your 3-5 most important observations.
```

---

## Agent-specific notes

### Agent A (Doctrine/Spec Intent Validation)
- Start from the Phase 1 doctrine baseline; validate spec intent is faithful to doctrine (heart-and-soul, legends-and-lore); run mandate checks.
- Read README + all spec docs before anything else.
- Package manifests (package.json description, pyproject.toml metadata) often hold the most honest project description.
- README and specs both present → note any contradictions.
- Check git commit messages for intent signals (what recent efforts focused on).
- Look for non-goals and rejected proposals — they reveal direction as much as goals.
- Produce a requirement-fidelity assessment (Section 2.1 read as intent, not B's drift inventory).

### Agent B (Spec Adherence & Workflow Completeness)
- Build a complete spec section inventory first, then check each against code.
- Per spec section: implemented / partially implemented / contradicted / missing / exceeds spec.
- Workflow completeness: trace the 3-5 most important user journeys end-to-end.
- Note demo-quality vs production-quality paths.
- Watch error handling — a happy path that fails ungracefully is "partially implemented".

### Agent C (Implementation Fitness)
- Focus on whether the codebase can support the stated direction, not just current quality.
- Architectural fitness is the most important assessment — it determines whether future work is feasible.
- Look for coupling hotspots that would make spec'd features expensive.
- Check if the test suite tests the right things (behavior vs implementation details).
- Note missing extension points for spec'd-but-unimplemented features.

### Agent D (Alignment Review & Gap Analysis)
- Synthesize A, B, C — read their outputs before evaluating.
- Apply the 8-dimension framework to every proposed/discovered work item.
- Be conservative with "aligned next steps" — only items with clear spec backing AND architectural support.
- Push-back list is as important as the recommendations — be direct about what shouldn't be done.
- For gaps, distinguish "needs spec" from "needs implementation" — remediation differs.
