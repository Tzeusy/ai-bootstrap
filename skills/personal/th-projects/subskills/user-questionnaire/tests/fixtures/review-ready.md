# Owner decision questionnaire

**Evidence snapshot:** repository `ai-bootstrap` at commit `abc1234` on 2026-08-13
**Artifact boundary:** Local review document; no execution authority.

| # | Decision ID | Priority | Decision state | Recommended direction |
|---:|---|---:|---|---|
| 1 | `dec-auth` | P1 | Review-ready | Choose A: retain the single authority. |

### `dec-auth` — choose credential authority

**Decision state:** Review-ready
**Adversarial review:** Passed — reviewer `review-scope-1` on 2026-08-13

#### Decision needed

Choose the sole credential authority.

#### Background and freshness

- **[Observed]** The shared store is authoritative (`spec.md:42`).
- **[Unknown]** Live credential age was not inspected.

#### Options

| Option | Pros | Cons |
|---|---|---|
| A. Shared authority | One writer | Requires migration |
| B. Local authority | Small change | Reintroduces split brain |

#### Recommendation

Choose **A** because it preserves the governing contract.

#### Authorization boundary

The recorded scope is specification work only. This packet releases no
artifact, credential, runtime, restart, or external action.

#### Adversarial review record

- Reviewer: `review-scope-1`
- Scope verdict: Pass — bounded to the authority decision.
- Recommendation verdict: Pass — option A best fits the cited contract.
- Material corrections: Added the explicit no-restart boundary.
- Evidence freshness: repository `abc1234`; no live inspection.

#### Owner decision record

- Status: Pending owner response
- Actor/channel: Pending owner response
- Recorded at: Pending owner response
- Choice: Pending owner response
- Owner edits: None
- Post-answer review: Pending owner response
- Final authorization boundary: Pending owner response
- Canonical destination: Pending owner response
- Routing evidence: Pending owner response

#### Evidence

- `spec.md:42`
