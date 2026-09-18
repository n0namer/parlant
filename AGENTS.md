# MNNZ Parlant Fork — Agent Operating Contract

This repository is **not a standalone rewrite of Parlant**. It is the maintained MNNZ fork of `emcie-co/parlant`.

Read this file before changing anything. Then read `UPSTREAM.md`, `PATCHES.md`, and `PLAN.md`.

## Repository identity

- Upstream: `https://github.com/emcie-co/parlant`
- Maintained fork: `https://github.com/n0namer/parlant`
- Upstream accepted branch: `upstream/develop`
- Fork mirror branch: `main`
- Fork integration branch: `dev`
- Fork `develop`: intentionally does not exist; never recreate it as an MNNZ work branch
- Feature branches: short-lived `feature/*`, based on `dev`
- Upgrade branches: short-lived `upgrade/<upstream-sha-or-date>`
- Current accepted upstream baseline at bootstrap: `ea737442b8ae65854a842542e544fbe7e6144bad`

## Branch authority — non-negotiable

```
emcie-co/parlant:develop
        |
        v
n0namer/parlant:main      # clean/near-exact upstream mirror
        |
        v
n0namer/parlant:dev       # our durable integration branch
        |
        +--> feature/*    # bounded local work
        +--> upgrade/*    # bounded upstream-convergence candidates
```

1. **Never develop product features on `main`.**
2. **Never push to upstream.** Local `upstream` push URL is intentionally disabled.
3. Durable MNNZ work lands in `fork/dev`, not only in a runtime/container.
4. Prefer external adapters/extensions/overlay modules over edits to `src/parlant/core`.
5. Any unavoidable upstream-core edit must be registered in `PATCHES.md` before it is considered accepted.
6. A clean textual rebase/merge is not proof of semantic correctness.

## Source Loop Profile U rules

This fork follows the Source Loop upstream-managed-fork model.

Before every upstream update, resolve exact immutable refs:

- `last_accepted_upstream_sha`
- `current_upstream_sha`
- `fork_main_sha`
- `fork_dev_sha`

If the accepted upstream baseline cannot be proven, stop with `BASELINE_UNKNOWN`; do not auto-rebase or promote.

Every owned local patch must be classified against the new upstream exactly once:

- `UPSTREAM_FIXED` — do not replay; prove upstream satisfies the acceptance test.
- `LOCAL_PATCH_STILL_REQUIRED` — replay unchanged and rerun acceptance.
- `LOCAL_PATCH_NEEDS_REBASE` — adapt to moved APIs/contracts and rerun acceptance.
- `SEMANTIC_CONFLICT` — stop automatic promotion; explicit design review required.
- `PATCH_OBSOLETE` — remove deliberately and record why.

## Update / rebase procedure

Do **not** rebase shared `dev` blindly.

1. Ensure working tree is clean or preserve the active local slice first.
2. `git fetch upstream --prune`
3. Record exact SHAs in the upgrade evidence.
4. Advance local/fork `main` to the exact accepted upstream `develop` candidate only in the bounded upgrade flow.
5. Create fresh `upgrade/<date-or-sha>` from the new `main`.
6. Replay/rebase only the still-required, intentionally small MNNZ overlay from `dev`.
7. Produce semantic-overlap classification for every entry in `PATCHES.md`.
8. Run upstream-native tests plus MNNZ compatibility/replay/safety tests.
9. If upstream or accepted fork refs moved while testing, candidate is stale: discard/recreate it.
10. Merge/promote the exact tested candidate into `dev`.
11. Only after acceptance, update `last_accepted_upstream_sha` in `UPSTREAM.md`.
12. Rebuild/reconcile runtime from the exact accepted fork SHA and verify provenance + behavior.

Feature branches may be rebased onto current `dev`; shared `dev` history should not be destructively rewritten as routine maintenance.

## Fork Delta Budget

Target:
- upstream-core files modified by MNNZ: **0**
- soft alarm: **>5 upstream-core files**
- track LOC delta on every upstream sync

When a generic capability is missing, prefer:
1. public config/API,
2. adapter/port implementation,
3. external extension/package,
4. wrapper/composition,
5. generic upstreamable extension point,
6. upstream-core patch only as last resort.

## Parlant role in the wider sales architecture

Parlant is the conversation-governance/planning layer. It is **not** the deterministic safety authority.

Ultra/Vacancy deterministic code continues to own:
- legal action envelope,
- terminal / do-not-contact legality,
- offer/capability truth validation,
- aggregate/revision freshness,
- exact-payload approval/hash,
- duplicate prevention/fencing,
- side-effect authorization,
- post-effect verification.

Do not move those controls into LLM-mediated Guidelines/Journeys as their only enforcement.

## Working style

- Brownfield first: inspect existing ports/adapters and tests before designing new abstractions.
- Container Coding First for product/source code when a project container exists.
- Work in bounded DoD batches; keep `PLAN.md` current.
- No deploy/redeploy/PR/CI churn while a local working-state batch is still red.
- Runtime success, HTTP 200, a clean merge, or a created branch is not enough evidence by itself.
- Every accepted change must have exact-SHA evidence and regression coverage appropriate to its risk.

Upstream's original coding guidance remains in `CLAUDE.md`; this file adds fork-maintenance constraints and takes precedence for branch/source-ownership questions.
