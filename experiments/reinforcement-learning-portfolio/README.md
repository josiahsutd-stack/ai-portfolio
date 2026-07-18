# Sequential Decision Simulation Baselines

Warehouse inventory and dynamic-pricing simulators with random and hand-written policies, explicit rewards, and repeatable policy evaluation. No policy is learned in the current implementation.

## Problem

Sequential decisions such as reordering or price changes require simulation, rewards, baselines, and evaluation before optimization claims are meaningful.

## Demo

```bash
streamlit run experiments/reinforcement-learning-portfolio/app.py
```

## Features

- Inventory-control environment
- Dynamic-pricing environment
- Random and heuristic baselines
- Reward curves via local evaluation metrics
- Reproducible seeds
- Short local simulation/evaluation path

## Tech Stack

Python, NumPy-style environment design, Streamlit, pytest.

## Architecture

```mermaid
flowchart LR
  A["Environment state"] --> B["Policy"]
  B --> C["Action"]
  C --> D["Reward + next state"]
  D --> E["Evaluation metrics"]
```

## Tests

```bash
python -m pytest tests/test_general_ai_projects.py -k rl_environment
```

## Limitations

- Lightweight custom environments rather than heavy RL libraries.
- The current policies are random or hand-written; no policy parameters are learned.
- No production pricing or inventory claims.

## Deployment-Relevant Extensions

- Add Gymnasium wrappers, DQN/PPO integrations, experiment tracking, and richer simulations.

## Evidence

Environment design, reward shaping, sequential decision-making, simulation, and baseline evaluation without a learned-policy claim.

## Implementation Notes

- The project focuses on small environments where state, action, reward, and policy behavior can be inspected without heavy dependencies.
- Baseline policies make reward tradeoffs visible before introducing DQN, PPO, or other learned agents.
- The environments are intentionally business-flavored so RL is connected to operational decisions rather than abstract benchmarks only.
- Production use would require Gymnasium-compatible wrappers, experiment tracking, reproducible seeds, stronger baselines, and safety-aware evaluation.

## Design Decisions

- Each environment exposes its state, action, reward, and transition design directly.
- Reward shaping is framed as both a design tool and a source of unintended behavior.
- Baseline policies are included before deep RL to make comparisons meaningful.
- PPO/DQN are documented as future extensions to compare against heuristic policies.
- The project is clearly framed as RL fundamentals, not a production RL deployment.

