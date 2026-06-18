# VLA Embodied Agent Simulator

VLA-inspired simulation that maps natural-language instructions and grid-world state into safe action sequences. This is not a real robot deployment.

## Problem

Robotics/VLA systems need to connect instructions, observations, state, actions, and safety constraints before touching hardware.

## Demo

```bash
streamlit run projects/vla-embodied-agent-simulator/app.py
```

## Features

- Simulated grid-world state
- Natural-language task parser
- Rule-based baseline planner
- Safety constraints and invalid-action handling
- Episode trace and text renderer
- Success/failure metrics through tests

## Tech Stack

Python, Streamlit, dataclass environment, pytest.

## Architecture

```mermaid
flowchart LR
  A["Language instruction"] --> B["Task parser"]
  C["Visual/state grid"] --> D["Safety-aware planner"]
  B --> D
  D --> E["Action sequence"]
  E --> F["Episode replay"]
```

## Limitations

- Grid-world only.
- No real vision model, robot hardware, ROS, or learned policy.

## How I Would Improve This In Production

- Add Gymnasium integration, learned policies, richer visual observations, and robotics simulation.
- Add ROS 2 bridge and safety validation before hardware use.

## What This Proves To Employers

VLA concepts, embodied AI simulation, action planning, robotics safety thinking, and practical environment design.

## Engineering Notes

- The simulator connects language goals, grid-world state, valid actions, and safety checks to demonstrate the core VLA loop in a lightweight form.
- A rule-based planner is used as a clear baseline before introducing learned policies or perception models.
- The environment records traces so action choices and failures can be inspected step by step.
- Production-grade embodied AI would require richer observations, learned policies, simulation benchmarks, ROS/simulator bridges, and hardware safety validation.

## Interview Talking Points

- Explain what "vision-language-action" means and how this project approximates it.
- Walk through how instructions become actions under state and safety constraints.
- Discuss why simple environments are valuable for debugging embodied agents.
- Describe how you would extend this toward Gymnasium, Isaac Sim, Habitat, or ROS 2.
- Connect the project to your embodied AI specialization and construction robotics interests.

