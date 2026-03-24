# Beads Field Reference & Examples

## Complete Field Schema

### Core Identity
| Field | Flag | Required | Description |
|-------|------|----------|-------------|
| title | positional or `--title` | Yes | Short imperative summary (<72 chars) |
| type | `-t` / `--type` | Yes | `task`, `bug`, `feature`, `chore`, `epic` |
| status | `-s` / `--status` | Auto | `open` (default), `in_progress`, `blocked`, `deferred`, `closed` |
| id | auto-generated | Auto | Hash-based identifier (e.g., `bd-a3f8e9`) |

### Content Fields
| Field | Flag | Purpose |
|-------|------|---------|
| description | `-d` / `--description` | Detailed body: what, why, context, repro steps |
| notes | `--notes` | Implementation notes, caveats, references |
| design | `--design` | Architecture decisions, technical approach |
| acceptance | `--acceptance` | Testable success criteria |

### Metadata
| Field | Flag | Values |
|-------|------|--------|
| priority | `-p` / `--priority` | 0-4 (0=critical, 2=medium/default, 4=backlog) |
| labels | `-l` / `--labels` | Comma-separated tags (e.g., `backend,api,security`) |
| assignee | `-a` / `--assignee` | Username |
| estimate | `-e` / `--estimate` | Minutes (integer) |
| due | `--due` | Date: absolute (`2025-03-01`) or relative (`+2d`, `tomorrow`) |

### Relationships
| Field | Flag | Purpose |
|-------|------|---------|
| parent | `--parent` | Parent epic ID for hierarchy |
| deps | `--deps` | Dependency field (`blocks:ID`, `discovered-from:ID`, `relates_to:ID`, `waits-for:ID`). In this repo, create dependencies with `bd dep add <issue> <depends-on>` after creation for stability. |

### External
| Field | Flag | Purpose |
|-------|------|---------|
| external_ref | `--external-ref` | Link to external tracker (e.g., `gh-42`, `jira-PROJ-123`) |
| spec_id | `--spec-id` | Link to specification document |

---

## Type Selection Guide

| Type | When to Use | Example |
|------|-------------|---------|
| `task` | General work items, implementation | "Add pagination to user list API" |
| `bug` | Defects, broken behavior | "Fix timeout on login with 2FA on mobile Safari" |
| `feature` | New user-facing capability | "Add dark mode support" |
| `chore` | Maintenance, cleanup, upgrades | "Upgrade Node.js to v20 LTS" |
| `epic` | Large work spanning multiple issues | "User authentication system" |

---

## Priority Calibration

| Priority | Label | Signal | Example |
|----------|-------|--------|---------|
| P0 | Critical | Production down, data loss, security breach | "Fix SQL injection in login endpoint" |
| P1 | High | Significant impact, blocking other work | "Fix payment processing failure for EU customers" |
| P2 | Medium | Important but not urgent (default) | "Add input validation to settings form" |
| P3 | Low | Nice to have, minor improvement | "Improve error message wording on 404 page" |
| P4 | Backlog | Future consideration, no urgency | "Investigate alternative caching strategies" |

---

## Exemplary Beads by Type

### Bug Report

```bash
bd create "Fix timeout on login with 2FA on mobile Safari" \
  --type bug \
  --priority 1 \
  --description "Users report 30s timeout during 2FA TOTP verification on mobile Safari (iOS 17+). Desktop browsers and mobile Chrome work normally. The POST to /api/auth/verify-totp hangs until the browser kills it. Likely related to Safari's aggressive connection timeout on cellular networks.

Steps to reproduce:
1. Open app in mobile Safari on iPhone
2. Enter credentials and submit
3. Enter valid TOTP code
4. Observe 30s hang then timeout error

Expected: 2FA verification completes in <3s
Actual: Request hangs for 30s then fails" \
  --acceptance "2FA flow completes in <5s on mobile Safari iOS 17+. Verified on both WiFi and cellular." \
  --labels security,frontend,mobile \
  --estimate 120
```

### Feature Request

```bash
bd create "Add cursor-based pagination to user list API" \
  --type feature \
  --priority 2 \
  --description "The GET /api/users endpoint returns all users in a single response. For deployments with >10k users this causes memory pressure on the API server and >5s response times on the client.

Need cursor-based pagination following our existing pattern from the /api/audit-logs endpoint. Must be backwards-compatible (no page params = return first page with default limit)." \
  --design "Cursor-based pagination using opaque base64 cursor encoding the last-seen user ID. Parameters: page_size (default 50, max 200), after_cursor (opaque string). Response includes: data[], next_cursor (null if last page), total_count, has_more." \
  --acceptance "1. API handles 100k+ users without timeout
2. Response includes pagination metadata (next_cursor, total_count, has_more)
3. Existing clients without pagination params still work (backwards compat)
4. Cursor is opaque and tamper-resistant" \
  --labels backend,api,performance \
  --estimate 240
```

### Task with Dependency

```bash
TEST_ID=$(bd create --title="Add unit tests for PSF scoring algorithm" \
  --type=task \
  --priority=2 \
  --description="PSF scoring was implemented in bd-a3f8e9 but shipped without test coverage. Need comprehensive unit tests covering:
- Normal scoring with complete input data
- Edge cases: missing fields, zero values, negative scores
- Boundary conditions at score thresholds (0, 50, 100)
- Input validation (reject malformed data gracefully)" \
  --acceptance="1. >90% branch coverage on scoring module
2. Tests cover all edge cases listed in description
3. Tests run in <2s" \
  --labels=testing,backend \
  --estimate=90 \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

bd dep add $TEST_ID bd-a3f8e9
```

### Epic with Children

```bash
# Create the epic (capture ID from JSON)
EPIC=$(bd create --title="User authentication system" --type=epic --priority=1 \
  --description="Replace the current session-cookie auth with JWT-based authentication. Includes password hashing upgrade, token lifecycle, login UI, and integration tests." \
  --design "JWT with RS256 signing. Access tokens (15min TTL) + refresh tokens (7d TTL, stored in httpOnly cookie). Argon2id for password hashing. Middleware validates on every request." \
  --acceptance="1. All existing auth flows work with JWT
2. Token refresh is transparent to the user
3. Password hashes upgraded on next login (lazy migration)
4. No session cookies remain in the system" \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Create children — each is a focused, single-responsibility task
HASH_ID=$(bd create --title="Implement Argon2id password hashing" --type=task --priority=1 --parent=$EPIC \
  --description="Replace bcrypt with Argon2id. Lazy migration: re-hash on successful login. Keep bcrypt verification for unmigrated passwords." \
  --estimate=120 \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

JWT_ID=$(bd create --title="Add JWT token generation and validation middleware" --type=task --priority=1 --parent=$EPIC \
  --description="RS256-signed JWTs. Access token 15min, refresh token 7d. Middleware extracts and validates on every request. Refresh endpoint issues new access token." \
  --estimate=180 \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

UI_ID=$(bd create --title="Build login and token refresh UI" --type=task --priority=2 --parent=$EPIC \
  --description="Update login form to handle JWT flow. Add silent token refresh before expiry. Handle refresh failure (redirect to login)." \
  --estimate=120 \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

TEST_ID=$(bd create --title="Write auth integration tests" --type=task --priority=2 --parent=$EPIC \
  --description="End-to-end tests: login, token refresh, expired token rejection, password migration, concurrent refresh requests." \
  --estimate=90 \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Optional cross-dependency among implementation children
bd dep add $JWT_ID $HASH_ID

# Final reconciliation bead (always create last)
RECON_ID=$(bd create --title="Reconcile spec-to-code coverage for auth system" --type=task --priority=1 --parent=$EPIC \
  --description="Deep-dive review: map each epic requirement to implementing child beads and code changes. For uncovered requirements, create implementation/fix child beads under this epic (do not create another reconciliation bead). Keep this bead open until all gap beads close, then re-run the checklist and close with a coverage summary." \
  --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Ensure reconciliation runs last by depending on all implementation children
bd dep add $RECON_ID $HASH_ID
bd dep add $RECON_ID $JWT_ID
bd dep add $RECON_ID $UI_ID
bd dep add $RECON_ID $TEST_ID
```

### Chore

```bash
bd create "Upgrade Node.js from 18 to 20 LTS" \
  --type chore \
  --priority 3 \
  --description "Node.js 18 reaches EOL in April 2025. Upgrade to 20 LTS for continued security patches. Need to verify all dependencies are compatible and update CI pipeline." \
  --acceptance "1. All tests pass on Node 20
2. CI pipeline updated to use Node 20
3. .nvmrc updated
4. No runtime warnings in dev or production" \
  --labels infra,ci \
  --estimate 60
```

---

## Label Taxonomy (Suggested Conventions)

### By Component
`frontend`, `backend`, `api`, `database`, `infra`, `ci`, `docs`

### By Concern
`security`, `performance`, `accessibility`, `ux`, `tech-debt`, `testing`

### By Urgency (use sparingly — priority field is primary)
`urgent`, `blocking`

### By Platform
`mobile`, `desktop`, `ios`, `android`, `linux`, `macos`

Prefer consistent, lowercase, hyphenated labels. Avoid proliferating one-off labels — reuse existing ones where possible.
