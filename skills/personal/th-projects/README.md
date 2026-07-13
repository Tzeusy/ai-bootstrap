# th-projects

Superskill for spec+vision-driven project governance: establish a project's
knowledge architecture (five pillars), funnel feature requests into spec
deltas, audit repo health, and plan direction from specs.

**[`SKILL.md`](SKILL.md) is the only routing authority** — start there. This
README is a signpost for humans browsing the repo, nothing more.

## Layout

| Path | What it is |
|------|------------|
| `SKILL.md` | Router: lifecycle, routing table, shared invariants |
| `subskills/project-shape/` | Five-pillar knowledge architecture (bootstrap/audit) |
| `subskills/project-feature-request/` | Idea funnel → signed-off spec delta; amendment mode |
| `subskills/project-review/` | Scored repo health audit; spec reconciliation |
| `subskills/project-direction/` | Prioritized spec-driven work plan; milestone synthesis |
| `references/spec-format.md` | Shared OpenSpec file contract (IDs, headings, test tagging) |
| `references/work-allocation.md` | Shared cohesive-bead, ownership, overhead, and discovery-triage contract |
| `scripts/spec-trace-check.py` | Mechanical spec-traceability validator (`uv run`) |
| `scripts/validate-th-projects.sh` | Package self-test — run after any change here |
| `tests/fixtures/` | Regression fixtures consumed by the validator |

Subskills are internal: `bootstrap.sh` prunes `subskills/` on install so only
the router enters a tool's global skill catalog.
