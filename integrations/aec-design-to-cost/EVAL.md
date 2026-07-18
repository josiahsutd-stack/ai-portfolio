# Contract Evaluation

## Evaluation Question

Can three independently runnable local projects exchange a bounded, source-linked AEC workflow record while rejecting incomplete or contradictory handoffs?

This is an integration-contract evaluation. It does not evaluate design quality, retrieval quality, language-model quality, cost accuracy, code compliance, or real project outcomes.

## Fixture

[`sample_data/synthetic_workflow_case.json`](sample_data/synthetic_workflow_case.json) contains one authored synthetic clinic scenario with:

- 8 role-tagged messages;
- 5 approved requirements;
- a synthetic 60 m by 60 m site and explicit constraint/proxy inputs;
- a fixed 96-candidate massing search with seed 17;
- a synthetic rate library shared with the QS project.

No client, practice, site, bidder, confidential project, or market-rate data is included.

## Assertions

[`tests/test_aec_workflow_integration.py`](../../tests/test_aec_workflow_integration.py) checks:

| Test area | Evidence sought |
| --- | --- |
| Happy path | Approved/mapped/retained counts, complete field source map, feasible storey-matched selection, and bounded takeoff |
| Approval gate | Missing approval prevents the workflow from running |
| Message validation | An unsupported role fails with the offending entry number |
| Conflict gate | An unresolved required requirement conflict prevents the workflow from running |
| Site invariant | Approved area must agree with supplied dimensions |
| Height invariant | Approved storeys must fit the supplied height and floor-to-floor values |
| Empty option set | A search with no feasible storey-matched candidate fails instead of selecting an invalid option |
| Provenance | Selected candidate id survives into the schematic plan and QS result |
| Scope boundary | Budget comparison remains false and tender analysis remains `not_run` |
| Reproducibility | Repeated runs produce the same trace version and generated artifacts |

## Recorded Fixture Result

The checked-in trace records 92 feasible candidates, 42 feasible storey-matched candidates, and 7 priced quantity lines with no unpriced lines. These counts show the code path executed for this fixture; they are not generalization or accuracy metrics.

## Run

```bash
python integrations/aec-design-to-cost/run_workflow.py
python -m pytest tests/test_aec_workflow_integration.py
```

The broader repository verification also regenerates the trace and checks that tracked outputs remain unchanged:

```bash
python scripts/verify.py
```
