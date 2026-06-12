---
name: writing-agents
description: Guide for creating effective LLM subagent prompts and personas. This skill should be used when writing, reviewing, or improving agent definitions for Claude Code or similar multi-agent systems. Covers YAML frontmatter, system prompt structure, tool selection, and common pitfalls.
---

# Writing Effective LLM Agents

This skill provides guidance for creating high-quality subagent prompts that enable effective task delegation in multi-agent systems like Claude Code.

## Overview

Subagents are specialized AI assistants that handle specific types of tasks. Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions. The quality of a subagent is measured by how reliably it accomplishes its intended tasks and how clearly it communicates results.

### What Makes a Good Subagent

1. **Focused scope** - Excels at one specific task or domain
2. **Clear delegation trigger** - Description tells the parent agent exactly when to delegate
3. **Operational instructions** - System prompt provides actionable steps, not abstract principles
4. **Appropriate tool access** - Only the tools needed for the task
5. **Structured output** - Consistent, predictable response format

---

## Agent File Structure

Agent files use YAML frontmatter for configuration, followed by the system prompt in Markdown:

```markdown
---
name: agent-name
description: When and why to use this agent
tools: Tool1, Tool2, Tool3
model: inherit
---

System prompt content here...
```

### Required Frontmatter Fields

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Unique identifier using lowercase letters and hyphens | `code-reviewer` |
| `description` | When the parent agent should delegate to this subagent | See "Writing Effective Descriptions" below |

### Optional Frontmatter Fields

| Field | Default | Description |
|-------|---------|-------------|
| `tools` | Inherits all | Comma-separated list of allowed tools |
| `disallowedTools` | None | Tools to explicitly deny |
| `model` | `inherit` | Model to use: `sonnet`, `opus`, `haiku`, or `inherit` |
| `permissionMode` | `default` | Permission handling: `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `skills` | None | Skills to preload into context |
| `hooks` | None | Lifecycle hooks for validation |

---

## Writing Effective Descriptions

The `description` field determines when the parent agent delegates tasks. To write effective descriptions:

### Make Descriptions Action-Oriented

Describe what the agent does and when to use it, not what it is.

**Weak:**
```yaml
description: A code reviewer agent
```

**Strong:**
```yaml
description: Principal+ code reviewer for quality and correctness assessment. Use proactively after code modifications to review changes, trace execution paths, identify regressions, and provide evidence-based feedback ordered by severity.
```

### Include Delegation Triggers

Use phrases like "Use proactively when..." or "Use after..." to signal automatic delegation.

**Examples:**
- `Use proactively after code changes to run tests and verify behavior`
- `Use when defining scope, surfacing trade-offs, or creating implementation plans`
- `Use immediately after writing code to review for quality issues`

### Specify Expertise Level

Include seniority/expertise level to set expectations for output quality.

**Examples:**
- `Staff+ software engineer for implementation tasks`
- `Principal+ code reviewer for quality assessment`
- `Senior security engineer for vulnerability analysis`

---

## System Prompt Structure

The body of the agent file becomes the system prompt. Structure it for operational clarity, not as a job description.

### High-Value Sections

#### 1. Role Statement (1-2 sentences)

Start with a clear statement of identity and purpose.

```markdown
You are a Staff+ QA Engineer verifying behavior with reproducible evidence and preventing regressions.
```

#### 2. "When Invoked" Action Steps

Provide numbered steps for immediate execution upon invocation. This section drives actual behavior and should be included in every agent.

```markdown
When invoked:
1. Run `git diff` to see recent changes
2. Identify the scope and intent of the change
3. Trace execution paths affected by the change
4. Check for correctness, security, and test coverage
5. Assess regression and compatibility risks
6. Report findings by severity with file references
```

#### 3. Domain-Specific Checklist

Provide concrete items to verify, not abstract principles.

```markdown
Security review checklist:
- No secrets, API keys, or credentials in code or logs
- Input validation on all untrusted data
- Output encoding to prevent XSS
- Parameterized queries to prevent SQL injection
- Authentication checks on protected endpoints
```

#### 4. Output Format Specification

Define the exact response structure. Use numbered sections with bold labels.

```markdown
For each review, provide:
1. **Summary**: What the change does (1-2 sentences)
2. **Critical issues**: Must-fix problems with file:line references
3. **Warnings**: Should-fix concerns with evidence
4. **Suggestions**: Optional improvements
5. **Questions**: Clarifications needed before approval
```

#### 5. Red Flags / Anti-Patterns

List specific behaviors to avoid. Frame as actions, not personality traits.

```markdown
Red flags to avoid:
- Making claims without file references or evidence
- Suggesting broad refactors without clear benefit
- Claiming success without verification evidence
- Quick-fixing without understanding root cause
```

### Low-Value Sections to Avoid

- **Mission statements** - Too abstract to drive behavior
- **Core values** - Models already have values; focus on actions
- **Lengthy background** - Wastes context window
- **Personality descriptions** - Focus on actions, not identity
- **Verbose explanations** - Be concise and actionable

---

## Tool Selection Guidelines

Grant only the tools necessary for the task. Restricting tools prevents scope creep and enforces the agent's role.

### Common Tool Configurations

| Agent Type | Typical Tools | Rationale |
|------------|---------------|-----------|
| **Read-only reviewer** | Read, Grep, Glob, Bash | Inspect code and run git commands, no modification |
| **Implementation** | Read, Edit, Write, Bash, Grep, Glob | Full modification capabilities |
| **Planner** | Read, Grep, Glob | Read-only, no execution |
| **Tester** | Read, Edit, Write, Bash, Grep, Glob | Write tests and run them |
| **Security auditor** | Read, Bash, Grep, Glob | Read-only plus security tools via Bash |

### Tool Restriction Patterns

**To deny destructive tools for reviewers:**
```yaml
tools: Read, Bash, Grep, Glob
# Implicitly denies Edit, Write
```

**To use fine-grained control:**
```yaml
tools: Read, Edit, Write, Bash, Grep, Glob
disallowedTools: Write
# Can edit existing files but not create new ones
```

---

## Common Pitfalls

### Pitfall 1: Abstract Role Descriptions

**Problem:** System prompts that read like job descriptions fail to drive action.

```markdown
# Avoid
## Mission
Deliver high-quality code with explicit reasoning.

## Core Principles
- Maintain code quality
- Follow best practices
```

**Solution:** Replace with operational instructions.

```markdown
# Prefer
You are a Staff+ software engineer delivering correct, maintainable code changes.

When invoked:
1. Clarify scope and success criteria if ambiguous
2. Inspect existing code before making changes
3. Implement changes matching local style
4. Verify outcomes with tests or concrete evidence
5. Report what changed and how to verify
```

### Pitfall 2: Missing Output Format

**Problem:** Agent produces inconsistent, hard-to-parse responses.

**Solution:** Always specify exact output structure.

```markdown
For each implementation, provide:
1. **Summary**: What changed and why (with file paths)
2. **Verification**: Commands to run and expected outcomes
3. **Risks**: Edge cases, follow-ups, or concerns (if any)
```

### Pitfall 3: Vague Descriptions

**Problem:** Parent agent cannot determine when to delegate.

```markdown
# Avoid
description: Helps with code
```

**Solution:** Specify triggers and capabilities.

```markdown
# Prefer
description: Staff+ QA engineer for test execution. Use proactively after code changes to run tests, verify behavior, and report failures with reproduction steps.
```

### Pitfall 4: Overly Broad Tool Access

**Problem:** Reviewer agent with Edit access might "fix" issues instead of reporting them.

**Solution:** Match tools to the agent's role. Read-only agents require read-only tools.

### Pitfall 5: No Decision Gates

**Problem:** Agent takes actions without appropriate checkpoints.

**Solution:** Include explicit gates.

```markdown
Decision gates:
- Do not implement without a clear plan for non-trivial work
- Do not expand scope without explicit confirmation
- If verification fails, perform root-cause analysis before retrying
```

### Pitfall 6: Missing Evidence Requirements

**Problem:** Agent makes claims without substantiation.

**Solution:** Require evidence in the output format.

```markdown
- Cite file paths and line numbers for all findings
- Include exact commands run and their outputs
- Separate verified facts from inferences
```

---

## Model Selection Guidelines

| Model | Best For | Trade-offs |
|-------|----------|------------|
| `haiku` | Fast, simple tasks (file search, basic analysis) | Lower capability, faster and cheaper |
| `sonnet` | Balanced tasks (code review, moderate analysis) | Good capability/cost balance |
| `opus` | Complex reasoning, architecture decisions | Highest capability, slower |
| `inherit` | Match parent conversation | Default choice for most agents |

**Recommendation:** Default to `inherit` unless there is a specific reason to override.

---

## Quality Checklist

To verify agent quality before finalizing:

### Frontmatter
- [ ] `name` uses lowercase-hyphenated format
- [ ] `description` includes delegation triggers ("Use proactively when...")
- [ ] `description` specifies expertise level
- [ ] `tools` restricted to what is necessary
- [ ] `model` appropriate for the task

### System Prompt
- [ ] Starts with clear role statement (1-2 sentences)
- [ ] Includes "When invoked:" numbered action steps
- [ ] Has domain-specific checklist
- [ ] Specifies exact output format with sections
- [ ] Lists red flags / anti-patterns to avoid
- [ ] Includes decision gates if applicable

### Content Quality
- [ ] Uses imperative/operational language, not abstract principles
- [ ] Checklists contain concrete, verifiable items
- [ ] Output format uses numbered sections with bold labels
- [ ] No verbose mission statements or personality descriptions
- [ ] Evidence requirements are explicit

---

## Reference

For complete examples, see the reference file: [Agent Examples](./references/examples.md)

For the Claude Code subagents specification: [Claude Code Sub-agents Documentation](https://code.claude.com/docs/en/sub-agents)
