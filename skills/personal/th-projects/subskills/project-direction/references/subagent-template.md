# Subagent Dispatch Template

Use this template when dispatching investigation subagents for project direction analysis.

---

## Agent Roles

| Agent | Role | Depends on | Output |
|-------|------|-----------|--------|
| A | Project spirit & requirements | Scan output | Direction model: spirit, requirements, reality check |
| B | Spec adherence & workflow completeness | Scan output + spec inventory from A | Spec drift report, workflow assessment |
| C | Implementation fitness | Scan output | Test confidence, observability, delivery readiness, architectural fitness |
| D | Alignment review & gap analysis | A + B + C findings | Alignment matrix, classification, gaps, push-back list |

**Dispatch strategy**:
- Launch A, B, C in parallel (B can start with scan output; it doesn't strictly need A's full output to begin reading specs)
- Launch D after A, B, C complete (it synthesizes their findings)
- Phase 4 (work plan) is done by the orchestrator using all agent outputs

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
  - Agent A: direction-model.md Phase 1 + Phase 2 sections 2.1-2.2
  - Agent B: direction-model.md Phase 2 sections 2.1-2.3
  - Agent C: direction-model.md Phase 2 sections 2.3-2.6
  - Agent D: alignment-review.md (full file)}

## Investigation rules
- Use Glob and Grep tools for file/content search (not bash grep/find)
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

### Agent A (Project Spirit & Requirements)
- Read README and all spec documents before anything else
- Package manifests (package.json description, pyproject.toml metadata) often contain the most honest project description
- If the project has both a README and specs, note any contradictions
- Check git commit messages for intent signals (what were recent efforts focused on?)
- Look for non-goals and rejected proposals — they reveal direction as much as goals do

### Agent B (Spec Adherence & Workflow Completeness)
- Build a complete spec section inventory first, then check each against code
- For each spec section, determine: implemented / partially implemented / contradicted / missing / exceeds spec
- For workflow completeness, trace the 3-5 most important user journeys end-to-end
- Note "demo-quality" paths vs "production-quality" paths
- Pay attention to error handling in workflows — a happy path that works but fails ungracefully is "partially implemented"

### Agent C (Implementation Fitness)
- Focus on whether the codebase can support the stated direction, not just current quality
- Architectural fitness is the most important assessment — it determines whether future work is feasible
- Look for coupling hotspots that would make spec'd features expensive
- Check if the test suite tests the right things (behavior vs implementation details)
- Note missing extension points for features described in specs but not yet implemented

### Agent D (Alignment Review & Gap Analysis)
- You synthesize findings from A, B, and C — read their outputs before starting evaluation
- Apply the 8-dimension evaluation framework to every proposed/discovered work item
- Be conservative with "aligned next steps" — only items with clear spec backing AND architectural support
- The push-back list is as important as the recommendations — be direct about what shouldn't be done
- For gaps, distinguish between "needs spec" and "needs implementation" — the remediation is different
