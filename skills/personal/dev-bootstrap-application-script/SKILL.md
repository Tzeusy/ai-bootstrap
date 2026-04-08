---
name: dev-bootstrap-application-script
description: This skill should be used when asked to create a dev.sh (or similar) bash script that launches an application's full stack in tmux. It guides research of the project's services, generates an idempotent tmux bootstrap script with named windows, pane-ID-based splits, health checks, env loading, and sanitized per-run stdout/stderr logs.
---

# Dev Bootstrap Application Script

## Overview

Generate an idempotent bash script that launches every service in a project's full stack inside named tmux window(s), with up to 4 panes per window. The script handles session detection, window teardown/recreation, dependency ordering, health checks, per-run log capture, and optional reverse-proxy path-prefix bootstrapping (for tailscale serve, cloudflared, etc.).

A ready-made template is bundled at `assets/dev.sh.template`.

## When to Use

- A user asks to "write a dev script", "bootstrap the app in tmux", or "create a dev.sh"
- A user wants to launch multiple services (API, frontend, workers, databases) in one command
- A user has an existing dev script and wants it rewritten following best practices

## Workflow

### Phase 1 — Research the Project

Before writing any code, discover what services the project needs. Read the following files (when present) to build a service inventory:

| File | What to look for |
|---|---|
| `docker-compose.yml` / `compose.yaml` | Infrastructure services (postgres, redis, rabbitmq, etc.) |
| `package.json` | `scripts.dev`, `scripts.start`, framework (Next.js, Vite, Remix, etc.) |
| `Makefile` / `Justfile` | Existing `dev` / `run` / `serve` targets |
| `Procfile` / `Procfile.dev` | Named processes and their commands |
| `pyproject.toml` / `Pipfile` | Python entry points, uvicorn/gunicorn commands |
| `Cargo.toml` / `go.mod` | Build-and-run patterns |
| `.env` / `.env.example` | Environment variables needed at boot |
| `turbo.json` / `pnpm-workspace.yaml` | Monorepo workspace structure |
| `README.md` | "Getting Started" / "Development" sections |
| Frontend router / API client files | Whether routes and API calls are base-path aware |
| Vite/Next/webpack dev config | Base path and dev proxy rewrite behavior |

Produce a **service inventory** — an ordered list of:

```
1. Service name — command — working directory — depends on (if any)
```

Example:

```
1. postgres    — docker compose up -d postgres  — .          — (none)
2. redis       — docker compose up -d redis     — .          — (none)
3. api         — uv run uvicorn app:main        — .          — postgres, redis
4. frontend    — npm run dev                    — ./frontend — api
```

### Phase 2 — Design the Layout

#### Pane Limit

Maximum **4 panes per tmux window**. Beyond 4, panes become unreadably small.

#### Window Count Decision

| Services | Windows | Rationale |
|---|---|---|
| 1-4 | 1 window | Everything fits |
| 5-8 | 2 windows | Group by concern (infra vs app, backend vs frontend) |
| 9+ | 3 windows | Rare — consider if some services should stay in docker |

#### Layout Selection

Pick the tmux preset layout that best matches the pane count:

| Panes | Recommended layout | Visual |
|---|---|---|
| 2 | `even-horizontal` | `[A \| B]` |
| 2 | `even-vertical` | `[A / B]` (stacked) |
| 3 | `main-vertical` | `[A \| B/C]` (main left, two right) |
| 3 | `main-horizontal` | `[A / B\|C]` (main top, two bottom) |
| 4 | `tiled` | `[A\|B / C\|D]` (2x2 grid) |

#### Grouping Heuristic

When splitting across multiple windows, group by concern:

- **Window 1 ("infra")**: databases, caches, message brokers, docker services
- **Window 2 ("app")**: API server, background workers, task queues
- **Window 3 ("frontend")**: dev server, storybook, docs site

### Phase 3 — Write the Script

Start from `assets/dev.sh.template` and fill in the placeholders. Follow these mandatory patterns:

#### Script Structure

```
1. Shebang + header comment with layout diagram
2. set -euo pipefail
3. Parse script args (for optional checks like --skip-tailscale-check)
4. PROJECT_DIR and WINDOW constants
5. Optional Layer 0 preflight (tailscale/dependencies/etc.)
6. tmux prerequisite check
7. Session detection (inside tmux vs new session)
8. Kill existing window (idempotency)
9. Create window + split panes (capture pane IDs)
10. Small post-split delay before send-keys
11. Initialize logs directory (timestamped run dir + latest symlink)
12. Register pane log piping before launching commands
13. Load environment variables
14. Layer 1 launch services (send-keys to each pane)
15. Layer 2 readiness gates (health endpoints/ports)
16. Print operator URLs (local + remote when available)
17. Apply layout + set focus
18. Attach if started detached
```

#### Mandatory Rules

- **Pane IDs, never indices.** Always capture pane IDs with `-P -F '#{pane_id}'` and reference them by variable. Never use `tmux select-pane -t 0`.
- **Idempotent.** `tmux kill-window -t "${SESSION}:${WINDOW}" 2>/dev/null || true` before recreating.
- **Session-aware.** Detect `$TMUX` to decide whether to create a session or reuse the current one.
- **Header comment.** Every script must start with an ASCII layout diagram showing what runs where.
- **Per-run logs + latest link.** Create logs under `logs/YYYYmmdd_HHMMSS/` and refresh `logs/latest -> logs/<run_id>`.
- **Pipe with `-o`.** Use `tmux pipe-pane -o` so re-runs do not stack duplicate pipe commands.
- **Layered startup.** Prefer explicit layers (preflight -> launch -> readiness).
- **User-facing URLs.** Always print local frontend URL and API base URL; print remote URL if a reverse proxy is configured.
- **No prefix-only proxying.** If a path prefix is introduced (for example `/app`), all app layers must agree on it (frontend base path, API path, router path parsing, and dev proxy rewrites).

#### Reverse Proxy Prefix Coherency (Mandatory when using path prefixes)

If your script configures a reverse-proxy path prefix (for example `tailscale serve --set-path /myapp`), ensure all of the following are aligned:

1. Frontend dev server base path (`--base`, framework equivalent, or env setting).
2. Frontend router path parsing/navigation (strip/add base path).
3. API client prefix generation (`BASE_URL`-aware, not hardcoded root-only paths).
4. Health/readiness fetch paths (for example `/ready` -> `/myapp/ready` when prefixed).
5. Dev proxy routes and rewrites (strip prefix before forwarding upstream).
6. PWA scope/start_url/assets if PWA is enabled.

Anti-pattern to avoid: adding reverse-proxy path mapping alone while leaving client/router/API paths hardcoded to root.

#### Tailscale Serve Preflight (Optional but Recommended)

When bootstrapping HTTPS access via tailscale:

1. Validate CLI exists (`command -v tailscale`).
2. Validate authenticated state (`tailscale status --json`, reject `NeedsLogin`/`Stopped` states).
3. Inspect existing config first (`tailscale serve status --json`).
4. Only apply missing mapping(s), then re-read status to verify mapping exists.
5. Support CLI compatibility fallback (new vs legacy `tailscale serve` syntax).
6. Emit actionable recovery instructions (manual command, `tailscale up`, permission hint such as `sudo tailscale set --operator=$USER` when relevant).
7. Provide a skip flag (`--skip-tailscale-check`) for local-only workflows.

#### Stdout/Stderr Logging (Mandatory)

Direct `tmux pipe-pane ... "cat >> file"` captures interactive shell control sequences and pollutes logs. Use sanitized piping plus unbuffered writes.

```bash
LOGS_ROOT="${PROJECT_DIR}/logs"
LOGS_RUN_ID="$(date +%Y%m%d_%H%M%S)"
LOGS_RUN_DIR="${LOGS_ROOT}/${LOGS_RUN_ID}"
LOGS_LATEST_LINK="${LOGS_ROOT}/latest"

mkdir -p \
  "${LOGS_RUN_DIR}/backend" \
  "${LOGS_RUN_DIR}/workers" \
  "${LOGS_RUN_DIR}/frontend"
rm -rf "${LOGS_LATEST_LINK}"
ln -s "${LOGS_RUN_DIR}" "${LOGS_LATEST_LINK}"
echo "Logs for this run: ${LOGS_RUN_DIR}"
```

```bash
pipe_pane_to_log() {
  local pane_id="$1"
  local log_file="$2"

  tmux pipe-pane -o -t "$pane_id" \
    "perl -pe 'BEGIN { \$| = 1 } s/\\e\\[[0-?]*[ -\\/]*[@-~]//g; s/\\e\\][^\\a]*(?:\\a|\\e\\\\)//g; s/\\r//g; s/[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]//g' >> '${log_file}'"
}
```

```bash
pipe_pane_to_log "$PANE_API" "${LOGS_RUN_DIR}/backend/api.log"
pipe_pane_to_log "$PANE_WORKER" "${LOGS_RUN_DIR}/workers/worker.log"
pipe_pane_to_log "$PANE_WEB" "${LOGS_RUN_DIR}/frontend/web.log"
```

Requirements:
- Include `BEGIN { $| = 1 }` in the sanitizer so logs are written incrementally (not buffered until process exit/buffer fill).
- Strip CSI + OSC + control characters before writing logs so `logs/latest/**/*.log` remains plain-text and grep-friendly.

#### Pane Creation Patterns

Two panes (horizontal split):
```bash
PANE_LEFT=$(tmux new-window -t "$SESSION" -n "$WINDOW" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_RIGHT=$(tmux split-window -t "$PANE_LEFT" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')
```

Three panes (main-vertical — large left, two stacked right):
```bash
PANE_MAIN=$(tmux new-window -t "$SESSION" -n "$WINDOW" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_TOP_R=$(tmux split-window -t "$PANE_MAIN" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_BOT_R=$(tmux split-window -t "$PANE_TOP_R" -v -c "$PROJECT_DIR" -P -F '#{pane_id}')
```

Four panes (2x2 tiled):
```bash
PANE_TL=$(tmux new-window -t "$SESSION" -n "$WINDOW" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_TR=$(tmux split-window -t "$PANE_TL" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_BL=$(tmux split-window -t "$PANE_TL" -v -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_BR=$(tmux split-window -t "$PANE_TR" -v -c "$PROJECT_DIR" -P -F '#{pane_id}')
```

#### Multiple Windows

When services overflow a single window, create additional windows:

```bash
WINDOW_1="myapp-infra"
WINDOW_2="myapp-app"

# Tear down both
tmux kill-window -t "${SESSION}:${WINDOW_1}" 2>/dev/null || true
tmux kill-window -t "${SESSION}:${WINDOW_2}" 2>/dev/null || true

# Window 1: infrastructure
PANE_DB=$(tmux new-window -t "$SESSION" -n "$WINDOW_1" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_CACHE=$(tmux split-window -t "$PANE_DB" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')

# Window 2: application
PANE_API=$(tmux new-window -t "$SESSION" -n "$WINDOW_2" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_WEB=$(tmux split-window -t "$PANE_API" -h -c "${PROJECT_DIR}/frontend" -P -F '#{pane_id}')
```

#### Environment Loading

```bash
# Single .env file
export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs -d '\n')

# Multiple env files (e.g., secrets + local overrides)
ENV_CMD="export \$(grep -v '^#' /secrets/.env | xargs -d '\n') && export \$(grep -v '^#' .env | xargs -d '\n') && "
tmux send-keys -t "$PANE_API" "${ENV_CMD}uv run uvicorn app:main" Enter
```

#### Health Checks and Dependency Ordering

When a service depends on another (e.g., API needs postgres), use a wait loop:

```bash
# Inline wait-for-port in the pane command
tmux send-keys -t "$PANE_API" \
  "until nc -z localhost 5432 2>/dev/null; do echo 'Waiting for postgres...'; sleep 1; done && uv run uvicorn app:main --reload" Enter
```

For a reusable helper defined at the top of the script:

```bash
wait_for_port() {
  local port=$1 name=${2:-"port $1"} retries=${3:-30}
  echo "Waiting for ${name}..."
  for i in $(seq 1 "$retries"); do
    nc -z localhost "$port" 2>/dev/null && echo "${name} ready" && return 0
    sleep 1
  done
  echo "Timed out waiting for ${name}" >&2
  return 1
}
```

For HTTP readiness gates run in the outer shell (recommended after launch):

```bash
wait_for_http() {
  local url="$1"
  local label="$2"
  local max_wait="${3:-60}"
  local interval=2
  local elapsed=0

  echo "Waiting for ${label} (${url})..."
  while [ "$elapsed" -lt "$max_wait" ]; do
    if curl -sf "$url" >/dev/null 2>&1; then
      echo "${label} ready (${elapsed}s)"
      return 0
    fi
    sleep "$interval"
    elapsed=$((elapsed + interval))
  done
  echo "Warning: ${label} not ready within ${max_wait}s" >&2
  return 1
}
```

Then in the pane:

```bash
tmux send-keys -t "$PANE_API" \
  "source dev.sh.helpers 2>/dev/null; wait_for_port 5432 postgres && uv run uvicorn app:main" Enter
```

Or define the function inline and send it:

```bash
tmux send-keys -t "$PANE_API" \
  'until nc -z localhost 5432; do sleep 1; done && npm start' Enter
```

#### Common Service Patterns

| Stack | Typical command |
|---|---|
| Docker infra | `docker compose up -d postgres redis` (run once in first pane, then start app) |
| Python (uv) | `uv sync --dev && uv run uvicorn app:main --reload` |
| Python (pip) | `pip install -e '.[dev]' && python -m app` |
| Node (npm) | `npm install && npm run dev` |
| Node (pnpm) | `pnpm install && pnpm dev` |
| Go | `go run ./cmd/server` |
| Rust | `cargo watch -x run` |
| Ruby/Rails | `bundle install && bin/rails server` |
| Elixir/Phoenix | `mix deps.get && mix phx.server` |
| Next.js | `npm install && npm run dev -- --port 3000` |
| Vite | `npm install && npm run dev -- --host 0.0.0.0` |

### Phase 4 — Verify

Before delivering the script, verify:

- [ ] `set -euo pipefail` is present
- [ ] Header comment includes ASCII layout diagram
- [ ] All pane references use captured `$PANE_*` variables, never indices
- [ ] `tmux kill-window` teardown precedes window creation (idempotent)
- [ ] Both `$TMUX` / non-`$TMUX` paths are handled
- [ ] Script supports layered startup (preflight, launch, readiness)
- [ ] Services with dependencies have a wait/health-check
- [ ] HTTP readiness checks exist for critical endpoints where applicable
- [ ] Working directories (`-c` flag) are correct for each pane
- [ ] Layout command matches pane count
- [ ] Logs are written to `logs/<YYYYmmdd_HHMMSS>/...` and `logs/latest` points to that run
- [ ] `tmux pipe-pane -o` is used for each pane log sink
- [ ] Logs are clean (no ANSI escape sequences), e.g. `rg -nP "\x1b" logs/latest/**/*.log` returns nothing
- [ ] Script is `chmod +x`-able (shebang present)
- [ ] Max 4 panes per window; overflow uses additional named windows
- [ ] If using a path prefix, frontend base/router/API/proxy/health paths are coherent end-to-end
- [ ] If using tailscale serve, script checks status first and verifies mapping after apply
- [ ] Script includes compatibility fallback for tailscale CLI argument variants when needed
- [ ] Script prints local URLs and (if configured) the remote/tailnet URL
- [ ] A short post-split delay exists before `tmux send-keys` to avoid dropped keystrokes on fast reruns

## Assets

- `assets/dev.sh.template` — Skeleton script with all placeholders. Copy and fill in.
