# MNNZ bounded sales profile

This overlay expresses reusable sales-conversation governance through public Parlant API concepts. It does not modify upstream Parlant core.

## Boundary

Parlant owns conversational governance:
- language continuity,
- supported-capability discipline,
- no invented business facts,
- channel preference,
- problem-first next step,
- terminal stop,
- multi-turn journey guidance.

Parlant does **not** become the deterministic safety authority. Ultra/Vacancy still validate legal actions, offer truth, freshness, approvals, idempotency and effects outside this profile.

## Files

- `profile.py` — reusable Guideline/Journey definitions and agent-description builder.
- `provision.py` — creates a disposable agent/tag/guidelines/journey through the public REST API.
- `fixtures/ultra_vacancy_baseline.json` — cross-project replay contract intended to be shareable with Ultra.
- `replay.py` — provisions the profile, runs the baseline turns in one session, and evaluates deterministic forbidden-pattern constraints.
- `dialogue_suite.py` — runs independent adversarial multi-turn scenarios in fresh sessions and supports exact-result recheck after evaluator changes.
- `fixtures/p0_adversarial_dialogues.json` — P0 manual-audit dialogue suite.

## Run

With an isolated Parlant+FCM runtime already running:

```powershell
python -m mnnz.sales.replay --base-url http://127.0.0.1:8811
```

The replay is evaluation only. It does not send Telegram/email/provider messages.

## Recheck an exact captured replay without another LLM run

If only evaluator rules changed, re-evaluate the exact captured messages instead of spending another slow Parlant/FCM run:

```powershell
python -m mnnz.sales.replay --recheck-result path/to/captured-result.json
```

The CLI forces UTF-8 stdout so redirected JSON remains portable on Windows.


## P0 adversarial dialogue suite

Run against an isolated Parlant+FCM runtime:

```powershell
python -m mnnz.sales.dialogue_suite --base-url http://127.0.0.1:8811 --timeout 240
```

If only evaluator rules changed, recheck the exact captured JSON without another model run:

```powershell
python -m mnnz.sales.dialogue_suite --recheck-result path/to/p0-live-result.json
```

For newly added scenarios, machine PASS is not sufficient in the current phase: manually inspect the full transcript and record the verdict in `EVIDENCE.md`.
