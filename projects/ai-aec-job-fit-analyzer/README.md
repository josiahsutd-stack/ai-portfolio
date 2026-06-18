# AI Job Market Fit Analyzer for AI + Architecture Roles

Personal career tool that parses job descriptions, classifies role fit, extracts skill signals, identifies gaps, and generates a tailored application strategy.

## Problem

Candidates pivoting from architecture into AI need to decide which roles fit their background and how to position project evidence without overclaiming.

## Why It Matters

This project connects directly to the candidate story: AI engineering, applied AI, and built-environment domain expertise.

## Demo

```bash
streamlit run projects/ai-aec-job-fit-analyzer/app.py
```

## Features

- Job description parser
- Skill extraction
- Role classification
- Resume keyword matching
- Gap analysis
- Tailored application strategy output
- Sample job descriptions

## Tech Stack

Python, Streamlit, deterministic NLP rules, pytest.

## Architecture

```mermaid
flowchart LR
  A["Job description"] --> B["Normalize and extract skills"]
  B --> C["Role classifier"]
  B --> D["Candidate skill matcher"]
  C --> E["Fit score"]
  D --> E
  E --> F["Application strategy"]
```

## How It Works

The analyzer maps job text to skill categories, compares extracted requirements to the candidate's AI plus AEC positioning, and returns a role class with a fit score.

## Example Output

```text
Role type: AI + architecture / AEC
Fit score: 86
Strategy: Lead with AI plus built-environment positioning and show RAG, BIM QA, CV progress, and energy ML projects.
```

## Run Locally

```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py
streamlit run projects/ai-aec-job-fit-analyzer/app.py
```

## Tests

```bash
pytest tests/test_job_fit.py
```

## Limitations

- Uses transparent keyword rules rather than a large NLP model.
- The resume profile is a placeholder and should be customized.
- Fit scoring is a decision aid, not a guarantee.

## How I Would Improve This In Production

- Add resume upload and structured resume parsing.
- Add LLM-based evidence mapping from portfolio projects to job requirements.
- Add cover-letter and recruiter-message drafts with review controls.

## What This Proves To Employers

- NLP product thinking
- Structured classification
- Honest career-positioning automation
- Ability to connect AI systems to a real user workflow

## Engineering Notes

- The project uses transparent role rules because the goal is explainable career matching, not opaque resume ranking.
- The output is structured around decisions a job seeker actually makes: role fit, skill gaps, portfolio evidence, and next actions.
- Synthetic sample jobs keep the workflow safe to share while demonstrating how AI can organize ambiguous job descriptions.
- A production version would add resume parsing, LLM evidence extraction, calibrated scoring, prompt/version tracking, and recruiter-message review controls.

## Interview Talking Points

- Explain why interpretability matters in career and hiring-adjacent tools.
- Discuss how you would evaluate role classification quality across AI, ML, and AEC postings.
- Walk through how portfolio evidence is mapped to job requirements.
- Describe where an LLM should help and where deterministic rules are preferable.
- Be clear that fit scores are guidance, not hiring predictions.
