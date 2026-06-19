# Spatial Design Recommendation Engine

Explainable recommendation engine that scores design scenarios and suggests layout improvements based on daylight, circulation, room sizing, adjacency, and zoning constraints.

## Problem

Early layout decisions affect daylight, circulation efficiency, adjacency quality, and operational usability, but design teams often lack fast quantitative feedback.

## Why It Matters

The project shows recommendation-system thinking in an architecture context without overclaiming full automated design generation.

## Demo

```bash
streamlit run projects/spatial-design-recommender/app.py
```

## Features

- Constraint input form
- Scoring function
- Rule-based recommendation engine
- Explainable recommendation rationales
- Example scenarios
- API plus simple UI

## Tech Stack

Python, FastAPI, Streamlit, pytest.

## Architecture

```mermaid
flowchart LR
  A["User constraints"] --> B["Scenario validator"]
  B --> C["Scoring function"]
  C --> D["Recommendation engine"]
  D --> E["Explanation layer"]
  E --> F["Dashboard/API response"]
```

## How It Works

The engine evaluates whether a scenario sits inside target bands for daylight, circulation ratio, average room area, and public/private separation. It returns prioritized actions with score impact estimates.

## Example Outputs

```text
Score: 58
High priority: Improve daylight by moving high-occupancy rooms closer to facade zones.
High priority: Reduce circulation inefficiency by consolidating corridor runs.
```

## Run Locally

```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py
streamlit run projects/spatial-design-recommender/app.py
python -m uvicorn spatial_design_recommender.api:app --app-dir projects/spatial-design-recommender/src --reload
```

## Tests

```bash
pytest tests/test_recommender.py
```

## Limitations

- Uses simplified constraints and handcrafted scoring.
- Does not generate floor plans or optimize geometry.
- Real production use would need project-specific requirements and user validation.

## Deployment-Relevant Extensions

- Add multi-objective optimization.
- Connect to BIM/geometry exports.
- Add preference learning from designer feedback.
- Generate option-comparison reports.

## Reviewer Signal

- Recommendation-system thinking
- Explainable AI for design decisions
- Built-environment product framing
- Clear separation between prototype scoring and production optimization

## Engineering Notes

- The recommender uses handcrafted scoring so reviewers can inspect every factor that affects the recommendation.
- The product surface emphasizes comparisons and explanations because design teams need to understand tradeoffs, not accept a black-box layout score.
- The project intentionally stops short of geometry generation; it focuses on preference modeling and decision support.
- Production use would require BIM/geometry ingestion, user preference learning, constraint solving, and validation with designers or planners.

## Technical Review Discussion Points

- Reviewers can assess why recommendations are useful before generative floor-plan tooling is introduced.
- Spatial constraints, accessibility, daylight, circulation, and adjacency are clear feature-extension paths.
- Explanations make the recommendations more credible for designers and planners.
- The project shows a path from handcrafted scoring to learned ranking or multi-objective optimization.
- The prototype is clearly framed as scenario scoring, not buildable plan generation.
