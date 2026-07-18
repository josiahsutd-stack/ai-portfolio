# Retrieval Uncertainty Report

Singapore public-source uncertainty analysis for the AEC retrieval evaluation.

## Interpretation Boundary

Intervals quantify case-resampling uncertainty inside this fixed authored evaluation set. They do not measure label independence, corpus currency, expert agreement, or performance on a broader query population.

These intervals are not a claim of production accuracy or external validity.

## Protocol

- Confidence level: 0.95
- Bootstrap resamples: 10000
- Bootstrap seed: 20260718
- Sampling unit: `authored_evaluation_case`
- Wide-interval threshold: 0.2
- Total authored cases: 24
- Answerable cases: 21
- No-evidence cases: 2
- Review or unsupported-scope cases: 1

## Metric Intervals

| Metric | Point | 95% interval | n | Method | Width flag |
| --- | ---: | ---: | ---: | --- | --- |
| Hit@1 | 0.952 | [0.773, 0.992] | 21 | `wilson_score_95` | wide |
| Mean reciprocal rank | 0.976 | [0.929, 1.000] | 21 | `percentile_bootstrap_10000_95` | not wide |
| Citation coverage | 0.968 | [0.921, 1.000] | 21 | `percentile_bootstrap_10000_95` | not wide |
| Grounding check rate | 0.905 | [0.711, 0.973] | 21 | `wilson_score_95` | wide |
| Status accuracy | 1.000 | [0.862, 1.000] | 24 | `wilson_score_95` | not wide |
| Exact evidence target Hit@1 | 0.810 | [0.600, 0.923] | 21 | `wilson_score_95` | wide |
| Exact evidence target MRR | 0.881 | [0.762, 0.976] | 21 | `percentile_bootstrap_10000_95` | wide |
| Source-page target Hit@1 | 0.778 | [0.548, 0.910] | 18 | `wilson_score_95` | wide |
| Source-page target MRR | 0.861 | [0.722, 0.972] | 18 | `percentile_bootstrap_10000_95` | wide |
| No-answer accuracy | 1.000 | [0.342, 1.000] | 2 | `wilson_score_95` | wide |
| Review/unsupported routing | 1.000 | [0.207, 1.000] | 1 | `wilson_score_95` | wide |

## Answerable Case Types

| Case type | n | Hit@1 (95% Wilson) | MRR (95% bootstrap) |
| --- | ---: | ---: | ---: |
| `public_source_direct` | 15 | 1.000 [0.796, 1.000] | 1.000 [1.000, 1.000] |
| `public_source_paraphrase` | 6 | 0.833 [0.436, 0.970] | 0.917 [0.750, 1.000] |

## Paired Retrieval-Mode Comparisons

Each delta is candidate minus baseline over matching answerable case IDs. A comparison is marked inconclusive when its 95% interval includes zero.

| Comparison | Metric | Delta | 95% paired interval | Win/tie/loss | Conclusion |
| --- | --- | ---: | ---: | ---: | --- |
| `hybrid` vs `bm25` | Mean reciprocal rank | +0.012 | [+0.000, +0.036] | 1/20/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `bm25` | Hit@1 | +0.000 | [+0.000, +0.000] | 0/21/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `bm25` | Citation coverage | +0.000 | [+0.000, +0.000] | 0/21/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `bm25` | Exact evidence target MRR | +0.067 | [+0.000, +0.151] | 3/18/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `bm25` | Exact evidence target Hit@1 | +0.095 | [+0.000, +0.238] | 2/19/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `dense_lsa` | Mean reciprocal rank | +0.119 | [+0.000, +0.262] | 3/18/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `dense_lsa` | Hit@1 | +0.095 | [+0.000, +0.238] | 2/19/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `dense_lsa` | Citation coverage | +0.191 | [+0.064, +0.341] | 6/15/0 | `candidate_higher_on_fixed_set` |
| `hybrid` vs `dense_lsa` | Exact evidence target MRR | +0.337 | [+0.139, +0.540] | 11/8/2 | `candidate_higher_on_fixed_set` |
| `hybrid` vs `dense_lsa` | Exact evidence target Hit@1 | +0.381 | [+0.143, +0.619] | 9/11/1 | `candidate_higher_on_fixed_set` |
| `hybrid` vs `tfidf` | Mean reciprocal rank | +0.103 | [+0.024, +0.206] | 4/17/0 | `candidate_higher_on_fixed_set` |
| `hybrid` vs `tfidf` | Hit@1 | +0.143 | [+0.000, +0.286] | 3/18/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `tfidf` | Citation coverage | +0.095 | [+0.000, +0.238] | 2/19/0 | `inconclusive_interval_includes_zero` |
| `hybrid` vs `tfidf` | Exact evidence target MRR | +0.262 | [+0.119, +0.417] | 9/12/0 | `candidate_higher_on_fixed_set` |
| `hybrid` vs `tfidf` | Exact evidence target Hit@1 | +0.333 | [+0.143, +0.524] | 7/14/0 | `candidate_higher_on_fixed_set` |

## Reviewer Takeaway

Point estimates remain useful as deterministic regression checks. Wide intervals identify claims that need more independently labeled cases before they should be generalized. Paired comparisons describe only this fixed set.
