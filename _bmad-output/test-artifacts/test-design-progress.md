---
workflowStatus: 'completed'
totalSteps: 5
stepsCompleted: ['step-01-detect-mode', 'step-02-load-context', 'step-03-risk-and-testability', 'step-04-coverage-plan', 'step-05-generate-output']
lastStep: 'step-05-generate-output'
nextStep: ''
lastSaved: '2026-09-19T01:24:00+03:00'
inputDocuments: ['PLAN.md','AGENTS.md','UPSTREAM.md','PATCHES.md','mnnz/sales/profile.py','mnnz/sales/replay.py','mnnz/sales/fixtures/ultra_vacancy_baseline.json','tests/mnnz/test_mnnz_sales_profile.py','pyproject.toml']
---

# BMad Test Design Progress — MNNZ Parlant Sales Conversation Layer

## Step 01 — Mode and prerequisites

- Mode: Epic-Level.
- Target: `n0namer/parlant`, local `D:\Users\NIKITA\Documents\DEV\parlant-mnnz`.
- Active slice: reusable sales/conversation profile under `mnnz/sales`.
- Acceptance source: existing `PLAN.md` Current DoD + current live evidence.
- Architecture context: `AGENTS.md`, `UPSTREAM.md`, `PATCHES.md`.
- User correction: work only on the forked Parlant until it is independently good; no further Ultra integration work in this phase.
- Test objective: deepen dialogue-quality validation with fixed adversarial conversations manually audited by the agent before any AI-customer simulator is introduced.

## Step 02 — Loaded context and coverage

- Stack: backend Python package; pytest/pytest-asyncio/pytest-bdd available; Ruff available.
- Relevant existing layers: upstream API/core/e2e tests plus downstream `tests/mnnz` overlay tests.
- Existing downstream live coverage: one 4-turn sales replay with pricing, unsupported capability/no-call, CRM first-step and terminal-stop cases.
- Existing hard checks: forbidden regex, profile/guideline structure, timeout/retry behavior, recheck semantics.
- Coverage gap: dialogue quality is under-sampled; one conversation does not exercise independent starts, ambiguity, negotiation pressure, changing intent, repeated objections, fact traps, user correction, mixed buyer/seller signals or recovery after a bad turn.
- NFR concern: observed live response latency is material and must stay visible, but current batch prioritizes correctness/quality before optimization.
- BMad risk discipline: probability × impact; score >=6 requires mitigation, score 9 blocks acceptance. P0/P1 coverage should be deterministic where possible; subjective quality can be manually audited by the agent for now.

## Step 03 — Risk assessment

| Risk | Category | P | I | Score | Mitigation / evidence |
|---|---|---:|---:|---:|---|
| Agent invents unsupported capabilities, prices, teams, proof or timelines | BUS | 3 | 3 | 9 | P0 deterministic forbidden-claim checks + adversarial live dialogues + manual transcript audit. |
| Agent ignores no-call / terminal stop or resurrects the sale | BUS | 2 | 3 | 6 | P0 multi-turn cases with persistent preference/terminal state and explicit post-stop turns. |
| Agent loses prior-turn context or contradicts its own earlier answer | DATA | 2 | 3 | 6 | P0/P1 multi-turn scenarios with state changes, corrections and repeated objections; inspect full transcripts. |
| Evaluator reports false positives/negatives and hides real model quality | TECH | 3 | 2 | 6 | Freeze evaluator regression examples; manually audit every new dialogue in this phase; never accept machine PASS alone. |
| Response latency makes the conversation impractical | PERF | 3 | 2 | 6 | Record per-turn latency and distribution. Threshold remains UNKNOWN until a product target is set; optimize only after correctness baseline. |
| Generic sales profile overfits the current CRM example | BUS | 2 | 2 | 4 | Add independent conversation starts and diverse objections without changing canonical offer truth. |
| Runtime/session collisions contaminate evidence | OPS | 2 | 2 | 4 | Unique PARLANT_HOME/session identity; bind evidence to exact branch/SHA/session. |
| Downstream fork drifts into upstream core | TECH | 1 | 2 | 2 | Keep core delta=0 target; Source Loop / PATCHES gate remains active. |

### NFR planning

- Performance: measurable evidence exists (per-turn latency); acceptable target is UNKNOWN and must not be invented.
- Reliability: require deterministic replay tooling to survive transient GET polling timeouts; side-effectful POSTs are not blindly retried.
- Maintainability: downstream sales work should remain in `mnnz/`; upstream core delta target remains zero.
- Security/compliance: not a primary scope of this dialogue-quality slice; no external transport or side effects are enabled.

Highest-priority mitigation for this batch: expand fixed adversarial conversations, manually audit complete transcripts, and convert every discovered failure into a deterministic regression where feasible.

## Step 04 — Coverage and execution strategy

### Coverage matrix

| ID | Scenario | Level | Priority | Primary risk/evidence |
|---|---|---|---|---|
| DLG-P0-01 | Unknown price: no invented number/team handoff | Live API replay | P0 | BUS-9; transcript + deterministic regex |
| DLG-P0-02 | Unsupported cold calls/training + no-call preference | Live API replay | P0 | BUS-9/BUS-6; transcript + regex |
| DLG-P0-03 | Concrete CRM pain: useful first step without invented timeline | Live API replay | P0 | BUS-9; transcript + timeline regex |
| DLG-P0-04 | Terminal stop: no sale resurrection | Live API replay | P0 | BUS-6; terminal transcript |
| DLG-P0-05 | Terminal stop followed by a new non-sales factual question | Live API replay | P0 | Context/state; must answer question without resuming pitch |
| DLG-P0-06 | Customer corrects a fact stated earlier | Live API replay | P0 | DATA-6; agent must adopt correction and not repeat stale fact |
| DLG-P0-07 | Repeated no-call request after prior sales turn | Live API replay | P0 | BUS-6; channel preference persists |
| DLG-P0-08 | Explicit unsupported guarantee/outcome request | Live API replay | P0 | BUS-9; no guaranteed result invented |
| DLG-P1-01 | “Too expensive” when canonical price is absent | Live API replay | P1 | Avoid fake discount/price; useful scope question |
| DLG-P1-02 | Competitor comparison with no proof points | Live API replay | P1 | No invented superiority/customer proof |
| DLG-P1-03 | Ambiguous automation request | Live API replay | P1 | One focused clarification, no scope invention |
| DLG-P1-04 | Customer switches Russian→English | Live API replay | P1 | Language continuity/switch correctness |
| DLG-P1-05 | Customer asks for unsupported integration by name | Live API replay | P1 | Capability grounding |
| DLG-P1-06 | Mixed seller/buyer language | Manual live audit | P1 | Avoid aggressive pitch when intent is ambiguous |
| EVAL-U-01 | Explicit denial must not trigger affirmative forbidden-claim detector | Unit | P0 | TECH-6 evaluator correctness |
| EVAL-U-02 | Invented timeline, team handoff, price patterns are caught | Unit | P0 | TECH-6 evaluator correctness |
| REL-U-01 | Poll GET transient timeout retries within global deadline | Unit | P1 | OPS reliability |

### Execution strategy

- Local/PR-equivalent fast gate: Ruff + py_compile + downstream unit regressions + fixture schema checks.
- Manual batch gate: selected P0/P1 live dialogues against isolated Parlant+FCM; every transcript manually audited by the agent in this phase.
- Expensive/nightly-later: broad persona simulation and repeated stochastic runs; explicitly deferred by user.
- Performance evidence: record every live turn latency; no invented pass threshold until product target exists.

### Quality gates

- P0 pass rate: 100%.
- P1 pass rate: >=95% once enough cases/runs exist; for the current small fixed suite any material semantic failure blocks acceptance until reviewed.
- Zero invented canonical business facts in accepted P0 transcripts.
- Machine PASS alone is insufficient in this phase: each newly added live dialogue must receive manual transcript review.
- Upstream core delta target: 0.
- Sender/external business side effects: 0.

### Effort bands

- P0 fixed-dialogue expansion + regressions: ~3–6 focused hours.
- P1 fixed dialogues/manual audit: ~2–5 focused hours.
- Later AI-customer simulation: deferred; not part of current gate.


## Step 05 — Completion

- Execution mode: sequential.
- Final artifact: _bmad-output/test-artifacts/test-design-epic-sales-conversation.md.
- Checklist review: risk IDs/scoring, coverage priorities, NFR unknowns, execution strategy, interval estimates and quality gates are present. Formal PRD/epic files are absent by design; current PLAN.md DoD is the accepted slice requirement source.
- Next implementation gate: implement and manually audit the P0 adversarial dialogue suite in mnnz/sales.
