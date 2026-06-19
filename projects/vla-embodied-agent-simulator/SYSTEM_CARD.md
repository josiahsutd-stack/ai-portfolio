# System Card

## Intended Use

This project is a local construction-site embodied AI simulator. It is intended for inspecting language-to-action parsing, constrained route planning, action masking, reward design, and trace-based evaluation.

## Not Intended For

- Real robot operation.
- Physical safety certification.
- ROS, SLAM, perception, or hardware integration claims.
- Proof that a learned VLA policy works in the physical world.

## Safety Controls In Scope

- Invalid action rejection.
- Obstacle, restricted-zone, and worker-proximity checks.
- Battery and timeout handling.
- Repeatable policy evaluation across fixed scenarios.

## Evaluation

The included evaluation compares random, naive language, and safety-shielded policies. Metrics are simulator regression checks: success rate, average reward, unsafe action rate, blocked actions, and replay traces.

## Main Risk

The simulator can demonstrate engineering structure and safety thinking, but it must not be presented as evidence of deployed robotics ownership or validated real-world robot safety.
