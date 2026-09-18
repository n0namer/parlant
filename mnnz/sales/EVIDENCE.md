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
