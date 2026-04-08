# Patterns

Use this reference when the main `SKILL.md` is active and you need exact layout or proxy details.

## Window Selection

| Long-running services | Recommended shape |
| --- | --- |
| 1-4 | one window |
| 5-8 | two windows, grouped by concern |
| 9+ | three windows, or move more infra into docker |

Recommended grouping:

- `infra`: databases, caches, brokers, docker services
- `app`: API server, workers, queue consumers
- `frontend`: web app, docs site, Storybook

## Pane Layouts

Two panes:

```bash
PANE_LEFT=$(tmux new-window -t "$SESSION" -n "$WINDOW" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_RIGHT=$(tmux split-window -t "$PANE_LEFT" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')
```

Three panes:

```bash
PANE_MAIN=$(tmux new-window -t "$SESSION" -n "$WINDOW" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_TOP_R=$(tmux split-window -t "$PANE_MAIN" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_BOT_R=$(tmux split-window -t "$PANE_TOP_R" -v -c "$PROJECT_DIR" -P -F '#{pane_id}')
```

Four panes:

```bash
PANE_TL=$(tmux new-window -t "$SESSION" -n "$WINDOW" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_TR=$(tmux split-window -t "$PANE_TL" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_BL=$(tmux split-window -t "$PANE_TL" -v -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_BR=$(tmux split-window -t "$PANE_TR" -v -c "$PROJECT_DIR" -P -F '#{pane_id}')
```

Two-window pattern:

```bash
WINDOW_INFRA="myapp-infra"
WINDOW_APP="myapp-app"

tmux kill-window -t "${SESSION}:${WINDOW_INFRA}" 2>/dev/null || true
tmux kill-window -t "${SESSION}:${WINDOW_APP}" 2>/dev/null || true

PANE_DB=$(tmux new-window -t "$SESSION" -n "$WINDOW_INFRA" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_CACHE=$(tmux split-window -t "$PANE_DB" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')

PANE_API=$(tmux new-window -t "$SESSION" -n "$WINDOW_APP" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_WEB=$(tmux split-window -t "$PANE_API" -h -c "${PROJECT_DIR}/frontend" -P -F '#{pane_id}')
```

Three-window pattern:

```bash
WINDOW_INFRA="myapp-infra"
WINDOW_APP="myapp-app"
WINDOW_FRONTEND="myapp-frontend"

tmux kill-window -t "${SESSION}:${WINDOW_INFRA}" 2>/dev/null || true
tmux kill-window -t "${SESSION}:${WINDOW_APP}" 2>/dev/null || true
tmux kill-window -t "${SESSION}:${WINDOW_FRONTEND}" 2>/dev/null || true

PANE_DB=$(tmux new-window -t "$SESSION" -n "$WINDOW_INFRA" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_CACHE=$(tmux split-window -t "$PANE_DB" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')

PANE_API=$(tmux new-window -t "$SESSION" -n "$WINDOW_APP" -c "$PROJECT_DIR" -P -F '#{pane_id}')
PANE_WORKER=$(tmux split-window -t "$PANE_API" -h -c "$PROJECT_DIR" -P -F '#{pane_id}')

PANE_WEB=$(tmux new-window -t "$SESSION" -n "$WINDOW_FRONTEND" -c "${PROJECT_DIR}/frontend" -P -F '#{pane_id}')
PANE_STORYBOOK=$(tmux split-window -t "$PANE_WEB" -h -c "${PROJECT_DIR}/frontend" -P -F '#{pane_id}')
```

## Logging Pattern

```bash
pipe_pane_to_log() {
  local pane_id="$1"
  local log_file="$2"

  tmux pipe-pane -o -t "$pane_id" \
    "perl -pe 'BEGIN { \$| = 1 } s/\\e\\[[0-?]*[ -\\/]*[@-~]//g; s/\\e\\][^\\a]*(?:\\a|\\e\\\\)//g; s/\\r//g; s/[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]//g' >> '${log_file}'"
}
```

## Prefix-Coherency Checklist

Only apply this when remote access introduces a path prefix such as `/app`.

Confirm all of the following:

1. Frontend dev server base path matches the prefix.
2. Frontend router adds and strips the prefix correctly.
3. API clients generate prefixed URLs rather than assuming root-only paths.
4. Readiness checks use prefixed URLs when they go through the proxy.
5. Dev proxy rewrites strip the prefix before forwarding upstream.
6. PWA `scope`, `start_url`, and asset paths are updated if applicable.

Anti-pattern: `tailscale serve --set-path /app ...` plus an otherwise root-only app.

## Validation Commands

```bash
INSTALLED_SKILL_DIR="${HOME}/.codex/skills/dev-bootstrap-application-script" # adjust client dir if needed
bash -n ./dev.sh
python3 "${INSTALLED_SKILL_DIR}/scripts/validate_dev_bootstrap.py" ./dev.sh
```

Optional checks:

```bash
python3 "${INSTALLED_SKILL_DIR}/scripts/validate_dev_bootstrap.py" --expect-multi-window ./dev.sh
python3 "${INSTALLED_SKILL_DIR}/scripts/validate_dev_bootstrap.py" --expect-tailscale ./dev.sh
```
