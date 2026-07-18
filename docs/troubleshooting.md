# Troubleshooting

## Python Version

Use Python 3.11 or newer. The repo has been tested locally with Python 3.13.

```powershell
python --version
```

## Windows Setup

```powershell
cd "C:\path\to\ai-portfolio"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python scripts/generate_sample_data.py
```

## macOS / Linux Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python scripts/generate_sample_data.py
```

## Missing Python Packages

Run:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

If a package still cannot be imported, confirm the virtual environment is active.

## Streamlit Issues

Run one project at a time:

```bash
streamlit run experiments/deterministic-research-workflow/app.py
```

If the port is busy:

```bash
streamlit run experiments/deterministic-research-workflow/app.py --server.port 8502
```

## FastAPI Issues

Use the project `src` path:

```bash
python -m uvicorn local_model_serving_monitoring.api:app --app-dir experiments/local-model-serving-monitoring/src --reload
```

If the port is busy, add `--port 8001`.

## Missing `.env` Variables

No paid API keys are required. Copy `.env.example` to `.env` only when you want to experiment with real providers.

Default local mode:

```text
AI_PROVIDER=mock
VLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
QUICK_MODE=true
```

## Model / API Key Issues

The demos use mock providers when API keys are missing. Real provider integrations should be treated as optional extensions.

## SQLite / Database Issues

Current demos do not require external databases. Future persistence can use local SQLite files, which should be deleted and regenerated if schema changes.

## Docker Issues

Build from the repository root:

```bash
docker build -f experiments/local-model-serving-monitoring/Dockerfile -t ai-portfolio-local-serving .
```

If Docker cannot find files, confirm you are in the repo root.

## Test Failures

Run:

```bash
python scripts/generate_sample_data.py
python scripts/run_smoke_tests.py
python -m pytest
```

If failures persist, run the single failing test file shown in the output.

## Reset Sample Data

```bash
python scripts/generate_sample_data.py
```

## Run A Single Project

```bash
streamlit run projects/<project-folder>/app.py
```

Example:

```bash
streamlit run experiments/visual-provider-contract/app.py
```

## Smoke Tests

```bash
python scripts/run_smoke_tests.py
```
