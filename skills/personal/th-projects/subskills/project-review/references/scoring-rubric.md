# Scoring Rubric

Scoring scale: 1-5 per category. Confidence: High / Medium / Low.

Calibrate to project type and stated maturity. A prototype scoring 3 on testing is fine; a production service scoring 3 is a risk. See `project-type-adaptations.md` for per-type calibration.

## N/A Handling

Score a category **N/A** when it genuinely doesn't apply to this project type:
- Observability (6) for a pure library with no runtime
- Security (10) for a local-only CLI that reads/writes files with no network
- Release/ops (14) for a prototype or spike
- Data/API design (12) for a project with no API or data layer

Mark as N/A with a one-line justification. Do NOT force a 1-5 score on inapplicable categories — it distorts the average.

## Confidence Guidelines

- **High**: 5+ pieces of evidence examined, patterns are clear and consistent
- **Medium**: 2-4 pieces of evidence, or evidence is mixed/ambiguous
- **Low**: 0-1 pieces of evidence, or significant areas could not be examined

## 1. Goal Alignment and Product Coherence

| Score | Criteria |
|-------|----------|
| 1 | Normative requirements or README claims don't match implementation; no clear purpose |
| 2 | Partial alignment; major required or stated features missing or broken |
| 3 | Core goals met; some documented or specified features incomplete or diverged |
| 4 | Strong alignment; minor gaps between doctrine/specs/docs and reality |
| 5 | Doctrine/specs/docs accurately reflect capabilities; clear, coherent product vision throughout |

**Evidence to cite**: doctrine/spec claims, README claims, actual code paths, example outputs, feature flags, dead code for unfinished features.

## 2. Architecture and Modularity

| Score | Criteria |
|-------|----------|
| 1 | Monolithic blob; circular dependencies; no discernible structure |
| 2 | Some structure but tight coupling; changing one module risks many others |
| 3 | Reasonable module boundaries; some coupling hotspots |
| 4 | Clean separation of concerns; dependency direction is intentional |
| 5 | Well-defined boundaries; modules are independently testable and replaceable |

**Evidence to cite**: Import graphs, package/module structure, interface definitions, dependency injection patterns, circular imports.

## 3. Code Clarity and Craftsmanship

| Score | Criteria |
|-------|----------|
| 1 | Unreadable; inconsistent naming; magic numbers; copy-paste duplication |
| 2 | Readable in spots but inconsistent; poor naming or confusing control flow |
| 3 | Generally readable; some unclear sections; minor style inconsistencies |
| 4 | Clean, consistent style; good naming; intent is clear |
| 5 | Exemplary clarity; self-documenting code; appropriate abstractions |

**Evidence to cite**: Specific functions/files, naming conventions, linter config, code complexity metrics if available.

## 4. Correctness and Reliability

| Score | Criteria |
|-------|----------|
| 1 | Obvious bugs; race conditions; data corruption paths |
| 2 | Fragile; edge cases unhandled; partial implementations |
| 3 | Core paths work; some edge cases unhandled |
| 4 | Robust core with good edge-case handling; few known issues |
| 5 | Comprehensive correctness; defensive coding; invariant enforcement |

**Evidence to cite**: Bug patterns, TODO/FIXME/HACK comments, known-issue trackers, race conditions, null/undefined handling.

## 5. Error Handling and Failure Behavior

| Score | Criteria |
|-------|----------|
| 1 | Errors swallowed or crash the system; no recovery paths |
| 2 | Inconsistent error handling; some paths panic or return ambiguous results |
| 3 | Major paths have error handling; some gaps in edge cases |
| 4 | Consistent error strategy; graceful degradation; clear error messages |
| 5 | Comprehensive error taxonomy; circuit breakers; retry policies; user-friendly errors |

**Evidence to cite**: Try/catch patterns, error types/codes, panic/exit calls, error propagation patterns, user-facing error messages.

## 6. Observability, Tracing, and Debuggability

| Score | Criteria |
|-------|----------|
| 1 | No logging; no metrics; impossible to diagnose production issues |
| 2 | Minimal logging; no structured data; hard to correlate events |
| 3 | Reasonable logging; some metrics; can diagnose common issues |
| 4 | Structured logging; metrics; tracing; dashboards referenced |
| 5 | Full observability stack; distributed tracing; alerting; runbooks |

**Evidence to cite**: Logging framework usage, metric exports, tracing instrumentation, dashboard configs, alert rules.

## 7. Testing Strategy and Test Quality

| Score | Criteria |
|-------|----------|
| 1 | No tests or only trivial/broken tests |
| 2 | Some unit tests; no integration tests; low coverage of critical paths |
| 3 | Decent unit coverage; some integration tests; gaps in edge cases |
| 4 | Layered testing (unit/integration/e2e); good coverage of critical paths |
| 5 | Comprehensive strategy; mutation testing or property testing; test infra is maintained |

**Evidence to cite**: Test directories, test runner config, coverage reports, CI test steps, test-to-code ratio, fixture quality.

## 8. Tooling and Engineering Hygiene

| Score | Criteria |
|-------|----------|
| 1 | No linting, formatting, or type checking; manual everything |
| 2 | Some tooling but inconsistently applied; no pre-commit hooks |
| 3 | Linting and formatting configured; some automation |
| 4 | Comprehensive tooling; CI enforces standards; good developer scripts |
| 5 | Best-in-class toolchain; reproducible builds; dev containers; Makefile/taskfile |

**Evidence to cite**: Linter configs, formatters, pre-commit hooks, Makefile/scripts, CI config, editor configs.

## 9. Dependency and Ecosystem Health

| Score | Criteria |
|-------|----------|
| 1 | Outdated deps with known CVEs; no lock file; unmaintained libraries |
| 2 | Some outdated deps; lock file present but stale; risky transitive deps |
| 3 | Dependencies mostly current; lock file maintained; some concerns |
| 4 | Well-managed deps; regular updates; audit process; minimal transitive risk |
| 5 | Exemplary dep hygiene; automated updates; license compliance; SBOM |

**Evidence to cite**: Lock files, dep age, CVE databases, license files, renovate/dependabot config, transitive dep count.

## 10. Security Posture

| Score | Criteria |
|-------|----------|
| 1 | Hardcoded secrets; SQL injection; no auth; OWASP top-10 violations |
| 2 | Some security measures but inconsistent; secrets in config files |
| 3 | Reasonable security; auth present; input validation on major paths |
| 4 | Strong security posture; secrets management; RBAC; security headers |
| 5 | Defense in depth; security scanning in CI; threat model; penetration-tested |

**Evidence to cite**: Auth middleware, input validation, secrets management, security headers, CSP, CORS config, .env handling.

## 11. Performance and Scalability

| Score | Criteria |
|-------|----------|
| 1 | O(n²) algorithms in hot paths; no caching; unbounded queries |
| 2 | Some performance issues; no benchmarks; scaling concerns |
| 3 | Acceptable performance; some optimization; basic caching |
| 4 | Good performance awareness; benchmarks; connection pooling; pagination |
| 5 | Optimized hot paths; load testing; auto-scaling; performance budgets |

**Evidence to cite**: Algorithm complexity, query patterns, caching layers, benchmark files, connection pool config, pagination.

## 12. Data Model and API Design

| Score | Criteria |
|-------|----------|
| 1 | No schema; inconsistent APIs; breaking changes without versioning |
| 2 | Partial schema; API inconsistencies; no versioning strategy |
| 3 | Reasonable data model; API mostly consistent; some versioning |
| 4 | Well-designed schema; consistent API patterns; migration strategy |
| 5 | Thoughtful data model; API versioning; backward compatibility; OpenAPI/GraphQL schema |

**Evidence to cite**: Schema files, migration directories, API route definitions, OpenAPI specs, GraphQL schemas, serializers.

## 13. Documentation and Developer Experience

| Score | Criteria |
|-------|----------|
| 1 | No docs; no README; impossible to onboard |
| 2 | Minimal README; no setup guide; tribal knowledge required |
| 3 | Decent README; some API docs; setup works with effort |
| 4 | Good docs; clear setup; architecture docs; contribution guide |
| 5 | Excellent DX; interactive examples; API docs; searchable; maintained |

**Evidence to cite**: README quality, setup instructions, API docs, architecture docs, contribution guide, examples directory.

## 14. Release, Operations, and Production Readiness

| Score | Criteria |
|-------|----------|
| 1 | Manual deployment; no versioning; no rollback plan |
| 2 | Some automation; inconsistent versioning; fragile deploy |
| 3 | CI/CD present; versioning scheme; basic deploy automation |
| 4 | Robust CI/CD; semantic versioning; rollback capability; health checks |
| 5 | Full GitOps; canary/blue-green; feature flags; runbooks; incident response |

**Evidence to cite**: CI/CD configs, Dockerfile, deploy scripts, version tags, changelog, health check endpoints, runbooks.

## 15. Maintainability and Change Safety

| Score | Criteria |
|-------|----------|
| 1 | Any change is risky; no tests; no types; high coupling |
| 2 | Changes often break things; regression-prone areas |
| 3 | Most changes are safe; some brittle areas; decent test coverage |
| 4 | High change confidence; good test coverage; type safety; code review |
| 5 | Refactoring is routine; comprehensive tests; feature flags; incremental rollout |

**Evidence to cite**: Type system usage, test coverage, code review config, feature flag system, migration patterns.
