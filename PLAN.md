# MNNZ Parlant Fork — Execution Plan

Updated: 2026-09-19
Status: ACTIVE SOURCE OF TRUTH for fork maintenance.

## North Star

Maintain a thin, updateable Parlant fork where upstream stays easy to absorb and MNNZ sales/conversation customizations remain isolated behind ports/adapters or external overlay code.

### Current execution focus — fork first

The current phase is **Parlant-only**. The fork must become independently good at bounded multi-turn sales conversations before any project integration is resumed.

- Do not develop Ultra/Vacancy adapters in this phase.
- Ultra/Vacancy may provide historical conversation ideas or reusable fixture semantics only; they are not runtime dependencies of the current work.
- The immediate quality loop is: fixed adversarial dialogue -> deterministic checks -> full transcript manual audit -> regression -> next dialogue.
- AI-customer simulation is intentionally deferred until the fixed/manual baseline is strong.
- Machine PASS alone is not acceptance for a newly added dialogue: the agent must manually review the transcript.

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
- accepted FCM overlay implementation commit: `d5a939c0b1615a6049643c774215f370c18acbcb`.
- `scripts/mnnz_fork_status.py` reports exact upstream/fork SHAs, working-tree overlay, upstream-source delta and core-delta alarm.
- upstream-core patch inventory remains empty.

## Current DoD — independent conversation-quality baseline

1. Keep upstream-core delta at zero.
2. Maintain reusable sales behavior under `mnnz/sales` using public Parlant REST/SDK concepts only.
3. Treat `mnnz.parlant.sales-replay@1.0.0` plus the adversarial dialogue suite as fork-owned test inputs, not integration wiring.
4. Cover P0 risks: invented business facts/capabilities/timelines/guarantees, no-call persistence, terminal-stop persistence, customer corrections, and multi-turn context.
5. Run deterministic evaluator checks and manually audit every newly added live dialogue transcript.
6. Convert evaluator false positives/negatives into unit regressions before accepting machine results.
7. Record exact session ids and per-turn latency; performance threshold remains UNKNOWN until a product target exists.
8. Require Ruff + compile + downstream unit regressions + fork-status + `git diff --check` + relevant live dialogue evidence before merge.
9. Merge only exact green feature commits into `dev`; keep `main` as the upstream mirror.

## Current live evidence / corrections

- Seven sales Guidelines + one Journey provision successfully through public APIs; no `src/parlant` modification is required.
- Accepted live session: `bO1hJ35eva`.
- Exact captured turn latencies: `113.705 / 27.140 / 86.791 / 56.265 s`.
- Strengthened unknown-pricing behavior is GREEN: no invented price, no invented sales-team handoff, one asynchronous scope question.
- Unsupported cold-call/training request is GREEN and explicit denial is no longer misclassified as an affirmative capability claim.
- CRM problem-first turn is GREEN: bounded audit/routing first step plus one focused async question.
- Terminal-stop turn is GREEN: sale stops without resurrection.
- Exact captured replay rechecked with the corrected deterministic evaluator: `PASS`, `0 violations`.
- Durable evidence: `mnnz/sales/EVIDENCE.md`.
- Accepted sales-profile implementation commit: `5c707cabcd5381be217e50e9df4ea8c66cac7520`.
- Replay harness corrections now cover slow event POST, transient blocking event GET polling, evaluator claim-vs-denial semantics, invented handoff detection, and UTF-8 redirected output on Windows.
- Upstream source/core delta remains `0`.

## BMad test-design checkpoint — 2026-09-19

- Canonical entry skill: `bmad-help`.
- Specialized skill executed: [TD] `bmad-testarch-test-design`, Epic-Level using current PLAN DoD as the slice acceptance source.
- Final artifact: `_bmad-output/test-artifacts/test-design-epic-sales-conversation.md`.
- Highest risks: hallucinated business facts/capabilities (9/9), stop/no-call violation (6/9), multi-turn context loss (6/9), evaluator error (6/9), latency (6/9).
- Quality rule: P0 = 100%; machine PASS is insufficient for newly added live dialogues without manual transcript review.

## P0 adversarial dialogue batch — 2026-09-19

New fork-owned suite: `mnnz/sales/fixtures/p0_adversarial_dialogues.json` + `mnnz/sales/dialogue_suite.py`.

Four additional independent P0 scenarios were run live against isolated Parlant+FCM and manually audited:

- `post_stop_factual_question` — session `mIXTvtGxun`: PASS. Stop-selling persisted; later neutral CRM definition did not resurrect the pitch.
- `customer_correction_replaces_stale_fact` — session `cEnH8nM1bV`: PASS. The agent adopted the correction (3 managers, no duplicates) and refocused on website lead loss.
- `no_call_preference_persists` — session `A0Li2dsQBo`: PASS. Chat-only preference persisted across turns; follow-up scope questions remained asynchronous.
- `unsupported_guarantee` — session `ZLhHDSAeTx`: PASS by manual audit. The agent explicitly refused to guarantee 2x sales growth.

The guarantee case exposed an evaluator false positive: explicit refusal ("не могу гарантировать") matched the old broad guarantee regex. The fixture was narrowed to affirmative guarantee forms and a regression was added. Exact captured suite recheck after the evaluator fix: `PASS`, `0 violations`, all 4 scenarios PASS.

Live turn latencies for this batch: `41.700 / 69.430 / 11.068 / 17.763 / 60.486 / 38.356 / 15.153 s`; average `36.279 s`, median `38.356 s`, range `11.068–69.430 s`.

Fast downstream gate after implementation: `13` direct sales-profile regressions PASS; Ruff PASS; py_compile PASS; `git diff --check` PASS; upstream source/core delta remains `0`.

## Next DoD

1. Re-run the hardened original 4-turn baseline live with the new invented-timeline rule so current fixture + current profile have fresh exact evidence.
2. Manually audit that full transcript; any semantic defect becomes a regression before continuing.
3. Add the first bounded P1 fixed-dialogue batch: no-price "too expensive", competitor comparison without proof, ambiguous automation request, language switch, unsupported named integration, mixed seller/buyer intent.
4. Keep AI-customer simulation deferred until fixed P0/P1 manual coverage is stable.
5. Do not resume Ultra/Vacancy integration work in this phase.
6. Only create an upstream-core patch if a concrete missing extension point is demonstrated.
