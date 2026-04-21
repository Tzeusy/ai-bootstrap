---
name: training-curriculum
description: >
  Use when you need to inspect a target repository and generate a repo-grounded prerequisite
  curriculum in `curriculum/` that teaches the fundamental technical concepts someone must know
  before the codebase will make sense or be safe to change.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-04-21"
---

# Training Curriculum

This skill answers a specific onboarding question: "What fundamental technical concepts do I need to know before this repository will make sense?"

The output is not a generic technology explainer and not a normal repo walkthrough. It is a concept-first prerequisite curriculum: the repository is used to decide which technical fundamentals matter, but the curriculum should mainly teach transferable concepts such as transport, concurrency, serialization, timing, media, storage, and security.

Assume read access to the target repository and permission to create or update a `curriculum/` directory there before using this skill.

## Use This Skill When

- A user asks what they need to learn before they can understand or contribute to a repository
- A codebase depends on unfamiliar protocols, runtimes, infrastructure, math, media, security, or systems concepts
- You need an ordered learning path that starts before repo-specific onboarding docs
- A project needs a `curriculum/` directory that teaches prerequisite technical concepts with direct links back to repository evidence
- A repository already has a curriculum and it needs to be refreshed, split, or validated against the current codebase

## Do Not Use This Skill When

- The task is to explain the repository as it already exists for a contributor who has the prerequisite background: use `project-shape`, `project-review`, or the repo's own docs
- The task is to write capability specs, RFCs, or implementation plans rather than educational material
- The user needs quick bug triage, code review, or feature delivery instead of a learning path
- The user wants generic topic tutoring detached from any target repository
- The primary need is project onboarding, setup, scaffolding, or directory-orientation guidance rather than technical fundamentals

## Core Rules

- Derive every prerequisite topic from repository evidence, not vibes.
- Favor comprehensiveness during prerequisite discovery. It is better to reconcile and trim a broad candidate set after repeated analysis than to miss a critical enabling concept.
- Teach fundamental technical concepts first. "Learn WebRTC" or "learn TCP vs UDP" is the center of gravity; the repo only explains why those concepts matter here.
- Separate prerequisite knowledge from repo-specific orientation. "Learn WebRTC" and "understand this project's signaling layer" are different layers.
- Prefer the minimum complete curriculum that unlocks real comprehension. Do not pad it into a textbook.
- Mark uncertainty explicitly when a topic is inferred from weak evidence or missing docs.
- Record evidence confidence for every inferred topic. Fail closed with open questions when the repo does not justify a confident prerequisite claim.
- Perform a hard minimum of 3 deep-dive prerequisite-discovery passes using independent subagents with isolated context. Do not treat a single sweep as comprehensive research.
- Do not build the prerequisite map until all 3 isolated discovery passes have completed.
- Repo orientation belongs only in "why this matters here" and "where it appears in the repo" sections unless the user explicitly asks for more onboarding detail.
- Distinguish `must know before reading code`, `must know before making safe changes`, and `nice to know later`.
- Start every curriculum with an overview that names the major sections, estimated study time, and why each section matters before reading or changing code.
- Every technical subsection must end with challenge-style sample Q&A plus explicit Markdown progress checkboxes that the learner can update over time.
- Progress checkboxes should reflect mastery, not just reading completion. Use explicit criteria for recall, explanation, and repo-grounded reasoning.
- Cap any single curriculum path at 100 hours of estimated smart-human study time and any single module at 10 hours. Split anything larger into separate curriculum paths.
- Treat existing project docs as evidence inputs, not output targets to duplicate. The curriculum should complement architecture and onboarding docs, not fork them.
- Do not create standalone modules whose main content is project scaffolding, directory layout, build commands, or local naming unless that context is strictly necessary to motivate a technical concept.

## Operational Boundaries

- If the repository itself lacks intelligible shape docs, use `project-shape` or `project-review` separately; do not silently turn this skill into a repo-architecture authoring workflow.
- If `curriculum/` already exists, update it in place and validate the result instead of generating a competing second structure.
- If independent subagents are unavailable, do not claim the curriculum is comprehensive. Stop and report that the hard 3-pass requirement could not be satisfied.
- If fewer than 3 isolated discovery passes complete, or any pass reused another pass's notes or conclusions before completion, discard the run and fail closed.
- Use `scripts/scaffold_curriculum.py` to create structure and `scripts/validate_curriculum.py` before finalizing a generated or updated curriculum.

## Workflow Summary

1. Run the hard-minimum 3-pass research protocol in `references/deep-dive-passes.md` using independent subagents with isolated context.
2. Reconcile the pass outputs into an evidence-backed prerequisite map: topic, why it matters here, what file or pattern proves it, what confidence it deserves, and what depth is required.
3. Sequence the prerequisite topics into a shortest-path curriculum that moves from fundamentals to this repo's own abstractions while respecting the 100-hour total and 10-hour module caps.
4. Generate or update the curriculum in the target repo's `curriculum/` path using the contract in `references/curriculum-contract.md`.
5. Run `scripts/validate_curriculum.py` and fix contract drift before considering the curriculum done.

## Read Order

| File | Read when | Content |
|------|-----------|---------|
| `references/workflow.md` | Every real use of this skill | Repo analysis flow, prerequisite extraction, sequencing rules, and final quality checks |
| `references/deep-dive-passes.md` | Before selecting curriculum topics | Hard-minimum 3-pass subagent research protocol and reconciliation rules for comprehensive discovery |
| `references/topic-discovery.md` | You are mapping repo evidence to prerequisite topics | Heuristics for identifying hidden prerequisite domains and calibrating required depth |
| `references/curriculum-contract.md` | Before writing into `curriculum/` | Required output tree, file purposes, and per-module content contract |
| `references/mastery-rubric.md` | You are defining completion criteria or progress checkboxes | Shared mastery levels and how to convert them into updateable curriculum criteria |
| `scripts/scaffold_curriculum.py` | You need a repeatable `curriculum/` starting structure | Deterministic helper that creates the root curriculum structure and optional real path/module templates |
| `scripts/validate_curriculum.py` | Before finalizing or refreshing a curriculum | Deterministic validator for required files, budgets, and module/path contract markers |

## Trigger Sanity Check

- Should trigger: "Deep dive this media repo and tell me what I need to learn before I can contribute."
- Should trigger: "Inspect this codebase and generate a `curriculum/` folder for onboarding prerequisites."
- Should trigger: "Refresh this repository's existing curriculum after the architecture changed."
- Should not trigger: "Explain how this one module works."
- Should not trigger: "Plan the next implementation milestone for this project."
- Should not trigger: "Teach me distributed systems in general."

## Resources

### references/
- `workflow.md` — End-to-end process for repo inspection, prerequisite extraction, sequencing, writing, and review.
- `deep-dive-passes.md` — Mandatory 3-pass independent-subagent protocol for comprehensive prerequisite discovery and reconciliation.
- `topic-discovery.md` — Topic-finding heuristics, depth calibration, and evidence rules for deciding what belongs in the curriculum.
- `curriculum-contract.md` — Required `curriculum/` layout and the content contract for each generated file.
- `mastery-rubric.md` — Shared rubric for when a learner can legitimately mark a section or module complete.

### scripts/
- `scaffold_curriculum.py` — Creates the baseline `curriculum/` directory and optional real path/module templates in a target repository.
- `validate_curriculum.py` — Validates generated curricula against the package contract, including budget and structure checks.
