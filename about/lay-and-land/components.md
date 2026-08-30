# Components

## System Overview

```mermaid
flowchart TD
    R[ai-bootstrap repo]
    R --> TF[Tool facades]
    R --> SH[Shared authoring]
    R --> SU[Support utilities]
    R --> PO[Independent offerings]
    TF --> C[.claude]
    TF --> X[.codex]
    TF --> G[.gemini]
    TF --> O[opencode]
    SH --> A[agents/]
    SH --> S[skills/]
    SH --> D[about/ + openspec/]
    SU --> SC[scripts/]
    PO --> P[projects/]
```

## Component Inventory

| Component | Responsibility | Stability |
|-----------|----------------|-----------|
| `.claude/` | Tracked Claude config plus ignored runtime/plugin state; install target is `~/.claude` | Mixed tracked config + local runtime state |
| `.codex/` | Tracked Codex config; mirrored skills and most runtime state are ignored locally | Mixed tracked config + local runtime state |
| `.gemini/` | Tracked Gemini config; mirrored skills, antigravity runtime state, and local auth/runtime data are ignored locally | Mixed tracked config + local runtime state |
| `opencode/` | OpenCode-specific config surface installed under `$HOME/.config/opencode`; no in-repo skill mirror surface today | Smaller tracked adapter |
| `skills/personal/` | Sole active authored workflow layer, including Beads, engineering, project, writing, tooling, and BWS methods | Canonical local authored layer |
| `skills/archive/` | Retired packages retained for history-backed rollback and pruned from catalogs | Inactive legacy material |
| `agents/` | Older tool-agnostic role prompts retained for reference or selective reuse | Secondary reference layer |
| `scripts/` | Repository-level maintenance utilities | Narrow support layer |
| `about/` | Human-and-agent orientation docs | New canonical documentation layer |
| `openspec/` | Normative requirements and change records | New canonical requirements layer |
| `projects/` | Independently shaped product offerings with product-local `about/` and OpenSpec authority | Separate from shared skill mirroring and installation flow |

## Boundary Notes

- `skills/` owns the main reusable workflow semantics and is the only layer mirrored broadly across tool skill directories.
- `skills/personal/` is the only active workflow surface; archived packages do
  not participate in discovery or mirroring.
- `agents/` is a reference layer, not the default execution path.
- Tool facades mix tracked baseline config with ignored runtime or mirror surfaces; they are not uniformly canonical.
- `about/` and `openspec/` own the explanation of where things belong and why.
- `projects/` makes product offerings discoverable without turning them into a
  root pillar, shared skill, tool facade, or installation dependency.
- Generated or vendored outputs may sit under a skill or tool facade, but only with a documented regeneration path.
