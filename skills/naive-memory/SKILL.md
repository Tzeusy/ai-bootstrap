---
name: naive-memory
description: "This skill should be used at the end of a session (or when explicitly asked) to persist generalizable, repository-specific knowledge to .genai/memory.md. It acts as a note-to-self scratchpad for LLMs, capturing lessons learned so future sessions start with useful context. At the start of any session, check if .genai/memory.md exists in the repository root — it may contain valuable context from previous sessions."
---

# Naive Memory

## Overview

Persist useful, repository-specific knowledge discovered during a session into a shared
memory file at `.genai/memory.md` in the repository root. This file serves as a durable
scratchpad that any LLM agent can read at the start of future sessions to avoid rediscovering
the same information.

## When to Invoke

- At the end of a working session, before closing out
- When explicitly asked to "remember" or "save notes"
- After resolving a non-obvious problem where the solution would help future sessions

## Workflow

### 1. Reflect

Ask yourself:

> Is there any generalizable knowledge specific to this repository that I wish I'd known
> prior to this conversation that would have made work more efficient?

Only proceed if the answer is yes.

### 2. Read existing memory

Read `.genai/memory.md` from the repository root. If the file does not exist, create it with
a `# Notes to self` heading.

### 3. Evaluate before writing

Add a new entry under `# Notes to self` **IF AND ONLY IF** all of the following are true:

1. The knowledge is **not already documented** in the file
2. The knowledge is **generally useful** for future work on this repository
3. The knowledge is **unlikely to change** soon (avoid transient details)
4. The knowledge is **specific to this repository** (not general programming knowledge)

### 4. Write the entry

Each entry must include:

- **Timestamp**: ISO 8601 date (`YYYY-MM-DD`)
- **Model name**: The model that authored the entry (e.g., `claude-opus-4-6`)
- **Content**: Concise, accurate, actionable knowledge

Format:

```markdown
## <Topic>

_Added: YYYY-MM-DD by <model-name>_

<knowledge>
```

### 5. Maintain the file

- Keep the file concise — remove or update entries that are outdated or proven wrong
- Deduplicate — if new knowledge supersedes an existing entry, replace rather than append
- Organize semantically by topic, not chronologically

## Anti-patterns

- Do NOT document session narratives ("Today I fixed bug X")
- Do NOT include secrets, credentials, or API keys
- Do NOT add general programming knowledge ("Python uses indentation")
- Do NOT add information that is already obvious from the codebase structure
- Do NOT add entries on every session — only when genuinely useful knowledge was discovered
