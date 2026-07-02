---
name: interaction-speed
description: >
  Use when a user surface feels sluggish, when designing the responsiveness of
  a new interaction, or when reviewing perceived performance — latency budgets,
  preloading and caching strategy, optimistic rendering, loading states, and
  double-click/double-submit hazards.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-07-03"
---

# Interaction Speed

Perceived performance as a design property. The bar: **snappy** — the UI moves
as fast as the user's thought, acknowledges every input instantly, and does its
slow work where the user can't feel it.

## Use This Skill When

- A flow feels sluggish, or users report clicking things twice
- Designing the responsiveness of a new interaction: what happens in the first
  100ms, what's optimistic, what's preloaded
- Reviewing loading states, spinners, skeletons, and cache strategy
- Deciding whether an operation runs synchronously in the UI or in background

Example trigger phrasings: "make this feel faster", "why does this feel
sluggish", "users double-click the save button", "should this be optimistic",
"what should we preload".

## Do Not Use This Skill For

- Diagnosing an actual performance regression to root cause —
  `/th-engineering` diagnosis (come back here for how the UI should behave
  while slow)
- Animation duration policy — [visual-language](../visual-language/SKILL.md)

## Reviewable Expectations

### Latency budgets

Measure input → first visible response, not server time:

| Budget | Requirement |
|---|---|
| < 100ms | Feels instant. Target for all local interactions: typing echo, toggles, menu open, palette filtering. No feedback needed beyond the state change itself. |
| 100–300ms | Acknowledge immediately (pressed state, highlight), complete without progress UI. |
| 300ms–1s | Show lightweight progress (inline skeleton/shimmer), keep the rest of the UI live. |
| > 1s | Run async: UI stays fully usable, progress is visible, completion is announced where the user is now — not where they were. |

A hot-path interaction over budget is a defect regardless of what the backend
costs; move the cost off the interaction.

### Optimism and caching

- **Optimistic rendering by default** for mutations that almost always
  succeed: apply the change locally at once, reconcile in background, and on
  failure roll back *loudly* (restore state + explain), never silently.
- **Preload what the user will probably want next**: warm caches at idle,
  prefetch on hover/focus/route-likelihood, precompute the expensive view
  before it's opened.
- **Stale-while-revalidate**: render last-known data immediately, refresh in
  place. A blank screen that could have shown yesterday's data is a defect.
- Cache invalidation states its rule (event, TTL, version) — "we'll refetch
  every time to be safe" is a latency defect wearing a correctness costume.

### Input integrity

- Input is never blocked: typing, scrolling, and clicking stay live during
  background work. A frozen frame is worse than a slow result.
- **Repeat-safe controls**: the first activation disables, debounces, or
  dedupes; a double-click must never double-submit, double-charge, or
  double-navigate. And treat the double-click itself as a finding — the user
  clicked twice because feedback was late. Fix both.
- Layout never shifts under a pending click: content that pops in must not
  move the button the user is aiming at.

### Waiting UI

- Skeletons over spinners: show the shape of what's coming in place. Global
  spinners/overlays are a last resort.
- Progress is honest: no fake bars; if duration is unknown, say what's
  happening.
- Never make the user re-request: if it failed, offer retry with the input
  preserved.

## Review Method

1. Walk the hot paths with the design-bar walkthrough's **Pace** and
   **Repetition** questions ([design-bar](../design-bar/SKILL.md)); time
   input → visible response where measurable.
2. For each interaction over budget: classify the fix — acknowledge sooner,
   render optimistically, preload earlier, or move work async.
3. Grep mutation handlers for missing pending/disabled states and
   non-idempotent submits; cite file:line.
