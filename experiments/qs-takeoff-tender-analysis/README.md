# QS Takeoff and Tender Analysis Workbench

Local quantity-takeoff, cost-build-up, and tender-exception workflow over explicit vector geometry. The project demonstrates auditable calculation and commercial-review boundaries without claiming PDF interpretation, current market pricing, or professional quantity-surveying output.

**Data status:** all bundled plans, rates, and tenders are synthetic fixtures. No customer drawings, rate books, quotations, bidder identities, or live project data are included.

![Measured plan, cost build-up, and tender exception evidence](../../docs/assets/screenshots/qs-takeoff-tender-demo.png)

## Evidence Snapshot

| Evidence | Current result |
| --- | ---: |
| Hand-calculated floor-plan fixtures | 3 |
| Quantity line exact-match rate | 1.000 |
| Shared-wall estimator MAE | 0.000 m |
| Naive room-perimeter baseline MAE | 6.333 m |
| Cost-total MAE against authored fixture totals | SGD 0.00 |
| Cost lines with geometry and rate provenance | 1.000 |
| Tender exception precision / recall / F1 | 1.000 / 1.000 / 1.000 |

These are deterministic regression results on deliberately small authored fixtures. They are evidence that the implemented formulas and checks reproduce known examples, not evidence of open-world drawing understanding or commercial accuracy. Full case details are in [EVAL.md](EVAL.md) and [evaluation_summary.json](demo_outputs/evaluation_summary.json).

## Local Review

From the repository root:

```bash
python experiments/qs-takeoff-tender-analysis/evaluate_qs.py
pytest tests/test_qs_takeoff_tender_analysis.py -q
streamlit run experiments/qs-takeoff-tender-analysis/app.py
```

The evaluator uses only the Python standard library and repository dependencies. No API key or paid service is required.

## Implemented Workflow

1. Parse a typed rectangular floor-plan schema with an explicit drawing scale.
2. Reject overlapping rooms, invalid dimensions, duplicate ids, and openings that do not lie on a classified wall.
3. Split collinear room edges into atomic segments and classify each as external or shared partition geometry.
4. Deduct door and window openings from the correct wall class.
5. Produce seven quantity lines with formulas and source geometry ids.
6. Join quantities to a versioned rate library with unit checks, provenance, and item-level uncertainty bands.
7. Compare normalized synthetic tenders against the benchmark and expose missing, unusually low, unusually high, and extra line items.

The tender layer does not rank bidders or recommend an award. It creates a review queue for human commercial analysis.

## Checked-In Review Artifacts

- [Sample vector plan](demo_outputs/sample_plan.svg)
- [Sample quantity takeoff](demo_outputs/sample_takeoff.csv)
- [Cost build-up](demo_outputs/cost_breakdown.svg)
- [Sample cost estimate](demo_outputs/sample_estimate.json)
- [Tender comparison](demo_outputs/tender_comparison.svg)
- [Tender exception records](demo_outputs/sample_tender_analysis.json)
- [Evaluation report](demo_outputs/evaluation_report.md)
- [Failure analysis](demo_outputs/failure_analysis.md)

## Architecture and Interfaces

[ARCHITECTURE.md](ARCHITECTURE.md) documents the trust boundaries, geometry algorithm, and data contracts. A FastAPI surface is available locally:

```bash
python -m uvicorn qs_takeoff_tender_analysis.api:app --app-dir experiments/qs-takeoff-tender-analysis/src --reload
```

Endpoints: `GET /health`, `POST /takeoff`, `POST /estimate`, and `POST /tender-review`.

## Limitations

The main constraints are summarized in [LIMITATIONS.md](LIMITATIONS.md):

- rectangular, axis-aligned, single-storey vector rooms only;
- no raster/PDF OCR, symbol detection, CAD/BIM/IFC ingestion, or drawing-revision comparison;
- no foundations, reinforcement, MEP, temporary works, preliminaries, escalation, taxes, overhead, or profit model;
- synthetic rates are not market benchmarks and uncertainty bands are illustrative;
- simple ratio bands are not bid-risk models, fraud detection, or tender advice;
- all outputs require qualified QS, design-team, and commercial review.

## Next Steps

1. Add a versioned IFC or DXF adapter while retaining the same validated intermediate geometry contract.
2. Evaluate room, wall, opening, and dimension extraction against a licensed public drawing set with held-out projects.
3. Connect rates to a permitted, timestamped source and model location, quantity, procurement, and time effects separately.
4. Add revision diffs, measurement-rule configuration, elemental cost plans, and human approval history.
5. Evaluate tender normalization on de-identified, permissioned schedules with expert-adjudicated exceptions.
