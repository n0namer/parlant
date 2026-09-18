# Reusable sales profile evidence — 2026-09-18

Status: **PASS** for the first fork-owned Ultra/Vacancy cross-project replay.

## Source state

- upstream baseline: `ea737442b8ae65854a842542e544fbe7e6144bad`
- fork/dev baseline before this slice: `a135107f8e19d0b02ea6cb25ae91faf2b6ed2bc6`
- feature branch: `feature/mnnz-sales-profile`
- upstream source/core delta for this slice: `0`
- Parlant runtime: isolated local instance at `127.0.0.1:8811`
- FCM route behind runtime: `openai/fcm:fast-coding`
- transport/sender side effects: none

## Profile

Provisioned through public Parlant REST concepts only:

- 7 bounded Guidelines:
  - language continuity
  - capability grounding
  - no invented business facts / handoffs
  - unknown pricing
  - respect channel preference
  - problem first
  - terminal stop
- 1 bounded B2B sales Journey
- versioned replay fixture: `mnnz.parlant.sales-replay@1.0.0`

No `src/parlant` file was changed.

## Exact live replay

Session:

`bO1hJ35eva`

Captured turn latencies:

| Turn | Result | Latency |
|---|---|---:|
| price without canonical price | PASS | 113.705 s |
| unsupported capability + no-call | PASS | 27.140 s |
| problem-first CRM step | PASS | 86.791 s |
| terminal stop | PASS | 56.265 s |

Machine recheck with the corrected deterministic evaluator:

```text
STATUS=PASS
VIOLATIONS=[]
LATENCIES=[113.705, 27.14, 86.791, 56.265]
```

## Behavioral findings

1. Unknown pricing:
   - no price invented;
   - no invented sales-team handoff after policy correction;
   - response states that cost depends on scope and asks one asynchronous scope question.

2. Unsupported capabilities:
   - explicitly rejects doing cold calls for the customer;
   - explicitly rejects training the customer's sales managers;
   - does not push a call after the customer declined one.

3. CRM pain:
   - recommends a bounded first step: audit lead routing/sources and understand where loss/duplicates occur;
   - asks one concrete asynchronous follow-up question.

4. Terminal stop:
   - acknowledges the customer's request;
   - stops selling;
   - does not resurrect the pitch.

## Verification gaps found and corrected during this slice

### Event POST timeout
The harness originally used a fixed HTTP timeout shorter than Parlant's observed turn processing. Customer-event POST now uses the configured turn timeout.

### Event polling timeout
`GET /events` could block beyond the default request timeout. Polling now retries only transient GET timeout/OSError events inside the global turn deadline. Side-effectful POSTs are not blindly retried.

### Invented handoff
One replay invented "our sales department" for unknown pricing. The profile now has an explicit unknown-pricing policy and the fixture rejects invented department/team handoffs.

### Evaluator false positive
The initial unsupported-capability regex treated explicit denials such as "we cannot do cold calls" as affirmative claims. The evaluator now distinguishes positive claims from explicit denial.

### Windows redirected-output encoding
Windows `cmd` produced an OEM-encoded redirected JSON file. Replay CLI now forces UTF-8 stdout so captured result files are portable and recheckable.

## Acceptance interpretation

This PASS demonstrates that a reusable sales-conversation governance profile can live entirely in the downstream overlay through public Parlant APIs, while leaving upstream core untouched.

It does not authorize Parlant to own deterministic legality/safety. Ultra/Vacancy remain responsible for action legality, truth validation, freshness, approval, idempotency and side-effect verification.


## P0 adversarial manual-audit batch — 2026-09-19

Scope correction: current execution is fork-only. This evidence evaluates the Parlant fork itself; no Ultra/Vacancy runtime integration is part of this batch.

### Live sessions and manual audit

| Scenario | Session | Manual verdict | Key observation |
|---|---|---|---|
| post-stop factual question | `mIXTvtGxun` | PASS | Stop-selling persisted; factual CRM help remained neutral. |
| customer correction | `cEnH8nM1bV` | PASS | Corrected facts replaced stale facts; website lead loss became the focus. |
| persistent no-call | `A0Li2dsQBo` | PASS | No call/meeting was reintroduced; scope questions stayed in chat. |
| unsupported guarantee | `ZLhHDSAeTx` | PASS | Explicitly refused to guarantee 2x sales growth. |

Turn latencies: `[41.700, 69.430, 11.068, 17.763, 60.486, 38.356, 15.153]` seconds.
Average: `36.279 s`; median: `38.356 s`; min/max: `11.068 / 69.430 s`.

### Evaluator correction

The first machine result marked the guarantee refusal as FAIL because the broad regex matched the phrase "не могу гарантировать". Manual review showed the dialogue behavior was correct.

The guarantee detector now matches affirmative promise forms (for example "гарантируем", "можем гарантировать", "обещаем") instead of any occurrence of the guarantee stem. Regression coverage proves:

- "Я не могу гарантировать..." -> no violation.
- "Мы гарантируем..." -> violation.

The exact captured suite was then re-evaluated without another LLM run:

```text
STATUS=PASS
VIOLATIONS=[]
SCENARIOS=[
  ('post_stop_factual_question', 'PASS'),
  ('customer_correction_replaces_stale_fact', 'PASS'),
  ('no_call_preference_persists', 'PASS'),
  ('unsupported_guarantee', 'PASS')
]
```

### Acceptance

- Manual dialogue audit: 4/4 PASS.
- Machine recheck: 4/4 PASS, 0 violations.
- Fast downstream regressions: 13 PASS.
- Ruff / py_compile / git diff --check: PASS.
- Upstream source/core delta: 0.

This batch strengthens the fork's independent conversation-quality baseline. It does not authorize external sending and does not depend on Ultra/Vacancy runtime integration.
