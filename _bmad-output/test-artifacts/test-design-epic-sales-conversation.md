---
workflowStatus: 'completed'
mode: 'epic-level'
epicId: 'sales-conversation'
date: '2026-09-19'
---

# Test Design: Sales Conversation Layer

**Target:** `n0namer/parlant` downstream fork`r`n**Acceptance source:** `PLAN.md` Current DoD + `AGENTS.md` / `UPSTREAM.md` invariants`r`n**Scope:** `mnnz/sales` only; no Ultra/Vacancy integration work in this phase.

## Executive Summary

The current 4-turn replay proves the basic bounded-sales path but is too narrow to establish conversational quality. The next gate is a manually audited adversarial dialogue suite, with deterministic checks for hard failures and transcript review for quality/context behavior.

High risks:
- R-001 hallucinated business facts/capabilities — BUS, 3×3=9.
- R-002 no-call / terminal-stop violation — BUS, 2×3=6.
- R-003 context loss / contradiction across turns — DATA, 2×3=6.
- R-004 evaluator false positive/negative — TECH, 3×2=6.
- R-005 excessive response latency — PERF, 3×2=6.

## Not in Scope

| Item | Reason | Mitigation |
|---|---|---|
| Ultra/Vacancy adapters | User explicitly froze integration work | Keep the fixture format reusable; do not wire projects now |
| AI-customer simulator | User asked to manually inspect dialogues first | Fixed scenarios now; simulation later |
| Production sender/actions | Conversation quality is not yet accepted | Keep all external side effects disabled |
| Upstream core modifications | Thin-fork policy | Use `mnnz/` overlay and public Parlant APIs |

## Risk Assessment

| ID | Category | Risk | P | I | Score | Mitigation |
|---|---|---|---:|---:|---:|---|
| R-001 | BUS | Invented price, capability, team, proof, integration, timeline or guarantee | 3 | 3 | 9 | P0 forbidden-claim checks + manual transcript audit |
| R-002 | BUS | Ignores no-call/stop or resurrects sale | 2 | 3 | 6 | P0 persistent-preference and post-stop scenarios |
| R-003 | DATA | Forgets correction/history or contradicts prior answer | 2 | 3 | 6 | Multi-turn correction/context scenarios |
| R-004 | TECH | Evaluator misclassifies safe/unsafe answer | 3 | 2 | 6 | Unit regressions + manual review of every new live transcript |
| R-005 | PERF | Latency makes interaction impractical | 3 | 2 | 6 | Record per-turn latency; threshold UNKNOWN until product target exists |
| R-006 | BUS | CRM example overfits generic sales profile | 2 | 2 | 4 | Independent starts, varied objections and ambiguity |
| R-007 | OPS | Shared runtime/session contamination | 2 | 2 | 4 | Unique sessions/home and exact evidence identifiers |
| R-008 | TECH | Fork drifts into upstream core | 1 | 2 | 2 | Source Loop + core-delta=0 gate |

## NFR Planning

- **Performance:** record every live turn latency. Acceptable target is **UNKNOWN**; do not invent one.
- **Reliability:** transient GET polling may retry within a global deadline; side-effectful POSTs must not be blindly retried.
- **Maintainability:** downstream sales behavior stays in `mnnz/`; target upstream-core delta = 0.
- **Security/compliance:** external business transport remains disabled in this phase.

## Coverage Plan

P0/P1 below are **risk priority**, not execution timing.

| ID | Scenario | Level | Priority | Risk |
|---|---|---|---|---|
| DLG-P0-01 | Unknown price without invented handoff | Live API | P0 | R-001 |
| DLG-P0-02 | Unsupported cold calls/training + no-call | Live API | P0 | R-001/R-002 |
| DLG-P0-03 | CRM first step without invented timeline | Live API | P0 | R-001 |
| DLG-P0-04 | Terminal stop | Live API | P0 | R-002 |
| DLG-P0-05 | Post-stop factual question without renewed pitch | Live API | P0 | R-002/R-003 |
| DLG-P0-06 | Customer corrects prior fact | Live API | P0 | R-003 |
| DLG-P0-07 | Repeated no-call preference persists | Live API | P0 | R-002/R-003 |
| DLG-P0-08 | Unsupported guarantee/outcome request | Live API | P0 | R-001 |
| DLG-P1-01 | “Too expensive” with no canonical price | Live API | P1 | R-001 |
| DLG-P1-02 | Competitor comparison without proof | Live API | P1 | R-001 |
| DLG-P1-03 | Ambiguous automation request | Live API | P1 | R-006 |
| DLG-P1-04 | Russian→English language switch | Live API | P1 | R-006 |
| DLG-P1-05 | Unsupported named integration | Live API | P1 | R-001 |
| DLG-P1-06 | Mixed seller/buyer language | Live/manual | P1 | R-006 |
| EVAL-U-01 | Explicit denial ≠ affirmative claim | Unit | P0 | R-004 |
| EVAL-U-02 | Price/team/timeline patterns caught | Unit | P0 | R-004 |
| REL-U-01 | Transient poll timeout retry | Unit | P1 | R-007 |

## Execution Strategy

- Fast local gate: Ruff, py_compile, downstream unit tests, fixture/schema checks.
- Live manual gate: selected P0/P1 conversations against isolated Parlant+FCM; each transcript manually reviewed.
- Expensive later gate: repeated stochastic/persona simulation; deferred.
- Run all cheap functional tests locally; defer only long live dialogue batches.

## Resource Estimate

- P0 fixed-dialogue expansion/regressions: ~3–6 focused hours.
- P1 fixed dialogue/manual audit: ~2–5 focused hours.
- AI-customer simulation: deferred, outside this gate.

## Quality Gate

- P0: 100%.
- P1: ≥95% once the sample is large enough; in the current small suite, any material semantic failure blocks acceptance until reviewed.
- Zero invented canonical business facts in accepted P0 transcripts.
- Machine PASS alone is insufficient: every newly added live dialogue gets manual transcript review.
- Upstream core delta: 0 target.
- External sender/side effects: 0.

## Entry Criteria

- Isolated Parlant runtime available.
- FCM route available.
- Canonical offer/capability truth supplied by fixture.
- Working tree/baseline recorded.

## Exit Criteria

- P0 fixed suite implemented and 100% machine-green.
- Manual audit finds no unresolved high-risk semantic failure.
- Every discovered failure becomes a deterministic regression where feasible.
- `PLAN.md` updated with exact sessions, findings, latency and next gate.
- `git diff --check`, Ruff, compile and downstream tests green.

## Interworking & Regression

| Component | Impact | Regression |
|---|---|---|
| `mnnz/sales/profile.py` | Conversation policy | profile tests + live suite |
| `mnnz/sales/replay.py` | Live evaluation transport | timeout/recheck tests |
| fixture suite | Acceptance cases | schema/evaluator tests |
| upstream Parlant | Runtime dependency | no upstream source change; smoke/replay only |
