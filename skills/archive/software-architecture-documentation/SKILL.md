---
name: software-architecture-documentation
description: This skill should be used when creating, reviewing, or updating architecture documentation (ARCHITECTURE.md) for a software project. It provides a comprehensive template and best practices for producing documentation that enables rapid codebase comprehension by developers and AI agents.
---

# Software Architecture Documentation

Generate comprehensive ARCHITECTURE.md files that enable developers and AI agents to rapidly understand a codebase. Based on the [architecture.md](https://architecture.md/) template by [timajwilliams](https://github.com/timajwilliams/architecture).

## When To Use

- A new project needs architecture documentation
- Onboarding documentation is missing or outdated
- A codebase is being prepared for AI agent interaction
- Existing architecture docs need review or improvement
- Documentation completeness audit is requested

## Workflow

### Creating New Architecture Docs

1. **Explore the codebase** - Run `tree -L 3 -I 'node_modules|__pycache__|.git|dist|build'` to understand directory structure
2. **Identify technologies** - Check package.json, requirements.txt, go.mod, Cargo.toml, or similar dependency files
3. **Trace data flow** - Follow entry points (routes, handlers) through to storage
4. **Map external dependencies** - Review configs and environment variables for third-party services
5. **Load the template** - Read `references/architecture-template.md` and fill in each section
6. **Verify accuracy** - Cross-reference documented structure against actual code

### Reviewing Existing Docs

1. **Compare against template** - Read `references/architecture-template.md` to identify missing sections
2. **Verify currency** - Check if documented structure matches actual codebase
3. **Test comprehension** - Determine if someone can navigate the codebase using only the doc
4. **Update stale sections** - Prioritize project structure and external integrations

## Output Location

Place the generated documentation at `ARCHITECTURE.md` in the repository root, or `docs/ARCHITECTURE.md` if documentation is centralized.

## Key Principles

1. **Optimize for speed** - Enable rapid comprehension, not exhaustive coverage
2. **Stay current** - Outdated docs are worse than no docs
3. **Be honest** - Document what exists, not what is wished for
4. **Link, don't duplicate** - Reference code files instead of copying content
5. **Use portable diagrams** - ASCII art or Mermaid for version control friendliness

## Resources

- `references/architecture-template.md` - The complete 11-section template to fill in
- `references/writing-guide.md` - Best practices, anti-patterns, and project-type-specific guidance
