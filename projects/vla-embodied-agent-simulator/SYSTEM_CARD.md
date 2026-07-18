# Construction Embodied Agent Simulator: System Card

## Intended Use

This local simulator supports inspection of task parsing, observation encoding, supervised imitation, constrained route planning, action filtering, reward design, trace-based evaluation, and a bounded planar command replay through MuJoCo.

## Not Intended For

- Real robot operation or physical safety decisions.
- Mobile-base dynamics, controller tuning, contact-force assessment, ROS, SLAM, hardware, or sim-to-real claims.
- Proof that a learned policy works on a construction site.
- Foundation vision-language-action evaluation.

## Models In Scope

1. A random-forest action classifier over 24 engineered state features.
2. A one-hidden-layer MLP over eight fully observable 7x7 semantic state channels plus six global features.
3. A one-hidden-layer MLP over an agent-centered 5x5 semantic window plus ten task/navigation values.
4. A one-hidden-layer MLP over a rendered 10x10 RGB crop plus ten task/navigation values, evaluated under standard and unseen appearance palettes.

The fourth model consumes image pixels, but they are rendered directly from privileged simulator state rather than captured by a physical or photorealistic simulated camera. The world-raster model exposes a representation and data-scale limitation. The egocentric model recovers performance through agent-centered alignment. The RGB model performs competitively in its standard appearance and fails severely under an unseen palette. Every local policy filter continues to apply full-state simulator rules.

## Safety Controls In Scope

- Invalid action rejection.
- Obstacle, restricted-zone, and worker-proximity checks.
- Battery and timeout handling.
- Ranked-action filtering with intervention counts.
- Repeatable evaluation across fixed-seed procedural train and holdout splits.
- Named rigid-contact and target-error regression for a balanced 12-scenario command subset.

## Evaluation

All four learned policy families train on 192 synthetic scenarios and are evaluated on the same 96 disjoint holdout scenarios. The RGB model sees two appearance variants during training and a separate unseen palette at evaluation. Reports separate expert-state action accuracy from closed-loop success, unsafe-action rate, task-error rate, interventions, and failure traces. A deterministic A* planner is retained as a full-map reference, not a learned baseline. MuJoCo replays movement commands for four holdout scenarios per task family; contacts are planar regression events against static proxies, not real collision-risk estimates.

## Main Risk

The action filter can make weak learned behavior look safer than it is. The published report therefore includes raw rollouts, intervention counts, failed episodes, and explicit model boundaries. None of these results establish perception, physical safety, or deployment readiness.
