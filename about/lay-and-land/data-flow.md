# Data Flow

## Authoring to Consumption

```mermaid
flowchart LR
    C[Contributor edits repo] --> S1[Canonical workflow assets in skills/]
    C --> A1[Optional reference prompts in agents/]
    C --> S2[Tool-specific assets in .claude/.codex/.gemini/opencode]
    S1 --> M[In-repo tool skill mirrors or entrypoints]
    M --> I[Symlink/copy into local tool home]
    S2 --> I
    A1 --> T
    I --> T[Agent runtime loads prompts, rules, skills, settings]
```

## Generated Asset Flow

```mermaid
flowchart LR
    A[Authored regeneration script] --> R[scripts/refresh.sh example]
    R --> V[Vendored artifact under skill path]
    V --> U[Skill runtime consumes generated asset]
```

## Trust and Drift Boundaries

- Human-authored source for day-to-day workflow logic lives in `skills/`; `agents/` is a secondary reference source.
- In-repo tool skill mirrors are distribution surfaces, not the authored source of truth.
- Installed home-directory or XDG copies are distribution outputs, not the repository's only source of truth.
- Generated assets are acceptable only when the regeneration path is checked in; `scripts/refresh.sh` is an example, not the only allowed pattern.
- Runtime traces, caches, local auth, and machine-private IDs sit outside the canonical flow and should not round-trip back into git.
