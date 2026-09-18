# MNNZ overlay

This subtree contains downstream-only integration assets for the maintained `n0namer/parlant` fork.

Rules:
- Prefer this subtree, public Parlant APIs, and existing ports/adapters before editing upstream-owned `src/parlant` code.
- Any required edit under upstream-owned source must be registered in `/PATCHES.md`.
- The deterministic sales safety kernel remains outside Parlant.
- FCM integration is a provider/runtime compatibility concern, not a new Parlant core abstraction.

Current overlay:
- `fcm/` — reproducible FCM bootstrap, launch profile, and live compatibility smoke.
