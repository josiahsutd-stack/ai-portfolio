# Local Service And Deployment Boundary

The verified runtime in this repository is local. The Streamlit app and FastAPI service run with bundled synthetic data and no paid API. No public deployment, uptime, traffic, operational-security, or user-adoption claim is made.

## Verified Local FastAPI Service

PowerShell from the repository root:

```powershell
$env:AEC_RAG_API_KEY = "local-review-key"
python -m uvicorn api:app --app-dir projects/aec-code-compliance-rag --host 127.0.0.1 --port 8000
```

Runtime configuration:

| Variable | Default | Boundary |
| --- | --- | --- |
| `AEC_RAG_API_KEY` | none | Required; protected routes fail closed when absent. |
| `AEC_RAG_CORPUS` | `synthetic` | Use `public` only after downloading the optional public corpus. |
| `AEC_RAG_LOG_PATH` | `.artifacts/aec-rag/query_log.sqlite` | Ignored local SQLite path; not a distributed audit store. |
| `AEC_RAG_LOG_PAYLOADS` | `false` | Questions and response bodies remain redacted unless explicitly enabled. |
| `AEC_RAG_TELEMETRY_RETENTION` | `5000` | Maximum local request rows retained in SQLite. |
| `AEC_RAG_TELEMETRY_WINDOW` | `200` | Latest durable rows considered by service metrics. |
| `AEC_RAG_QUERY_OBJECTIVE_MIN_REQUESTS` | `20` | Query objective remains `insufficient_data` below this sample. |
| `AEC_RAG_QUERY_P95_BUDGET_MS` | `500` | Local query P95 threshold; not a production SLO. |
| `AEC_RAG_QUERY_SERVER_ERROR_RATE_BUDGET` | `0.01` | Local query 5xx-rate threshold; not an availability claim. |

Public endpoints are `/health/live` and `/health/ready`. The `X-API-Key` header is required for `/sources`, `/query`, `/retrieve`, `/logs/recent`, and `/metrics`.

The deterministic contract evaluator exercises authentication, request IDs, readiness, retrieval, abstention, log redaction, and metrics without opening a network port:

```bash
python projects/aec-code-compliance-rag/evaluate_service.py
python projects/aec-code-compliance-rag/evaluate_service_reliability.py
```

Versioned outputs include the [service contract report](demo_outputs/service_contract_report.md) and [local reliability report](demo_outputs/service_reliability_report.md). The latter runs 48 warmed in-process queries at maximum concurrency 8, checks fixed latency/error budgets, and reconstructs the app to verify local SQLite persistence. These are not proof of an internet-facing deployment, sustained capacity, or availability.

## Verified Local Streamlit App

```bash
streamlit run projects/aec-code-compliance-rag/app.py
```

The repository root also includes `app.py`, which delegates to the project app for hosts that expect a root Streamlit entrypoint.

## Unverified Hosting Options

The following configurations are implementation notes only. They have not been presented as deployed evidence in this repository.

## Option A: Streamlit Community Cloud

1. Go to Streamlit Community Cloud and choose **New app**.
2. Select repository: `josiahsutd-stack/ai-portfolio`.
3. Select branch: `main`.
4. Set main file path to `app.py`.
5. Keep secrets empty for the default mock/synthetic mode.
6. Deploy.
7. Confirm the app loads and the sidebar shows the local corpus controls.
8. Verify the public URL in a signed-out browser session before presenting it as deployment evidence.

The app uses the repository root `requirements.txt` and `.streamlit/config.toml`.

## Option B: Hugging Face Spaces

1. Create a new Hugging Face Space.
2. SDK: **Streamlit**.
3. Visibility: public or private.
4. Upload or connect this repository.
5. Ensure the Space uses root `app.py` as the app file.
6. If creating a separate Space repo, copy `deploy/huggingface-space/README.md` to the Space root as `README.md`.
7. Ensure `requirements.txt` is present in the Space root.
8. Start the Space.
9. Confirm the app loads without secrets.
10. Verify the public URL in a signed-out browser session before presenting it as deployment evidence.

## Option C: Render

The root `render.yaml` defines a web service that runs:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

Render installs from `requirements.txt` and uses Python 3.11.

## Runtime Behavior

- Default mode uses the bundled synthetic corpus.
- If `OPENAI_API_KEY` is absent, the app uses deterministic mock behavior.
- Public Singapore source PDFs are not committed. To enable the optional public-source corpus on a host, run:

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
```

Only do that if the host allows network download and persistent storage.

## Safety Copy

Any hosted version must identify the interface as source-grounded document assistance, not legal, architectural, engineering, or code-compliance sign-off. Before a deployment could support an operational claim, it would also need identity-aware authorization, managed secrets, TLS, rate limiting, distributed telemetry, source refresh controls, network load and security testing, incident handling, and observed reliability targets.
