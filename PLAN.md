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
- `scripts/mnnz_fork_status.py` reports exact upstream/fork SHAs, working-tree overlay, upstream-source delta and core-delta alarm.
- upstream-core patch inventory remains empty.

## Current DoD

1. Keep upstream-core delta at zero for the first FCM integration slice.
2. Prove the fork-owned FCM profile against a live Parlant runtime.
3. Prove the anti-drift report sees both committed and uncommitted overlay files.
4. Run lightweight downstream tests, Python compile, PowerShell parse, Ruff, fork-status and `git diff --check`.
5. Merge the exact green feature commit into `dev` and push only the fork.
6. Keep `main` unchanged.

## Next DoD

1. Add the first MNNZ sales/conversation extension module using public Parlant SDK/ports only.
2. Encode reusable sales Guidelines/Journeys as fork-owned overlay code/data, not modifications to upstream core.
3. Add one compatibility replay that can be run both from this fork and from Ultra's `ParlantSalesPlanner`.
4. Add a semantic-overlap section to the fork-status report for any future `PATCHES.md` entries.
5. Only create an upstream-core patch if a concrete missing extension point is demonstrated.
