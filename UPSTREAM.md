# Upstream Maintenance — Source Loop Profile U

This file is the canonical operational contract for keeping `n0namer/parlant` converged with `emcie-co/parlant` while preserving a small, reviewable MNNZ overlay.

## 1. Topology and authorities

| Role | Value |
|---|---|
| Upstream repo | `emcie-co/parlant` |
| Upstream tracked branch | `develop` |
| Fork repo | `n0namer/parlant` |
| Fork mirror branch | `main` |
| Fork integration branch | `dev` |
| Fork `develop` branch | intentionally absent; `upstream/develop` is the external source and `dev` is our integration branch |
| Local canonical checkout | `D:\Users\NIKITA\Documents\DEV\parlant-mnnz` |
| Promotion authority | explicit local/GitHub operation against the fork only |
| Upstream push | disabled locally |
| Initial accepted upstream SHA | `ea737442b8ae65854a842542e544fbe7e6144bad` |
| Initial fork/main SHA | `ea737442b8ae65854a842542e544fbe7e6144bad` |
| Initial fork/dev SHA | `ea737442b8ae65854a842542e544fbe7e6144bad` |

Source authority:
- external Parlant source authority = upstream `develop`;
- our durable customization authority = fork `dev`;
- runtime/container state = observed working state, never durable truth by itself.

Canonical SourceLoop lifecycle ownership:
- cross-service architecture/bootstrap contract: `n0namer/server-ops/SOURCELOOP.md`, Profile U;
- machine-readable lifecycle: `n0namer/server-ops/ops/registry.json` objects `parlant-upstream` and `parlant-fork-dev`;
- cross-service lifecycle card: `n0namer/server-ops/services/parlant-fork.md`;
- this repository remains authoritative for fork-local patch inventory (`PATCHES.md`), upgrade procedure (this file), product execution (`PLAN.md`) and acceptance evidence;
- local Windows Parlant instances are test evidence only; no canonical deployed Parlant runtime is currently registered or implied.

## 2. Why this model exists

The fork must remain cheap to update. The MNNZ delta is treated as a bounded overlay, not a divergent product tree.

The key Source Loop rule is:

> A clean Git merge/rebase proves only textual compatibility. It does not prove semantic compatibility.

Therefore every upstream transition is an acceptance process tied to exact SHAs.

## 3. Exact-baseline gate

Before every upstream update, record:

```text
last_accepted_upstream_sha
current_upstream_sha
fork_main_sha
fork_dev_sha
observed_at
```

The accepted baseline must come from durable evidence: this file, accepted upgrade record, ancestry, release/provenance evidence. Never infer it from a version string alone.

If not provable:

```text
BASELINE_UNKNOWN
```

and stop automatic replay/promotion.

## 4. Owned patch inventory

`PATCHES.md` is authoritative for any local delta that changes upstream-owned behavior/files.

Every patch record needs:
- stable patch ID,
- purpose,
- owner,
- paths/symbols,
- acceptance tests,
- introduced-at fork SHA,
- upstream issue/PR if any,
- security/safety implications,
- current classification,
- removal condition.

For each new upstream candidate classify each patch exactly once:

| Classification | Meaning / action |
|---|---|
| `UPSTREAM_FIXED` | Do not replay. Prove upstream now passes our acceptance test. |
| `LOCAL_PATCH_STILL_REQUIRED` | Replay bounded patch unchanged, then rerun tests. |
| `LOCAL_PATCH_NEEDS_REBASE` | Adapt to changed API/contract, then rerun tests. |
| `SEMANTIC_CONFLICT` | Stop. Explicit architecture/design review required. |
| `PATCH_OBSOLETE` | Remove deliberately; record why requirement disappeared. |

## 5. Fresh upgrade candidate

Never keep incrementally trusting an old upgrade branch.

Recommended flow:

```bash
git fetch upstream --prune
git fetch fork --prune

# Record exact SHAs first.
git rev-parse upstream/develop
git rev-parse fork/main
git rev-parse fork/dev

# In a clean, bounded update operation:
git checkout main
git reset --hard upstream/develop
git push fork main --force-with-lease=<previous-fork-main-sha>

git checkout -B upgrade/YYYY-MM-DD-<shortsha> main

# Replay/rebase only the still-required small overlay from dev.
# The exact method depends on the patch inventory; do not blindly rebase all history.
```

Why a fresh candidate:
- if upstream changes again during testing, the old candidate is stale;
- if fork/main/dev moves unexpectedly, assumptions must be re-observed;
- acceptance must bind to one immutable candidate SHA.

## 6. Rebase policy

Use rebase for:
- short-lived `feature/*` branches onto current `dev`;
- bounded `upgrade/*` reconstruction when the local delta is intentionally small and fully inventoried.

Do not routinely destructive-rebase shared `dev`.

For upstream upgrades, the preferred mental model is **replay the owned overlay onto the fresh upstream baseline**, not "make conflicts disappear."

A conflict-free rebase may still be a `SEMANTIC_CONFLICT`.

## 7. Semantic-overlap report

For every owned patch, compare the new upstream to our patch and record:

```text
patch_id
upstream_candidate_sha
textual_overlap: yes/no
semantic_overlap: yes/no/unknown
classification
reason
required_action
acceptance_test
```

`semantic_overlap=unknown` on a material patch blocks automatic promotion.

Check whether upstream:
- changed the same path/symbol,
- changed assumptions our patch consumes,
- implemented equivalent behavior elsewhere,
- invalidated our existing acceptance test,
- made our patch redundant or unsafe.

## 8. Acceptance gates

Before promoting an upgrade candidate into `dev`:

1. changed-path / diff sanity,
2. upstream-native lint/type/test gates for touched areas,
3. MNNZ fork-compatibility suite,
4. FCM/Parlant startup compatibility where relevant,
5. Ultra/Vacancy replay fixtures for sales overlay changes,
6. deterministic safety/adversarial fixtures,
7. persistence/restart checks when storage/runtime contracts changed,
8. latency measurement for conversation-pipeline changes.

Runtime/semantic acceptance must bind to the exact candidate SHA. Source tests alone are not enough.

## 9. Promotion

Only after exact-candidate PASS:

```text
stale-check fork refs
-> promote exact tested candidate to dev
-> record accepted fork SHA
-> update last_accepted_upstream_sha
-> record rollback ref
-> rebuild/reconcile runtime from accepted fork
-> verify provenance + semantics again
```

Never update the accepted upstream baseline merely because a candidate was built or tested.

## 10. Anti-drift / Fork Delta Budget

At every sync record:

```text
previous accepted upstream SHA
new upstream SHA
fork/main SHA
fork/dev SHA
upstream commits traversed
upstream-core files modified by us
upstream-core LOC delta
patch classifications
textual conflicts
semantic conflicts/unknowns
test outcomes
accepted candidate SHA
rollback SHA
```

Budget:
- target upstream-core modified files = `0`;
- `>5` modified upstream-core files = architecture-drift alarm;
- rising core LOC delta requires architecture review.

## 11. Failure / stop conditions

Stop automatic upgrade/promotion when:
- `BASELINE_UNKNOWN`;
- working tree contains unpreserved useful work;
- fork/upstream refs move during validation;
- material patch has `semantic_overlap=unknown`;
- any material patch is `SEMANTIC_CONFLICT`;
- required source or runtime acceptance is red;
- secrets/generated/transient files enter the candidate;
- runtime provenance cannot be tied to the candidate SHA.

## 12. Provenance

This runbook adapts the existing Source Loop Profile U model already used in:
- `n0namer/server-ops/SOURCELOOP.md`
- `n0namer/universal-solver/docs/runbooks/agentfield-dev-debug-test-handoff.md`

Those projects remain references; this file is the authoritative fork-maintenance contract for this repository.
