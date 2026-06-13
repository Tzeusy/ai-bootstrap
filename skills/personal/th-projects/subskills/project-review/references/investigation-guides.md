# Investigation Guides

Per-domain checklists for subagent investigators. Each section is self-contained — pass only the relevant domain section to its subagent.

If Phase 0 found usable `project-shape` artifacts, treat them as the normative baseline for every domain. README claims are evidence but do not override doctrine, lore, or spec.

**Tool usage**: Glob for file discovery, Grep for content search. Bash only for piping (`wc -l`, `sort`).

---

## Domain A: Project Mapping, Normative Baseline & Goal Inference

**Objective**: Build the project map, establish the normative baseline, infer goals. Grounds all other investigations.

### Examine
- Shape artifacts: `about/heart-and-soul/`, `about/legends-and-lore/`, `about/lay-and-land/`, `openspec/`
- README.md, docs/, wiki refs
- Manifests: package.json, pyproject.toml, Cargo.toml, go.mod, Gemfile, pom.xml, build.gradle
- Entry points: main.*, index.*, app.*, cmd/, bin/, src/main
- Directory structure (top 3 levels)
- .gitmodules, monorepo config (nx.json, lerna.json, turbo.json, pnpm-workspace.yaml)
- CI/CD: .github/workflows/, .gitlab-ci.yml, Jenkinsfile, .circleci/
- Deploy: Dockerfile, docker-compose.yml, k8s/, terraform/, serverless.yml, fly.toml
- DB: migrations/, schema files, ORM config, prisma/, alembic/
- Changelog, git tags, CONTRIBUTING.md, LICENSE

### Search patterns
```
Glob: "about/heart-and-soul/**/*", "about/legends-and-lore/**/*", "about/lay-and-land/**/*", "openspec/**/*"
Glob: "**/main.*", "**/index.*", "**/app.*", "cmd/**/*", "bin/**/*"
Glob: "**/*.proto", "**/*.graphql", "**/openapi.*", "**/swagger.*"
Grep: pattern="description" glob="package.json"   # project description
Bash: git log --oneline -20                        # goal inference
Bash: git tag --sort=-creatordate | head -10       # version history
```

### Deliverable — structured summary
1. **Shape maturity** + which pillars exist
2. **Normative baseline** (doctrine, design contracts, specs, topology)
3. **Languages & frameworks** (evidence: extensions, imports, configs)
4. **Entry points & services** (what runs, what deploys)
5. **Dependency management** (lock files, version pinning)
6. **Test structure** (dirs, frameworks, CI test steps)
7. **CI/CD pipeline** (stages, triggers, deploy targets)
8. **Infrastructure** (containers, cloud, DBs, caches, queues)
9. **Maturity signals** (versioning, changelog, contribution guide, benchmarks, runbooks)
10. **Explicit goals** (doctrine, specs, README, docs, package description)
11. **Implicit goals** (architecture choices; built but undocumented)
12. **Goal contradictions** (where doctrine/spec/README and code disagree)

---

## Domain B: Code Quality & Architecture (Categories 1-4)

**Objective**: Evaluate goal alignment, architecture, code clarity, correctness.

### Examine
- Module/package structure and import graph
- Core abstractions: interfaces, base classes, type definitions
- Dependency direction (do high-level modules import low-level?)
- Code style consistency: naming, indentation, patterns
- Complexity hotspots: longest files, deepest nesting, most imports
- Type coverage: untyped code, `any` usage, type ignores
- Generated code (exclude from scoring): protobuf output, ORM migrations, bundled assets

### Search patterns
```
# Complexity hotspots — use scan churn data, then read top files
Bash: find . -name '*.ts' -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o -name '*.java' | \
  xargs wc -l 2>/dev/null | sort -rn | head -20

Grep: pattern="TODO|FIXME|HACK|WORKAROUND" glob="*.{ts,py,go,rs,java,rb}"   # debt density

# Imports (per language)
Grep: pattern="^import |^from " glob="*.py"
Grep: pattern="^import " glob="*.{ts,tsx,js,jsx}"
Grep: pattern="^import " glob="*.go"

# Type-safety gaps
Grep: pattern=": any\b|as any" glob="*.{ts,tsx}"
Grep: pattern="# type: ignore" glob="*.py"
Grep: pattern="\.unwrap\(\)" glob="*.rs"
```

### Key questions
- Module structure reflects domain, or purely framework-driven?
- Clear interface boundaries between major components?
- Function purpose clear from name + signature?
- Unsafe patterns (unchecked unwrap, unvalidated casts, race conditions)?
- Ratio of business logic to boilerplate?
- God files (>500 lines) or god modules (>20 exports)?

### Deliverable
Scored (1-5 + confidence) for categories 1-4: specific file/function evidence per claim · what works · what's weak/risky · concrete remediation.

---

## Domain C: Reliability & Tooling (Categories 5-8)

**Objective**: Evaluate error handling, observability, testing, engineering hygiene.

### Examine
- Error handling: try/catch, Result types, error middleware, panic/unwrap
- Logging: framework, structured vs unstructured, levels, correlation IDs
- Metrics: prometheus, StatsD, custom metrics, dashboards
- Tracing: OpenTelemetry, Datadog, Jaeger
- Test dirs: tests/, __tests__/, spec/, *_test.go, *_test.rs
- Test config: jest.config, pytest.ini, vitest.config, coverage thresholds
- Test types: unit, integration, e2e, snapshot, property-based, load
- CI: test steps, coverage gates, required checks, flaky indicators
- Linter/formatter: .eslintrc, .prettierrc, ruff.toml, clippy, golangci-lint
- Pre-commit: .pre-commit-config.yaml, husky, lint-staged
- Build scripts: Makefile, justfile, package.json scripts

### Search patterns
```
Grep: pattern="catch|except |\.catch\(|Error\(|panic\(|unwrap\(\)" glob="*.{ts,py,go,rs}"
Grep: pattern="throw new|raise |return err|Err\(" glob="*.{ts,py,go,rs}"
Grep: pattern="logger\.|log\.(info|warn|error|debug)|console\.(log|error|warn)" glob="*.{ts,py,go,js}"
Grep: pattern="skip|xfail|flaky|retry|@pytest.mark.skip" glob="*.{ts,py,go,rs}"   # flaky tests
Glob: ".github/workflows/*.yml"                                                    # then read test steps
Glob: "**/jest.config.*", "**/vitest.config.*", "**/pytest.ini", "**/conftest.py"
Grep: pattern="coverage|threshold|--cov|istanbul|nyc|c8" glob="*.{json,yml,yaml,toml,cfg}"
```

### Key questions
- Consistent error-handling strategy or ad-hoc?
- Can you diagnose a prod issue from logs alone?
- % of critical paths with test coverage?
- Tests check behavior or implementation details?
- Test suite fast enough to run on every commit?
- Flaky tests (skip/retry annotations)?
- CI checks block merges?

### Deliverable
Scored (1-5 + confidence) for categories 5-8 with evidence.

---

## Domain D: Security, Performance & Data (Categories 9-12)

**Objective**: Evaluate dependencies, security, performance, data/API design.

### Examine
- **Dependencies (9)**: lock files + pinning strategy; direct vs transitive count; renovate.json/dependabot.yml; license compliance
- **Security (10)**: auth middleware, JWT, session mgmt; input validation/sanitizers; secrets (.env, hardcoded, creds in code); CORS/CSP/headers; SQL/NoSQL injection vectors; rate limiting/abuse prevention
- **Performance (11)**: algorithm complexity in hot paths; caching (Redis, in-memory, HTTP cache headers); DB indexes, query optimization, N+1; connection pooling, timeouts; pagination/query bounding
- **Data/API (12)**: route definitions + versioning; schemas (OpenAPI, GraphQL, Protobuf); migrations + rollback; serialization consistency; error-response format across endpoints

### Search patterns
```
# HIGH PRIORITY: secrets in code (check first)
Grep: pattern="password|secret|api_key|apikey|token|credential|private_key" glob="*.{ts,py,go,env,yml,yaml,json,toml}" -i=true
Grep: pattern="(sk-|pk-|ghp_|gho_|AKIA)" glob="*.{ts,py,go,json,yml,env}"   # secret prefixes

# SQL injection
Grep: pattern="f\".*SELECT|f\".*INSERT|f\".*UPDATE|f\".*DELETE" glob="*.py"
Grep: pattern="`.*(SELECT|INSERT|UPDATE|DELETE)" glob="*.{ts,js}"
Grep: pattern='"\+.*SELECT|string\.Format.*SELECT' glob="*.{cs,java}"

Grep: pattern="auth|authenticate|authorize|middleware|guard|protect" glob="*.{ts,py,go,rs,java}"
Grep: pattern="router\.|app\.(get|post|put|delete|patch)|@(app\.route|router)|HandleFunc" glob="*.{ts,py,go,java}"
Grep: pattern="for.*\n.*\.find|for.*\n.*\.query|for.*\n.*\.get" multiline=true glob="*.{ts,py}"   # N+1

# Dependency count
Bash: cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'deps: {len(d.get(\"dependencies\",{}))}, devDeps: {len(d.get(\"devDependencies\",{}))}')" 2>/dev/null || true
```

### Key questions
- Known CVEs in deps? (lock file age, automated-update config)
- Auth consistently enforced across all endpoints? Skip lists?
- SQL injection or XSS vectors?
- Queries bounded (pagination, limits, timeouts)?
- Data model normalized for the use case?
- Migration strategy supports rollback?
- API responses consistent in format across endpoints?

### Deliverable
Scored (1-5 + confidence) for categories 9-12 with evidence.

---

## Domain E: Documentation, Maintainability & Operations (Categories 13-15)

**Objective**: Evaluate docs, DX, release process, long-term maintainability.

### Examine
- README quality + accuracy (mentally walk the setup steps)
- API docs (generated or hand-written); architecture docs, ADRs; examples/; CONTRIBUTING.md; changelog/release notes
- CI/CD: stages, gates, deploy process; Dockerfile/docker-compose for local dev
- Version strategy: semver, calver, tags
- Health-check endpoints, readiness/liveness probes; runbooks, incident-response docs
- Type strictness: TS strict mode, mypy strict
- Code-review config: CODEOWNERS, required reviewers, branch protection; feature-flag system; migration + rollback capability
- `about/craft-and-care/` (engineering-standards pillar): exists? Do its stated standards — testing discipline, review expectations, observability, verification, documentation — match observed practice? Divergence is a normative violation, not a style note; absence is a shape gap to record.

### Search patterns
```
Glob: "**/*.md"                                            # then filter node_modules, vendor
Glob: "docs/**/*", "examples/**/*", "ADR/**/*", "adr/**/*"
Grep: pattern="\"strict\": true|strict = true|strict_mode" glob="tsconfig.json"
Grep: pattern="strict = true|disallow_untyped" glob="mypy.ini"
Grep: pattern=": any\b" glob="*.{ts,tsx}" output_mode="count"
Glob: "**/CODEOWNERS", "**/.github/CODEOWNERS"
Grep: pattern="required_approving_review_count|branch_protection" glob="*.{yml,yaml}"
Grep: pattern="feature.flag|featureFlag|FEATURE_|feature_toggle|LaunchDarkly|unleash" glob="*.{ts,py,go,java}"
Grep: pattern="health|readiness|liveness|/healthz|/ready|/alive" glob="*.{ts,py,go,java,yml,yaml}"
Glob: "about/craft-and-care/**/*.md"
```

### Key questions
- New dev can set up + contribute within a day?
- Release process automated + repeatable?
- Bus factor? (git contributor distribution, CODEOWNERS breadth)
- How safe are changes? What guardrails (types, tests, CI gates, review)?
- Areas nobody wants to touch? (churn hotspots from scan)

### Deliverable
Scored (1-5 + confidence) for categories 13-15 with evidence.

---

## Domain F: Feature Gaps, Scale & Risk Analysis

**Objective**: Identify missing capabilities, scaling limits, prioritized risks.

### Step 1: Feature gap discovery

Read `references/project-type-adaptations.md` for standard expectations per project type. For each expected feature: check the shape baseline first (if doctrine/spec/topology defines it, treat as normative), then determine present / partial / absent.

Categorize gaps:

| Category | Look for |
|----------|----------|
| Core features | Stated in README but missing in code |
| Operational | Health checks, graceful shutdown, rate limiting, circuit breakers, retry policies |
| DX | Dev server, hot reload, debugging config, setup scripts, seed data |
| Enterprise/readiness | SSO, RBAC, audit logging, multi-tenancy, SBOM, compliance controls |

Per gap: **blocker** (prevents use in stated context) vs **enhancement** · **user impact** (end user / operator / contributor) · **evidence** intended? (TODO, open issue, empty stub) · **effort** S (<1d) / M (1-5d) / L (1-3w) / XL (>3w).

### Step 2: Scale analysis

Trace the critical path (request → auth → handler → DB → serialization → response). Per component:

| Scale | Question |
|-------|----------|
| 10x | Known scaling limit? (single-threaded, in-memory, no connection pool) |
| 100x | What breaks first? (DB connections, memory, CPU, disk I/O, external API rate limits) |

Org scaling: test suite run time scales linearly with code size? Codebase splittable into independently deployable units? Config sprawl (many env vars/config files, inconsistent patterns)?

### Step 3: Time-horizon analysis

| Horizon | Assess |
|---------|--------|
| 1 year | Dependency maintenance burden, framework/language ecosystem trajectory |
| 3 years | Tech-debt accumulation rate, bus-factor impact, documentation drift |
| 5 years | Lock-in risks, calcified areas (too expensive to change), architectural ceilings |

Dependency drift:
```
Bash: git log --oneline -500 --name-only | grep -c 'lock\|package'   # update frequency
Grep: pattern="renovate|dependabot" glob="*.{json,yml,yaml}"          # automated updates
```

### Step 4: Risk register

Per risk across steps 1-3: **Title** · **Severity** C/H/M/L · **Likelihood** H/M/L · **Impact** H/M/L · **Confidence** H/M/L · **Evidence** (files/patterns) · **Why it matters** · **Suggested fix** · **Effort** S/M/L/XL.

### Deliverable
1. Feature gap analysis (blockers vs enhancements table, with effort)
2. Scale analysis (10x bottleneck, 100x breaking point, org limits)
3. Time-horizon risks (1yr, 3yr, 5yr)
4. Prioritized risk register (top 10-15, by severity × likelihood)
5. Advisory roadmap draft: 5 quick wins, 5 medium, 3 strategic
6. Planning constraints for `/project-direction`: required spec work, sequencing constraints, explicit deprioritizations

---

## Cross-Domain Concerns

Listed agent has **primary ownership**; others flag related findings.

| Concern | Primary | Also relevant to | Coordinate |
|---------|---------|------------------|------------|
| Observability | C (logging/metrics) | D (perf monitoring), E (ops/runbooks) | Sufficient for incident diagnosis? |
| Version strategy | E (release) | D (API versioning), A (maturity signals) | One coherent versioning approach? |
| Configuration management | E (maintainability) | D (secrets), F (config sprawl) | Configs consistent, documented, not sprawling? |
| Developer onboarding | E (docs/DX) | A (project map), C (test running) | Can someone actually set up + run everything? |
| Auth & access control | D (security) | E (CODEOWNERS/review) | Auth enforced across code AND process? |
| Data integrity | D (data model) | C (error handling), F (scale) | Paths where data can become inconsistent? |
