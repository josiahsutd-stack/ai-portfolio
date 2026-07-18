# AEC RAG Deployment Guide

This guide deploys the flagship AEC Code Compliance RAG Streamlit app in mock/synthetic mode. No paid API keys are required for the app to load.

The repository root now includes `app.py`, which delegates to `projects/aec-code-compliance-rag/app.py`. This keeps deployment simple for hosts that expect a root Streamlit entrypoint.

## Option A: Streamlit Community Cloud

Expected time: under 15 minutes after signing in.

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

Expected time: under 15 minutes after signing in.

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

Keep visible copy clear that the demo is source-grounded document assistance, not legal, architectural, engineering, or code-compliance sign-off.
