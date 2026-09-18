# MNNZ Parlant fork instructions

Before changing this repository, read:
1. `/AGENTS.md`
2. `/UPSTREAM.md`
3. `/PATCHES.md`
4. `/PLAN.md`

Critical rules:
- `main` is the upstream mirror; do not put MNNZ product changes there.
- durable local work belongs on `dev` or a short `feature/*` branch from `dev`.
- upstream push is forbidden.
- prefer ports/adapters/extensions over editing upstream core.
- every unavoidable upstream-core patch must be registered in `PATCHES.md`.
- upstream upgrades use a fresh `upgrade/*` candidate and exact-SHA Source Loop Profile U acceptance.
- a conflict-free merge/rebase is not semantic proof.
- do not move deterministic sales legality/safety exclusively into Parlant Guidelines/Journeys.
