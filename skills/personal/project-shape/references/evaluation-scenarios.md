# Evaluation Scenarios

Use these scenarios to pressure-test the skill package itself, not just the target project.

## Scenario Matrix

| Scenario | Environment | Expected outcome |
|----------|-------------|------------------|
| Bootstrap a brand-new project | Strong model, subagents, diagram tooling available | Produces five-pillar structure, reviewed documents, no scaffold leftovers before claiming maturity |
| Audit a legacy repo with `docs/rfcs/` + `ARCHITECTURE.md` | Strong or mid-tier model | Detects legacy layout, recommends canonical migration, does not miss design/topology pillars |
| Audit a scaffolded repo | Any model | Reports `shaped` or lower, never `mature` |
| Constrained environment: no subagents | Single-agent environment | Uses lite review path with explicit self-critique and user validation |
| Constrained environment: no Excalidraw | No diagram renderer | Falls back to Mermaid or prose without blocking the workflow |
| Mid-tier model | Lower reasoning budget | Still follows the five-pillar workflow and references the correct files, possibly with more cautious phrasing |

## Package-Level Checks

Run these after editing the skill package:

```bash
bash <skill-path>/scripts/self-test.sh
bash <skill-path>/scripts/eval-fallbacks.sh
bash <skill-path>/scripts/shape-scan.sh <fixture-or-temp-project>
```

## Human Review Checklist

- Does the skill still degrade gracefully when premium capabilities are unavailable?
- Does the scanner under-claim rather than over-claim?
- Do docs, scripts, and adapter metadata all agree on the same five-pillar model?
- Are the examples and templates specific enough to guide action, but generic enough to reuse across projects?
- Can a new agent find the right reference file without reading the whole package?
