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

- GitHub fork created and default branch set to `main`.
- local `main`, `dev`, `upstream/develop`, `fork/main`, and `fork/dev` were aligned at bootstrap SHA `ea737442b8ae65854a842542e544fbe7e6144bad`.
- upstream push disabled locally.
- inherited `fork/develop` removed to prevent confusion with MNNZ `dev`; only `upstream/develop` is tracked as the upstream development source.
- governance docs being installed before product customization begins.
- upstream-core patch inventory is empty.

## Next DoD

1. Land this fork-governance documentation on `fork/dev`.
2. Add the MNNZ extension/adapter subtree without modifying upstream core unless an extension-point gap is proven.
3. Move/recreate Parlant-specific FCM compatibility configuration/tests from the external spike into the fork-owned extension/test area.
4. Add an automated fork-status/semantic-overlap report script.
5. Run upstream-native checks for touched areas.
6. Keep `main` unchanged except during an explicit upstream-sync operation.
