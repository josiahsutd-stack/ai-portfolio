# GitHub Setup Guide

## 1. Rename And Personalize

- Replace placeholder contact links in `profile-readme.md`.
- Add the candidate's real name only where appropriate.
- Keep the positioning statement confident and specific.

## 2. Generate Data And Run Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
python scripts/generate_sample_data.py
pytest
```

## 3. Add Screenshots

Run each Streamlit app and capture a clean desktop screenshot. Add screenshots to each project README under the Demo section.

Suggested filenames:

- `projects/aec-code-compliance-rag/docs/screenshot.png`
- `projects/construction-progress-cv/docs/screenshot.png`
- `projects/bim-issue-detection-agent/docs/screenshot.png`
- `projects/ai-aec-job-fit-analyzer/docs/screenshot.png`
- `projects/building-energy-ml-pipeline/docs/screenshot.png`
- `projects/spatial-design-recommender/docs/screenshot.png`

## 4. Publish The Profile README

Copy the contents of `profile-readme.md` into a GitHub profile repository named the same as the GitHub username.

## 5. Create Repository Description

Suggested GitHub repo description:

```text
Applied AI engineering portfolio for built-environment workflows: RAG, BIM QA, CV-style progress tracking, energy ML, and spatial recommendations.
```

## 6. Topics

Suggested topics:

```text
ai-engineering rag fastapi streamlit machine-learning computer-vision aec bim construction-tech proptech built-environment
```

