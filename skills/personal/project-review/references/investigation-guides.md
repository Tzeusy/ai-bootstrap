# Investigation Guides

Per-domain checklists for subagent investigators. Each section is self-contained — pass only the relevant domain section to the assigned subagent.

If Phase 0 of `project-review` found usable `project-shape` artifacts, treat them as the normative baseline for every domain. README claims are still evidence, but they do not override doctrine, law, or spec.

**Tool usage**: Use Glob for file discovery and Grep for content search. Fall back to Bash only for commands that require piping (e.g., `wc -l`, `sort`).

---

## Domain A: Project Mapping, Normative Baseline & Goal Inference

**Objective**: Build the project map, establish the normative baseline, and infer goals. This grounds all other investigations.

### What to examine
- Project-shape artifacts: `about/heart-and-soul/`, `about/legends-and-lore/`, `about/lay-and-land/`, `openspec/`
- README.md, docs/, wiki references
- Package manifests: package.json, pyproject.toml, Cargo.toml, go.mod, Gemfile, pom.xml, build.gradle
- Entry points: main.*, index.*, app.*, cmd/, bin/, src/main
- Directory structure (top 3 levels)
- .gitmodules, monorepo config (nx.json, lerna.json, turbo.json, pnpm-workspace.yaml)
- CI/CD: .github/workflows/, .gitlab-ci.yml, Jenkinsfile, .circleci/
- Deploy: Dockerfile, docker-compose.yml, k8s/, terraform/, serverless.yml, fly.toml
- DB: migrations/, schema files, ORM config, prisma/, alembic/
- Changelog, git tags, CONTRIBUTING.md, LICENSE

### Search patterns (using LLM tools)
```
Glob: "about/heart-and-soul/**/*", "about/legends-and-lore/**/*", "about/lay-and-land/**/*", "openspec/**/*"
Glob: "**/main.*", "**/index.*", "**/app.*", "cmd/**/*", "bin/**/*"
Glob: "**/*.proto", "**/*.graphql", "**/openapi.*", "**/swagger.*"
Grep: pattern="description" glob="package.json" (extract project description)
Bash: git log --oneline -20 (recent commit messages for goal inference)
Bash: git tag --sort=-creatordate | head -10 (version history)
```

### Deliverable
Structured summary covering:
1. **Project-shape maturity** and which pillars exist
2. **Normative baseline** (doctrine, design contracts, specs, topology)
3. **Languages & frameworks** (evidence: file extensions, imports, configs)
4. **Entry points & services** (what runs, what deploys)
5. **Dependency management** (lock files, version pinning)
6. **Test structure** (test dirs, frameworks, CI test steps)
7. **CI/CD pipeline** (stages, triggers, deploy targets)
8. **Infrastructure** (containers, cloud, databases, caches, queues)
9. **Maturity signals** (versioning, changelog, contribution guide, benchmarks, runbooks)
10. **Explicit goals** (from doctrine, specs, README, docs, package description)
11. **Implicit goals** (from architecture choices, what was built but not documented)
12. **Goal contradictions** (where doctrine/spec/README and code disagree)

---

## Domain B: Code Quality & Architecture (Categories 1-4)

**Objective**: Evaluate goal alignment, architecture, code clarity, and correctness.

### What to examine
- Module/package structure and import graph
- Core abstractions: interfaces, base classes, type definitions
- Dependency direction (do high-level modules import low-level ones?)
- Code style consistency: naming, indentation, patterns
- Complexity hotspots: longest files, deepest nesting, most imports
- Type coverage: untyped code, `any` usage, type ignores
- Generated code (exclude from quality assessment): protobuf output, ORM migrations, bundled assets

### Search patterns (using LLM tools)
```
# Complexity hotspots — use churn data from scan output, then read top files
Bash: find . -name '*.ts' -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o -name '*.java' | \
  xargs wc -l 2>/dev/null | sort -rn | head -20

# TODO/FIXME/HACK density
Grep: pattern="TODO|FIXME|HACK|WORKAROUND" glob="*.{ts,py,go,rs,java,rb}"

# Import analysis (adjust per language)
Grep: pattern="^import |^from " glob="*.py"       # Python
Grep: pattern="^import " glob="*.{ts,tsx,js,jsx}"  # TypeScript/JS
Grep: pattern="^import " glob="*.go"               # Go

# Type safety gaps
Grep: pattern=": any\b|as any" glob="*.{ts,tsx}"   # TypeScript any usage
Grep: pattern="# type: ignore" glob="*.py"          # Python type ignores
Grep: pattern="\.unwrap\(\)" glob="*.rs"            # Rust unwrap usage
```

### Key questions
- Does the module structure reflect the domain or is it purely framework-driven?
- Are there clear interface boundaries between major components?
- Can you understand a function's purpose from its name and signature?
- Are there unsafe patterns (unchecked unwrap, unvalidated casts, race conditions)?
- What is the ratio of business logic to boilerplate?
- Are there god files (>500 lines) or god modules (>20 exports)?

### Deliverable
Scored assessments (1-5 with confidence) for categories 1-4 with:
- Specific file/function evidence for each claim
- What is working well
- What is weak or risky
- Concrete remediation recommendations

---

## Domain C: Reliability & Tooling (Categories 5-8)

**Objective**: Evaluate error handling, observability, testing, and engineering hygiene.

### What to examine
- Error handling: try/catch, Result types, error middleware, panic/unwrap
- Logging: framework, structured vs unstructured, log levels, correlation IDs
- Metrics: prometheus, StatsD, custom metrics, dashboards
- Tracing: OpenTelemetry, Datadog, Jaeger instrumentation
- Test dirs: tests/, __tests__/, spec/, *_test.go, *_test.rs
- Test config: jest.config, pytest.ini, vitest.config, coverage thresholds
- Test types: unit, integration, e2e, snapshot, property-based, load
- CI: test steps, coverage gates, required checks, flaky test indicators
- Linter/formatter: .eslintrc, .prettierrc, ruff.toml, clippy, golangci-lint
- Pre-commit: .pre-commit-config.yaml, husky, lint-staged
- Build scripts: Makefile, justfile, package.json scripts

### Search patterns (using LLM tools)
```
# Error handling strategy
Grep: pattern="catch|except |\.catch\(|Error\(|panic\(|unwrap\(\)" glob="*.{ts,py,go,rs}"
Grep: pattern="throw new|raise |return err|Err\(" glob="*.{ts,py,go,rs}"

# Logging framework usage
Grep: pattern="logger\.|log\.(info|warn|error|debug)|console\.(log|error|warn)" glob="*.{ts,py,go,js}"

# Flaky test indicators
Grep: pattern="skip|xfail|flaky|retry|@pytest.mark.skip" glob="*.{ts,py,go,rs}"

# CI test configuration
Glob: ".github/workflows/*.yml"  # then read for test steps
Glob: "**/jest.config.*", "**/vitest.config.*", "**/pytest.ini", "**/conftest.py"

# Coverage configuration
Grep: pattern="coverage|threshold|--cov|istanbul|nyc|c8" glob="*.{json,yml,yaml,toml,cfg}"
```

### Key questions
- Is there a consistent error handling strategy or ad-hoc patterns?
- Can you diagnose a production issue from logs alone?
- What percentage of critical paths have test coverage?
- Are tests testing behavior or implementation details?
- Is the test suite fast enough to run on every commit?
- Are there flaky tests (skip/retry annotations)?
- Do CI checks block merges?

### Deliverable
Scored assessments (1-5 with confidence) for categories 5-8 with evidence.

---

## Domain D: Security, Performance & Data (Categories 9-12)

**Objective**: Evaluate dependencies, security, performance, and data/API design.

### What to examine

**Dependencies (Category 9)**:
- Lock files and version pinning strategy
- Direct vs transitive dependency count
- Automated updates: renovate.json, dependabot.yml
- License compliance signals

**Security (Category 10)**:
- Auth middleware, JWT handling, session management
- Input validation: schemas, validators, sanitizers
- Secrets: .env files, hardcoded strings, credentials in code
- CORS, CSP, security headers
- SQL/NoSQL injection vectors
- Rate limiting, abuse prevention

**Performance (Category 11)**:
- Algorithm complexity in hot paths
- Caching layers: Redis, in-memory, HTTP cache headers
- Database indexes, query optimization, N+1 patterns
- Connection pooling, timeout configuration
- Pagination and query bounding

**Data/API Design (Category 12)**:
- API route definitions, versioning strategy
- Schema definitions: OpenAPI, GraphQL, Protobuf
- Migration files and rollback strategy
- Serialization/deserialization consistency
- Error response format across endpoints

### Search patterns (using LLM tools)
```
# HIGH PRIORITY: Secrets in code (check first)
Grep: pattern="password|secret|api_key|apikey|token|credential|private_key" glob="*.{ts,py,go,env,yml,yaml,json,toml}" -i=true
Grep: pattern="(sk-|pk-|ghp_|gho_|AKIA)" glob="*.{ts,py,go,json,yml,env}"  # Common secret prefixes

# SQL injection patterns
Grep: pattern="f\".*SELECT|f\".*INSERT|f\".*UPDATE|f\".*DELETE" glob="*.py"
Grep: pattern="`.*(SELECT|INSERT|UPDATE|DELETE)" glob="*.{ts,js}"
Grep: pattern='"\+.*SELECT|string\.Format.*SELECT' glob="*.{cs,java}"

# Auth middleware
Grep: pattern="auth|authenticate|authorize|middleware|guard|protect" glob="*.{ts,py,go,rs,java}"

# API routes
Grep: pattern="router\.|app\.(get|post|put|delete|patch)|@(app\.route|router)|HandleFunc" glob="*.{ts,py,go,java}"

# N+1 query patterns (ORM usage in loops)
Grep: pattern="for.*\n.*\.find|for.*\n.*\.query|for.*\n.*\.get" multiline=true glob="*.{ts,py}"

# Dependency count
Bash: cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'deps: {len(d.get(\"dependencies\",{}))}, devDeps: {len(d.get(\"devDependencies\",{}))}')" 2>/dev/null || true
```

### Key questions
- Are there known CVEs in dependencies? (Check lock file age, automated update config)
- Is auth consistently enforced across all endpoints? Are there skip lists?
- Are there SQL injection or XSS vectors?
- Are queries bounded (pagination, limits, timeouts)?
- Is the data model normalized appropriately for the use case?
- Is there a migration strategy that supports rollback?
- Are API responses consistent in format across endpoints?

### Deliverable
Scored assessments (1-5 with confidence) for categories 9-12 with evidence.

---

## Domain E: Documentation, Maintainability & Operations (Categories 13-15)

**Objective**: Evaluate docs, DX, release process, and long-term maintainability.

### What to examine
- README.md quality and accuracy (mentally walk through setup instructions)
- API documentation: generated or hand-written
- Architecture docs, ADRs (Architecture Decision Records)
- Examples directory
- CONTRIBUTING.md quality
- Changelog and release notes
- CI/CD pipeline: stages, gates, deploy process
- Dockerfile, docker-compose for local dev
- Version strategy: semver, calver, tags
- Health check endpoints, readiness/liveness probes
- Runbooks, incident response docs
- Type system strictness: TypeScript strict mode, mypy strict
- Code review config: CODEOWNERS, required reviewers, branch protection
- Feature flag system
- Migration patterns and rollback capability

### Search patterns (using LLM tools)
```
# Documentation inventory
Glob: "**/*.md" (then filter out node_modules, vendor)
Glob: "docs/**/*", "examples/**/*", "ADR/**/*", "adr/**/*"

# Type safety strictness
Grep: pattern="\"strict\": true|strict = true|strict_mode" glob="tsconfig.json"
Grep: pattern="strict = true|disallow_untyped" glob="mypy.ini"
Grep: pattern=": any\b" glob="*.{ts,tsx}" output_mode="count"  # TypeScript any count

# Code review governance
Glob: "**/CODEOWNERS", "**/.github/CODEOWNERS"
Grep: pattern="required_approving_review_count|branch_protection" glob="*.{yml,yaml}"

# Feature flags
Grep: pattern="feature.flag|featureFlag|FEATURE_|feature_toggle|LaunchDarkly|unleash" glob="*.{ts,py,go,java}"

# Health checks
Grep: pattern="health|readiness|liveness|/healthz|/ready|/alive" glob="*.{ts,py,go,java,yml,yaml}"
```

### Key questions
- Can a new developer set up and contribute within a day?
- Is the release process automated and repeatable?
- What is the bus factor? (Check git contributor distribution, CODEOWNERS breadth)
- How safe is it to make changes? What guardrails exist (types, tests, CI gates, review)?
- Are there areas of the codebase nobody wants to touch? (Check churn hotspots from scan)

### Deliverable
Scored assessments (1-5 with confidence) for categories 13-15 with evidence.

---

## Domain F: Feature Gaps, Scale & Risk Analysis

**Objective**: Identify missing capabilities, scaling limits, and prioritized risks.

### Investigation process

**Step 1: Feature gap discovery**

Read `references/project-type-adaptations.md` for standard expectations per project type. For each expected feature:
- Check the project-shape baseline first. If doctrine/spec/topology already defines the expectation, treat it as normative.
- Is it present? (search for it)
- Is it partially implemented?
- Is it completely absent?

Categorize gaps:

| Category | What to look for |
|----------|-----------------|
| Core features | Features stated in README but missing in code |
| Operational | Health checks, graceful shutdown, rate limiting, circuit breakers, retry policies |
| DX | Dev server, hot reload, debugging config, setup scripts, seed data |
| Enterprise/readiness | SSO, RBAC, audit logging, multi-tenancy, SBOM, compliance controls |

For each gap, determine:
- Is it a **blocker** (prevents use in stated context) or **enhancement** (nice-to-have)?
- **User impact**: Who feels the pain? (end user, operator, contributor)
- **Evidence**: Was it intended? (TODO comment, open issue, empty stub)
- **Effort**: S (<1 day), M (1-5 days), L (1-3 weeks), XL (>3 weeks)

**Step 2: Scale analysis**

Trace the critical execution path (e.g., request → auth → handler → DB → serialization → response). For each component on the path:

| Scale | Question |
|-------|----------|
| 10x | Does this component have a known scaling limit? (single-threaded, in-memory, no connection pool) |
| 100x | What breaks first? (DB connections, memory, CPU, disk I/O, external API rate limits) |

Also assess organizational scaling:
- Does the test suite run time scale linearly with code size?
- Can the codebase be split into independently deployable units?
- Is there config sprawl (many env vars, many config files, inconsistent patterns)?

**Step 3: Time-horizon analysis**

| Horizon | Assess |
|---------|--------|
| 1 year | Dependency maintenance burden, framework/language ecosystem trajectory |
| 3 years | Tech debt accumulation rate, bus factor impact, documentation drift |
| 5 years | Lock-in risks, calcified areas (too expensive to change), architectural ceilings |

For dependency drift specifically:
```
Bash: git log --oneline -500 --name-only | grep -c 'lock\|package' (how often deps are updated)
Grep: pattern="renovate|dependabot" glob="*.{json,yml,yaml}" (automated update config)
```

**Step 4: Risk register**

For each risk discovered across steps 1-3:

| Field | Value |
|-------|-------|
| **Title** | One-line description |
| **Severity** | Critical / High / Medium / Low |
| **Likelihood** | High / Medium / Low |
| **Impact** | High / Medium / Low |
| **Confidence** | High / Medium / Low |
| **Evidence** | Specific files/patterns |
| **Why it matters** | Business/engineering impact |
| **Suggested fix** | Concrete remediation |
| **Effort** | S / M / L / XL |

### Deliverable
1. Feature gap analysis (blockers vs enhancements table, with effort)
2. Scale analysis (10x bottleneck, 100x breaking point, org scaling limits)
3. Time-horizon risks (1yr, 3yr, 5yr)
4. Prioritized risk register (top 10-15 risks, ordered by severity × likelihood)
5. Advisory roadmap draft: 5 quick wins, 5 medium improvements, 3 strategic investments
6. Planning constraints for `/project-direction`: required spec work, sequencing constraints, and explicit deprioritizations

---

## Cross-Domain Concerns

These topics span multiple domains. The listed agent has **primary ownership**, but other agents should flag related findings.

| Concern | Primary | Also relevant to | What to coordinate |
|---------|---------|-------------------|-------------------|
| Observability | C (logging/metrics) | D (perf monitoring), E (ops/runbooks) | Is observability sufficient for incident diagnosis? |
| Version strategy | E (release process) | D (API versioning), A (maturity signals) | Is there one coherent versioning approach? |
| Configuration management | E (maintainability) | D (secrets), F (config sprawl) | Are configs consistent, documented, and not sprawling? |
| Developer onboarding | E (docs/DX) | A (project map), C (test running) | Can someone actually set up and run everything? |
| Auth & access control | D (security) | E (CODEOWNERS/review) | Is auth enforced consistently across code AND process? |
| Data integrity | D (data model) | C (error handling), F (scale) | Are there paths where data can become inconsistent? |
