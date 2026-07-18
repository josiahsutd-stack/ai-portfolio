# Retrieval Uncertainty Report

Synthetic demo uncertainty analysis for the AEC retrieval evaluation.

## Interpretation Boundary

Intervals quantify case-resampling uncertainty inside this fixed authored evaluation set. They do not measure label independence, corpus currency, expert agreement, or performance on a broader query population.

These intervals are not a claim of production accuracy or external validity.

## Protocol

- Confidence level: 0.95
- Bootstrap resamples: 10000
- Bootstrap seed: 20260718
- Sampling unit: `authored_evaluation_case`
- Wide-interval threshold: 0.2
- Total authored cases: 51
- Answerable cases: 41
- No-evidence cases: 6
- Review or unsupported-scope cases: 4

## Metric Intervals

| Metric | Point | 95% interval | n | Method | Width flag |
| --- | ---: | ---: | ---: | --- | --- |
| Hit@1 | 0.829 | [0.687, 0.915] | 41 | `wilson_score_95` | wide |
| Mean reciprocal rank | 0.906 | [0.837, 0.963] | 41 | `percentile_bootstrap_10000_95` | not wide |
| Citation coverage | 1.000 | [1.000, 1.000] | 41 | `percentile_bootstrap_10000_95` | not wide |
| Grounding check rate | 1.000 | [0.914, 1.000] | 41 | `wilson_score_95` | not wide |
| Status accuracy | 1.000 | [0.930, 1.000] | 51 | `wilson_score_95` | not wide |
| No-answer accuracy | 1.000 | [0.610, 1.000] | 6 | `wilson_score_95` | wide |
| Review/unsupported routing | 1.000 | [0.510, 1.000] | 4 | `wilson_score_95` | wide |

## Answerable Case Types

| Case type | n | Hit@1 (95% Wilson) | MRR (95% bootstrap) |
| --- | ---: | ---: | ---: |
| `answerable_direct` | 24 | 0.917 [0.742, 0.977] | 0.958 [0.896, 1.000] |
| `answerable_multi_clause` | 5 | 0.600 [0.231, 0.882] | 0.800 [0.600, 1.000] |
| `answerable_paraphrase` | 11 | 0.727 [0.434, 0.903] | 0.833 [0.651, 1.000] |
| `answerable_pdf` | 1 | 1.000 [0.207, 1.000] | 1.000 [1.000, 1.000] |

## Paired Retrieval-Mode Comparisons

Each delta is candidate minus baseline over matching answerable case IDs. A comparison is marked inconclusive when its 95% interval includes zero.

| Comparison | Metric | Delta | 95% paired interval | Win/tie/loss | Conclusion |
| --- | --- | ---: | ---: | ---: | --- |
| `hybrid` vs `bm25` | Mean reciprocal rank | +0.000 | [+0.000, +0.000] | 0/41/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `bm25` | Hit@1 | +0.000 | [+0.000, +0.000] | 0/41/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `bm25` | Citation coverage | +0.000 | [+0.000, +0.000] | 0/41/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `dense_lsa` | Mean reciprocal rank | -0.020 | [-0.069, +0.024] | 1/37/3 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `dense_lsa` | Hit@1 | -0.024 | [-0.098, +0.049] | 1/38/2 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `dense_lsa` | Citation coverage | +0.000 | [+0.000, +0.000] | 0/41/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `tfidf` | Mean reciprocal rank | -0.008 | [-0.045, +0.028] | 1/37/3 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `tfidf` | Hit@1 | +0.000 | [-0.073, +0.073] | 1/39/1 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `tfidf` | Citation coverage | +0.000 | [+0.000, +0.000] | 0/41/0 | `inconclusive_interval_includes_zero` |

## Reviewer Takeaway

Point estimates remain useful as deterministic regression checks. Wide intervals identify claims that need more independently labeled cases before they should be generalized. Paired comparisons describe only this fixed set.
