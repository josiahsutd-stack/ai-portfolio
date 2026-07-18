# Evaluation

## Question

Can the implemented geometry and commercial-review pipeline reproduce independently authored quantities, costs, and tender exceptions on a bounded local fixture set?

## Dataset

- Three synthetic rectangular floor plans: a single room, two adjoining rooms, and an L-shaped three-room arrangement.
- Twenty-one expected quantity lines calculated manually from fixture geometry.
- Seven synthetic SGD rates with explicit uncertainty and provenance fields.
- Three synthetic anonymous tenders with five authored review exceptions.

The data is intentionally small enough for a reviewer to calculate by hand. It is not split into training and test sets because no model is trained.

## Baseline

The baseline adds every room perimeter. It cannot distinguish external walls from shared partitions, so it over-counts adjoining geometry. The implemented estimator splits coincident edges and counts each shared wall once.

## Metrics

| Metric | Current result |
| --- | ---: |
| Quantity line exact-match rate | 1.000 |
| Quantity mean absolute error | 0.000 |
| Wall-length MAE | 0.000 m |
| Naive perimeter baseline wall-length MAE | 6.333 m |
| Cost-total MAE | SGD 0.00 |
| Cost-line provenance coverage | 1.000 |
| Tender exception precision | 1.000 |
| Tender exception recall | 1.000 |
| Tender exception F1 | 1.000 |

## Interpretation

Perfect fixture results are expected for deterministic formulas tested against authored labels. They show regression correctness within this geometry grammar. They do not measure extraction from arbitrary plans, robustness to drawing conventions, pricing calibration, tender risk, or professional judgment.

## Error and Rejection Tests

The test suite covers missing scale, overlapping rooms, openings away from walls, opening overlap, missing rates, rate-unit mismatch, currency mismatch, and line-level tender exceptions. Invalid geometry is rejected rather than silently estimated.

## Reproduce

```bash
python experiments/qs-takeoff-tender-analysis/evaluate_qs.py
pytest tests/test_qs_takeoff_tender_analysis.py -q
```

Machine-readable case results are in [demo_outputs/evaluation_summary.json](demo_outputs/evaluation_summary.json).
