# Massing Search Evaluation

**Data status:** synthetic

The benchmark uses 3 bundled synthetic sites, 96 candidates per mode, and fixed seeds `[11, 23, 37]`. It compares geometry sampled without constraint awareness against the constraint-aware generator using the same validator and objective calculations.

| Metric | Constraint-aware | Unconstrained baseline |
| --- | ---: | ---: |
| Mean feasible-candidate rate | 0.977 | 0.052 |
| Mean best utility per run | 0.767 | 0.628 |
| Mean best GFA error | 0.19% | 34.47% |

Feasibility means the candidate passed the supplied site, setback, height, site-coverage, maximum-GFA, overlap, and open-site access-path checks. Utility is a transparent weighted score over target-GFA fit and four proxy objectives. These numbers are regression evidence for this local search implementation, not architectural performance or regulatory validation.
