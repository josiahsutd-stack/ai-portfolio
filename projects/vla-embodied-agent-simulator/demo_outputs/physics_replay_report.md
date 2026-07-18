# MuJoCo Planar Physics Replay

This fixed-set evaluation replays discrete policy commands as continuous planar position-control targets in headless MuJoCo. Static obstacles, restricted-area proxies, worker proxies, and site boundaries participate in rigid contact. It is a command-interface and collision-regression test, not a mobile-robot dynamics or safety validation.

- Engine: `MuJoCo 3.10.0`
- Scenarios: 12
- Policies: 3
- Cell scale: 1.0 m
- Target tolerance: 0.08 m

| Policy | Episodes | Discrete success | Move commands | Reached target | Contact commands | Contact rate | Max final alignment error (m) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `egocentric_mlp_raw` | 12 | 0.833 | 150 | 0.660 | 51 | 0.340 | 0.0290 |
| `egocentric_mlp_shielded` | 12 | 0.917 | 148 | 1.000 | 0 | 0.000 | 0.0290 |
| `safety_shielded` | 12 | 1.000 | 98 | 1.000 | 0 | 0.000 | 0.0290 |

## Interpretation

- A contact command means the robot body touched a named rigid obstacle or exclusion proxy while pursuing that command; floor contact is excluded.
- Reached-target rate tests whether the continuous body arrived within the declared tolerance before any recovery command.
- A blocked discrete move is returned to the discrete result cell before the next command. This preserves trace alignment and is not presented as a recovery controller.
- Restricted and worker cells are represented as rigid proxies solely to regression-test the command boundary; their geometry is not a physical human or site model.

## Boundary

Continuous planar command replay with rigid contacts; not a mobile-robot model, controller validation, ROS integration, perception stack, or physical-safety result.
