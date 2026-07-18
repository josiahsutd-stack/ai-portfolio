# Architecture

## Scope

The system searches a bounded family of rectangular 2.5D massing typologies. It separates supplied hard constraints from preference objectives so an attractive score cannot hide an invalid candidate.

## Components

| Component | Responsibility | Deliberate boundary |
| --- | --- | --- |
| `models.py` | Typed sites, rectangles, masses, candidates, violations, and assessments. | Bundled scenarios must declare `data_status: synthetic`. |
| `generation.py` | Reproducible slab, twin-bar, courtyard, and stepped candidates. | Parametric search; no learned generative model. |
| `assessment.py` | Hard validation, access-grid search, proxy objectives, utility, and Pareto dominance. | No statutory or calibrated simulation engine. |
| `rendering.py` | SVG plan, isometric view, and option comparison from candidate geometry. | Diagrams are evaluated geometry, not photorealistic design claims. |
| `evaluation.py` | Fixed-site, fixed-seed baseline comparison and artifact generation. | Synthetic regression evidence only. |
| `app.py` | Interactive constraints, option selection, metrics, and provenance record. | Local decision-support interface. |

## Data Flow

```mermaid
flowchart TD
  A["Scenario JSON"] --> B["SiteScenario validation"]
  B --> C1["Unconstrained baseline sampler"]
  B --> C2["Constraint-aware sampler"]
  C1 --> D["Shared hard validator"]
  C2 --> D
  D --> E["Feasible and invalid sets"]
  E --> F["GFA, solar, daylight, wind, and access proxies"]
  F --> G["Pareto dominance"]
  G --> H["Preference-weighted ordering"]
  H --> I["JSON, Markdown, SVG, and Streamlit views"]
```

## Hard And Soft Separation

Hard failures cover site bounds, supplied setbacks, height, site coverage, maximum GFA, overlap, and open-site route reachability. GFA target fit and four environmental/circulation proxies are soft objectives. Pareto ranking runs only over feasible candidates.

## Access Path Model

The site is rasterized at the scenario's stated resolution. Footprint cells are blocked and breadth-first search measures an open route from each supplied site access point to a free cell adjacent to any mass. This tests site-level reachability only; internal egress is out of scope.

## Reproducibility

- Candidate generation uses explicit seeds.
- Scenario rows and objective weights are versioned.
- Baseline and constraint-aware modes share the same validator and metrics.
- Generated artifacts contain no timestamps or machine-specific paths.
