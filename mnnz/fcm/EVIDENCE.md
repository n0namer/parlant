# FCM compatibility evidence — 2026-09-18

Status: PASS for the first fork-owned live compatibility smoke.

## Exact source / topology

- fork repo: `n0namer/parlant`
- working branch during proof: `feature/mnnz-fcm-overlay`
- fork/dev baseline before this slice: `10d5233f0707268282b27846e4298731b1e8cdf6`
- upstream baseline: `ea737442b8ae65854a842542e544fbe7e6144bad`
- upstream provider path used: existing `LiteLLMService`
- Parlant runtime: isolated local instance on `127.0.0.1:8811`
- FCM endpoint behind that runtime: `http://127.0.0.1:19280/v1`
- model route: `openai/fcm:fast-coding`

## Live smoke

Command:

```powershell
python mnnz/fcm/smoke.py --base-url http://127.0.0.1:8811 --timeout 60
```

Observed result:

- status: PASS
- latency: 29.193 s
- disposable agent: `F96WSx1NlT`
- disposable session: `tnQ6AhcHXe`
- behavior: Russian reply, no invented price, proposed a minimal diagnostic first step.
- external sales transport / provider side effects: none.

A prior run of the same fork-owned smoke created session `lmzR8OIAjv` and returned a Russian response recommending an audit of lead-loss points before proposing a concrete solution.

## Dependency compatibility evidence

The earlier A55 spike on Parlant 3.3.2 found:

- `chromadb` was required by the tested startup/migration path.
- Transformers 5.x broke the Jina fallback embedding path because `transformers.onnx` was unavailable.
- the proven Windows profile therefore installs the fork editable with `[litellm]`, adds `chromadb>=1.1.1`, and pins `transformers<5`.

These remain downstream compatibility constraints. No upstream-owned source file was modified for FCM compatibility in this slice.

## Acceptance interpretation

PASS means:
- fork-owned tooling can reach the live Parlant runtime;
- the upstream LiteLLM adapter can reach FCM using the canonical fast-coding route;
- a real multi-stage Parlant generation completes and returns a usable message;
- this integration did not require modifying `src/parlant`.

It does **not** mean Parlant replaces Ultra/Vacancy deterministic safety. That boundary remains external and is documented in `AGENTS.md` / `PLAN.md`.


## Canonical fork-runtime provenance check — 2026-09-19

A fresh acceptance runtime was launched from the fork-owned editable environment:

- checkout: `D:\Users\NIKITA\Documents\DEV\parlant-mnnz`
- environment: `.venv-mnnz-fcm`
- resolved adapter source: `D:\Users\NIKITA\Documents\DEV\parlant-mnnz\src\parlant\adapters\nlp\litellm_service.py`
- isolated home: `.parlant-data\fork-acceptance-20260919-1316c`
- port: `127.0.0.1:8811`
- model route: `openai/fcm:fast-coding`
- initial fresh instance id: `gvgLYH6YaH`
- initial engine/NLP sample counts before replay: `0`

This corrects an earlier verification ambiguity where port 8811 had been occupied by a reused runtime. Acceptance evidence must bind runtime source path + fresh home + exact session, not port number alone.
