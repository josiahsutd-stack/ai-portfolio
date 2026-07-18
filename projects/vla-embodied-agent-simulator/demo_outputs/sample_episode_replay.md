# Sample Embodied Agent Episode Replay

- Scenario: Drywall Delivery To Level 2 Staging
- Instruction: Deliver the drywall stack to the level 2 staging area.
- Policy: safety_shielded
- Success: True
- Steps: 14
- Total reward: 4.8

| Step | Action | Reward | Done | Info | Agent | Carrying |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | move_down | -0.1 | False | `{"safety": "safe"}` | (0, 1) | None |
| 2 | move_down | -0.1 | False | `{"safety": "safe"}` | (0, 2) | None |
| 3 | move_down | -0.1 | False | `{"safety": "safe"}` | (0, 3) | None |
| 4 | move_down | -0.1 | False | `{"safety": "safe"}` | (0, 4) | None |
| 5 | move_right | -0.1 | False | `{"safety": "safe"}` | (1, 4) | None |
| 6 | pick | 1.0 | False | `{"picked": "drywall_stack", "safety": "safe"}` | (1, 4) | drywall_stack |
| 7 | move_right | -0.1 | False | `{"safety": "safe"}` | (2, 4) | drywall_stack |
| 8 | move_down | -0.1 | False | `{"safety": "safe"}` | (2, 5) | drywall_stack |
| 9 | move_right | -0.1 | False | `{"safety": "safe"}` | (3, 5) | drywall_stack |
| 10 | move_right | -0.1 | False | `{"safety": "safe"}` | (4, 5) | drywall_stack |
| 11 | move_right | -0.1 | False | `{"safety": "safe"}` | (5, 5) | drywall_stack |
| 12 | move_right | -0.1 | False | `{"safety": "safe"}` | (6, 5) | drywall_stack |
| 13 | move_up | -0.1 | False | `{"safety": "safe"}` | (6, 4) | drywall_stack |
| 14 | drop | 5.0 | True | `{"dropped": "drywall_stack", "success": "task_complete"}` | (6, 4) | None |
