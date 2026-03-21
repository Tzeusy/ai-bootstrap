# Project Type Adaptations

Adjust emphasis, expectations, and scoring thresholds based on project type. Use this to calibrate investigation depth per domain.

---

## Library / SDK

**Elevated priority**: Categories 2 (architecture), 3 (code clarity), 12 (API design), 13 (docs/DX), 15 (maintainability)

**Key concerns**:
- API surface clarity and consistency
- Semver adherence and backward compatibility
- Examples and getting-started docs
- Install/import ergonomics across package managers
- Type definitions and IDE support
- Minimal dependency footprint (transitive deps are your users' deps)
- Bundle size (for JS libraries)
- Cross-platform compatibility

**Lower priority**: Categories 6 (observability), 14 (release/ops) — unless it's a hosted service SDK

**Feature gap focus**: Missing examples, missing types, missing platform support, missing migration guides between versions

---

## Backend Service / API

**Elevated priority**: Categories 5 (error handling), 6 (observability), 10 (security), 11 (performance), 14 (release/ops)

**Key concerns**:
- Auth and authorization on every endpoint
- Input validation and sanitization
- Database migration safety and rollback
- Connection pooling, timeouts, circuit breakers
- Health checks and graceful shutdown
- Rate limiting and abuse prevention
- Structured logging with request correlation
- Runbooks for common incidents
- Secrets management (no hardcoded credentials)

**Lower priority**: Category 13 (docs/DX) unless it's a public API

**Feature gap focus**: Missing health checks, missing rate limiting, missing graceful shutdown, missing structured logging, missing auth on endpoints

---

## SaaS Application (Full-stack)

**Elevated priority**: All categories matter; emphasize 4 (correctness), 10 (security), 11 (performance), 14 (release/ops)

**Key concerns**:
- Multi-tenancy isolation
- Payment/billing integration security
- Session management and CSRF protection
- Frontend performance (bundle size, loading, caching)
- State management correctness
- Error states and empty states in UI
- Accessibility (WCAG compliance)
- Feature flagging for safe rollout
- Database migration strategy at scale

**Feature gap focus**: Missing tenant isolation, missing billing security, missing accessibility, missing feature flags

---

## Frontend Application

**Elevated priority**: Categories 3 (code clarity), 4 (correctness), 11 (performance), 13 (docs/DX)

**Key concerns**:
- State management architecture and consistency
- Error boundaries and error states
- Loading states and skeleton screens
- Accessibility (ARIA, keyboard navigation, screen readers)
- Bundle size and code splitting
- Responsive design
- Browser compatibility
- UX consistency across flows
- Component reusability and design system adherence

**Lower priority**: Categories 6 (observability), 14 (release/ops) — unless it's a complex SPA

**Feature gap focus**: Missing error boundaries, missing loading states, missing accessibility, missing responsive design

---

## CLI Tool

**Elevated priority**: Categories 3 (code clarity), 5 (error handling), 13 (docs/DX)

**Key concerns**:
- Exit codes (0 for success, non-zero for failure, distinct codes for distinct errors)
- Scriptability (machine-readable output option: JSON, TSV)
- Stderr vs stdout separation
- Help text and man page quality
- Platform compatibility (Linux, macOS, Windows)
- Config file ergonomics (XDG dirs, sensible defaults)
- Shell completion generation
- Signal handling (SIGINT, SIGTERM)
- Progress indicators for long operations

**Lower priority**: Categories 6 (observability), 11 (performance) — unless it processes large data

**Feature gap focus**: Missing exit codes, missing JSON output, missing shell completions, missing platform support

---

## Mobile Application

**Elevated priority**: Categories 4 (correctness), 5 (error handling), 11 (performance), 10 (security)

**Key concerns**:
- Offline capability and sync
- Battery and memory efficiency
- Secure storage (keychain/keystore)
- Deep linking and navigation
- Push notification handling
- App lifecycle management
- Crash reporting integration
- Backwards compatibility with OS versions
- Store compliance (App Store, Play Store)

**Feature gap focus**: Missing offline support, missing secure storage, missing crash reporting

---

## Monorepo

**Elevated priority**: Categories 2 (architecture), 8 (tooling), 14 (release/ops), 15 (maintainability)

**Key concerns**:
- Package boundaries and dependency direction
- Workspace/package ownership (CODEOWNERS)
- Build graph health and caching (nx, turbo, bazel)
- Independent vs synchronized versioning
- CI pipeline efficiency (affected-only testing)
- Shared code management (internal packages)
- Cross-package type safety
- Release coordination

**Feature gap focus**: Missing build caching, missing CODEOWNERS, missing affected-only CI, missing independent versioning

---

## ML / Data Project

**Elevated priority**: Categories 4 (correctness), 7 (testing), 13 (docs/DX)

**Key concerns**:
- Reproducibility (pinned deps, random seeds, deterministic pipelines)
- Data lineage and versioning (DVC, MLflow, W&B)
- Experiment tracking and comparison
- Model versioning and registry
- Evaluation rigor (proper train/test splits, metrics)
- Pipeline debuggability (intermediate outputs, logging)
- Data validation (schema checks, drift detection)
- GPU/compute resource management
- Notebook hygiene (execution order, cleared outputs)

**Lower priority**: Categories 10 (security), 14 (release/ops) — unless serving models in production

**Feature gap focus**: Missing reproducibility, missing experiment tracking, missing data validation, missing model versioning

---

## Internal Tool

**Elevated priority**: Categories 3 (code clarity), 13 (docs/DX), 15 (maintainability)

**Key concerns**:
- Onboarding documentation (the bus-factor mitigation)
- Authentication integration (SSO, LDAP)
- Reasonable error messages (users are internal but still need help)
- Logging for debugging (not just for ops)
- Simple deployment (should be easy to maintain)

**Lower priority**: Categories 11 (performance), 14 (release/ops) — unless serving high internal traffic

**Feature gap focus**: Missing onboarding docs, missing SSO integration, missing error messages

---

## Infrastructure-as-Code (IaC)

**Elevated priority**: Categories 2 (architecture), 4 (correctness), 7 (testing), 15 (maintainability)

**Key concerns**:
- Idempotency of all operations
- State management (remote state, locking, drift detection)
- Provider/module versioning and pinning
- Plan/apply separation (never auto-apply without review)
- Secret injection (not hardcoded in config)
- Environment parity (dev/staging/prod use same modules)
- Blast radius controls (target limiting, workspace isolation)
- Rollback strategy (can you revert a bad apply?)

**Lower priority**: Categories 6 (observability), 11 (performance)

**Feature gap focus**: Missing remote state, missing drift detection, missing environment parity, missing blast radius controls

---

## Serverless / Lambda

**Elevated priority**: Categories 5 (error handling), 10 (security), 11 (performance), 14 (release/ops)

**Key concerns**:
- Cold start optimization (bundle size, lazy initialization)
- Handler structure (single-responsibility, shared middleware)
- Event source contracts (what triggers what, idempotency)
- Timeout and memory configuration per function
- Dead letter queues for failed invocations
- IAM least-privilege per function
- Local development and testing story (SAM, serverless-offline)
- Observability across distributed invocations (correlation IDs)

**Lower priority**: Categories 2 (architecture) — unless complex event-driven system

**Feature gap focus**: Missing DLQ, missing local dev story, missing correlation IDs, missing per-function IAM

---

## Hybrid Projects

For projects that combine multiple types (e.g., monorepo with frontend + backend, library that's also a CLI):

1. Identify the **primary type** — where most value and risk concentrate.
2. Apply the primary type's elevated/lowered categories at full weight.
3. Import **2-3 key elevated categories** from secondary types.
4. When types conflict on a category's priority, use the **higher** priority.

### Common hybrids

| Combination | Primary | Import from secondary |
|-------------|---------|----------------------|
| Monorepo (frontend + backend) | Monorepo | Security (10) from Backend, Accessibility from Frontend |
| Library + CLI | Library | Error handling (5) and exit codes from CLI |
| Hosted SDK | Library | Observability (6) and Release/ops (14) from Backend |
| Full-stack SaaS | SaaS | All categories at full weight (already specified) |
| Backend + IaC | Backend | Correctness (4) and State management from IaC |
| ML serving in production | Backend | Reproducibility and Evaluation from ML/Data |

---

## Calibrating Maturity Expectations

| Signal | Prototype | Beta | Production | Mission-critical |
|--------|-----------|------|------------|-----------------|
| Tests | Optional | Unit tests | Unit + integration | Full suite + mutation/property |
| CI | Optional | Basic | Comprehensive | Enforced gates |
| Docs | README | README + setup | Full docs | Docs + runbooks + ADRs |
| Security | Basic | Auth present | Security review | Threat model + pen test |
| Observability | Logging | Structured logs | Metrics + tracing | Full stack + alerting |
| Error handling | Console.log | Try/catch | Consistent strategy | Circuit breakers + recovery |
| Deps | Latest | Pinned | Audited | SBOM + automated updates |

Adjust scores relative to these expectations. A prototype with no tests scores 3 (adequate for maturity); a production service with no tests scores 1.
