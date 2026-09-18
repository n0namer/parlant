# MNNZ Parlant Fork — Execution Plan

Updated: 2026-09-18
Status: ACTIVE SOURCE OF TRUTH for fork maintenance.

## North Star

Maintain a thin, updateable Parlant fork where upstream stays easy to absorb and MNNZ sales/conversation customizations remain isolated behind ports/adapters or external overlay code.

## Current topology

- upstream: `emcie-co/parlant:develop`
- fork: `n0namer/parlant`
- fork mirror: `main`
- fork integration: `dev`
- local checkout: `D:\Users\NIKITA\Documents\DEV\parlant-mnnz`
- bootstrap baseline: `ea737442b8ae65854a842542e544fbe7e6144bad`
- local upstream push: disabled

## Adopted invariants

- `main` stays near-exact upstream mirror.
- all durable MNNZ work lands in `dev`.
- no product development directly on `main`.
- upstream-core patch budget target = 0.
- every unavoidable upstream-core patch is inventoried in `PATCHES.md`.
- upstream transitions follow `UPSTREAM.md` / Source Loop Profile U.
- clean textual merge/rebase is not semantic acceptance.
- Parlant conversation governance never replaces external deterministic legality/safety controls.

## Current checkpoint

- GitHub fork exists and default branch is `main`.
- `main` remains the clean upstream mirror at `ea737442b8ae65854a842542e544fbe7e6144bad`.
- fork-governance contract is durable on `dev` at `10d5233f0707268282b27846e4298731b1e8cdf6`.
- upstream push is disabled locally.
- inherited `fork/develop` was removed; only `upstream/develop` is the external development source.
- MNNZ overlay now exists under `mnnz/`; no `src/parlant` file is modified by the FCM slice.
- `mnnz/fcm` contains reproducible bootstrap/run/smoke tooling for the canonical `fcm:fast-coding` route.
- live fork-owned FCM smoke is PASS; evidence is in `mnnz/fcm/EVIDENCE.md`.
- accepted FCM overlay implementation commit: `d5a939c0b1615a6049643c774215f370c18acbcb`.
- `scripts/mnnz_fork_status.py` reports exact upstream/fork SHAs, working-tree overlay, upstream-source delta and core-delta alarm.
- upstream-core patch inventory remains empty.

## Current DoD — reusable sales profile

1. Keep upstream-core delta at zero.
2. Maintain the reusable sales profile under `mnnz/sales` using public Parlant REST/SDK concepts only.
3. Provision bounded Guidelines + Journey from canonical offer truth and run the versioned `ultra_vacancy_baseline.json` replay in one session.
4. Deterministically reject invented pricing, invented departments/handoffs, unsupported capabilities, renewed call pressure and terminal-sale resurrection.
5. Make the replay resilient to slow Parlant event POSTs and transient `GET /events` poll timeouts without retrying side-effectful POSTs blindly.
6. Record matched Guidelines/Journey and per-turn latency.
7. Require Ruff + compile + downstream unit regressions + fork-status + `git diff --check` + full live replay PASS before merge.
8. Merge the exact green feature commit into `dev` with ff-only and push only the fork; keep `main` unchanged.

## Current live evidence / corrections

- Seven sales Guidelines + one Journey provision successfully through public APIs; no `src/parlant` modification is required.
- Accepted live session: `bO1hJ35eva`.
- Exact captured turn latencies: `113.705 / 27.140 / 86.791 / 56.265 s`.
- Strengthened unknown-pricing behavior is GREEN: no invented price, no invented sales-team handoff, one asynchronous scope question.
- Unsupported cold-call/training request is GREEN and explicit denial is no longer misclassified as an affirmative capability claim.
- CRM problem-first turn is GREEN: bounded audit/routing first step plus one focused async question.
- Terminal-stop turn is GREEN: sale stops without resurrection.
- Exact captured replay rechecked with the corrected deterministic evaluator: `PASS`, `0 violations`.
- Durable evidence: `mnnz/sales/EVIDENCE.md`.
- Accepted sales-profile implementation commit: `5c707cabcd5381be217e50e9df4ea8c66cac7520`.
- Replay harness corrections now cover slow event POST, transient blocking event GET polling, evaluator claim-vs-denial semantics, invented handoff detection, and UTF-8 redirected output on Windows.
- Upstream source/core delta remains `0`.

## Next DoD

1. Run final Ruff + compile + downstream unit regressions + fork-status + `git diff --check` on the exact feature tree.
2. DCO-commit the green sales-profile slice, ff-only merge into `dev`, push only the fork, and keep `main` unchanged.
3. Make the same versioned JSON replay fixture consumable by Ultra's `ParlantSalesPlanner` comparison harness.
4. Extend `scripts/mnnz_fork_status.py` with semantic-overlap output once `PATCHES.md` gains a real upstream-owned patch.
5. Only create an upstream-core patch if a concrete missing extension point is demonstrated.
