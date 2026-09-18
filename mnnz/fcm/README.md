# FCM compatibility profile

This is the fork-owned reproducible profile for running Parlant against the local FCM OpenAI-compatible endpoint.

## Canonical baseline

- FCM base URL: `http://127.0.0.1:19280/v1`
- model route: `openai/fcm:fast-coding`
- Parlant provider: existing upstream `LiteLLMService`
- transport/sender: not enabled by this profile

The `openai/` LiteLLM prefix is intentional: FCM exposes an OpenAI-compatible API while the model identifier remains `fcm:fast-coding`.

## Why a downstream bootstrap exists

The A55 spike found two dependency/runtime compatibility issues:

1. Parlant startup migration imported ChromaDB on the tested path, so `chromadb` had to be installed.
2. Jina embedding code expected `transformers.onnx`; Transformers 5.x removed that import path, so the proven Windows profile pins `transformers<5`.

These are kept as **downstream compatibility constraints** instead of modifying upstream core or dependency metadata before an upstreamable fix is demonstrated.

## Bootstrap

From repository root on Windows PowerShell:

```powershell
./mnnz/fcm/bootstrap.ps1
```

This creates `.venv-mnnz-fcm` and installs this fork editable with the upstream LiteLLM extra plus the proven compatibility constraints.

## Run

```powershell
./mnnz/fcm/run.ps1
```

Useful overrides:

```powershell
./mnnz/fcm/run.ps1 -Port 8811 -Home ".parlant-data/my-isolated-run"
```

Every concurrent test/runtime must use a unique `PARLANT_HOME`. Reusing a scratch home across agents/tests caused misleading session/config collisions in the spike.

## Live smoke

Once the server is ready:

```powershell
.\.venv-mnnz-fcm\Scripts\python.exe .\mnnz\fcm\smoke.py --base-url http://127.0.0.1:8811
```

The smoke:
1. creates a disposable agent;
2. creates a session;
3. posts a Russian sales-like message;
4. waits for an AI message;
5. prints machine-readable JSON including latency.

It does not perform external sales transport or side effects.
