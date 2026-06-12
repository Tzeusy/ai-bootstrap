# Writing Effective Architecture Documents

Best practices for creating architecture documentation that enables rapid codebase comprehension.

## Core Principles

### 1. Optimize for Speed of Comprehension

The primary goal is enabling a new developer or AI agent to understand the system quickly. Every section should answer: "What is needed to work effectively in this codebase?"

### 2. Keep It Living

Architecture documents become worthless when stale. Design for maintainability:
- Link to code rather than duplicating it
- Use relative paths that survive refactors
- Include the "Date of Last Update" field
- Review quarterly or after major changes

### 3. Balance Depth vs. Breadth

- **Too shallow:** "We use React" tells nothing useful
- **Too deep:** 50-page documents won't be read
- **Just right:** Enough context to navigate, with links to deeper docs

## Section-by-Section Guidance

### Project Structure

**Do:**
- Show the actual directory tree (use `tree -L 2` as a starting point)
- Annotate each directory with its purpose
- Highlight where to find specific concerns (auth, API routes, models)

**Don't:**
- List every single file
- Include generated or build directories
- Describe obvious directories like `node_modules/`

### High-Level System Diagram

**Do:**
- Show data flow between major components
- Identify system boundaries (controlled vs. external)
- Use ASCII diagrams for portability, or link to a diagram tool

**Don't:**
- Include implementation details in the overview
- Show every microservice in a complex system (summarize by domain)
- Use proprietary diagram formats that can't be viewed without tools

**Diagram Options:**
- ASCII art (portable, lives in markdown)
- Mermaid.js (renders in GitHub, many tools)
- C4 Model (structured approach: Context → Container → Component → Code)
- draw.io/excalidraw (export as PNG with source file)

### Core Components

For each component, answer:
1. What problem does it solve?
2. What technologies power it?
3. Where is it deployed?
4. Who owns it? (if relevant)

### Data Stores

Critical for understanding data flow:
- What data lives where?
- Why was this storage chosen? (relational needs, speed requirements, etc.)
- Key tables/collections that matter most

### External Integrations

Document every external dependency:
- What could break if this service is down?
- Where are credentials managed?
- Are there rate limits or quotas?

### Security Considerations

Essential for understanding trust boundaries:
- How do users authenticate?
- How is authorization enforced?
- What data is encrypted and how?

### Development Environment

Enable quick onboarding:
- Prerequisites (language versions, tools)
- Setup steps (ideally one command)
- Common development tasks

## Anti-Patterns to Avoid

### 1. The Wishful Architecture Doc
Documents what the system should be, not what it is. Be honest about tech debt.

### 2. The Novel
30+ pages that no one reads. Keep it scannable with headers and bullet points.

### 3. The Fossil
Written once, never updated. Outdated docs are worse than no docs.

### 4. The Jargon Dump
Uses internal terminology without explanation. Include a glossary.

### 5. The Code Dump
Copies large code blocks. Link to actual files instead.

## Templates for Different Project Types

### Monolith
Focus on:
- Module/package boundaries within the monolith
- Database schema overview
- Key entry points (routes, commands)

### Microservices
Focus on:
- Service catalog with ownership
- Inter-service communication patterns (sync vs. async)
- Service discovery and configuration

### Serverless
Focus on:
- Function inventory and triggers
- Event flow between functions
- Cold start considerations

### Library/Package
Focus on:
- Public API surface
- Extension points
- Compatibility guarantees

## Practical Tips

### Starting from Scratch
1. Run the project structure section first (low effort, high value)
2. Draw the system diagram on paper, then transcribe
3. Interview teammates about "what do you wish you knew on day 1?"

### Updating Existing Docs
1. Check the "Date of Last Update" - if >6 months, full review needed
2. Run a diff against current project structure
3. Verify all linked docs/files still exist

### Validating Quality
Questions to answer with the doc alone:
- Where does authentication happen?
- How does a request flow from frontend to database?
- What would break if external service X went down?

## External Resources

- [C4 Model](https://c4model.com/) - Structured approach to diagramming
- [arc42](https://arc42.org/) - Comprehensive architecture documentation template
- [ADRs](https://adr.github.io/) - Architecture Decision Records for capturing "why"
