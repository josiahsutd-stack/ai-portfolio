# AEC RAG Deployment Notes

The AEC Code Compliance RAG app is designed to run locally without API keys. A hosted demo should use the same mock/local mode by default and should not present outputs as professional compliance advice.

## Streamlit Community Cloud

Suggested settings:

- Repository: `josiahsutd-stack/ai-portfolio`
- Branch: `main`
- Main file path: `projects/aec-code-compliance-rag/app.py`
- Python version: 3.11
- Secrets: none required for mock/local mode

After deployment, replace the placeholder link in the root `README.md` with the Streamlit app URL.

## Render

This repo includes a root `render.yaml` with a web service that runs:

```bash
streamlit run projects/aec-code-compliance-rag/app.py --server.address 0.0.0.0 --server.port $PORT
```

Render should install dependencies from `requirements.txt`.

## Hugging Face Spaces

For Spaces, create a Streamlit Space and set the app entrypoint to `projects/aec-code-compliance-rag/app.py`. If the Space requires a root `app.py`, use a tiny wrapper that imports and runs the project app, or copy the project app into the Space-specific branch.

## Public Source Corpus

Public Singapore source PDFs are downloaded locally and are not committed. A hosted demo can either:

- stay on the bundled synthetic corpus, or
- run `python projects/aec-code-compliance-rag/scripts/download_public_sources.py` during setup if the host allows network download and storage.

## Safety Copy

Keep visible copy clear that the demo is source-grounded document assistance, not legal, architectural, engineering, or code-compliance sign-off.
