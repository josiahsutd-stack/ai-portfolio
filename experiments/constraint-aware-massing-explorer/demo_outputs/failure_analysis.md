# Failure Analysis

**Data status:** synthetic

Violation counts are event counts, so one candidate may contribute more than one violation.

| Validator code | Constraint-aware | Unconstrained baseline |
| --- | ---: | ---: |
| `egress_path` | 0 | 75 |
| `height_limit` | 0 | 453 |
| `ingress_path` | 0 | 91 |
| `max_gfa` | 20 | 347 |
| `outside_site` | 0 | 864 |
| `setback_envelope` | 0 | 1537 |
| `site_coverage` | 0 | 255 |

The generator does not repair every invalid option. Invalid candidates remain visible in the evaluation so that feasibility yield and recurrent failure modes can be inspected.
